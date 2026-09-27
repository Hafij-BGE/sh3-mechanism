import pandas as pd, numpy as np
from scipy.stats import spearmanr
P="/home/hafij/Documents/thesis/sh3 updated/results/"
D="/home/hafij/Documents/thesis/SH3 extended/Downloded data/Human Domainome 1.0 — external human stability measurements/"

pred = pd.read_parquet(P+"B3_uncertainty_and_calls/atlas_predictions.parquet")
atlas = pd.read_csv(P+"A0_cancer_atlas/SH3_cancer_master.tsv", sep="\t",
                    usecols=["variant_id","uniprot","pos_protein","wt_aa","mut_aa","gene"])
pred = pred.merge(atlas[["variant_id","pos_protein"]], on="variant_id", how="left")

dom = pd.read_csv(D+"Supplementary_Table_2_fitness_scores_normalized_domainranks from version 5.txt/Extended_data_Table_2_fitness_scores_normalized_domainranks.txt",
                  sep="\t", usecols=["domain_ID","uniprot_ID","wt_aa","position","mut_aa","STOP",
                                     "normalized_fitness","normalized_fitness_sigma","quality_rank"])
stop = dom.STOP.astype("string").str.upper()
dom = dom[(stop=="FALSE") & dom.normalized_fitness.notna()]

m = pred.merge(dom, left_on=["uniprot","pos_protein","wt_aa","mut_aa"],
                    right_on=["uniprot_ID","position","wt_aa","mut_aa"], how="inner")
print(f"matched variants: {len(m)}   domains: {m.domain_ID.nunique()}   genes: {m.gene.nunique()}")

r,p = spearmanr(m.pred_ddG_fold, m.normalized_fitness)
print(f"\nPOOLED  Spearman rho = {r:+.3f}  (p={p:.2e}, n={len(m)})")
print("  negative is correct: high predicted ddG (destabilising) -> low abundance")

print("\nPER DOMAIN (n>=20):")
rows=[]
for d,g in m.groupby("domain_ID"):
    if len(g)>=20:
        rr,pp = spearmanr(g.pred_ddG_fold, g.normalized_fitness)
        rows.append((d, g.gene.iloc[0], len(g), rr))
t = pd.DataFrame(rows, columns=["domain","gene","n","rho"]).sort_values("rho")
for _,x in t.iterrows(): print(f"  {x.gene:<10} {x.domain:<24} n={x.n:<4} rho={x.rho:+.3f}")
print(f"\n  median rho = {t.rho.median():+.3f}   domains with rho<0: {(t.rho<0).sum()}/{len(t)}")

print("\nDESTABILISING CALLS (fold_lo >= 1):")
m["destab"] = m.fold_lo >= 1
print(m.groupby("destab").normalized_fitness.agg(n="size", median="median", mean="mean").to_string())
from scipy.stats import mannwhitneyu
a=m.loc[m.destab,"normalized_fitness"]; b=m.loc[~m.destab,"normalized_fitness"]
if len(a)>0:
    u,pu = mannwhitneyu(a,b,alternative="less")
    print(f"  Mann-Whitney (destab < tolerated): U={u:.0f}, p={pu:.3e}")
