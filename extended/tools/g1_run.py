#!/usr/bin/env python3
"""
G1 — run both spectra locally, end to end.

G1 needs no GPU and every input is on the laptop, so there is no reason to run it
on Colab.  This is the same pipeline the notebooks run, calling the same
`g1_core.py`, so a result obtained here and a result obtained there are the same
computation -- and this one can be iterated on without a re-upload.

    python3 tools/g1_run.py --root . --out results/G1_mutational_context

Writes metrics_G1a.json and metrics_G1b.json, which `g1_compare.py` then reads.
"""
import argparse, gzip, json, sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1_core as G


def build_pool(dbnsfp: Path, wt: dict) -> pd.DataFrame:
    """Every in-domain missense base change whose reference residue matches the atlas.

    dbNSFP lists one aapos per transcript and the transcript it carries for a given
    UniProt accession can be a different isoform, so accession matching admits rows
    that are frame-shifted relative to the atlas.  Requiring aaref to equal the
    atlas residue is the rule g1_coordinates.py used for the observed set.
    """
    rows = []
    with gzip.open(dbnsfp, 'rt') as fh:
        ix = {c: j for j, c in enumerate(fh.readline().rstrip('\n').split('\t'))}
        C, P, RF, AL = ix['#chr'], ix['pos(1-based)'], ix['ref'], ix['alt']
        AR, AA, AP, GN = ix['aaref'], ix['aaalt'], ix['aapos'], ix['genename']
        for line in fh:
            f = line.rstrip('\n').split('\t')
            ar, aa = f[AR], f[AA]
            if ar == '.' or aa == '.' or ar == aa:
                continue
            seen = set()
            for g in {x for x in f[GN].split(';') if x and x != '.'}:
                for q in f[AP].split(';'):
                    if not q or q == '.':
                        continue
                    k = (g, int(q))
                    if wt.get(k) == ar and k not in seen:
                        seen.add(k)
                        rows.append((g, int(q), ar, aa, str(f[C]), int(f[P]),
                                     f[RF], f[AL]))
    return pd.DataFrame(rows, columns=['gene', 'pos_protein', 'wt_aa', 'mut_aa',
                                       'chrom', 'pos_grch38', 'ref', 'alt']
                        ).drop_duplicates()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--frozen', default='../results')
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    b6 = pd.read_parquet(Path(a.frozen) /
                         'B6_virtual_saturation_mutagenesis/sh3_virtual_dms.parquet')
    assert len(b6) == 366168, f'B6 has {len(b6)} rows, expected 366,168'
    atlas = pd.read_csv(root / 'input/frozen/results/SH3_cancer_master.tsv', sep='\t')
    assert len(atlas) == 6884
    bad = int((atlas['pos_protein'] - atlas['dom_start'] + 1
               != atlas['pos_in_domain']).sum())
    assert bad == 0, f'{bad} atlas rows fail the domain-offset identity'

    obs = pd.read_csv(out / 'atlas_grch38_coordinates.tsv', sep='\t')
    obs['pos_protein'] = obs['pos_protein'].astype(int)
    print(f'B6 {len(b6)}  atlas {len(atlas)}  observed {len(obs)}', file=sys.stderr)

    wt = G.wt_by_position(b6, atlas)
    dbn = root / 'results/X1_dbnsfp_subset old/dbnsfp_sh3.tsv.gz'
    if not dbn.exists():
        dbn = root / 'results/X1_dbnsfp_subset/dbnsfp_sh3.tsv.gz'
    pool = build_pool(dbn, wt)
    print(f'pool {len(pool)} base changes', file=sys.stderr)

    fasta = root / 'input/external/genome/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz'
    ctx = G.build_context(observed=obs, pool=pool, b6=b6, domains=atlas, fasta=fasta)
    print(json.dumps(ctx['counts'], indent=2), file=sys.stderr)

    cov = G.coverage_report(ctx, b6, atlas)
    B6_NULL = 0.09232
    assert abs(cov['destabilising_all_reachable'] - B6_NULL) <= 5e-4, (
        f"we get {cov['destabilising_all_reachable']:.5f} over B6's own reachable "
        f'set where B6 published {B6_NULL:.5f}')
    print('reproduction passes', file=sys.stderr)

    a3a = G.run_arm(ctx, name='3a uniform over substitutions', unit='substitution',
                    spectrum=None)
    a3b = G.run_arm(ctx, name='3b uniform over base changes', unit='base_change',
                    spectrum=None)

    prereg = (root / 'docs/preregistration/G1.md').read_text()
    named = [l.split('PRIMARY SPECTRUM:', 1)[1].strip()
             for l in prereg.splitlines() if 'PRIMARY SPECTRUM:' in l]
    PRIMARY = named[0] if named else None
    ALPHA = 0.025 if PRIMARY else 0.0125

    obs_spec = G.observed_spectrum(ctx)
    sigs = root / 'input/external/signatures/COSMIC_v3.6_SBS_GRCh38.txt'
    for nb, which, spec, arm in (
            ('G1a', 'observed', obs_spec, '1 observed spectrum'),
            ('G1b', 'cosmic', G.cosmic_spectrum(sigs, ('SBS1', 'SBS5')),
             '2 COSMIC SBS1+SBS5')):
        main_arm = G.run_arm(ctx, name=arm, unit='base_change', spectrum=spec)
        is_primary = (PRIMARY is None) or PRIMARY.lower().startswith(which)
        v = G.verdict(main_arm, ALPHA)
        G.write_metrics(out / f'metrics_{nb}.json', {
            'notebook': nb, 'spectrum': which,
            'primary_named_in_prereg': PRIMARY, 'is_primary': bool(is_primary),
            'alpha': ALPHA, 'verdict': v,
            'main': main_arm, 'control_3a': a3a, 'control_3b': a3b,
            'b6_published_null': B6_NULL, 'coverage': cov,
            'cosine_fit_to_observed': G.cosine(spec, obs_spec),
            'counts': ctx['counts'], 'multiplicity': ctx['multiplicity'],
            'exclusion_check': {'n_included': ctx['counts']['observed_eligible'],
                                'n_excluded': None, 'rate_included': None,
                                'rate_excluded': None},
            'spectrum_used': {k: float(x) for k, x in spec.items()},
            'observed_spectrum': {k: float(x) for k, x in obs_spec.items()},
            'opportunity': ctx['opportunity']})
        print(f"{nb} {which:9s} null {main_arm['null_median']:.4f} "
              f"obs {main_arm['observed_rate']:.4f} "
              f"gap {main_arm['gap_pp']:+.2f}pp "
              f"p {main_arm['p_one_sided_depleted']:.5f}  -> {v}")

    print(f"\nB6 published   {B6_NULL:.4f}")
    print(f"3a             {a3a['null_median']:.4f}  "
          f"({(a3a['null_median']-B6_NULL)*100:+.2f} pp codon reachability)")
    print(f"3b             {a3b['null_median']:.4f}  "
          f"({(a3b['null_median']-a3a['null_median'])*100:+.2f} pp multiplicity)")


if __name__ == '__main__':
    main()
