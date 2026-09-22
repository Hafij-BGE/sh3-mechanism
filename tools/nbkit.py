"""Tiny helper that writes Jupyter notebooks from lists of cells (no nbformat needed)."""
import json, textwrap


def _src(text):
    lines = textwrap.dedent(text).strip('\n').split('\n')
    return [l + '\n' for l in lines[:-1]] + [lines[-1]]


def md(text):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': _src(text)}


def code(text):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': _src(text)}


def write(path, cells, gpu=False):
    meta = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python'}, 'colab': {'provenance': []}}
    if gpu:
        meta['accelerator'] = 'GPU'
        meta['colab']['gpuType'] = 'T4'
    json.dump({'cells': cells, 'metadata': meta, 'nbformat': 4, 'nbformat_minor': 5},
              open(path, 'w'), indent=1, ensure_ascii=False)


def setup(pid, title, gpu=False, pip=''):
    """The identical first code cell of every notebook."""
    L = ["# ── setup (identical in every notebook) ─────────────────────────────────────────",
         "ROOT   = '/content/drive/MyDrive/sh3_repro'   # the Drive folder from UPLOAD_GUIDE.md",
         "RESUME = True                                  # reuse finished steps after a disconnect",
         "",
         "import os, sys, json, time, importlib",
         "from google.colab import drive; drive.mount('/content/drive')"]
    if pip:
        L.append(f"os.system('pip -q install {pip}')")
    L += ["sys.path.insert(0, f'{ROOT}/code')",
          "import sh3_common as C; importlib.reload(C)",
          "import numpy as np, pandas as pd",
          f"R = C.Run(ROOT, '{pid}', '{title}', resume=RESUME)"]
    if gpu:
        L += ["if C.DEV == 'cpu':",
              "    print('WARNING: no GPU. Runtime -> Change runtime type -> T4 GPU.')"]
    L.append("print(C.env_info())")
    return code('\n'.join(L))
