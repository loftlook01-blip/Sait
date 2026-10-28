"""
Рендер визуализаций: venv/bin/python render.py <сцена> [--raw] [--w 1600 --h 1200 --samples 128] [--out путь] [--opt key=value]
"""
import argparse, sys, time, os
sys.path.insert(0, os.path.dirname(__file__))
import lib, scenes

ap = argparse.ArgumentParser()
ap.add_argument('scene')
ap.add_argument('--raw', action='store_true')
ap.add_argument('--w', type=int, default=1600)
ap.add_argument('--h', type=int, default=1200)
ap.add_argument('--samples', type=int, default=128)
ap.add_argument('--out', default=None)
ap.add_argument('--opt', action='append', default=[])
a = ap.parse_args()
opts = dict(kv.split('=', 1) for kv in a.opt)
t = time.time()
lib.reset()
kw = {'raw': True} if a.raw else {}
kw.update(opts)
cfg = getattr(scenes, a.scene.replace('-', '_'))(**kw) or {}
out = a.out or f'out/{a.scene}{"-before" if a.raw else ""}.png'
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
lib.render(os.path.abspath(out), a.w, a.h, a.samples, cfg.get('exposure', 0))
print(f'✓ {out} за {time.time() - t:.0f} с')
