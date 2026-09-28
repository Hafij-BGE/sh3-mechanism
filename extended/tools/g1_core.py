"""
G1 — shared machinery for both spectrum notebooks.

`docs/preregistration/G1.md` Part 9.1 requires that the eligible variant set, the
domain-specific opportunity counts, the B6 predictions, the draw procedure, the test
statistic and the seed be *shared code*, not a shared intention: two notebooks that
merely look alike would leave any difference in the result ambiguous between the
spectrum and an implementation slip.

So everything except the spectrum lives here.  `G1a_observed_spectrum` and
`G1b_cosmic_spectrum` differ in exactly one call:

    spectrum = g1_core.observed_spectrum(ctx)      # G1a
    spectrum = g1_core.cosmic_spectrum(ctx, path)  # G1b

Both notebooks embed this file byte-for-byte and assert its SHA-256, so "identical
machinery" is checkable rather than asserted.

What the arms are (Part 10):

    3a  uniform over amino-acid substitutions  -- B6's null; MUST reproduce 9.18 %
    3b  uniform over base changes              -- + reachability multiplicity
    1/2 spectrum-weighted over base changes    -- + trinucleotide context

Only 1/2 carries a verdict.  3a and 3b carry none; they exist so that any change in
the null rate can be attributed to a step rather than asserted.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260928
N_DRAWS = 10_000
CALL = 'fold_lo'          # destabilising iff fold_lo >= 1, exactly as B3 defined it
CALL_THRESHOLD = 1.0

PURINES = {'A', 'G'}
COMP = str.maketrans('ACGTN', 'TGCAN')


# ─────────────────────────────────────────────────────────────────────────────
# 96-channel classification
# ─────────────────────────────────────────────────────────────────────────────

def channels() -> list[str]:
    """The 96 SBS channels in COSMIC's own row order."""
    out = []
    for ref in 'CT':
        for alt in 'ACGT':
            if alt == ref:
                continue
            for up in 'ACGT':
                for down in 'ACGT':
                    out.append(f'{up}[{ref}>{alt}]{down}')
    return sorted(out)


def to_channel(up: str, ref: str, alt: str, down: str) -> str | None:
    """Pyrimidine-referenced 96-channel label, or None if any base is not ACGT.

    A mutation and its reverse complement are the same event observed from the
    other strand, so channels are defined with a C or T in the middle.
    """
    if ref in PURINES:
        up, ref, alt, down = (down.translate(COMP), ref.translate(COMP),
                              alt.translate(COMP), up.translate(COMP))
    if ref not in 'CT' or alt not in 'ACGT' or alt == ref:
        return None
    if up not in 'ACGT' or down not in 'ACGT':
        return None
    return f'{up}[{ref}>{alt}]{down}'


# ─────────────────────────────────────────────────────────────────────────────
# Genome
# ─────────────────────────────────────────────────────────────────────────────

def read_flanks(fasta: Path, positions: dict[str, set[int]]) -> dict[tuple, str]:
    """Bases at every position in `positions`, by one streaming pass.

    The Ensembl primary assembly ships as plain gzip, not BGZF, so there is no
    random access and no index; one pass is the whole cost.  We ask for pos-1,
    pos and pos+1 together so the trinucleotide context comes out of the same pass.
    """
    want = {c: set() for c in positions}
    for c, ps in positions.items():
        for p in ps:
            want[c].update((p - 1, p, p + 1))

    got: dict[tuple, str] = {}
    cur, off, targets, maxpos = None, 0, None, 0
    with gzip.open(fasta, 'rt') as fh:
        for line in fh:
            if line[0] == '>':
                cur = line[1:].split()[0]
                off, targets = 0, want.get(cur)
                maxpos = max(targets) if targets else 0
                continue
            if not targets:
                continue
            if off >= maxpos:
                off += len(line) - 1
                continue
            s = line.rstrip('\n')
            lo = off + 1
            for p in range(lo, off + len(s) + 1):
                if p in targets:
                    got[(cur, p)] = s[p - lo].upper()
            off += len(s)
    return got


def add_context(df: pd.DataFrame, flanks: dict[tuple, str]) -> pd.DataFrame:
    """Attach `up`, `down` and `channel`; assert the reference base agrees.

    The reference check is the one number this reduction does not control, and X1
    is the reason it is demanded.
    """
    key = list(zip(df['chrom'], df['pos_grch38']))
    ref_seen = np.array([flanks.get((c, p), 'N') for c, p in key])
    bad = int((ref_seen != df['ref'].to_numpy()).sum())
    assert bad == 0, (
        f'{bad} rows whose GRCh38 base disagrees with the recorded ref allele; '
        'the coordinates are wrong and G1 must not proceed')

    up = np.array([flanks.get((c, p - 1), 'N') for c, p in key])
    down = np.array([flanks.get((c, p + 1), 'N') for c, p in key])
    out = df.copy()
    out['up'], out['down'] = up, down
    out['channel'] = [to_channel(u, r, a, d) for u, r, a, d
                      in zip(up, df['ref'], df['alt'], down)]
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Pools
# ─────────────────────────────────────────────────────────────────────────────

def wt_by_position(b6: pd.DataFrame, domains: pd.DataFrame) -> dict:
    """The atlas's own wild-type residue at every in-domain protein position.

    This is the key a dbNSFP row has to satisfy to enter the null pool.  Matching
    the UniProt *accession* is not enough: dbNSFP lists one `aapos` per transcript,
    and the transcript it carries for an accession can be a different isoform with
    different numbering.  Measured against the release, 31,458 of 132,704
    accession-matched rows (23.7 %) land on a position whose residue disagrees with
    the atlas -- and it is all-or-nothing per gene, which is what a frame shift
    looks like.

    Requiring `aaref` to equal the atlas residue is the rule `g1_coordinates.py`
    already used for the observed set, so pool and observed are built alike.  A null
    drawn under a different rule from the thing it is a null for is not a null.
    """
    x = b6.merge(domains.drop_duplicates(['gene', 'uniprot', 'domain_idx'])
                        [['gene', 'uniprot', 'domain_idx', 'dom_start']],
                 on=['gene', 'uniprot', 'domain_idx'], how='inner')
    pos = x['dom_start'].astype(int) + x['pos'].astype(int) - 1
    return dict(zip(zip(x['gene'], pos), x['wt_aa']))


def build_context(*, observed: pd.DataFrame, pool: pd.DataFrame,
                  b6: pd.DataFrame, domains: pd.DataFrame, fasta: Path) -> dict:
    """Everything both notebooks share.

    observed : atlas variants with one verified GRCh38 coordinate each
    pool     : every in-domain missense base change, from dbNSFP
    b6       : the frozen virtual DMS -- predictions, never re-fitted
    domains  : the atlas, for dom_start (see below)

    **B6's `pos` is the position WITHIN THE DOMAIN, not the protein position.**
    B6 indexes its per-position arrays as `LO[domain_key][pos - 1]` and computes
    `rel_pos = pos / dom_len`, so `pos` runs 1..dom_len. Joining it to a protein
    position matches only where the domain happens to start at residue 1 -- 147 of
    the 6,884 atlas variants -- and silently drops the rest. It is converted here:

        pos_protein = dom_start + pos - 1

    verified against the atlas's own `pos_in_domain` for all 6,884 rows.
    """
    b6 = b6.copy()
    dom = (domains.drop_duplicates(['gene', 'uniprot', 'domain_idx'])
                  [['gene', 'uniprot', 'domain_idx', 'dom_start']])
    n_b6 = len(b6)
    b6 = b6.merge(dom, on=['gene', 'uniprot', 'domain_idx'], how='inner',
                  validate='m:1')
    assert len(b6) >= 0.95 * n_b6, (
        f'only {len(b6)} of {n_b6} B6 rows found a dom_start in the atlas; the '
        'domain tables have diverged and every protein position below would be wrong')
    b6['pos_protein'] = b6['dom_start'].astype(int) + b6['pos'].astype(int) - 1
    call = (b6[CALL] >= CALL_THRESHOLD).astype(np.int8)
    if 'destabilising' in b6:
        # B6 ships its own column. Recomputing it from fold_lo and checking the two
        # agree costs nothing and catches a wrong file or a changed threshold.
        disagree = int((call != b6['destabilising'].astype(np.int8)).sum())
        assert disagree == 0, (
            f'{disagree} rows where fold_lo >= 1 disagrees with B6\'s own '
            "`destabilising` column; this is not the frozen call B3 defined")
    b6['destabilising'] = call
    keys = ['gene', 'pos_protein', 'wt_aa', 'mut_aa']
    # A residue can sit in two overlapping domain annotations of the same gene (X0
    # found 3,856 such rows, from dual Pfam entries), and each gets its own B6
    # prediction. Deduplicating keeps the first, so record how often that happens
    # and whether the collapsed rows would have been called differently -- a silent
    # pick between disagreeing predictions is the thing to catch, not the dedup.
    g = b6.groupby(keys, sort=False)['destabilising']
    dup_keys = int((g.size() > 1).sum())
    dup_conflict = int((g.nunique() > 1).sum())
    b6k = b6[keys + ['domain_key', 'destabilising', CALL]].drop_duplicates(keys)

    n_obs_in, n_pool_in = len(observed), len(pool)

    # Why anything drops, recorded rather than argued. build_pool only emits a row
    # where the atlas residue equals dbNSFP's aaref, so gene, pos_protein and wt_aa
    # already agree by construction and B6 holds all 19 non-wildtype standard
    # residues at every position it covers. A drop can therefore only come from
    # mut_aa, and this says which values caused it.
    _lost = pool.merge(b6k[keys], on=keys, how='left', indicator=True)
    _lost = _lost[_lost['_merge'] == 'left_only']
    drop_mut_aa = _lost['mut_aa'].value_counts().head(25).to_dict()
    _std = set('ACDEFGHIKLMNPQRSTVWY')
    drop_nonstandard = int((~_lost['mut_aa'].isin(_std)).sum())

    observed = observed.merge(b6k, on=keys, how='inner', validate='m:1')
    pool = pool.merge(b6k, on=keys, how='inner', validate='m:1')

    # X0's lesson, restated: an inner merge that loses rows loses them silently, and
    # a smaller table still looks plausible. B6 scored all 19 substitutions at every
    # position of all 310 atlas domains, so every atlas variant MUST be in it -- and
    # when the join key was wrong this retained 187 of 6,456 without complaint.
    assert len(observed) >= 0.95 * n_obs_in, (
        f'the B6 join kept only {len(observed)} of {n_obs_in} observed variants. B6 '
        'covers every substitution in every atlas domain, so this cannot be a real '
        'absence -- the join key is wrong. Check that B6\'s domain-relative `pos` was '
        'converted to a protein position.')
    assert len(pool) >= 10 * len(observed), (
        f'the null pool holds {len(pool)} candidates for {len(observed)} observed '
        'variants, too few for a domain-matched draw to have anything to choose from')

    pos = {}
    for d in (observed, pool):
        for c, p in zip(d['chrom'], d['pos_grch38']):
            pos.setdefault(c, set()).add(int(p))
    flanks = read_flanks(fasta, pos)
    observed, pool = add_context(observed, flanks), add_context(pool, flanks)

    # Part 10: a base change with no definable channel (N in the flank) cannot be
    # weighted by any spectrum, so it leaves both the pool and the observed set --
    # dropping it from one only would compare different populations.
    n_obs_ctx, n_pool_ctx = len(observed), len(pool)
    observed = observed[observed['channel'].notna()].reset_index(drop=True)
    pool = pool[pool['channel'].notna()].reset_index(drop=True)

    # 3a's unit: one item per amino-acid substitution, not per base change.
    sub = ['domain_key', 'pos_protein', 'wt_aa', 'mut_aa']
    subs = pool.drop_duplicates(sub).reset_index(drop=True)
    mult = pool.groupby(sub, sort=False).size()

    ctx = {
        'observed': observed, 'pool': pool, 'subs': subs,
        'counts': {
            'observed_in': n_obs_in, 'pool_in': n_pool_in,
            'observed_after_b6_join': n_obs_ctx, 'pool_after_b6_join': n_pool_ctx,
            'observed_eligible': len(observed), 'pool_base_changes': len(pool),
            'pool_substitutions': len(subs),
            'domains_observed': observed['domain_key'].nunique(),
            'domains_pool': pool['domain_key'].nunique(),
            'pool_dropped': int(n_pool_in - len(pool)),
            'pool_dropped_nonstandard_mut_aa': drop_nonstandard,
            'b6_keys_in_two_domains': dup_keys,
            'b6_keys_whose_domains_disagree': dup_conflict,
        },
        'multiplicity': {int(k): int(v) for k, v in mult.value_counts().items()},
        'pool_drop_reason_mut_aa': drop_mut_aa,
        'opportunity': pool['channel'].value_counts().reindex(channels()).fillna(0)
                           .astype(int).to_dict(),
    }
    return ctx


def coverage_report(ctx: dict, b6: pd.DataFrame, domains: pd.DataFrame) -> dict:
    """Which of B6's reachable substitutions have a coordinate, and are they milder?

    The 3a control compares a draw from OUR pool against B6's published 9.18 %, and
    that only means something if the two pools are the same set.  They are not: a
    substitution enters our pool only if dbNSFP carries it on the transcript the
    atlas numbered against.  This measures the gap and, more importantly, whether
    what is missing differs in predicted damage -- because if it does, the control
    cannot pass however correct the code is, and the restriction is a limitation of
    G1 rather than a bug in it.

    Carries no verdict.  It is a diagnostic, run before the control.
    """
    b6 = b6.merge(domains.drop_duplicates(['gene', 'uniprot', 'domain_idx'])
                         [['gene', 'uniprot', 'domain_idx', 'dom_start']],
                  on=['gene', 'uniprot', 'domain_idx'], how='inner')
    b6 = b6.copy()
    b6['pos_protein'] = b6['dom_start'].astype(int) + b6['pos'].astype(int) - 1
    b6['destabilising'] = (b6[CALL] >= CALL_THRESHOLD).astype(np.int8)
    reach = b6[b6['snv_reachable']] if 'snv_reachable' in b6 else b6

    keys = ['gene', 'pos_protein', 'wt_aa', 'mut_aa']
    have = set(map(tuple, ctx['pool'][keys].drop_duplicates().to_numpy()))
    covered = np.array([tuple(r) in have for r in reach[keys].to_numpy()])

    out = {
        'b6_reachable': int(len(reach)),
        'covered': int(covered.sum()),
        'uncovered': int((~covered).sum()),
        'coverage_pct': round(100 * covered.mean(), 2),
        'destabilising_covered': round(float(reach['destabilising'][covered].mean()), 5),
        'destabilising_uncovered': round(
            float(reach['destabilising'][~covered].mean()), 5),
        'destabilising_all_reachable': round(float(reach['destabilising'].mean()), 5),
    }

    # Where does the shortfall sit -- whole domains, or positions inside them?
    per = (reach.assign(covered=covered).groupby('domain_key')['covered']
                .agg(['mean', 'size']))
    out['domains_total'] = int(len(per))
    out['domains_fully_absent'] = int((per['mean'] == 0).sum())
    out['domains_below_half'] = int((per['mean'] < 0.5).sum())
    out['domain_coverage_median'] = round(float(per['mean'].median()), 4)

    # ...and are the uncovered ones at the domain edges?
    edge = reach['pos'].astype(int)
    out['mean_pos_in_domain_covered'] = round(float(edge[covered].mean()), 2)
    out['mean_pos_in_domain_uncovered'] = round(float(edge[~covered].mean()), 2)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Spectra -- the only thing the two notebooks do differently
# ─────────────────────────────────────────────────────────────────────────────

def _normalise(s: pd.Series) -> pd.Series:
    s = s.reindex(channels()).fillna(0.0).astype(float)
    assert s.sum() > 0, 'spectrum is empty'
    return s / s.sum()


def observed_spectrum(ctx: dict) -> pd.Series:
    """G1a: the 96-channel distribution of the variants under study.

    Part 6 and 9.4: this is estimated from the same variants whose damage is being
    tested, so it is NOT independent of the test set.  It is here because it
    reproduces whatever mixture of processes the atlas aggregates without having to
    estimate it -- and G1b exists because of the dependence, not in spite of it.
    """
    return _normalise(ctx['observed']['channel'].value_counts())


def cosmic_spectrum(path: Path, sigs=('SBS1', 'SBS5')) -> pd.Series:
    """G1b: an equal mixture of clock-like COSMIC signatures, fixed externally.

    Independent of the test set, at the price of assuming clock-like processes
    dominate across the tumour types the atlas aggregates.  Neither spectrum is
    automatically the safer choice; Part 9.4 says how they are compared.
    """
    t = pd.read_csv(path, sep='\t').set_index('Type')
    missing = [s for s in sigs if s not in t.columns]
    assert not missing, f'{missing} absent from the COSMIC table'
    return _normalise(t[list(sigs)].mean(axis=1))


def cosine(a: pd.Series, b: pd.Series) -> float:
    """Part 9.4's fit measure: how close an assumed spectrum is to the observed one."""
    x, y = _normalise(a).to_numpy(), _normalise(b).to_numpy()
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))


# ─────────────────────────────────────────────────────────────────────────────
# The draw
# ─────────────────────────────────────────────────────────────────────────────

def _draw(pool: pd.DataFrame, need: dict[str, int], weight: np.ndarray | None,
          rng: np.random.Generator) -> np.ndarray:
    """Destabilising count per draw, matched to the observed per-domain counts.

    Sampling is WITH replacement.  Each domain's pool (hundreds of candidates) is
    far larger than its observed count (tens), so the difference from B6's draw is
    negligible -- and 3a is the arm that has to prove that, by reproducing 9.18 %.
    """
    total = np.zeros(N_DRAWS, dtype=np.int32)
    dest = pool['destabilising'].to_numpy()
    for dom, idx in pool.groupby('domain_key', sort=False).indices.items():
        n = need.get(dom, 0)
        if n == 0:
            continue
        p = None
        if weight is not None:
            w = weight[idx]
            if w.sum() <= 0:
                continue          # no candidate in this domain carries any weight
            p = w / w.sum()
        picked = rng.choice(idx, size=(N_DRAWS, n), replace=True, p=p)
        total += dest[picked].sum(axis=1, dtype=np.int32)
    return total


def run_arm(ctx: dict, *, name: str, unit: str, spectrum: pd.Series | None) -> dict:
    """One arm.  `unit` is 'base_change' or 'substitution' (Part 10)."""
    obs = ctx['observed']
    pool = ctx['pool'] if unit == 'base_change' else ctx['subs']
    need = obs['domain_key'].value_counts().to_dict()

    weight = None
    if spectrum is not None:
        assert unit == 'base_change', 'a spectrum can only weight base changes'
        weight = spectrum.reindex(pool['channel']).to_numpy(dtype=float)

    rng = np.random.default_rng(SEED)
    counts = _draw(pool, need, weight, rng)
    n = len(obs)
    null = counts / n
    observed_rate = float(obs['destabilising'].mean())

    # one-sided, observed BELOW null -- the direction was declared in Part 6
    p = float((np.sum(counts <= obs['destabilising'].sum()) + 1) / (N_DRAWS + 1))
    return {
        'arm': name, 'unit': unit, 'n_observed': n, 'pool_size': len(pool),
        'observed_rate': observed_rate,
        'null_median': float(np.median(null)),
        'null_mean': float(null.mean()), 'null_sd': float(null.std(ddof=1)),
        'null_ci95': [float(np.percentile(null, 2.5)),
                      float(np.percentile(null, 97.5))],
        'gap_pp': float((np.median(null) - observed_rate) * 100),
        'p_one_sided_depleted': p,
        'draws': N_DRAWS, 'seed': SEED,
    }


def verdict(arm: dict, alpha: float) -> str:
    """Part 4's three outcomes.  The middle one is the one most exposed to hindsight,
    so it is named rather than left to prose."""
    if arm['p_one_sided_depleted'] >= alpha:
        return 'vanishes'
    return 'survives' if arm['gap_pp'] >= 0.5 * 3.25 else 'shrinks_but_survives'


def self_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def write_metrics(path: Path, payload: dict) -> None:
    payload = dict(payload, g1_core_sha256=self_sha256(), seed=SEED, draws=N_DRAWS)
    Path(path).write_text(json.dumps(payload, indent=2))
