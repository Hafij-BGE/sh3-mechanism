#!/usr/bin/env python3
"""
H1.0 — is the candidate family in the training set?

The frozen model held out SH3 and trained on everything else in MegaScale, so every
other family was in training.  Applying it to a second family only tests generality
if that family is genuinely absent.  E3 is why this is asked first: its pre-commit
check found 13 of our 15 held-out domains inside ThermoMPNN's published training
split, and disqualified the comparison before it ran rather than after.

The question is specifically: **are the Domainome domains we would evaluate on
present in MegaScale?**  So the audit matches in that direction -- every MegaScale
training domain against every Domainome domain, which carries a Pfam label -- rather
than trying to name the family of MegaScale's many de novo designs.

Two numbers come out, and both matter:

  1. how many MegaScale domains belong to each Domainome family
  2. the LENGTH distribution of each family against MegaScale's own

The second is not a detail.  MegaScale's proteolysis assay caps constructs at 72
residues, so any family longer than that is absent *by construction* -- held out,
but held out for the wrong reason.  Evaluating on it confounds "new family" with
"longer than anything in training".

    python3 tools/h1_leakage_audit.py --root .. --out results/H1_0_leakage_audit
"""
import argparse
import json
from pathlib import Path

import pandas as pd

MIN_IDENTITY = 0.50          # the threshold Phase 1 used to match MegaScale to UniProt
LEN_TOLERANCE = 40           # skip pairs too different in length to align meaningfully


def best_identity(a: str, b: str) -> float:
    """Max fractional identity of the shorter sequence over all offsets of the longer.

    The same sliding comparison A2 used to derive PDB offsets: no gaps, because these
    are constructs of the same region rather than diverged homologues.
    """
    if len(a) > len(b):
        a, b = b, a
    best = 0
    for k in range(len(b) - len(a) + 1):
        m = sum(x == y for x, y in zip(a, b[k:]))
        if m > best:
            best = m
    return best / len(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='..')
    ap.add_argument('--domainome', required=True,
                    help='TSV of dom_id<TAB>sequence extracted from the Domainome '
                         'structural annotation')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    dom = pd.read_csv(a.domainome, sep='\t', names=['dom_id', 'seq'])
    dom['pfam'] = dom['dom_id'].str.split('_').str[1]
    ms = (pd.read_parquet(root / 'results/A2_features/features_megascale.parquet',
                          columns=['domain_key', 'wt_seq', 'is_sh3'])
            .drop_duplicates('domain_key'))
    ms['L'] = ms['wt_seq'].str.len()
    dom['L'] = dom['seq'].str.len()

    rows = []
    dseqs = list(zip(dom['dom_id'], dom['seq'], dom['pfam']))
    for dk, seq, sh3 in zip(ms['domain_key'], ms['wt_seq'], ms['is_sh3']):
        bi, bid, bp = 0.0, None, None
        for did, ds, pf in dseqs:
            if abs(len(ds) - len(seq)) > LEN_TOLERANCE:
                continue
            v = best_identity(seq, ds)
            if v > bi:
                bi, bid, bp = v, did, pf
        rows.append((dk, bool(sh3), round(bi, 3), bid, bp))
    r = pd.DataFrame(rows, columns=['megascale_domain', 'is_sh3', 'identity',
                                    'best_domainome', 'pfam'])
    r.to_csv(out / 'megascale_family_map.csv', index=False)
    hit = r[r['identity'] >= MIN_IDENTITY]

    # The audit validates itself on SH3: the one family we know is in MegaScale.
    sh3_found = int((hit['pfam'] == 'PF00018').sum())
    assert sh3_found >= 20, (
        f'only {sh3_found} MegaScale domains matched SH3 (PF00018), but the training '
        'table marks 26 as is_sh3. The matching is not working; nothing below is '
        'trustworthy.')

    fam = (dom.groupby('pfam')
              .agg(domainome_domains=('dom_id', 'size'), median_len=('L', 'median'),
                   min_len=('L', 'min'), max_len=('L', 'max')).reset_index())
    fam['megascale_domains'] = fam['pfam'].map(
        hit['pfam'].value_counts()).fillna(0).astype(int)
    fam['in_training'] = fam['megascale_domains'] > 0
    fam['length_matched'] = (fam['median_len'] >= ms['L'].min()) & \
                            (fam['median_len'] <= ms['L'].max())
    fam = fam.sort_values('domainome_domains', ascending=False)
    fam.to_csv(out / 'family_audit.csv', index=False)

    m = {
        'megascale': {'domains': int(len(ms)), 'rows': 389068,
                      'len_min': int(ms['L'].min()), 'len_max': int(ms['L'].max()),
                      'len_median': float(ms['L'].median())},
        'matched_to_a_domainome_family': int(len(hit)),
        'sh3_control': {'is_sh3_in_training': int(ms['is_sh3'].sum()),
                        'matched_PF00018': sh3_found},
        'candidates': fam[(~fam['in_training']) & fam['length_matched'] &
                          (fam['domainome_domains'] >= 15)]
                        .to_dict(orient='records'),
        'pdz': fam[fam['pfam'] == 'PF00595'].to_dict(orient='records'),
    }
    (out / 'metrics_H1_0.json').write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))


if __name__ == '__main__':
    main()
