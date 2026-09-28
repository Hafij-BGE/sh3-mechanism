#!/usr/bin/env python3
"""
G1 step 0 — give every atlas variant a GRCh38 coordinate.

The frozen atlas records protein position and CDS notation (`c.196C>T`) but no
genomic coordinate, so a trinucleotide-context null cannot be built from it
directly.  X1's dbNSFP subset carries `#chr`/`pos(1-based)`/`ref`/`alt` for every
possible in-domain missense SNV, so the coordinate can be recovered by joining on
(gene, protein position, wild-type aa, mutant aa).

Two things make that join correct rather than approximate:

1.  dbNSFP's `aapos`, `Uniprot_acc` and `Ensembl_proteinid` are semicolon-separated
    *per transcript* and are index-aligned (verified: 0 length mismatches over
    2,120,008 rows).  Taking element [0] — the defect that cost X1 a run — silently
    picks whichever transcript dbNSFP listed first.  We instead align on the
    atlas's own UniProt accession, so a residue number is interpreted on the same
    protein the atlas numbered it against.

2.  One amino-acid substitution can be reachable by more than one nucleotide
    change, so a residue-level key can still map to several coordinates.  The
    atlas's `mutation_cds` gives the actual base substitution and breaks the tie,
    complementing for genes on the minus strand.

Variants that remain ambiguous, or that dbNSFP does not carry, are written out
with a reason and excluded — G1's pre-registration states the exclusion count.

The recovered coordinates are then checked against GRCh38 itself: the reference
base at every position must equal dbNSFP's `ref`.  That is the one number this
reduction does not control, and it is the check X1 taught us to demand — a derived
table needs at least one value verifiable against something outside itself.

Output is per-variant and COSMIC-derived, so it stays out of git (`*.tsv`).
"""
import argparse, csv, gzip, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

CDS = re.compile(r'^c\.(\d+)([ACGT])>([ACGT])$')
COMP = str.maketrans('ACGT', 'TGCA')


def load_atlas(path):
    rows = list(csv.DictReader(open(path), delimiter='\t'))
    key = {}
    for i, r in enumerate(rows):
        k = (r['gene'], r['pos_protein'], r['wt_aa'], r['mut_aa'])
        assert k not in key, f'duplicate atlas key {k}'
        key[k] = i
    return rows, key


def scan_dbnsfp(path, key, atlas):
    """Return (uniprot-aligned hits, any-transcript hits)."""
    upr, any_ = defaultdict(set), defaultdict(set)
    mismatch = n = 0
    with gzip.open(path, 'rt') as fh:
        ix = {c: j for j, c in enumerate(fh.readline().rstrip('\n').split('\t'))}
        C, P, RF, AL = ix['#chr'], ix['pos(1-based)'], ix['ref'], ix['alt']
        AR, AA, AP = ix['aaref'], ix['aaalt'], ix['aapos']
        GN, UP = ix['genename'], ix['Uniprot_acc']
        for line in fh:
            n += 1
            f = line.rstrip('\n').split('\t')
            aaref, aaalt = f[AR], f[AA]
            if aaref == '.' or aaalt == '.':
                continue
            poss, ups = f[AP].split(';'), f[UP].split(';')
            if len(poss) != len(ups):
                mismatch += 1
            coord = (f[C], f[P], f[RF], f[AL])
            for g in {g for g in f[GN].split(';') if g and g != '.'}:
                for j, p in enumerate(poss):
                    if not p or p == '.':
                        continue
                    k = (g, p, aaref, aaalt)
                    if k not in key:
                        continue
                    any_[k].add(coord)
                    if j < len(ups) and ups[j].split('-')[0] == \
                            (atlas[key[k]]['uniprot'] or '').split('-')[0]:
                        upr[k].add(coord)
    assert mismatch == 0, (
        f'{mismatch} rows where aapos and Uniprot_acc have different lengths; '
        'the per-transcript fields are no longer index-aligned and this join is unsafe')
    return upr, any_, n


def resolve(k, cands, atlas, key):
    """One coordinate, or None if the CDS change cannot break the tie."""
    s = sorted(cands)
    if len(s) == 1:
        return s[0]
    m = CDS.match((atlas[key[k]].get('mutation_cds') or '').strip())
    if not m:
        return None
    ref, alt = m.group(2), m.group(3)
    ok = [c for c in s if (c[2], c[3]) in
          ((ref, alt), (ref.translate(COMP), alt.translate(COMP)))]
    return ok[0] if len(ok) == 1 else None


def verify_against_genome(rows, fasta):
    """Every recovered position must carry dbNSFP's `ref` base in GRCh38.

    The Ensembl primary assembly ships as plain gzip, not BGZF, so there is no
    random access and no index; one streaming pass is the whole cost.
    """
    want = defaultdict(set)
    for r in rows:
        want[r['chrom']].add(int(r['pos_grch38']))
    got, targets, maxpos, cur, off = {}, None, 0, None, 0
    with gzip.open(fasta, 'rt') as fh:
        for line in fh:
            if line[0] == '>':
                cur = line[1:].split()[0]
                off, targets = 0, want.get(cur)
                maxpos = max(targets) if targets else 0
                continue
            if not targets or off >= maxpos:
                if targets:
                    off += len(line) - 1
                continue
            s = line.rstrip('\n')
            lo = off + 1
            for p in range(lo, off + len(s) + 1):
                if p in targets:
                    got[(cur, p)] = s[p - lo].upper()
            off += len(s)

    bad = [r for r in rows
           if got.get((r['chrom'], int(r['pos_grch38']))) != r['ref']]
    return {'verified': len(rows) - len(bad), 'mismatched': len(bad),
            'unique_positions': sum(len(v) for v in want.values())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--atlas', required=True)
    ap.add_argument('--dbnsfp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--metrics', required=True)
    ap.add_argument('--genome', help='GRCh38 primary assembly FASTA (.fa.gz); '
                                      'when given, every coordinate is checked against it')
    a = ap.parse_args()

    atlas, key = load_atlas(a.atlas)
    print(f'atlas variants: {len(atlas)}', file=sys.stderr)
    upr, any_, n = scan_dbnsfp(a.dbnsfp, key, atlas)
    print(f'dbNSFP rows scanned: {n}', file=sys.stderr)

    out, drop, src = {}, {}, Counter()
    for k in key:
        c = resolve(k, upr[k], atlas, key) if k in upr else None
        if c is not None:
            src['uniprot_aligned'] += 1
        elif k in any_:
            c = resolve(k, any_[k], atlas, key)
            if c is not None:
                src['any_transcript_plus_cds'] += 1
        if c is not None:
            out[k] = c
        else:
            drop[k] = 'not_in_dbnsfp' if k not in any_ else 'ambiguous_coordinate'

    with open(a.out, 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['variant_id', 'gene', 'pos_protein', 'wt_aa', 'mut_aa',
                    'chrom', 'pos_grch38', 'ref', 'alt', 'source'])
        for k, c in sorted(out.items()):
            r = atlas[key[k]]
            w.writerow([r['variant_id'], *k, *c,
                        'uniprot_aligned' if k in upr and resolve(k, upr[k], atlas, key)
                        else 'any_transcript_plus_cds'])

    written = [dict(zip(('variant_id','gene','pos_protein','wt_aa','mut_aa',
                         'chrom','pos_grch38','ref','alt'),
                        (atlas[key[k]]['variant_id'], *k, *c)))
               for k, c in sorted(out.items())]

    m = {'atlas_variants': len(atlas), 'dbnsfp_rows_scanned': n,
         'resolved': len(out), 'resolved_pct': round(100 * len(out) / len(atlas), 2),
         'by_source': dict(src), 'dropped': dict(Counter(drop.values()))}
    if a.genome:
        v = verify_against_genome(written, a.genome)
        m['genome_check'] = v
        assert v['mismatched'] == 0, (
            f"{v['mismatched']} recovered coordinates do not carry dbNSFP's ref "
            'base in GRCh38; the join is wrong and G1 must not proceed')
    json.dump(m, open(a.metrics, 'w'), indent=2)
    print(json.dumps(m, indent=2))


if __name__ == '__main__':
    main()
