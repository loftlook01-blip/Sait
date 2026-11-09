"""
Фотореалистичный режим сцен: реальное небо (HDRI), сканированные ели и подрост, трава из пучков-моделей,
фототекстуры профлиста, досок, настила и лесной земли (Poly Haven, CC0).

Подменяет функции окружения в ext.py (небо, землю, траву, лес), поэтому все сцены и ракурсы из ext.py
работают без изменений. Ассеты скачиваются скриптом assets.py в папку из переменной KARKAS_ASSETS.
Модели берутся в формате glTF (только данные, без встроенного кода).
"""
import math
import os
import random

import bpy
from mathutils import Matrix, Vector

import ext
import lib
from lib import mat, srgb

A = os.environ.get('KARKAS_ASSETS', 'assets')


def P(*p):
    return os.path.join(A, *p)


# Положение солнца в HDRI (азимут от +Y к +X, как у Nishita в ext.py), измерено hdri_sun.py
HDRI_DAY = ('kloofendal_48d_partly_cloudy_puresky_4k.hdr', -55.8)
HDRI_EVE = ('belfast_sunset_puresky_4k.hdr', -52.3)
HDRI_INT = ('misty_pines_4k.hdr', 0.0)

_img = {}


def img(path, color=True):
    key = (path, color)
    if key not in _img:
        im = bpy.data.images.load(path, check_existing=True)
        if path.endswith('.hdr') or path.endswith('.exr'):
            im.colorspace_settings.name = 'Linear Rec.709'
        else:
            im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
        _img[key] = im
    return _img[key]


# ───────────────────────── Материалы из фототекстур ─────────────────────────

def mat_tex(name, tex, size_m, tint=None, tint_mix=1.0, sat=1.0, val=1.0, rough_add=0.0, rough_mul=1.0,
            bump=0.35, rot90=False, metal=0.0, coat=0.0):
    """Текстура с кубической (box) проекцией в координатах объекта — не нужны UV-развёртки."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    n, l, b = nt.nodes, nt.links, nt.nodes['Principled BSDF']
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    s = 1.0 / size_m
    mp.inputs['Scale'].default_value = (s, s, s)
    if rot90:
        mp.inputs['Rotation'].default_value = (0, math.radians(90), 0)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    folder = P('tex', tex)

    def tx(fn, color):
        t = n.new('ShaderNodeTexImage')
        t.image = img(os.path.join(folder, fn), color)
        t.projection = 'BOX'
        t.projection_blend = 0.2
        l.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t

    col = tx('diff.jpg', True).outputs['Color']
    hsv = n.new('ShaderNodeHueSaturation')
    hsv.inputs['Saturation'].default_value = sat
    hsv.inputs['Value'].default_value = val
    l.new(col, hsv.inputs['Color'])
    col = hsv.outputs['Color']
    if tint:
        mix = n.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = tint_mix
        l.new(col, mix.inputs['A'])
        mix.inputs['B'].default_value = (*srgb(tint), 1)
        col = mix.outputs['Result']
    l.new(col, b.inputs['Base Color'])
    if os.path.exists(os.path.join(folder, 'rough.jpg')):
        r = tx('rough.jpg', False)
        mm = n.new('ShaderNodeMath')
        mm.operation = 'MULTIPLY_ADD'
        mm.use_clamp = True
        mm.inputs[1].default_value = rough_mul
        mm.inputs[2].default_value = rough_add
        l.new(r.outputs['Color'], mm.inputs[0])
        l.new(mm.outputs[0], b.inputs['Roughness'])
    hfile = 'disp.jpg' if os.path.exists(os.path.join(folder, 'disp.jpg')) else 'rough.jpg'
    h = tx(hfile, False)
    bn = n.new('ShaderNodeBump')
    bn.inputs['Strength'].default_value = bump
    bn.inputs['Distance'].default_value = 0.01
    l.new(h.outputs['Color'], bn.inputs['Height'])
    l.new(bn.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    return m


_mats = {}


def M(key):
    """Библиотека реалистичных материалов (создаются по требованию)."""
    if key in _mats:
        return _mats[key]
    f = {
        'metal_black': lambda: mat_tex('r_metal_black', 'box_profile_metal_sheet', 2.0, tint='#1a1c1e', sat=0.0, val=0.55, rough_mul=0.6, rough_add=0.25, metal=0.6, bump=0.6),
        'metal_graphite': lambda: mat_tex('r_metal_graphite', 'box_profile_metal_sheet', 2.0, tint='#4a4f52', sat=0.0, val=0.8, rough_mul=0.6, rough_add=0.25, metal=0.55, bump=0.6),
        'roof': lambda: mat_tex('r_roof', 'box_profile_metal_sheet', 2.0, tint='#202325', sat=0.0, val=0.5, rough_mul=0.5, rough_add=0.22, metal=0.7, bump=0.8),
        'larch': lambda: mat_tex('r_larch', 'wood_planks', 1.5, tint='#f3d9b4', tint_mix=0.5, sat=0.62, val=1.7, rot90=True, bump=0.3, coat=0.1),
        'larch_h': lambda: mat_tex('r_larch_h', 'wood_planks', 1.5, tint='#f3d9b4', tint_mix=0.5, sat=0.62, val=1.7, bump=0.3, coat=0.1),
        'charred': lambda: mat_tex('r_charred', 'black_painted_planks', 1.6, bump=0.4),
        'white': lambda: mat_tex('r_white', 'white_planks_clean', 1.8, tint='#f3efe7', tint_mix=0.6, sat=0.5, val=1.2, bump=0.3),
        'grey_boards': lambda: mat_tex('r_grey_boards', 'wood_planks_grey', 1.5, rot90=True, bump=0.4),
        'deck': lambda: mat_tex('r_deck', 'wood_floor_deck', 1.8, sat=0.5, val=1.05, bump=0.4),
        'ground': lambda: mat_tex('r_ground', 'forest_ground_04', 3.15, sat=0.9, val=0.9, bump=0.6),
        'grass_ground': lambda: mat_tex('r_grass_ground', 'sparse_grass', 2.0, tint='#6f8a3a', tint_mix=0.35, sat=1.0, val=0.9, bump=0.4),
        'lining': lambda: mat_tex('r_lining', 'wood_planks', 1.5, tint='#f1dcbc', tint_mix=0.7, sat=0.6, val=1.45, rot90=True, rough_add=0.15, bump=0.2),
        'floor': lambda: mat_tex('r_floor', 'wood_floor_deck', 1.8, tint='#d9b38a', tint_mix=0.4, sat=0.75, val=1.15, rough_mul=0.6, bump=0.2, coat=0.25),
    }[key]
    _mats[key] = f()
    return _mats[key]


# Какие процедурные материалы ext.py чем заменить (по началу имени материала)
REMAP = [
    ('clad_black', 'metal_black'), ('clad_graphite', 'metal_graphite'), ('clad_wood', 'larch'),
    ('clad_charred', 'charred'), ('clad_white', 'white'), ('roof', 'roof'),
    ('larch_v', 'larch_h'), ('larch', 'larch'), ('post', 'larch_h'), ('tframe', 'larch_h'),
    ('deck', 'deck'), ('int_plank', 'floor'), ('int_lining', 'lining'),
    ('lining', 'lining'), ('ifloor', 'floor'), ('hb', 'larch_h'),
]


def retexture():
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        for slot in o.material_slots:
            m = slot.material
            if not m or m.name.startswith('r_'):
                continue
            for prefix, key in REMAP:
                if m.name.startswith(prefix):
                    slot.material = M(key)
                    break


# ───────────────────────── Небо и свет ─────────────────────────

def world(hdri, rot=0.0, strength=1.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('world')
    sc.world = w
    w.use_nodes = True
    n, l = w.node_tree.nodes, w.node_tree.links
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(rot))
    env = n.new('ShaderNodeTexEnvironment')
    env.image = img(P('hdri', hdri), True)
    l.new(tc.outputs['Generated'], mp.inputs['Vector'])
    l.new(mp.outputs['Vector'], env.inputs['Vector'])
    l.new(env.outputs['Color'], n['Background'].inputs['Color'])
    n['Background'].inputs['Strength'].default_value = strength
    w.mist_settings.start = 25
    w.mist_settings.depth = 160
    w.mist_settings.falloff = 'QUADRATIC'


def setup_render(eve=False):
    sc = bpy.context.scene
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast' if not eve else 'AgX - Base Contrast'
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transparent_max_bounces = 24  # хвоя с альфа-каналом
    sc.cycles.adaptive_threshold = 0.03
    sc.render.film_transparent = False


def real_ext_setup(sun_elev=22, sun_rot=210, mist=0.3, sun_strength=4.5, eve=False):
    setup_render(eve)
    name, az = HDRI_EVE if eve else HDRI_DAY
    world(name, rot=-(sun_rot + az), strength=0.7 if eve else 1.0)  # проверено hdri_check: солнце в азимуте sun_rot
    if eve:
        ext.mist_comp(color='#56657a', amount=0.25)
    else:
        ext.mist_comp(color='#c3cfd6', amount=0.18)
    real_ground()


def real_ground(size=500):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = 'ground'
    g.data.materials.append(M('ground'))
    # мягкий рельеф, чтобы горизонт не был идеально ровным
    sub = g.modifiers.new('sub', 'SUBSURF')
    sub.subdivision_type = 'SIMPLE'
    sub.levels = sub.render_levels = 6
    tex = bpy.data.textures.new('ground_relief', 'CLOUDS')
    tex.noise_scale = 25
    d = g.modifiers.new('relief', 'DISPLACE')
    d.texture = tex
    d.strength = 1.2
    d.texture_coords = 'GLOBAL'
    # в центре (поляна) рельеф гасим: вершинная группа по расстоянию
    vg = g.vertex_groups.new(name='far')
    for v in g.data.vertices:
        r = math.hypot(v.co.x, v.co.y)
        vg.add([v.index], min(1.0, max(0.0, (r - 18) / 30)), 'REPLACE')
    d.vertex_group = 'far'
    g.location.z = -0.05
    return g


# ───────────────────────── Растительность ─────────────────────────

_src = {}


def load_gltf(name):
    """Импортирует glTF (данные без кода) и прячет исходники в отдельную, не отображаемую коллекцию."""
    if name in _src:
        return _src[name]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=P(name, f'{name}.gltf'))
    objs = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new(f'src_{name}')
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    meshes = [o for o in objs if o.type == 'MESH']
    for o in meshes:
        for slot in o.material_slots:  # хвоя/листья: двусторонние, с альфой
            m = slot.material
            if m and m.node_tree:
                b = m.node_tree.nodes.get('Principled BSDF')
                if b:
                    b.inputs['Subsurface Weight'].default_value = 0.0
    _src[name] = (meshes, col)
    return _src[name]


def instance(name, loc, rot_z, scale, which=None, rnd=None):
    meshes, _ = load_gltf(name)
    src = which if which is not None else (rnd or random).choice(meshes)
    o = src.copy()  # копия объекта ссылается на тот же меш — инстанс
    o.parent = None
    bpy.context.scene.collection.objects.link(o)
    base = src.matrix_world.copy()
    o.matrix_world = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Scale(scale, 4) @ base
    return o


def real_forest(keepout, seed=1, ring=(11, 75), n=900, mix=None, hmin=17, hmax=28, keep=None):
    """Лес из сканированных елей + подрост, кусты и папоротник по опушке."""
    rnd = random.Random(seed)
    firs = load_gltf('fir_tree_01')[0]
    saps = load_gltf('fir_sapling_medium')[0]
    placed = 0
    tries = 0
    target = 650
    pts = []
    r0 = ring[0] + 2
    while placed < target and tries < target * 40:
        tries += 1
        a = rnd.random() * math.tau
        r = r0 + (max(ring[1], 110) - r0) * math.sqrt(rnd.random())
        x, y = math.cos(a) * r, math.sin(a) * r
        if keepout(x, y) or any((x - px) ** 2 + (y - py) ** 2 < 7 for px, py in pts[-300:]):
            continue
        pts.append((x, y))
        s = rnd.uniform(0.75, 1.3)
        instance('fir_tree_01', (x, y, -0.1), rnd.random() * math.tau, s, rnd.choice(firs))
        placed += 1
    # опушка: подрост, кусты, папоротник, камни
    edge = 0
    tries = 0
    while edge < 70 and tries < 4000:
        tries += 1
        a = rnd.random() * math.tau
        r = ring[0] + rnd.uniform(-1.5, 4.5)
        x, y = math.cos(a) * r * 1.15, math.sin(a) * r
        if keepout(x, y):
            continue
        k = rnd.random()
        if k < 0.35:
            instance('fir_sapling_medium', (x, y, -0.05), rnd.random() * math.tau, rnd.uniform(0.35, 0.9), rnd.choice(saps))
        elif k < 0.65:
            instance(rnd.choice(['shrub_02', 'shrub_02', 'shrub_03']), (x, y, -0.05), rnd.random() * math.tau, rnd.uniform(0.6, 1.3), rnd=rnd)
        elif k < 0.92:
            for j in range(3):
                instance('fern_02', (x + rnd.uniform(-0.8, 0.8), y + rnd.uniform(-0.8, 0.8), -0.03), rnd.random() * math.tau, rnd.uniform(0.8, 1.5), rnd=rnd)
        else:
            instance('rock_moss_set_01', (x, y, -0.2), rnd.random() * math.tau, rnd.uniform(0.4, 0.8), rnd=rnd)
        edge += 1


def real_grass(center=(0, 0), size=(30, 24), count=9000, children=40, length=0.16, seed=1, palette=None):
    """Газон-поляна: пучки травы из моделей, раскиданные частицами (инстансы)."""
    g1 = load_gltf('grass_medium_01')[1]
    g2 = load_gltf('grass_medium_02')[1]
    gcol = bpy.data.collections.new('grass_set')
    for c in (g1, g2):
        for o in c.objects:
            if o.type == 'MESH':
                gcol.objects.link(o)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1, fill_type='NGON', location=(center[0], center[1], 0.0))
    p = bpy.context.active_object
    p.name = 'lawn'
    p.scale = (size[0] / 2, size[1] / 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    # неровный край поляны
    rnd = random.Random(seed)
    for v in p.data.vertices:
        if v.co.length > 0.5:
            v.co.x *= rnd.uniform(0.88, 1.08)
            v.co.y *= rnd.uniform(0.88, 1.08)
    p.data.materials.append(M('grass_ground'))
    p.location.z = 0.005
    ps = p.modifiers.new('grass', 'PARTICLE_SYSTEM').particle_system
    s = ps.settings
    s.type = 'HAIR'
    s.count = int(size[0] * size[1] * 55)
    s.hair_length = 1.0
    s.render_type = 'COLLECTION'
    s.instance_collection = gcol
    s.use_collection_pick_random = True
    s.particle_size = 1.35
    s.size_random = 0.5
    s.use_advanced_hair = True
    s.use_rotations = True
    s.rotation_mode = 'GLOB_Z'
    s.phase_factor_random = 2.0
    s.distribution = 'RAND'
    ps.seed = seed
    return p


def real_sky_interior(**kw):
    setup_render(False)
    world(HDRI_INT[0], rot=kw.get('rot', 90), strength=1.2)


_INTERIOR = {'on': False}


def patch():
    ext.ext_setup = real_ext_setup
    ext.forest = real_forest
    ext.grass = real_grass
    ext.ground = lambda size=400: (None if _INTERIOR['on'] else real_ground(size))
    orig_sky = ext.sky

    def sky(*a, **kw):  # sky() напрямую вызывают только интерьеры
        _INTERIOR['on'] = True
        real_sky_interior()
        sun = None
        return sun
    ext.sky = sky
    # в интерьерах лес и трава за окном — это фото (HDRI), 3D не нужно
    ext_forest = ext.forest
    ext_grass = ext.grass
    ext.forest = lambda *a, **kw: None if _INTERIOR['on'] else ext_forest(*a, **kw)
    ext.grass = lambda *a, **kw: None if _INTERIOR['on'] else ext_grass(*a, **kw)


def hdri_check(**kw):
    """Тест направления солнца: столб на земле, вид сверху. Солнце задано в азимуте 90° (на +X)."""
    real_ext_setup(sun_rot=90)
    lib.box('pole', (0.3, 0.3, 4), (0, 0, 0), mat('pole', '#ff3030'))
    lib.box('marker_x', (1, 0.2, 0.05), (5, 0, 0), mat('mx', '#3030ff'))
    c = lib.camera((0.01, -14, 9), (0, 0, 0.5), lens=30)
    return dict(exposure=0)
