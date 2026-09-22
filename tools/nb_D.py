"""Part D — figures from every program's outputs, and the reproduction check across the whole pipeline."""
from nbkit import md, code, setup

D1 = [md(r"""
# D1 — Figures, and did the whole pipeline reproduce?

**What it does.**
1. Collects every program's comparison table and writes one **reproduction report**: how many
   recorded quantities came out identical, within tolerance, or different — with the ORIGINAL and
   CORRECTED binding procedures side by side.
2. Draws the six result figures from the programs' own output files (nothing is re-computed here).
3. Writes `results/RESULTS_SUMMARY.md`, the one-page overview of the run.

**Inputs:** every `results/*/` folder. **Runtime:** about 1 min, CPU.
**Outputs:** `fig1…fig6` (PNG + PDF), `reproduction_table.csv`, `original_vs_corrected.csv`,
`RESULTS_D1.md`, and `results/RESULTS_SUMMARY.md`. Explanation: `docs/D1_figures_and_verification.md`.
"""),
setup('D1', 'Figures and verification'),
code(r"""
import glob
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 110,
                     'savefig.dpi': 300, 'savefig.bbox': 'tight'})
BLUE, ORANGE, GREEN, RED, PURPLE, GREY = '#2f6fb5', '#d8792a', '#3f8f5e', '#c0392b', '#7a5aa8', '#9a9a9a'
RES = f'{ROOT}/results'
def res(pid, name): return R.res(pid, name)
MET, CMP, missing = {}, [], []
for pid in C.PROGRAMS[:-1]:
    try:
        MET[pid] = json.load(open(res(pid, f'metrics_{pid}.json')))
        CMP.append(pd.read_csv(res(pid, f'comparison_{pid}.csv')).assign(program=pid))
    except FileNotFoundError:
        missing.append(pid)
print('programs found:', list(MET), '| missing:', missing)
CMP = pd.concat(CMP, ignore_index=True)
"""),
md("## 1. Reproduction report"),
code(r"""
checked = CMP[CMP.status.isin(['identical', 'within tolerance', 'DIFF'])]
BYP = checked.groupby(['program', 'status']).size().unstack(fill_value=0).reindex(columns=['identical', 'within tolerance', 'DIFF'],
                                                                                   fill_value=0).reset_index()
BYP = BYP.merge(pd.DataFrame([dict(program=p, verdict=MET[p]['meta']['verdict'], minutes=MET[p]['meta']['minutes'])
                              for p in MET]), on='program')
checked.to_csv(R.out('reproduction_table.csv'), index=False)
print(BYP.to_string(index=False))
if (checked.status == 'DIFF').any(): print('\nDIFFERENT:\n' + checked[checked.status == 'DIFF'].to_string(index=False))

# ORIGINAL vs CORRECTED, side by side, for every binding quantity measured both ways
bm = CMP[CMP.program.isin(['C1', 'C2', 'C3']) & CMP.quantity.str.match(r'^(original|corrected)\.')].copy()
bm['mode'] = bm.quantity.str.split('.').str[0]; bm['what'] = bm.quantity.str.split('.', n=1).str[1]
OVC = bm.pivot_table(index=['program', 'what'], columns='mode', values='this_run', aggfunc='first').reset_index()
rec = bm[bm['mode'] == 'original'].set_index(['program', 'what']).recorded
OVC['recorded'] = [rec.get((p, w)) for p, w in zip(OVC.program, OVC.what)]
num = lambda s: pd.to_numeric(s, errors='coerce')
OVC['change'] = num(OVC.get('corrected')) - num(OVC.get('original'))
OVC.to_csv(R.out('original_vs_corrected.csv'), index=False)
key = OVC[OVC.what.str.contains('GRB2-SH3.repeats_median|PSD95-PDZ3.repeats_median|matched_median|sweep_B_thin_median|'
                                'sweep_C_fewpos_median|GRB2-SH3.rho')]
print(key.to_string(index=False))
"""),
md("## 2. Figures"),
code(r"""
def save(fig, name):
    for ext in ('png', 'pdf'): fig.savefig(R.out(f'{name}.{ext}'))
    plt.show(); plt.close(fig)

# fig1 — folding head vs ESM-2 on every held-out domain
PD = pd.read_csv(res('B1', 'folding_per_domain_ci.csv')).sort_values('rho')
fig, ax = plt.subplots(figsize=(7.5, 5.8)); yy = np.arange(len(PD))
ax.hlines(yy, PD.lo, PD.hi, color=BLUE, alpha=.5, lw=2.5); ax.plot(PD.rho, yy, 'o', color=BLUE, ms=7, label='supervised head (95% CI)')
ax.plot(PD.esm.abs(), yy, 'D', color=ORANGE, ms=6, label='ESM-2 zero-shot (|ρ|)')
ax.axvline(PD.rho.median(), color=BLUE, ls='--', lw=1); ax.axvline(PD.esm.abs().median(), color=ORANGE, ls='--', lw=1)
ax.set_yticks(yy, PD.gene); ax.set_xlim(0, 1); ax.set_xlabel('Spearman ρ against measured ΔΔG$_{fold}$')
ax.set_title(f'Folding head beats ESM-2 on {int((PD.rho > PD.esm.abs()).sum())}/{len(PD)} held-out SH3 domains', loc='left', weight='bold')
ax.legend(frameon=False, loc='lower left'); save(fig, 'fig1_folding_vs_esm')

# fig2 — damage follows burial, not the interface
H = pd.read_csv(res('B2', 'position_structure_check.csv'))
fig, axs = plt.subplots(1, 2, figsize=(10, 4.3), sharey=True)
for ax, x, lab, col, flag, rho in [(axs[0], H.rsasa, 'relative solvent accessibility', GREEN, H.buried, MET['B2']['metrics']['rho_damage_vs_burial']),
                                   (axs[1], H.dist_peptide, 'distance to bound peptide (Å)', PURPLE, H.interface, MET['B2']['metrics']['rho_damage_vs_interface'])]:
    ax.scatter(x, H.mean_fold, c=np.where(flag, col, GREY), s=34, edgecolor='white')
    ax.set_xlabel(lab); ax.text(.97, .95, f'ρ = {rho:+.3f}', transform=ax.transAxes, ha='right', va='top', color=col, weight='bold', fontsize=12)
axs[0].set_ylabel('mean predicted ΔΔG$_{fold}$ (kcal/mol)')
fig.suptitle('Predicted damage tracks burial (A), not the binding interface (B)', x=.01, ha='left', weight='bold'); save(fig, 'fig2_burial_specificity')

# fig3 — positions, not rows
SW = pd.read_csv(res('C3', 'threshold_sweeps.csv')); PS = pd.read_csv(res('C3', 'position_sweep.csv'))
MB = pd.read_csv(res('C3', 'matched_budget.csv'))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={'width_ratios': [1, 1.2]})
cols = {'A_folds': BLUE, 'B_thin': GREEN, 'C_fewpos': RED}; labs = {'A_folds': 'full data', 'B_thin': 'rows cut', 'C_fewpos': 'positions cut'}
for i, s in enumerate(['A_folds', 'B_thin', 'C_fewpos']):
    for j, (m, mk) in enumerate([('original', 'o'), ('corrected', 's')]):
        v = SW[(SW.sweep == s) & (SW['mode'] == m)].rho
        if len(v) == 0: continue
        x = i + (j - .5) * .3
        axs[0].scatter(np.full(len(v), x) + np.random.default_rng(0).uniform(-.05, .05, len(v)), v, color=cols[s], alpha=.35, s=14, marker=mk)
        axs[0].hlines(v.median(), x - .12, x + .12, color=cols[s], lw=3)
axs[0].set_xticks(range(3), [labs[s] for s in ['A_folds', 'B_thin', 'C_fewpos']]); axs[0].axhline(0, color='k', ls=':', lw=.8)
axs[0].set_ylabel('Spearman ρ on held-out positions'); axs[0].set_title('A. matched rows, different positions\n(left: original, right: corrected partitions)', loc='left', fontsize=9.5)
q = PS.groupby('target_pos').rho
axs[1].scatter(PS.target_pos, PS.rho, color=BLUE, alpha=.3, s=12); axs[1].plot(q.median().index, q.median().values, 'o-', color=BLUE)
for m, mk in [('original', 'D'), ('corrected', 's')]:
    v = MB[MB['mode'] == m].rho
    if len(v): axs[1].plot(56, v.median(), mk, color=RED, ms=9, label=f'PSD95 cut to GRB2 budget ({m})')
cross = MET['C3']['metrics'].get('crossing_positions')
if cross: axs[1].axvspan(cross, 85, color=GREEN, alpha=.07)
axs[1].axhline(0, color='k', ls=':', lw=.8); axs[1].set_xlabel('distinct positions in the training data'); axs[1].legend(frameon=False, fontsize=8)
axs[1].set_title('B. accuracy against positions sampled', loc='left', fontsize=9.5)
fig.suptitle('What limits the binding head is positions sampled, not rows of data', x=.01, ha='left', weight='bold'); save(fig, 'fig3_binding_positions')

# fig4 — ProteinGym transfer
PG = pd.read_csv(res('B4', 'proteingym_results.csv'))
fig, ax = plt.subplots(figsize=(8, 4.6))
for i, b in enumerate(['primary', 'secondary', 'sanity']):
    g = PG[PG.block == b]
    for _, r in g.iterrows():
        w = abs(r.rho_model) > abs(r.rho_esm)
        ax.plot([i - .15, i + .15], [abs(r.rho_model), abs(r.rho_esm)], color=GREEN if w else RED, alpha=.4)
    ax.scatter(np.full(len(g), i - .15), g.rho_model.abs(), color=BLUE, s=22, zorder=3)
    ax.scatter(np.full(len(g), i + .15), g.rho_esm.abs(), color=ORANGE, s=22, zorder=3)
    ax.text(i, -.1, f"head wins {int((g.rho_model.abs() > g.rho_esm.abs()).sum())}/{len(g)}", ha='center', fontsize=9)
ax.set_xticks(range(3), ['primary\n(external stability)', 'secondary\n(abundance)', 'sanity\n(training data)'])
ax.set_ylim(-.15, 1.02); ax.set_ylabel('|Spearman ρ|'); ax.scatter([], [], color=BLUE, label='SH3-trained head'); ax.scatter([], [], color=ORANGE, label='ESM-2 zero-shot')
ax.legend(frameon=False, loc='upper left'); ax.set_title('Transfer to other protein families: the head falls further than ESM-2', loc='left', weight='bold')
save(fig, 'fig4_proteingym_transfer')

# fig5 — atlas calls and the biological tests
b3, b5 = MET['B3']['metrics'], MET['B5']['metrics']
counts = {k: b3[f'n_{k}'] for k in ('tolerated', 'destabilising', 'both', 'rewiring')}
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={'width_ratios': [1.3, 1]})
called = {k: v for k, v in counts.items() if k != 'tolerated'}
axs[0].barh(list(called), list(called.values()), color=[RED, ORANGE, PURPLE])
for i, v in enumerate(called.values()): axs[0].text(v + 5, i, f'{v:,}', va='center')
axs[0].invert_yaxis(); axs[0].set_xlabel('variants')
axs[0].set_title(f"{sum(called.values()):,} of {sum(counts.values()):,} variants called; {counts['tolerated']:,} tolerated", loc='left', fontsize=10)
tests = [('genes enriched (all)', f"{b5['genes_sig_all']}/{b5['genes_tested_all']}"), ('genes enriched (non-hyper)', f"{b5['genes_sig_nonhyper']}/{b5['genes_tested_nonhyper']}"),
         ('tumour sites enriched', f"{b5['sites_sig']}/{b5['sites_tested']}"), ('ρ(variants, damage)', f"{b5['rho_variants_vs_damage']:+.3f}"),
         ('positional non-uniformity p', f"{b5['positional_uniform_p']:.0e}")]
axs[1].axis('off'); axs[1].set_title('Does damage explain cancer selection?', loc='left', fontsize=10)
for i, (a, v) in enumerate(tests):
    axs[1].text(0, .85 - i * .18, a, fontsize=10); axs[1].text(1, .85 - i * .18, v, fontsize=10, ha='right', weight='bold', color=GREEN if 'p' in a else RED)
fig.suptitle('What the atlas calls — a mechanism map, not a driver predictor', x=.01, ha='left', weight='bold'); save(fig, 'fig5_atlas_mechanisms')

# fig6 — refitting the same binding data
RP = pd.read_csv(res('C2', 'within_domain_repeats.csv')); LC = pd.read_csv(res('C3', 'learning_curve.csv'))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.3), gridspec_kw={'width_ratios': [1.3, 1]})
for dom, col in [('PSD95-PDZ3', BLUE), ('GRB2-SH3', ORANGE)]:
    g = LC[(LC.domain == dom) & (LC['mode'] == 'original')].groupby('n').rho
    axs[0].plot(g.median().index, g.median().values, 'o-', color=col, label=dom)
    axs[0].fill_between(g.median().index, g.min().values, g.max().values, color=col, alpha=.12)
axs[0].axhline(0, color='k', ls=':', lw=.8); axs[0].set_xlabel('measurements in the draw'); axs[0].set_ylabel('Spearman ρ on held-out positions')
axs[0].legend(frameon=False); axs[0].set_title('A. accuracy against training size', loc='left', fontsize=9.5)
doms = ['PSD95-PDZ3', 'GRB2-SH3', 'GB1']
for i, dom in enumerate(doms):
    for j, (m, col) in enumerate([('original', GREY), ('corrected', BLUE)]):
        v = RP[(RP.domain == dom) & (RP['mode'] == m)].rho
        if len(v): axs[1].scatter(np.full(len(v), i + (j - .5) * .3), v, color=col, s=26, label=m if i == 0 else None)
axs[1].axhline(0, color='k', ls=':', lw=.8); axs[1].set_xticks(range(3), doms)
axs[1].legend(frameon=False, fontsize=8); axs[1].set_title('B. six refits of the full data, by partition mode', loc='left', fontsize=9.5)
fig.suptitle('Refitting the same binding data gives a different answer each time', x=.01, ha='left', weight='bold'); save(fig, 'fig6_binding_refits')

# fig7 — the independent specificity axis (C4), if it was run
if 'C4' in MET:
    CV = pd.read_csv(res('C4', 'specificity_cv.csv')); c4 = MET['C4']['metrics']
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    axs[0].hist(CV.r_model, bins=20, color=BLUE, alpha=.8); axs[0].axvline(0, color='k', ls=':')
    axs[0].axvline(c4['median_centred_r'], color=RED, lw=2)
    axs[0].set_xlabel('centred r, predicted vs observed specificity profile'); axs[0].set_ylabel('held-out domains')
    axs[0].set_title(f"A. median r {c4['median_centred_r']:+.2f} [{c4['median_centred_r_ci_lo']:+.2f}, {c4['median_centred_r_ci_hi']:+.2f}]"
                     f" — {'validated' if c4['validated'] else 'NOT validated'}", loc='left', fontsize=9.5)
    AR = pd.read_parquet(res('C4', 'atlas_rewiring.parquet'))
    axs[1].scatter(AR.pred_ddG_fold, AR.rewiring, s=5, alpha=.3, color=np.where(AR.fold_lo >= 1, RED, GREY))
    axs[1].set_xlabel('predicted ΔΔG$_{fold}$ (kcal/mol)'); axs[1].set_ylabel('predicted specificity change (JS distance)')
    axs[1].set_title(f"B. two axes, ρ = {c4['rho_rewiring_vs_predicted_fold']:+.2f}", loc='left', fontsize=9.5)
    fig.suptitle('An ESM-independent specificity axis from experimental PWMs', x=.01, ha='left', weight='bold'); save(fig, 'fig7_specificity_axis')

# fig8 — family-wide folding landscape (B6), if it was run
if 'B6' in MET:
    FAM = pd.read_csv(res('B6', 'family_position_map.csv'))
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.bar(FAM.ref_pos, FAM.mean_pred, color=np.where(FAM.buried, GREEN, np.where(FAM.interface, PURPLE, GREY)))
    ax.set_xlabel('aligned position (GRB2-SH3 frame)'); ax.set_ylabel('mean predicted ΔΔG$_{fold}$, all substitutions')
    ax.bar([], [], color=GREEN, label='buried'); ax.bar([], [], color=PURPLE, label='interface'); ax.legend(frameon=False)
    ax.set_title('Virtual saturation mutagenesis: where every human SH3 domain is fragile', loc='left', weight='bold'); save(fig, 'fig8_family_landscape')
"""),
md("## 3. Summary files"),
code(r"""
m = lambda p, k: MET[p]['metrics'].get(k)
tot = checked.status.value_counts()
R.metric('quantities_checked', len(checked)); R.metric('identical', int(tot.get('identical', 0)))
R.metric('within_tolerance', int(tot.get('within tolerance', 0))); R.metric('different', int(tot.get('DIFF', 0)))
R.section('Reproduction by program', '', BYP)
R.section('Binding: ORIGINAL vs CORRECTED partitions (key quantities)', 'Full table: `original_vs_corrected.csv`.', key, '{:.3f}')
if (checked.status == 'DIFF').any(): R.section('Quantities that differ', '', checked[checked.status == 'DIFF'])
HEAD = [f"Stage 0: {m('A0','variants'):,} variants in {m('A0','domains')} domains; byte-identical to the original atlas: "
        f"{m('A0','master_md5') == 'cef897f4dd25f9cd56f2c40bb7ec0b08'}.",
        f"Folding: per-domain median ρ {m('B1','per_domain_median_rho'):.3f} on {m('B1','domains')} held-out SH3 domains; beats ESM-2 on "
        f"{m('B1','domains_won')}/{m('B1','domains')}.",
        f"Specificity: damage vs burial ρ {m('B2','rho_damage_vs_burial'):+.3f}, vs interface ρ {m('B2','rho_damage_vs_interface'):+.3f}.",
        f"Binding: GRB2-SH3 median ρ {m('C2','original.GRB2-SH3.repeats_median'):+.3f} (original) / "
        f"{m('C2','corrected.GRB2-SH3.repeats_median') if m('C2','corrected.GRB2-SH3.repeats_median') is None else round(m('C2','corrected.GRB2-SH3.repeats_median'),3)} (corrected); "
        f"predictability appears at ~{m('C3','crossing_positions')} positions, GRB2-SH3 has {m('C3','grb2_positions')}.",
        f"Atlas: {m('B3','n_destabilising')} destabilising, {m('B3','n_both')} both, {m('B3','n_rewiring')} rewiring (not claimed), "
        f"{m('B3','n_tolerated'):,} tolerated; genes enriched {m('B5','genes_sig_all')}/{m('B5','genes_tested_all')}.",
        *([f"Specificity axis (C4): median centred r {m('C4','median_centred_r'):+.3f}; "
           f"{'validated' if m('C4','validated') else 'not validated - no rewiring claim'}."] if 'C4' in MET else []),
        *([f"Virtual scan (B6): {m('B6','virtual_variants'):,} substitutions; {m('B6','frac_destabilising_all_possible'):.1%} of all possible "
           f"vs {m('B6','frac_destabilising_observed'):.1%} of observed cancer variants destabilising."] if 'B6' in MET else []),
        f"Reproduction: {int(tot.get('identical',0))} identical, {int(tot.get('within tolerance',0))} within tolerance, "
        f"{int(tot.get('DIFF',0))} different, of {len(checked)} recorded quantities."]
S = ['# SH3 pipeline — results summary', '', f'*Generated by D1 on {R.started}.*', '', '## Headline', ''] + [f'- {h}' for h in HEAD]
S += ['', '## Every program', '', C.md_table(BYP), '', '## Figures', '']
S += [f'- `D1_figures_and_verification/{f}.png`' for f in ['fig1_folding_vs_esm', 'fig2_burial_specificity', 'fig3_binding_positions',
                                                           'fig4_proteingym_transfer', 'fig5_atlas_mechanisms', 'fig6_binding_refits',
                                                           'fig7_specificity_axis', 'fig8_family_landscape']]
S += ['', 'Each program folder holds its own `RESULTS_<ID>.md` with the full detail.']
open(f'{RES}/RESULTS_SUMMARY.md', 'w').write('\n'.join(S))
R.finish(HEAD)
"""),
]
NOTEBOOKS = {'D1_figures_and_verification': (D1, False)}
