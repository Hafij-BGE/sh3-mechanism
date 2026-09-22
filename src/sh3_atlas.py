"""Stage 0 — build the SH3 cancer-variant atlas from raw COSMIC and a frozen UniProt snapshot.

Standard library only, so it runs the same in Colab and on a laptop. The logic is the
original Stage 0 build (phase1_domain_atlas/scripts/build_master_v2.py and
add_tumour_types.py), with the hard-coded paths replaced by arguments. Nothing in the
selection or aggregation rules has changed, so the output is byte-identical to
SH3_cancer_master_v3.tsv when the inputs are the same files.
"""
import csv, gzip, json, collections, os, re, tempfile

csv.field_size_limit(10**9)

MASTER_COLS = ["variant_id", "gene", "uniprot", "domain_idx", "domain_desc", "dom_start", "dom_end",
               "dom_len", "pos_protein", "pos_in_domain", "wt_aa", "mut_aa", "mutation_aa", "prot_len",
               "wt_domain_seq", "mut_domain_seq", "position_source", "cosmic_reported_pos",
               "n_samples_mutated", "n_cmc_rows", "n_diseases", "top_diseases",
               "onc_tsg", "cgc_tier", "mutation_significance_tier", "dnds_disease_qval_sig",
               "min_sift_score", "min_sift_pred", "gerp_rs", "clinvar_clnsig", "clinvar_trait",
               "gnomad_exomes_af", "gnomad_genomes_af", "is_recurrent", "likely_germline",
               "mutation_cds", "legacy_mutation_ids"]
TUMOUR_COLS = ["n_samples_gsm", "n_samples_nonhyper", "n_hypermutated_samples",
               "n_primary_sites", "top_primary_sites", "top_histologies", "top_histology_subtypes"]
HYPERMUTATION_THRESHOLD = 1000      # mutations per sample in the genome screens


def _open_text(path):
    """Plain or gzip text, streamed. gzip raises EOFError if the archive is truncated."""
    if path.endswith(".gz"):
        return gzip.open(path, "rt", newline="")
    return open(path, newline="")


# ── step 1: domain windows on the canonical sequence and on every alternative isoform ──
def domain_windows(domains_tsv, proteins_tsv, isoforms_json):
    canon = {r["uniprot"]: r["sequence"] for r in
             csv.DictReader(open(proteins_tsv), delimiter="\t")}
    iso = json.load(open(isoforms_json))
    iso_by_acc = collections.defaultdict(list)
    for sid, s in iso.items():
        iso_by_acc[sid.split("-")[0]].append((sid, s))

    dinfo, windows, nwin = {}, collections.defaultdict(list), collections.Counter()
    for r in csv.DictReader(open(domains_tsv), delimiter="\t"):
        acc, didx, dseq = r["uniprot"], r["domain_idx"], r["domain_seq"]
        dinfo[(acc, didx)] = r
        g, L = r["gene"], len(dseq)
        windows[g].append((acc, didx, acc, canon[acc], int(r["start"]), int(r["end"]), True))
        nwin["canonical"] += 1
        for sid, s in iso_by_acc[acc]:
            if sid == acc or "-" not in sid:
                continue
            j = s.find(dseq)
            if j >= 0 and s != canon[acc]:
                windows[g].append((acc, didx, sid, s, j + 1, j + L, False))
                nwin["isoform"] += 1
    return dinfo, windows, dict(nwin)


# ── step 2: scan COSMIC CMC, keep residue-verified missense variants inside a domain ──
def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _fmax(a, b):
    v = [x for x in (a, b) if x is not None]
    return max(v) if v else None


def build_master(cmc_path, dinfo, windows):
    Agg = lambda: {"rows": 0, "samples": 0, "dis": collections.Counter(), "tiers": set(), "dnds": set(),
                   "sift": None, "sift_pred": set(), "gerp": None, "gnomad_e": None, "gnomad_g": None,
                   "clnsig": set(), "cltrait": set(), "onc": set(), "cgc": set(), "cds": set(),
                   "legacy": set(), "src": set(), "tpos": set()}
    agg = collections.defaultdict(Agg)
    unmapped, stat = [], collections.Counter()

    with _open_text(cmc_path) as fh:
        rd = csv.reader(fh, delimiter="\t")
        hdr = next(rd)
        ix = {n: i for i, n in enumerate(hdr)}
        c = lambda n: ix[n]
        for row in rd:
            stat["rows"] += 1
            g = row[c("GENE_NAME")].split("_")[0]
            if g not in windows:
                continue
            if "Missense" not in row[c("Mutation Description AA")]:
                continue
            stat["missense_sh3_gene"] += 1
            try:
                pos = int(row[c("AA_MUT_START")])
            except ValueError:
                continue
            wt, mu = row[c("AA_WT_ALLELE_SEQ")], row[c("AA_MUT_ALLELE_SEQ")]
            if not (wt and mu and len(wt) == 1 and len(mu) == 1):
                continue
            best = None
            for acc, didx, sid, s, ws, we, is_canon in windows[g]:
                if ws <= pos <= we and len(s) >= pos and s[pos - 1] == wt:
                    if is_canon:
                        best = (acc, didx, sid, pos - ws + 1, True)
                        break
                    if best is None:
                        best = (acc, didx, sid, pos - ws + 1, False)
            if best is None:
                if any(ws <= pos <= we for *_, ws, we, ic in windows[g] if ic):
                    stat["in_window_residue_mismatch"] += 1
                    unmapped.append([g, pos, wt, mu, row[c("Mutation AA")],
                                     row[c("COSMIC_SAMPLE_MUTATED")], row[c("DISEASE")]])
                continue
            acc, didx, sid, pid, is_canon = best
            stat["mapped_canonical" if is_canon else "mapped_isoform"] += 1
            a = agg[(acc, didx, pid, wt, mu)]
            a["rows"] += 1
            n = int(row[c("COSMIC_SAMPLE_MUTATED")] or 0)
            a["samples"] += n
            a["src"].add("canonical" if is_canon else f"isoform:{sid}")
            a["tpos"].add(str(pos))
            if row[c("DISEASE")]:
                a["dis"][row[c("DISEASE")]] += max(n, 1)
            for k, col in (("tiers", "MUTATION_SIGNIFICANCE_TIER"), ("dnds", "DNDS_DISEASE_QVAL_SIG"),
                           ("sift_pred", "MIN_SIFT_PRED"), ("clnsig", "CLINVAR_CLNSIG"),
                           ("cltrait", "CLINVAR_TRAIT"), ("onc", "ONC_TSG"), ("cgc", "CGC_TIER"),
                           ("cds", "Mutation CDS"), ("legacy", "LEGACY_MUTATION_ID")):
                if row[c(col)]:
                    a[k].add(row[c(col)])
            v = _num(row[c("MIN_SIFT_SCORE")])
            if v is not None:
                a["sift"] = v if a["sift"] is None else min(a["sift"], v)
            v = _num(row[c("GERP++_RS")])
            if v is not None:
                a["gerp"] = v if a["gerp"] is None else max(a["gerp"], v)
            a["gnomad_e"] = _fmax(a["gnomad_e"], _num(row[c("GNOMAD_EXOMES_AF")]))
            a["gnomad_g"] = _fmax(a["gnomad_g"], _num(row[c("GNOMAD_GENOMES_AF")]))

    j = lambda s: ";".join(sorted(x for x in s if x)) if s else ""
    out = []
    for (acc, didx, pid, wt, mu), a in agg.items():
        d = dinfo[(acc, didx)]
        s, e = int(d["start"]), int(d["end"])
        wt_dom = d["domain_seq"]
        assert wt_dom[pid - 1] == wt, (acc, didx, pid, wt)
        mut_dom = wt_dom[:pid - 1] + mu + wt_dom[pid:]
        pos_prot = s + pid - 1
        gaf = _fmax(a["gnomad_e"], a["gnomad_g"]) or 0.0
        t = sorted(a["tiers"])
        out.append([f"{acc}_d{didx}_{wt}{pos_prot}{mu}", d["gene"], acc, didx, d["desc"], s, e, e - s + 1,
                    pos_prot, pid, wt, mu, f"p.{wt}{pos_prot}{mu}", d["prot_len"], wt_dom, mut_dom,
                    j(a["src"]), j(a["tpos"]), a["samples"], a["rows"], len(a["dis"]),
                    ";".join(f"{k}({v})" for k, v in a["dis"].most_common(3)),
                    j(a["onc"]), j(a["cgc"]), t[0] if t else "", j(a["dnds"]),
                    "" if a["sift"] is None else f"{a['sift']:.3f}", j(a["sift_pred"]),
                    "" if a["gerp"] is None else f"{a['gerp']:.2f}", j(a["clnsig"]), j(a["cltrait"]),
                    "" if a["gnomad_e"] is None else f"{a['gnomad_e']:.3e}",
                    "" if a["gnomad_g"] is None else f"{a['gnomad_g']:.3e}",
                    int(a["samples"] >= 3), int(gaf > 1e-3), j(a["cds"]), j(a["legacy"])])
    out.sort(key=lambda r: (-r[18], r[1], r[8]))
    return out, unmapped, dict(stat)


def write_tsv(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(header)
        w.writerows(rows)


# ── step 3: per-sample genome screens → tumour type and hypermutation status ──
def add_tumour_types(master_v2_tsv, gsm_path, classification_tsv, thresh=HYPERMUTATION_THRESHOLD):
    master = list(csv.DictReader(open(master_v2_tsv), delimiter="\t"))
    lookup = {}
    for r in master:
        for p in r["cosmic_reported_pos"].split(";"):
            if p:
                lookup[(r["gene"], r["wt_aa"], p, r["mut_aa"])] = r["variant_id"]

    pheno = {}
    for r in csv.DictReader(open(classification_tsv), delimiter="\t"):
        pheno[r["COSMIC_PHENOTYPE_ID"]] = (r.get("PRIMARY_SITE", ""), r.get("PRIMARY_HISTOLOGY", ""),
                                           r.get("HISTOLOGY_SUBTYPE_1", ""))

    AA = re.compile(r"^p\.([A-Z])(\d+)([A-Z])$")
    burden, hits = collections.Counter(), []
    n = short = 0
    with _open_text(gsm_path) as fh:
        rd = csv.reader(fh, delimiter="\t")
        hdr = next(rd)
        ix = {nm: i for i, nm in enumerate(hdr)}
        G, S, P, A, D = (ix["GENE_SYMBOL"], ix["COSMIC_SAMPLE_ID"], ix["COSMIC_PHENOTYPE_ID"],
                         ix["MUTATION_AA"], ix["MUTATION_DESCRIPTION"])
        need = max(G, S, P, A, D) + 1
        for row in rd:
            n += 1
            if len(row) < need:
                short += 1
                continue
            burden[row[S]] += 1
            if "missense" not in row[D]:
                continue
            m = AA.match(row[A])
            if not m:
                continue
            wt, pos, mu = m.groups()
            vid = lookup.get((row[G].split("_")[0], wt, pos, mu))
            if vid:
                hits.append((vid, row[S], row[P]))

    vals = sorted(burden.values())
    p50, p95, p99 = (vals[int(len(vals) * q)] for q in (0.50, 0.95, 0.99))
    hyper = {s for s, c in burden.items() if c > thresh}

    V = lambda: {"samples": set(), "hyper": set(), "site": collections.Counter(),
                 "hist": collections.Counter(), "sub": collections.Counter()}
    agg = collections.defaultdict(V)
    for vid, sid, pid in hits:
        a = agg[vid]
        a["samples"].add(sid)
        if sid in hyper:
            a["hyper"].add(sid)
        site, hist, sub = pheno.get(pid, ("", "", ""))
        if site: a["site"][site] += 1
        if hist: a["hist"][hist] += 1
        if sub:  a["sub"][sub] += 1

    top = lambda c, k=3: ";".join(f"{x}({y})" for x, y in c.most_common(k))
    out_rows = []
    for r in master:
        a = agg.get(r["variant_id"])
        if a:
            new = [len(a["samples"]), len(a["samples"]) - len(a["hyper"]), len(a["hyper"]),
                   len(a["site"]), top(a["site"]), top(a["hist"]), top(a["sub"])]
        else:
            new = [0, 0, 0, 0, "", "", ""]
        out_rows.append(list(r.values()) + [str(v) for v in new])
    cols = list(master[0].keys()) + TUMOUR_COLS
    stats = dict(gsm_rows=n, gsm_short_rows=short, gsm_samples=len(burden), atlas_hits=len(hits),
                 burden_median=p50, burden_p95=p95, burden_p99=p99,
                 hypermutated_samples=len(hyper), hypermutated_fraction=len(hyper) / len(burden))
    return cols, out_rows, stats


def build_atlas(cmc, gsm, classification, domains_tsv, proteins_tsv, isoforms_json, out_dir):
    """Full Stage 0. Writes SH3_cancer_master.tsv and SH3_cancer_unmapped.tsv to out_dir."""
    os.makedirs(out_dir, exist_ok=True)
    dinfo, windows, nwin = domain_windows(domains_tsv, proteins_tsv, isoforms_json)
    rows, unmapped, stat = build_master(cmc, dinfo, windows)
    write_tsv(f"{out_dir}/SH3_cancer_unmapped.tsv",
              ["gene", "cosmic_pos", "cosmic_wt_aa", "mut_aa", "mutation_aa", "samples_mutated", "disease"],
              unmapped)
    with tempfile.TemporaryDirectory() as td:        # the v2 table is an intermediate, as in the original
        v2 = f"{td}/SH3_cancer_master_v2.tsv"
        write_tsv(v2, MASTER_COLS, rows)
        cols, out_rows, tstat = add_tumour_types(v2, gsm, classification)
    write_tsv(f"{out_dir}/SH3_cancer_master.tsv", cols, out_rows)
    return dict(windows=nwin, cmc=stat, tumour=tstat, variants=len(out_rows), columns=len(cols))


if __name__ == "__main__":        # local run: python sh3_atlas.py <cmc> <gsm> <classif> <dom> <prot> <iso> <out>
    import sys
    print(json.dumps(build_atlas(*sys.argv[1:8]), indent=1))
