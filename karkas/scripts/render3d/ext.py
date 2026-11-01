"""
Экстерьерные сцены модульных домов (Blender / Cycles): дом-барнхаус, лес, трава, небо.
Запуск: venv/bin/python render.py <сцена> --w 1600 --h 1200 --samples 64 --out out/<имя>.png
Единицы — метры. X — вдоль конька дома, Y — вглубь, Z — вверх.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector
from lib import (mat, srgb, _nodes, mat_wood, mat_noise, mat_glass, mat_emit, mat_plank,
                 box, cyl, sphere, soft, camera, area, point, pendant, rug, plant)

# ───────────────────────── Материалы ─────────────────────────

def mat_ribbed(name, hexcolor, pitch=0.2, axis='X', rough=0.45, metal=0.55, strength=0.25):
    """Профлист / фальц: полосы-рёбра через Wave Texture + Bump."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    b.inputs['Base Color'].default_value = (*srgb(hexcolor), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    tc = n.new('ShaderNodeTexCoord')
    wave = n.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = axis
    wave.wave_profile = 'SAW'
    wave.inputs['Scale'].default_value = 1.0 / pitch
    wave.inputs['Distortion'].default_value = 0
    l.new(tc.outputs['Object'], wave.inputs['Vector'])
    # Wave Texture масштабирует сам, но scale в объектных координатах ~ 1/шаг
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.86
    ramp.color_ramp.elements[1].position = 0.95
    l.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = strength
    bump.inputs['Distance'].default_value = 0.02
    l.new(ramp.outputs['Color'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_boards(name, light, dark, pitch=0.14, axis='X', rough=0.6, grain='Z'):
    """Вертикальная доска (планкен): волокна + швы + случайный тон доски."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = tuple(1.0 if a == grain else 40.0 for a in 'XYZ')
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 6
    nz.inputs['Distortion'].default_value = 0.4
    l.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[0].color = (*srgb(dark), 1)
    ramp.color_ramp.elements[1].color = (*srgb(light), 1)
    l.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    # доски: случайная яркость полосы
    wave = n.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = axis
    wave.wave_profile = 'SAW'
    wave.inputs['Scale'].default_value = 1.0 / pitch
    wave.inputs['Distortion'].default_value = 0
    l.new(tc.outputs['Object'], wave.inputs['Vector'])
    seam = n.new('ShaderNodeValToRGB')
    seam.color_ramp.elements[0].position = 0.93
    seam.color_ramp.elements[1].position = 0.97
    seam.color_ramp.elements[0].color = (1, 1, 1, 1)
    seam.color_ramp.elements[1].color = (0.25, 0.25, 0.25, 1)
    l.new(wave.outputs['Fac'], seam.inputs['Fac'])
    mix = n.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    l.new(ramp.outputs['Color'], mix.inputs['A'])
    l.new(seam.outputs['Color'], mix.inputs['B'])
    l.new(mix.outputs['Result'], b.inputs['Base Color'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    l.new(seam.outputs['Color'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = rough
    return m


def mat_ground(name='ground'):
    """Земля: зелень с пятнами сухой травы и хвои."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 0.35
    nz.inputs['Detail'].default_value = 10
    nz.inputs['Roughness'].default_value = 0.65
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.35
    cr.elements[0].color = (*srgb('#3e4f22'), 1)
    cr.elements[1].position = 0.7
    cr.elements[1].color = (*srgb('#6b6a35'), 1)
    e = cr.elements.new(0.52)
    e.color = (*srgb('#506227'), 1)
    l.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.95
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    nz2 = n.new('ShaderNodeTexNoise')
    nz2.inputs['Scale'].default_value = 40
    l.new(tc.outputs['Object'], nz2.inputs['Vector'])
    l.new(nz2.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_grass_hair(name='grass', palette=('#41561f', '#5c7a2a', '#7d8f3a', '#9a9450')):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    hi = n.new('ShaderNodeHairInfo')
    ramp = n.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*srgb(palette[0]), 1)
    cr.elements[1].position = 0.86
    cr.elements[1].color = (*srgb(palette[3]), 1)
    for pos, c in ((0.35, palette[1]), (0.66, palette[2])):
        e = cr.elements.new(pos)
        e.color = (*srgb(c), 1)
    l.new(hi.outputs['Random'], ramp.inputs['Fac'])
    # темнее у корня
    grad = n.new('ShaderNodeValToRGB')
    grad.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1)
    grad.color_ramp.elements[1].position = 0.6
    l.new(hi.outputs['Intercept'], grad.inputs['Fac'])
    mix = n.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    l.new(ramp.outputs['Color'], mix.inputs['A'])
    l.new(grad.outputs['Color'], mix.inputs['B'])
    l.new(mix.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.6
    b.inputs['Subsurface Weight'].default_value = 0.0
    b.inputs['Transmission Weight'].default_value = 0.0
    b.inputs['Sheen Weight'].default_value = 0.3
    return m


def mat_foliage(name, c1, c2, scale=3.0, holes=120.0, cutoff=0.47):
    """Хвоя/листва: шумовой цвет + рваные края (прозрачность по шуму) — пушистый силуэт без текстур."""
    m = mat_noise(name, c1, c2, scale=scale, rough=0.7, bump=0.3)
    nt, n, l, b = _nodes(m)
    b.inputs['Sheen Weight'].default_value = 0.4
    out = n['Material Output']
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = holes
    nz.inputs['Detail'].default_value = 4
    nz.inputs['Roughness'].default_value = 0.7
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    th = n.new('ShaderNodeMath')
    th.operation = 'GREATER_THAN'
    th.inputs[1].default_value = cutoff
    l.new(nz.outputs['Fac'], th.inputs[0])
    tr = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    l.new(th.outputs[0], mix.inputs['Fac'])
    l.new(tr.outputs[0], mix.inputs[1])
    l.new(b.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs['Surface'])
    return m


# ───────────────────────── Окружение ─────────────────────────

def sky(sun_elev=24, sun_rot=215, strength=1.0, sun_strength=4.5, sun_color='#fff0dc', sun_dir=None):
    sc = bpy.context.scene
    world = bpy.data.worlds.new('world')
    sc.world = world
    world.use_nodes = True
    n = world.node_tree.nodes
    l = world.node_tree.links
    bg = n['Background']
    s = n.new('ShaderNodeTexSky')
    s.sky_type = 'NISHITA'
    s.sun_elevation = math.radians(sun_elev)
    s.sun_rotation = math.radians(sun_rot)
    s.altitude = 200
    s.air_density = 1.0
    s.dust_density = 0.6
    s.sun_disc = False
    l.new(s.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.active_object
    if sun_dir is None:
        e, r = math.radians(sun_elev), math.radians(sun_rot)
        # Nishita: rotation 0 → солнце на +Y, 90° → на +X. Свет идёт от солнца.
        sun_dir = (-math.sin(r) * math.cos(e), -math.cos(r) * math.cos(e), -math.sin(e))
    sun.rotation_euler = Vector(sun_dir).normalized().to_track_quat('-Z', 'Y').to_euler()
    sun.data.energy = sun_strength
    sun.data.angle = math.radians(1.5)
    sun.data.color = srgb(sun_color)
    world.mist_settings.start = 18
    world.mist_settings.depth = 140
    world.mist_settings.falloff = 'QUADRATIC'
    return sun


def mist_comp(color='#b9c8c8', amount=0.3):
    """Воздушная перспектива: смешиваем рендер с цветом дымки по проходу Mist."""
    sc = bpy.context.scene
    sc.view_layers[0].use_pass_mist = True
    sc.use_nodes = True
    tree = sc.node_tree
    for nd in list(tree.nodes):
        tree.nodes.remove(nd)
    rl = tree.nodes.new('CompositorNodeRLayers')
    mul = tree.nodes.new('CompositorNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = amount
    tree.links.new(rl.outputs['Mist'], mul.inputs[0])
    mix = tree.nodes.new('CompositorNodeMixRGB')
    mix.inputs[2].default_value = (*srgb(color), 1)
    tree.links.new(mul.outputs[0], mix.inputs[0])
    tree.links.new(rl.outputs['Image'], mix.inputs[1])
    out = tree.nodes.new('CompositorNodeComposite')
    tree.links.new(mix.outputs[0], out.inputs[0])


def ground(size=400):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = 'ground'
    g.data.materials.append(mat_ground())
    return g


def grass(center=(0, 0), size=(30, 24), count=9000, children=40, length=0.16, seed=1, palette=None):
    """Трава частицами-волосами на отдельном участке."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(center[0], center[1], 0.002))
    p = bpy.context.active_object
    p.name = 'grass_patch'
    p.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.modifier_add(type='SUBSURF')
    p.modifiers[-1].subdivision_type = 'SIMPLE'
    p.modifiers[-1].levels = 3
    p.data.materials.append(mat_ground('ground_patch'))
    p.data.materials.append(mat_grass_hair(palette=palette) if palette else mat_grass_hair())
    ps_mod = p.modifiers.new('grass', 'PARTICLE_SYSTEM')
    ps = ps_mod.particle_system
    s = ps.settings
    s.type = 'HAIR'
    s.count = count
    s.hair_length = length
    s.use_advanced_hair = False
    s.material = 2
    s.render_type = 'PATH'
    s.root_radius = 1.0
    s.tip_radius = 0.0
    s.radius_scale = 0.0035
    s.child_type = 'INTERPOLATED'
    s.child_percent = 4
    s.rendered_child_count = children
    s.child_radius = 0.25
    s.child_length = 1.0
    s.child_length_threshold = 0.4
    s.clump_factor = 0.15
    s.roughness_endpoint = 0.06
    s.roughness_end_shape = 1.0
    s.roughness_2 = 0.02
    s.kink = 'NO'
    ps.seed = seed
    s.use_modifier_stack = True
    return p


def _displace(o, scale=0.6, strength=0.5, levels=3, tex_type='CLOUDS', seed=0):
    sub = o.modifiers.new('sub', 'SUBSURF')
    sub.levels = levels
    sub.render_levels = levels
    tex = bpy.data.textures.new(f'tx{seed}', tex_type)
    if hasattr(tex, 'noise_scale'):
        tex.noise_scale = scale
    if hasattr(tex, 'noise_depth'):
        tex.noise_depth = 2
    d = o.modifiers.new('disp', 'DISPLACE')
    d.texture = tex
    d.strength = strength
    d.mid_level = 0.5
    d.texture_coords = 'GLOBAL'
    for p in o.data.polygons:
        p.use_smooth = True
    return o


_proto = {}


def _apply_mods(o):
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def _join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    o.location = (0, 0, 0)
    return o


def spruce_proto(seed, h=1.0):
    """Ель: ярусы конусов с шумом. Единичная высота, масштабируется при расстановке."""
    rnd = random.Random(seed)
    bark = mat_noise('bark_spruce', '#3b2e24', '#5a4635', scale=30, rough=0.9, bump=0.4)
    needles = mat_foliage('needles', '#16241a', '#2a3f2c', scale=6, holes=220, cutoff=0.44)
    parts = [cyl('trunk', 0.016, 0.8, (0, 0, 0), bark, verts=12)]
    tiers = 11
    for i in range(tiers):
        t = i / tiers
        z0 = 0.08 + t * 0.82
        r = 0.2 * (1 - t) ** 1.05 + 0.025
        hh = 0.17 * (1 - t * 0.4)
        c = cyl(f'tier{i}', r, hh, (rnd.uniform(-0.008, 0.008), rnd.uniform(-0.008, 0.008), z0), needles, verts=16, r2=0.004)
        _displace(c, scale=0.035, strength=0.05, levels=3, seed=seed * 10 + i)
        parts.append(c)
        core = cyl(f'core{i}', r * 0.82, hh * 0.85, (0, 0, z0 + hh * 0.05), mat('needle_core', '#101a12', rough=0.9), verts=12, r2=0.003)
        _displace(core, scale=0.035, strength=0.04, levels=2, seed=seed * 10 + i + 5)
        parts.append(core)
    for p in parts:
        _apply_mods(p)
    o = _join(parts, f'spruce{seed}')
    return o


def pine_proto(seed):
    """Сосна: высокий рыжий ствол, крона облаками наверху."""
    rnd = random.Random(seed)
    bark = mat_noise('bark_pine', '#6e3f22', '#a8653a', scale=24, rough=0.85, bump=0.4)
    needles = mat_foliage('pine_needles', '#1d301e', '#36502d', scale=5, holes=200, cutoff=0.44)
    parts = [cyl('trunk', 0.016, 0.92, (0, 0, 0), bark, verts=12, r2=0.008)]
    for i in range(12):
        a = rnd.random() * math.tau
        rr = rnd.uniform(0.0, 0.09)
        z = rnd.uniform(0.62, 0.92)
        s = sphere(f'cl{i}', rnd.uniform(0.045, 0.075), (math.cos(a) * rr, math.sin(a) * rr, z), needles, scale=(1, 1, 0.5))
        _displace(s, scale=0.05, strength=0.05, levels=2, seed=seed * 20 + i)
        parts.append(s)
        parts.append(sphere(f'core{i}', s.dimensions.x * 0.42, s.location, mat('needle_core', '#0b130d', rough=0.9), scale=(1, 1, 0.5)))
    for p in parts:
        _apply_mods(p)
    return _join(parts, f'pine{seed}')


def birch_proto(seed):
    rnd = random.Random(seed)
    bark = bpy.data.materials.get('bark_birch') or mat_noise('bark_birch', '#1c1c1a', '#ece9e1', scale=14, rough=0.6, bump=0.2)
    leaves = mat_foliage('birch_leaves', '#3d5420', '#62782e', scale=4, holes=150, cutoff=0.48)
    parts = [cyl('trunk', 0.012, 0.85, (0, 0, 0), bark, verts=10, r2=0.006)]
    for i in range(6):
        a = rnd.random() * math.tau
        rr = rnd.uniform(0.02, 0.09)
        z = rnd.uniform(0.5, 0.86)
        s = sphere(f'bl{i}', rnd.uniform(0.07, 0.12), (math.cos(a) * rr, math.sin(a) * rr, z), leaves, scale=(1, 1, 0.8))
        _displace(s, scale=0.04, strength=0.06, levels=2, seed=seed * 30 + i)
        parts.append(s)
    for p in parts:
        _apply_mods(p)
    return _join(parts, f'birch{seed}')


def protos():
    if not _proto:
        _proto['spruce'] = [spruce_proto(s) for s in (1, 2)]
        _proto['pine'] = [pine_proto(s) for s in (3, 4)]
        _proto['birch'] = [birch_proto(s) for s in (5,)]
        for lst in _proto.values():
            for o in lst:
                o.hide_render = True
                o.hide_viewport = True
    return _proto


def tree(kind, x, y, h, rnd):
    src = rnd.choice(protos()[kind])
    o = src.copy()  # общий меш — экономит память
    bpy.context.collection.objects.link(o)
    o.hide_render = False
    o.hide_viewport = False
    s = h * rnd.uniform(0.9, 1.1)
    o.scale = (s * rnd.uniform(0.85, 1.15), s * rnd.uniform(0.85, 1.15), s)
    o.location = (x, y, -0.05)
    o.rotation_euler = (rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), rnd.random() * math.tau)
    return o


def forest(keepout, seed=1, ring=(11, 75), n=900, mix=(0.52, 0.48, 0.0), hmin=17, hmax=28, keep=None):
    """Лес вокруг точки (0,0). keepout(x,y) → True, если дерево ставить нельзя (поляна, кадр)."""
    rnd = random.Random(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 20:
        tries += 1
        a = rnd.random() * math.tau
        r = ring[0] + (ring[1] - ring[0]) * math.sqrt(rnd.random())
        x, y = math.cos(a) * r, math.sin(a) * r
        if keepout(x, y):
            continue
        k = rnd.random()
        kind = 'spruce' if k < mix[0] else ('pine' if k < mix[0] + mix[1] else 'birch')
        h = rnd.uniform(hmin, hmax) * (0.75 if kind == 'birch' else 1)
        tree(kind, x, y, h, rnd)
        placed += 1


# ───────────────────────── Дом ─────────────────────────

def pent_mesh(name, W, H, R, x0, x1, m=None, z0=0.0, y0=0.0):
    """Призма с профилем «домик» (пятиугольник в плоскости YZ), вытянутая по X от x0 до x1."""
    prof = [(-W / 2, 0), (W / 2, 0), (W / 2, H), (0, H + R), (-W / 2, H)]
    verts = [(x0, y0 + y, z0 + z) for y, z in prof] + [(x1, y0 + y, z0 + z) for y, z in prof]
    faces = [(0, 1, 2, 3, 4)[::-1], (5, 6, 7, 8, 9)]
    for i in range(5):
        j = (i + 1) % 5
        faces.append((i, j, j + 5, i + 5))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if m:
        me.materials.append(m)
    return o


def cut(target, cutter):
    mod = target.modifiers.new('bool', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def cutbox(target, size, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2] + size[2] / 2))
    c = bpy.context.active_object
    c.scale = size
    bpy.ops.object.transform_apply(scale=True)
    cut(target, c)


CLAD = {
    'black': lambda: mat_ribbed('clad_black', '#0e0f10', pitch=0.18, axis='X', rough=0.55, metal=0.2),
    'graphite': lambda: mat_ribbed('clad_graphite', '#3a3d3e', pitch=0.18, axis='X', rough=0.55, metal=0.3),
    'wood': lambda: mat_boards('clad_wood', '#c99a66', '#9c6c40', pitch=0.12, axis='X'),
    'charred': lambda: mat_boards('clad_charred', '#2a2622', '#16130f', pitch=0.14, axis='X', rough=0.75),
    'white': lambda: mat_boards('clad_white', '#ece8e0', '#d9d3c8', pitch=0.14, axis='X', rough=0.7),
}


def window(x, y, z, w, h, axis='X', frame='#1a1a1a', glass=None, depth=0.12, mull=None):
    """Окно в стене. axis — вдоль какой оси лежит стена (X — длинная стена, Y — торец)."""
    fm = mat('wframe' + frame, frame, rough=0.4, metal=0.3)
    g = glass or mat('glass_ext', '#c4d0d0', rough=0.0, transmission=1.0, ior=1.5, spec=0.6)
    t = 0.06
    if axis == 'X':
        box('wg', (w, 0.02, h), (x, y, z), g)
        box('wf_t', (w, depth, t), (x, y, z + h - t), fm)
        box('wf_b', (w, depth, t), (x, y, z), fm)
        box('wf_l', (t, depth, h), (x - w / 2 + t / 2, y, z), fm)
        box('wf_r', (t, depth, h), (x + w / 2 - t / 2, y, z), fm)
        for mx in (mull or []):
            box('wf_m', (0.05, depth, h), (x - w / 2 + mx * w, y, z), fm)
    else:
        box('wg', (0.02, w, h), (x, y, z), g)
        box('wf_t', (depth, w, t), (x, y, z + h - t), fm)
        box('wf_b', (depth, w, t), (x, y, z), fm)
        box('wf_l', (depth, t, h), (x, y - w / 2 + t / 2, z), fm)
        box('wf_r', (depth, t, h), (x, y + w / 2 - t / 2, z), fm)
        for my in (mull or []):
            box('wf_m', (depth, 0.05, h), (x, y - w / 2 + my * w, z), fm)


def interior_glow(x0, x1, W, F, H, warm=1.0):
    """Тёплый интерьер за стеклом: светлый пол/стены и мягкий свет."""
    wood = mat_wood('int_wood', '#d9b98e', '#b08858', scale=2, rough=0.6)
    box('int_floor', (x1 - x0, W - 0.3, 0.02), ((x0 + x1) / 2, 0, F + 0.01), mat_plank('int_plank', '#c69c6d', '#9a7047'))
    box('int_back', (x1 - x0, 0.02, H), ((x0 + x1) / 2, W / 2 - 0.18, F), wood)
    if warm:
        area(((x0 + x1) / 2, 0, F + H - 0.2), (0, 0, 0), 1.6, 500 * warm, '#ffd9a8', size_y=1.2)


def modhouse(L=9.0, W=4.2, H=2.9, R=2.3, F=0.6, clad='black', portal=True, portal_side='+',
             deck=True, deck_w=2.4, deck_side='front', long_windows=None, roof='#1c1e1f',
             terrace=0.0, warm=1.0, x0=0.0, y0=0.0, rot=0.0, chimney=False, steps=True):
    """
    Модульный дом-барнхаус. Начало координат — центр пятна дома на земле.
    portal — деревянный портал-рамка вокруг остеклённого торца (как на фото проекта).
    terrace — длина крытой террасы под продолжением кровли (у торца x=+L/2).
    """
    objs_before = set(bpy.data.objects)
    cladm = CLAD[clad]()
    wood = mat_boards('larch', '#d8a874', '#ad7b4c', pitch=0.1, axis='Y', rough=0.55)
    wood_v = mat_boards('larch_v', '#d8a874', '#ad7b4c', pitch=0.1, axis='Z', rough=0.55, grain='X')
    roofm = mat_ribbed('roof', roof, pitch=0.5, axis='X', rough=0.45, metal=0.55, strength=0.4)
    dark = mat('pile', '#2a2b2c', rough=0.5, metal=0.6)
    xe = L / 2  # торец со стеклом
    body = pent_mesh('body', W, H, R, -L / 2, xe - (0.35 if portal else 0), cladm, z0=F)
    hollow = pent_mesh('hollow', W - 0.3, H - 0.25, R - 0.15, -L / 2 + 0.15, xe + 1.0 if portal else xe - 0.15, None, z0=F + 0.05)
    cut(body, hollow)
    # тёплый свет внутри + светлая обшивка
    box('in_floor', (L - 0.3, W - 0.3, 0.02), (0, 0, F + 0.05), mat_plank('int_plank', '#c69c6d', '#9a7047'))
    lining = mat_wood('int_lining', '#e6cfa8', '#cdb088', scale=2, rough=0.7)
    box('in_back', (L - 0.4, 0.02, H - 0.3), (0, W / 2 - 0.17, F + 0.05), lining)
    box('in_end', (0.02, W - 0.34, H - 0.3), (-L / 2 + 0.17, 0, F + 0.05), lining)
    box('in_ceil', (L - 0.4, W - 0.34, 0.02), (0, 0, F + H - 0.27), lining)
    # цоколь + сваи
    box('plinth', (L - 0.1, W - 0.1, F), (0, 0, 0), mat('plinth', '#1e1f20', rough=0.8))
    # окна длинной стороны (y = -W/2)
    lw = long_windows if long_windows is not None else [(-L / 2 + 1.6, 1.0, 2.0), (-L / 2 + 3.3, 1.0, 2.0)]
    for (wx, ww, wh) in lw:
        cutbox(body, (ww, 0.6, wh), (wx, -W / 2, F + 0.25))
    portal_d = 0.75
    if portal:
        # стекло торца утоплено, вокруг — деревянный портал
        tglass = mat('glass_ext', '#c4d0d0', rough=0.0, transmission=1.0, ior=1.5, spec=0.6)
        gx = xe - 0.35
        g = pent_mesh('gable_glass', W - 0.24, H - 0.12, R - 0.12, gx - 0.02, gx, tglass, z0=F + 0.06)
        fm = mat('wframe#1a1a1a', '#1a1a1a', rough=0.4, metal=0.3)
        # переплёты
        for yy in (-W / 2 + 0.12 + (W - 0.24) * k / 3 for k in range(4)):
            box('mul_v', (0.06, 0.06, H - 0.12), (gx, yy, F + 0.06), fm)
        box('mul_h', (0.06, W - 0.24, 0.06), (gx, 0, F + H - 0.12), fm)
        box('mul_b', (0.06, W - 0.24, 0.08), (gx, 0, F + 0.04), fm)
        # раскосы по скатам
        ang = math.atan2(R, W / 2)
        Ls = math.hypot(W / 2, R) - 0.1
        for sgn in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(gx, sgn * W / 4, F + H + R / 2 - 0.08))
            mb = bpy.context.active_object
            mb.scale = (0.06, Ls, 0.06)
            mb.rotation_euler = (sgn * -ang, 0, 0)
            mb.data.materials.append(fm)
        out = pent_mesh('portal', W + 0.36, H + 0.18, R + 0.2, gx - 0.1, xe + portal_d - 0.35, wood_v, z0=F - 0.12)
        inner = pent_mesh('portal_in', W - 0.06, H - 0.04, R - 0.06, gx - 0.5, xe + portal_d, None, z0=F + 0.02)
        cut(out, inner)
        interior_glow(xe - 4.0, gx - 0.05, W, F, H, warm)
        point((gx - 1.2, 0, F + 1.6), 500 * warm, '#ffcf96', 0.3)
        pendant(gx - 1.4, 0.3, F + H + R - 0.4, drop=1.5, r=0.2, power=30 * warm)
    else:
        # торец со стеклянной дверью
        cutbox(body, (0.6, 1.8, 2.3), (xe, -0.6, F + 0.1))
        window(xe - 0.1, -0.6, F + 0.1, 1.8, 2.3, axis='Y', mull=[0.5])
        if warm:
            point((xe - 1.5, -0.4, F + 1.6), 180 * warm, '#ffcf96', 0.3)
    for (wx, ww, wh) in lw:
        window(wx, -W / 2 + 0.08, F + 0.25, ww, wh, axis='X')
        if warm:
            point((wx, -W / 2 + 1.0, F + 1.6), 220 * warm, '#ffcf96', 0.3)
    # кровля
    ang = math.atan2(R, W / 2)
    over = 0.35
    slope = math.hypot(W / 2, R) + over
    RL = L + 0.3 + terrace + (0.4 if portal else 0)
    rx = (-L / 2 - 0.25 + xe + terrace + (0.45 if portal else 0.05)) / 2
    for sgn in (-1, 1):
        cy = sgn * (W / 4 + over / 2 * math.cos(ang))
        cz = F + H + R / 2 - over / 2 * math.sin(ang) + 0.06
        bpy.ops.mesh.primitive_cube_add(size=1, location=(rx, cy, cz))
        r_ = bpy.context.active_object
        r_.scale = (RL, slope, 0.07)
        r_.rotation_euler = (sgn * -ang, 0, 0)
        bpy.ops.object.transform_apply(scale=True)
        r_.data.materials.append(roofm)
    if portal:
        # портал прикрывает край крыши — ничего
        pass
    # терраса под кровлей
    if terrace > 0:
        tx0 = xe
        tx1 = xe + terrace
        box('terrace_floor', (terrace, W + 0.4, 0.06), ((tx0 + tx1) / 2, 0, F - 0.06), mat_plank('deck', '#b88a5a', '#8a6038'))
        post = mat_wood('post', '#d0a06c', '#a77748', scale=2)
        for xx in (tx1 - 0.1,):
            for yy in (-W / 2 + 0.05, W / 2 - 0.05):
                box('tpost', (0.14, 0.14, H), (xx, yy, F), post)
        # фронтон террасы — рамы
        pent_frame = pent_mesh('tframe', W + 0.2, H + 0.1, R + 0.1, tx1 - 0.18, tx1 + 0.02, post, z0=F - 0.05)
        inner = pent_mesh('tframe_in', W - 0.2, H - 0.12, R - 0.12, tx1 - 0.5, tx1 + 0.5, None, z0=F + 0.06)
        cut(pent_frame, inner)
        box('rail', (terrace, 0.06, 0.06), ((tx0 + tx1) / 2, -W / 2 - 0.05, F + 0.95), post)
        for k in range(int(terrace / 0.9) + 1):
            box('rail_p', (0.06, 0.06, 0.95), (tx0 + 0.3 + k * 0.9, -W / 2 - 0.05, F), post)
        # мебель террасы
        box('tchair', (0.6, 0.6, 0.45), (tx0 + 1.0, 0.6, F), mat('tchair', '#2e2c29', rough=0.7))
        plant(tx0 + 0.5, W / 2 - 0.6, 0.8)
        if warm:
            point(((tx0 + tx1) / 2, 0, F + H - 0.3), 80 * warm, '#ffcf96', 0.1)
    # настил и ступени перед длинной стороной
    if deck:
        dk = mat_plank('deck', '#b88a5a', '#8a6038')
        if deck_side == 'front':
            dx0, dx1 = (lw[0][0] - 1.2, xe + (portal_d if portal else 0.3))
            box('deck', (dx1 - dx0, deck_w, 0.05), ((dx0 + dx1) / 2, -W / 2 - deck_w / 2, F - 0.08), dk)
            box('deck_frame', (dx1 - dx0, deck_w - 0.1, F - 0.1), ((dx0 + dx1) / 2, -W / 2 - deck_w / 2, 0), mat('deck_under', '#1a1712', rough=1))
            if steps:
                n = 3
                for k in range(n):
                    box('step', (2.0, 0.34, 0.05), ((dx0 + dx1) / 2 + 0.6, -W / 2 - deck_w - 0.17 - k * 0.32, F - 0.08 - (k + 1) * F / (n + 1)), dk)
                    box('step_riser', (2.0, 0.3, F - (k + 1) * F / (n + 1) - 0.06), ((dx0 + dx1) / 2 + 0.6, -W / 2 - deck_w - 0.17 - k * 0.32, 0), mat('deck_under', '#1a1712', rough=1))
        else:  # у торца
            box('deck', (deck_w, W + 1.0, 0.05), (xe + deck_w / 2, 0, F - 0.08), dk)
    if chimney:
        cyl('chimney', 0.11, 1.4, (-L / 4, W / 6, F + H + R * 0.6), mat('chim', '#3a3a3a', rough=0.3, metal=0.9))
    # поворот/смещение всего дома
    new = [o for o in bpy.data.objects if o not in objs_before]
    if rot or x0 or y0:
        pivot = bpy.data.objects.new('house_pivot', None)
        bpy.context.collection.objects.link(pivot)
        for o in new:
            if o.parent is None:
                o.parent = pivot
        pivot.rotation_euler = (0, 0, math.radians(rot))
        pivot.location = (x0, y0, 0)
    return new


def gazebo(x0=0, y0=0, L=4.0, W=3.2, H=2.4, R=1.4, rot=0):
    """Беседка: деревянный каркас, кровля, стол."""
    before = set(bpy.data.objects)
    post = mat_wood('post', '#d0a06c', '#a77748', scale=2)
    roofm = mat_ribbed('roof', '#1c1e1f', pitch=0.5, axis='X', rough=0.45, metal=0.55, strength=0.4)
    box('gz_floor', (L + 0.4, W + 0.4, 0.25), (0, 0, 0), mat_plank('deck', '#b88a5a', '#8a6038'))
    for xx in (-L / 2, 0, L / 2):
        for yy in (-W / 2, W / 2):
            box('gz_post', (0.15, 0.15, H), (xx, yy, 0.25), post)
    for xx in (-L / 2, L / 2):
        fr = pent_mesh('gz_fr', W + 0.15, H + 0.1, R, xx - 0.08, xx + 0.08, post, z0=0.25)
        inn = pent_mesh('gz_in', W - 0.15, H - 0.1, R - 0.12, xx - 0.5, xx + 0.5, None, z0=0.3)
        cut(fr, inn)
    ang = math.atan2(R, W / 2)
    slope = math.hypot(W / 2, R) + 0.3
    for sgn in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, sgn * (W / 4 + 0.13), 0.25 + H + R / 2 - 0.1))
        r_ = bpy.context.active_object
        r_.scale = (L + 0.5, slope, 0.06)
        r_.rotation_euler = (sgn * -ang, 0, 0)
        r_.data.materials.append(roofm)
    oak = mat_wood('oak_t', '#c79c71', '#94683f', scale=3)
    box('gz_table', (1.8, 0.9, 0.05), (0, 0, 0.98), oak)
    box('gz_tleg', (1.4, 0.1, 0.72), (0, 0, 0.26), oak)
    for yy in (-0.75, 0.75):
        box('gz_bench', (1.8, 0.35, 0.05), (0, yy, 0.68), oak)
        box('gz_bleg', (1.4, 0.08, 0.42), (0, yy, 0.26), oak)
    new = [o for o in bpy.data.objects if o not in before]
    pivot = bpy.data.objects.new('gz_pivot', None)
    bpy.context.collection.objects.link(pivot)
    for o in new:
        if o.parent is None:
            o.parent = pivot
    pivot.rotation_euler = (0, 0, math.radians(rot))
    pivot.location = (x0, y0, 0)


def dof(cam, target, fstop=4.0):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (Vector(target) - cam.location).length
    cam.data.dof.aperture_fstop = fstop


def ext_setup(sun_elev=22, sun_rot=210, mist=0.3, sun_strength=4.5):
    sc = bpy.context.scene
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transparent_max_bounces = 8
    sky(sun_elev=sun_elev, sun_rot=sun_rot, sun_strength=sun_strength)
    mist_comp(amount=mist)
    ground()


def clearing(cx=0, cy=0, rx=12, ry=10, cam=None, cone=None):
    """Функция-запрет для леса: эллипс поляны + сектор обзора камеры."""
    def ko(x, y):
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
            return True
        if cam and cone:
            # не ставим деревья между камерой и домом
            vx, vy = cx - cam[0], cy - cam[1]
            px, py = x - cam[0], y - cam[1]
            d = math.hypot(vx, vy)
            t = (px * vx + py * vy) / (d * d)
            if -0.3 < t < 1.0:
                perp = abs(px * vy - py * vx) / d
                if perp < cone * max(t, 0.15) * d * 0.5 + 2:
                    return True
        return False
    return ko


# ───────────────────────── Сцены ─────────────────────────

def _scene_house(cam_loc, look, house_kw, lens=35, seed=1, sun=(34, 210), fstop=5.6,
                 trees=900, grass_size=(34, 28), grass_center=(0, -4), mist=0.3, extra=None, gaz=None,
                 clear=(13, 10), exposure=0.0, ring=(11, 75)):
    ext_setup(sun_elev=sun[0], sun_rot=sun[1], mist=mist)
    modhouse(**house_kw)
    if gaz:
        gazebo(**gaz)
    if extra:
        extra()
    grass(center=grass_center, size=grass_size, seed=seed)
    c = camera(cam_loc, look, lens=lens)
    dof(c, look, fstop)
    forest(clearing(0, 0, clear[0], clear[1], cam=cam_loc, cone=0.9), seed=seed, n=trees, ring=ring)
    return dict(exposure=exposure)


def hero(**kw):
    """Главный кадр: барнхаус с порталом, 3/4 ракурс."""
    return _scene_house((14.5, -12.0, 1.9), (0.8, 0, 2.6), dict(L=9.0, W=4.4, R=2.5, clad='black'),
                        lens=38, seed=11, sun=(34, 125), fstop=3.2, exposure=0.15)


def series8(**kw):
    return _scene_house((-11, -14, 2.2), (0, 0, 2.0), dict(L=8.0, W=4.2, R=2.2, clad='wood', portal=False, roof='#2b2d2e',
                        long_windows=[(-1.8, 1.4, 2.2), (0.6, 1.4, 2.2), (2.6, 1.0, 1.0)]),
                        lens=40, seed=12, sun=(34, 230), fstop=3.5, exposure=0.1)


def cozy(**kw):
    """Широкий кадр для блока «Есть всё для уютной жизни»: длинный дом с крытой террасой."""
    return _scene_house((10.5, -16.5, 1.7), (1.8, 0, 2.1), dict(L=11.0, W=4.4, R=2.2, clad='black', portal=False,
                        terrace=4.2, deck=True, long_windows=[(-3.8, 1.2, 2.0), (-1.4, 2.4, 2.2), (1.8, 1.2, 2.0)]),
                        lens=30, seed=13, sun=(34, 140), fstop=4.5, mist=0.3, grass_size=(46, 30), clear=(16, 11), exposure=0.2)


def model(variant='nord', **kw):
    v = variant
    presets = {
        # small single module
        'mini': dict(house=dict(L=6.0, W=3.4, R=1.9, clad='graphite', portal=True, long_windows=[(-1.4, 0.9, 1.6)], deck_w=1.8), cam=(10.5, -9.5, 1.8), look=(0.4, 0, 1.8), sun=(34, 130), lens=36),
        'nord': dict(house=dict(L=7.5, W=4.0, R=2.2, clad='wood', portal=True, long_windows=[(-1.8, 1.0, 1.9), (-0.2, 1.0, 1.9)]), cam=(12, -10.5, 1.9), look=(0.5, 0, 2.2), sun=(34, 120), lens=36),
        'barn': dict(house=dict(L=9.0, W=4.4, R=2.5, clad='black'), cam=(5, -16, 1.8), look=(0.8, 0, 2.3), sun=(34, 125), lens=36),
        'duo': dict(house=dict(L=12.0, W=4.6, R=2.4, clad='charred', portal=True, long_windows=[(-4.4, 1.0, 1.9), (-2.6, 1.0, 1.9), (-0.6, 2.4, 2.2), (2.0, 1.0, 1.9)]), cam=(15, -13.5, 2.1), look=(0.5, 0, 2.2), sun=(34, 135), lens=34),
        'family': dict(house=dict(L=12.0, W=6.0, H=3.0, R=3.0, clad='white', roof='#2a2c2d', portal=True, long_windows=[(-4.4, 1.2, 2.0), (-2.4, 1.2, 2.0), (-0.2, 2.4, 2.2), (2.4, 1.2, 2.0)]), cam=(17, -15, 2.2), look=(0.5, 0, 2.6), sun=(34, 125), lens=34),
        'terrace': dict(house=dict(L=8.0, W=4.2, R=2.2, clad='graphite', portal=False, terrace=3.2, long_windows=[(-2.4, 1.0, 1.9), (-0.4, 2.0, 2.2)]), cam=(13, -12, 1.9), look=(1.4, 0, 2.0), sun=(34, 140), lens=34),
        'banya': dict(house=dict(L=5.0, W=3.0, H=2.5, R=1.5, clad='wood', portal=False, long_windows=[(-0.8, 0.8, 0.6)], deck_w=1.6, chimney=True, steps=True, warm=1.3), cam=(-9, -8, 1.6), look=(0.3, 0, 1.6), sun=(34, 240), lens=36),
        'hozblok': dict(house=dict(L=4.0, W=2.6, H=2.3, R=1.1, F=0.3, clad='charred', portal=False, long_windows=[(-0.6, 0.6, 0.6)], deck=False, warm=0.0), cam=(7.5, -7, 1.6), look=(0.2, 0, 1.3), sun=(34, 120), lens=36),
    }
    if v == 'gazebo':
        ext_setup(sun_elev=24, sun_rot=130)
        gazebo()
        grass(center=(0, -3), size=(24, 20), seed=21)
        cam_loc, look = (7, -7, 1.7), (0, 0, 1.5)
        c = camera(cam_loc, look, lens=34)
        dof(c, look, 5.6)
        forest(clearing(0, 0, 10, 8, cam=cam_loc, cone=0.9), seed=21, n=320, ring=(10, 80))
        return dict(exposure=0.15)
    p = presets[v]
    return _scene_house(p['cam'], p['look'], p['house'], lens=p['lens'], seed=hash(v) % 97, sun=p['sun'], fstop=3.5, exposure=0.15)


def interior(**kw):
    """Интерьер барнхауса: скатный потолок в дереве, панорамное остекление торца, печь."""
    W, H, R, L = 4.4, 2.9, 2.5, 7.0
    sc = bpy.context.scene
    sky(sun_elev=18, sun_rot=60, strength=1.0, sun_strength=3.0)
    ground()
    wood = mat_boards('lining', '#ead9bd', '#d4b994', pitch=0.12, axis='Z', rough=0.6, grain='X')
    wood_c = mat_boards('lining_c', '#e2c49a', '#c49f72', pitch=0.12, axis='Y', rough=0.6)
    # оболочка: пятиугольная призма, вывернутая внутрь (нормали — внутрь)
    shell = pent_mesh('shell', W, H, R, -L, 0.0, wood)
    bm = bmesh.new()
    bm.from_mesh(shell.data)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(shell.data)
    bm.free()
    sol = shell.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = 0.15
    # вырез торца под стекло
    inner = pent_mesh('glass_cut', W - 0.3, H - 0.15, R - 0.15, -0.5, 0.5, None, z0=0.08)
    bpy.context.view_layer.objects.active = shell
    bpy.ops.object.modifier_apply(modifier='solid')
    cut(shell, inner)
    tglass = mat('glass_int', '#e8f0f0', rough=0.0, transmission=1.0, ior=1.45, spec=0.5)
    pent_mesh('gable_glass', W - 0.3, H - 0.15, R - 0.15, -0.02, 0.0, tglass, z0=0.08)
    fm = mat('wframe#1a1a1a', '#1a1a1a', rough=0.4, metal=0.3)
    for yy in (-W / 2 + 0.15 + (W - 0.3) * k / 3 for k in range(1, 3)):
        box('mul_v', (0.05, 0.05, H - 0.15), (-0.03, yy, 0.08), fm)
    box('mul_h', (0.05, W - 0.3, 0.05), (-0.03, 0, H - 0.1), fm)
    # пол
    from lib import plank_floor
    floor = mat_plank('ifloor', '#b98c5e', '#86603b')
    floor.node_tree.nodes['Mapping'].inputs['Scale'].default_value = (1.2, 38, 38)
    box('subfloor', (L, W, 0.02), (-L / 2, 0, -0.02), mat('sub', '#3a2a1e'))
    for o in []:
        pass
    # доски вдоль X
    rnd = random.Random(2)
    y = -W / 2
    while y < W / 2:
        x = -L
        while x < 0:
            Lb = rnd.choice((1.2, 1.8, 2.4))
            x1 = min(x + Lb, 0)
            box('plank', (x1 - x - 0.002, 0.178, 0.012), ((x + x1) / 2, y + 0.09, 0), floor, bevel=0.0015)
            x = x1
        y += 0.18
    # конёк-балка и стяжки
    beam = mat_wood('beam', '#a8794c', '#7a5432', scale=2)
    box('ridge', (L, 0.16, 0.22), (-L / 2, 0, H + R - 0.32), beam)
    for k in range(3):
        box('tie', (0.14, W, 0.18), (-1.4 - k * 2.0, 0, H - 0.05), beam)
    # печь
    black = mat('stove', '#141414', rough=0.45, metal=0.6)
    box('stove', (0.55, 0.5, 0.8), (-1.2, W / 2 - 0.7, 0.18), black, bevel=0.02)
    box('stove_base', (0.9, 0.9, 0.04), (-1.2, W / 2 - 0.7, 0.012), mat('tile', '#5b5550', rough=0.8))
    for dx in (-0.22, 0.22):
        for dy in (-0.2, 0.2):
            box('leg', (0.04, 0.04, 0.18), (-1.2 + dx, W / 2 - 0.7 + dy, 0.0), black)
    box('stove_glass', (0.02, 0.32, 0.3), (-0.93, W / 2 - 0.7, 0.4), mat_emit('fire', '#ff8a30', 12))
    point((-0.75, W / 2 - 0.7, 0.55), 40, '#ff9a4c', 0.15)
    cyl('flue', 0.08, H + R - 1.2, (-1.2, W / 2 - 0.7, 0.98), black)
    # диван
    fab = mat_noise('sofa', '#d8d0c3', '#cfc6b8', scale=80, rough=0.9, bump=0.1)
    soft(box('sofa_base', (2.2, 0.95, 0.42), (-3.0, -W / 2 + 0.75, 0.0), fab, bevel=0.06), 1)
    soft(box('sofa_back', (2.2, 0.25, 0.45), (-3.0, -W / 2 + 0.35, 0.4), fab, bevel=0.08), 1)
    for k in range(3):
        soft(box('cush', (0.45, 0.16, 0.4), (-3.7 + k * 0.7, -W / 2 + 0.55, 0.45), mat_noise('cush', '#b48a5f' if k == 1 else '#e9e3d7', '#d8d0c3', scale=60), bevel=0.06), 1)
    rug(-2.4, -0.2, 2.6, 1.8, color='#c9b9a2')
    oak = mat_wood('oak', '#c79c71', '#94683f', scale=3)
    cyl('ctable', 0.45, 0.04, (-2.4, -0.1, 0.38), oak, bevel=0.01)
    cyl('ctable_leg', 0.06, 0.38, (-2.4, -0.1, 0), black)
    # обеденный стол у окна
    box('table', (0.9, 1.6, 0.04), (-0.9, -0.6, 0.74), oak, bevel=0.005)
    box('table_leg', (0.08, 1.2, 0.72), (-0.9, -0.6, 0.02), black)
    for yy in (-1.1, -0.1):
        for xx in (-1.45, -0.35):
            box('chair', (0.42, 0.42, 0.04), (xx, yy, 0.45), mat('chair', '#7a4a32', rough=0.6), bevel=0.01)
            box('chair_leg', (0.04, 0.04, 0.45), (xx, yy, 0), black)
    plant(-0.4, W / 2 - 0.5, 1.3)
    pendant(-0.9, -0.6, H + R - 0.4, drop=1.6, r=0.22, power=10)
    # лес за окном
    grass(center=(10, 0), size=(18, 18), seed=31, count=6000)
    forest(lambda x, y: x < 4 or (x < 9 and abs(y) < 3), seed=31, n=260, ring=(6, 70))
    # дневной свет через остекление (портал) и мягкая подсветка
    a = area((-0.15, 0, 2.2), (0, -90, 0), 4.0, 380, '#eef3f6', size_y=4.2)
    a.visible_camera = False
    a.visible_transmission = False
    area((-3.5, 0, H + R - 0.6), (0, 0, 0), 2.0, 120, '#fff0dc', size_y=1.5).visible_camera = False
    point((-4.5, -1.2, 2.2), 60, '#ffcf96', 0.3)
    c = camera((-6.5, -1.4, 1.35), (0, 0.4, 1.7), lens=20)
    sc.cycles.max_bounces = 8
    return dict(exposure=0.15)
