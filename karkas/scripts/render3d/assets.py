import json, os, subprocess, sys
base = 'ph'
def files(a):
    p = f'{base}/{a}.files.json'
    if not os.path.exists(p):
        subprocess.run(['curl', '-s', '-m', '60', f'https://api.polyhaven.com/files/{a}', '-o', p], check=True)
    return json.load(open(p))
def get(url, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return
    subprocess.run(['curl', '-s', '-L', '--retry', '4', '-m', '900', url, '-o', dst], check=True)
def model(a, res='2k'):
    j = files(a)['gltf'][res]['gltf']
    d = f'{base}/{a}'
    get(j['url'], f'{d}/{a}.gltf')
    for rel, v in j.get('include', {}).items():
        get(v['url'], f'{d}/{rel}')
    print('model', a, flush=True)
def tex(a, res='2k'):
    j = files(a)
    d = f'{base}/tex/{a}'
    for key, name in (('Diffuse', 'diff'), ('nor_gl', 'nor'), ('Rough', 'rough'), ('Displacement', 'disp'), ('AO', 'ao')):
        if key in j and res in j[key]:
            v = j[key][res].get('jpg') or j[key][res].get('png')
            if v: get(v['url'], f'{d}/{name}.' + ('jpg' if 'jpg' in j[key][res] else 'png'))
    print('tex', a, flush=True)
def hdri(a, res='4k'):
    v = files(a)['hdri'][res]['hdr']
    get(v['url'], f'{base}/hdri/{a}_{res}.hdr'); print('hdri', a, flush=True)
kind, *names = sys.argv[1:]
for n in names:
    {'model': model, 'tex': tex, 'hdri': hdri}[kind](n)
