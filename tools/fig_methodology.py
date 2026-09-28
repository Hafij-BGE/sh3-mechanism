#!/usr/bin/env python3
"""
The methodology figure for docs/METHODOLOGY.md.

One diagram of the whole pipeline, with each program coloured by what it produced
rather than by what it is -- the point is that a reader sees at a glance which claims
held, which were withdrawn and which are still open.

Okabe-Ito throughout, so it survives colour-vision deficiency and greyscale, and
nothing is encoded by colour alone: every box carries its outcome in words.

Layout note: rows are placed on an explicit grid with a checked gap between them,
and box height is derived from the number of text lines rather than guessed. The
first version of this figure guessed, and every box overlapped the one below it.

    python3 tools/fig_methodology.py
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK, LIGHT = '#000000', '#F2F2F2'
BLUE, GREEN, ORANGE, RED, GREY = '#0072B2', '#009E73', '#E69F00', '#D55E00', '#8C8C8C'

FIG_H = 12.0
TITLE_PT, BODY_PT = 7.4, 6.3
LINE = BODY_PT * 1.5 / 72 / FIG_H        # one body line, in axes fraction
PAD_TOP, PAD_BOT = 0.014, 0.008

plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.dpi': 200})


def height(n_lines):
    """Box height that actually fits a title plus n body lines."""
    return PAD_TOP + TITLE_PT * 1.6 / 72 / FIG_H + n_lines * LINE + PAD_BOT


def box(ax, x, y, w, title, lines, edge, fill='white'):
    h = height(len(lines))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.006,rounding_size=0.012',
                                linewidth=1.3, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h - PAD_TOP, title, ha='center', va='top',
            fontsize=TITLE_PT, fontweight='bold', color=INK, zorder=3)
    ax.text(x + w / 2, y + h - PAD_TOP - TITLE_PT * 1.6 / 72 / FIG_H,
            '\n'.join(lines), ha='center', va='top', fontsize=BODY_PT,
            color=INK, linespacing=1.5, zorder=3)
    return h


def band(ax, y0, y1, label, sub):
    ax.add_patch(plt.Rectangle((0.004, y0), 0.992, y1 - y0, facecolor=LIGHT,
                               edgecolor='none', zorder=0))
    ax.text(0.016, y1 - 0.011, label, ha='left', va='top', fontsize=8.6,
            fontweight='bold', color=INK, zorder=3)
    ax.text(0.016, y1 - 0.030, sub, ha='left', va='top', fontsize=6.2,
            color='#555555', style='italic', zorder=3)


def bar(ax, y, text, colour):
    ax.text(0.5, y, text, ha='center', va='center', fontsize=6.9, fontweight='bold',
            color=colour, zorder=4,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=colour, linewidth=1.2))


def arrow(ax, p, q, lw=1.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=9,
                                 linewidth=lw, color=INK, zorder=1,
                                 shrinkA=2, shrinkB=2))


def main():
    fig, ax = plt.subplots(figsize=(7.5, FIG_H))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    X = [0.030, 0.352, 0.674]          # three columns
    W = 0.296

    # ── legend, above everything ─────────────────────────────────────────────
    for i, (c, t) in enumerate([(BLUE, 'infrastructure / audit'), (GREEN, 'claim holds'),
                                (ORANGE, 'holds, qualified'), (RED, 'withdrawn / failed'),
                                (GREY, 'provisional / open')]):
        x = 0.030 + i * 0.195
        ax.add_patch(plt.Rectangle((x, 0.9805), 0.016, 0.010, facecolor='white',
                                   edgecolor=c, linewidth=1.5))
        ax.text(x + 0.022, 0.9855, t, ha='left', va='center', fontsize=6.2, color=INK)

    # ── PHASE 1 ──────────────────────────────────────────────────────────────
    band(ax, 0.742, 0.968, 'PHASE 1 · build, then freeze',
         'the whole SH3 family held out — not random variants, because two variants in one domain are not independent')

    r1 = 0.845
    box(ax, X[0], r1, W, 'MegaScale', ['389,068 substitutions', '412 domains, 32–72 aa',
                                       'ΔΔG by proteolysis'], BLUE)
    box(ax, X[1], r1, W, 'Features · 1,292', ['1,280 ESM-2 650M dims', '+ 12 scalars',
                                              'structure excluded by design'], BLUE)
    box(ax, X[2], r1, W, 'Head · 1292→512→128→1', ['frozen encoder, small head',
                                                   'grouped on accession',
                                                   'SH3 family held out'], BLUE)
    r2 = 0.760
    box(ax, X[0], r2, W, 'Conformal calibration', ['q90 = 6.807', 'coverage 89.9 % vs 90 %',
                                                   'fold_lo ≥ 1 = confident'], GREEN)
    box(ax, X[1], r2, W, 'Held-out accuracy', ['median ρ = 0.839', '15 SH3 domains',
                                               'beats zero-shot ESM-2 15/15'], GREEN)
    box(ax, X[2], r2, W, 'Applied to the atlas', ['6,884 cancer variants',
                                                  '310 domains, 235 genes',
                                                  '410 confident calls (6.0 %)'], GREEN)
    for i in range(2):
        arrow(ax, (X[i] + W, r1 + 0.030), (X[i + 1], r1 + 0.030))
    for i in range(3):
        arrow(ax, (X[i] + W / 2, r1), (X[i] + W / 2, r2 + height(3)))

    bar(ax, 0.727, 'FROZEN  ·  input/frozen/ is chmod a-w  ·  everything below re-derives '
                   'and asserts first  ·  187/187 values reproduce', INK)

    # ── PHASE 2 ──────────────────────────────────────────────────────────────
    band(ax, 0.292, 0.712, 'PHASE 2 · test it against the outside world',
         'four independent external sources — and a re-test of the project’s own claims')

    r3 = 0.598
    box(ax, X[0], r3, W, 'X0 · acquire once', ['ClinVar, gnomAD, Domainome',
                                               'assert row count unchanged',
                                               '→ caught 3 join defects'], BLUE)
    box(ax, X[1], r3, W, 'X1 · dbNSFP', ['2.1 M rows → 152,852',
                                         'coverage vs publisher’s own',
                                         '→ caught mislabelled columns'], BLUE)
    box(ax, X[2], r3, W, 'Pre-registration', ['rule committed to git',
                                              'BEFORE the code existed',
                                              'threshold, min n, reading'], BLUE)
    r4 = 0.500
    box(ax, X[0], r4, W, 'E2 · measured', ['Domainome, 880 variants',
                                           '41 domains, 32 genes',
                                           '|ρ| 0.600 = 85 % of the',
                                           '0.709 two-assay ceiling'], GREEN)
    box(ax, X[1], r4, W, 'E3 · benchmark', ['ThermoMPNN disqualified:',
                                            '13/15 domains in its training',
                                            'SaProtΔG 0.855 vs 0.839 (ns)',
                                            'ESM3ΔG 0.792, p = 0.0084'], GREEN)
    box(ax, X[2], r4, W, 'E1 · clinical', ['ClinVar 21 vs 101',
                                           '1.67 vs 0.19 kcal/mol',
                                           'p = 4.9 × 10⁻⁶',
                                           'but sensitivity only 4.8 %'], ORANGE)
    r5 = 0.402
    box(ax, X[0], r5, W, 'E4 · specificity', ['model r = +0.023 (p 0.91)',
                                              'CONTROL: observed profile',
                                              'r = −0.051 — a predictor',
                                              'of X cannot beat X'], RED)
    box(ax, X[1], r5, W, 'G1 · context-aware null', ['6,456 coords, 100 % verified',
                                                     '0.0923 → 0.0860 → 0.0788',
                                                     '→ 0.0604 vs observed 0.0596',
                                                     'p = 0.40, two spectra agree'], RED)
    box(ax, X[2], r5, W, 'G2 · per-domain intervals', ['coverage 83.3 % – 95.0 %',
                                                       'quantile varies 1.79×',
                                                       'count robust: 410 (378–421)',
                                                       'per-variant claim is not'], ORANGE)
    r6 = 0.316
    box(ax, 0.191, r6, W, 'G3 · scoped, then dropped', ['would recover 72, not 219',
                                                        'changes NO prediction',
                                                        '→ kept as a limitation'], GREY)
    box(ax, 0.513, r6, W, 'G4 · rebuild the panel', ['5/10 picks at one position',
                                                     'controls differed by burial',
                                                     '→ 10 positions, 3 exposed'], GREEN)

    bar(ax, 0.278, 'OUTCOME  ·  three objections closed  ·  one claim WITHDRAWN — '
                   'the cancer depletion was mutational bias, not selection', RED)

    # ── PHASE 3 ──────────────────────────────────────────────────────────────
    band(ax, 0.036, 0.262, 'PHASE 3 · does any of it generalise?',
         'provisional — not in the manuscript')

    r7 = 0.143
    box(ax, X[0], r7, W, 'H1.0 · leakage audit', ['every other family WAS',
                                                  'in training; PDZ absent only',
                                                  'because it exceeds 72 aa'], BLUE)
    box(ax, X[1], r7, W, 'H1.1 · power first', ['15 domains → CI width 0.243',
                                                'wider than the margin itself',
                                                '→ pooled to 35, width 0.148'], BLUE)
    box(ax, X[2], r7, W, 'H1.2 · evaluation', ['PDZ 0.602 vs SH3 0.623',
                                               'three families 0.420',
                                               'main arm INCONCLUSIVE'], GREY)
    r8 = 0.060
    box(ax, 0.191, r8, W, 'H1.3 · assay quality', ['matched: −0.203 → −0.187',
                                                   'Myb/SANT: better data,',
                                                   'lower accuracy'], GREY)
    box(ax, 0.513, r8, W, 'H2 · bench', ['20 constructs ready (G4)',
                                         'DSF, then CD on discordant',
                                         'NOT STARTED'], GREY, fill=LIGHT)

    arrow(ax, (0.5, 0.292), (0.5, 0.262), lw=1.2)

    ax.text(0.5, 0.020,
            'Length is NOT the limit — PDZ is 88 aa against a 72 aa training ceiling and still matches SH3.\n'
            'Measurement quality is not the limit either. What is, is not yet named.',
            ha='center', va='center', fontsize=6.6, color=INK, style='italic',
            linespacing=1.6)

    out = Path(__file__).resolve().parent.parent / 'docs' / 'figures'
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / 'methodology.png', bbox_inches='tight', facecolor='white', dpi=300)
    fig.savefig(out / 'methodology.pdf', bbox_inches='tight', facecolor='white')
    print(f'wrote {out}/methodology.png and .pdf')


if __name__ == '__main__':
    main()
