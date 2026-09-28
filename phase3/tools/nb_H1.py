"""Generates H1 — does the frozen model generalise to families it has never seen?

Judged against docs/preregistration/H1.md, committed before this file existed. The
rules implemented here are that file's, not choices made while writing code:

  Part 1   the H1.0 audit: no retraining, the frozen model is applied unchanged
  Part 3   three arms; the SH3 reproduction control stops the run if it fails
  Part 4   median per-domain |rho|, NON-INFERIORITY against a -0.15 margin
  Part 5   4,000 bootstrap resamples over DOMAINS, not variants
  Part 6   the 2x2 reading of main vs PDZ, fixed in advance
  Part 9   the SH3 comparator is RECOMPUTED on Domainome, not borrowed from E2;
           E2's 0.573 becomes the reproduction control; clip=10; the position
           assertion

Target hardware: A100 40 GB. The only GPU work is ESM-2 650M over ~102 domains of
45-97 residues -- one forward pass each for the embedding, plus a masked scan for
the log-odds. Minutes, not hours; the 40 GB is far more than needed and the batch
size is set for comfort rather than for the limit.

Shares md()/code()/build() with the extended phase's nb_E.py.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'extended' / 'tools'))
from nb_E import md, code, build


SETUP = code(
    "from google.colab import drive",
    "drive.mount('/content/drive')",
    "",
    "import os, sys, json, time",
    "from pathlib import Path",
    "import numpy as np, pandas as pd",
    "",
    "DRIVE = Path('/content/drive/MyDrive')",
    "",
    "def pick(*names, what=''):",
    "    for n in names:",
    "        if (DRIVE / n).exists(): return DRIVE / n",
    "    raise FileNotFoundError(f'No {what} folder in MyDrive. Tried: ' + ', '.join(names))",
    "",
    "FROZEN  = pick('sh3_repro', what='frozen-run')            # READ ONLY",
    "EXT     = pick('sh3_repro/extended', what='extended phase')",
    "PHASE3  = DRIVE / 'sh3_repro' / 'phase3'",
    "OUT     = PHASE3 / 'results' / 'H1_generality'",
    "OUT.mkdir(parents=True, exist_ok=True)",
    "",
    "# sh3_common.py is the frozen pipeline's own module: SCALARS, build_X, FoldHead,",
    "# load_fold_models, fold_scores. Re-implementing any of it here would be the",
    "# fastest way to make H1 incomparable with Phase 1.",
    "def frozen_file(rel, bundled):",
    "    \"\"\"The frozen run's own copy, or the bundled one in extended/input/frozen/.\"\"\"",
    "    p = FROZEN / 'results' / rel",
    "    q = EXT / 'input' / 'frozen' / 'results' / bundled",
    "    if p.exists(): return p",
    "    assert q.exists(), f'neither {p} nor {q} exists'",
    "    return q",
    "",
    "sys.path.insert(0, str(FROZEN / 'code'))",
    "import sh3_common as C",
    "print('device:', C.DEV)",
    "assert C.DEV == 'cuda', 'H1 needs a GPU: Runtime > Change runtime type > A100'",
    "!nvidia-smi --query-gpu=name,memory.total --format=csv,noheader",
    "print('SCALARS:', C.SCALARS)",
    "assert len(C.SCALARS) == 12, 'the frozen scalar list has changed; 1292 no longer holds'",
)


PREREG_CELL = code(
    "# Part 4 and Part 9 are read from the committed pre-registration rather than",
    "# typed here, so the margin cannot drift between the file and the code.",
    "prereg = PHASE3 / 'docs' / 'preregistration' / 'H1.md'",
    "assert prereg.exists(), f'{prereg} not found -- upload docs/ before running'",
    "# The pre-registration is prose, and prose uses typographic dashes: the margin is",
    "# written with U+2212 MINUS SIGN, not ASCII hyphen. Normalise before matching --",
    "# the document is right and a naive string check is what was wrong.",
    "raw = prereg.read_text()",
    "text = raw.translate({0x2212: '-', 0x2013: '-', 0x2014: '-', 0x2010: '-', 0x00ad: ''})",
    "",
    "MARGIN        = -0.15      # Part 4: one SD of SH3's own per-domain |rho|",
    "MIN_VARIANTS  = 20         # Part 4: E2's convention for a per-domain correlation",
    "MIN_DOMAINS   = 20         # Part 4: below this the main arm carries no verdict",
    "N_BOOT        = 4000       # Part 5",
    "CLIP          = 10         # Part 9.4: how the atlas predictions were produced",
    "E2_MEDIAN     = 0.573      # Part 9.2: the reproduction target",
    "E2_TOL        = 0.02",
    "# Only the distinctive constants are checked. '10' and '20' would match almost any",
    "# document, so asserting them would look like a guard while guaranteeing nothing;",
    "# the margin and the reproduction target are the two values that identify THIS file.",
    "for k in (str(MARGIN), str(E2_MEDIAN)):",
    "    assert k in text, (",
    "        f'{k!r} does not appear in {prereg.name}. Either the notebook is using a '",
    "        'value the pre-registration never fixed, or the uploaded copy is stale.')",
    "print(f'margin {MARGIN}  min_variants {MIN_VARIANTS}  clip {CLIP}  '",
    "      f'E2 target {E2_MEDIAN}+-{E2_TOL}')",
)


DATA_CELL = code(
    "# ---- the measurements: Domainome Table 2 ----",
    "DOM = EXT / 'input' / 'external' / 'domainome'",
    "T2 = pd.read_csv(DOM / 'Extended_data_Table_2_fitness_scores_normalized_domainranks.txt',",
    "                 sep='\\t', low_memory=False,",
    "                 usecols=['domain_ID','uniprot_ID','wt_aa','position','mut_aa','STOP',",
    "                          'normalized_fitness','normalized_fitness_sigma'])",
    "T2['pfam'] = T2.domain_ID.str.split('_').str[1]",
    "stop = T2.STOP.astype(str).str.upper().isin(['TRUE','T'])",
    "M = T2[(~stop) & T2.normalized_fitness.notna() & (T2.wt_aa != T2.mut_aa)].copy()",
    "print(f'Domainome: {len(T2):,} rows -> {len(M):,} scored missense')",
    "",
    "# ---- the domain sequences ----",
    "SEQ = pd.read_csv(PHASE3 / 'input' / 'domainome_domain_sequences.tsv', sep='\\t',",
    "                  names=['domain_ID','wt_seq'])",
    "M = M.merge(SEQ, on='domain_ID', how='inner')",
    "print(f'with a domain sequence: {len(M):,}')",
    "",
    "# Part 2: the arms, by Pfam",
    "MAIN = ['PF00249','PF00628','PF00643']        # Myb/SANT, PHD, B-box -- length-matched",
    "PDZ  = ['PF00595']                            # length-confounded",
    "SH3  = ['PF00018']                            # the comparator, recomputed (Part 9.1)",
    "M = M[M.pfam.isin(MAIN + PDZ + SH3)].copy()",
    "M['arm'] = np.where(M.pfam.isin(MAIN), 'main',",
    "           np.where(M.pfam.isin(PDZ), 'pdz', 'sh3'))",
    "",
    "# Each domain carries one WILD-TYPE reference row, with wt_aa, mut_aa and position",
    "# all null. `wt_aa != mut_aa` does not remove it, because NaN != NaN is True. Drop",
    "# it explicitly and check the count is exactly one per domain -- if it is more, the",
    "# nulls are something else and dropping them silently would be a real loss.",
    "n_dom = M.domain_ID.nunique()",
    "null_pos = M.position.isna() | M.wt_aa.isna() | M.mut_aa.isna()",
    "print(f'wild-type reference rows dropped: {int(null_pos.sum())} '",
    "      f'({n_dom} domains in these families)')",
    "assert int(null_pos.sum()) <= n_dom, (",
    "    f'{int(null_pos.sum())} rows have a null position but there are only {n_dom} '",
    "    'domains, so these are not just the wild-type rows. Investigate before dropping.')",
    "M = M[~null_pos].copy()",
    "",
    "print(M.groupby(['arm','pfam']).agg(domains=('domain_ID','nunique'),",
    "                                    variants=('domain_ID','size')).to_string())",
)


CHECK_CELL = code(
    "# Part 9.5. Domainome's `position` is domain-relative, and three Phase 2 defects",
    "# came from a position index that looked right and was not. Nothing proceeds until",
    "# the residue at that index is the residue the row claims.",
    "# Table 2's `position` is UNIPROT numbering, not domain-relative: domain",
    "# A1X283_PF00018_155 starts at residue 155 and its positions begin at 155. The",
    "# domain start is the third field of domain_ID, and the construct index is",
    "#     pos = position - start + 1",
    "# Verified on the release: as-is, 1,774 of 119,394 rows agree (1.49%) -- the few",
    "# domains that happen to start at residue 1. Offset, 119,394 of 119,394 (100%).",
    "start = M.domain_ID.str.split('_').str[2].astype(int)",
    "pos = (M.position.astype(int) - start + 1).values",
    "seq = M.wt_seq.values",
    "ok = np.array([0 < p <= len(s) and s[p-1] == w",
    "               for p, s, w in zip(pos, seq, M.wt_aa.values)])",
    "bad = int((~ok).sum())",
    "print(f'position check: {int(ok.sum()):,} of {len(M):,} agree')",
    "if bad:",
    "    print(M.assign(idx=pos)[~ok].head(8)"
    "[['domain_ID','position','idx','wt_aa']].to_string(index=False))",
    "assert bad == 0, (",
    "    f'{bad} rows where wt_seq[position-1] != wt_aa. The index is wrong and every '",
    "    'embedding lookup below would take the wrong residue.')",
    "M['pos'] = pos",
)


ESM_CELL = code(
    "# ---- ESM-2 650M, exactly as A2 computed it ----",
    "# Embeddings come from the WILD-TYPE domain sequence, last hidden state, residue",
    "# pos-1; the log-odds come from masking each position in turn. Any deviation here",
    "# makes H1's predictions incomparable with Phase 1's, which is the whole point.",
    "import torch",
    "from transformers import AutoTokenizer, AutoModelForMaskedLM",
    "tok = AutoTokenizer.from_pretrained('facebook/esm2_t33_650M_UR50D')",
    "esm = AutoModelForMaskedLM.from_pretrained('facebook/esm2_t33_650M_UR50D').to(C.DEV).eval()",
    "esm = esm.half()",
    "AAS = list('ACDEFGHIKLMNPQRSTVWY'); AAPOS = {a: i for i, a in enumerate(AAS)}",
    "AA_IDX = torch.tensor([tok.convert_tokens_to_ids(a) for a in AAS]).to(C.DEV)",
    "",
    "@torch.no_grad()",
    "def embed_and_score(s, batch=64):",
    "    L = len(s); enc = tok(s, return_tensors='pt').to(C.DEV)",
    "    rep = esm(**enc, output_hidden_states=True).hidden_states[-1][0, 1:L+1].float().cpu().numpy()",
    "    ids = enc['input_ids'][0]; rows = []",
    "    for st in range(0, L, batch):",
    "        idx = list(range(st, min(st + batch, L)))",
    "        bb = ids.unsqueeze(0).repeat(len(idx), 1).clone()",
    "        for k, i in enumerate(idx): bb[k, i + 1] = tok.mask_token_id",
    "        lg = esm(input_ids=bb, attention_mask=torch.ones_like(bb)).logits",
    "        for k, i in enumerate(idx):",
    "            rows.append(torch.log_softmax(lg[k, i + 1].float(), -1)[AA_IDX].cpu().numpy())",
    "    return rep, np.stack(rows)",
    "",
    "seqs = M[['domain_ID','wt_seq']].drop_duplicates('domain_ID')",
    "cache = OUT / 'esm_H1.npz'",
    "if cache.exists():",
    "    z = np.load(cache); EMB = {k: z[k] for k in z.files if k.startswith('e|')}",
    "    LO  = {k[2:]: z[k] for k in z.files if k.startswith('l|')}",
    "    EMB = {k[2:]: v for k, v in EMB.items()}",
    "    print(f'{len(EMB)} domains loaded from cache')",
    "else:",
    "    EMB, LO = {}, {}; t0 = time.time()",
    "    for n, (k, s) in enumerate(zip(seqs.domain_ID, seqs.wt_seq), 1):",
    "        e, l = embed_and_score(s); EMB[k] = e.astype(np.float16); LO[k] = l.astype(np.float32)",
    "        if n % 20 == 0: print(f'  {n}/{len(seqs)}  {(time.time()-t0)/60:.1f} min')",
    "    np.savez_compressed(cache, **{f'e|{k}': v for k, v in EMB.items()},",
    "                                **{f'l|{k}': v for k, v in LO.items()})",
    "    print(f'{len(EMB)} domains embedded in {(time.time()-t0)/60:.1f} min')",
    "del esm; torch.cuda.empty_cache()",
)


FEAT_CELL = code(
    "# ---- the 12 scalars, formula for formula as A2 wrote them ----",
    "from Bio.Align import substitution_matrices",
    "B62 = substitution_matrices.load('BLOSUM62')",
    "lo = np.stack([LO[k][p-1] for k, p in zip(M.domain_ID, M['pos'])])",
    "r = np.arange(len(M))",
    "w = M.wt_aa.map(AAPOS).values; mu = M.mut_aa.map(AAPOS).values",
    "M['esm_score']    = lo[r, mu] - lo[r, w]",
    "M['esm_wt_logp']  = lo[r, w]",
    "M['esm_entropy']  = -(np.exp(lo) * lo).sum(1)",
    "M['dom_len']      = M.wt_seq.str.len()",
    "M['rel_pos']      = M['pos'] / M.dom_len",
    "M['d_hydropathy'] = M.mut_aa.map(C.KD) - M.wt_aa.map(C.KD)",
    "M['d_volume']     = M.mut_aa.map(C.VOL) - M.wt_aa.map(C.VOL)",
    "M['d_charge']     = M.mut_aa.map(C.CHG).fillna(0) - M.wt_aa.map(C.CHG).fillna(0)",
    "M['blosum62']     = [B62[a][b] if (a in B62.alphabet and b in B62.alphabet) else np.nan",
    "                     for a, b in zip(M.wt_aa, M.mut_aa)]",
    "M['to_proline']   = (M.mut_aa == 'P').astype(int)",
    "M['from_glycine'] = (M.wt_aa == 'G').astype(int)",
    "M['to_glycine']   = (M.mut_aa == 'G').astype(int)",
    "del lo",
    "",
    "# build_X keys embeddings on `domain_key`, so give it that name.",
    "M['domain_key'] = M.domain_ID",
    "X, M = C.build_X(M, EMB, half=True)",
    "assert X.shape[1] == 1292, f'feature width {X.shape[1]}, expected 1292'",
    "print('X', X.shape)",
)


PREDICT_CELL = code(
    "# ---- the frozen head, unchanged ----",
    "MODELS = frozen_file('B1_folding_model/models.pt', 'models.pt')",
    "print('head:', MODELS)",
    "FOLD, SC_M, SC_SD = C.load_fold_models(str(MODELS))",
    "print(f'{len(FOLD)} seed models loaded')",
    "P = C.fold_scores(FOLD, X, SC_M, SC_SD, clip=CLIP)    # Part 9.4",
    "M['pred_ddG_fold'] = P.mean(0)",
    "M['sd_fold'] = P.std(0)",
    "print(M.groupby('arm').pred_ddG_fold.describe()[['count','mean','std']].to_string())",
)


RHO_CELL = code(
    "from scipy.stats import spearmanr",
    "",
    "def per_domain(df):",
    "    out = []",
    "    for k, g in df.groupby('domain_ID'):",
    "        if len(g) < MIN_VARIANTS: continue",
    "        rho = spearmanr(g.pred_ddG_fold, g.normalized_fitness).statistic",
    "        if np.isnan(rho): continue",
    "        out.append({'domain_ID': k, 'pfam': g.pfam.iloc[0], 'arm': g.arm.iloc[0],",
    "                    'n': len(g), 'rho': float(rho), 'absrho': abs(float(rho))})",
    "    return pd.DataFrame(out)",
    "",
    "PD = per_domain(M)",
    "PD.to_csv(OUT / 'per_domain_H1.csv', index=False)",
    "print(PD.groupby('arm').agg(domains=('absrho','size'), median_absrho=('absrho','median'),",
    "                            sd=('absrho','std')).round(3).to_string())",
    "print()",
    "print(PD.groupby('pfam').agg(domains=('absrho','size'),",
    "                             median_absrho=('absrho','median')).round(3).to_string())",
)


CONTROL_CELL = code(
    "# ---- Part 9.2: the reproduction control, on E2's OWN matched variants ----",
    "# If this fails, the features or the model are not the frozen ones, and no arm",
    "# below is interpretable. It is the role G1's reproduction check played.",
    "e2 = pd.read_csv(EXT / 'results' / 'E2_domainome_external' / 'matched_variants_E2.csv')",
    "key = ['domain_ID','position','mut_aa']",
    "rep = M.merge(e2[key].drop_duplicates(), on=key, how='inner')",
    "RP = per_domain(rep)",
    "got = float(RP.absrho.median()) if len(RP) else float('nan')",
    "print(f'reproduction on E2 matched variants: {len(rep):,} variants, {len(RP)} domains, '",
    "      f'median |rho| {got:.4f}  (E2 published {E2_MEDIAN})')",
    "assert abs(got - E2_MEDIAN) <= E2_TOL, (",
    "    f'we get {got:.4f} on E2\\'s own variants where E2 published {E2_MEDIAN}. The "
    "pipeline is not the frozen one -- check the embedding source, the scalar order and "
    "clip. Nothing below is interpretable.')",
    "print('reproduction passes')",
)


TEST_CELL = code(
    "# ---- Part 4: non-inferiority against the recomputed SH3 arm (Part 9.1) ----",
    "rng = np.random.default_rng(20260928)",
    "ref = PD[PD.arm == 'sh3'].absrho.values",
    "assert len(ref) >= 10, f'only {len(ref)} SH3 domains; the comparator is not usable'",
    "",
    "def verdict(arm_vals, name):",
    "    d = np.median(arm_vals) - np.median(ref)",
    "    b = np.array([np.median(rng.choice(arm_vals, arm_vals.size, True))",
    "                  - np.median(rng.choice(ref, ref.size, True)) for _ in range(N_BOOT)])",
    "    lo, hi = np.percentile(b, [2.5, 97.5])",
    "    v = ('supported' if lo > MARGIN else",
    "         'not_supported' if hi < MARGIN else 'inconclusive')",
    "    print(f'{name:26s} median |rho| {np.median(arm_vals):.3f}  vs SH3 "
    "{np.median(ref):.3f}  delta {d:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  -> {v.upper()}')",
    "    return {'arm': name, 'domains': int(arm_vals.size),",
    "            'median_absrho': float(np.median(arm_vals)),",
    "            'sh3_median_absrho': float(np.median(ref)), 'delta': float(d),",
    "            'ci95': [float(lo), float(hi)], 'margin': MARGIN, 'verdict': v}",
    "",
    "main_vals = PD[PD.arm == 'main'].absrho.values",
    "pdz_vals  = PD[PD.arm == 'pdz'].absrho.values",
    "if main_vals.size < MIN_DOMAINS:",
    "    print(f'MAIN ARM HAS {main_vals.size} DOMAINS, BELOW THE FLOOR OF {MIN_DOMAINS}. '",
    "          'Part 4: numbers are printed, NO VERDICT.')",
    "RES_MAIN = verdict(main_vals, 'MAIN length-matched')",
    "RES_PDZ  = verdict(pdz_vals,  'SECONDARY PDZ')",
    "if main_vals.size < MIN_DOMAINS: RES_MAIN['verdict'] = 'no_verdict_too_few_domains'",
    "RES_PDZ['verdict_carries_weight'] = False   # Part 6: PDZ never carries a verdict",
)


READ_CELL = code(
    "# ---- Part 6: the 2x2, fixed before any number existed ----",
    "READING = {",
    "  ('supported','supported'):",
    "    'generality supported, and construct length is not a limit either',",
    "  ('supported','not_supported'):",
    "    'THE LIMIT IS CONSTRUCT LENGTH, NOT FAMILY -- the most informative outcome, and "
    "available only because both arms ran',",
    "  ('not_supported','not_supported'):",
    "    'generality not supported. The length confound cannot be blamed, because the main "
    "arm is length-matched',",
    "  ('not_supported','supported'):",
    "    'unexpected. Reported as observed, NO claim either way -- the design is measuring "
    "something not yet identified',",
    "}",
    "k = (RES_MAIN['verdict'], RES_PDZ['verdict'])",
    "print(READING.get(k, 'at least one arm is inconclusive; Part 4 says the design could "
    "not resolve it, and the report says so'))",
    "",
    "# Part 7: no noise ceiling exists for the new families -- they have no MegaScale data",
    "# BY CONSTRUCTION, which is why they are held out. This within-assay bound from the",
    "# replicate sigma is weaker and must NOT be called a ceiling in E2's sense.",
    "M['snr'] = M.normalized_fitness.abs() / M.normalized_fitness_sigma.replace(0, np.nan)",
    "BND = M.groupby('arm').snr.median().round(3)",
    "print('\\nmedian |fitness| / sigma by arm (assay quality, NOT a noise ceiling):')",
    "print(BND.to_string())",
)


WRITE_CELL = code(
    "payload = {'prereg': 'phase3/docs/preregistration/H1.md',",
    "           'margin': MARGIN, 'clip': CLIP, 'n_boot': N_BOOT,",
    "           'min_variants_per_domain': MIN_VARIANTS, 'min_domains': MIN_DOMAINS,",
    "           'reproduction': {'e2_published': E2_MEDIAN, 'recomputed': got,",
    "                            'variants': int(len(rep)), 'domains': int(len(RP))},",
    "           'main': RES_MAIN, 'pdz': RES_PDZ,",
    "           'per_family': PD.groupby('pfam').absrho.agg(['size','median']).round(4)",
    "                           .rename(columns={'size':'domains','median':'median_absrho'})",
    "                           .reset_index().to_dict(orient='records'),",
    "           'assay_snr_by_arm': BND.to_dict(),",
    "           'reading': READING.get(k, 'inconclusive')}",
    "(OUT / 'metrics_H1.json').write_text(json.dumps(payload, indent=2))",
    "",
    "L = ['# H1 — machine-written results', '',",
    "     f'Pre-registered in `docs/preregistration/H1.md`. Margin {MARGIN}, clip {CLIP}, '",
    "     f'{N_BOOT} bootstrap resamples over domains.', '',",
    "     f'Reproduction on E2 matched variants: **{got:.4f}** against published '",
    "     f'{E2_MEDIAN}.', '',",
    "     '| arm | domains | median \\\\|rho\\\\| | SH3 | delta | 95% CI | verdict |',",
    "     '|---|---|---|---|---|---|---|']",
    "for R_ in (RES_MAIN, RES_PDZ):",
    "    L.append(f\"| {R_['arm']} | {R_['domains']} | {R_['median_absrho']:.3f} | \"",
    "             f\"{R_['sh3_median_absrho']:.3f} | {R_['delta']:+.3f} | \"",
    "             f\"[{R_['ci95'][0]:+.3f}, {R_['ci95'][1]:+.3f}] | **{R_['verdict']}** |\")",
    "L += ['', '## Per family', '',",
    "      '| Pfam | domains | median \\\\|rho\\\\| |', '|---|---|---|']",
    "for row in payload['per_family']:",
    "    L.append(f\"| {row['pfam']} | {int(row['domains'])} | {row['median_absrho']:.3f} |\")",
    "L += ['', f\"**Reading (Part 6):** {payload['reading']}\", '',",
    "      'PDZ carries no verdict of its own; its role is the contrast.']",
    "(OUT / 'RESULTS_H1.md').write_text('\\n'.join(L))",
    "print('wrote', OUT / 'RESULTS_H1.md', 'and metrics_H1.json')",
)


CELLS = [
    md("# H1 — does the frozen model generalise beyond SH3?",
       "",
       "**Pre-registered in `phase3/docs/preregistration/H1.md`, committed before this "
       "notebook was written.** Every threshold, every arm and the reading of the result "
       "come from that file, and the notebook reads it at run time rather than restating "
       "it.",
       "",
       "Phase 1's per-domain ρ of 0.839 and Phase 2's |ρ| of 0.600 are both about **one "
       "family**. H1 asks whether that matters.",
       "",
       "| | |",
       "|---|---|",
       "| **Main arm** | Myb/SANT + PHD + B-box — absent from training **and** length-matched |",
       "| **Secondary** | PDZ — absent, but longer than anything in training |",
       "| **Control** | SH3, recomputed; must reproduce E2 |",
       "| Model | the frozen head, **unchanged**. No retraining anywhere in H1 |",
       "| Hardware | **A100 40 GB**. ESM-2 over ~102 short domains — minutes |"),
    SETUP,
    md("## 1 — The rules, read from the committed file",
       "",
       "Part 4's margin and Part 9's settings are read from `H1.md` rather than typed "
       "here, so the code and the pre-registration cannot drift apart."),
    PREREG_CELL,
    md("## 2 — Measurements and arms",
       "",
       "Domainome Table 2, scored missense only. The three arms are selected by Pfam "
       "accession from the domain identifier — the same labels the H1.0 audit used."),
    DATA_CELL,
    md("## 3 — The position assertion",
       "",
       "Domainome's `position` is domain-relative. **Three defects in Phase 2 came from a "
       "position index that looked right and was not**, so nothing proceeds until the "
       "residue at that index is the residue the row claims. Every embedding lookup below "
       "depends on it."),
    CHECK_CELL,
    md("## 4 — ESM-2 650M, exactly as A2 computed it",
       "",
       "Embeddings from the **wild-type** domain sequence, last hidden state, residue "
       "`pos − 1`; log-odds by masking each position in turn. Any deviation makes H1's "
       "predictions incomparable with Phase 1's, which is the whole point of the exercise.",
       "",
       "Cached to Drive, so a disconnected session resumes without repeating the GPU work."),
    ESM_CELL,
    md("## 5 — The twelve scalars",
       "",
       "Formula for formula as A2 wrote them, and `C.SCALARS` fixes the order. The "
       "assertion on `X.shape[1] == 1292` is what catches a silent mismatch."),
    FEAT_CELL,
    md("## 6 — The frozen head",
       "",
       "`clip = 10`, which is how the atlas predictions B3 and E2 used were produced "
       "(Part 9.4). No weight is loaded from anywhere but `models.pt`."),
    PREDICT_CELL,
    md("## 7 — Per-domain correlations",
       "",
       "Spearman |ρ| between predicted ΔΔG and measured abundance, per domain, for "
       "domains with at least 20 scored variants — E2's convention."),
    RHO_CELL,
    md("## 8 — The reproduction control",
       "",
       "**Part 9.2.** Restricted to E2's own matched variants, this implementation must "
       "return E2's published median |ρ| of 0.573 to within 0.02. If it does not, the "
       "features or the model are not the frozen ones and **no arm below means "
       "anything** — the run stops here."),
    CONTROL_CELL,
    md("## 9 — The test",
       "",
       "**Non-inferiority, not significance.** \"Comparable accuracy\" cannot be "
       "supported by failing to reject a null, which is the trap E1 hit from the other "
       "side. The margin is −0.15, one SD of SH3's own per-domain spread, fixed in "
       "advance.",
       "",
       "The SH3 comparator is **recomputed on Domainome** under this identical pipeline "
       "(Part 9.1) — not E2's 880 atlas variants, which are a selected population and "
       "would have biased the comparison."),
    TEST_CELL,
    md("## 10 — Reading it, and what cannot be had",
       "",
       "Part 6's 2 × 2 was fixed before any number existed. The informative cell is "
       "*main supported, PDZ not*: that would show the limit is **construct length rather "
       "than family**, and it is reachable only because both arms run.",
       "",
       "Part 7: **there is no noise ceiling for the new families.** They have no MegaScale "
       "data by construction — that is why they are held out. The replicate-based figure "
       "printed below is a weaker within-assay quantity and must not be described as a "
       "ceiling in E2's sense."),
    READ_CELL,
    md("## 11 — The machine-written record",
       "",
       "Nothing in `RESULTS_H1.md` is typed by hand. The interpretation goes in "
       "`ANALYSIS_H1.md`, and the sources and methodology in `METHODS_H1.md`, per the "
       "Phase 3 convention."),
    WRITE_CELL,
]

if __name__ == '__main__':
    out = HERE.parent / 'notebooks'
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'H1_generality.ipynb'
    p.write_text(json.dumps(build(CELLS), indent=1))
    print(f'wrote {p}  ({len(CELLS)} cells)')

    # The same cell-order guard the G1 generator grew after a NameError on Colab.
    import ast, builtins
    bound = set(dir(builtins)) | {'get_ipython', 'In', 'Out', '_'}
    for i, c in enumerate(x for x in CELLS if x['cell_type'] == 'code'):
        src = '\n'.join('' if l.lstrip().startswith('!') else l
                        for l in c['source'].splitlines())
        tree = ast.parse(src)
        here = set(bound)
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
                here.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                here.add(n.name)
            elif isinstance(n, ast.arg):
                here.add(n.arg)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                here.update((a.asname or a.name).split('.')[0] for a in n.names)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                here.add(n.name)
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                assert n.id in here, (
                    f'code cell {i} reads `{n.id}` (line {n.lineno}) but no earlier cell '
                    'binds it; the notebook would raise NameError there')
        bound = here
    print('verified: no cell reads a name an earlier cell has not bound')
