"""Part F — follow-up that reads frozen outputs only. F1 experimental validation candidates (roadmap N1–N3)."""
from nbkit import md, code, setup

# ════════════════════════════════════════════════════════════════════════ F1
F1 = [md(r"""
# F1 — Experimental validation candidates (roadmap N1–N3)

**Question.** Of the 6,884 predicted variants, which should go on a bench first, and with which
assay? And does the project's own mechanism map support a four-group design
(destabilising-only / rewiring-only / both / neither), or only the two-group version?

**What it does.** Nothing new is derived. F1 reads the frozen outputs of B3 (conformal folding
calls), C4 (the independent specificity axis and its pre-registered decision) and A0 (tumour
context), and turns them into a small, ranked, assay-tagged candidate panel. No model is
retrained, no feature is recomputed, and no number reported by A0–D1 changes. F1 runs after D1
and is not part of the reproduction check.

**The one thing it will not do.** B3's `mechanism` column labels some variants "rewiring" or
"both", but that label rests on rank-matched zero-shot ESM-2 (`bind_source == 'esm_rank_matched'`),
which the project does not claim as a binding prediction (C2 `binding_decision.json`;
B5 `binding_claims_made = False`). F1 does **not** use that column. Specificity candidates come
only from C4's independently trained rewiring score, and only if C4's own pre-registered rule
returned `validated: true`. If it did not, the rewiring panel and the four-group design are not
built: the notebook says so and keeps the two-group design the data support.

**Inputs:** `A0/SH3_cancer_master.tsv`, `B3/atlas_predictions.parquet`,
`C4/specificity_decision.json` (+ `C4/atlas_rewiring.parquet` if validated).
**Outputs:** `experimental_candidates.csv` (per-variant, stays on Drive), `panel_summary.csv`,
`RESULTS_F1.md`. **Runtime:** seconds, CPU. Explanation: `docs/F1_experimental_candidates.md`.
"""),
setup('F1', 'Experimental validation candidates'),
md("## 1. Load frozen outputs — nothing here is re-derived\n"
   "`N_PER_PANEL` is the only setting: how many candidates per class a first bench campaign could take on. "
   "It is small on purpose; this is a prioritisation aid, not a discovery list."),
code(r"""
N_PER_PANEL = 10   # candidates per class: a starting bench panel, not an exhaustive list

# the atlas must be the verified one from A0 (same MD5 as the original)
a0 = json.load(open(R.res('A0', 'metrics_A0.json')))['metrics']['master_md5']
got = C.md5(R.res('A0', 'SH3_cancer_master.tsv'))
assert got == a0, f'SH3_cancer_master.tsv changed since A0 ran ({got} vs {a0}). Re-run A0.'
MASTER = pd.read_csv(R.res('A0', 'SH3_cancer_master.tsv'), sep='\t', keep_default_na=False, dtype=str)
A = pd.read_parquet(R.res('B3', 'atlas_predictions.parquet'))
A = A.merge(MASTER[['variant_id', 'n_samples_nonhyper', 'top_primary_sites']].drop_duplicates('variant_id'),
            on='variant_id', how='left')
A['nonhyper'] = pd.to_numeric(A.n_samples_nonhyper, errors='coerce').fillna(0) > 0
A['destab'] = A.fold_lo >= 1.0
A['fold_halfwidth'] = A.pred_ddG_fold - A.fold_lo            # the B3 90% half-width

DEC_C4 = json.load(open(R.res('C4', 'specificity_decision.json')))
HAVE_REWIRING = bool(DEC_C4.get('validated', False))
REWIRE_THRESH = np.nan
if HAVE_REWIRING:
    RW = pd.read_parquet(R.res('C4', 'atlas_rewiring.parquet'))[['variant_id', 'rewiring']]
    A = A.merge(RW, on='variant_id', how='left')
    REWIRE_THRESH = A.rewiring.quantile(0.9)                   # same top-decile convention as C4
    A['high_rewiring'] = A.rewiring >= REWIRE_THRESH
else:
    A['rewiring'] = np.nan; A['high_rewiring'] = False
print(f'{len(A):,} atlas variants | destabilising {int(A.destab.sum())} | C4 validated: {HAVE_REWIRING}')
"""),
md(r"""
## 2. Panel S — stability candidates (roadmap N1)

Destabilising calls ranked by **how far the lower 90 % bound clears 1 kcal/mol** (`fold_lo`,
highest first), with non-hypermutated occurrences first: a variant seen outside hypermutated
tumours is the more defensible one to spend bench time on. The negative controls are confidently
tolerated variants (|predicted ΔΔG| < 0.3 kcal/mol, narrowest interval), taken **from the same
domains as Panel S where possible**, so that each domain is tested with a positive and a negative.
"""),
code(r"""
stable_pool = A[A.destab].sort_values(['nonhyper', 'fold_lo'], ascending=[False, False])
PANEL_S = stable_pool.head(N_PER_PANEL)

control_pool = A[~A.destab & (A.pred_ddG_fold.abs() < 0.3)].sort_values('fold_halfwidth')
same_dom = control_pool[control_pool.domain_key.isin(PANEL_S.domain_key)].drop_duplicates('domain_key')
PANEL_S_CTRL = pd.concat([same_dom, control_pool.drop(same_dom.index)]).head(N_PER_PANEL)
CTRL_MATCHED = int(PANEL_S_CTRL.domain_key.isin(PANEL_S.domain_key).sum())

STABILITY_ASSAYS = ['thermal denaturation (CD or DSF)', 'proteolysis-based stability assay',
                    'cellular abundance assay', 'ddPCA (AbundancePCA) if the domain can be cloned into that system']
print(f'Panel S: {len(PANEL_S)} destabilising | {len(PANEL_S_CTRL)} controls ({CTRL_MATCHED} from the same domains)')
print(PANEL_S[['variant_id', 'gene', 'pred_ddG_fold', 'fold_lo', 'nonhyper']].to_string(index=False))
"""),
md(r"""
## 3. Panel R — specificity (rewiring) candidates (roadmap N2), gated on C4's own rule

Built only if `specificity_decision.json` says `validated: true`. Otherwise this section records
why no panel is produced, instead of falling back to the disclaimed ESM-based label.
"""),
code(r"""
SPECIFICITY_ASSAYS = ['phage display against the peptide library', 'peptide array',
                      'fluorescence polarisation (WT vs mutant against candidate peptides)',
                      'SPR for kinetic confirmation of the top hits',
                      'yeast two-hybrid or a cell-based binding assay']
if HAVE_REWIRING:
    PANEL_R = (A[A.high_rewiring & ~A.destab]
               .sort_values(['nonhyper', 'rewiring'], ascending=[False, False]).head(N_PER_PANEL))
    print(f'Panel R (rewiring, not destabilising): {len(PANEL_R)}')
else:
    PANEL_R = A.iloc[0:0]
    print(f"No specificity panel: C4's pre-registered rule returned validated=False "
          f"(median centred r {DEC_C4.get('median_centred_r', float('nan')):.3f}). A panel built on B3's "
          "rank-matched ESM placeholder would present an unvalidated axis as a prediction.")
"""),
md(r"""
## 4. Panel D — the four-group dual-mechanism design (roadmap N3)

The C4 crosstab (destabilising × top-decile rewiring) turned into four **named** lists:
destabilising-only, rewiring-only, both, neither. Without a validated specificity axis only two of
the four groups exist, and those two are exactly Panel S and its controls, so Panel D is not built
a second time.
"""),
code(r"""
PANEL_D = {}
if HAVE_REWIRING:
    groups = {'destabilising_only': A[A.destab & ~A.high_rewiring], 'rewiring_only': A[~A.destab & A.high_rewiring],
              'both': A[A.destab & A.high_rewiring], 'neither': A[~A.destab & ~A.high_rewiring]}
    for name, pool in groups.items():
        key = {'destabilising_only': 'fold_lo', 'both': 'fold_lo', 'rewiring_only': 'rewiring'}.get(name, 'fold_halfwidth')
        asc = key == 'fold_halfwidth'                      # strongest effect first; narrowest interval for 'neither'
        PANEL_D[name] = pool.sort_values(['nonhyper', key], ascending=[False, asc]).head(min(N_PER_PANEL, 6))
    print({k: len(v) for k, v in PANEL_D.items()})
else:
    print('Four-group design not available: only destabilising vs not-destabilising is supported, '
          'which Panel S and its controls already cover.')
PANEL_D_SIZES = {k: len(v) for k, v in PANEL_D.items()}
"""),
md(r"""
## 5. Assemble the panel, assign assays and a priority tier

**Tier 1:** seen in a non-hypermutated tumour **and** an interval narrower than the atlas median.
**Tier 2:** everything else that met the panel's rule. A ranking aid for where to start, not a
statement that tier-2 variants matter less.
"""),
code(r"""
MEDIAN_HW = float(A.fold_halfwidth.median())
COLS = ['variant_id', 'gene', 'domain_idx', 'pos', 'pred_ddG_fold', 'fold_lo', 'fold_halfwidth',
        'rewiring', 'nonhyper', 'top_primary_sites', 'mechanism', 'assay_recommendation', 'priority_tier']

def assemble(df, mechanism, assays):
    out = df.copy()
    out['mechanism'] = mechanism; out['assay_recommendation'] = '; '.join(assays)
    out['priority_tier'] = np.where(out.nonhyper & (out.fold_halfwidth <= MEDIAN_HW), 1, 2)
    out = out.reindex(columns=COLS)
    out['domain_idx'] = pd.to_numeric(out.domain_idx, errors='coerce').astype('Int64')   # 2, not 2.000
    return out

parts = [assemble(PANEL_S, 'destabilising (Panel S)', STABILITY_ASSAYS),
         assemble(PANEL_S_CTRL, 'tolerated control (Panel S)', ['same stability assay as Panel S (negative control)']),
         assemble(PANEL_R, 'rewiring only (Panel R)', SPECIFICITY_ASSAYS)]
parts += [assemble(v, f'{k} (Panel D)', STABILITY_ASSAYS + (SPECIFICITY_ASSAYS if k in ('rewiring_only', 'both') else []))
          for k, v in PANEL_D.items()]
CAND = pd.concat([p for p in parts if len(p)], ignore_index=True).drop_duplicates(['variant_id', 'mechanism'])
CAND.to_csv(R.out('experimental_candidates.csv'), index=False)
SUMMARY = CAND.groupby('mechanism').agg(candidates=('variant_id', 'size'),
                                        tier1=('priority_tier', lambda s: int((s == 1).sum()))).reset_index()
SUMMARY.to_csv(R.out('panel_summary.csv'), index=False)
print(SUMMARY.to_string(index=False))
"""),
md(r"""
## Results

**What this is not.** A destabilising call here is a hypothesis this stage exists to test, not
evidence on its own. Assay feasibility (expression, peptide availability, cost, throughput) is
not modelled and must be checked before committing bench time. Panel sizes are a first campaign,
to be revised when the first results come back. `experimental_candidates.csv` lists COSMIC
variants with tumour sites, so it stays on Drive (`.gitignore`); the report below omits the
tumour-site column.
"""),
code(r"""
for k, v in [('n_per_panel', N_PER_PANEL), ('specificity_axis_validated', HAVE_REWIRING),
             ('panel_s_destabilising', len(PANEL_S)), ('panel_s_control', len(PANEL_S_CTRL)),
             ('panel_s_control_same_domain', CTRL_MATCHED), ('panel_r_rewiring_only', len(PANEL_R)),
             ('four_group_design_available', HAVE_REWIRING), ('total_candidates', len(CAND)),
             ('total_tier1', int((CAND.priority_tier == 1).sum())), ('median_atlas_fold_halfwidth', MEDIAN_HW)]:
    R.metric(k, v)
for k, v in PANEL_D_SIZES.items(): R.metric(f'panel_d_{k}', v)

R.section('Panel sizes by class', 'Tier 1 = seen in a non-hypermutated tumour and a below-median 90% half-width.', SUMMARY)
R.section('Candidates', 'Full table (with tumour sites): `experimental_candidates.csv`, on Drive only.',
          CAND.drop(columns=['top_primary_sites', 'assay_recommendation']), '{:.3f}')
R.section('Assays by class', '', pd.DataFrame([('stability (Panel S)', '; '.join(STABILITY_ASSAYS)),
                                               ('specificity (Panel R)', '; '.join(SPECIFICITY_ASSAYS))],
                                              columns=['class', 'recommended assays']))
if not HAVE_REWIRING:
    R.section('Why there is no specificity or four-group panel',
              f"C4's pre-registered rule returned validated=False (median centred r "
              f"{DEC_C4.get('median_centred_r', float('nan')):.3f}; wins vs the average profile "
              f"{DEC_C4.get('wins_vs_mean')}/{DEC_C4.get('domains')}). Panel R and the rewiring groups of Panel D are "
              "intentionally empty rather than built from the disclaimed ESM-based label in B3.")
R.finish([f"{len(CAND)} candidates in {SUMMARY.shape[0]} classes, {int((CAND.priority_tier == 1).sum())} of them tier 1.",
          f"Controls from the same domains as the destabilising picks: {CTRL_MATCHED} of {len(PANEL_S_CTRL)}.",
          f"Specificity axis validated (C4): {HAVE_REWIRING}" + ('.' if HAVE_REWIRING else
          ' — no rewiring panel and no four-group design, by design.'),
          'Nothing upstream was re-run or changed; a prioritisation aid, not a result.'])
"""),
]

# ════════════════════════════════════════════════════════════════════════ F2
F2 = [md(r"""
# F2 — Figures for the experimental candidate panel (F1)

**Question.** How do the F1 candidates look against their own uncertainty, against the whole atlas,
and on the SH3 fold, so the panel can be shown (thesis, supervisor, collaborators) before any bench
work is planned?

**What it does.** Draws three figures from files that already exist. Nothing is recomputed, and no
number from A0–F1 changes.
1. **figF1_candidate_pairs:** each destabilising pick next to its same-domain control, with the 90 %
   conformal interval and the 1 kcal/mol threshold.
2. **figF2_atlas_context:** where the picks and controls sit in the distribution of lower bounds of all
   6,884 atlas variants.
3. **figF3_position_map:** the picks on the SH3 family landscape from B6 (mean predicted damage per
   aligned position), showing how concentrated the panel is along the fold.

**Inputs:** `F1/experimental_candidates.csv`, `B3/atlas_predictions.parquet`, `B6/family_position_map.csv`.
**Outputs:** `figF1…figF3` (PNG + PDF), `candidate_positions.csv`, `RESULTS_F2.md`.
**Runtime:** seconds, CPU. Explanation: `docs/F2_candidate_figures.md`.
"""),
setup('F2', 'Figures for the experimental candidate panel'),
code(r"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 110,
                     'savefig.dpi': 300, 'savefig.bbox': 'tight'})
BLUE, ORANGE, GREEN, RED, PURPLE, GREY = '#2f6fb5', '#d8792a', '#3f8f5e', '#c0392b', '#7a5aa8', '#9a9a9a'
def save(fig, name):
    for ext in ('png', 'pdf'): fig.savefig(R.out(f'{name}.{ext}'))
    plt.show(); plt.close(fig)

CAND = pd.read_csv(R.res('F1', 'experimental_candidates.csv'))
A = pd.read_parquet(R.res('B3', 'atlas_predictions.parquet'))
FAM = pd.read_csv(R.res('B6', 'family_position_map.csv'))
CAND = CAND.merge(A[['variant_id', 'ref_pos', 'wt_aa', 'mut_aa']], on='variant_id', how='left')
CAND['label'] = CAND.gene + '  ' + CAND.wt_aa + CAND.pos.astype(int).astype(str) + CAND.mut_aa
CAND['upper'] = CAND.pred_ddG_fold + CAND.fold_halfwidth
PICK = CAND[CAND.mechanism.str.startswith('destabilising')].copy()
CTRL = CAND[CAND.mechanism.str.startswith('tolerated')].copy()
assert len(PICK) and len(CTRL), 'Run F1 first: no candidates found.'
print(f'{len(PICK)} picks, {len(CTRL)} controls, {len(A):,} atlas variants, {len(FAM)} aligned positions')
"""),
md("## 1. Each pick next to its same-domain control"),
code(r"""
order = PICK.sort_values('fold_lo').gene.tolist()
fig, ax = plt.subplots(figsize=(8.5, 0.55 * len(order) + 1.6))
for i, g in enumerate(order):
    for df, col, dy, mk in [(PICK, RED, 0.17, 'o'), (CTRL, BLUE, -0.17, 's')]:
        r = df[df.gene == g]
        if len(r) == 0: continue
        r = r.iloc[0]
        ax.hlines(i + dy, r.fold_lo, r.upper, color=col, lw=2.5, alpha=.55)
        ax.plot(r.pred_ddG_fold, i + dy, mk, color=col, ms=7)
        ax.text(r.upper + 0.12, i + dy, r.label.split('  ')[1], va='center', fontsize=8, color=col)
ax.axvline(1.0, color='k', ls='--', lw=1); ax.axvline(0, color=GREY, lw=.8)
ax.text(1.03, len(order) - 0.4, 'call threshold: lower bound ≥ 1 kcal/mol', fontsize=8)
ax.set_yticks(range(len(order)), order); ax.set_xlabel('predicted ΔΔG$_{fold}$ (kcal/mol), 90 % conformal interval')
ax.plot([], [], 'o', color=RED, label='destabilising pick'); ax.plot([], [], 's', color=BLUE, label='tolerated control, same domain')
ax.legend(frameon=False, loc='lower right', fontsize=8)
ax.set_title(f'{len(PICK)} bench picks, each paired with a neutral control from the same SH3 domain', loc='left', weight='bold')
save(fig, 'figF1_candidate_pairs')
"""),
md("## 2. The panel against the whole atlas"),
code(r"""
PCT = {v: float((A.fold_lo < l).mean() * 100) for v, l in zip(PICK.variant_id, PICK.fold_lo)}
fig, ax = plt.subplots(figsize=(8.5, 4.2))
bins = np.linspace(A.fold_lo.min(), A.fold_lo.max(), 70)
ax.hist(A.fold_lo, bins=bins, color=GREY, alpha=.6, label=f'all {len(A):,} atlas variants')
ax.hist(A.fold_lo[A.fold_lo >= 1], bins=bins, color=ORANGE, alpha=.7, label=f'called destabilising ({int((A.fold_lo >= 1).sum())})')
top = ax.get_ylim()[1]
for x in PICK.fold_lo: ax.plot([x, x], [0, top * .12], color=RED, lw=2)
for x in CTRL.fold_lo: ax.plot([x, x], [0, top * .12], color=BLUE, lw=2)
ax.plot([], [], color=RED, lw=2, label='picks'); ax.plot([], [], color=BLUE, lw=2, label='controls')
ax.axvline(1.0, color='k', ls='--', lw=1); ax.set_yscale('log')
ax.set_xlabel('lower 90 % bound of predicted ΔΔG$_{fold}$ (kcal/mol)'); ax.set_ylabel('variants (log scale)')
ax.set_title(f'Picks are the extreme tail: every pick above the {min(PCT.values()):.1f}th percentile of the atlas',
             loc='left', weight='bold')
ax.legend(frameon=False, fontsize=8); save(fig, 'figF2_atlas_context')
"""),
md("## 3. Where the picks sit on the SH3 fold (B6 family landscape)"),
code(r"""
POS = PICK.dropna(subset=['ref_pos']).groupby('ref_pos').agg(picks=('variant_id', 'size'),
                                                             genes=('gene', lambda s: ', '.join(s))).reset_index()
POS.to_csv(R.out('candidate_positions.csv'), index=False)
fig, ax = plt.subplots(figsize=(10, 4.2))
cols = np.where(FAM.buried, ORANGE, GREY)
ax.bar(FAM.ref_pos, FAM.mean_pred, color=cols, width=.8)
ax.bar(FAM.ref_pos[FAM.interface], FAM.mean_pred[FAM.interface], color='none', edgecolor=PURPLE, lw=1.5, width=.8)
ymax = FAM.mean_pred.max()
for _, r in POS.iterrows():
    ax.annotate(f'{int(r.picks)}', (r.ref_pos, FAM.set_index('ref_pos').mean_pred.get(r.ref_pos, ymax) + .08),
                ha='center', color=RED, weight='bold')
    ax.plot(r.ref_pos, -0.12, '^', color=RED, ms=9, clip_on=False)
# proxy handles must be real artists: ax.bar([], []) yields a container with no patch,
# so the legend falls back to a default swatch and the colours are wrong.
HANDLES = [Patch(facecolor=ORANGE, label='buried'),
           Patch(facecolor=GREY, label='exposed'),
           Patch(facecolor='none', edgecolor=PURPLE, lw=1.5, label='peptide interface'),
           Line2D([], [], marker='^', color=RED, ls='none', ms=9, label='F1 picks (number above bar)')]
ax.set_xlabel('aligned position (GRB2-SH3 frame)'); ax.set_ylabel('mean predicted ΔΔG$_{fold}$, all substitutions')
ax.set_ylim(0, ymax * 1.2); ax.legend(handles=HANDLES, frameon=False, fontsize=8, ncol=4, loc='upper right')
TOPPOS = POS.sort_values('picks', ascending=False).iloc[0]
ax.set_title(f'{int(TOPPOS.picks)} of {len(PICK)} picks sit at aligned position {int(TOPPOS.ref_pos)}: '
             f'the panel covers {len(POS)} of {len(FAM)} positions', loc='left', weight='bold')
save(fig, 'figF3_position_map')
print(POS.to_string(index=False))
"""),
md("## Results"),
code(r"""
for k, v in [('picks', len(PICK)), ('controls', len(CTRL)), ('positions_covered', len(POS)),
             ('aligned_positions', len(FAM)), ('max_picks_at_one_position', int(TOPPOS.picks)),
             ('most_used_position', int(TOPPOS.ref_pos)), ('min_pick_percentile', min(PCT.values())),
             ('picks_buried', int(PICK.ref_pos.map(FAM.set_index('ref_pos').buried).fillna(False).sum())),
             ('picks_to_proline', int((PICK.mut_aa == 'P').sum()))]:
    R.metric(k, v)
R.section('Figures', '', pd.DataFrame([('figF1_candidate_pairs', 'each pick vs its same-domain control, 90 % intervals'),
                                       ('figF2_atlas_context', 'picks and controls in the distribution of all atlas lower bounds'),
                                       ('figF3_position_map', 'picks on the B6 family landscape (aligned positions)')],
                                      columns=['file (PNG + PDF)', 'shows']))
R.section('Aligned positions used by the picks', 'Concentration check: one position dominating means the panel '
          'tests one structural mechanism.', POS)
R.finish([f"{len(PICK)} picks and {len(CTRL)} same-domain controls drawn; every pick is above the "
          f"{min(PCT.values()):.1f}th percentile of atlas lower bounds.",
          f"The picks cover {len(POS)} of {len(FAM)} aligned positions; {int(TOPPOS.picks)} sit at position {int(TOPPOS.ref_pos)}.",
          f"{int((PICK.mut_aa == 'P').sum())} of {len(PICK)} picks are substitutions to proline.",
          'Figures only: nothing upstream was re-run or changed.'])
"""),
]

NOTEBOOKS = {'F1_experimental_candidates': (F1, False), 'F2_candidate_figures': (F2, False)}
