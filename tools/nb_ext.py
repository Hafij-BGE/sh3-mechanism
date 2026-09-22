"""Extensions chosen from the upgrade roadmap: B6 virtual saturation mutagenesis (L3/L4, G4) and
C4 an ESM-independent specificity axis from experimental PWMs (F1-F3)."""
from nbkit import md, code, setup

# ════════════════════════════════════════════════════════════════════════ B6
B6 = [md(r"""
# B6 — Virtual saturation mutagenesis of every human SH3 domain (roadmap L3/L4, G4)

**Question.** What would a deep mutational scan of every SH3 domain in the atlas look like, and
where do the cancer mutations that actually occur sit within that landscape?

**What it does.** Predicts ΔΔG_fold, with its conformal interval, for **all 19 substitutions at
every position** of the 310 atlas SH3 domains (about 350,000 variants) with the folding head from
B1. The features are exactly those used for the observed variants (embeddings and ESM log-odds are
per domain, so nothing new has to be run through ESM), and the notebook **checks** that the
observed atlas variants get the same prediction as in B1.

It then maps the family-wide landscape on the 56-position GRB2-SH3 frame, and compares observed
cancer variants with all possible substitutions. Because tumours can mostly reach only amino-acid
changes that need one nucleotide substitution, the comparison is also made against the
**single-nucleotide-reachable** subset (from the genetic code; the actual codons are not known).
This is **not** a mutational-opportunity model (roadmap G1 needs trinucleotide context).

**Inputs:** A2 embeddings/log-odds/features, B1 models and atlas predictions, B3 conformal quantile.
**Runtime:** about 5 min (CPU is fine). **Outputs:** `sh3_virtual_dms.parquet`, `family_position_map.csv`,
`domain_summary.csv`, `RESULTS_B6.md`. Explanation: `docs/B6_virtual_saturation_mutagenesis.md`.
"""),
setup('B6', 'Virtual saturation mutagenesis', pip='biopython'),
code(r"""
from Bio import Align
from Bio.Align import substitution_matrices
EMB = C.load_embeddings(R.res('A2', 'esm_domain_embeddings.npz'))
LO = C.load_embeddings(R.res('A2', 'esm_logodds.npz'))
AT = pd.read_parquet(R.res('A2', 'features_atlas.parquet'))
STR = pd.read_csv(R.res('A2', 'structure_features.csv'))
DD = pd.read_parquet(R.res('A2', 'features_ddpca.parquet'), columns=['domain_key', 'wt_seq'])
FOLD, SC_M, SC_SD = C.load_fold_models(R.res('B1', 'models.pt'))
OBS = pd.read_parquet(R.res('B3', 'atlas_predictions.parquet'))
Q90 = json.load(open(R.res('B3', 'metrics_B3.json')))['metrics']['conformal_q90']; EPS = 0.05
DOMS = AT.drop_duplicates('domain_key')[['domain_key', 'gene', 'uniprot', 'domain_idx', 'wt_seq']].reset_index(drop=True)
print(f'{len(DOMS)} domains, {DOMS.wt_seq.str.len().sum():,} positions, {19 * DOMS.wt_seq.str.len().sum():,} substitutions')
"""),
md("## 1. Every substitution, same features, same model"),
code(r"""
AAS = list('ACDEFGHIKLMNPQRSTVWY'); AAPOS = {a: i for i, a in enumerate(AAS)}
B62 = substitution_matrices.load('BLOSUM62')
rows = []
for k, s in zip(DOMS.domain_key, DOMS.wt_seq):
    for p, w in enumerate(s, 1):
        for m in AAS:
            if m != w: rows.append((k, p, w, m))
V = pd.DataFrame(rows, columns=['domain_key', 'pos', 'wt_aa', 'mut_aa']).merge(DOMS, on='domain_key')
lo = np.stack([LO[k][p - 1] for k, p in zip(V.domain_key, V.pos)]); r = np.arange(len(V))
w = V.wt_aa.map(AAPOS).values; mu = V.mut_aa.map(AAPOS).values
V['esm_score'] = lo[r, mu] - lo[r, w]; V['esm_wt_logp'] = lo[r, w]; V['esm_entropy'] = -(np.exp(lo) * lo).sum(1); del lo
V['dom_len'] = V.wt_seq.str.len(); V['rel_pos'] = V.pos / V.dom_len
V['d_hydropathy'] = V.mut_aa.map(C.KD) - V.wt_aa.map(C.KD); V['d_volume'] = V.mut_aa.map(C.VOL) - V.wt_aa.map(C.VOL)
V['d_charge'] = V.mut_aa.map(C.CHG).fillna(0) - V.wt_aa.map(C.CHG).fillna(0)
V['blosum62'] = [B62[a][b] for a, b in zip(V.wt_aa, V.mut_aa)]
V['to_proline'] = (V.mut_aa == 'P').astype(int); V['from_glycine'] = (V.wt_aa == 'G').astype(int); V['to_glycine'] = (V.mut_aa == 'G').astype(int)
X, V = C.build_X(V, EMB)
P = C.fold_scores(FOLD, X, SC_M, SC_SD, clip=10); del X
V['pred_ddG_fold'], V['sd_fold'] = P.mean(0), P.std(0)
V['fold_lo'] = V.pred_ddG_fold - Q90 * (V.sd_fold + EPS); V['destabilising'] = V.fold_lo >= 1.0
# consistency: observed atlas variants must get exactly the B1/B3 prediction
chk = OBS[['domain_key', 'pos', 'wt_aa', 'mut_aa', 'pred_ddG_fold']].merge(V[['domain_key', 'pos', 'wt_aa', 'mut_aa', 'pred_ddG_fold']],
                                                                           on=['domain_key', 'pos', 'wt_aa', 'mut_aa'], suffixes=('_obs', '_virtual'))
MAXDIFF = float((chk.pred_ddG_fold_obs - chk.pred_ddG_fold_virtual).abs().max())
print(f'{len(V):,} virtual variants | {len(chk):,} observed variants matched, max prediction difference {MAXDIFF:.2e}')
assert len(chk) == len(OBS) and MAXDIFF < 1e-4, 'virtual scan does not reproduce the observed-variant predictions'
"""),
md("## 2. Which substitutions can a single nucleotide change reach?"),
code(r"""
CODE = {'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L','ATT':'I','ATC':'I','ATA':'I','ATG':'M',
        'GTT':'V','GTC':'V','GTA':'V','GTG':'V','TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
        'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A','TAT':'Y','TAC':'Y','CAT':'H','CAC':'H',
        'CAA':'Q','CAG':'Q','AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E','TGT':'C','TGC':'C',
        'TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R','AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G'}
reach = set()
for cod, a in CODE.items():
    for i in range(3):
        for b in 'ACGT':
            c2 = cod[:i] + b + cod[i + 1:]
            if c2 in CODE and CODE[c2] != a: reach.add((a, CODE[c2]))
V['snv_reachable'] = [(a, b) in reach for a, b in zip(V.wt_aa, V.mut_aa)]
obs_keys = set(zip(OBS.domain_key, OBS.pos, OBS.mut_aa)); V['observed_in_cancer'] = [(k, p, m) in obs_keys for k, p, m in zip(V.domain_key, V.pos, V.mut_aa)]
print(f"single-nucleotide-reachable: {V.snv_reachable.mean():.1%} of substitutions; observed cancer variants reachable: "
      f"{V[V.observed_in_cancer].snv_reachable.mean():.1%}")
"""),
md("## 3. The family landscape and where cancer mutations sit"),
code(r"""
al = Align.PairwiseAligner(mode='global', open_gap_score=-11, extend_gap_score=-1); al.match_score = 2; al.mismatch_score = -1
ref_seq = DD[DD.domain_key == 'GRB2-SH3'].wt_seq.iat[0]
def to_ref(seq):
    a = al.align(ref_seq, seq)[0]
    return {qs + k + 1: rs_ + k + 1 for (rs_, re_), (qs, qe) in zip(a.aligned[0], a.aligned[1]) for k in range(re_ - rs_)}
REFMAP = {k: to_ref(s) for k, s in zip(DOMS.domain_key, DOMS.wt_seq)}
V['ref_pos'] = [REFMAP[k].get(int(p), np.nan) for k, p in zip(V.domain_key, V.pos)]
ref = STR[STR.domain_key == 'GRB2-SH3'].set_index('pos')
FAM = V.dropna(subset=['ref_pos']).groupby('ref_pos').agg(domains=('domain_key', 'nunique'), mean_pred=('pred_ddG_fold', 'mean'),
                                                        frac_destabilising=('destabilising', 'mean'),
                                                        observed_variants=('observed_in_cancer', 'sum')).reset_index()
FAM['rsasa'] = FAM.ref_pos.map(ref.rsasa); FAM['buried'] = FAM.rsasa < 0.25; FAM['interface'] = FAM.ref_pos.map(ref.dist_peptide) < 5.0
FAM.round(4).to_csv(R.out('family_position_map.csv'), index=False)
DSUM = V.groupby(['domain_key', 'gene']).agg(length=('pos', 'max'), frac_destabilising=('destabilising', 'mean'),
                                            mean_pred=('pred_ddG_fold', 'mean'), observed=('observed_in_cancer', 'sum')).reset_index()
DSUM.to_csv(R.out('domain_summary.csv'), index=False)
cmp_rows = []
for label, pool in [('all possible substitutions', V), ('single-nucleotide-reachable only', V[V.snv_reachable])]:
    cmp_rows.append(dict(set=label, variants=len(pool), frac_destabilising=pool.destabilising.mean(),
                         median_pred=pool.pred_ddG_fold.median()))
o = V[V.observed_in_cancer]
cmp_rows.append(dict(set='observed in cancer', variants=len(o), frac_destabilising=o.destabilising.mean(), median_pred=o.pred_ddG_fold.median()))
CMPT = pd.DataFrame(cmp_rows)
# within the same domains and the reachable set: are observed variants depleted of damage? (permutation, matched on domain)
pool = V[V.snv_reachable]; rng = np.random.default_rng(0); need = o[o.snv_reachable].domain_key.value_counts()
idx = {k: np.flatnonzero(pool.domain_key.values == k) for k in need.index}; pv = pool.destabilising.values
null = np.array([sum(pv[rng.choice(idx[k], n, replace=False)].sum() for k, n in need.items()) / need.sum() for _ in range(1000)])
OBS_FR = float(o[o.snv_reachable].destabilising.mean()); P_LOW = float((np.sum(null <= OBS_FR) + 1) / 1001)
V.drop(columns=['wt_seq']).to_parquet(R.out('sh3_virtual_dms.parquet'), index=False)
print(CMPT.round(4).to_string(index=False)); print(f'observed {OBS_FR:.4f} vs domain-matched reachable null median {np.median(null):.4f}, p(depleted) = {P_LOW:.3g}')
"""),
md("## Results"),
code(r"""
for k, v in [('virtual_variants', len(V)), ('domains', V.domain_key.nunique()), ('max_diff_vs_observed', MAXDIFF),
             ('frac_destabilising_all_possible', CMPT.frac_destabilising[0]), ('frac_destabilising_reachable', CMPT.frac_destabilising[1]),
             ('frac_destabilising_observed', CMPT.frac_destabilising[2]), ('frac_destabilising_observed_reachable', OBS_FR),
             ('matched_null_median', float(np.median(null))), ('p_observed_depleted', P_LOW),
             ('rho_family_damage_vs_burial', C.spearman(FAM.dropna(subset=['rsasa']).mean_pred, -FAM.dropna(subset=['rsasa']).rsasa))]:
    R.metric(k, v)
R.section('Observed cancer variants against every possible substitution', 'Destabilising = lower 90% interval bound ≥ 1 kcal/mol.', CMPT, '{:.4f}')
R.section('Domain-matched test', f'Observed single-nucleotide-reachable variants: {OBS_FR:.2%} destabilising; random reachable '
          f'substitutions from the same domains: median {np.median(null):.2%} (1,000 draws); one-sided p that observed variants are '
          f'depleted of damage = {P_LOW:.3g}. Depletion would be the signature of purifying selection; enrichment of positive '
          'selection. Codon usage and trinucleotide context are not modelled.')
R.section('Family map: the 15 most damage-sensitive aligned positions', '', FAM.sort_values('mean_pred', ascending=False).head(15), '{:.3f}')
R.finish([f"{len(V):,} virtual substitutions predicted across {V.domain_key.nunique()} SH3 domains; the observed variants reproduce B1 "
          f"exactly (max difference {MAXDIFF:.1e}).",
          f"{CMPT.frac_destabilising[0]:.1%} of all possible substitutions are called destabilising "
          f"({CMPT.frac_destabilising[1]:.1%} of single-nucleotide-reachable ones) against {CMPT.frac_destabilising[2]:.1%} of observed cancer variants.",
          f"Domain-matched: observed {OBS_FR:.2%} vs expected {np.median(null):.2%} (p depleted = {P_LOW:.2g}).",
          'A citable resource: a predicted folding landscape for every human SH3 domain in the atlas, with intervals.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ C4
C4 = [md(r"""
# C4 — An independent specificity axis from experimental PWMs (roadmap F1–F3)

**Why.** C1–C3 show that ΔΔG of binding cannot be learned from ddPCA data for SH3 domains, so the
atlas "rewiring" flag rests on zero-shot ESM-2 (B3). Both atlas axes therefore come from ESM, and
the thesis cannot test whether folding and binding effects really separate. This program tries
the one route the data allows: learn **binding specificity** from **experimental** phage-display
profiles (154 PWMs for human SH3 domains, Teyra et al. 2017) and use it as a second axis.

**What it does.**
1. Summarises each PWM as an **information-weighted amino-acid preference profile** (20 numbers).
   PWMs have different widths and no shared peptide frame, so position-by-position comparison is
   not possible; the profile is alignment-free.
2. Learns profile ← domain sequence (mean ESM-2 embedding), by ridge regression in centred
   log-ratio space, and tests it **leaving out whole clusters of related domains** (≥40 % identity),
   against two baselines: the average profile, and the profile of the most similar training domain.
3. **Pre-specified decision rule.** The axis counts as validated only if (a) the median centred
   correlation between predicted and observed profile has a 95 % bootstrap CI above zero **and**
   (b) the model beats the average profile on a sign test (p < 0.05).
4. If validated, scores every atlas variant: **rewiring = Jensen–Shannon distance between the
   predicted profiles of the wild-type and mutant domain**, then asks whether rewiring concentrates
   at the peptide interface and whether it is independent of predicted folding damage.

If the rule fails, the scores are still written but labelled *not validated*, and no rewiring claim
is made. A clear negative is reportable, just like the binding result.

**Inputs:** `input/datasets/SH3_PWM.zip`, `HumanSH3TableS2.xlsx` (upload these two), A0 atlas, A2
embeddings/structure, B1/B3 predictions. **Runtime:** about 10 min, **T4 GPU** (ESM passes for 6,884
mutant domains). **Outputs:** `pwm_profiles.csv`, `specificity_cv.csv`, `specificity_decision.json`,
`atlas_rewiring.parquet`, `RESULTS_C4.md`. Explanation: `docs/C4_specificity_axis.md`.
"""),
setup('C4', 'Independent specificity axis (PWMs)', gpu=True, pip='biopython openpyxl'),
code(r"""
import zipfile, re, torch
from Bio import Align
from scipy.spatial.distance import jensenshannon
from scipy.stats import mannwhitneyu
from sklearn.linear_model import Ridge
R.verify_inputs(['input/datasets/SH3_PWM.zip', 'input/datasets/HumanSH3TableS2.xlsx'])
AAS = list('ACDEFGHIKLMNPQRSTVWY')
Z = zipfile.ZipFile(f'{R.IN}/datasets/SH3_PWM.zip'); pwm = {}
for n in Z.namelist():
    if not n.endswith('.txt') or '__MACOSX' in n: continue
    rows = {p[0]: [float(x) for x in p[1:]] for p in (l.split() for l in Z.read(n).decode().splitlines()) if p and p[0] in AAS and len(p) > 1}
    if len(rows) == 20:
        M_ = np.array([rows[a] for a in AAS]); pwm[os.path.basename(n)[:-4]] = M_ / M_.sum(0, keepdims=True)   # columns sum to 20 as shipped
raw = pd.read_excel(f'{R.IN}/datasets/HumanSH3TableS2.xlsx', header=None)
h = raw.index[raw.apply(lambda r: r.astype(str).str.strip().eq('Domain ID').any(), axis=1)][0]
S2 = pd.read_excel(f'{R.IN}/datasets/HumanSH3TableS2.xlsx', skiprows=h); S2.columns = [str(c).strip() for c in S2.columns]
S2 = S2.dropna(subset=['Domain ID', 'Domain Sequence']); S2['did'] = S2['Domain ID'].astype(str).str.replace('*', '', regex=False).str.strip()
seq_of = dict(zip(S2.did, S2['Domain Sequence'].astype(str).str.strip()))
def profile(P):
    ic = np.log2(20) + (P * np.log2(np.clip(P, 1e-12, 1))).sum(0)
    return (P * ic).sum(1) / ic.sum()
recs, unmatched = [], []
for name, P in pwm.items():
    did = re.sub(r'-\d+$', '', name).replace('_', '/')
    if did in seq_of: recs.append(dict(pwm=name, domain=did, seq=seq_of[did], width=P.shape[1], **dict(zip(AAS, profile(P)))))
    else: unmatched.append(name)
PR = pd.DataFrame(recs); PR.to_csv(R.out('pwm_profiles.csv'), index=False)
DOM = PR.groupby(['domain', 'seq'])[AAS].mean().reset_index()          # domains with two PWMs: average profile
print(f'{len(pwm)} PWMs, {len(PR)} matched to a domain sequence, {DOM.domain.nunique()} domains; unmatched: {unmatched}')
"""),
md("## 1. Features, clusters of related domains, and the cross-validated test"),
code(r"""
from transformers import AutoTokenizer, AutoModelForMaskedLM
tok = AutoTokenizer.from_pretrained('facebook/esm2_t33_650M_UR50D')
esm = AutoModelForMaskedLM.from_pretrained('facebook/esm2_t33_650M_UR50D').to(C.DEV).eval()
if C.DEV == 'cuda': esm = esm.half()
@torch.no_grad()
def mean_embed(seq):      # the same representation as A2: last hidden layer, mean over residues
    enc = tok(seq, return_tensors='pt').to(C.DEV)
    return esm(**enc, output_hidden_states=True).hidden_states[-1][0, 1:len(seq) + 1].float().mean(0).cpu().numpy()
XP = np.stack([mean_embed(s) for s in DOM.seq])
clr = lambda P: np.log(np.clip(P, 1e-6, None)) - np.log(np.clip(P, 1e-6, None)).mean(1, keepdims=True)
soft = lambda Y: np.exp(Y) / np.exp(Y).sum(1, keepdims=True)
Y = clr(DOM[AAS].values)
idal = Align.PairwiseAligner(open_gap_score=-11, extend_gap_score=-1); idal.match_score = 1; idal.mismatch_score = 0
n = len(DOM); ID = np.eye(n)
for i in range(n):
    for j in range(i + 1, n):
        ID[i, j] = ID[j, i] = idal.score(DOM.seq[i], DOM.seq[j]) / min(len(DOM.seq[i]), len(DOM.seq[j]))
lab = np.arange(n)                                                      # single-linkage clusters at >=40% identity
for i in range(n):
    for j in range(n):
        if ID[i, j] >= 0.40: lab[lab == lab[j]] = lab[i]
print(f'{n} domains in {len(np.unique(lab))} clusters (>=40% identity)')
rows = []
for c in np.unique(lab):
    te = np.where(lab == c)[0]; tr = np.where(lab != c)[0]
    mu, sd = XP[tr].mean(0), XP[tr].std(0) + 1e-6; ybar = Y[tr].mean(0)
    alpha = max([1, 10, 100, 1000], key=lambda a: np.mean([np.corrcoef((Ridge(alpha=a).fit((XP[np.setdiff1d(tr, [k])] - mu) / sd, Y[np.setdiff1d(tr, [k])])
                                                                           .predict(((XP[k] - mu) / sd)[None])[0] - ybar), Y[k] - ybar)[0, 1]
                                                               for k in tr[::4]]))
    pred = Ridge(alpha=alpha).fit((XP[tr] - mu) / sd, Y[tr]).predict((XP[te] - mu) / sd)
    for k, t in enumerate(te):
        nn_ = tr[np.argmax(ID[t, tr])]
        rows.append(dict(domain=DOM.domain[t], cluster=int(c), alpha=alpha, nearest_identity=float(ID[t, nn_]),
                         r_model=float(np.corrcoef(pred[k] - ybar, Y[t] - ybar)[0, 1]),
                         r_nearest=float(np.corrcoef(Y[nn_] - ybar, Y[t] - ybar)[0, 1]),
                         js_model=float(jensenshannon(soft(pred[k][None])[0], DOM[AAS].values[t], base=2)),
                         js_nearest=float(jensenshannon(DOM[AAS].values[nn_], DOM[AAS].values[t], base=2)),
                         js_mean=float(jensenshannon(soft(ybar[None])[0], DOM[AAS].values[t], base=2))))
CV = pd.DataFrame(rows); CV.to_csv(R.out('specificity_cv.csv'), index=False)
bs = [np.median(np.random.default_rng(b).choice(CV.r_model, len(CV))) for b in range(2000)]
R_MED, (R_LO, R_HI) = float(CV.r_model.median()), np.percentile(bs, [2.5, 97.5])
WIN_MEAN = int((CV.js_model < CV.js_mean).sum()); WIN_NN = int((CV.js_model < CV.js_nearest).sum())
P_MEAN = C.sign_test_two_sided(WIN_MEAN, len(CV)) if WIN_MEAN > len(CV) / 2 else 1.0
VALID = bool(R_LO > 0 and P_MEAN < 0.05)
print(f'median centred r {R_MED:+.3f} [{R_LO:+.3f}, {R_HI:+.3f}] | beats the average profile on {WIN_MEAN}/{len(CV)} (p {P_MEAN:.2g}) '
      f'| beats nearest neighbour on {WIN_NN}/{len(CV)} | VALIDATED: {VALID}')
json.dump(dict(validated=VALID, median_centred_r=R_MED, ci=[float(R_LO), float(R_HI)], wins_vs_mean=WIN_MEAN,
               wins_vs_nearest=WIN_NN, domains=len(CV), sign_test_p=P_MEAN,
               rule='CI of median centred r above 0 AND sign test vs average profile p < 0.05'),
          open(R.out('specificity_decision.json'), 'w'), indent=1)
"""),
md("## 2. Score every atlas variant: rewiring = distance between predicted wild-type and mutant profiles"),
code(r"""
mu, sd = XP.mean(0), XP.std(0) + 1e-6
alpha = int(CV.alpha.mode().iat[0]); final = Ridge(alpha=alpha).fit((XP - mu) / sd, Y)
MASTER = pd.read_csv(R.res('A0', 'SH3_cancer_master.tsv'), sep='\t', usecols=['variant_id', 'wt_domain_seq', 'mut_domain_seq'])
A = pd.read_parquet(R.res('B3', 'atlas_predictions.parquet'))[['variant_id', 'domain_key', 'gene', 'pos', 'ref_pos', 'pred_ddG_fold',
                                                              'fold_lo', 'esm_score', 'mechanism']].merge(MASTER, on='variant_id')
if R.done('atlas_rewiring.parquet'):
    A = pd.read_parquet(R.out('atlas_rewiring.parquet')); print('loaded from this folder')
else:
    wt_e = {s: mean_embed(s) for s in A.wt_domain_seq.unique()}; t0 = time.time()
    mut_e = np.stack([mean_embed(s) for s in A.mut_domain_seq]); print(f'mutant embeddings {(time.time() - t0) / 60:.1f} min')
    Pw = soft(final.predict((np.stack([wt_e[s] for s in A.wt_domain_seq]) - mu) / sd)); Pm = soft(final.predict((mut_e - mu) / sd))
    A['rewiring'] = [jensenshannon(a, b, base=2) for a, b in zip(Pw, Pm)]
    A.drop(columns=['wt_domain_seq', 'mut_domain_seq']).to_parquet(R.out('atlas_rewiring.parquet'), index=False)
del esm; torch.cuda.empty_cache()
STR = pd.read_csv(R.res('A2', 'structure_features.csv')); ref = STR[STR.domain_key == 'GRB2-SH3'].set_index('pos')
A['interface'] = A.ref_pos.map(ref.dist_peptide) < 5.0; A['buried'] = A.ref_pos.map(ref.rsasa) < 0.25
a_ = A.dropna(subset=['ref_pos'])
U = mannwhitneyu(a_[a_.interface].rewiring, a_[~a_.interface].rewiring, alternative='greater')
TOP = A.rewiring >= A.rewiring.quantile(0.9); DEST = A.fold_lo >= 1.0
TWO = pd.crosstab(np.where(DEST, 'destabilising', 'not destabilising'), np.where(TOP, 'top-10% rewiring', 'other'))
print(TWO); print(f'interface vs rest: median rewiring {a_[a_.interface].rewiring.median():.4f} vs {a_[~a_.interface].rewiring.median():.4f}, p {U.pvalue:.2g}')
"""),
md("## Results"),
code(r"""
for k, v in [('pwms', len(pwm)), ('pwms_matched', len(PR)), ('domains', len(DOM)), ('clusters', int(len(np.unique(lab)))),
             ('median_centred_r', R_MED), ('median_centred_r_ci_lo', float(R_LO)), ('median_centred_r_ci_hi', float(R_HI)),
             ('wins_vs_average_profile', WIN_MEAN), ('wins_vs_nearest_neighbour', WIN_NN), ('sign_test_p', P_MEAN), ('validated', VALID),
             ('rho_rewiring_vs_predicted_fold', C.spearman(A.rewiring, A.pred_ddG_fold)),
             ('rho_rewiring_vs_esm_score', C.spearman(A.rewiring, A.esm_score)),
             ('rewiring_interface_median', float(a_[a_.interface].rewiring.median())),
             ('rewiring_other_median', float(a_[~a_.interface].rewiring.median())), ('interface_test_p', float(U.pvalue)),
             ('n_top_rewiring_not_destabilising', int((TOP & ~DEST).sum())), ('n_both_axes', int((TOP & DEST).sum()))]:
    R.metric(k, v)
R.section('Cross-validated test (whole clusters of related domains held out)', 'centred r: correlation of predicted and observed '
          'profile after removing the training average (the shared proline preference). js: Jensen–Shannon distance, lower is better.',
          CV.describe().loc[['count', 'mean', '50%', 'min', 'max']].reset_index(), '{:.3f}')
R.section('Decision', '```\n' + open(R.out('specificity_decision.json')).read() + '\n```')
R.section('Two-axis map of the atlas', ('**Validated axis.** ' if VALID else '**NOT validated — shown for completeness; no rewiring '
          'claim is made.** ') + f"Rewiring vs predicted folding damage ρ {R.metrics['rho_rewiring_vs_predicted_fold']:+.3f}; vs zero-shot "
          f"ESM ρ {R.metrics['rho_rewiring_vs_esm_score']:+.3f}. Interface positions: median rewiring "
          f"{R.metrics['rewiring_interface_median']:.4f} vs {R.metrics['rewiring_other_median']:.4f} elsewhere (one-sided p {U.pvalue:.2g}).",
          TWO.reset_index().rename(columns={'row_0': 'folding axis'}))
R.finish([f"{len(PR)} of {len(pwm)} PWMs linked to {len(DOM)} domain sequences; tested by holding out {len(np.unique(lab))} clusters of related domains.",
          f"Predicted vs observed specificity: median centred r {R_MED:+.3f} [95% CI {R_LO:+.3f}, {R_HI:+.3f}]; beats the average profile on "
          f"{WIN_MEAN}/{len(CV)} domains and the nearest-neighbour profile on {WIN_NN}/{len(CV)}.",
          f"Pre-specified rule: {'VALIDATED' if VALID else 'NOT validated'}.",
          (f"Rewiring is {'higher' if U.pvalue < 0.05 else 'not higher'} at the peptide interface (p {U.pvalue:.2g}) and correlates "
           f"ρ {R.metrics['rho_rewiring_vs_predicted_fold']:+.3f} with predicted folding damage."
           if VALID else 'Without a validated axis, the fold/rewiring separation stays untested; this is reported as a data limit.')])
"""),
]
NOTEBOOKS = {'B6_virtual_saturation_mutagenesis': (B6, False), 'C4_specificity_axis': (C4, True)}
