#!/usr/bin/env python3
"""
G1 step 3 — compare the two spectra.

`docs/preregistration/G1.md` Part 9.1 names this the deliverable: not either
notebook's verdict on its own, but **whether the conclusion depends on which
mutation spectrum is assumed**.

Part 9.4 fixes how that judgement is made, and this script implements it so it
cannot drift:

  1. fit          cosine similarity of each assumed spectrum to the observed
                  96-channel distribution
  2. robustness   do the two notebooks agree on the verdict?
  3. support      how many channels carry the observed spectrum

and the rule that matters: **never by which p-value is smaller.** The script
prints no ranking by p, and says so where a reader might expect one.

It also checks the two things that would invalidate the comparison outright: that
both notebooks ran the same `g1_core.py`, and that both reproduced B6's control.
"""
import argparse
import json
from pathlib import Path

OUTCOME = {
    'survives': 'the depletion is not explained by mutational context',
    'shrinks_but_survives': 'context explains part of it — a weakened claim',
    'vanishes': 'consistent with mutational bias alone',
}


def load(path: Path) -> dict:
    assert path.exists(), f'{path} not found — run the notebook first'
    return json.loads(path.read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True, help='results/G1_mutational_context')
    ap.add_argument('--out', help='where to write RESULTS_G1_comparison.md')
    a = ap.parse_args()
    d = Path(a.results)

    A, B = load(d / 'metrics_G1a.json'), load(d / 'metrics_G1b.json')
    L = []

    def say(*s):
        for x in (s or ('',)):
            print(x)
            L.append(x)

    # ── the two checks that decide whether any comparison is valid ────────────
    assert A['g1_core_sha256'] == B['g1_core_sha256'], (
        f"the notebooks ran different g1_core.py "
        f"({A['g1_core_sha256'][:12]} vs {B['g1_core_sha256'][:12]}); any difference "
        'between their results could be the code rather than the spectrum, so this '
        'comparison is not valid')
    assert A['control_3a']['null_median'] == B['control_3a']['null_median'], (
        'the uniform control differs between the notebooks, so the shared machinery '
        'is not in fact shared')
    assert A['counts'] == B['counts'], 'the two notebooks used different eligible sets'

    say('# G1 — does the conclusion depend on the spectrum?', '',
        'Machine-written by `tools/g1_compare.py`. Judged by the rules in '
        '`docs/preregistration/G1.md` Part 9.4, fixed before either notebook ran.', '')

    say(f"Both notebooks ran `g1_core.py` `{A['g1_core_sha256'][:16]}…`, the same "
        f"{A['counts']['observed_eligible']:,} eligible variants, and the same seed. "
        'The uniform control is identical in both, which is how that is known rather '
        'than assumed.', '')

    # ── where the null rate comes from ───────────────────────────────────────
    b6 = A['b6_published_null']
    a3a, a3b = A['control_3a'], A['control_3b']
    say('## Where the null rate comes from', '',
        '| step | null rate | change |', '|---|---|---|',
        f"| B6, published | {b6:.4f} | — |",
        f"| 3a uniform over substitutions | {a3a['null_median']:.4f} | "
        f"{(a3a['null_median']-b6)*100:+.2f} pp vs B6 |",
        f"| 3b uniform over base changes | {a3b['null_median']:.4f} | "
        f"{(a3b['null_median']-a3a['null_median'])*100:+.2f} pp — reachability multiplicity |",
        f"| **1 observed spectrum** | **{A['main']['null_median']:.4f}** | "
        f"{(A['main']['null_median']-a3b['null_median'])*100:+.2f} pp — context |",
        f"| **2 COSMIC SBS1+SBS5** | **{B['main']['null_median']:.4f}** | "
        f"{(B['main']['null_median']-a3b['null_median'])*100:+.2f} pp — context |", '')

    # ── the result ───────────────────────────────────────────────────────────
    say('## The result under each spectrum', '',
        '| | observed | null median | gap (pp) | p | α | verdict |',
        '|---|---|---|---|---|---|---|')
    for lab, m in (('observed spectrum', A), ('COSMIC SBS1+SBS5', B)):
        k, role = m['main'], '' if m['is_primary'] else ' *(sensitivity)*'
        say(f"| **{lab}**{role} | {k['observed_rate']:.4f} | {k['null_median']:.4f} | "
            f"{k['gap_pp']:+.2f} | {k['p_one_sided_depleted']:.5f} | {m['alpha']} | "
            f"**{m['verdict']}** |")
    say('')

    agree = A['verdict'] == B['verdict']
    if agree:
        say(f"**The two spectra agree: {A['verdict']}** — "
            f"{OUTCOME.get(A['verdict'], '')}.", '',
            'Agreement is what Part 9.4 calls robustness, and it is the outcome that '
            "settles the awkward part of this design: the observed spectrum's "
            'dependence on the test set stops mattering when an externally fixed '
            'spectrum reaches the same verdict.', '')
    else:
        say(f"**The two spectra disagree — observed: {A['verdict']}, "
            f"COSMIC: {B['verdict']}.**", '',
            'Part 9.4: disagreement *is* the finding and is reported as such. Neither '
            'arm is promoted. The conclusion is spectrum-dependent, and the honest '
            'claim is that these data cannot separate selection from mutational bias '
            'without settling which spectrum describes this atlas.', '')

    # ── fit, which is the other half of Part 9.4 ─────────────────────────────
    fit = B['cosine_fit_to_observed']
    obs_spec = A['observed_spectrum']
    supported = sum(1 for v in obs_spec.values() if v > 0)
    say('## Fit and support', '',
        f"COSMIC SBS1+SBS5 reaches **cosine {fit:.4f}** against the observed "
        '96-channel distribution. The observed spectrum reaches 1.0 by construction, '
        'so that number is not a contest — what matters is how far COSMIC is from it, '
        'because a close fit means the non-independence of the observed spectrum is '
        'buying very little.', '',
        f"The observed spectrum rests on **{supported} of 96 channels**. Channels with "
        'little support make it noisy, and that weakens the observed arm specifically.', '')

    say('## What this comparison does not do', '',
        'It does not rank the two spectra by p-value, and no such ranking appears '
        'above. Part 9.4 fixed that before any number existed, because whichever '
        'spectrum gave the smaller p would otherwise have an argument waiting for it.',
        '')

    excl = A['exclusion_check']
    if excl.get('rate_excluded') is not None:
        say('## The excluded variants', '',
            f"{excl['n_included']:,} included at {excl['rate_included']:.4f} "
            f"destabilising; {excl['n_excluded']:,} excluded at "
            f"{excl['rate_excluded']:.4f}. Part 6 required this whether or not it "
            'changes anything, so that the choice to report it was not made after '
            'seeing it.', '')

    if a.out:
        Path(a.out).write_text('\n'.join(L) + '\n')
        print(f'\nwrote {a.out}')


if __name__ == '__main__':
    main()
