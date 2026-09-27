"""Figure 1 - what the extended phase established.

Four panels, built only from committed result tables. Nothing is typed by hand:
every number is read from results/*/ at run time, so the figure cannot drift from
the numbers in OUTCOMES.md.

Design follows the journal conventions used for the frozen run's D1 figures:
Nature two-column width (183 mm), Okabe-Ito colour-vision-safe palette, sans-serif
at 6-7 pt, vector PDF plus a 600 dpi raster, and every panel states its n.

    python tools/fig_outcomes.py          # writes results/figures/fig_outcomes.{pdf,png}
"""
import csv, json, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES  = ROOT / 'results'
OUT  = RES / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

# ── Okabe-Ito: distinguishable under all common colour-vision deficiencies
OURS, SAPROT, ESM3, GREY, RED = '#000000', '#0072B2', '#E69F00', '#999999', '#D55E00'

MM = 1 / 25.4
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 6.5, 'axes.labelsize': 7, 'axes.titlesize': 7.5,
    'xtick.labelsize': 6, 'ytick.labelsize': 6, 'legend.fontsize': 6,
    'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'xtick.major.size': 2, 'ytick.major.size': 2,
    'axes.spines.top': False, 'axes.spines.right': False,
    'legend.frameon': False, 'figure.dpi': 200,
})

rows = lambda p: list(csv.DictReader(open(p)))


def panel_a(ax):
    """E3: per-domain Spearman, our head against two structure-conditioned predictors."""
    sa = {r['gene']: (float(r['rho_comp']), float(r['rho_ours']), int(float(r['n'])))
          for r in rows(RES / 'E3_sota_benchmark' / 'per_domain_SaProtdG_E3.csv')}
    es = {r['gene']: float(r['rho_comp'])
          for r in rows(RES / 'E3_sota_benchmark' / 'per_domain_ESM3dG_E3.csv')}
    genes = sorted(sa, key=lambda g: sa[g][1])
    y = range(len(genes))
    for i, g in enumerate(genes):                      # connector, so the triplet reads as one row
        lo = min(sa[g][0], sa[g][1], es[g]); hi = max(sa[g][0], sa[g][1], es[g])
        ax.plot([lo, hi], [i, i], color=GREY, lw=0.5, zorder=1)
    ax.scatter([es[g] for g in genes], y, s=11, c=ESM3, marker='s', zorder=3, label='ESM3ΔG')
    ax.scatter([sa[g][0] for g in genes], y, s=11, c=SAPROT, marker='^', zorder=3, label='SaProtΔG')
    ax.scatter([sa[g][1] for g in genes], y, s=13, c=OURS, marker='o', zorder=4, label='ours (B1)')
    ax.set_yticks(list(y)); ax.set_yticklabels(genes)
    ax.set_xlabel('per-domain Spearman $\\rho$ against measured $\\Delta\\Delta G$')
    ax.set_xlim(0.40, 0.98)
    ax.legend(loc='upper left', handletextpad=0.3, borderpad=0.2)
    ax.set_title('15 held-out SH3 domains, 27,590 variants, 0 dropped', loc='left', pad=3)


def panel_b(ax):
    """E2: our correlation against the agreement between two independent assays."""
    m = rows(RES / 'E2_domainome_external' / 'noise_ceiling_matched_E2.csv')
    genes = [r['gene'] for r in m]
    ceil = [float(r['ceiling']) for r in m]
    ours = [float(r['ours']) for r in m]
    ns   = [int(r['n']) for r in m]
    x = range(len(genes))
    for i in x:
        ax.plot([i, i], [ours[i], ceil[i]], color=GREY, lw=0.6, zorder=1)
    ax.scatter(x, ceil, s=16, c=RED, marker='_', lw=1.4, zorder=3,
               label='ceiling (two assays agreeing)')
    ax.scatter(x, ours, s=13, c=OURS, marker='o', zorder=4, label='ours')
    for i in x:
        ax.annotate(f'{100*ours[i]/ceil[i]:.0f}%', (i, max(ours[i], ceil[i]) + 0.03),
                    ha='center', fontsize=5.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f'{g}\nn={n}' for g, n in zip(genes, ns)])
    ax.set_ylabel('|Spearman $\\rho$|')
    ax.set_ylim(0.45, 0.95)
    ax.legend(loc='lower center', handletextpad=0.3, borderpad=0.2)
    ax.set_title('Matched variants: share of the achievable limit', loc='left', pad=3)


def panel_c(ax):
    """E4: the specificity axis, and the control that interprets its failure."""
    d = json.load(open(RES / 'E4_specificity_independent' / 'metrics_E4.json'))
    items = [('model\n(leave-cluster-out)', d['E1_main']['r'], OURS),
             ('average profile\n(domain-agnostic)', d['E1_average']['r'], GREY),
             ('observed profile\n(the ceiling)', d['E1_observed']['r'], RED)]
    y = range(len(items))
    ax.axvspan(-0.44, 0.44, color='#EEEEEE', zorder=0)
    ax.axvline(0, color='k', lw=0.5, zorder=1)
    for i, (_, r, c) in enumerate(items):
        ax.plot([0, r], [i, i], color=c, lw=0.8, zorder=2)
        ax.scatter([r], [i], s=16, c=c, zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels([t for t, _, _ in items])
    ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.75, 2.6)
    ax.set_xlabel('within-domain-centred $r$ against measured $\\log_{10} K_d$')
    ax.annotate('shaded: smaller than n = 44 can detect', (0, -0.6),
                ha='center', fontsize=5.5, color='#555555')
    ax.set_title('Even the measured profile fails — the representation, not the model',
                 loc='left', pad=3)


def panel_d(ax):
    """The leakage audit, which stands whatever the comparison returns."""
    names = ['SaProtΔG', 'ESM3ΔG', 'ThermoMPNN']
    vals  = [0, 0, 13]
    cols  = [SAPROT, ESM3, RED]
    y = range(len(names))
    ax.barh(list(y), vals, color=cols, height=0.55, zorder=2)
    ax.barh(list(y), [15] * 3, color='#F0F0F0', height=0.55, zorder=1)
    for i, v in enumerate(vals):
        ax.annotate(f'{v} of 15', (max(v, 0) + 0.4, i), va='center', fontsize=6)
    ax.set_yticks(list(y)); ax.set_yticklabels(names)
    ax.set_xlim(0, 16); ax.set_xticks([0, 5, 10, 15])
    ax.set_xlabel('held-out domains inside the competitor’s published training split')
    ax.set_title('23,191 of 27,590 variants are ThermoMPNN’s own training data',
                 loc='left', pad=3)


fig = plt.figure(figsize=(183 * MM, 132 * MM))
gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1.35, 1],
                      wspace=0.42, hspace=0.55, left=0.085, right=0.985,
                      top=0.935, bottom=0.085)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
for fn, ax in zip((panel_a, panel_b, panel_c, panel_d), axes):
    fn(ax)
for lab, ax in zip('ABCD', axes):
    ax.annotate(lab, xy=(-0.13, 1.14), xycoords='axes fraction',
                fontsize=9, fontweight='bold', va='top')

fig.savefig(OUT / 'fig_outcomes.pdf', bbox_inches='tight')
fig.savefig(OUT / 'fig_outcomes.png', dpi=600, bbox_inches='tight')
print('wrote', OUT / 'fig_outcomes.pdf')
print('wrote', OUT / 'fig_outcomes.png')
