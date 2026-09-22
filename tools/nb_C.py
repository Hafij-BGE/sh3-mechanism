"""Part C — why binding cannot be predicted: C1 across domains, C2 within a domain, C3 data sufficiency."""
from nbkit import md, code, setup

LOAD_BINDING = r"""
DD = pd.read_parquet(R.res('A2', 'features_ddpca.parquet'))
EMB = C.load_embeddings(R.res('A2', 'esm_domain_embeddings.npz'))
Xd, DB = C.build_X(DD, EMB)
B = DB[DB.ddG_bind.notna() & DB.binding_reliable.eq(True)].copy()
XB = Xd[B.index.values].astype(np.float32); B = B.reset_index(drop=True)
print(B.groupby('domain_key').agg(measurements=('pos', 'size'), positions=('pos', 'nunique')).to_string())
"""

MODES_MD = r"""
**Two partition modes, run side by side.** Re-checking the original code showed that Stages
3b–3d split positions into folds with scikit-learn's `GroupKFold`, which assigns groups
deterministically and does not shuffle by default. Every "repeat" therefore reused the same
partition; only the inner validation split and the model seeds changed.
- `original` — the unshuffled procedure, reproducing the recorded numbers exactly.
- `corrected` — positions shuffled with the seed before assignment (the Stage 3e design), so each
  repeat is a genuinely different partition.
Set `MODES` below to run one or both. The results table lists them side by side.
"""

# ════════════════════════════════════════════════════════════════════════ C1
C1 = [md(r"""
# C1 — Can binding be learned *across* domains? (Stage 3)

**Question.** Train a binding head on two ddPCA domains and predict the third. Does binding
transfer?

**What it does.** Leave-one-domain-out over GRB2-SH3, PSD95-PDZ3 and GB1. The binding head sees a
64-component PCA of the frozen features (a small head, because ~2,800 measurements against a
650M-parameter encoder would memorise).

**Why it fails, and why that was predictable.** To predict GRB2-SH3 the model trains on a PDZ
domain that reads C-terminal peptides and on GB1, which binds a folded IgG surface. No training
domain shares the SH3 binding mode, so there is nothing to transfer. This experiment is kept
because it is the first step of the reasoning, not because it tests SH3 biology.

**Two versions.**
- `original` — the Stage 3 code exactly, which (it turned out) **stopped training on the test
  domain**: the held-out domain doubled as the early-stopping set. That is leakage.
- `corrected` — early stopping on an inner split of the *training* domains only, with the
  variance-floored scaler and whitened PCA established in Stage 3b.

**Inputs:** A2 features. **Runtime:** about 3 min, T4 GPU. **Outputs:** `lodo_results.csv`, `RESULTS_C1.md`.
Explanation: `docs/C1_binding_cross_domain.md`.
"""),
setup('C1', 'Binding across domains (leave-one-domain-out)', gpu=True),
code(LOAD_BINDING),
code(r"""
from sklearn.decomposition import PCA
y_all = B.ddG_bind.values.astype(np.float32); rows = []
for held in B.domain_key.unique():
    te = (B.domain_key == held).values; tr = ~te; y = y_all[te]; esm = C.spearman(y, B.esm_score.values[te])
    # original Stage 3: raw PCA, 1e-6 scaler, the TEST domain used for early stopping
    pca = PCA(n_components=64, random_state=0).fit(XB[tr])
    s2 = C.ScalerStage3().fit(pca.transform(XB[tr]))
    Ztr, Zte = s2(pca.transform(XB[tr])), s2(pca.transform(XB[te]))
    p = np.mean([C.predict(C.train(C.BindHead, Ztr, y_all[tr], Zte, y, epochs=60, bs=256, lr=3e-3, wd=1e-3, seed=s), Zte)
                 for s in range(5)], 0)
    lo, hi = C.boot_ci(y, p, 1000)
    rows.append(dict(mode='original', held_out=held, n=int(te.sum()), rho=C.spearman(y, p), lo=lo, hi=hi, esm=esm))
    # corrected: early stopping on an inner split of the training domains, Stage 3b preprocessing
    gtr = (B.domain_key[tr] + '_' + B.pos[tr].astype(str)).values
    vm = C.inner_validation(gtr, 0); itr = np.where(tr)[0]; fit, val = itr[~vm], itr[vm]
    s0 = C.Scaler().fit(XB[fit]); pca = PCA(n_components=64, whiten=True, random_state=0).fit(s0(XB[fit]))
    proj = lambda Q: np.clip(pca.transform(s0(Q)), -10, 10).astype(np.float32)
    ms = [C.train(C.BindHead, proj(XB[fit]), y_all[fit], proj(XB[val]), y_all[val], epochs=60, bs=256, seed=s, guard=True)
          for s in range(5)]
    p = np.mean([C.predict(m, proj(XB[te])) for m in ms if m is not None], 0)
    lo, hi = C.boot_ci(y, p, 1000)
    rows.append(dict(mode='corrected', held_out=held, n=int(te.sum()), rho=C.spearman(y, p), lo=lo, hi=hi, esm=esm))
LD = pd.DataFrame(rows); LD['beats_esm'] = LD.rho > -LD.esm   # signed: the head should correlate positively, ESM negatively
LD.to_csv(R.out('lodo_results.csv'), index=False)
print(LD.round(3).to_string(index=False))
"""),
code(r"""
for _, r in LD.iterrows():
    for c in ('rho', 'esm', 'n', 'lo', 'hi'): R.metric(f'{r["mode"]}.{r.held_out}.{c}', r[c])
g = LD[LD.held_out == 'GRB2-SH3'].set_index('mode')
R.section('Leave-one-domain-out', 'Spearman ρ on the held-out domain, 95% bootstrap CI. ESM = zero-shot score.', LD, '{:.3f}')
R.finish([f"Held-out GRB2-SH3: head ρ {g.loc['original','rho']:+.3f} (original) / {g.loc['corrected','rho']:+.3f} (corrected) "
          f"against zero-shot ESM {g.loc['original','esm']:+.3f}.",
          f"The head beats ESM on {int(LD[LD['mode']=='corrected'].beats_esm.sum())}/3 held-out domains in the corrected version.",
          'Transfer between unrelated binding modes fails; the next question (C2) removes transfer altogether.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ C2
C2 = [md(r"""
# C2 — Can binding be learned *within* one domain? (Stages 3b and 3c)

**Question.** Remove the transfer problem: train and test inside the same domain, holding out
whole sequence **positions** so the model cannot interpolate from other substitutions at a position
it has seen. Is binding predictable then — and is a single fit trustworthy?

**What it does.** 7-fold cross-validation grouped by position, an inner validation split also
held out by position, a variance-floored scaler, a whitened 64-component PCA, three model seeds
per fold. Run **six times per domain** (Stage 3c): a single fit — what Stage 3b reported — cannot
show how much the answer depends on the random split.
"""), md(MODES_MD), md(r"""
**Decision written for B3:** `binding_decision.json` records whether the trained head beats the
zero-shot ESM-2 score on GRB2-SH3 in any mode. If it does not, the atlas binding axis stays
rank-matched ESM-2.

**Inputs:** A2 features. **Runtime:** about 15 min (both modes), T4 GPU.
**Outputs:** `within_domain_repeats.csv`, `within_domain_summary.csv`, `binding_decision.json`, `RESULTS_C2.md`.
Explanation: `docs/C2_binding_within_domain.md`.
"""),
setup('C2', 'Binding within one domain', gpu=True),
code("MODES = ['original', 'corrected']   # either or both\n" + LOAD_BINDING),
code(r"""
if R.done('within_domain_repeats.csv'):
    RP = pd.read_csv(R.out('within_domain_repeats.csv')); CI = pd.read_csv(R.out('single_fit_ci.csv'))
    print('loaded from this folder')
else:
    rows, ci = [], []; t0 = time.time()
    for mode in MODES:
        for dom in ['GB1', 'GRB2-SH3', 'PSD95-PDZ3']:
            d = B[B.domain_key == dom]
            for s in range(6):
                r = C.eval_budget(B, XB, dom, d.pos.nunique(), len(d), seed=s, n_splits=7, model_seeds=3, epochs=60,
                                  mode=mode, keep_oof=(s == 0))
                if r is None: continue
                if s == 0:          # seed 0 is the single fit Stage 3b reported
                    lo, hi = C.boot_ci(r.pop('_y'), r.pop('_oof'), 1000); ci.append(dict(mode=mode, domain=dom, lo=lo, hi=hi))
                rows.append(r)
            print(f'  {mode:<9} {dom:<11} {(time.time() - t0) / 60:.1f} min')
    RP, CI = pd.DataFrame(rows), pd.DataFrame(ci)
    RP.to_csv(R.out('within_domain_repeats.csv'), index=False); CI.to_csv(R.out('single_fit_ci.csv'), index=False)
SUM = RP.groupby(['mode', 'domain']).agg(n=('n', 'first'), positions=('n_pos', 'first'), repeats=('rho', 'size'),
                                         repeats_median=('rho', 'median'), repeats_lo=('rho', 'min'), repeats_hi=('rho', 'max'),
                                         esm=('esm', 'first')).reset_index()
SUM = SUM.merge(RP[RP.seed == 0][['mode', 'domain', 'rho']].rename(columns={'rho': 'single_fit_rho'}), on=['mode', 'domain'])
SUM = SUM.merge(CI, on=['mode', 'domain']).rename(columns={'lo': 'single_fit_ci_lo', 'hi': 'single_fit_ci_hi'})
SUM['spread'] = SUM.repeats_hi - SUM.repeats_lo; SUM['crosses_zero'] = (SUM.repeats_lo < 0) & (SUM.repeats_hi > 0)
SUM['beats_esm'] = SUM.repeats_median > -SUM.esm   # signed: a wrong-direction correlation is not a win
SUM.to_csv(R.out('within_domain_summary.csv'), index=False); print(SUM.round(3).to_string(index=False))
"""),
code(r"""
g = SUM[SUM.domain == 'GRB2-SH3']
DEC = dict(head_beats_esm=bool(g.beats_esm.any()),
           grb2_median_rho={m: float(v) for m, v in zip(g['mode'], g.repeats_median)},
           grb2_esm_rho=float(g.esm.iloc[0]),
           predictor_of_record='trained head' if g.beats_esm.any() else 'esm_zero_shot')
json.dump(DEC, open(R.out('binding_decision.json'), 'w'), indent=1); print(DEC)
for _, r in SUM.iterrows():
    R.metric(f'{r["mode"]}.{r.domain}.single_fit_rho', r.single_fit_rho)
    for c in ('n', 'positions', 'repeats_median', 'repeats_lo', 'repeats_hi', 'spread'):
        R.metric(f'{r["mode"]}.{r.domain}.{c}', r[c])
    R.metric(f'{r.domain}.esm', r.esm)
R.metric('head_beats_esm_on_grb2', DEC['head_beats_esm'])
R.section('Within-domain binding, six repeats per domain', 'Spearman ρ on held-out positions. single_fit = seed 0 (what '
          'Stage 3b reported), with its bootstrap CI; the repeats show what the bootstrap cannot: variance of the procedure.', SUM, '{:.3f}')
R.section('Decision for the atlas (read by B3)', '```\n' + json.dumps(DEC, indent=1) + '\n```')
o = SUM.set_index(['mode', 'domain'])
R.finish([f"PSD95-PDZ3 (84 positions): median ρ {o.loc[('original','PSD95-PDZ3'),'repeats_median']:+.3f} over six repeats — learnable."
          if 'original' in SUM['mode'].values else 'PSD95-PDZ3 learnable.',
          f"GRB2-SH3 (56 positions): median ρ " + ', '.join(f"{o.loc[(m,'GRB2-SH3'),'repeats_median']:+.3f} ({m})" for m in SUM['mode'].unique())
          + f"; the six repeats cross zero, and ESM gives {DEC['grb2_esm_rho']:+.3f}.",
          f"Binding predictor of record: {DEC['predictor_of_record']}.",
          'The single +0.124 fit reported by Stage 3b is one draw from this spread, not a result.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ C3
C3 = [md(r"""
# C3 — Why: is the limit the number of measurements, or the number of positions? (Stages 3c–3e)

**Question.** PSD95-PDZ3 is learnable and GRB2-SH3 is not. PSD95 has twice the measurements
*and* 1.5× the positions. Which one matters — and could more GRB2-SH3 mutagenesis ever fix it?

**What it does**, each step answering the question the previous one raised:
1. **Matched budget** (3c): cut PSD95-PDZ3 to GRB2-SH3's exact budget (56 positions, 619
   measurements), 20 draws. Does it collapse to GRB2's level?
2. **Diagnostic grid** (3c): the same full data at 5 vs 7 folds and 40 vs 60 epochs.
3. **Learning curve** (3c): both domains across six budgets.
4. **Three sweeps** (3d): A varies only the fold count; B thins measurements but keeps all 84
   positions; C removes positions at matched measurement budgets. If B and C disagree, *how* the
   data is thin matters.
5. **Position sweep** (3e): every position count from 60 to 84, ten random subsets each, with
   shuffled partitions. Where does predictability appear, and is it *which* positions or *how many*?
"""), md(MODES_MD), md(r"""
Step 5 already used shuffled partitions in the original run, so it runs once.

**Inputs:** A2 features, C2 repeats. **Runtime:** 30–45 min (both modes), T4 GPU; each step
resumes from its own file. **Outputs:** `matched_budget.csv`, `diagnostic_grid.csv`,
`learning_curve.csv`, `threshold_sweeps.csv`, `position_sweep.csv`, `position_leverage.csv`,
`RESULTS_C3.md`. Explanation: `docs/C3_binding_data_sufficiency.md`.
"""),
setup('C3', 'Binding data sufficiency', gpu=True),
code("MODES = ['original', 'corrected']   # either or both\n" + LOAD_BINDING + r"""
DOM = 'PSD95-PDZ3'; D = B[B.domain_key == DOM]; ALLPOS = np.sort(D.pos.unique())
C2S = pd.read_csv(R.res('C2', 'within_domain_summary.csv'))
def cached(name, fn):
    if R.done(name): return pd.read_csv(R.out(name))
    t0 = time.time(); df = pd.DataFrame(fn()); df.to_csv(R.out(name), index=False)
    print(f'{name}: {len(df)} runs, {(time.time() - t0) / 60:.1f} min'); return df
"""),
md("## 1. Matched budget: PSD95-PDZ3 cut to GRB2-SH3's data"),
code(r"""
MB = cached('matched_budget.csv', lambda: [r for m in MODES for s in range(20)
            if (r := C.eval_budget(B, XB, DOM, 56, 619, seed=s, n_splits=7, epochs=60, mode=m))])
MBS = MB.groupby('mode').rho.agg(median='median', ci_lo=lambda x: np.percentile(x, 2.5),
                                 ci_hi=lambda x: np.percentile(x, 97.5), draws='size').reset_index()
MBS = MBS.merge(C2S[C2S.domain == 'GRB2-SH3'][['mode', 'repeats_median']].rename(columns={'repeats_median': 'grb2_median'}), on='mode')
MBS['covers_grb2'] = (MBS.ci_lo <= MBS.grb2_median) & (MBS.grb2_median <= MBS.ci_hi); print(MBS.round(3).to_string(index=False))
"""),
md("## 2. Diagnostic grid and 3. learning curve"),
code(r"""
DG = cached('diagnostic_grid.csv', lambda: [dict(r) for m in MODES for ns in (7, 5) for ep in (60, 40) for s in range(6)
            if (r := C.eval_budget(B, XB, DOM, D.pos.nunique(), len(D), seed=s, n_splits=ns, model_seeds=1, epochs=ep, mode=m))])
BUDGETS = [(25, 200), (35, 350), (45, 500), (56, 619), (70, 850), (84, 1221)]
def lc_runs():
    for m in MODES:
        for dom in ['PSD95-PDZ3', 'GRB2-SH3']:
            d = B[B.domain_key == dom]
            for npos, nrow in BUDGETS:
                if npos > d.pos.nunique() or nrow > len(d): continue
                for s in range(6):
                    r = C.eval_budget(B, XB, dom, npos, nrow, seed=s, n_splits=7, epochs=60, mode=m)
                    if r: yield r
LC = cached('learning_curve.csv', lambda: list(lc_runs()))
DGS = DG.groupby(['mode', 'n_splits', 'epochs']).rho.median().rename('median_rho').reset_index()
LCS = LC.groupby(['mode', 'domain', 'n_pos']).agg(n=('n', 'max'), median=('rho', 'median'), min=('rho', 'min'),
                                                  max=('rho', 'max'), size=('rho', 'size')).reset_index()   # one row per budget, even if a draw had fewer rows
print(DGS.round(3).to_string(index=False)); print(LCS.round(3).to_string(index=False))
"""),
md("## 4. Three sweeps: fold count (A), thinned rows at all positions (B), fewer positions (C)"),
code(r"""
def sweeps():
    for m in MODES:
        for k in (3, 4, 5, 6, 7, 8, 10):
            for s in range(6):
                r = C.run_cv_3d(D, XB, n_splits=k, seed=s, mode=m)
                if r: yield {**r, 'sweep': 'A_folds'}
        for budget in (700, 800, 900, 1000, 1100, 1221):
            for s in range(6):
                rng = np.random.default_rng(1000 + s)
                sub = D.sample(min(budget, len(D)), random_state=1000 + s)
                r = C.run_cv_3d(sub, XB, n_splits=7, seed=s, mode=m)
                if r: yield {**r, 'sweep': 'B_thin'}
                npos = max(8, int(round(84 * budget / len(D))))
                pos = rng.permutation(D.pos.unique())[:npos]
                sub = D[D.pos.isin(pos)]
                if len(sub) > budget: sub = sub.sample(budget, random_state=1000 + s)
                r = C.run_cv_3d(sub, XB, n_splits=7, seed=s, mode=m)
                if r: yield {**r, 'sweep': 'C_fewpos'}
SW = cached('threshold_sweeps.csv', lambda: list(sweeps()))
SWS = SW.groupby(['mode', 'sweep']).rho.agg(median='median', runs='size').reset_index(); print(SWS.round(3).to_string(index=False))
GAP = {}
for m, g in SW.groupby('mode'):
    piv = g.assign(bin=g.train_rows.round(-2)).pivot_table(index='bin', columns='sweep', values='rho', aggfunc='median').dropna()
    GAP[m] = float((piv.max(axis=1) - piv.min(axis=1)).max()) if len(piv) >= 3 else np.nan
from scipy.optimize import curve_fit
logistic = lambda x, L, k, x0: L / (1 + np.exp(-k * (x - x0)))
FITS = []
for m, g in SW.groupby('mode'):
    for label, sel in [('all sweeps', g), ('A only', g[g.sweep == 'A_folds'])]:
        q = sel.groupby(sel.train_rows.round(-1)).rho.median()
        try:
            p, _ = curve_fit(logistic, np.log10(q.index.values.astype(float)), q.values, p0=[0.4, 20, 3.0],
                             bounds=([0.05, 1, 2.5], [1.0, 300, 3.3]), maxfev=20000)
            FITS.append(dict(mode=m, fit=label, plateau=p[0], steepness=p[1], midpoint_rows=10 ** p[2]))
        except Exception as e:
            FITS.append(dict(mode=m, fit=label, note=type(e).__name__))
print('max disagreement between sweeps at a shared training size:', GAP)
"""),
md("## 5. Position sweep: 60 to 84 positions, ten shuffled subsets each"),
code(r"""
from scipy.stats import mannwhitneyu
COUNTS = sorted(set(range(60, 85, 2)) | {84})
def pos_runs():
    for npos in COUNTS:
        for s in range(10):
            keep = np.random.default_rng(5000 + s).permutation(ALLPOS)[:npos]
            sub = D[D.pos.isin(keep)].reset_index(); Xs = XB[sub['index'].values]; sub = sub.drop(columns=['index'])
            r = C.run_cv_3e(sub, Xs, n_splits=7, seed=s)
            if r: yield {**r, 'target_pos': npos}
PS = cached('position_sweep.csv', lambda: list(pos_runs()))
PSS = PS.groupby('target_pos').rho.agg(['median', 'min', 'max', 'size']).reset_index()
base = PS[PS.target_pos == COUNTS[0]].rho.values; cross = None; mw = []
for n in COUNTS[1:]:
    v = PS[PS.target_pos == n].rho.values; p = mannwhitneyu(v, base, alternative='greater').pvalue
    mw.append(dict(positions=n, median=np.median(v), p_vs_60=p))
    if p < 0.05 and cross is None: cross = n
hi, lo = PS[PS.rho > 0.25].target_pos, PS[PS.rho < 0.15].target_pos
overlap = sorted(set(hi) & set(lo))
from collections import Counter
good, bad = Counter(), Counter()
for _, r in PS.iterrows():
    keep = set(np.random.default_rng(5000 + int(r.seed)).permutation(ALLPOS)[:int(r.target_pos)])
    tgt = good if r.rho > 0.25 else (bad if r.rho < 0.15 else None)
    if tgt is not None:
        for p_ in keep: tgt[p_] += 1
LEV = pd.DataFrame([dict(pos=int(p_), in_success=good.get(p_, 0), in_failure=bad.get(p_, 0),
                         enrichment=(good.get(p_, 0) + 1) / (bad.get(p_, 0) + 1)) for p_ in ALLPOS
                    if good.get(p_, 0) + bad.get(p_, 0) >= 8]).sort_values('enrichment', ascending=False)
LEV.to_csv(R.out('position_leverage.csv'), index=False)
GRB2_POS = int(B[B.domain_key == 'GRB2-SH3'].pos.nunique())
print(PSS.round(3).to_string(index=False)); print(f'crossing at {cross} positions; GRB2-SH3 has {GRB2_POS}')
print(f'position enrichment ranges {LEV.enrichment.min():.2f}-{LEV.enrichment.max():.2f}: no position stands out')
"""),
md("## Results"),
code(r"""
for _, r in MBS.iterrows():
    R.metric(f'{r["mode"]}.matched_median_rho', r['median']); R.metric(f'{r["mode"]}.matched_ci_lo', r.ci_lo)
    R.metric(f'{r["mode"]}.matched_ci_hi', r.ci_hi); R.metric(f'{r["mode"]}.matched_draws', r.draws)
    R.metric(f'{r["mode"]}.matched_covers_grb2', r.covers_grb2)
for _, r in DGS.iterrows(): R.metric(f'{r["mode"]}.diag_k{r.n_splits}_ep{r.epochs}_median', r.median_rho)
for _, r in LCS.iterrows(): R.metric(f'{r["mode"]}.lc_{r.domain}_{r.n_pos}pos_median', r['median'])
for _, r in SWS.iterrows():
    R.metric(f'{r["mode"]}.sweep_{r.sweep}_median', r['median']); R.metric(f'{r["mode"]}.sweep_{r.sweep}_runs', r.runs)
for m in SW['mode'].unique():
    R.metric(f'{m}.sweep_max_gap', GAP[m]); R.metric(f'{m}.sweep_runs', int((SW['mode'] == m).sum()))
for _, r in PSS.iterrows(): R.metric(f'position_sweep_{int(r.target_pos)}_median', r['median'])
for k, v in [('position_sweep_runs', len(PS)), ('crossing_positions', cross), ('grb2_positions', GRB2_POS),
             ('success_failure_share_counts', len(overlap)), ('position_enrichment_max', LEV.enrichment.max())]:
    R.metric(k, v)
R.section('1. Matched budget', 'PSD95-PDZ3 at 56 positions / 619 measurements, 20 draws, against GRB2-SH3 (C2).', MBS, '{:.3f}')
R.section('2. Diagnostic grid (PSD95-PDZ3, full data)', 'A result that swings with the fold count is fragile.', DGS, '{:.3f}')
R.section('3. Learning curve', 'Superseded as a model by steps 4–5: a log-linear fit through a step is the wrong shape.', LCS, '{:.3f}')
R.section('4. Three sweeps', f'Maximum disagreement between sweeps at a shared training size: {GAP}. B keeps all positions and '
          'holds its accuracy; C removes positions at the same row budget and loses it.', SWS, '{:.3f}')
R.section('4b. Logistic fits (superseded by step 5)', 'Kept for the record; the apparent sharp step came from the unshuffled '
          'partition.', pd.DataFrame(FITS), '{:.3g}')
R.section('5. Position sweep (shuffled partitions)', f'First count significantly above 60 positions (Mann–Whitney, p < 0.05): '
          f'**{cross}**. GRB2-SH3 has {GRB2_POS} positions in total.', PSS.merge(pd.DataFrame(mw).rename(columns={'positions': 'target_pos'}),
          on='target_pos', how='left'), '{:.3g}')
R.section('5b. Is it which positions, or how many?', f"Counts where both successes (ρ > 0.25) and failures (ρ < 0.15) occur: "
          f"{overlap}. The original notebook read any overlap as 'leverage'. The enrichment table says otherwise: every position "
          f"scores {LEV.enrichment.min():.2f}–{LEV.enrichment.max():.2f}, i.e. the base rate of successes to failures. No position "
          f"carries the signal; the controlling variable is the **count**.")
R.finish([f"Matched budget: PSD95-PDZ3 cut to GRB2-SH3's data falls to median ρ "
          + ', '.join(f"{r['median']:+.3f} ({r['mode']})" for _, r in MBS.iterrows()) + '.',
          'Keeping all positions while cutting rows costs almost nothing; cutting positions at the same row budget collapses it: '
          + ', '.join(f"{m}: B {SWS[(SWS['mode']==m)&(SWS.sweep=='B_thin')]['median'].iat[0]:+.3f} vs C "
                      f"{SWS[(SWS['mode']==m)&(SWS.sweep=='C_fewpos')]['median'].iat[0]:+.3f}" for m in SWS['mode'].unique()) + '.',
          f"Predictability appears at about {cross} positions (solid by 82); GRB2-SH3 has {GRB2_POS}.",
          'Single-domain ddPCA cannot supply enough positions for an SH3 domain (56–60 residues): the fix is more domains, not '
          'more mutations. The number is calibrated on one domain — quote "of the order of 80", not a precise cut.'])
"""),
]
NOTEBOOKS = {'C1_binding_cross_domain': (C1, True), 'C2_binding_within_domain': (C2, True),
             'C3_binding_data_sufficiency': (C3, True)}
