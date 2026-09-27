"""E2 noise ceiling: how well could ANY predictor score?

Seven SH3 domains were measured twice, independently:
  MegaScale (Tsuboyama/Rocklin) - proteolysis, ddG in kcal/mol
  Domainome (Beltran/Lehner)    - aPCA, cellular abundance
Agreement between the two assays on the SAME variants bounds what a model can
reach against Domainome fitness. Our per-domain rho only means something beside it.

Position mapping (verified empirically, 1102 matches for BTK at the recorded offset):
    rocklin_pos = domainome_position - domain_start + 1 + offset
domain_start is the suffix of domain_ID; offset comes from the overlaps file.

Signs (reference/domainome_column_map.md):
  Rocklin ddG (V35)   negative = destabilising
  aPCA fitness        negative = destabilising   -> the two agree POSITIVELY
  our pred_ddG_fold   positive = destabilising   -> agrees NEGATIVELY
Compared as |rho|.
"""
import pandas as pd, numpy as np
from scipy.stats import spearmanr

B = "input/external/domainome/"
OV = ['pdb_id','uniprot_ID','dom_ID','aa_seq_aPCA','aa_seq_Rocklin','overlap','offset','percent_overlap']
GENE = {'Q06187':'BTK','P08631':'HCK','P06239':'LCK','O15259':'NPHP1','P20936':'RASA1','P07751':'SPTB1'}

ov = pd.read_csv(B+"analysis_files/domains_from_tsuboyama_rocklin_overlaps.txt",
                 sep="\t", header=None, names=OV)
ov = ov[ov.dom_ID.str.contains("PF00018|PF07653|PF14604")]
ov['start'] = ov.dom_ID.str.rsplit('_', n=1).str[1].astype(int)
print(f"{len(ov)} SH3 domain pairs measured in both studies ({ov.uniprot_ID.nunique()} proteins)")

roc = pd.read_csv(B+"analysis_files/K50_dG_Dataset1_Dataset2_in_aPCA.csv", header=None, low_memory=False)
roc['pdb_id'] = roc[29].astype(str).str.split('.pdb').str[0]
m = roc[28].astype(str).str.extract(r'^([A-Z])(\d+)([A-Z])$')
roc = roc.assign(wt_aa=m[0], rpos=pd.to_numeric(m[1], errors='coerce'), mut_aa=m[2],
                 rocklin_ddG=pd.to_numeric(roc[34], errors='coerce'))
roc = roc.dropna(subset=['rpos','rocklin_ddG']).merge(ov, on='pdb_id')

dom = pd.read_csv(B+"Extended_data_Table_2_fitness_scores_normalized_domainranks.txt", sep="\t")
dom['STOP'] = dom.STOP.astype('string').str.upper()
dom = dom[(dom.STOP=='FALSE') & dom.normalized_fitness.notna() & dom.position.notna()]
dom = dom.rename(columns={'domain_ID':'dom_ID'})
dom['start'] = dom.dom_ID.str.rsplit('_', n=1).str[1].astype(int)

d = dom.merge(ov[['dom_ID','offset','percent_overlap']], on='dom_ID')
d['rpos'] = (d.position - d.start + 1 + d.offset).astype(int)

j = roc.merge(d[['dom_ID','rpos','wt_aa','mut_aa','normalized_fitness','mean_input_count',
                 'uniprot_ID','percent_overlap']],
              on=['dom_ID','rpos','wt_aa','mut_aa'], how='inner', suffixes=('','_d'))
j = j[(j.percent_overlap > 80) & (j.mean_input_count > 5)]     # the authors' own QC
print(f"{len(j):,} variants measured by both assays after QC\n")

ours = pd.read_csv("results/E2_domainome_external/per_domain_E2.csv").set_index('domain')
rows = []
for dm, g in j.groupby('dom_ID'):
    if len(g) < 20: continue
    r, p = spearmanr(g.rocklin_ddG, g.normalized_fitness)
    o = ours.rho.get(dm, np.nan)
    rows.append((GENE.get(g.uniprot_ID.iloc[0], g.uniprot_ID.iloc[0]), dm, len(g),
                 abs(r), p, abs(o) if pd.notna(o) else np.nan))
t = (pd.DataFrame(rows, columns=['gene','domain','n','ceiling','p','ours'])
       .sort_values('ceiling', ascending=False))
t['pct_of_ceiling'] = 100 * t.ours / t.ceiling
t.to_csv("results/E2_domainome_external/noise_ceiling_E2.csv", index=False)

print("|rho| throughout. 'ceiling' = MegaScale vs Domainome on the same variants;")
print("'ours' = our frozen head vs Domainome (from E2).\n")
print(t[['gene','n','ceiling','ours','pct_of_ceiling']].to_string(
      index=False, formatters={'ceiling':'{:.3f}'.format, 'ours':'{:.3f}'.format,
                               'pct_of_ceiling':'{:.0f}%'.format}))
s = t.dropna(subset=['ours'])
print(f"\nmedian ceiling {t.ceiling.median():.3f}")
if len(s):
    print(f"median ours    {s.ours.median():.3f}  ->  {100*s.ours.median()/s.ceiling.median():.0f}% of the ceiling")

# ---- matched subset: the ceiling recomputed on exactly the variants we predict ----
ours_v = pd.read_csv("results/E2_domainome_external/matched_variants_E2.csv")
j2 = j.merge(ours_v[['domain_ID','pos_protein','wt_aa','mut_aa','pred_ddG_fold']],
             left_on=['dom_ID','wt_aa','mut_aa'], right_on=['domain_ID','wt_aa','mut_aa'], how='inner')
j2 = j2[j2.rpos == (j2.pos_protein - j2.start + 1 + j2.offset)]
rows = []
for dm, g in j2.groupby('dom_ID'):
    if len(g) < 15: continue
    c = abs(spearmanr(g.rocklin_ddG, g.normalized_fitness)[0])
    o = abs(spearmanr(g.pred_ddG_fold, g.normalized_fitness)[0])
    rows.append((GENE.get(g.uniprot_ID.iloc[0], '?'), dm, len(g), c, o, 100*o/c))
t2 = pd.DataFrame(rows, columns=['gene','domain','n','ceiling','ours','pct_of_ceiling'])
t2.to_csv("results/E2_domainome_external/noise_ceiling_matched_E2.csv", index=False)
print("\nMATCHED SUBSET (identical variants both sides - directly comparable):")
print(t2[['gene','n','ceiling','ours','pct_of_ceiling']].to_string(
      index=False, formatters={'ceiling':'{:.3f}'.format,'ours':'{:.3f}'.format,
                               'pct_of_ceiling':'{:.0f}%'.format}))
