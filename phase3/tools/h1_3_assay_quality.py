#!/usr/bin/env python3
"""
H1.3 — Is H1's family ordering assay quality?

H1 returned inconclusive on its main arm and named two explanations it could not
separate: zinc coordination, and assay quality.  This tests the second.

Pre-registered in `docs/preregistration/H1_3_assay_quality.md`, committed before the
join between accuracy and assay quality existed.  It is pre-registered BECAUSE it is
post-hoc: the question came from H1's result, so the rule had to be fixed first.

Nothing is re-predicted.  H1's per-domain |rho| is read as published.

    python3 tools/h1_3_assay_quality.py --rho <per_domain_H1.csv> \
        --domainome <Table2.txt> --out results/H1_3_assay_quality
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

MARGIN = -0.15
N_BOOT = 4000
SHIFT_THRESHOLD = 0.05      # a third of the margin; smaller is below this design's resolution
MIN_DOMAINS = 20
MIN_VARIANTS = 20
SEED = 20260928


def assay_quality(table2: Path) -> pd.DataFrame:
    """median |normalized_fitness| / sigma per domain. No prediction touches this."""
    d = pd.read_csv(table2, sep='\t', low_memory=False,
                    usecols=['domain_ID', 'wt_aa', 'position', 'mut_aa', 'STOP',
                             'normalized_fitness', 'normalized_fitness_sigma'])
    stop = d['STOP'].astype(str).str.upper().isin(['TRUE', 'T'])
    d = d[(~stop) & d['normalized_fitness'].notna() & (d['wt_aa'] != d['mut_aa'])]
    d = d[~(d['position'].isna() | d['wt_aa'].isna() | d['mut_aa'].isna())]
    d['snr'] = d['normalized_fitness'].abs() / d['normalized_fitness_sigma'].replace(0, np.nan)
    g = d.groupby('domain_ID').agg(n=('snr', 'size'), snr=('snr', 'median')).reset_index()
    return g[g['n'] >= MIN_VARIANTS]


def delta(a: np.ndarray, ref: np.ndarray, rng) -> dict:
    d = float(np.median(a) - np.median(ref))
    b = np.array([np.median(rng.choice(a, a.size, True)) - np.median(rng.choice(ref, ref.size, True))
                  for _ in range(N_BOOT)])
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {'n_arm': int(a.size), 'n_ref': int(ref.size),
            'median_arm': float(np.median(a)), 'median_ref': float(np.median(ref)),
            'delta': d, 'ci95': [float(lo), float(hi)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rho', required=True)
    ap.add_argument('--domainome', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    R = pd.read_csv(a.rho)
    Q = assay_quality(Path(a.domainome))
    D = R.merge(Q[['domain_ID', 'snr']], on='domain_ID', how='inner')
    assert len(D) == len(R), (
        f'{len(D)} of {len(R)} H1 domains found an assay-quality value; the join lost '
        'rows and the comparison would be on a different set than H1 reported')
    D.to_csv(out / 'per_domain_rho_and_snr.csv', index=False)

    rng = np.random.default_rng(SEED)
    main_, sh3, pdz = (D[D.arm == k] for k in ('main', 'sh3', 'pdz'))

    # Part 3: the band is the main arm's 10th percentile to SH3's 90th.
    lo, hi = float(main_.snr.quantile(.10)), float(sh3.snr.quantile(.90))
    inb = lambda df: df[(df.snr >= lo) & (df.snr <= hi)]
    m_m, m_s, m_p = inb(main_), inb(sh3), inb(pdz)

    unmatched = delta(main_.absrho.values, sh3.absrho.values, rng)
    matched = delta(m_m.absrho.values, m_s.absrho.values, rng)

    # Part 4's rule for Q1
    shift = matched['delta'] - unmatched['delta']          # >0 means closer to zero
    if matched['ci95'][0] <= 0 <= matched['ci95'][1]:
        q1 = 'assay_quality_explains_the_gap'
    elif matched['ci95'][1] < 0 and abs(shift) <= SHIFT_THRESHOLD:
        q1 = 'assay_quality_does_not_explain_it'
    elif matched['ci95'][1] < 0:
        q1 = 'partly'
    else:
        q1 = 'inconclusive'
    if min(len(m_m), len(m_s)) < MIN_DOMAINS:
        q1 = 'no_verdict_too_few_domains'

    q2 = delta(m_p.absrho.values, m_s.absrho.values, rng) if len(m_p) else None
    rs = spearmanr(D.absrho, D.snr)

    m = {'prereg': 'docs/preregistration/H1_3_assay_quality.md',
         'band': {'lo': lo, 'hi': hi,
                  'kept': {k: [int(len(inb(v))), int(len(v))]
                           for k, v in (('main', main_), ('sh3', sh3), ('pdz', pdz))}},
         'q1_main_vs_sh3': {'unmatched': unmatched, 'matched': matched,
                            'shift_toward_zero': float(shift),
                            'shift_threshold': SHIFT_THRESHOLD, 'verdict': q1},
         'q2_pdz_vs_sh3_matched': q2,
         'q3_rho_vs_snr_all_domains': {'n': int(len(D)),
                                       'spearman': float(rs.statistic),
                                       'p': float(rs.pvalue)},
         'per_family_snr': D.groupby('pfam').snr.median().round(3).to_dict()}
    (out / 'metrics_H1_3.json').write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))


if __name__ == '__main__':
    main()
