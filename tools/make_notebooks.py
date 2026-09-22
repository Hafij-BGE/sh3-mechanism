"""Regenerate every notebook in notebooks/ from the definitions in nb_A..nb_D.py.
Run from anywhere:  python tools/make_notebooks.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import nbkit, nb_A, nb_B, nb_C, nb_D, nb_ext
OUT = os.path.join(os.path.dirname(HERE), 'notebooks'); os.makedirs(OUT, exist_ok=True)
for mod in (nb_A, nb_B, nb_C, nb_ext, nb_D):
    for name, (cells, gpu) in mod.NOTEBOOKS.items():
        nbkit.write(os.path.join(OUT, f'{name}.ipynb'), cells, gpu)
        print(f'wrote notebooks/{name}.ipynb  ({len(cells)} cells, {"T4 GPU" if gpu else "CPU"})')
