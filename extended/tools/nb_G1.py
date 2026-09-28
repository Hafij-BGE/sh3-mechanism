"""Generates G1a and G1b — the two mutational-spectrum notebooks.

Judged against docs/preregistration/G1.md, committed before this file existed. The
rules implemented here are that file's, not choices made while writing code:

  Part 2   predictions come from B6's frozen virtual DMS; `fold_lo >= 1` is the call
  Part 3   the uniform control must reproduce B6's 9.18 % or both notebooks stop
  Part 4   one-sided p, observed BELOW null; three outcomes fixed in advance
  Part 9.1 two notebooks, sharing tools/g1_core.py as CODE, not as intention
  Part 9.3 alpha is 0.025 if a primary is named in G1.md before running, else
           0.0125 for both -- the notebook reads the file and decides, so the
           choice cannot be made after seeing a p-value
  Part 10  the null draws BASE CHANGES; 3a (substitutions) and 3b (base changes)
           separate B6's baseline from reachability multiplicity from context
  Part 11  "retains most of its size" is >= 1.63 pp, implemented in g1_core.verdict

The two notebooks differ in exactly one cell: the SPECTRUM cell. Everything else is
generated from the same strings below, and g1_core.py is embedded byte-for-byte with
its SHA-256 asserted at run time, so "identical machinery" is checkable.

Shares md()/code()/build() with nb_E.py.
"""
import ast
import builtins
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nb_E import md, code, build

HERE = pathlib.Path(__file__).resolve().parent
CORE = HERE / 'g1_core.py'
CORE_SRC = CORE.read_text()
CORE_SHA = hashlib.sha256(CORE.read_bytes()).hexdigest()


SETUP = code(
    "from google.colab import drive",
    "drive.mount('/content/drive')",
    "",
    "import json, sys, hashlib",
    "from pathlib import Path",
    "import pandas as pd, numpy as np",
    "",
    "DRIVE = Path('/content/drive/MyDrive')",
    "",
    "def pick(*names, what=''):",
    "    for n in names:",
    "        if (DRIVE / n).exists(): return DRIVE / n",
    "    raise FileNotFoundError(f'No {what} folder in MyDrive. Tried: ' + ', '.join(names))",
    "",
    "PROJECT = pick('sh3_repro/extended', 'SH3_extended', 'SH3 extended', what='project')",
    "FROZEN  = pick('sh3_repro', what='frozen-run')          # READ ONLY",
    "FROZEN_IN = PROJECT / 'input' / 'frozen'",
    "IN      = PROJECT / 'input' / 'external'",
    "OUT     = PROJECT / 'results' / 'G1_mutational_context'",
    "OUT.mkdir(parents=True, exist_ok=True)",
    "",
    "def frozen(rel, bundled):",
    "    p = FROZEN / 'results' / rel",
    "    return p if p.exists() else FROZEN_IN / 'results' / bundled",
    "",
    "print('project:', PROJECT); print('frozen :', FROZEN)",
)


CORE_CELL = code(
    "# g1_core.py, embedded byte-for-byte by tools/nb_G1.py at generation time.",
    "# Part 9.1: the two notebooks must run IDENTICAL machinery, so this is written",
    "# from one source and its hash is asserted below rather than trusted.",
    "core_src = r'''" + CORE_SRC.replace("'''", "\\'\\'\\'") + "'''",
    "Path('g1_core.py').write_text(core_src)",
    "",
    f"EXPECTED_SHA = '{CORE_SHA}'",
    "got = hashlib.sha256(Path('g1_core.py').read_bytes()).hexdigest()",
    "assert got == EXPECTED_SHA, (",
    "    f'g1_core.py hashes to {got}, expected {EXPECTED_SHA}. The two notebooks would '",
    "    'not be running the same code, so no comparison between them would be valid.')",
    "",
    "sys.path.insert(0, '.')",
    "# A kernel that already imported g1_core keeps the OLD module: `import` is a",
    "# no-op once sys.modules holds the name, so rewriting the file above changes",
    "# nothing and the hash check passes while stale code runs. Drop it first.",
    "import linecache",
    "sys.modules.pop('g1_core', None)",
    "linecache.checkcache('g1_core.py')",
    "import g1_core as G",
    "",
    "# The hash above covers the file; this covers what actually got imported.",
    "NEEDED = ('build_context', 'coverage_report', 'run_arm', 'observed_spectrum',",
    "          'cosmic_spectrum', 'verdict', 'cosine', 'write_metrics')",
    "missing = [n for n in NEEDED if not hasattr(G, n)]",
    "assert not missing, (",
    "    f'the imported g1_core is missing {missing}. It is stale -- restart the "
    "runtime (Runtime > Restart) and run from the top, and make sure this notebook "
    "is the freshly generated one.')",
    "print('g1_core sha256:', got[:16], '...  seed', G.SEED, ' draws', G.N_DRAWS)",
)


ALPHA_CELL = code(
    "# Part 9.3 -- the threshold is read from the pre-registration, not chosen here.",
    "# If G1.md names a primary spectrum before the run, that arm takes alpha = 0.025",
    "# and the other is a sensitivity analysis. If it names none, both are co-primary",
    "# at 0.0125 (Bonferroni, family-wise 0.025). Deciding after seeing a p-value is",
    "# therefore impossible: by then the file is already committed.",
    "prereg = (PROJECT / 'docs' / 'preregistration' / 'G1.md')",
    "text = prereg.read_text() if prereg.exists() else ''",
    "MARK = 'PRIMARY SPECTRUM:'",
    "named = [l.split(MARK, 1)[1].strip() for l in text.splitlines() if MARK in l]",
    "PRIMARY = named[0] if named else None",
    "ALPHA = 0.025 if PRIMARY else 0.0125",
    "print(f'primary named in G1.md : {PRIMARY!r}')",
    "print(f'alpha                  : {ALPHA}')",
    "",
    "# Which role THIS notebook plays needs its identity, and the identity lives in",
    "# the spectrum cell -- the one cell that differs between G1a and G1b. Naming it",
    "# here too would make two cells differ, and the comparison rests on exactly one",
    "# differing. So IS_PRIMARY is resolved in section 8, once the spectrum is known.",
    "print('role resolved in section 8, once the spectrum cell has named this notebook')",
)


DATA_CELL = code(
    "# ---- the three pinned inputs (Part 2). Nothing here is re-fitted. ----",
    "b6 = pd.read_parquet(frozen('B6_virtual_saturation_mutagenesis/sh3_virtual_dms.parquet',",
    "                            'sh3_virtual_dms.parquet'))",
    "print('B6 virtual DMS:', len(b6), 'rows')",
    "assert len(b6) == 366168, f'B6 has {len(b6)} rows, expected 366,168 -- wrong file'",
    "",
    "obs = pd.read_csv(OUT / 'atlas_grch38_coordinates.tsv', sep='\\t')",
    "obs['pos_protein'] = obs['pos_protein'].astype(int)",
    "print('observed with a verified coordinate:', len(obs))",
    "",
    "atlas = pd.read_csv(FROZEN_IN / 'results' / 'SH3_cancer_master.tsv', sep='\\t')",
    "assert len(atlas) == 6884, f'atlas has {len(atlas)} rows, expected 6,884'",
    "# The atlas's own pos_in_domain is the check on the offset B6's `pos` needs.",
    "bad = int((atlas['pos_protein'] - atlas['dom_start'] + 1 != atlas['pos_in_domain']).sum())",
    "assert bad == 0, f'{bad} atlas rows where pos_protein - dom_start + 1 != pos_in_domain'",
    "print('atlas:', len(atlas), 'rows; domain offset verified on all of them')",
    "",
    "# The null pool comes from the GENE-level release, not X1's in-domain parquet.",
    "# That parquet was filtered on the FIRST listed transcript's aapos; re-keying it",
    "# to another transcript afterwards keeps rows whose new position is outside the",
    "# domain and cannot recover rows the first-transcript filter never admitted.",
    "DBN = PROJECT / 'results' / 'X1_dbnsfp_subset' / 'dbnsfp_sh3.tsv.gz'",
    "assert DBN.exists(), (",
    "    f'{DBN} not found. X1\\'s gene-level release must be on Drive: the in-domain '",
    "    'parquet cannot serve as the null pool, because its domain filter used a '",
    "    'different transcript from the one the atlas numbers against.')",
    "print('dbNSFP gene-level release:', DBN.stat().st_size, 'bytes')",
)


POOL_CELL = code(
    "# dbNSFP lists one aapos per transcript. Matching the UniProt accession is NOT",
    "# enough -- the transcript it carries for an accession can be a different isoform,",
    "# and 23.7% of accession-matched rows land on a position whose residue disagrees",
    "# with the atlas, all-or-nothing per gene, which is what a frame shift looks like.",
    "#",
    "# So a transcript is accepted only where dbNSFP's aaref equals the atlas's own",
    "# wild-type residue there. That is the rule g1_coordinates.py used for the",
    "# observed set: a null built under a different rule is not a null for it.",
    "import gzip",
    "WT = G.wt_by_position(b6, atlas)",
    "print('in-domain protein positions known to the atlas:', len(WT))",
    "",
    "rows = []",
    "with gzip.open(DBN, 'rt') as fh:",
    "    ix = {c: j for j, c in enumerate(fh.readline().rstrip('\\n').split('\\t'))}",
    "    C, P, RF, AL = ix['#chr'], ix['pos(1-based)'], ix['ref'], ix['alt']",
    "    AR, AA, AP, GN = ix['aaref'], ix['aaalt'], ix['aapos'], ix['genename']",
    "    for line in fh:",
    "        f = line.rstrip('\\n').split('\\t')",
    "        ar, aa = f[AR], f[AA]",
    "        if ar == '.' or aa == '.' or ar == aa:",
    "            continue",
    "        seen = set()",
    "        for g in {x for x in f[GN].split(';') if x and x != '.'}:",
    "            for q in f[AP].split(';'):",
    "                if not q or q == '.':",
    "                    continue",
    "                key = (g, int(q))",
    "                if WT.get(key) == ar and key not in seen:",
    "                    seen.add(key)",
    "                    rows.append((g, int(q), ar, aa, str(f[C]), int(f[P]), f[RF], f[AL]))",
    "",
    "pool = pd.DataFrame(rows, columns=['gene', 'pos_protein', 'wt_aa', 'mut_aa',",
    "                                   'chrom', 'pos_grch38', 'ref', 'alt'])",
    "pool = pool.drop_duplicates()",
    "print('null pool, sequence-consistent base changes:', len(pool))",
    "print('distinct substitutions                    :',",
    "      len(pool[['gene', 'pos_protein', 'wt_aa', 'mut_aa']].drop_duplicates()))",
)


CONTEXT_CELL = code(
    "# One streaming pass over GRCh38 gives every trinucleotide context. The assembly",
    "# ships as plain gzip, not BGZF, so there is no index and no region query.",
    "FASTA = IN / 'genome' / 'Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz'",
    "GENOME_BYTES = 881964081          # DATA_PROVENANCE.md §7",
    "GENOME_URL = ('https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/'",
    "              'Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz')",
    "if not FASTA.exists():",
    "    # 842 MB. Colab pulls it from Ensembl far faster than a home connection can",
    "    # push it to Drive, so this is the preferred route rather than a fallback.",
    "    local = Path('/content/GRCh38.fa.gz')",
    "    if not (local.exists() and local.stat().st_size == GENOME_BYTES):",
    "        print('fetching GRCh38 from Ensembl (~842 MB)...')",
    "        !wget -q --show-progress -O {local} {GENOME_URL}",
    "    FASTA = local",
    "assert FASTA.stat().st_size == GENOME_BYTES, (",
    "    f'{FASTA} is {FASTA.stat().st_size} bytes, expected {GENOME_BYTES}. Ensembl "
    "moved to a new release, or the download was truncated -- either way the contexts "
    "would not be the ones DATA_PROVENANCE §7 pins.')",
    "print('genome:', FASTA)",
    "",
    "# `domains` supplies dom_start: B6's `pos` is the position WITHIN the domain,",
    "# not the protein position, so it has to be converted before any join.",
    "ctx = G.build_context(observed=obs, pool=pool, b6=b6, domains=atlas, fasta=FASTA)",
    "print(json.dumps(ctx['counts'], indent=2))",
    "c = ctx['counts']",
    "print(f\"\\nB6 join retained {c['observed_after_b6_join']}/{c['observed_in']} \"",
    "      f\"observed ({100*c['observed_after_b6_join']/c['observed_in']:.1f}%) and \"",
    "      f\"{c['pool_after_b6_join']}/{c['pool_in']} pool \"",
    "      f\"({100*c['pool_after_b6_join']/c['pool_in']:.1f}%)\")",
    "print('\\nbase changes reaching one amino-acid substitution:')",
    "print(json.dumps(ctx['multiplicity'], indent=2))",
    "",
    "assert ctx['counts']['observed_eligible'] >= 3000, (",
    "    'fewer than 3,000 eligible observed variants -- Part 4 says numbers are shown "
    "and NO verdict is given')",
)


COVERAGE_CELL = code(
    "# Diagnostic, no verdict. The 3a control compares a draw from OUR pool against",
    "# B6's published 9.18 %, which only means something if the two pools are the same",
    "# set. A substitution enters our pool only if dbNSFP carries it on the transcript",
    "# the atlas numbered against, so it is a subset -- this measures how much of one,",
    "# and whether what is missing is milder. If it is, the control cannot pass however",
    "# correct the code is, and the restriction is a limitation of G1, not a bug in it.",
    "assert hasattr(G, 'coverage_report'), (",
    "    'This runtime has a stale g1_core module. Restart the runtime, then run '",
    "    'the notebook from the first cell so the embedded shared code is imported.')",
    "cov = G.coverage_report(ctx, b6, atlas)",
    "print(json.dumps(cov, indent=2))",
    "",
    "d = cov['destabilising_uncovered'] - cov['destabilising_covered']",
    "print(f\"\\nour pool covers {cov['coverage_pct']}% of B6's reachable substitutions\")",
    "print(f\"destabilising: covered {cov['destabilising_covered']:.4f}  \"",
    "      f\"uncovered {cov['destabilising_uncovered']:.4f}  ({d*100:+.2f} pp)\")",
    "print(f\"B6 over all reachable: {cov['destabilising_all_reachable']:.4f} \"",
    "      f\"(published 0.09232)\")",
)


CONTROL_CELL = code(
    "# ---- Controls (Part 10, amended by Part 12). Neither carries a verdict. ----",
    "#",
    "# Part 12: the reproduction check sits on the POOL, not on a draw. Our handling of",
    "# B6 must reproduce its published rate over B6's OWN reachable set -- that is what",
    "# establishes that any difference below is the null's DEFINITION and not our",
    "# arithmetic. Asserting it on a draw from a pool B6 never used cannot establish it,",
    "# because a codon-aware pool sits below 9.2 % by construction.",
    "B6_NULL = 0.09232           # RESULTS_B6.md, frac_destabilising_reachable",
    "rep = cov['destabilising_all_reachable']",
    "print(f'reproduction: {rep:.5f} vs B6 published {B6_NULL:.5f}')",
    "assert abs(rep - B6_NULL) <= 5e-4, (",
    "    f'we get {rep:.5f} over B6\\'s OWN reachable set where B6 published "
    "{B6_NULL:.5f}. This is not the pool-restriction question -- it is the same set "
    "B6 used, so the difference is in how we read B6. Stop and find it.')",
    "print('reproduction passes -- our B6 handling is exact')",
    "",
    "a3a = G.run_arm(ctx, name='3a uniform over substitutions', unit='substitution',",
    "                spectrum=None)",
    "a3b = G.run_arm(ctx, name='3b uniform over base changes', unit='base_change',",
    "                spectrum=None)",
    "for a in (a3a, a3b):",
    "    print(f\"{a['arm']:34s} pool {a['pool_size']:7d}  null median \"",
    "          f\"{a['null_median']:.4f}  observed {a['observed_rate']:.4f}\")",
    "",
    "# Part 12's decomposition, with B6's over-permissive step now at the top.",
    "codon = (a3a['null_median'] - B6_NULL) * 100",
    "mult = (a3b['null_median'] - a3a['null_median']) * 100",
    "print('')",
    "print(f'B6 published   {B6_NULL:.4f}   amino-acid-pair reachability')",
    "print(f'3a             {a3a[\"null_median\"]:.4f}   codon reachability          "
    "({codon:+.2f} pp)')",
    "print(f'3b             {a3b[\"null_median\"]:.4f}   + reachability multiplicity "
    "({mult:+.2f} pp)')",
    "print(f'observed       {a3a[\"observed_rate\"]:.4f}')",
)


MAIN_CELL = code(
    "# Now that the spectrum cell has named this notebook, section 2's threshold can",
    "# be turned into a role. Still nothing chosen here: PRIMARY came from the",
    "# committed pre-registration, not from anything computed below.",
    "IS_PRIMARY = (PRIMARY is None) or PRIMARY.lower().startswith(NOTEBOOK_SPECTRUM)",
    "print(f'this notebook : {NOTEBOOK_SPECTRUM}')",
    "print('role          : '",
    "      + ('co-primary (no primary named)' if PRIMARY is None else",
    "         'PRIMARY' if IS_PRIMARY else 'sensitivity analysis -- no verdict'))",
    "",
    "# ---- The arm that carries the verdict ----",
    "main = G.run_arm(ctx, name=ARM_NAME, unit='base_change', spectrum=spectrum)",
    "obs_spec = G.observed_spectrum(ctx)",
    "fit = G.cosine(spectrum, obs_spec)",
    "",
    "print(json.dumps(main, indent=2))",
    "print(f'\\ncosine fit to the observed 96-channel distribution: {fit:.4f}')",
    "print(f'context alone moves the null by "
    "{(main[\"null_median\"] - a3b[\"null_median\"])*100:+.2f} pp')",
    "",
    "v = G.verdict(main, ALPHA)",
    "print(f'\\nalpha {ALPHA}   p {main[\"p_one_sided_depleted\"]:.5f}   "
    "gap {main[\"gap_pp\"]:+.2f} pp   ->  {v.upper()}')",
    "if not IS_PRIMARY:",
    "    print('This notebook is the SENSITIVITY analysis -- reported, no verdict.')",
)


EXCLUSION_CELL = code(
    "# Part 6 requires this whether or not it changes anything, so that the choice to",
    "# report it is not made after seeing it.",
    "k = ['gene', 'pos_protein', 'wt_aa', 'mut_aa']",
    "b6k = b6.merge(atlas.drop_duplicates(['gene', 'uniprot', 'domain_idx'])",
    "               [['gene', 'uniprot', 'domain_idx', 'dom_start']],",
    "               on=['gene', 'uniprot', 'domain_idx'], how='inner')",
    "b6k['pos_protein'] = b6k['dom_start'].astype(int) + b6k['pos'].astype(int) - 1",
    "b6k['destabilising'] = (b6k[G.CALL] >= G.CALL_THRESHOLD).astype(int)",
    "full = atlas[k].merge(b6k[k + ['destabilising']], on=k, how='inner')",
    "kept = set(map(tuple, ctx['observed'][k].values))",
    "mask = [tuple(r) in kept for r in full[k].values]",
    "inc, exc = full[mask], full[[not m for m in mask]]",
    "print(f'included {len(inc):5d}  destabilising {inc[\"destabilising\"].mean():.4f}')",
    "print(f'excluded {len(exc):5d}  destabilising "
    "{exc[\"destabilising\"].mean():.4f}' if len(exc) else 'excluded     0')",
    "excl = {'n_included': int(len(inc)), 'n_excluded': int(len(exc)),",
    "        'rate_included': float(inc['destabilising'].mean()),",
    "        'rate_excluded': float(exc['destabilising'].mean()) if len(exc) else None}",
)


WRITE_CELL = code(
    "payload = {'notebook': NOTEBOOK, 'spectrum': NOTEBOOK_SPECTRUM,",
    "           'primary_named_in_prereg': PRIMARY, 'is_primary': bool(IS_PRIMARY),",
    "           'alpha': ALPHA, 'verdict': v,",
    "           'main': main, 'control_3a': a3a, 'control_3b': a3b,",
    "           'b6_published_null': B6_NULL,",
    "           'cosine_fit_to_observed': fit,",
    "           'counts': ctx['counts'], 'multiplicity': ctx['multiplicity'],",
    "           'exclusion_check': excl,",
    "           'spectrum_used': {k: float(x) for k, x in spectrum.items()},",
    "           'observed_spectrum': {k: float(x) for k, x in obs_spec.items()},",
    "           'opportunity': ctx['opportunity']}",
    "G.write_metrics(OUT / f'metrics_{NOTEBOOK}.json', payload)",
    "print('wrote', OUT / f'metrics_{NOTEBOOK}.json')",
    "",
    "# Part 7: the spectrum is published as normalised proportions, never raw counts,",
    "# and the per-variant tables stay on the laptop.",
    "lines = [f'# {NOTEBOOK} — machine-written results', '',",
    "         f'Spectrum: **{NOTEBOOK_SPECTRUM}**. Role: "
    "**{\"primary\" if IS_PRIMARY else \"sensitivity\"}**. alpha = {ALPHA}.', '',",
    "         '| arm | unit | pool | null median | observed | gap (pp) | p |',",
    "         '|---|---|---|---|---|---|---|']",
    "for a in (a3a, a3b, main):",
    "    lines.append(f\"| {a['arm']} | {a['unit']} | {a['pool_size']} | \"",
    "                 f\"{a['null_median']:.4f} | {a['observed_rate']:.4f} | \"",
    "                 f\"{a['gap_pp']:+.2f} | {a['p_one_sided_depleted']:.5f} |\")",
    "lines += ['', f'**Verdict ({NOTEBOOK_SPECTRUM}): {v}**', '',",
    "          f'Cosine fit to the observed 96-channel distribution: {fit:.4f}.', '',",
    "          f'g1_core sha256 `{G.self_sha256()[:16]}...`, seed {G.SEED}, "
    "{G.N_DRAWS} draws.']",
    "(OUT / f'RESULTS_{NOTEBOOK}.md').write_text('\\n'.join(lines))",
    "print('wrote', OUT / f'RESULTS_{NOTEBOOK}.md')",
)


def spectrum_cell(which: str):
    if which == 'observed':
        return code(
            "# ======== THE ONLY CELL THAT DIFFERS BETWEEN G1a AND G1b ========",
            "# G1a -- the 96-channel distribution of the variants under study.",
            "#",
            "# Part 9.4, stated before any result: this spectrum is estimated from the",
            "# same variants whose damage is being tested, so it is NOT independent of",
            "# the test set. G1b exists because of that, and 'which is better' is judged",
            "# on biological fit and robustness -- never on which p-value is smaller.",
            "NOTEBOOK = 'G1a'",
            "NOTEBOOK_SPECTRUM = 'observed'",
            "ARM_NAME = '1 observed spectrum'",
            "spectrum = G.observed_spectrum(ctx)",
            "",
            "supp = ctx['observed']['channel'].value_counts()",
            "print(f'channels with any observed variant: {len(supp)} of 96')",
            "print(f'channels with fewer than 10       : {int((supp < 10).sum())}')",
            "print('\\ntop channels:'); print(supp.head(10).to_string())",
        )
    return code(
        "# ======== THE ONLY CELL THAT DIFFERS BETWEEN G1a AND G1b ========",
        "# G1b -- an equal mixture of the clock-like COSMIC signatures SBS1 and SBS5,",
        "# fixed externally and estimated from nothing in this project.",
        "#",
        "# Independent of the test set, at the price of assuming clock-like processes",
        "# dominate across the tumour types the atlas aggregates. That is a real",
        "# assumption and it is why this arm is not automatically the safer one.",
        "NOTEBOOK = 'G1b'",
        "NOTEBOOK_SPECTRUM = 'cosmic'",
        "ARM_NAME = '2 COSMIC SBS1+SBS5'",
        "SIGS = IN / 'signatures' / 'COSMIC_v3.6_SBS_GRCh38.txt'",
        "assert SIGS.exists(), f'{SIGS} not found'",
        "spectrum = G.cosmic_spectrum(SIGS, sigs=('SBS1', 'SBS5'))",
        "print('COSMIC SBS1+SBS5, top channels:')",
        "print(spectrum.sort_values(ascending=False).head(10).to_string())",
    )


def cells(which: str):
    a = which == 'observed'
    return [
        md(f"# G1{'a' if a else 'b'} — cancer-variant depletion against a "
           f"{'variant-derived' if a else 'COSMIC'} mutational spectrum",
           "",
           "**Pre-registered in `docs/preregistration/G1.md`, committed before this "
           "notebook was written.** Every threshold, every arm, and the reading of the "
           "result come from that file.",
           "",
           "B6 reported that observed SH3 cancer variants are depleted of predicted "
           "fold-breaking substitutions — 5.93 % against 9.18 % expected — and said "
           "plainly what the test could not do: *mutational context was not modelled, "
           "and a trinucleotide-aware null is needed before claiming selection.* "
           "This is that test.",
           "",
           "This notebook is one of a pair. It differs from its twin in **one cell** — "
           "the spectrum — and shares everything else as code, not as intention: "
           "`g1_core.py` is embedded below byte-for-byte and its SHA-256 is asserted, "
           "so any difference in the result is attributable to the spectrum rather "
           "than to an implementation slip.",
           "",
           "| | |",
           "|---|---|",
           "| Spectrum | " + ("the 96-channel distribution of the variants under study"
                              if a else "COSMIC SBS1 + SBS5, equal mixture") + " |",
           "| Independent of the test set? | " + ("**no** — see Part 9.4" if a else "yes") + " |",
           "| Predictions | B6's frozen virtual DMS, 22 Sep 2026. Never re-fitted |",
           "| The call | `fold_lo >= 1`, exactly as B3 defined it |"),
        SETUP,
        md("## 1 — The shared machinery",
           "",
           "`tools/g1_core.py`, written to disk from a string this generator read at "
           "build time. The hash assertion is the point: without it, 'both notebooks "
           "run the same code' would be a claim rather than a check."),
        CORE_CELL,
        md("## 2 — Which threshold applies",
           "",
           "Part 9.3 lets the choice of primary spectrum be deferred, and charges for "
           "it in advance. The notebook **reads the pre-registration** and takes "
           "α = 0.025 if a line `PRIMARY SPECTRUM: …` is there, or α = 0.0125 for both "
           "notebooks if it is not. Choosing after seeing a p-value is therefore not "
           "possible — by then the file is already committed.",
           "",
           "Which role *this* notebook plays needs its identity, and the identity is "
           "set in the spectrum cell — the single cell that differs between G1a and "
           "G1b. Naming it here as well would make two cells differ, and the whole "
           "comparison rests on exactly one differing. So the threshold is read here "
           "and the role is resolved in §8."),
        ALPHA_CELL,
        md("## 3 — The pinned inputs",
           "",
           "Three files, none of them re-fitted here: B6's virtual DMS, the verified "
           "coordinate table from `tools/g1_coordinates.py`, and X1's dbNSFP subset, "
           "which is the only source of a genomic coordinate for every *possible* "
           "in-domain missense SNV — that is, for the null pool."),
        DATA_CELL,
        md("## 4 — Building the null pool",
           "",
           "Part 10: the null draws **base changes**, not amino-acid substitutions. One "
           "amino-acid change can be reached by several base changes, each with its own "
           "trinucleotide context, so a context-weighted null is meaningless at the "
           "amino-acid level.",
           "",
           "The pool is aligned on the atlas's own UniProt accession, the same way the "
           "observed set was. Taking element `[0]` of dbNSFP's per-transcript fields is "
           "the defect that cost X1 a run."),
        POOL_CELL,
        md("## 5 — Trinucleotide context",
           "",
           "One streaming pass over GRCh38 for both pools at once. `add_context` "
           "asserts that the reference base agrees at every position — the one number "
           "this reduction does not control."),
        CONTEXT_CELL,
        md("## 5b — Is our pool B6's pool?",
           "",
           "A diagnostic with no verdict, and it has to come before the control.",
           "",
           "A substitution enters our null pool only if dbNSFP carries it on the "
           "transcript the atlas numbered its residues against. That makes the pool a "
           "**subset** of the SNV-reachable substitutions B6 drew from, and the 3a "
           "control compares a draw from *our* pool against *B6's* published 9.18 %.",
           "",
           "If the substitutions we lack are systematically milder, 3a cannot reproduce "
           "9.18 % however correct the code is — and that is a limitation of G1 to be "
           "reported, not a defect to be fixed. This cell measures it either way."),
        COVERAGE_CELL,
        md("## 6 — The controls, which decide whether anything below is interpretable",
           "",
           "**3a must reproduce B6's 9.18 %.** If it does not, this implementation "
           "differs from B6 in something that is not the trinucleotide weighting, and "
           "the spectrum arm means nothing. The notebook stops.",
           "",
           "**3b is not an error if it differs from 3a.** That difference is "
           "reachability multiplicity — how many distinct base changes reach each "
           "amino-acid substitution — isolated from sequence context, and it is "
           "reported as its own number.",
           "",
           "```",
           "3a  uniform over substitutions   -- B6's null",
           "3b  uniform over base changes    -- + reachability multiplicity",
           "1/2 spectrum-weighted            -- + trinucleotide context",
           "```"),
        CONTROL_CELL,
        md("## 7 — The spectrum",
           "",
           "The one cell that differs between the two notebooks."),
        spectrum_cell(which),
        md("## 8 — The test",
           "",
           "One-sided, observed **below** null, the direction declared in Part 6. The "
           "verdict label comes from `g1_core.verdict()` so that Part 11's 1.63 pp "
           "boundary between *survives* and *shrinks but survives* is applied by code "
           "rather than by hand."),
        MAIN_CELL,
        md("## 9 — Who was excluded",
           "",
           "6.2 % of the atlas has no unambiguous coordinate, and the exclusion "
           "plausibly correlates with genes carrying many transcripts. Part 6 requires "
           "this comparison to be **computed and reported whether or not it changes "
           "anything** — it is not a condition on the verdict, because the rule for "
           "that would have to be invented after seeing it."),
        EXCLUSION_CELL,
        md("## 10 — Write the machine-written record",
           "",
           "Part 7: the spectrum is published as normalised proportions, never raw "
           "counts; the per-variant tables stay on the laptop. Nothing in "
           "`RESULTS_*.md` is typed by hand; the interpretation goes in `ANALYSIS_G1.md` "
           "once both notebooks and `tools/g1_compare.py` have run."),
        WRITE_CELL,
    ]


NOTEBOOKS = {
    'G1a_observed_spectrum': cells('observed'),
    'G1b_cosmic_spectrum': cells('cosmic'),
}


def check_cell_order(cs) -> None:
    """Every name must be bound by an earlier cell, or by an earlier line in its own.

    Cells run top to bottom, and a generator that assembles them out of fragments
    makes it easy to read a name one cell before it is written -- which is exactly
    what happened: the alpha cell used NOTEBOOK_SPECTRUM, which the spectrum cell
    five cells later defines. Counting differing cells did not catch it, so this does.
    """
    def binds(tree) -> set:
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
                out.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(n.name)
            elif isinstance(n, ast.arg):
                out.add(n.arg)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                out.update((a.asname or a.name).split('.')[0] for a in n.names)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                out.add(n.name)
        return out

    bound = set(dir(builtins)) | {'get_ipython', 'In', 'Out', '_'}
    for i, c in enumerate(x for x in cs if x['cell_type'] == 'code'):
        # `!cmd` is IPython, not Python; blank those lines before parsing.
        src = '\n'.join('' if l.lstrip().startswith('!') else l
                        for l in c['source'].splitlines())
        tree = ast.parse(src)
        # A name bound anywhere in this cell counts as available: within one cell a
        # reader sees the order, and comprehension and loop targets would otherwise
        # read as forward references. The cross-cell case is the one a generator
        # creates by assembling fragments, and it is the one this catches.
        here = bound | binds(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                assert n.id in here, (
                    f'code cell {i} reads `{n.id}` (line {n.lineno}) but no earlier '
                    'cell binds it; the notebook would raise NameError there')
        bound = here

if __name__ == '__main__':
    out = HERE.parent / 'notebooks'
    out.mkdir(parents=True, exist_ok=True)
    for name, cs in NOTEBOOKS.items():
        p = out / f'{name}.ipynb'
        p.write_text(json.dumps(build(cs), indent=1))
        print(f'wrote {p}  ({len(cs)} cells)')
    print(f'g1_core.py sha256 {CORE_SHA}')

    # The two notebooks must differ in exactly one code cell (Part 9.1).
    a = [c['source'] for c in NOTEBOOKS['G1a_observed_spectrum'] if c['cell_type'] == 'code']
    b = [c['source'] for c in NOTEBOOKS['G1b_cosmic_spectrum'] if c['cell_type'] == 'code']
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert len(a) == len(b) and len(diff) == 1, (
        f'the notebooks differ in {len(diff)} code cells, expected exactly 1 '
        '(the spectrum); anything else breaks the comparison')
    print(f'verified: {len(a)} code cells each, differing in exactly one (#{diff[0]})')

    for name, cs in NOTEBOOKS.items():
        check_cell_order(cs)
    print('verified: no cell reads a name an earlier cell has not bound')

    # The embedded core is a raw string literal, so verify it survives the round
    # trip -- otherwise the hash assertion fails on Colab rather than here.
    for name in NOTEBOOKS:
        src = next(c['source'] for c in json.loads((out / f'{name}.ipynb').read_text())['cells']
                   if c['cell_type'] == 'code' and 'core_src' in c['source'])
        ns: dict = {}
        exec("core_src = r'''" + src.split("core_src = r'''", 1)[1].rsplit("'''", 1)[0]
             + "'''", ns)
        got = hashlib.sha256(ns['core_src'].encode()).hexdigest()
        assert got == CORE_SHA, (
            f'{name} embeds a g1_core.py that hashes to {got}, not {CORE_SHA}; the '
            'notebook would abort on Colab')
    print('verified: both notebooks embed g1_core.py byte-for-byte')
