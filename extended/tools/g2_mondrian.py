#!/usr/bin/env python3
"""
G2 — per-domain (Mondrian) conformal intervals.

The frozen run calibrated one global conformal quantile, q90 = 6.807, and reported
89.9 % empirical coverage.  That is **marginal** coverage: correct on average over
all held-out variants.  It says nothing about any particular domain, and the
stratified table B3 itself printed shows the spread is wide -- 83.3 % on LYN against
95.0 % on FYN.

A 90 % interval that is really 83 % on one domain and 95 % on another is two
different instruments sharing a name.  Mondrian conformal prediction fixes this by
calibrating within each stratum, so coverage holds *conditionally* on the domain
rather than only on average.

What this program does NOT do: re-fit the model, change a prediction, or move the
`fold_lo >= 1` rule.  It recalibrates an interval and reports what that does to the
count of confident calls, beside the published 410 rather than in place of it.
There is no pass/fail verdict here, so there is no pre-registration.

    python3 tools/g2_mondrian.py --root . --out results/G2_mondrian
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

EPS = 0.05                  # B3's normaliser floor, unchanged
SEED = 0                    # B3's split seed, unchanged
PUBLISHED_Q90 = 6.807
PUBLISHED_COVERAGE = 0.899
PUBLISHED_CALLS = 410
MIN_CAL = 100               # below this a per-domain 90 % quantile is not estimable


def conformal_q(err: np.ndarray, sd: np.ndarray, alpha: float) -> float:
    """B3's quantile, character for character, so the global number reproduces."""
    s = np.sort(err / (sd + EPS))
    return float(s[min(int(np.ceil((len(s) + 1) * (1 - alpha))), len(s)) - 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    F = root / 'input/frozen/results'

    T = pd.read_parquet(F / 'heldout_predictions.parquet')
    pred, sd = T['pred_c10'].values, T['sd_c10'].values
    y = T['ddG_fold'].values.astype(np.float32)
    err = np.abs(y - pred)
    perm = np.random.default_rng(SEED).permutation(len(T))
    cal, val = perm[:len(T) // 2], perm[len(T) // 2:]

    # ---- reproduce the global calibration, or stop -------------------------
    q_global = conformal_q(err[cal], sd[cal], 0.10)
    covered = np.abs(y[val] - pred[val]) <= q_global * (sd[val] + EPS)
    cov_global = float(covered.mean())
    assert abs(q_global - PUBLISHED_Q90) < 5e-3, (
        f'global q90 is {q_global:.4f}, published {PUBLISHED_Q90}. This is B3\'s own '
        'procedure on B3\'s own file, so a mismatch means the inputs changed.')
    assert abs(cov_global - PUBLISHED_COVERAGE) < 2e-3, (
        f'global coverage is {cov_global:.4f}, published {PUBLISHED_COVERAGE}')

    # ---- per-domain calibration -------------------------------------------
    Tc, Tv = T.iloc[cal].assign(_e=err[cal], _s=sd[cal]), T.iloc[val].copy()
    Tv['_e'], Tv['_s'] = err[val], sd[val]
    rows = []
    for gene, c in Tc.groupby('gene'):
        v = Tv[Tv['gene'] == gene]
        if len(c) < MIN_CAL or len(v) == 0:
            rows.append({'gene': gene, 'n_cal': len(c), 'n_val': len(v),
                         'q90': np.nan, 'coverage_global': np.nan,
                         'coverage_mondrian': np.nan, 'estimable': False})
            continue
        q = conformal_q(c['_e'].values, c['_s'].values, 0.10)
        rows.append({
            'gene': gene, 'n_cal': int(len(c)), 'n_val': int(len(v)),
            'q90': q,
            'coverage_global': float((v['_e'] <= q_global * (v['_s'] + EPS)).mean()),
            'coverage_mondrian': float((v['_e'] <= q * (v['_s'] + EPS)).mean()),
            'median_halfwidth_global': float(np.median(q_global * (v['_s'] + EPS))),
            'median_halfwidth_mondrian': float(np.median(q * (v['_s'] + EPS))),
            'estimable': True})
    per = pd.DataFrame(rows).sort_values('coverage_global')
    per.to_csv(out / 'per_domain_q90_G2.csv', index=False)

    est = per[per['estimable']]
    # Does the global interval under- or over-cover in a way the normaliser missed?
    spread_global = float(est['coverage_global'].max() - est['coverage_global'].min())
    spread_mondrian = float(est['coverage_mondrian'].max() - est['coverage_mondrian'].min())

    # ---- what it does to the atlas ----------------------------------------
    A = pd.read_parquet(F / 'atlas_fold_predictions.parquet')
    hw = lambda q: q * (A['sd_fold'].values + EPS)
    calls = lambda q: int(((A['pred_ddG_fold'].values - hw(q)) >= 1.0).sum())

    n_global = calls(q_global)
    assert n_global == PUBLISHED_CALLS, (
        f'{n_global} confident calls under the global q90, published '
        f'{PUBLISHED_CALLS}; the atlas file or the rule has changed')

    # Where a domain was calibrated, use its own q90; elsewhere the global one.
    qmap = dict(zip(est['gene'], est['q90']))
    q_row = A['gene'].map(qmap).fillna(q_global).values
    lo_hybrid = A['pred_ddG_fold'].values - q_row * (A['sd_fold'].values + EPS)
    n_hybrid = int((lo_hybrid >= 1.0).sum())
    in_cal = A['gene'].isin(qmap).values

    # What would the count be if the 310 atlas domains varied as the 15 held-out
    # ones do?  The min/max bracket above puts every domain at one extreme at once,
    # which cannot happen.  Resampling a q90 per domain from the observed 15 gives
    # the spread that is actually implied -- an uncertainty band on 410 that the
    # single global quantile hides rather than removes.
    rng = np.random.default_rng(SEED)
    qs = est['q90'].to_numpy()
    keys = A['domain_key'].to_numpy()
    uniq, inv = np.unique(keys, return_inverse=True)
    pred_a, sd_a = A['pred_ddG_fold'].to_numpy(), A['sd_fold'].to_numpy()
    counts = np.empty(2000, dtype=int)
    for i in range(counts.size):
        qd = rng.choice(qs, size=len(uniq), replace=True)[inv]
        counts[i] = int(((pred_a - qd * (sd_a + EPS)) >= 1.0).sum())

    m = {
        'global': {'q90': q_global, 'coverage': cov_global,
                   'confident_calls': n_global},
        'per_domain': {
            'n_domains': int(len(est)),
            'q90_min': float(est['q90'].min()), 'q90_max': float(est['q90'].max()),
            'q90_median': float(est['q90'].median()),
            'q90_ratio_max_over_min': float(est['q90'].max() / est['q90'].min()),
            'coverage_spread_under_global': spread_global,
            'coverage_spread_under_mondrian': spread_mondrian,
            'worst_gene_under_global': str(est.iloc[0]['gene']),
            'worst_coverage_under_global': float(est.iloc[0]['coverage_global']),
        },
        'atlas': {
            'total_variants': int(len(A)),
            'confident_calls_global': n_global,
            'confident_calls_hybrid': n_hybrid,
            'variants_in_a_calibrated_gene': int(in_cal.sum()),
            'calls_if_every_domain_used_min_q90': calls(float(est['q90'].min())),
            'calls_if_every_domain_used_max_q90': calls(float(est['q90'].max())),
            'calls_if_every_domain_used_median_q90': calls(float(est['q90'].median())),
            'resampled_domain_q90': {
                'draws': int(counts.size),
                'median': int(np.median(counts)),
                'ci95': [int(np.percentile(counts, 2.5)),
                         int(np.percentile(counts, 97.5))],
                'sd': float(counts.std(ddof=1)),
                'note': ('each of the 310 atlas domains given a q90 drawn from the '
                         '15 observed per-domain values; the band the global '
                         'quantile hides'),
            },
        },
    }
    (out / 'metrics_G2.json').write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))
    print('\nper-domain calibration:')
    print(per[['gene', 'n_cal', 'n_val', 'q90', 'coverage_global',
               'coverage_mondrian']].round(4).to_string(index=False))


if __name__ == '__main__':
    main()
