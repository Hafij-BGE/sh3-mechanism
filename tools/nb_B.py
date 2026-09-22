"""Part B — main task: loss of fold. B1 model, B2 structural check, B3 uncertainty and calls,
B4 external validation, B5 cancer biology."""
from nbkit import md, code, setup

# ════════════════════════════════════════════════════════════════════════ B1
B1 = [md(r"""
# B1 — The folding predictor, tested on SH3 families it never saw

**Question.** Can ΔΔG of folding be predicted for an SH3 domain from sequence alone, and does a
supervised model beat the zero-shot ESM-2 score it is built on?

**What it does.** A 1292 → 512 → 128 → 1 network on frozen ESM-2 features, trained on the
~361,000 **non-SH3** MegaScale variants (validation = whole held-out domains), five seeds. The
entire SH3 family — 15 genes, 27,590 variants — is held out, and each domain is scored
separately with a 2,000-resample bootstrap interval. Splits are grouped on UniProt accession +
domain index so no domain sits on both sides.

**Inputs:** A2 features and embeddings; A1 ground truth (for the cross-assay check).
**Outputs:** `models.pt`, `folding_per_domain_ci.csv`, `heldout_predictions.parquet`,
`atlas_fold_predictions.parquet`, `ablation.csv`, `RESULTS_B1.md`.
It also runs four robustness checks (feature ablation, ridge regression, error breakdown, FoldX/EVE),
which do not change the model.
**Runtime:** about 25 min on a **T4 GPU** (10 of them the robustness checks). Explanation: `docs/B1_folding_model.md`.
"""),
setup('B1', 'Folding predictor', gpu=True),
code(r"""
import torch
MG = pd.read_parquet(R.res('A2', 'features_megascale.parquet'))
DD = pd.read_parquet(R.res('A2', 'features_ddpca.parquet'))
AT = pd.read_parquet(R.res('A2', 'features_atlas.parquet'))
EMB = C.load_embeddings(R.res('A2', 'esm_domain_embeddings.npz'))
print(f'megascale {len(MG):,} | ddpca {len(DD):,} | atlas {len(AT):,} | embeddings {len(EMB)}')
"""),
md("## 1. Train on non-SH3 domains (or reload this folder's models)"),
code(r"""
Xall, M = C.build_X(MG, EMB)
M['group'] = np.where(M.uniprot.notna() & M.domain_idx.notna(),
                      M.uniprot.astype(str) + '_' + M.domain_idx.astype(str), M.domain_key.astype(str))
tr = np.where(~M.is_sh3.eq(True).values)[0]
g = M.group.values[tr]; uq = np.unique(g); np.random.default_rng(0).shuffle(uq)
vm = np.isin(g, uq[:max(1, len(uq) // 10)]); fit, val = tr[~vm], tr[vm]
SPLIT = dict(train_variants=len(fit), train_groups=len(np.unique(M.group.values[fit])),
             val_variants=len(val), val_groups=len(np.unique(M.group.values[val])),
             heldout_sh3_variants=int(M.is_sh3.eq(True).sum()))
assert not set(M.group.values[fit]) & set(M.group.values[M.is_sh3.eq(True).values]), 'SH3 group leaked into training'
print(SPLIT)
if R.done('models.pt'):
    FOLD, SC_M, SC_SD = C.load_fold_models(R.out('models.pt')); print('folding models loaded from this folder')
else:
    Xf = Xall[fit].astype(np.float32); SC_M = Xf.mean(0); SC_SD = Xf.std(0) + 1e-6
    Xf = (Xf - SC_M) / SC_SD; Xv = (Xall[val].astype(np.float32) - SC_M) / SC_SD
    y = M.ddG_fold.values.astype(np.float32); FOLD = []
    for s in range(5):
        t0 = time.time(); FOLD.append(C.train(C.FoldHead, Xf, y[fit], Xv, y[val], epochs=30, bs=1024, wd=1e-4, seed=s))
        print(f'  seed {s}  {(time.time() - t0) / 60:.1f} min')
    del Xf, Xv
    torch.save({'fold': [m.state_dict() for m in FOLD], 'fold_scaler': {'m': SC_M, 'sd': SC_SD}}, R.out('models.pt'))
del Xall
"""),
md("## 2. Score every held-out SH3 domain separately\nPer-domain ρ with a bootstrap interval, the "
   "zero-shot ESM-2 score on the same variants, and a sign test across domains. Predictions for the "
   "calibration step (B3) are saved alongside."),
code(r"""
X32, T = C.build_X(MG[MG.is_sh3.eq(True)], EMB, half=False)
T['group'] = T.uniprot.astype(str) + '_' + T.domain_idx.astype(str)
T['pred'] = C.fold_scores(FOLD, X32, SC_M, SC_SD, clip=20).mean(0)            # Stage 4 evaluation setting
P10 = C.fold_scores(FOLD, X32.astype(np.float16), SC_M, SC_SD, clip=10)        # Stage 3b calibration setting
T['pred_c10'], T['sd_c10'] = P10.mean(0), P10.std(0)
rows = []
for g_, sub in T.groupby('group'):
    if len(sub) < 30: continue
    y, p = sub.ddG_fold.values, sub.pred.values; lo, hi = C.boot_ci(y, p, 2000)
    rows.append(dict(group=g_, gene=sub.gene.iloc[0], n=len(sub), rho=C.spearman(y, p), lo=lo, hi=hi,
                     esm=C.spearman(y, sub.esm_score.values)))
PD = pd.DataFrame(rows).sort_values('rho'); PD.to_csv(R.out('folding_per_domain_ci.csv'), index=False)
WINS = int((PD.rho > PD.esm.abs()).sum())
T[['domain_key', 'group', 'gene', 'uniprot', 'domain_idx', 'pos', 'wt_aa', 'mut_aa', 'ddG_fold', 'esm_score',
   'pred', 'pred_c10', 'sd_c10']].to_parquet(R.out('heldout_predictions.parquet'), index=False)
print(PD.round(3).to_string(index=False))
print(f'\nper-domain median rho {PD.rho.median():.3f} | ESM {PD.esm.median():.3f} | head wins {WINS}/{len(PD)} '
      f'| sign test p = {C.sign_test_two_sided(WINS, len(PD)):.1e}')
"""),
md("## 3. Apply to the atlas, and a cross-assay check on ddPCA folding energies"),
code(r"""
Xa, A = C.build_X(AT, EMB)
Pa = C.fold_scores(FOLD, Xa, SC_M, SC_SD, clip=10)
A['pred_ddG_fold'], A['sd_fold'] = Pa.mean(0), Pa.std(0)
A.to_parquet(R.out('atlas_fold_predictions.parquet'), index=False)
rel = pd.read_parquet(R.res('A1', 'ddpca_ground_truth.parquet'))[['domain', 'pos', 'wt_aa', 'mut_aa', 'folding_reliable']]
Xd, D_ = C.build_X(DD, EMB)
D_['pred'] = C.fold_scores(FOLD, Xd, SC_M, SC_SD, clip=20).mean(0)
D_ = D_.merge(rel.rename(columns={'domain': 'domain_key'}), on=['domain_key', 'pos', 'wt_aa', 'mut_aa'], how='left')
XA = pd.DataFrame([dict(domain=k, n=len(g_), rho_model=C.spearman(g_.ddG_fold, g_.pred), rho_esm=C.spearman(g_.ddG_fold, g_.esm_score))
                   for k, g_ in D_[D_.folding_reliable.eq(True) & D_.ddG_fold.notna()].groupby('domain_key')])
print(XA.round(3).to_string(index=False))
"""),
md("## 4. Robustness checks\n"
   "- **Feature ablation (roadmap K1):** what does each feature group contribute? One seed each, same split.\n"
   "- **Simpler models (K2):** ridge regression on the same 1,292 features.\n"
   "- **Error breakdown (J4):** where the head is wrong — by substitution type and by effect size.\n"
   "- **Conventional predictors (J6):** FoldX and EVE (shipped with the ddPCA archive) against the head on the ddPCA domains.\n"
   "None of these changes the model or the headline numbers above."),
code(r"""
from sklearn.linear_model import Ridge
pdmed = lambda p: float(pd.Series([C.spearman(g_.ddG_fold, p[g_.index]) for _, g_ in T.groupby('group') if len(g_) >= 30]).median())
if R.done('ablation.csv'):
    AB = pd.read_csv(R.out('ablation.csv')); print('ablation loaded from this folder')
else:
    Xall, _ = C.build_X(MG, EMB); y = M.ddG_fold.values.astype(np.float32); rows = []
    for name, cols in [('ESM embedding only', list(range(1280))), ('embedding + 5 ESM scalars', list(range(1285))),
                       ('12 scalars only (no embedding)', list(range(1280, 1292)))]:
        Xf = Xall[fit][:, cols].astype(np.float32); m_ = Xf.mean(0); s_ = Xf.std(0) + 1e-6
        mdl = C.train(C.FoldHead, (Xf - m_) / s_, y[fit], (Xall[val][:, cols].astype(np.float32) - m_) / s_, y[val],
                      epochs=30, bs=1024, wd=1e-4, seed=0)
        p = C.predict(mdl, np.clip((X32[:, cols] - m_) / s_, -20, 20)); del Xf
        rows.append(dict(model=f'MLP, {name}', features=len(cols), per_domain_median_rho=pdmed(p), pooled_rho=C.spearman(T.ddG_fold, p)))
        print(rows[-1])
    p = C.predict(FOLD[0], np.clip((X32 - SC_M) / SC_SD, -20, 20))
    rows.append(dict(model='MLP, all 1,292 features (seed 0)', features=1292, per_domain_median_rho=pdmed(p), pooled_rho=C.spearman(T.ddG_fold, p)))
    rows.append(dict(model='MLP, all features, 5-seed ensemble (the model)', features=1292, per_domain_median_rho=pdmed(T.pred.values),
                     pooled_rho=C.spearman(T.ddG_fold, T.pred)))
    Xs = ((Xall[fit].astype(np.float32) - SC_M) / SC_SD); Xv = ((Xall[val].astype(np.float32) - SC_M) / SC_SD)
    best = max([1, 10, 100, 1000], key=lambda a: C.spearman(y[val], Ridge(alpha=a).fit(Xs, y[fit]).predict(Xv)))
    rg = Ridge(alpha=best).fit(Xs, y[fit]); p = rg.predict(np.clip((X32 - SC_M) / SC_SD, -20, 20)); del Xs, Xv, Xall
    rows.append(dict(model=f'ridge regression, all features (alpha {best})', features=1292, per_domain_median_rho=pdmed(p),
                     pooled_rho=C.spearman(T.ddG_fold, p)))
    rows.append(dict(model='zero-shot ESM-2 score (no training)', features=0, per_domain_median_rho=pdmed(-T.esm_score.values),
                     pooled_rho=C.spearman(T.ddG_fold, -T.esm_score)))
    AB = pd.DataFrame(rows); AB.to_csv(R.out('ablation.csv'), index=False)
print(AB.round(3).to_string(index=False))
"""),
code(r"""
KDm = T.mut_aa.map(C.KD); KDw = T.wt_aa.map(C.KD)
T['substitution'] = np.select([T.mut_aa == 'P', T.wt_aa == 'G', T.mut_aa == 'G', (KDw > 1.5) & (KDm < -1.5), (KDw < -1.5) & (KDm > 1.5)],
                              ['to proline', 'from glycine', 'to glycine', 'hydrophobic to polar', 'polar to hydrophobic'], 'other')
T['effect'] = pd.cut(T.ddG_fold, [-np.inf, 0, 1, 2, 3, np.inf], labels=['stabilising (<0)', '0-1', '1-2', '2-3', '>3 kcal/mol'])
def err_table(col):
    return T.groupby(col, observed=True).apply(lambda g_: pd.Series(dict(n=len(g_), rho=C.spearman(g_.ddG_fold, g_.pred) if len(g_) > 20 else np.nan,
                                                            mae=float(np.mean(np.abs(g_.ddG_fold - g_.pred))),
                                                            bias=float(np.mean(g_.pred - g_.ddG_fold))))).reset_index()
ERR_SUB, ERR_EFF = err_table('substitution'), err_table('effect')
print(ERR_SUB.round(3).to_string(index=False)); print(ERR_EFF.round(3).to_string(index=False))

import re
fx = pd.read_csv(R.res('A1', 'baseline_foldx.csv')); ev = pd.read_csv(R.res('A1', 'baseline_eve.csv'))
D2 = D_[D_.folding_reliable.eq(True) & D_.ddG_fold.notna()].copy(); D2['id'] = D2.wt_aa + D2.pos.astype(int).astype(str) + D2.mut_aa
D2 = D2.merge(fx.rename(columns={'domain': 'domain_key'}), on=['domain_key', 'id'], how='left')
ev = ev.join(ev.id.astype(str).str.extract(r'^([A-Z])(\d+)([A-Z])$').rename(columns={0: 'e_wt', 1: 'e_pos', 2: 'e_mut'})).dropna(subset=['e_pos'])
ev['e_pos'] = ev.e_pos.astype(int); parts = []
for dom, g_ in ev.groupby('domain'):         # EVE numbers residues on the full protein: derive the offset
    wt_at = dict(zip(D2[D2.domain_key == dom].pos.astype(int), D2[D2.domain_key == dom].wt_aa))
    off = max(range(-400, 401), key=lambda o: sum(wt_at.get(p - o) == w for p, w in zip(g_.e_pos, g_.e_wt)))
    parts.append(g_.assign(domain_key=dom, pos=g_.e_pos - off, mut_aa=g_.e_mut, eve_offset=off))
ev = pd.concat(parts)[['domain_key', 'pos', 'mut_aa', 'prediction_EVE_evol_indices', 'eve_offset']]
D2 = D2.merge(ev, on=['domain_key', 'pos', 'mut_aa'], how='left')
BASE = []
for dom, g_ in D2.groupby('domain_key'):
    c = g_.dropna(subset=['foldx_ddg', 'prediction_EVE_evol_indices'])
    BASE.append(dict(domain=dom, common_variants=len(c), head=C.spearman(c.ddG_fold, c.pred), esm_zero_shot=C.spearman(c.ddG_fold, -c.esm_score),
                     foldx=C.spearman(c.ddG_fold, c.foldx_ddg), eve=C.spearman(c.ddG_fold, c.prediction_EVE_evol_indices),
                     eve_offset=int(g_.eve_offset.dropna().iloc[0]) if g_.eve_offset.notna().any() else None))
BASE = pd.DataFrame(BASE); print(BASE.round(3).to_string(index=False))
"""),
md("## 5. Results"),
code(r"""
from scipy.stats import pearsonr
q1, q3 = np.percentile(PD.rho, [25, 75])
for k, v in [('domains', len(PD)), ('per_domain_median_rho', PD.rho.median()), ('per_domain_min_rho', PD.rho.min()),
             ('per_domain_max_rho', PD.rho.max()), ('per_domain_iqr_low', q1), ('per_domain_iqr_high', q3),
             ('all_ci_exclude_zero', bool((PD.lo > 0).all())), ('esm_per_domain_median_rho', PD.esm.median()),
             ('domains_won', WINS), ('sign_test_p', C.sign_test_two_sided(WINS, len(PD))),
             ('heldout_variants', len(T)), ('pooled_rho', C.spearman(T.ddG_fold, T.pred)),
             ('pooled_pearson_r', float(pearsonr(T.ddG_fold, T.pred)[0])),
             ('pooled_rmse', float(np.sqrt(np.mean((T.ddG_fold - T.pred) ** 2)))),
             *[(k, v) for k, v in SPLIT.items()]]:
    R.metric(k, v)
R.section('Per held-out SH3 domain', 'Spearman ρ against measured ΔΔG_fold, 95% bootstrap CI (2,000 resamples). '
          'ESM is the zero-shot score on the same variants (negative sign is correct).', PD, '{:.3f}')
R.section('Cross-assay check on ddPCA folding energies (reliable fits)', 'A different assay (AbundancePCA) from the '
          'training data (proteolysis); GRB2-SH3 is the only SH3.', XA, '{:.3f}')
for _, r in AB.iterrows(): R.metric('ablation: ' + r.model, r.per_domain_median_rho)
for _, r in BASE.iterrows():
    for c in ('head', 'esm_zero_shot', 'foldx', 'eve'): R.metric(f'baseline_{r.domain}_{c}', r[c])
R.section('Feature ablation and simpler models (K1, K2)', 'Per-domain median ρ on the 15 held-out SH3 domains. Single-seed rows '
          'should be compared with the single-seed full model, not the ensemble.', AB, '{:.3f}')
R.section('Error by substitution type (J4)', 'bias = mean(predicted − measured); negative means under-predicted damage.', ERR_SUB, '{:.3f}')
R.section('Error by measured effect size (J4)', '', ERR_EFF, '{:.3f}')
R.section('Against conventional predictors on the ddPCA domains (J6)', 'Spearman ρ with measured ΔΔG_fold on variants all four '
          'methods score. FoldX needs a structure; EVE needs a deep alignment; the head needs neither. EVE residue numbering '
          'is converted to construct numbering by the derived offset.', BASE, '{:.3f}')
R.finish([f"Per-domain median ρ {PD.rho.median():.3f} (range {PD.rho.min():.3f}–{PD.rho.max():.3f}, IQR {q1:.3f}–{q3:.3f}) "
          f"over {len(PD)} held-out SH3 domains; every 95% CI excludes zero: {bool((PD.lo > 0).all())}.",
          f"Beats zero-shot ESM-2 (median |ρ| {PD.esm.abs().median():.3f}) on {WINS}/{len(PD)} domains; "
          f"two-sided sign test p = {C.sign_test_two_sided(WINS, len(PD)):.1e}.",
          f"Pooled over {len(T):,} variants: ρ {R.metrics['pooled_rho']:.3f}, RMSE {R.metrics['pooled_rmse']:.3f} kcal/mol "
          f"(quote the per-domain figure: SPTAN1 alone contributes {int((T.gene == 'SPTAN1').sum()):,} variants).",
          'The model uses no structural feature; structure is kept for the independent check in B2.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ B2
B2 = [md(r"""
# B2 — Is it really a folding predictor? The structural check

**Question.** If the model has learned folding, its predicted damage should follow **burial** and
ignore the **binding interface**. Structure was never a model input, so this is an independent test.

**What it does.** Places every atlas variant on the 56-position GRB2-SH3 frame, averages the
predicted ΔΔG_fold per position, and correlates it with burial and with distance to the bound
peptide in the solved complex. The measured separation tables from A1 and A2 are shown alongside:
they are the same premise in experimental data.

**Inputs:** B1 atlas predictions, A2 structure, A1/A2 separation tables. **Runtime:** under a minute, CPU.
**Outputs:** `position_structure_check.csv`, `position_predictions.csv`, `RESULTS_B2.md`.
Explanation: `docs/B2_structural_check.md`.
"""),
setup('B2', 'Structural check of the folding predictor'),
code(r"""
A = pd.read_parquet(R.res('B1', 'atlas_fold_predictions.parquet'))
STR = pd.read_csv(R.res('A2', 'structure_features.csv'))
ref = STR[STR.domain_key == 'GRB2-SH3'].set_index('pos')
H = A[A.ref_pos.notna()].groupby('ref_pos').agg(n=('pred_ddG_fold', 'size'), mean_fold=('pred_ddG_fold', 'mean')).reset_index()
H['rsasa'] = H.ref_pos.map(ref.rsasa); H['dist_peptide'] = H.ref_pos.map(ref.dist_peptide)
H['buried'] = H.rsasa < 0.25; H['interface'] = H.dist_peptide < 5.0
H.round(4).to_csv(R.out('position_predictions.csv'), index=False)
h = H[H.n >= 10].dropna(subset=['rsasa']).round(4).dropna(subset=['rsasa', 'dist_peptide', 'mean_fold'])
R_BUR = C.spearman(h.mean_fold, 1 - h.rsasa); R_INT = C.spearman(h.mean_fold, -h.dist_peptide)
h.set_index('ref_pos').to_csv(R.out('position_structure_check.csv'))
hv = H.dropna(subset=['rsasa'])
R_ALL = C.spearman(hv.mean_fold, -hv.rsasa)
byclass = h.groupby(['buried', 'interface']).agg(positions=('ref_pos', 'size'), median_pred=('mean_fold', 'median')).reset_index()
var = A.assign(cls=np.where(A.buried.eq(True), 'buried', np.where(A.buried.eq(False), 'surface', 'no structure')))
bv = var.groupby('cls').pred_ddG_fold.agg(['size', 'median']).rename(columns={'size': 'variants', 'median': 'median_pred'}).reset_index()
print(f'{len(h)} positions | burial rho {R_BUR:+.3f} | interface rho {R_INT:+.3f}'); print(byclass.round(3).to_string(index=False))
"""),
code(r"""
SEP = pd.read_csv(R.res('A1', 'separation_table.csv')); XS = pd.read_csv(R.res('A2', 'cross_fold_separation.csv'))
for k, v in [('positions', len(h)), ('rho_damage_vs_burial', R_BUR), ('rho_damage_vs_interface', R_INT),
             ('rho_damage_vs_burial_all_positions', R_ALL),
             ('burial_to_interface_ratio', abs(R_BUR) / max(abs(R_INT), 1e-9))]:
    R.metric(k, v)
for _, r in bv.iterrows(): R.metric(f'median_pred_{r.cls.replace(" ", "_")}_variants', r.median_pred)
R.section('Predicted damage by structural class (aligned positions with ≥10 variants)', '', byclass, '{:.3f}')
R.section('Predicted damage by the variant’s own structure (AlphaFold)', '', bv, '{:.3f}')
R.section('Measured, for comparison: GRB2-SH3 ddPCA (from A1)', 'Median measured ΔΔG (kcal/mol).', SEP, '{:.3f}')
R.section('Measured, cross-fold replication (from A2)', '', XS, '{:.3f}')
R.finish([f"Predicted damage follows burial: ρ {R_BUR:+.3f} over {len(h)} aligned positions.",
          f"It ignores the binding interface: ρ {R_INT:+.3f} — the burial signal is {abs(R_BUR)/max(abs(R_INT),1e-9):.0f}× larger.",
          'Structure was not a model input, so this is independent evidence that the head learned folding, not binding.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ B3
B3 = [md(r"""
# B3 — Uncertainty, and the mechanism call for every cancer variant

**Question.** For each of the 6,884 atlas variants, can we say *with error control* that it
destabilises the domain?

**What it does.**
- **Normalised split-conformal intervals** from the held-out SH3 family: half calibrates the
  90 % quantile of |error| / (ensemble SD + 0.05), the other half measures coverage.
- A variant is **destabilising only if the lower end of its interval exceeds 1 kcal/mol**.
- The binding axis is **zero-shot ESM-2 rank-matched** to the measured GRB2-SH3 binding scale,
  because Part C shows the trained binding head cannot beat it (read from C2's decision file).
  It carries **no binding claim**.
- Diagnostics: coverage at several nominal levels (calibration curve) and accuracy of the most
  confident predictions (rejection curve). The old ensemble-spread "confidence" filter is shown
  as a documented failure.

**Inputs:** B1 predictions, A2 ddPCA features, C2 `binding_decision.json`. **Runtime:** under a minute.
**Outputs:** `atlas_predictions.parquet`, `calibration_curve.csv`, `rejection_curve.csv`, `RESULTS_B3.md`.
Explanation: `docs/B3_uncertainty_and_calls.md`.
"""),
setup('B3', 'Uncertainty and mechanism calls'),
code(r"""
T = pd.read_parquet(R.res('B1', 'heldout_predictions.parquet'))
A = pd.read_parquet(R.res('B1', 'atlas_fold_predictions.parquet'))
DD = pd.read_parquet(R.res('A2', 'features_ddpca.parquet'))
DEC = json.load(open(R.res('C2', 'binding_decision.json')))
print('binding decision from C2:', DEC)
if DEC['head_beats_esm']:
    raise RuntimeError('C2 found a trained binding head that beats ESM-2 on GRB2-SH3, unlike the original run. '
                       'Investigate before making any atlas call.')
pte, sdte = T.pred_c10.values, T.sd_c10.values
yte = T.ddG_fold.values.astype(np.float32); err = np.abs(yte - pte)
perm = np.random.default_rng(0).permutation(len(T)); cal, val = perm[:len(T) // 2], perm[len(T) // 2:]
EPS = 0.05
def conformal_q(e, sd, alpha):
    s = np.sort(e / (sd + EPS)); return float(s[min(int(np.ceil((len(s) + 1) * (1 - alpha))), len(s)) - 1])
Q90 = conformal_q(err[cal], sdte[cal], 0.10)
COV = float(np.mean(np.abs(yte[val] - pte[val]) <= Q90 * (sdte[val] + EPS)))
SD_ERR = C.spearman(sdte, err)
print(f'q90 {Q90:.4f} | coverage {COV:.2%} (target 90%) | corr(ensemble SD, |error|) {SD_ERR:+.3f}')
"""),
md("## Calibration and rejection curves (diagnostics)"),
code(r"""
CAL = pd.DataFrame([dict(nominal=1 - a, quantile=conformal_q(err[cal], sdte[cal], a),
                         empirical=float(np.mean(np.abs(yte[val] - pte[val]) <= conformal_q(err[cal], sdte[cal], a) * (sdte[val] + EPS))),
                         median_halfwidth=float(np.median(conformal_q(err[cal], sdte[cal], a) * (sdte[val] + EPS))))
                    for a in (0.5, 0.4, 0.3, 0.2, 0.1, 0.05)])
order = val[np.argsort(sdte[val])]
REJ = pd.DataFrame([dict(kept_most_confident=f'{int(f*100)}%', n=int(len(order) * f),
                         rho=C.spearman(yte[order[:int(len(order) * f)]], pte[order[:int(len(order) * f)]]),
                         mae=float(np.mean(err[order[:int(len(order) * f)]])))
                    for f in (0.05, 0.1, 0.2, 0.5, 1.0)])
CAL.to_csv(R.out('calibration_curve.csv'), index=False); REJ.to_csv(R.out('rejection_curve.csv'), index=False)
# stratified coverage (roadmap I1): is the global 90% honest in every subgroup? The held-out MegaScale
# SH3 variants carry no structure, so strata are predicted-effect bins and domains, not burial.
cov_v = np.abs(yte[val] - pte[val]) <= Q90 * (sdte[val] + EPS)
Tv = T.iloc[val].assign(covered=cov_v, halfwidth=Q90 * (sdte[val] + EPS),
                        pred_bin=pd.cut(pte[val], [-np.inf, 0, 1, 2, np.inf], labels=['<0', '0-1', '1-2', '>2 kcal/mol']))
STRAT = pd.concat([Tv.groupby('pred_bin', observed=True).agg(n=('covered', 'size'), coverage=('covered', 'mean'),
                                                            median_halfwidth=('halfwidth', 'median')).reset_index()
                     .rename(columns={'pred_bin': 'stratum'}).assign(by='predicted ΔΔG'),
                   Tv.groupby('gene').agg(n=('covered', 'size'), coverage=('covered', 'mean'),
                                          median_halfwidth=('halfwidth', 'median')).reset_index()
                     .rename(columns={'gene': 'stratum'}).assign(by='domain (gene)')])[['by', 'stratum', 'n', 'coverage', 'median_halfwidth']]
STRAT.to_csv(R.out('stratified_coverage.csv'), index=False); print(STRAT.round(3).to_string(index=False))
print(CAL.round(3).to_string(index=False)); print(REJ.round(3).to_string(index=False))
"""),
md("## The calls"),
code(r"""
A['fold_halfwidth'] = Q90 * (A.sd_fold.values + EPS); A['fold_lo'] = A.pred_ddG_fold - A.fold_halfwidth
B = DD[DD.ddG_bind.notna() & DD.binding_reliable.eq(True)]
g = B[B.domain_key == 'GRB2-SH3'].ddG_bind.values
r = (-A.esm_score.values).argsort().argsort() / max(1, len(A) - 1)
A['pred_ddG_bind'] = np.quantile(np.sort(g), np.clip(r, 0, 1)); A['bind_source'] = 'esm_rank_matched'
A['bind_lo'] = A.pred_ddG_bind - float(np.quantile(np.abs(g - np.median(g)), 0.90))
f, b = A.fold_lo >= 1.0, A.bind_lo >= 1.0
A['mechanism'] = np.select([f & b, f & ~b, ~f & b], ['both', 'destabilising', 'rewiring'], 'tolerated')
A.to_parquet(R.out('atlas_predictions.parquet'), index=False)
MC = A.mechanism.value_counts()
AXIS = C.spearman(A.pred_ddG_fold, A.pred_ddG_bind)
print(MC.to_string()); print(f'point-estimate calls (pred >= 1, no interval): {int((A.pred_ddG_fold >= 1).sum()):,}')
"""),
md("## Results"),
code(r"""
for k, v in [('conformal_q90', Q90), ('conformal_coverage', COV), ('sd_vs_error_rho', SD_ERR),
             *[(f'n_{m}', int(MC.get(m, 0))) for m in ('tolerated', 'destabilising', 'rewiring', 'both')],
             ('point_estimate_destabilising', int((A.pred_ddG_fold >= 1).sum())),
             ('old_filter_pass_fraction', float((A.sd_fold < 0.5).mean())),
             ('axis_rank_correlation', AXIS), ('axis_correlation_is_valid_test', False),
             ('median_fold_halfwidth', float(A.fold_halfwidth.median()))]:
    R.metric(k, v)
R.section('Mechanism calls', 'Destabilising = lower interval bound ≥ 1 kcal/mol. "Rewiring" rests on rank-matched ESM-2 '
          'and is reported, not claimed.', MC.rename_axis('mechanism').reset_index(name='variants'))
R.section('Calibration curve (validation half)', 'Nominal against empirical coverage.', CAL, '{:.3f}')
R.section('Rejection curve (validation half)', 'Accuracy of the most confident predictions, ranked by ensemble SD.', REJ, '{:.3f}')
R.section('Stratified coverage (validation half)', 'The 90% target is global; this shows where it is met and where not. '
          'Burial cannot be used as a stratum here: the held-out MegaScale variants carry no structure.', STRAT, '{:.3f}')
R.metric('coverage_min_domain', float(STRAT[STRAT.by == 'domain (gene)'].coverage.min()))
R.metric('coverage_max_domain', float(STRAT[STRAT.by == 'domain (gene)'].coverage.max()))
R.section('Why the old confidence filter was dropped', f"The original Stage 3 called a prediction confident when the "
          f"five seeds agreed (SD < 0.5). Seed spread correlates only ρ {SD_ERR:+.3f} with the actual error, and "
          f"{(A.sd_fold < 0.5).mean():.1%} of atlas variants pass it: agreement between seeds is reproducibility, not accuracy.")
R.section('Axis correlation', f"ρ(predicted fold, predicted bind) = {AXIS:+.3f}. **Not a valid test** of whether a separate "
          "rewiring class exists: both axes derive from ESM-2 by construction.")
R.finish([f"Conformal q90 {Q90:.3f}; empirical coverage {COV:.1%} against a 90% target.",
          f"{int(MC.get('destabilising',0)):,} destabilising, {int(MC.get('both',0)):,} both, {int(MC.get('rewiring',0)):,} rewiring, "
          f"{int(MC.get('tolerated',0)):,} tolerated — {int((A.pred_ddG_fold >= 1).sum()):,} point-estimate calls reduced "
          f"to {int(MC.get('destabilising',0) + MC.get('both',0)):,} under error control.",
          'The binding axis is rank-matched zero-shot ESM-2 (Part C); no binding claim is made.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ B4
B4 = [md(r"""
# B4 — External validation on ProteinGym: where the predictor stops working

**Question.** Does the SH3-trained folding head transfer to proteins it has never seen, and how
does that compare with zero-shot ESM-2?

**What it does.** Scores ProteinGym v1.3 substitution assays in three pre-defined blocks:
**primary** (external stability, 3 assays), **secondary** (expression/abundance, 15 assays),
**sanity** (Tsuboyama assays = training data, 10 assays; a wiring check, not a result). Assays are
excluded from the first two blocks by `DMS_id` **and** by UniProt accession if they overlap
training. Full-length proteins are scored through a 128-residue window centred on the mutation.

**Inputs:** B1 models, A2 MegaScale features, `input/datasets/DMS_*`. **Runtime:** about 15 min, **T4 GPU**.
**Outputs:** `proteingym_results.csv`, `RESULTS_B4.md`. Explanation: `docs/B4_external_validation.md`.
"""),
setup('B4', 'External validation (ProteinGym)', gpu=True, pip='biopython'),
code(r"""
import zipfile, torch
from Bio.Align import substitution_matrices
R.verify_inputs(['input/datasets/DMS_ProteinGym_substitutions.zip', 'input/datasets/DMS_substitutions.csv'])
FOLD, SC_M, SC_SD = C.load_fold_models(R.res('B1', 'models.pt'))
MG = pd.read_parquet(R.res('A2', 'features_megascale.parquet'), columns=['uniprot'])
B1M = json.load(open(R.res('B1', 'metrics_B1.json')))['metrics']
"""),
code(r"""
if R.done('proteingym_results.csv'):
    PG = pd.read_csv(R.out('proteingym_results.csv')); print('loaded from this folder')
else:
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    tok = AutoTokenizer.from_pretrained('facebook/esm2_t33_650M_UR50D')
    esm = AutoModelForMaskedLM.from_pretrained('facebook/esm2_t33_650M_UR50D').to(C.DEV).eval()
    if C.DEV == 'cuda': esm = esm.half()
    AAS = list('ACDEFGHIKLMNPQRSTVWY'); AAPOS = {a: i for i, a in enumerate(AAS)}
    AA_IDX = torch.tensor([tok.convert_tokens_to_ids(a) for a in AAS]).to(C.DEV)
    B62 = substitution_matrices.load('BLOSUM62'); KD, VOL, CHG = C.KD, C.VOL, C.CHG
    ref = pd.read_csv(f'{R.IN}/datasets/DMS_substitutions.csv')
    sel = [c for c in ref.columns if 'selection' in c.lower()][0]
    upc = [c for c in ref.columns if c.lower() in ('uniprot_id', 'uniprot')][0]
    ncol = [c for c in ref.columns if c.lower() in ('dms_total_number_mutants', 'dms_number_single_mutants')]
    TRAIN_UP = set(MG.uniprot.dropna().astype(str).str.upper())
    ts = ref.DMS_id.str.contains('Tsuboyama', case=False, na=False); up = ref[upc].astype(str).str.upper().isin(TRAIN_UP)
    stab = ref[sel].astype(str).str.lower().str.contains('stability')
    expr = ref[sel].astype(str).str.lower().str.contains('expression|abundance')
    pick = lambda t, k: t.sort_values(ncol[0], ascending=False).head(k) if ncol else t.head(k)
    WANT = pd.concat([pick(ref[stab & ~ts & ~up], 25).assign(block='primary'),
                      pick(ref[expr & ~ts & ~up], 15).assign(block='secondary'),
                      pick(ref[stab & ts], 10).assign(block='sanity')])
    Z = zipfile.ZipFile(f'{R.IN}/datasets/DMS_ProteinGym_substitutions.zip')
    names = {os.path.basename(n): n for n in Z.namelist() if n.endswith('.csv')}
    WANT = WANT[WANT.DMS_id.map(lambda i: f'{i}.csv' in names)]
    print('assays:', WANT.block.value_counts().to_dict())
    Wn = 128
    @torch.no_grad()
    def window_feats(seq, pos):
        lo = max(0, pos - 1 - Wn // 2); hi = min(len(seq), lo + Wn); lo = max(0, hi - Wn); sub = seq[lo:hi]; p = pos - 1 - lo
        enc = tok(sub, return_tensors='pt').to(C.DEV)
        rep = esm(**enc, output_hidden_states=True).hidden_states[-1][0, 1 + p].float().cpu().numpy()
        ids = enc['input_ids'][0].clone().unsqueeze(0); ids[0, 1 + p] = tok.mask_token_id
        lp = torch.log_softmax(esm(input_ids=ids, attention_mask=torch.ones_like(ids)).logits[0, 1 + p].float(), -1)
        return rep, lp[AA_IDX].cpu().numpy(), len(sub), (p + 1) / len(sub)
    def score(rep, lp, dlen, rpos, wt, mut):
        e = lp[AAPOS[mut]] - lp[AAPOS[wt]]
        sc = [e, lp[AAPOS[wt]], float(-(np.exp(lp) * lp).sum()), rpos, dlen, KD[mut] - KD[wt], VOL[mut] - VOL[wt],
              CHG.get(mut, 0) - CHG.get(wt, 0), float(B62[wt][mut]) if (wt in B62.alphabet and mut in B62.alphabet) else 0.0,
              float(mut == 'P'), float(wt == 'G'), float(mut == 'G')]
        x = np.concatenate([rep, np.array(sc, np.float32)])[None]
        return float(C.fold_scores(FOLD, x, SC_M, SC_SD, clip=20).mean()), e
    PG = []; t0 = time.time()
    for _, a in WANT.iterrows():
        d = pd.read_csv(Z.open(names[f'{a.DMS_id}.csv']))
        mc = [c for c in d.columns if c.lower() in ('mutant', 'mutants')][0]
        d = d[~d[mc].astype(str).str.contains(':')]
        if len(d) > 1500: d = d.sample(1500, random_state=0)
        ex = d[mc].astype(str).str.extract(r'^([A-Z])(\d+)([A-Z])$').dropna(); d = d.loc[ex.index]
        wt, pos, mut = ex[0].values, ex[1].astype(int).values, ex[2].values; seqs = d['mutated_sequence'].astype(str).values
        ok = np.array([0 < p <= len(s) and s[p-1] == m for s, p, m in zip(seqs, pos, mut)])
        if ok.mean() < 0.9: continue
        wt, pos, mut, seqs, y = wt[ok], pos[ok], mut[ok], seqs[ok], d.DMS_score.values[ok]
        cache = {}; pr = []; es = []
        for s_, p_, w_, m_ in zip(seqs, pos, wt, mut):
            s_ = s_[:p_-1] + w_ + s_[p_:]
            if (len(s_), p_) not in cache: cache[(len(s_), p_)] = window_feats(s_, p_)
            a_, b_ = score(*cache[(len(s_), p_)], w_, m_); pr.append(a_); es.append(b_)
        PG.append(dict(DMS_id=a.DMS_id, block=a.block, n=len(y), seq_len=len(seqs[0]),
                       rho_model=C.spearman(y, pr), rho_esm=C.spearman(y, es)))
        print(f'  {a.DMS_id[:44]:<44} {a.block:<9} model {PG[-1]["rho_model"]:+.3f} esm {PG[-1]["rho_esm"]:+.3f}  {(time.time()-t0)/60:.1f} min')
    PG = pd.DataFrame(PG); PG.to_csv(R.out('proteingym_results.csv'), index=False)
    del esm; torch.cuda.empty_cache()
"""),
md("## Results"),
code(r"""
PG['model_wins'] = PG.rho_model.abs() > PG.rho_esm.abs()
BL = PG.groupby('block').agg(assays=('DMS_id', 'size'), model_median_abs_rho=('rho_model', lambda x: x.abs().median()),
                             esm_median_abs_rho=('rho_esm', lambda x: x.abs().median()), model_wins=('model_wins', 'sum')).reset_index()
for _, r in BL.iterrows():
    for c in ('assays', 'model_median_abs_rho', 'esm_median_abs_rho', 'model_wins'): R.metric(f'{r.block}_{c}', r[c])
ext = PG[PG.block.isin(['primary', 'secondary'])]
ih, ie = B1M['per_domain_median_rho'], abs(B1M['esm_per_domain_median_rho'])
drop = pd.DataFrame([dict(block=b, head_drop=ih - g_.rho_model.abs().median(), esm_drop=ie - g_.rho_esm.abs().median())
                     for b, g_ in ext.groupby('block')])
drop['ratio'] = drop.head_drop / drop.esm_drop
for _, r in drop.iterrows(): R.metric(f'{r.block}_drop_ratio_head_vs_esm', r.ratio)
LEN = ext.assign(length=np.where(ext.seq_len <= 250, '≤250', '>250')).groupby('length').agg(
    assays=('DMS_id', 'size'), model=('rho_model', lambda x: x.abs().median()), esm=('rho_esm', lambda x: x.abs().median())).reset_index()
R.section('By block', '|Spearman ρ| per assay, medians. The sanity block is the training distribution: a wiring check.', BL, '{:.3f}')
R.section('Transfer drop from the internal SH3 result', f'Internal: head {ih:.3f}, ESM {ie:.3f} (per-domain medians, B1).', drop, '{:.3f}')
R.section('By sequence length (primary + secondary)', 'Small n and confounded with assay type; shown only to rule out '
          'the explanation that the 128-residue window is the problem.', LEN, '{:.3f}')
R.section('Every assay', '', PG.drop(columns='model_wins'), '{:.3f}')
R.finish([f"Primary (external stability): head {BL.set_index('block').loc['primary','model_median_abs_rho']:.3f} vs ESM "
          f"{BL.set_index('block').loc['primary','esm_median_abs_rho']:.3f}, head wins {int(BL.set_index('block').loc['primary','model_wins'])}/"
          f"{int(BL.set_index('block').loc['primary','assays'])}.",
          f"Secondary (abundance): head {BL.set_index('block').loc['secondary','model_median_abs_rho']:.3f} vs ESM "
          f"{BL.set_index('block').loc['secondary','esm_median_abs_rho']:.3f}, wins {int(BL.set_index('block').loc['secondary','model_wins'])}/"
          f"{int(BL.set_index('block').loc['secondary','assays'])}.",
          f"Sanity (training data): {BL.set_index('block').loc['sanity','model_median_abs_rho']:.3f} vs "
          f"{BL.set_index('block').loc['sanity','esm_median_abs_rho']:.3f} — the pipeline is wired correctly.",
          'Claim: a domain-scale predictor validated within its regime. Not claimed: a general stability predictor.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ B5
B5 = [md(r"""
# B5 — Cancer biology: does predicted damage explain where cancer mutations fall?

**Question.** Are cancer mutations in SH3 domains enriched for predicted destabilisation — by gene,
by tumour site, or by position in the family?

**What it does.** Every group is compared only with random samples of the atlas **matched on
burial composition** (buried / surface / unknown; 2,000 draws), because a more buried domain will
show more predicted damage for trivial reasons. Benjamini–Hochberg across tests. Everything is run
on all variants and on non-hypermutated variants only. The positional test compares the 56
aligned positions with a uniform null; it does **not** model trinucleotide context or codon-level
mutational opportunity.

**Inputs:** B3 calls, A0 atlas, A2 structure. **Runtime:** about 3 min, CPU.
**Outputs:** `gene_enrichment.csv`, `tumour_type_enrichment.csv`, `position_hotspots.csv`, `RESULTS_B5.md`.
Explanation: `docs/B5_cancer_biology.md`.
"""),
setup('B5', 'Cancer biology'),
code(r"""
import re
A = pd.read_parquet(R.res('B3', 'atlas_predictions.parquet'))
MASTER = pd.read_csv(R.res('A0', 'SH3_cancer_master.tsv'), sep='\t')
STR = pd.read_csv(R.res('A2', 'structure_features.csv'))
A = A.merge(MASTER[['variant_id', 'n_samples_nonhyper', 'top_primary_sites']].drop_duplicates('variant_id'), on='variant_id', how='left')
A['destab'] = A.fold_lo >= 1.0; A['nonhyper'] = A.n_samples_nonhyper.fillna(0) > 0
A['stratum'] = np.where(A.buried.eq(True), 'buried', np.where(A.buried.eq(False) & A.has_structure.eq(True), 'surface', 'unknown'))

def matched_null(pool, group, n_perm=2000, seed=0):
    rng = np.random.default_rng(seed); ps = pool.stratum.values; pv = pool.destab.values.astype(float)
    idx = {k: np.flatnonzero(ps == k) for k in np.unique(ps)}; need = group.stratum.value_counts()
    if any(len(idx.get(k, ())) < n for k, n in need.items()): return np.nan, np.nan, np.nan
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = sum(pv[rng.choice(idx[k], n, replace=False)].sum() for k, n in need.items()) / need.sum()
    obs = float(group.destab.mean())
    return obs, float(np.median(null)), float((np.sum(null >= obs) + 1) / (n_perm + 1))
def bh(p):
    p = np.asarray(p, float); n = len(p); q = np.empty(n); prev = 1.0
    for rank, i in enumerate(np.argsort(p)[::-1]): prev = min(prev, p[i] * n / (n - rank)); q[i] = prev
    return q
def enrich(pool, key, min_n, n_perm=2000):
    rows = []
    for k, sub in pool.groupby(key):
        if len(sub) < min_n: continue
        o, e, p = matched_null(pool, sub, n_perm)
        if not np.isnan(o): rows.append({key: k, 'n': len(sub), 'frac_destab': o, 'expected': e, 'excess': o - e, 'p': p})
    t = pd.DataFrame(rows); t['q'] = bh(t.p.values); return t.sort_values('p')
"""),
code(r"""
t0 = time.time()
GA = enrich(A, 'gene', 20); GN = enrich(A[A.nonhyper], 'gene', 20)
ex = A[['destab', 'stratum']].assign(site=A.top_primary_sites.map(
    lambda v: [re.sub(r'\(.*?\)', '', x).strip().lower() for x in re.split(r'[;,|]', v) if x.strip()]
              if isinstance(v, str) else [])).explode('site').dropna(subset=['site'])
TT = enrich(ex[ex.site != ''], 'site', 30, n_perm=1000)
pd.concat([GA.assign(set='all'), GN.assign(set='nonhyper')]).to_csv(R.out('gene_enrichment.csv'), index=False)
TT.to_csv(R.out('tumour_type_enrichment.csv'), index=False)
print(f'permutation tests {time.time() - t0:.0f}s')
ref = STR[STR.domain_key == 'GRB2-SH3'].set_index('pos')
H = A[A.ref_pos.notna()].groupby('ref_pos').agg(n=('destab', 'size'), n_destab=('destab', 'sum'), mean_fold=('pred_ddG_fold', 'mean'),
                                              mean_bind=('pred_ddG_bind', 'mean'), n_nonhyper=('nonhyper', 'sum')).reset_index()
H['frac_destab'] = H.n_destab / H.n; H['rsasa'] = H.ref_pos.map(ref.rsasa); H['dist_peptide'] = H.ref_pos.map(ref.dist_peptide)
H['buried'] = H.rsasa < 0.25; H['interface'] = H.dist_peptide < 5.0
H.round(4).to_csv(R.out('position_hotspots.csv'), index=False)
obs = H.set_index('ref_pos').n.reindex(range(1, 57), fill_value=0).values; rng = np.random.default_rng(0)
null = np.array([np.bincount(rng.integers(0, 56, obs.sum()), minlength=56).var() for _ in range(5000)])
P_UNI = float((np.sum(null >= obs.var()) + 1) / 5001)
hv = H.dropna(subset=['rsasa'])
R_VD = C.spearman(hv.n, hv.mean_fold); R_DB = C.spearman(hv.mean_fold, -hv.rsasa); R_VB = C.spearman(hv.n, -hv.rsasa)
"""),
md("## Results\nThe gene table is not printed by name here: one hit at q < 0.1 among 170 tests is what "
   "Benjamini–Hochberg allows from noise, and it is not reported as a finding. The full table is in "
   "`gene_enrichment.csv`."),
code(r"""
for k, v in [('variants', len(A)), ('nonhyper', int(A.nonhyper.sum())), ('frac_destab_all', A.destab.mean()),
             ('frac_destab_nonhyper', A[A.nonhyper].destab.mean()),
             ('genes_tested_all', len(GA)), ('genes_sig_all', int((GA.q < 0.1).sum())),
             ('genes_tested_nonhyper', len(GN)), ('genes_sig_nonhyper', int((GN.q < 0.1).sum())),
             ('sites_tested', len(TT)), ('sites_sig', int((TT.q < 0.1).sum())), ('positions_mapped', len(H)),
             ('positional_uniform_p', P_UNI), ('rho_variants_vs_damage', R_VD), ('rho_damage_vs_burial', R_DB),
             ('rho_variants_vs_burial', R_VB), ('binding_claims_made', False)]:
    R.metric(k, v)
R.section('Enrichment tests', 'Burial-matched permutation null, Benjamini–Hochberg, q < 0.1.', pd.DataFrame([
    dict(test='genes, all variants (≥20 variants)', tested=len(GA), significant=int((GA.q < 0.1).sum()), smallest_q=GA.q.min()),
    dict(test='genes, non-hypermutated only (≥20)', tested=len(GN), significant=int((GN.q < 0.1).sum()), smallest_q=GN.q.min()),
    dict(test='tumour primary sites (≥30)', tested=len(TT), significant=int((TT.q < 0.1).sum()), smallest_q=TT.q.min())]), '{:.3g}')
R.section('Tumour sites', '', TT, '{:.3g}')
R.finish([f"{A.destab.mean():.2%} of atlas variants are called destabilising ({A[A.nonhyper].destab.mean():.2%} of non-hypermutated).",
          f"Genes enriched: {int((GA.q<0.1).sum())}/{len(GA)} (all), {int((GN.q<0.1).sum())}/{len(GN)} (non-hypermutated; "
          f"underpowered); tumour sites {int((TT.q<0.1).sum())}/{len(TT)}.",
          f"Variant counts do not follow predicted damage (ρ {R_VD:+.3f}) while damage follows burial (ρ {R_DB:+.3f}).",
          f"Positions are non-uniform (p = {P_UNI:.1e}), but the null ignores mutational opportunity and the pattern is "
          f"unrelated to damage: a mutational-process observation, not a selection signal."])
"""),
]
NOTEBOOKS = {'B1_folding_model': (B1, True), 'B2_structural_check': (B2, False),
             'B3_uncertainty_and_calls': (B3, False), 'B4_external_validation': (B4, True),
             'B5_cancer_biology': (B5, False)}
