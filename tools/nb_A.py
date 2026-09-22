"""Part A — initial data processing: A0 cancer atlas, A1 ground truth, A2 features."""
from nbkit import md, code, setup

# ════════════════════════════════════════════════════════════════════════ A0
A0 = [md(r"""
# A0 — The SH3 cancer-variant atlas, rebuilt from raw COSMIC (Stage 0)

**Question.** Which somatic missense mutations in human cancers fall inside an SH3 domain, and
can each one be placed on the correct residue?

**What it does.** Reads the COSMIC Cancer Mutation Census and keeps a missense row only if its
position lies inside a UniProt SH3 domain **and** the wild-type residue COSMIC reports is the
residue actually present there. Rows numbered on an alternative transcript are recovered through
UniProt isoforms. The per-sample genome screens then add tumour type and hypermutation status.

**Inputs** (`input/cosmic/`, `input/uniprot/`) — all MD5-checked before use:
`cmc_export.tsv`, `Cosmic_GenomeScreensMutant_v104_GRCh38.tsv.gz`,
`Cosmic_Classification_v104_GRCh38.tsv`, `sh3_domains_human.tsv`, `sh3_proteins_seq.tsv`,
`isoforms_all.json`. The UniProt files are a frozen 2026-09-20 snapshot, so a later UniProt
release cannot change the result.

**Outputs** (`results/A0_cancer_atlas/`): `SH3_cancer_master.tsv` (the atlas),
`SH3_cancer_unmapped.tsv` (rejected rows), `qc_checks.csv`, `RESULTS_A0.md`.

**Runtime:** 10–25 min on a standard CPU runtime (no GPU needed; 6 min on a laptop). The COSMIC
files are read by streaming; the 16.8 GB genome-screens file is never unpacked.

Explanation of every step: `docs/A0_cancer_atlas.md`.
"""),
setup('A0', 'Cancer-variant atlas from raw COSMIC'),
md("## 1. Check the inputs\nA wrong or truncated file stops the run here instead of silently changing the atlas "
   "(the original project once used a copy of the genome-screens file that had stopped at 1.35 of 16.8 GB)."),
code(r"""
COSMIC = ['input/cosmic/cmc_export.tsv',
          'input/cosmic/Cosmic_GenomeScreensMutant_v104_GRCh38.tsv.gz',
          'input/cosmic/Cosmic_Classification_v104_GRCh38.tsv']
UNIPROT = ['input/uniprot/sh3_domains_human.tsv', 'input/uniprot/sh3_proteins_seq.tsv',
           'input/uniprot/isoforms_all.json']
R.verify_inputs(UNIPROT + COSMIC)
# optional: the original Stage 0 atlas, used ONLY to prove the rebuild is identical (section 5)
ORIGINAL = f'{R.REF}/SH3_cancer_master_v3.tsv'
HAVE_ORIGINAL = os.path.exists(ORIGINAL)
print('original atlas for comparison:', 'found' if HAVE_ORIGINAL else 'not uploaded - comparison will be skipped')
"""),
md("## 2. Unit tests of the shared code\nFast checks of mutation parsing, the sign convention, the "
   "partition modes and the conformal quantile (`code/run_tests.py`)."),
code(r"""
rc = os.system(f'cd {ROOT}/code && python run_tests.py')
assert rc == 0, 'unit tests failed - see the output above'
"""),
md("## 3. Build the atlas\nThe same selection and aggregation rules as the original build "
   "(`code/sh3_atlas.py`, standard library only)."),
code(r"""
import sh3_atlas as S; importlib.reload(S)
if R.done('SH3_cancer_master.tsv', 'build_stats.json'):
    ST = json.load(open(R.out('build_stats.json'))); print('atlas already built in this folder - loaded')
else:
    t = time.time()
    ST = S.build_atlas(f'{ROOT}/{COSMIC[0]}', f'{ROOT}/{COSMIC[1]}', f'{ROOT}/{COSMIC[2]}',
                       *[f'{ROOT}/{p}' for p in UNIPROT], R.OUT)
    ST['minutes'] = round((time.time() - t) / 60, 1)
    json.dump(ST, open(R.out('build_stats.json'), 'w'), indent=1)
print(json.dumps(ST, indent=1))
"""),
md("## 4. Data-quality report\nEvery row is re-checked against its own sequence. A failed check "
   "is a bug, not a filter, so the notebook stops if any row fails."),
code(r"""
M = pd.read_csv(R.out('SH3_cancer_master.tsv'), sep='\t', keep_default_na=False, dtype=str)
U = pd.read_csv(R.out('SH3_cancer_unmapped.tsv'), sep='\t', keep_default_na=False, dtype=str)
I = lambda c: M[c].astype(int)
checks = {
  'variant_id unique':                         M.variant_id.is_unique,
  'wild-type residue matches domain sequence': all(s[p-1] == w for s, p, w in zip(M.wt_domain_seq, I('pos_in_domain'), M.wt_aa)),
  'mutant sequence differs at one residue':    all(sum(a != b for a, b in zip(w, m)) == 1 and len(w) == len(m)
                                                   for w, m in zip(M.wt_domain_seq, M.mut_domain_seq)),
  'position inside the domain':                bool(((I('pos_in_domain') >= 1) & (I('pos_in_domain') <= I('dom_len'))).all()),
  'protein position = domain start + offset':  bool((I('pos_protein') == I('dom_start') + I('pos_in_domain') - 1).all()),
  'domain length = sequence length':           bool((I('dom_len') == M.wt_domain_seq.str.len()).all()),
  'wild-type differs from mutant':             bool((M.wt_aa != M.mut_aa).all()),
  'standard amino acids only':                 bool(M.wt_aa.isin(list('ACDEFGHIKLMNPQRSTVWY')).all()
                                                    and M.mut_aa.isin(list('ACDEFGHIKLMNPQRSTVWY')).all()),
}
QC = pd.DataFrame({'check': list(checks), 'passed': list(checks.values())})
QC.to_csv(R.out('qc_checks.csv'), index=False); print(QC.to_string(index=False))
assert QC.passed.all(), 'a data-quality check failed'

route = M.position_source.map(lambda s: 'canonical' if 'canonical' in s else 'isoform only')
nh = I('n_samples_nonhyper'); gsm = I('n_samples_gsm')
R.section('Data-quality report', 'Every retained row re-verified against its own sequence.', QC)
R.section('How the variants were mapped', '',
          pd.DataFrame({'route': ['canonical sequence', 'recovered via an isoform', 'rejected: residue mismatch on every sequence'],
                        'COSMIC rows': [ST['cmc'].get('mapped_canonical', 0), ST['cmc'].get('mapped_isoform', 0),
                                        ST['cmc'].get('in_window_residue_mismatch', 0)]}))
R.section('Rejected rows, by gene (top 10)', 'Full list: `SH3_cancer_unmapped.tsv`.',
          U.gene.value_counts().head(10).rename_axis('gene').reset_index(name='rejected rows'))
"""),
md("## 5. Is it the same atlas as the original?\nThe rebuilt file's MD5 is compared with the recorded MD5 of the Stage 0 "
   "atlas of 2026-09-20. Only if they differ, and the original file was uploaded to `reference/`, are the "
   "differing variants and columns listed."),
code(r"""
new_md5 = C.md5(R.out('SH3_cancer_master.tsv'))
# the recorded MD5 of the original atlas also sits in expected_values.json, so the check in section 6
# works even without the file; the file itself only adds a row-by-row diff if they ever differ
identical = new_md5 == 'cef897f4dd25f9cd56f2c40bb7ec0b08'
print('byte-identical to the original Stage 0 atlas (by recorded MD5):', identical)
if not identical and HAVE_ORIGINAL:
    O = pd.read_csv(ORIGINAL, sep='\t', keep_default_na=False, dtype=str)
    only_new, only_old = set(M.variant_id) - set(O.variant_id), set(O.variant_id) - set(M.variant_id)
    j = M.merge(O, on='variant_id', suffixes=('', '_old'))
    diff = {c: int((j[c] != j[c + '_old']).sum()) for c in M.columns if c != 'variant_id' and c + '_old' in j}
    print(f'only in new: {len(only_new)} | only in old: {len(only_old)}')
    print('columns that differ:', {k: v for k, v in diff.items() if v})
"""),
md("## 6. Results"),
code(r"""
tier = M.mutation_significance_tier
for k, v in [('cmc_rows', ST['cmc']['rows']), ('missense_rows_in_sh3_genes', ST['cmc']['missense_sh3_gene']),
             ('mapped_canonical', ST['cmc'].get('mapped_canonical', 0)), ('mapped_isoform', ST['cmc'].get('mapped_isoform', 0)),
             ('unmapped', len(U)), ('variants', len(M)), ('columns', M.shape[1]),
             ('domains', M.groupby(['uniprot', 'domain_idx']).ngroups), ('genes', M.gene.nunique()),
             ('gsm_rows', ST['tumour']['gsm_rows']), ('gsm_short_rows', ST['tumour']['gsm_short_rows']),
             ('gsm_samples', ST['tumour']['gsm_samples']),
             ('hypermutated_fraction', round(ST['tumour']['hypermutated_fraction'], 4)),
             ('with_sample_records', int((gsm > 0).sum())), ('nonhyper_variants', int((nh > 0).sum())),
             ('recurrent_nonhyper', int((nh >= 3).sum())), ('hypermutated_only', int(((gsm > 0) & (nh == 0)).sum())),
             ('recurrent_any', int((M.is_recurrent == '1').sum())), ('likely_germline', int((M.likely_germline == '1').sum())),
             ('significance_tier_1_3', int(tier.isin(['1', '2', '3']).sum())),
             ('dnds_flagged', int((M.dnds_disease_qval_sig != '').sum())), ('master_md5', new_md5)]:
    R.metric(k, v)
R.section('Hypermutation', f"A sample with more than {S.HYPERMUTATION_THRESHOLD:,} mutations in the genome screens is "
          f"called hypermutated: {ST['tumour']['hypermutated_samples']:,} of {ST['tumour']['gsm_samples']:,} samples "
          f"({ST['tumour']['hypermutated_fraction']:.1%}); median burden {ST['tumour']['burden_median']}.")
R.finish([f"{len(M):,} residue-verified missense variants in {R.metrics['domains']} SH3 domains of {M.gene.nunique()} genes.",
          f"{R.metrics['mapped_isoform']:,} COSMIC rows recovered through alternative isoforms; {len(U)} rejected.",
          f"{R.metrics['nonhyper_variants']:,} variants are seen outside hypermutated tumours; only "
          f"{R.metrics['recurrent_nonhyper']} of them in 3 or more such samples.",
          f"No variant carries a COSMIC significance tier 1-3 or a dN/dS flag - recurrence-based driver "
          f"detection cannot see this domain family.",
          f"Byte-identical to the original atlas: {identical}."])
"""),
]

# ════════════════════════════════════════════════════════════════════════ A1
A1 = [md(r"""
# A1 — Ground truth: folding and binding free energies (Stage 1)

**Question.** What are the measured effects to learn from, and do they mean what we think they
mean (the sign, the scale)?

**What it does.**
- **ddPCA** (Faure et al. 2022): MoCHI separates each variant's ΔΔG of folding from its ΔΔG of
  binding for GRB2-SH3, PSD95-PDZ3 and GB1. Bootstrap spread flags unreliable fits.
- **MegaScale** (Tsuboyama et al. 2023): 389,068 single-substitution folding stabilities.
  Shipped with the opposite sign, so negated. SH3 domains identified by ≥50 % identity.
- **Sign and scale check** against independent in vitro measurements, before anything is
  trained. The binding check needs a numbering offset, which is derived, not assumed.
- **The premise, in measured data:** buried residues cost folding energy, interface residues
  cost binding energy.

**Inputs:** `input/datasets/Data.zip`, `Processed_K50_dG_datasets.zip`, `input/uniprot/sh3_domains_human.tsv`.
**Outputs:** `ddpca_ground_truth.parquet`, `megascale_singles.parquet`, `megascale_sh3_matches.csv`,
`calibration.csv`, `separation_table.csv`, `baseline_*.csv`, `RESULTS_A1.md`.
**Runtime:** about 10 min, CPU. Explanation: `docs/A1_ground_truth.md`.

Convention everywhere: **positive = destabilising / weaker binding**.
"""),
setup('A1', 'Ground truth', pip='biopython'),
code(r"""
import glob, collections
from Bio import Align
R.verify_inputs(['input/datasets/Data.zip', 'input/datasets/Processed_K50_dG_datasets.zip',
                 'input/uniprot/sh3_domains_human.tsv'])
DOMAINS = ['GRB2-SH3', 'PSD95-PDZ3', 'GB1']
FIT = 'mochi__fit_tmodel_3state_sparse_dimsum128'
m = R.extract('input/datasets/Data.zip', lambda s: any(s.startswith(f'Data/mochi/{d}/{FIT}/') for d in DOMAINS)
              or s.startswith(('Data/pdb/', 'Data/in_vitro/', 'Data/foldx/', 'Data/EVE/', 'Data/MSA/')))
print(f'Faure archive: {len(m)} files')
m = R.extract('input/datasets/Processed_K50_dG_datasets.zip',
              lambda s: s.endswith('/Tsuboyama2023_Dataset2_Dataset3_20230416.csv'))
assert len(m) == 1, m                     # guards against the macOS '._' shadow copy
TSU = f'{R.WORK}/{m[0]}'; W = R.WORK
"""),
md("## 1. ddPCA: separate folding and binding energies, with reliability flags"),
code(r"""
PAT = C.MUT_PATTERN
def load_domain(dom):
    base = f'{W}/Data/mochi/{dom}/{FIT}'
    w = pd.read_csv(f'{base}/model_weights_0.txt', sep='\t')
    p = w.id.str.extract(PAT); p.columns = ['wt_aa', 'pos', 'mut_aa']
    d = pd.concat([w, p], axis=1).dropna(subset=['wt_aa']).copy(); d['pos'] = d.pos.astype(int); d['domain'] = dom
    boots = sorted(glob.glob(f'{base}/bootstrap/boot_*/model_weights_0.txt'))
    F = pd.concat([pd.read_csv(b, sep='\t').set_index('id')['folding_coefficient'] for b in boots], axis=1)
    B = pd.concat([pd.read_csv(b, sep='\t').set_index('id')['binding_coefficient'] for b in boots], axis=1)
    return (d.set_index('id').join(F.std(axis=1).rename('folding_sd')).join(B.std(axis=1).rename('binding_sd'))
            .reset_index().assign(n_bootstraps=len(boots)))
dd = pd.concat([load_domain(d) for d in DOMAINS], ignore_index=True)
# a binding coefficient means nothing for a variant too unstable to fold: those fits are unreliable
dd['binding_reliable'] = dd.binding_coefficient.notna() & (dd.binding_coefficient.abs() <= 4) & (dd.binding_sd <= 0.5)
dd['folding_reliable'] = dd.folding_coefficient.notna() & (dd.folding_coefficient.abs() <= 6) & (dd.folding_sd <= 0.5)
QD = dd.groupby('domain').agg(singles=('id', 'size'), with_binding=('binding_coefficient', lambda s: s.notna().sum()),
                              reliable_binding=('binding_reliable', 'sum'), reliable_folding=('folding_reliable', 'sum'),
                              positions=('pos', 'nunique'), bootstraps=('n_bootstraps', 'first'),
                              duplicated_ids=('id', lambda s: int(s.duplicated().sum()))).reset_index()
print(QD.to_string(index=False))
assert QD.duplicated_ids.sum() == 0
"""),
md("## 2. Sign and scale check against in vitro measurements\nFolding against Φ-value kinetics of "
   "GRB2-SH3 (Troilo 2018); binding against double-mutant-cycle ΔΔG of PSD95-PDZ3 (Chi 2008). "
   "Chi numbers residues on full-length DLG4, so the offset to the MoCHI construct is found by "
   "maximising wild-type agreement."),
code(r"""
lit = pd.read_csv(f'{W}/Data/in_vitro/GRB2_literature_free_energies.txt', sep='\t')
tro = lit[lit.Dataset == 'Troilo_2018'].copy(); tro['id'] = tro.id.str.strip()
K = pd.Series((tro.Kf / tro.Ku).values, index=tro.id)
lf = (-0.592 * np.log(K / K['WT'])).drop('WT')
fold_pairs = pd.concat([lf.rename('in_vitro'), dd[dd.domain == 'GRB2-SH3'].set_index('id').folding_coefficient], axis=1).dropna()
r_fold = fold_pairs.corr().iloc[0, 1]
chi = pd.read_csv(f'{W}/Data/in_vitro/PDZ_literature_free_energies/Chi2008_invitro_kd_ddGf_ddGb_PDZ_CRIPTpeptide.txt', sep=r'\s+')
cm = chi.id.str.strip().str.extract(PAT).dropna(); cm[1] = cm[1].astype(int)
pz = dd[dd.domain == 'PSD95-PDZ3']; wt_at = dict(zip(pz.pos, pz.wt_aa))
off = max(range(250, 360), key=lambda o: sum(wt_at.get(p - o) == w for w, p in zip(cm[0], cm[1])))
chi.loc[cm.index, 'mid'] = [f'{w}{p - off}{m}' for w, p, m in zip(cm[0], cm[1], cm[2])]
bind_pairs = chi.dropna(subset=['mid']).set_index('mid')[['b_ddg']].join(pz.set_index('id').binding_coefficient).dropna()
r_bind = bind_pairs.corr().iloc[0, 1]
print(f'folding r {r_fold:+.3f} (n={len(fold_pairs)}) | binding r {r_bind:+.3f} (n={len(bind_pairs)}) | Chi offset {off}')
assert r_fold > 0 and r_bind > 0, 'MoCHI sign disagrees with in vitro data - stop'
pd.DataFrame([dict(axis='folding', reference='Troilo 2018 (GRB2-SH3, Kf/Ku)', n=len(fold_pairs), pearson_r=r_fold),
              dict(axis='binding', reference='Chi 2008 (PSD95-PDZ3, b_ddg)', n=len(bind_pairs), pearson_r=r_bind,
                   numbering_offset=off)]).to_csv(R.out('calibration.csv'), index=False)
"""),
md("## 3. MegaScale folding stabilities\nSingle substitutions only; the sign is flipped on load. A "
   "MegaScale domain is an SH3 if it is ≥50 % identical to a human SH3 domain."),
code(r"""
parts = []
for ch in pd.read_csv(TSU, chunksize=200_000, low_memory=False,
                      usecols=['WT_name', 'aa_seq', 'mut_type', 'ddG_ML', 'dG_ML', 'deltaG', 'deltaG_95CI', 'WT_cluster']):
    ch = ch[ch.mut_type.astype(str).str.match(r'^[A-Z]\d+[A-Z]$')]
    parts.append(ch[pd.to_numeric(ch.ddG_ML, errors='coerce').notna()])
mega = pd.concat(parts, ignore_index=True)
mega['ddG_fold'] = -pd.to_numeric(mega.ddG_ML)          # shipped with the opposite sign
DOMTBL = pd.read_csv(f'{R.IN}/uniprot/sh3_domains_human.tsv', sep='\t')
idal = Align.PairwiseAligner(open_gap_score=-11, extend_gap_score=-1, substitution_matrix=None)
idal.match_score = 1; idal.mismatch_score = 0
def identity(a, b):
    if abs(len(a) - len(b)) > 25: return 0.0
    try: return idal.score(a, b) / min(len(a), len(b))
    except Exception: return 0.0
hits = []
for _, m_ in mega.drop_duplicates('WT_name')[['WT_name', 'aa_seq']].iterrows():
    best = (0, None)
    for _, d in DOMTBL[['gene', 'uniprot', 'domain_idx', 'domain_seq']].iterrows():
        s = identity(str(m_.aa_seq), d.domain_seq)
        if s > best[0]: best = (s, d)
    if best[0] >= 0.50:
        hits.append(dict(WT_name=m_.WT_name, gene=best[1].gene, uniprot=best[1].uniprot,
                         domain_idx=best[1].domain_idx, identity=round(best[0], 3)))
hits = pd.DataFrame(hits)
mega['is_sh3'] = mega.WT_name.isin(set(hits.WT_name))
mega = mega.merge(hits.drop(columns='identity'), on='WT_name', how='left')
print(f'MegaScale: {len(mega):,} single substitutions, {mega.WT_name.nunique()} domains, {len(hits)} SH3 structures '
      f'({hits.gene.nunique()} genes, {int(mega.is_sh3.sum()):,} variants)')
print(f'median ddG_fold after the sign flip: {mega.ddG_fold.median():+.2f} (positive = destabilising)')
mega[['WT_name', 'aa_seq', 'mut_type', 'ddG_fold', 'is_sh3', 'gene', 'uniprot', 'domain_idx']].to_parquet(
    R.out('megascale_singles.parquet'), index=False)
hits.sort_values('identity', ascending=False).to_csv(R.out('megascale_sh3_matches.csv'), index=False)
dd.to_parquet(R.out('ddpca_ground_truth.parquet'), index=False)
"""),
md("## 4. The premise in measured data: burial drives folding cost, the interface drives binding cost\n"
   "GRB2-SH3 variants by structural class from the solved peptide complex (2VWF): buried = relative "
   "solvent accessibility < 0.25, interface = within 5 Å of the peptide. No model is involved."),
code(r"""
def parse_struct(pdb, rsasa_pdb, dom_chain='A', pep_chain='B'):
    rs = {int(l[22:26]): float(l[60:66]) for l in open(rsasa_pdb) if l.startswith('ATOM') and l[21] == dom_chain}
    dom, pep = collections.defaultdict(list), []
    for l in open(pdb):
        if not l.startswith('ATOM'): continue
        xyz = (float(l[30:38]), float(l[38:46]), float(l[46:54]))
        if l[21] == dom_chain: dom[int(l[22:26])].append(xyz)
        elif l[21] == pep_chain: pep.append(xyz)
    mind = {r: min(((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) ** .5 for a in ats for b in pep) if pep else np.nan
            for r, ats in dom.items()}
    return pd.DataFrame({'pos': list(rs), 'rsasa': [rs[p] for p in rs], 'dist_peptide': [mind.get(p, np.nan) for p in rs]})
st = parse_struct(f'{W}/Data/pdb/2vwf.pdb', f'{W}/Data/pdb/2vwf_RSASA.pdb')
g = dd[dd.domain == 'GRB2-SH3'].merge(st, on='pos', how='left')
g['buried'] = g.rsasa < 0.25; g['interface'] = g.dist_peptide < 5.0
SEP = g.groupby(['buried', 'interface'])[['folding_coefficient', 'binding_coefficient']].median()
SEP['variants'] = g.groupby(['buried', 'interface']).size()
SEP = SEP.reset_index(); SEP.to_csv(R.out('separation_table.csv'), index=False); print(SEP.round(3).to_string(index=False))
"""),
md("## 5. Conventional baselines shipped with the ddPCA archive (FoldX, EVE, MSA conservation)"),
code(r"""
import re
FOLDX = {'GRB2-SH3': 'PS_2vwf_nowater_noligand_restrict_scanning_output.txt',
         'PSD95-PDZ3': 'PS_1be9_nowater_noligand_restrict_scanning_output.txt',
         'GB1': 'PS_2gb1_nowater_noligand_restrict_scanning_output.txt'}
AA3 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I',
       'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
fx = []
for dom, fn in FOLDX.items():
    for line in open(f'{W}/Data/foldx/{dom}/{fn}'):
        p = line.split()
        if len(p) != 2: continue
        m_ = re.match(r'^([A-Z]{3})([A-Za-z])(\d+)([A-Z])$', p[0])
        if m_: fx.append({'domain': dom, 'id': f'{AA3.get(m_.group(1), "X")}{m_.group(3)}{m_.group(4)}', 'foldx_ddg': float(p[1])})
foldx = pd.DataFrame(fx); foldx.to_csv(R.out('baseline_foldx.csv'), index=False)
chk = dd.merge(foldx, on=['domain', 'id']).dropna(subset=['folding_coefficient', 'foldx_ddg'])
r_foldx = chk.folding_coefficient.corr(chk.foldx_ddg)
EVE = {'GRB2-SH3': 'GRB2_HUMAN_149-217_11-26-2021_b02_single_mutant_matrix.csv',
       'PSD95-PDZ3': 'DLG4_HUMAN_301-404_11-26-2021_b04_single_mutant_matrix.csv',
       'GB1': 'SPG1_STRSG_218-292_11-26-2021_b05_single_mutant_matrix.csv'}
ev = []
for dom, fn in EVE.items():
    e = pd.read_csv(f'{W}/Data/EVE/{dom}/{fn}', on_bad_lines='skip', low_memory=False)
    e = e[[c for c in ['id', 'prediction_EVE_evol_indices', 'prediction_epistatic', 'column_conservation'] if c in e.columns]].copy()
    e['domain'] = dom; ev.append(e)
pd.concat(ev, ignore_index=True).dropna(subset=['id']).to_csv(R.out('baseline_eve.csv'), index=False)
pd.concat([pd.read_csv(f'{W}/Data/MSA/{d}/frequencies.csv').assign(domain=d) for d in DOMAINS],
          ignore_index=True).to_csv(R.out('baseline_msa_conservation.csv'), index=False)
print(f'FoldX vs MoCHI folding: r {r_foldx:+.3f} over {len(chk):,} variants')
"""),
md("## 6. Results"),
code(r"""
for k, v in [('ddpca_singles', len(dd)),
             ('ddpca_both_energies', int((dd.folding_coefficient.notna() & dd.binding_coefficient.notna()).sum())),
             ('reliable_binding', int(dd.binding_reliable.sum())), ('reliable_folding', int(dd.folding_reliable.sum())),
             *[(f'reliable_binding_{d}', int(dd[dd.domain == d].binding_reliable.sum())) for d in DOMAINS],
             ('calibration_fold_r', r_fold), ('calibration_fold_n', len(fold_pairs)),
             ('calibration_bind_r', r_bind), ('calibration_bind_n', len(bind_pairs)), ('chi_offset', off),
             ('megascale_singles', len(mega)), ('megascale_domains', mega.WT_name.nunique()),
             ('megascale_sh3_structures', len(hits)), ('megascale_sh3_genes', hits.gene.nunique()),
             ('megascale_sh3_variants', int(mega.is_sh3.sum())),
             ('foldx_overlap', len(chk)), ('foldx_vs_mochi_r', r_foldx)]:
    R.metric(k, v)
lab = lambda b, i: f"{'buried' if b else 'surface'}_{'interface' if i else 'not_interface'}"
for _, r in SEP.iterrows():
    R.metric(f'sep_{lab(r.buried, r.interface)}_fold', r.folding_coefficient)
    R.metric(f'sep_{lab(r.buried, r.interface)}_bind', r.binding_coefficient)
R.section('ddPCA per domain', 'Reliable binding: coefficient present, |ΔΔG_bind| ≤ 4 and bootstrap SD ≤ 0.5.', QD)
R.section('In vitro calibration', 'Both correlations must be positive; they are the pipeline-wide sign check.',
          pd.read_csv(R.out('calibration.csv')))
R.section('Measured separation (GRB2-SH3, median ΔΔG in kcal/mol)',
          'The empirical premise of the thesis: the two energies separate along structural lines.', SEP, '{:.3f}')
R.section('MegaScale domains matched to human SH3 domains', '', hits.sort_values('identity', ascending=False))
R.finish([f"ddPCA: {len(dd):,} single substitutions in 3 domains; {R.metrics['reliable_binding']:,} reliable binding energies "
          f"(GRB2-SH3 {R.metrics['reliable_binding_GRB2-SH3']}, the only SH3).",
          f"MegaScale: {len(mega):,} folding stabilities in {mega.WT_name.nunique()} domains, sign flipped; "
          f"{len(hits)} structures of {hits.gene.nunique()} human SH3 genes ({R.metrics['megascale_sh3_variants']:,} variants).",
          f"Sign check: folding r {r_fold:+.3f} (n={len(fold_pairs)}), binding r {r_bind:+.3f} (n={len(bind_pairs)}, offset {off}).",
          f"Measured: buried non-interface residues cost {SEP.iloc[2].folding_coefficient:.2f} kcal/mol of folding energy; "
          f"buried interface residues cost {SEP.iloc[3].binding_coefficient:.2f} of binding energy."])
"""),
]

# ════════════════════════════════════════════════════════════════════════ A2
A2 = [md(r"""
# A2 — Features: ESM-2, chemistry, structure and the family frame (Stage 2)

**Question.** How is each variant turned into numbers a model can learn from, and where does it sit
in 3D?

**What it does.**
- One table of every variant (ddPCA, MegaScale, atlas) with the **wild-type sequence** of its
  domain; every row passes a residue check.
- **ESM-2 650M, one pass per wild-type domain** (725 domains): the 1,280-number representation of
  each residue plus masked-marginal log-odds, so every variant's features are a lookup
  (5 min instead of hours; 97 MB instead of 2 GB).
- Seven amino-acid chemistry scalars. **1,292 numbers per variant in total.**
- Structure: the three solved ddPCA complexes, and AlphaFold models for the atlas proteins
  (downloaded once, then **cached on Drive**). Structure is annotation for validation only,
  never a model input.
- Every atlas residue placed on the GRB2-SH3 reference frame (56 positions).

**Inputs:** A0 atlas, A1 ground truth, `input/datasets/Data.zip` (PDB files), `input/uniprot/sh3_domains_human.tsv`.
**Outputs:** `features_{megascale,ddpca,atlas}.parquet`, `esm_domain_embeddings.npz`,
`structure_features.csv`, `alphafold_log.csv`, `RESULTS_A2.md`.
**Runtime:** about 25 min on a **T4 GPU** (15 of them AlphaFold downloads on the first run only).
Explanation: `docs/A2_features.md`.
"""),
setup('A2', 'Features', gpu=True, pip='biopython'),
code(r"""
import collections, urllib.request, shutil
import torch
from Bio import Align
from Bio.Align import substitution_matrices
from Bio.PDB import MMCIFParser
from Bio.PDB.SASA import ShrakeRupley
R.verify_inputs(['input/datasets/Data.zip', 'input/uniprot/sh3_domains_human.tsv'])
R.extract('input/datasets/Data.zip', lambda s: s.startswith('Data/pdb/'))
W = R.WORK; PAT = C.MUT_PATTERN
FEAT = ['features_megascale.parquet', 'features_ddpca.parquet', 'features_atlas.parquet', 'structure_features.csv']
dd = pd.read_parquet(R.res('A1', 'ddpca_ground_truth.parquet'))
mega = pd.read_parquet(R.res('A1', 'megascale_singles.parquet'))
MASTER = pd.read_csv(R.res('A0', 'SH3_cancer_master.tsv'), sep='\t')
DOMTBL = pd.read_csv(f'{R.IN}/uniprot/sh3_domains_human.tsv', sep='\t')
print(f'ddpca {len(dd):,} | megascale {len(mega):,} | atlas {len(MASTER):,}')
"""),
md("## 1. One variant table, with the wild-type sequence of every domain\nMegaScale's `aa_seq` is the "
   "**mutant** sequence (a first-run bug in the original project); the wild type is reconstructed."),
code(r"""
frames = []
for dom, g in dd.groupby('domain'):     # ddPCA: consensus wild-type residue at each position
    seq = ''.join(g.groupby('pos').wt_aa.agg(lambda s: s.mode().iat[0]).sort_index().values)
    sub = g[['pos', 'wt_aa', 'mut_aa', 'folding_coefficient', 'binding_coefficient', 'binding_reliable']].copy()
    frames.append(sub.rename(columns={'folding_coefficient': 'ddG_fold', 'binding_coefficient': 'ddG_bind'})
                     .assign(set='ddpca', domain_key=dom, wt_seq=seq))
x = mega.mut_type.str.extract(PAT)
ms = mega.assign(wt_aa=x[0], pos=pd.to_numeric(x[1]), mut_aa=x[2]).dropna(subset=['pos', 'wt_aa', 'mut_aa', 'aa_seq'])
ms['pos'] = ms.pos.astype(int)
mutant_check = float(np.mean([s[p-1] == m for s, p, m in zip(ms.aa_seq, ms.pos, ms.mut_aa)]))
ms['wt_seq'] = [s[:p-1] + w + s[p:] for s, p, w in zip(ms.aa_seq, ms.pos, ms.wt_aa)]
frames.append(ms[['WT_name', 'pos', 'wt_aa', 'mut_aa', 'ddG_fold', 'is_sh3', 'gene', 'uniprot', 'domain_idx', 'wt_seq']]
              .rename(columns={'WT_name': 'domain_key'}).assign(set='megascale'))
at = MASTER[['variant_id', 'gene', 'uniprot', 'domain_idx', 'wt_domain_seq', 'pos_in_domain', 'wt_aa', 'mut_aa']]
at = at.rename(columns={'wt_domain_seq': 'wt_seq', 'pos_in_domain': 'pos'})
frames.append(at.assign(domain_key=at.uniprot + '_d' + at.domain_idx.astype(str), set='atlas'))
V = pd.concat(frames, ignore_index=True); V['pos'] = V.pos.astype('Int64')
n0 = len(V); V = V.dropna(subset=['wt_seq', 'pos', 'wt_aa', 'mut_aa'])
V = V[[len(s) >= p and s[p-1] == w for s, p, w in zip(V.wt_seq, V.pos, V.wt_aa)]].reset_index(drop=True)
DROPPED = n0 - len(V)
V['dom_len'] = V.wt_seq.str.len(); V['rel_pos'] = V.pos / V.dom_len
B62 = substitution_matrices.load('BLOSUM62')
V['d_hydropathy'] = V.mut_aa.map(C.KD) - V.wt_aa.map(C.KD)
V['d_volume'] = V.mut_aa.map(C.VOL) - V.wt_aa.map(C.VOL)
V['d_charge'] = V.mut_aa.map(C.CHG).fillna(0) - V.wt_aa.map(C.CHG).fillna(0)
V['blosum62'] = [B62[a][b] if (a in B62.alphabet and b in B62.alphabet) else np.nan for a, b in zip(V.wt_aa, V.mut_aa)]
V['to_proline'] = (V.mut_aa == 'P').astype(int); V['from_glycine'] = (V.wt_aa == 'G').astype(int)
V['to_glycine'] = (V.mut_aa == 'G').astype(int)
print(f'MegaScale aa_seq carries the mutant residue for {mutant_check:.1%} of rows (confirms it is the mutant sequence)')
print(f'variant table: {len(V):,} rows, {DROPPED} dropped by the residue check', V.groupby('set').size().to_dict())
assert DROPPED == 0, 'rows failed the residue check - investigate before continuing'
"""),
md("## 2. ESM-2: one forward pass per wild-type domain"),
code(r"""
if R.done('esm_domain_embeddings.npz', 'esm_scores.parquet', 'esm_logodds.npz'):
    EMB = C.load_embeddings(R.out('esm_domain_embeddings.npz'))
    V = V.join(pd.read_parquet(R.out('esm_scores.parquet'))); print('ESM features loaded from this folder')
else:
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    tok = AutoTokenizer.from_pretrained('facebook/esm2_t33_650M_UR50D')
    esm = AutoModelForMaskedLM.from_pretrained('facebook/esm2_t33_650M_UR50D').to(C.DEV).eval()
    if C.DEV == 'cuda': esm = esm.half()
    AAS = list('ACDEFGHIKLMNPQRSTVWY'); AAPOS = {a: i for i, a in enumerate(AAS)}
    AA_IDX = torch.tensor([tok.convert_tokens_to_ids(a) for a in AAS]).to(C.DEV)
    @torch.no_grad()
    def embed_and_score(seq, batch=32):
        L = len(seq); enc = tok(seq, return_tensors='pt').to(C.DEV)
        rep = esm(**enc, output_hidden_states=True).hidden_states[-1][0, 1:L+1].float().cpu().numpy()
        ids = enc['input_ids'][0]; rows = []
        for s in range(0, L, batch):
            idx = list(range(s, min(s + batch, L)))
            bb = ids.unsqueeze(0).repeat(len(idx), 1).clone()
            for k, i in enumerate(idx): bb[k, i + 1] = tok.mask_token_id        # residue i is token i+1
            lg = esm(input_ids=bb, attention_mask=torch.ones_like(bb)).logits
            for k, i in enumerate(idx): rows.append(torch.log_softmax(lg[k, i + 1].float(), -1)[AA_IDX].cpu().numpy())
        return rep, np.stack(rows)
    seqs = V[['domain_key', 'wt_seq']].drop_duplicates('domain_key')
    EMB, LO = {}, {}; t0 = time.time()
    for n, (k, s) in enumerate(zip(seqs.domain_key, seqs.wt_seq), 1):
        e, l = embed_and_score(s); EMB[k] = e.astype(np.float16); LO[k] = l
        if n % 100 == 0: print(f'  ESM {n}/{len(seqs)}  {(time.time() - t0) / 60:.1f} min')
    lo = np.stack([LO[k][p-1] for k, p in zip(V.domain_key, V.pos.astype(int))]); r = np.arange(len(V))
    w = V.wt_aa.map(AAPOS).values; mu = V.mut_aa.map(AAPOS).values
    V['esm_score'] = lo[r, mu] - lo[r, w]; V['esm_wt_logp'] = lo[r, w]; V['esm_entropy'] = -(np.exp(lo) * lo).sum(1)
    del lo, esm; torch.cuda.empty_cache()
    np.savez_compressed(R.out('esm_domain_embeddings.npz'), **EMB)
    np.savez_compressed(R.out('esm_logodds.npz'), **{k: v.astype(np.float32) for k, v in LO.items()})   # for B6
    V[['esm_score', 'esm_wt_logp', 'esm_entropy']].to_parquet(R.out('esm_scores.parquet'))
print(f'{len(EMB)} domains embedded')
"""),
md("## 3. Structure (annotation only)\nSolved complexes for the ddPCA domains, with the PDB→construct "
   "offset derived by sliding the construct along the chain. AlphaFold models for the atlas, cached "
   "in `cache/alphafold/`. Relative solvent accessibility by Shrake–Rupley, normalised by a standard "
   "maximum-accessibility table (the table's primary source could not be confirmed; see the doc)."),
code(r"""
T3 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I',
      'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
def struct_from_pdb(pdb, rsasa_pdb, dom_chain='A', pep_chain='B'):
    rs = {int(l[22:26]): float(l[60:66]) for l in open(rsasa_pdb) if l.startswith('ATOM') and l[21] == dom_chain}
    dom, pep = collections.defaultdict(list), []
    for l in open(pdb):
        if not l.startswith('ATOM'): continue
        xyz = (float(l[30:38]), float(l[38:46]), float(l[46:54]))
        if l[21] == dom_chain: dom[int(l[22:26])].append(xyz)
        elif l[21] == pep_chain: pep.append(xyz)
    return pd.DataFrame([{'pos': r, 'rsasa': rs.get(r, np.nan),
                          'dist_peptide': min(((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) ** .5
                                              for a in dom[r] for b in pep) if pep else np.nan} for r in sorted(dom)])
def derive_offset(construct, pdb, ch='A'):
    seen = {}
    for l in open(pdb):
        if l.startswith('ATOM') and l[21] == ch: seen.setdefault(int(l[22:26]), T3.get(l[17:20].strip(), 'X'))
    ks = sorted(seen); seq = ''.join(seen[k] for k in ks); best = (0, None)
    for k in range(max(1, len(seq) - len(construct) + 1)):
        ident = sum(a == b for a, b in zip(construct, seq[k:]))
        if ident > best[0]: best = (ident, k)
    frac = best[0] / len(construct)
    return (ks[best[1]] - 1, frac) if (best[1] is not None and frac >= 0.8) else (None, frac)

struct, offsets = [], []
for dom, pid in {'GRB2-SH3': '2vwf', 'PSD95-PDZ3': '1be9', 'GB1': '2gb1'}.items():
    construct = ''.join(V[V.domain_key == dom].groupby('pos').wt_aa.first().sort_index().values)
    off, frac = derive_offset(construct, f'{W}/Data/pdb/{pid}.pdb')
    offsets.append(dict(domain=dom, pdb=pid, offset=off, identity=round(frac, 3)))
    if off is None: continue
    s = struct_from_pdb(f'{W}/Data/pdb/{pid}.pdb', f'{W}/Data/pdb/{pid}_RSASA.pdb')
    s['pos'] = s['pos'] - off
    struct.append(s[(s.pos >= 1) & (s.pos <= len(construct))].assign(domain_key=dom, plddt=np.nan))
print(pd.DataFrame(offsets).to_string(index=False))

MAXACC = {'A':106,'R':248,'N':157,'D':163,'C':135,'Q':198,'E':194,'G':84,'H':184,'I':169,
          'L':164,'K':205,'M':188,'F':197,'P':136,'S':130,'T':142,'W':227,'Y':222,'V':142}
AF = f'{R.CACHE}/alphafold'; os.makedirs(AF, exist_ok=True)
sr = ShrakeRupley(); aflog = []
def alphafold(acc, a, b):
    f = f'{AF}/AF-{acc}.cif'; ver = 'cache'
    if not os.path.exists(f):
        ver = None
        for v in ('v6', 'v5', 'v4'):
            try:
                urllib.request.urlretrieve(f'https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.cif', f + '.part')
                shutil.move(f + '.part', f); ver = v; break
            except Exception:
                pass
        if ver is None: aflog.append(dict(uniprot=acc, status='not available')); return None
    try:
        ch = next(MMCIFParser(QUIET=True).get_structure(acc, f)[0].get_chains()); sr.compute(ch, level='R')
        aflog.append(dict(uniprot=acc, status=ver))
        return pd.DataFrame([{'pos': x.id[1] - a + 1, 'rsasa': x.sasa / MAXACC.get(T3.get(x.get_resname(), 'X'), 200),
                              'dist_peptide': np.nan, 'plddt': np.mean([t.get_bfactor() for t in x])}
                             for x in ch if a <= x.id[1] <= b])
    except Exception as e:
        aflog.append(dict(uniprot=acc, status=f'parse error: {type(e).__name__}')); return None
todo = DOMTBL.assign(domain_key=DOMTBL.uniprot + '_d' + DOMTBL.domain_idx.astype(str))
todo = todo[todo.domain_key.isin(set(V[V.set == 'atlas'].domain_key))]; t0 = time.time()
for n, (_, d) in enumerate(todo.iterrows(), 1):
    s = alphafold(d.uniprot, int(d.start), int(d.end))
    if s is not None and len(s): struct.append(s.assign(domain_key=d.domain_key))
    if n % 50 == 0: print(f'  AlphaFold {n}/{len(todo)}  {(time.time() - t0) / 60:.1f} min')
ST = pd.concat(struct, ignore_index=True)
AFL = pd.DataFrame(aflog).drop_duplicates(); AFL.to_csv(R.out('alphafold_log.csv'), index=False)
AF_FAILED = sorted(set(AFL[~AFL.status.isin(['v6', 'v5', 'v4', 'cache'])].uniprot))
print(f'structure: {len(ST):,} rows over {ST.domain_key.nunique()} domains | proteins without a model: {AF_FAILED}')
"""),
md("## 4. Every atlas residue on the GRB2-SH3 reference frame, then save"),
code(r"""
al = Align.PairwiseAligner(mode='global', open_gap_score=-11, extend_gap_score=-1); al.match_score = 2; al.mismatch_score = -1
ref_seq = V[V.domain_key == 'GRB2-SH3'].wt_seq.iat[0]
def to_ref(seq):
    try: a = al.align(ref_seq, seq)[0]
    except Exception: return {}
    return {qs + k + 1: rs_ + k + 1 for (rs_, re_), (qs, qe) in zip(a.aligned[0], a.aligned[1]) for k in range(re_ - rs_)}
seqs = V[['domain_key', 'wt_seq']].drop_duplicates('domain_key')
atlas_keys = set(V[V.set == 'atlas'].domain_key)
REFMAP = {k: to_ref(s) for k, s in zip(seqs.domain_key, seqs.wt_seq) if k in atlas_keys}
V['ref_pos'] = [REFMAP[k].get(int(p), np.nan) if k in REFMAP else np.nan for k, p in zip(V.domain_key, V.pos)]
V = V.merge(ST[['domain_key', 'pos', 'rsasa', 'dist_peptide']], on=['domain_key', 'pos'], how='left')
V['has_structure'] = V.rsasa.notna()
V['buried'] = (V.rsasa < 0.25).where(V.rsasa.notna()); V['interface'] = (V.dist_peptide < 5.0).where(V.dist_peptide.notna())
MG, DD, AT = [V[V.set == s].drop(columns=['set']).reset_index(drop=True) for s in ('megascale', 'ddpca', 'atlas')]
for d, f in zip((MG, DD, AT), FEAT[:3]): d.to_parquet(R.out(f), index=False)
ST.to_csv(R.out('structure_features.csv'), index=False)
print(f'megascale {len(MG):,} | ddpca {len(DD):,} | atlas {len(AT):,}')
"""),
md("## 5. Checks and results\nThe zero-shot ESM-2 score is the free baseline every later model must "
   "beat (negative is correct: a low ESM score means a damaging mutation). The cross-fold table pools "
   "GRB2-SH3 and PSD95-PDZ3; GB1 drops out because its structure has no bound partner."),
code(r"""
esm_rho = {}
for s, col in [('ddpca', 'ddG_fold'), ('ddpca', 'ddG_bind'), ('megascale', 'ddG_fold')]:
    x = V[V.set == s].dropna(subset=[col, 'esm_score']); esm_rho[(s, col)] = (len(x), x.esm_score.corr(x[col], method='spearman'))
d = V[(V.set == 'ddpca') & V.has_structure & V.binding_reliable.fillna(False)]
XS = d.groupby(['buried', 'interface'])[['ddG_fold', 'ddG_bind']].median().reset_index()
XS.to_csv(R.out('cross_fold_separation.csv'), index=False)
a = V[V.set == 'atlas']
for k, v in [('variants_total', len(V)), ('variants_megascale', len(MG)), ('variants_ddpca', len(DD)),
             ('variants_atlas', len(AT)), ('dropped_by_residue_check', DROPPED), ('esm_domains', len(EMB)),
             ('esm_rho_ddpca_fold', esm_rho[('ddpca', 'ddG_fold')][1]), ('esm_rho_ddpca_bind', esm_rho[('ddpca', 'ddG_bind')][1]),
             ('esm_rho_megascale_fold', esm_rho[('megascale', 'ddG_fold')][1]),
             ('structure_rows', len(ST)), ('structure_domains', ST.domain_key.nunique()),
             ('alphafold_proteins_missing', len(AF_FAILED)),
             ('atlas_structure_coverage', a.has_structure.mean()), ('atlas_refmap_coverage', a.ref_pos.notna().mean()),
             ('atlas_groups', a.groupby(['uniprot', 'domain_idx']).ngroups)]:
    R.metric(k, v)
lab = lambda b, i: f"{'buried' if b else 'surface'}_{'interface' if i else 'not_interface'}"
for _, r in XS.iterrows():
    R.metric(f'xsep_{lab(r.buried, r.interface)}_fold', r.ddG_fold); R.metric(f'xsep_{lab(r.buried, r.interface)}_bind', r.ddG_bind)
R.section('Variant table', '', V.groupby('set').agg(variants=('pos', 'size'), domains=('domain_key', 'nunique')).reset_index())
R.section('Zero-shot ESM-2 against measured ΔΔG (Spearman)', 'Folding is tracked better than binding: the gap the thesis is about.',
          pd.DataFrame([dict(set=s, target=c, n=n, rho=r) for (s, c), (n, r) in esm_rho.items()]))
R.section('PDB offsets (derived, not assumed)', '', pd.DataFrame(offsets))
R.section('Cross-fold separation (GRB2-SH3 + PSD95-PDZ3, reliable binding only)', 'Replication of A1 across two folds.', XS, '{:.3f}')
R.section('AlphaFold proteins without a model', 'Very large proteins that AlphaFold DB splits into fragments; only F1 is requested.',
          pd.DataFrame({'uniprot': AF_FAILED}))
R.finish([f"{len(V):,} variants pass the residue check ({DROPPED} dropped): MegaScale {len(MG):,}, ddPCA {len(DD):,}, atlas {len(AT):,}.",
          f"ESM-2 embedded {len(EMB)} wild-type domains; each variant = 1,280 + 12 = 1,292 numbers.",
          f"Zero-shot ESM-2: folding ρ {esm_rho[('ddpca','ddG_fold')][1]:+.3f}, binding ρ {esm_rho[('ddpca','ddG_bind')][1]:+.3f} (ddPCA).",
          f"Atlas structure coverage {a.has_structure.mean():.1%}; reference-frame mapping {a.ref_pos.notna().mean():.1%}; "
          f"{len(AF_FAILED)} proteins have no AlphaFold model."])
"""),
]
NOTEBOOKS = {'A0_cancer_atlas': (A0, False), 'A1_ground_truth': (A1, False), 'A2_features': (A2, True)}
