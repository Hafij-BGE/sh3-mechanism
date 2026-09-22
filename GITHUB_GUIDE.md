# GitHub guide (private repository)

The repository is this folder, `~/Documents/thesis/sh3 updated/`. It holds code, notebooks,
explanations and small result files. **Data never goes in**: `.gitignore` blocks COSMIC files,
raw archives, per-variant tables (`*.parquet`), embeddings and model weights. GitHub rejects
files over 100 MB anyway.

Git identity for this repository: **Hafijur Rahman, hafijurrahman.hr10@gmail.com**. It is set
locally for this folder only, so nothing else on your computer changes.

## One-time setup (you do this; it needs your GitHub login)

**1. GitHub account.** Sign in, or create an account, at github.com with
hafijurrahman.hr10@gmail.com.

**2. Create an empty private repository.** Click **+ → New repository**, name it
`sh3-mechanism-thesis`, choose **Private**, and **do not** add a README, .gitignore or licence.

**3. Create an SSH key on the laptop** (press Enter at every question):

```bash
ssh-keygen -t ed25519 -C "hafijurrahman.hr10@gmail.com"
```

**4. Give GitHub the public key.** Print it:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the whole line, then on GitHub go to **Settings → SSH and GPG keys → New SSH key**, paste it,
and save. Check that it works (answer `yes` the first time):

```bash
ssh -T git@github.com
```

**5. Connect this folder and push.** Replace `<your-username>` with your GitHub user name:

```bash
cd "$HOME/Documents/thesis/sh3 updated" && git remote add origin git@github.com:<your-username>/sh3-mechanism-thesis.git
```

```bash
cd "$HOME/Documents/thesis/sh3 updated" && git push -u origin main
```

## Everyday use

After a Colab run, download `MyDrive/sh3_repro/results/` into `sh3 updated/results/`, then:

```bash
cd "$HOME/Documents/thesis/sh3 updated" && git add -A && git status
```

Check that the list shows no `.tsv`, `.parquet`, `.npz`, `.pt` or `.zip` file, then:

```bash
cd "$HOME/Documents/thesis/sh3 updated" && git commit -m "Results of the Colab run" && git push
```

## Opening the notebooks in Colab

The simplest way with a private repository is from **Drive**: upload `notebooks/*.ipynb` and
`src/*.py` into `MyDrive/sh3_repro/code/` (see `UPLOAD_GUIDE.md`). Opening straight from GitHub
also works: in Colab choose **File → Open notebook → GitHub**, tick **Include private repos**, and
authorise Colab once.

## If you change a notebook

The notebooks are generated from `tools/nb_*.py`. Either edit those files and run
`python3 tools/make_notebooks.py`, or edit the notebook directly in Colab. If you edit in Colab,
download the edited notebook back into `notebooks/` before you commit, or the two will drift apart.
