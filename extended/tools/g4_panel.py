#!/usr/bin/env python3
"""
G4 — rebuild the F1 experimental panel so that it tests the model rather than the
genetic code.

F1 selected `stable_pool.head(10)` sorted by confidence, with no diversity
constraint of any kind.  Confidence is highest exactly where the prediction is
easiest, so the panel collapsed onto one structural position and one substitution
class:

    5 of 10 picks at domain position 8, ALL of them alanine
    A98D  A851P  A297D  A547P  A1600P
    4 of 10 to proline, 4 of 10 to aspartate

Five assays would have measured one substitution.  "Proline in a beta-barrel core
destabilises" is not a finding, and neither is "aspartate in a hydrophobic core".

Two changes, both about what the experiment can distinguish:

1.  **Diversity constraints.** One pick per aligned position (GRB2 reference frame),
    one gene, one proline, and a cap on any single mutant residue.  A panel that
    repeats a position cannot separate "the model is right" from "the model has
    learned one rule".

2.  **Exposed picks, and buried controls.** F1's picks were 8/10 buried and its
    controls sat at termini and exposed loops, so the positive and negative sets
    differed in burial as much as in predicted effect -- a confound, not a control.
    A destabilising call at an EXPOSED position is the one that can actually fail,
    so the panel reserves places for them; and a tolerated call at a BURIED position
    is the informative negative, so controls prefer burial.

Nothing about the model or the threshold changes.  `fold_lo >= 1` is still the call,
the predictions are the frozen ones, and no number is re-fitted.  This is a
selection, not an analysis, and it carries no verdict.

    python3 tools/g4_panel.py --root .. --out results/G4_panel
"""
import argparse
import json
from pathlib import Path

import pandas as pd

N_PANEL = 10
MAX_PROLINE = 1          # "to proline" is one hypothesis, not four
MAX_PER_MUT_AA = 2       # no single destination residue dominates
MIN_EXPOSED = 3          # the picks that can actually falsify the model
CONTROL_ABS_DDG = 0.3


def pick_diverse(pool: pd.DataFrame, n: int, *, min_exposed: int) -> pd.DataFrame:
    """Greedy by confidence, subject to the diversity constraints.

    Two passes.  The first fills the exposed quota from the most confident exposed
    candidates, because exposed destabilising calls are scarce and would never
    survive a pure confidence ranking.  The second fills the rest.
    """
    chosen, used_pos, used_gene, n_pro = [], set(), set(), 0
    mut_counts: dict[str, int] = {}

    def admits(r) -> bool:
        nonlocal n_pro
        if r.ref_pos in used_pos or r.gene in used_gene:
            return False
        if r.mut_aa == 'P' and n_pro >= MAX_PROLINE:
            return False
        if mut_counts.get(r.mut_aa, 0) >= MAX_PER_MUT_AA:
            return False
        return True

    def take(r):
        nonlocal n_pro
        chosen.append(r)
        used_pos.add(r.ref_pos)
        used_gene.add(r.gene)
        mut_counts[r.mut_aa] = mut_counts.get(r.mut_aa, 0) + 1
        if r.mut_aa == 'P':
            n_pro += 1

    ordered = pool.sort_values('fold_lo', ascending=False)
    exposed = ~ordered['buried'].fillna(True).astype(bool)
    for r in ordered[exposed].itertuples():
        if len(chosen) >= min_exposed:
            break
        if admits(r):
            take(r)
    for r in ordered.itertuples():
        if len(chosen) >= n:
            break
        if admits(r):
            take(r)
    return pd.DataFrame(chosen).drop(columns=['Index'], errors='ignore')


def pick_controls(pool: pd.DataFrame, picks: pd.DataFrame, n: int) -> pd.DataFrame:
    """One tolerated variant per picked domain, preferring buried positions.

    A tolerated variant at an exposed terminus is a weak negative: nothing predicted
    it would break.  A tolerated variant in the core, in the same domain as a pick,
    is the control that carries information -- it says the model is discriminating
    within a context, not just reporting burial.
    """
    c = pool[pool['domain_key'].isin(picks['domain_key'])].copy()
    c['buried_first'] = (~c['buried'].fillna(False).astype(bool)).astype(int)
    c = (c.sort_values(['buried_first', 'fold_halfwidth'])
           .drop_duplicates('domain_key'))
    if len(c) < n:      # top up from any domain if a picked domain has no control
        rest = pool[~pool['domain_key'].isin(c['domain_key'])].copy()
        rest['buried_first'] = (~rest['buried'].fillna(False).astype(bool)).astype(int)
        rest = rest.sort_values(['buried_first', 'fold_halfwidth'])
        c = pd.concat([c, rest.drop_duplicates('domain_key')])
    return c.head(n)


def describe(df: pd.DataFrame, label: str) -> dict:
    return {
        'panel': label, 'n': int(len(df)),
        'distinct_aligned_positions': int(df['ref_pos'].nunique(dropna=True)),
        'distinct_genes': int(df['gene'].nunique()),
        'distinct_mut_aa': int(df['mut_aa'].nunique()),
        'to_proline': int((df['mut_aa'] == 'P').sum()),
        'buried': int(df['buried'].fillna(False).astype(bool).sum()),
        'exposed': int((~df['buried'].fillna(True).astype(bool)).sum()),
        'max_at_one_position': int(df['ref_pos'].value_counts().max())
        if df['ref_pos'].notna().any() else 0,
        'max_one_mut_aa': int(df['mut_aa'].value_counts().max()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    A = pd.read_parquet(root / 'input/frozen/results/atlas_predictions.parquet')
    master = pd.read_csv(root / 'input/frozen/results/SH3_cancer_master.tsv',
                         sep='\t', usecols=['variant_id', 'n_samples_nonhyper',
                                            'top_primary_sites'])
    A = A.merge(master.drop_duplicates('variant_id'), on='variant_id', how='left')
    A['nonhyper'] = pd.to_numeric(A['n_samples_nonhyper'],
                                  errors='coerce').fillna(0) > 0
    assert len(A) == 6884, f'atlas has {len(A)} rows, expected 6,884'

    pool = A[(A['fold_lo'] >= 1.0) & A['nonhyper']]
    picks = pick_diverse(pool, N_PANEL, min_exposed=MIN_EXPOSED)
    ctrl_pool = A[(A['fold_lo'] < 1.0) & (A['pred_ddG_fold'].abs() < CONTROL_ABS_DDG)]
    ctrls = pick_controls(ctrl_pool, picks, N_PANEL)

    assert picks['ref_pos'].dropna().is_unique, 'two picks share an aligned position'
    assert int((picks['mut_aa'] == 'P').sum()) <= MAX_PROLINE, 'too many prolines'
    assert picks['gene'].is_unique, 'two picks from one gene'

    cols = ['variant_id', 'gene', 'domain_key', 'pos', 'wt_aa', 'mut_aa', 'ref_pos',
            'rsasa', 'buried', 'pred_ddG_fold', 'fold_lo', 'fold_halfwidth',
            'nonhyper', 'top_primary_sites']
    picks[cols].to_csv(out / 'panel_destabilising_G4.csv', index=False)
    ctrls[cols].to_csv(out / 'panel_control_G4.csv', index=False)

    m = {'destabilising': describe(picks, 'destabilising'),
         'control': describe(ctrls, 'control'),
         'pool_sizes': {'destabilising_nonhyper': int(len(pool)),
                        'aligned_positions_available': int(pool['ref_pos'].nunique()),
                        'control': int(len(ctrl_pool))},
         'constraints': {'max_proline': MAX_PROLINE,
                         'max_per_mut_aa': MAX_PER_MUT_AA,
                         'min_exposed': MIN_EXPOSED,
                         'one_per_aligned_position': True,
                         'one_per_gene': True},
         'controls_in_picked_domains': int(
             ctrls['domain_key'].isin(picks['domain_key']).sum())}
    (out / 'metrics_G4.json').write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))
    print('\ndestabilising picks:')
    print(picks[['gene', 'variant_id', 'ref_pos', 'wt_aa', 'mut_aa', 'buried',
                 'pred_ddG_fold', 'fold_lo']].to_string(index=False))
    print('\ncontrols:')
    print(ctrls[['gene', 'variant_id', 'ref_pos', 'wt_aa', 'mut_aa', 'buried',
                 'pred_ddG_fold', 'fold_halfwidth']].to_string(index=False))


if __name__ == '__main__':
    main()
