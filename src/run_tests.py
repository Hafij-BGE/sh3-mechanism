"""Unit tests for the shared pipeline code. Run: python run_tests.py (A0 runs it before building).

The atlas tests need only the standard library; the rest need numpy/pandas/scikit-learn and are
skipped with a message if those are missing (e.g. on a bare laptop Python)."""
import csv, json, os, re, sys, tempfile, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TESTS, SKIPPED = [], []


def test(fn):
    TESTS.append(fn)
    return fn


# ─────────────────────────────────────────────────────────── Stage 0 atlas (stdlib only)
def _write(path, header, rows):
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t'); w.writerow(header); w.writerows(rows)


@test
def atlas_keeps_only_residue_verified_variants_and_recovers_isoforms():
    import sh3_atlas as S
    d = tempfile.mkdtemp()
    canon = 'MAAAKVYALYDYEARTEDDLSFHKGEKFQILNSSEGDWWEARSLTTGETGYIPSNYVAPVDRRR'   # domain at 5..62
    iso = 'MQQ' + canon                                                         # isoform shifts numbering by +3
    dom = canon[4:62]
    _write(f'{d}/dom.tsv', ['uniprot', 'gene', 'domain_idx', 'desc', 'start', 'end', 'length', 'domain_seq', 'prot_len'],
           [['P00001', 'GENE1', '1', 'SH3', '5', '62', '58', dom, str(len(canon))]])
    _write(f'{d}/prot.tsv', ['uniprot', 'sequence'], [['P00001', canon]])
    json.dump({'P00001': canon, 'P00001-2': iso}, open(f'{d}/iso.json', 'w'))
    hdr = ['GENE_NAME', 'Mutation AA', 'AA_MUT_START', 'AA_WT_ALLELE_SEQ', 'AA_MUT_ALLELE_SEQ', 'Mutation Description AA',
           'COSMIC_SAMPLE_MUTATED', 'DISEASE', 'MUTATION_SIGNIFICANCE_TIER', 'DNDS_DISEASE_QVAL_SIG', 'MIN_SIFT_PRED',
           'CLINVAR_CLNSIG', 'CLINVAR_TRAIT', 'ONC_TSG', 'CGC_TIER', 'Mutation CDS', 'LEGACY_MUTATION_ID', 'MIN_SIFT_SCORE',
           'GERP++_RS', 'GNOMAD_EXOMES_AF', 'GNOMAD_GENOMES_AF']
    row = lambda pos, wt, mu, desc='Substitution - Missense', n='2': ['GENE1', f'p.{wt}{pos}{mu}', str(pos), wt, mu, desc, n,
                                                                        'carcinoma', 'Other', '', '', '', '', '', '', 'c.1A>G', 'L1',
                                                                        '0.01', '4.5', '', '']
    _write(f'{d}/cmc.tsv', hdr, [row(6, canon[5], 'P'),                  # canonical, residue matches -> kept
                                 row(6, 'W', 'P'),                       # residue mismatch -> rejected
                                 row(9, iso[8], 'D'),                    # only matches on the isoform -> recovered
                                 row(7, canon[6], 'G', desc='Substitution - coding silent'),   # not missense
                                 row(100, 'A', 'G')])                    # outside the domain
    _write(f'{d}/gsm.tsv', ['GENE_SYMBOL', 'COSMIC_SAMPLE_ID', 'COSMIC_PHENOTYPE_ID', 'MUTATION_AA', 'MUTATION_DESCRIPTION'],
           [['GENE1', 'S1', 'PH1', f'p.{canon[5]}6P', 'missense_variant'], ['GENE1', 'S2', 'PH1', f'p.{canon[5]}6P', 'missense_variant']]
           + [['OTHER', 'S2', 'PH1', 'p.A1G', 'missense_variant']] * 1001)   # S2 is hypermutated (>1000)
    _write(f'{d}/cls.tsv', ['COSMIC_PHENOTYPE_ID', 'PRIMARY_SITE', 'PRIMARY_HISTOLOGY', 'HISTOLOGY_SUBTYPE_1'],
           [['PH1', 'skin', 'carcinoma', 'NS']])
    st = S.build_atlas(f'{d}/cmc.tsv', f'{d}/gsm.tsv', f'{d}/cls.tsv', f'{d}/dom.tsv', f'{d}/prot.tsv', f'{d}/iso.json', d)
    M = list(csv.DictReader(open(f'{d}/SH3_cancer_master.tsv'), delimiter='\t'))
    assert st['cmc']['mapped_canonical'] == 1 and st['cmc']['mapped_isoform'] == 1, st['cmc']
    assert st['cmc']['in_window_residue_mismatch'] == 1 and len(M) == 2 and len(M[0]) == 44
    for r in M:
        assert r['wt_domain_seq'][int(r['pos_in_domain']) - 1] == r['wt_aa']
    k = {r['position_source'].split(':')[0]: r for r in M}
    assert k['canonical']['n_samples_gsm'] == '2' and k['canonical']['n_samples_nonhyper'] == '1'
    assert k['isoform']['cosmic_reported_pos'] == '9' and k['isoform']['pos_protein'] == '6'


# ─────────────────────────────────────────────────────────── shared ML/statistics code
def need_numpy():
    try:
        import numpy, pandas, sklearn  # noqa
        return True
    except ImportError:
        return False


@test
def mutation_pattern_and_sign_convention():
    import sh3_common as C
    assert re.match(C.MUT_PATTERN, 'A12G').groups() == ('A', '12', 'G') and not re.match(C.MUT_PATTERN, 'A12G:K3R')
    assert C.SIGN_CONVENTION.startswith('positive = destabilising')


@test
def sign_test_values():
    import sh3_common as C
    assert abs(C.sign_test_two_sided(15, 15) - 2 / 2 ** 15) < 1e-15
    assert abs(C.sign_test_two_sided(12, 15) - 0.03515625) < 1e-12
    assert C.sign_test_two_sided(11, 15) > 0.05


@test
def partition_modes():
    import numpy as np, sh3_common as C
    g = np.repeat(np.arange(1, 57), 11); X = np.zeros((len(g), 3)); y = np.zeros(len(g))
    o0, o1 = C.position_splits(X, y, g, 7, 'original', 0), C.position_splits(X, y, g, 7, 'original', 1)
    c0, c1 = C.position_splits(X, y, g, 7, 'corrected', 0), C.position_splits(X, y, g, 7, 'corrected', 1)
    same = lambda a, b: all(set(g[x[1]]) == set(g[z[1]]) for x, z in zip(a, b))
    assert same(o0, o1), 'original mode should ignore the seed'
    assert not same(c0, c1), 'corrected mode should change with the seed'
    for sp in (o0, c0):
        tests = [set(g[te]) for _, te in sp]
        assert sum(len(t) for t in tests) == 56 and set().union(*tests) == set(range(1, 57))
        assert all(not (set(g[tr]) & set(g[te])) for tr, te in sp), 'a position is on both sides'


@test
def inner_validation_is_deterministic_and_by_position():
    import numpy as np, sh3_common as C
    g = np.repeat(np.arange(48), 5)
    a, b = C.inner_validation(g, 3), C.inner_validation(g, 3)
    assert (a == b).all() and len(set(g[a])) == 48 // 6
    assert not (set(g[a]) & set(g[~a]))


@test
def conformal_quantile_formula():
    import numpy as np
    s = np.sort(np.arange(1, 101, dtype=float)); n = len(s)
    q = float(s[min(int(np.ceil((n + 1) * 0.9)), n) - 1])
    assert q == 91.0


@test
def build_X_shape_and_lookup():
    import numpy as np, pandas as pd, sh3_common as C
    EMB = {'d1': np.arange(3 * 1280, dtype=np.float16).reshape(3, 1280)}
    df = pd.DataFrame({'domain_key': ['d1', 'd1', 'dX', 'd1'], 'pos': [1, 3, 1, 9], **{s: 0.0 for s in C.SCALARS}})
    X, kept = C.build_X(df, EMB)
    assert X.shape == (2, 1292) and list(kept.pos) == [1, 3] and X[1, 0] == EMB['d1'][2, 0]


@test
def markdown_table():
    import pandas as pd, sh3_common as C
    t = C.md_table(pd.DataFrame({'a': [1.23456, float('nan')], 'b': ['x', 'y']}))
    assert t.splitlines()[0] == '| a | b |' and '1.235' in t and '|  | y |' in t


if __name__ == '__main__':
    have = need_numpy(); failed = 0
    for fn in TESTS:
        if fn.__name__ != 'atlas_keeps_only_residue_verified_variants_and_recovers_isoforms' and not have:
            SKIPPED.append(fn.__name__); continue
        try:
            fn(); print(f'  ok    {fn.__name__}')
        except Exception:
            failed += 1; print(f'  FAIL  {fn.__name__}'); traceback.print_exc()
    for s in SKIPPED: print(f'  skip  {s} (numpy/pandas/scikit-learn not installed)')
    print(f'{len(TESTS) - failed - len(SKIPPED)} passed, {failed} failed, {len(SKIPPED)} skipped')
    sys.exit(1 if failed else 0)
