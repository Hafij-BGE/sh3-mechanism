"""Shared code for the SH3 reproducible pipeline (notebooks A0–D1).

Every function here is the exact procedure used by the original stage-by-stage run, so the
ORIGINAL partition mode reproduces the recorded numbers. Where a procedure was found to be
flawed on re-checking, the flaw is kept behind `mode='original'` and the fix is offered as
`mode='corrected'`; nothing is changed silently.

Layout on Drive (ROOT = MyDrive/sh3_repro):
    input/{cosmic,uniprot,datasets}   raw files, checked by MD5
    reference/                        expected_values.json, checksums.md5, data_manifest.json
    cache/                            AlphaFold models, extracted archives
    results/<ID>/                     each program's outputs, metrics_<ID>.json, RESULTS_<ID>.md
"""
import os, re, json, time, glob, hashlib, zipfile, platform, datetime, math
import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
except ImportError:                     # the Stage 0 atlas and the tests do not need torch
    torch = nn = None

SIGN_CONVENTION = 'positive = destabilising / weaker binding'
PROGRAMS = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'C3', 'B3', 'C4', 'B4', 'B5', 'B6', 'D1']   # run order
PROGRAM_DIRS = {'A0': 'A0_cancer_atlas', 'A1': 'A1_ground_truth', 'A2': 'A2_features',
                'B1': 'B1_folding_model', 'B2': 'B2_structural_check', 'B3': 'B3_uncertainty_and_calls',
                'B4': 'B4_external_validation', 'B5': 'B5_cancer_biology', 'B6': 'B6_virtual_saturation_mutagenesis',
                'C1': 'C1_binding_cross_domain', 'C2': 'C2_binding_within_domain',
                'C3': 'C3_binding_data_sufficiency', 'C4': 'C4_specificity_axis',
                'D1': 'D1_figures_and_verification'}


# ═══════════════════════════════════════════════════════════════ run bookkeeping
def md5(path, block=1 << 24):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(block), b''):
            h.update(b)
    return h.hexdigest()


def env_info():
    info = {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__}
    for mod in ('scipy', 'sklearn', 'transformers', 'Bio'):
        try:
            info[mod] = __import__(mod).__version__
        except Exception:
            pass
    if torch is not None:
        info['torch'] = torch.__version__
        info['gpu'] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'
    return info


def md_table(df, floatfmt='{:.4g}', index=False):
    """Markdown table without needing the tabulate package."""
    d = df.reset_index() if index else df
    fmt = lambda v: ('' if (v is None or (isinstance(v, float) and math.isnan(v)))
                     else floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v))
    lines = ['| ' + ' | '.join(map(str, d.columns)) + ' |', '|' + '---|' * len(d.columns)]
    lines += ['| ' + ' | '.join(fmt(v) for v in row) + ' |' for row in d.itertuples(index=False)]
    return '\n'.join(lines)


class Run:
    """One program's run: paths, input checks, resumable outputs, metrics and the results report."""

    def __init__(self, root, pid, title, resume=True):
        self.root, self.id, self.title, self.resume = root, pid, title, resume
        self.IN, self.REF, self.CACHE = f'{root}/input', f'{root}/reference', f'{root}/cache'
        self.OUT = f'{root}/results/{PROGRAM_DIRS[pid]}'
        self.WORK = '/content/work' if os.path.isdir('/content') else os.path.join(
            os.environ.get('TMPDIR', '/tmp'), 'sh3_work')
        for d in (self.OUT, self.CACHE, self.WORK):
            os.makedirs(d, exist_ok=True)
        self.metrics, self.sections, self.t0 = {}, [], time.time()
        self.started = datetime.datetime.now().isoformat(timespec='seconds')
        print(f'{pid} — {title}\n  results -> {self.OUT}')

    # -- paths
    def out(self, name):
        return f'{self.OUT}/{name}'

    def res(self, pid, name):
        p = f'{self.root}/results/{PROGRAM_DIRS[pid]}/{name}'
        if not os.path.exists(p):
            raise FileNotFoundError(f'{name} not found. Run {pid} ({PROGRAM_DIRS[pid]}) first.')
        return p

    def done(self, *names):
        return self.resume and all(os.path.exists(self.out(n)) for n in names)

    # -- inputs
    def verify_inputs(self, relpaths):
        """MD5-check the named inputs against reference/checksums.md5. Stops on any mismatch."""
        want = {}
        for line in open(f'{self.REF}/checksums.md5'):
            if line.strip():
                h, p = line.split(None, 1)
                want[p.strip()] = h
        missing = [p for p in relpaths if not os.path.exists(f'{self.root}/{p}')]
        if missing:
            raise SystemExit(f'Upload these first (see UPLOAD_GUIDE.md): {missing}')
        for p in relpaths:
            t = time.time()
            got = md5(f'{self.root}/{p}')
            if got != want[p]:
                raise SystemExit(f'{p}: MD5 {got} is not the file this thesis used ({want[p]}). Stop.')
            print(f'  verified {p}  ({time.time() - t:.0f}s)')

    def extract(self, zip_rel, keep):
        """Extract matching members of an input archive into WORK (skips macOS resource forks)."""
        with zipfile.ZipFile(f'{self.root}/{zip_rel}') as z:
            m = [n for n in z.namelist() if keep(n) and not n.startswith('__MACOSX')]
            todo = [n for n in m if not os.path.exists(f'{self.WORK}/{n}')]
            if todo:
                z.extractall(self.WORK, members=todo)
        return m

    # -- reporting
    def metric(self, key, value):
        if isinstance(value, (np.integer,)):
            value = int(value)
        elif isinstance(value, (np.floating,)):
            value = float(value)
        elif isinstance(value, (np.bool_,)):
            value = bool(value)
        self.metrics[key] = value
        return value

    def section(self, heading, text='', table=None, floatfmt='{:.4g}'):
        self.sections.append((heading, text, None if table is None else md_table(table, floatfmt)))

    def compare(self):
        """Compare every metric that has a recorded value in reference/expected_values.json."""
        ref = json.load(open(f'{self.REF}/expected_values.json'))
        rows = []
        for k, v in self.metrics.items():
            key = f'{self.id}.{k}'
            e = ref.get(key)
            if '.corrected.' in f'.{k}.' or k.startswith('corrected.'):
                status, exp = 'new (corrected procedure)', None
            elif e is None:
                status, exp = '', None
            else:
                exp, tol = e['value'], e['tol']
                if isinstance(exp, (bool, str)) or isinstance(v, (bool, str)):
                    status = 'identical' if v == exp else 'DIFF'
                else:
                    d = abs(float(v) - float(exp))
                    status = ('identical' if (d == 0 or (d <= tol and tol <= 1e-9))
                              else 'within tolerance' if d <= tol else 'DIFF')
            rows.append(dict(quantity=k, this_run=v, recorded=exp, status=status))
        return pd.DataFrame(rows)

    def finish(self, summary):
        cmp_ = self.compare()
        n = cmp_.status.value_counts().to_dict()
        verdict = ('no recorded values to compare' if not any(s in n for s in ('identical', 'within tolerance', 'DIFF'))
                   else 'REPRODUCED' if n.get('DIFF', 0) == 0 else f'{n["DIFF"]} value(s) DIFFER')
        meta = {'program': self.id, 'title': self.title, 'started': self.started,
                'minutes': round((time.time() - self.t0) / 60, 1), 'environment': env_info(),
                'verdict': verdict, 'status_counts': n}
        json.dump({'meta': meta, 'metrics': self.metrics}, open(self.out(f'metrics_{self.id}.json'), 'w'),
                  indent=1, default=str)
        cmp_.to_csv(self.out(f'comparison_{self.id}.csv'), index=False)
        L = [f'# {self.id} — {self.title}', '',
             f'*Generated automatically by the notebook on {self.started} '
             f'({meta["minutes"]} min). Every number below comes from this run; nothing is typed by hand.*', '',
             '## Summary', '']
        L += [f'- {s}' for s in summary] + ['', f'**Check against the recorded run: {verdict}** '
                                                f'({", ".join(f"{v} {k}" for k, v in n.items() if k)})', '']
        for h, t, tb in self.sections:
            L += [f'## {h}', '']
            if t:
                L += [t, '']
            if tb:
                L += [tb, '']
        L += ['## All quantities and their check', '', md_table(cmp_), '',
              '## Environment', '', md_table(pd.DataFrame([meta['environment']])), '']
        open(self.out(f'RESULTS_{self.id}.md'), 'w').write('\n'.join(L))
        print(f'\n{self.id}: {verdict}')
        print(cmp_[cmp_.status != ''].to_string(index=False, max_colwidth=60))
        print(f'\nwrote RESULTS_{self.id}.md, metrics_{self.id}.json, comparison_{self.id}.csv')
        return cmp_


# ═══════════════════════════════════════════════════════════════ features
SCALARS = ['esm_score', 'esm_wt_logp', 'esm_entropy', 'rel_pos', 'dom_len', 'd_hydropathy',
           'd_volume', 'd_charge', 'blosum62', 'to_proline', 'from_glycine', 'to_glycine']
KD = {'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
      'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2}
VOL = {'A': 88.6, 'R': 173.4, 'N': 114.1, 'D': 111.1, 'C': 108.5, 'Q': 143.8, 'E': 138.4, 'G': 60.1, 'H': 153.2,
       'I': 166.7, 'L': 166.7, 'K': 168.6, 'M': 162.9, 'F': 189.9, 'P': 112.7, 'S': 89.0, 'T': 116.1,
       'W': 227.8, 'Y': 193.6, 'V': 140.0}
CHG = {'D': -1, 'E': -1, 'K': 1, 'R': 1, 'H': 0.5}
MUT_PATTERN = r'^([A-Z])(\d+)([A-Z])$'


def load_embeddings(path):
    E = np.load(path)
    return {k: E[k] for k in E.files}


def build_X(df, EMB, half=True):
    """1280 ESM dims of the mutated residue + the 12 scalars. Rows without an embedding are dropped."""
    df = df[df.domain_key.isin(EMB)].reset_index(drop=True)
    E = np.zeros((len(df), 1280), np.float16)
    good = np.ones(len(df), bool)
    for i, (k, p) in enumerate(zip(df.domain_key.values, df.pos.values)):
        e = EMB[k]; j = int(p) - 1
        if 0 <= j < len(e):
            E[i] = e[j]
        else:
            good[i] = False
    X = np.hstack([E.astype(np.float32), df[SCALARS].astype(np.float32).fillna(0.0).values])
    if half:
        X = X.astype(np.float16)
    return X[good], df[good].reset_index(drop=True)


# ═══════════════════════════════════════════════════════════════ models
DEV = 'cuda' if (torch is not None and torch.cuda.is_available()) else 'cpu'

if nn is not None:
    class FoldHead(nn.Module):
        def __init__(s, d):
            super().__init__()
            s.net = nn.Sequential(nn.Linear(d, 512), nn.ReLU(), nn.Dropout(0.2),
                                  nn.Linear(512, 128), nn.ReLU(), nn.Dropout(0.1), nn.Linear(128, 1))

        def forward(s, x):
            return s.net(x).squeeze(-1)

    class BindHead(nn.Module):
        """Deliberately small: ~2,800 measurements against a 650M-parameter encoder will memorise."""
        def __init__(s, d):
            super().__init__()
            s.net = nn.Sequential(nn.Linear(d, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 1))

        def forward(s, x):
            return s.net(x).squeeze(-1)


class Scaler:
    """Variance floor + clip. A 1e-6 floor is what made Stage 3b's first run diverge."""
    def fit(s, X):
        s.m = X.mean(0); s.sd = np.maximum(X.std(0), 1e-2); return s

    def __call__(s, X):
        return np.clip((X - s.m) / s.sd, -10, 10).astype(np.float32)


class ScalerStage3:
    """The original Stage 3 scaler (1e-6 floor, no clip). Kept only to reproduce C1 exactly."""
    def fit(s, X):
        s.m = X.mean(0); s.sd = X.std(0) + 1e-6; return s

    def __call__(s, X):
        return (X - s.m) / s.sd


def train(Model, Xtr, ytr, Xva, yva, epochs, bs, lr=1e-3, wd=1e-3, seed=0, guard=False):
    """AdamW + cosine schedule, keep the epoch with the lowest validation RMSE.
    guard=True adds gradient clipping and stops a diverging run (Stages 3b–3e)."""
    torch.manual_seed(seed); np.random.seed(seed)
    m = Model(Xtr.shape[1]).to(DEV)
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=wd)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs); lf = nn.SmoothL1Loss()
    Xt = torch.tensor(Xtr, dtype=torch.float32); yt = torch.tensor(ytr, dtype=torch.float32)
    Xv = torch.tensor(Xva, dtype=torch.float32).to(DEV); best = (1e9, None)
    for ep in range(epochs):
        m.train(); perm = torch.randperm(len(Xt))
        for i in range(0, len(perm), bs):
            idx = perm[i:i + bs]; opt.zero_grad()
            lf(m(Xt[idx].to(DEV)), yt[idx].to(DEV)).backward()
            if guard:
                torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)
            opt.step()
        sch.step(); m.eval()
        with torch.no_grad():
            r = float(np.sqrt(np.mean((m(Xv).cpu().numpy() - yva) ** 2)))
        if guard and (not np.isfinite(r) or r > 1e3):
            break
        if r < best[0]:
            best = (r, {k: v.detach().clone() for k, v in m.state_dict().items()})
    if best[1] is None:
        return None
    m.load_state_dict(best[1]); m.eval()
    return m


def predict(m, X, bs=8192):
    with torch.no_grad():
        return np.concatenate([m(torch.tensor(X[i:i + bs], dtype=torch.float32).to(DEV)).cpu().numpy()
                               for i in range(0, len(X), bs)])


def load_fold_models(path):
    ck = torch.load(path, map_location=DEV, weights_only=False)     # this pipeline's own file
    models = []
    for sd_ in ck['fold']:
        m = FoldHead(1292).to(DEV); m.load_state_dict(sd_); m.eval(); models.append(m)
    return models, ck['fold_scaler']['m'], ck['fold_scaler']['sd']


def fold_scores(models, X, sc_m, sc_sd, clip):
    """Per-seed folding predictions. clip=20 is the Stage 4 evaluation setting, clip=10 Stage 3b's."""
    Xs = np.clip((X.astype(np.float32) - sc_m) / sc_sd, -clip, clip).astype(np.float32)
    return np.stack([predict(m, Xs) for m in models])


# ═══════════════════════════════════════════════════════════════ statistics
def spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)


def boot_ci(y, p, B, seed=0):
    from scipy.stats import spearmanr
    rng = np.random.default_rng(seed); v = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 2:
            v.append(spearmanr(y[i], p[i]).statistic)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def sign_test_two_sided(wins, n):
    """Exact two-sided binomial sign test, p(X>=wins or X<=n-wins) under p=0.5."""
    k = max(wins, n - wins)
    tail = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


# ═══════════════════════════════════════════════════════════════ binding cross-validation
MODES = ('original', 'corrected')


def position_splits(X, y, groups, n_splits, mode, seed):
    """Folds that hold out whole positions.
    original  — sklearn GroupKFold: deterministic, so every seed gets the SAME partition (Stages 3b–3d).
    corrected — positions shuffled with the seed before assignment (the Stage 3e procedure)."""
    if mode == 'original':
        from sklearn.model_selection import GroupKFold
        return list(GroupKFold(n_splits=n_splits).split(X, y, groups))
    if mode != 'corrected':
        raise ValueError(mode)
    pos = np.array(sorted(np.unique(groups)))
    fold_of = {p: i % n_splits for i, p in enumerate(np.random.default_rng(seed).permutation(pos))}
    f = np.array([fold_of[p] for p in groups])
    return [(np.where(f != k)[0], np.where(f == k)[0]) for k in range(n_splits)]


def inner_validation(groups_tr, seed):
    """Inner early-stopping split, also by position, carved from the training fold."""
    ug = np.unique(groups_tr); rs = np.random.default_rng(seed); rs.shuffle(ug)
    vg = set(ug[:max(1, len(ug) // 6)])
    return np.array([g in vg for g in groups_tr])


def _bind_fit_predict(Xd, yd, fit, val, te, model_seeds, epochs):
    from sklearn.decomposition import PCA
    s0 = Scaler().fit(Xd[fit])
    pca = PCA(n_components=min(64, len(fit) - 1), whiten=True, random_state=0).fit(s0(Xd[fit]))
    proj = lambda A: np.clip(pca.transform(s0(A)), -10, 10).astype(np.float32)
    ms = [train(BindHead, proj(Xd[fit]), yd[fit], proj(Xd[val]), yd[val], epochs=epochs, bs=256,
                seed=s, guard=True) for s in model_seeds]
    ms = [m for m in ms if m is not None]
    if not ms:
        return np.full(len(te), yd[fit].mean())
    Zte = proj(Xd[te])
    return np.mean([predict(m, Zte) for m in ms], 0)


def eval_budget(B, XB, dom, n_pos, n_rows, seed=0, n_splits=7, model_seeds=1, epochs=60,
                mode='original', keep_oof=False):
    """Stage 3c protocol on a subsample: positions drawn first, then rows within them."""
    d = B[B.domain_key == dom]
    rng = np.random.default_rng(seed)
    pos = rng.permutation(d.pos.unique())[:n_pos]
    sub = d[d.pos.isin(pos)]
    if len(sub) > n_rows:
        sub = sub.sample(n_rows, random_state=seed)
    if sub.pos.nunique() < n_splits + 1:
        return None
    Xd = XB[sub.index.values]; yd = sub.ddG_bind.values.astype(np.float32); groups = sub.pos.values
    oof = np.zeros(len(sub))
    for tr, te in position_splits(Xd, yd, groups, n_splits, mode, seed):
        vm = inner_validation(groups[tr], seed); fit, val = tr[~vm], tr[vm]
        if len(fit) < 20 or len(val) < 5:
            return None
        oof[te] = _bind_fit_predict(Xd, yd, fit, val, te, range(model_seeds), epochs)
    rmse = float(np.sqrt(np.mean((yd - oof) ** 2)))
    if rmse > 10 * float(np.std(yd)):
        return None                                   # diverged: never reported
    r = dict(domain=dom, mode=mode, n_pos=int(sub.pos.nunique()), n=int(len(sub)), seed=seed,
             n_splits=n_splits, epochs=epochs, rho=spearman(yd, oof), rmse=rmse,
             esm=spearman(yd, sub.esm_score.values))
    if keep_oof:
        r['_oof'], r['_y'] = oof, yd
    return r


def run_cv_3d(sub, XB, n_splits=7, seed=0, epochs=40, mode='original'):
    """Stage 3d protocol: one model per fold with seed=seed; reports the training rows it used."""
    if sub.pos.nunique() < n_splits + 1:
        return None
    Xd = XB[sub.index.values]; yd = sub.ddG_bind.values.astype(np.float32); groups = sub.pos.values
    oof = np.zeros(len(sub)); ntr = []
    for tr, te in position_splits(Xd, yd, groups, n_splits, mode, seed):
        vm = inner_validation(groups[tr], seed); fit, val = tr[~vm], tr[vm]
        if len(fit) < 20 or len(val) < 5:
            return None
        ntr.append(len(fit))
        oof[te] = _bind_fit_predict(Xd, yd, fit, val, te, [seed], epochs)
    rmse = float(np.sqrt(np.mean((yd - oof) ** 2)))
    if rmse > 10 * float(np.std(yd)):
        return None
    return dict(mode=mode, rho=spearman(yd, oof), rmse=rmse, train_rows=float(np.mean(ntr)), n=int(len(sub)),
                n_pos=int(sub.pos.nunique()), n_splits=n_splits, seed=seed,
                heldout_pos=float(sub.pos.nunique() / n_splits))


def run_cv_3e(sub, XBsub, n_splits=7, seed=0, epochs=40):
    """Stage 3e protocol: positions shuffled before fold assignment (already the corrected design)."""
    pos = np.array(sorted(sub.pos.unique()))
    if len(pos) < n_splits + 1:
        return None
    fold_of = {p: i % n_splits for i, p in enumerate(np.random.default_rng(seed).permutation(pos))}
    fold = np.array([fold_of[p] for p in sub.pos.values])
    y = sub.ddG_bind.values.astype(np.float32); oof = np.zeros(len(sub)); ntr = []; ntp = []
    for f in range(n_splits):
        te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
        if len(te) < 5 or len(tr) < 40:
            return None
        gtr = sub.pos.values[tr]; ug = np.unique(gtr)
        vg = set(np.random.default_rng(seed * 100 + f).permutation(ug)[:max(1, len(ug) // 6)])
        vm = np.array([g in vg for g in gtr]); fit, val = tr[~vm], tr[vm]
        if len(fit) < 20 or len(val) < 5:
            return None
        ntr.append(len(fit)); ntp.append(len(np.unique(sub.pos.values[fit])))
        oof[te] = _bind_fit_predict(XBsub, y, fit, val, te, [seed], epochs)
    rmse = float(np.sqrt(np.mean((y - oof) ** 2)))
    if rmse > 10 * float(np.std(y)):
        return None
    return dict(rho=spearman(y, oof), rmse=rmse, train_rows=float(np.mean(ntr)), train_pos=float(np.mean(ntp)),
                n=int(len(sub)), n_pos=int(len(pos)), seed=seed)
