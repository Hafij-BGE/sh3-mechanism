"""Regenerate every notebook in notebooks/ from the definitions in nb_A..nb_F.py.
Run from anywhere:  python tools/make_notebooks.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import nbkit, nb_A, nb_B, nb_C, nb_D, nb_ext, nb_F
OUT = os.path.join(os.path.dirname(HERE), 'notebooks'); os.makedirs(OUT, exist_ok=True)
for mod in (nb_A, nb_B, nb_C, nb_ext, nb_D, nb_F):
    for name, (cells, gpu) in mod.NOTEBOOKS.items():
        nbkit.write(os.path.join(OUT, f'{name}.ipynb'), cells, gpu)
        print(f'wrote notebooks/{name}.ipynb  ({len(cells)} cells, {"T4 GPU" if gpu else "CPU"})')

# keep the Drive upload folder in step with the repository (drive_upload/ is git-ignored)
import shutil, glob
ROOT = os.path.dirname(HERE); UP = os.path.join(ROOT, 'drive_upload')
if os.path.isdir(UP):
    os.makedirs(os.path.join(UP, 'code'), exist_ok=True); os.makedirs(os.path.join(UP, 'reference'), exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.ipynb')) + glob.glob(os.path.join(ROOT, 'src', '*.py')):
        shutil.copy2(f, os.path.join(UP, 'code'))
    for f in glob.glob(os.path.join(ROOT, 'reference', '*')):
        shutil.copy2(f, os.path.join(UP, 'reference'))
    print('copied notebooks, src/*.py and reference/ into drive_upload/')
