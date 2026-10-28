"""
Библиотека для процедурных 3D-сцен интерьеров (Blender / Cycles).
Запуск сцен: см. render.py. Требуется модуль bpy (pip install bpy==4.5.*, Python 3.11).
Единицы — метры. Ось Y — вглубь комнаты, X — вправо, Z — вверх.
"""
import math
import random
import bpy
from mathutils import Vector

# ───────────────────────── Сцена ─────────────────────────

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.04
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 3
    sc.render.use_persistent_data = True
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 6
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    return sc


_mats = {}


def _principled(name, color, rough=0.5, metal=0.0, spec=0.5, coat=0.0, sheen=0.0, transmission=0.0, ior=1.45, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Sheen Weight'].default_value = sheen
    b.inputs['Transmission Weight'].default_value = transmission
    b.inputs['IOR'].default_value = ior
    if emission:
        b.inputs['Emission Color'].default_value = (*emission, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m


def srgb(hexstr):
    """'#b6774b' → линейный RGB"""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, hexcolor, **kw):
    key = (name, hexcolor, tuple(sorted(kw.items())))
    if key not in _mats:
        _mats[key] = _principled(name, srgb(hexcolor), **kw)
    return _mats[key]


def _nodes(m):
    nt = m.node_tree
    return nt, nt.nodes, nt.links, nt.nodes['Principled BSDF']


def mat_wood(name='wood', light='#c9a37a', dark='#8e6440', scale=1.0, rough=0.42, axis='X'):
    """Дерево для мебели и стен: мягкие волокна вдоль оси axis (шум, растянутый по одной оси)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    k = 30 * scale
    mp.inputs['Scale'].default_value = {'X': (1.0, k, k), 'Y': (k, 1.0, k), 'Z': (k, k, 1.0)}[axis]
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 8
    nz.inputs['Distortion'].default_value = 0.5
    l.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[0].color = (*srgb(dark), 1)
    ramp.color_ramp.elements[1].color = (*srgb(light), 1)
    l.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = 0.12
    return m


def mat_noise(name, c1, c2, scale=6.0, rough=0.8, bump=0.08, detail=6):
    """Шумовая фактура: штукатурка, бетон, микроцемент, ткань."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = scale
    nz.inputs['Detail'].default_value = detail
    nz.inputs['Roughness'].default_value = 0.6
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[0].color = (*srgb(c1), 1)
    ramp.color_ramp.elements[1].color = (*srgb(c2), 1)
    l.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if bump:
        bp = n.new('ShaderNodeBump')
        bp.inputs['Strength'].default_value = bump
        bp.inputs['Distance'].default_value = 0.02
        l.new(nz.outputs['Fac'], bp.inputs['Height'])
        l.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_brick(name='brick'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    br = n.new('ShaderNodeTexBrick')
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Brick Width'].default_value = 0.25
    br.inputs['Row Height'].default_value = 0.075
    br.inputs['Mortar Size'].default_value = 0.01
    br.inputs['Color1'].default_value = (*srgb('#a2614a'), 1)
    br.inputs['Color2'].default_value = (*srgb('#c08a6c'), 1)
    br.inputs['Mortar'].default_value = (*srgb('#d8d0c6'), 1)
    l.new(mp.outputs['Vector'], br.inputs['Vector'])
    l.new(br.outputs['Color'], b.inputs['Base Color'])
    bp = n.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = 0.6
    bp.invert = True
    l.new(br.outputs['Fac'], bp.inputs['Height'])
    l.new(bp.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = 0.85
    return m


def mat_emit(name, hexcolor, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    n.remove(b)
    em = n.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*srgb(hexcolor), 1)
    em.inputs['Strength'].default_value = strength
    l.new(em.outputs['Emission'], n['Material Output'].inputs['Surface'])
    return m


def mat_glass(name='glass', tint='#eef3f3'):
    return mat(name, tint, rough=0.02, transmission=1.0, ior=1.5, spec=0.5)


# ───────────────────────── Геометрия ─────────────────────────

def _finish(o, m, bevel):
    if m:
        o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = 'ANGLE'
        mod.harden_normals = True
    for p in o.data.polygons:
        p.use_smooth = bool(bevel)
    return o


def box(name, size, loc, m=None, bevel=0.0, rot=(0, 0, 0)):
    """size — полные размеры (x, y, z), loc — центр нижней грани."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2] + size[2] / 2), rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, m, bevel)


def cyl(name, r, h, loc, m=None, verts=64, bevel=0.0, rot=(0, 0, 0), r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=(loc[0], loc[1], loc[2] + h / 2), rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, vertices=verts, location=(loc[0], loc[1], loc[2] + h / 2), rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return _finish(o, m, bevel)


def sphere(name, r, loc, m=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    for p in o.data.polygons:
        p.use_smooth = True
    if m:
        o.data.materials.append(m)
    return o


def soft(o, levels=2):
    """Мягкая форма: подразделение поверх фаски (подушки, ванна)."""
    s = o.modifiers.new('subd', 'SUBSURF')
    s.levels = levels
    s.render_levels = levels
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def plane(name, size, loc, m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    if m:
        o.data.materials.append(m)
    return o


# ───────────────────────── Комната ─────────────────────────

def room(W, D, H, wall, floor, ceil, window=None, back_wall=None, right_wall=None, t=0.15):
    """
    Комната с полом в z=0. X: от -W/2 до W/2, Y: от 0 до D (задняя стена в y=D).
    Камера ставится около y=0.3. window — проём в левой стене: (y_center, width, sill, height).
    """
    box('floor', (W + 2 * t, D + 2 * t, t), (0, D / 2, -t), floor)
    box('ceiling', (W + 2 * t, D + 2 * t, t), (0, D / 2, H), ceil)
    box('back', (W, t, H), (0, D + t / 2, 0), back_wall or wall)
    box('front', (W, t, H), (0, -t / 2 - 0.6, 0), wall)
    box('right', (t, D + 0.6, H), (W / 2 + t / 2, D / 2 - 0.3, 0), right_wall or wall)
    if window:
        yc, ww, sill, wh = window
        x = -W / 2 - t / 2
        y0, y1 = yc - ww / 2, yc + ww / 2
        box('left_a', (t, y0 + 0.6, H), (x, (y0 - 0.6) / 2, 0), wall)
        box('left_b', (t, D - y1, H), (x, (D + y1) / 2, 0), wall)
        box('left_sill', (t, ww, sill), (x, yc, 0), wall)
        box('left_top', (t, ww, H - sill - wh), (x, yc, sill + wh), wall)
        # рама и подоконник
        frame = mat('frame', '#f2efea', rough=0.4)
        box('frame_mid', (0.06, 0.06, wh), (x + 0.02, yc, sill), frame)
        box('sill_board', (0.32, ww + 0.1, 0.03), (x + 0.13, yc, sill - 0.03), mat('sill', '#efebe4', rough=0.3))
        glass = mat_glass('window_glass')
        box('pane', (0.01, ww, wh), (x, yc, sill), glass)
    else:
        box('left', (t, D + 0.6, H), (-W / 2 - t / 2, D / 2 - 0.3, 0), wall)


def daylight(sun_dir=(0.8, 0.35, -0.5), sun_strength=3.2, sun_color='#fff1de', sky_strength=0.6, window=None, W=None, portal_strength=0):
    """Небо + солнце. Солнце светит в окно левой стены."""
    sc = bpy.context.scene
    world = bpy.data.worlds.new('world')
    sc.world = world
    world.use_nodes = True
    n = world.node_tree.nodes
    l = world.node_tree.links
    bg = n['Background']
    sky = n.new('ShaderNodeTexSky')
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(22)
    sky.sun_rotation = math.radians(250)
    sky.altitude = 100
    sky.air_density = 1.4
    sky.dust_density = 2.0
    sky.sun_disc = False
    l.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = sky_strength
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.active_object
    sun.rotation_euler = Vector(sun_dir).normalized().to_track_quat('-Z', 'Y').to_euler()
    sun.data.energy = sun_strength
    sun.data.angle = math.radians(2.5)
    sun.data.color = srgb(sun_color)
    if window and W:
        yc, ww, sill, wh = window
        bpy.ops.object.light_add(type='AREA', location=(-W / 2 - 0.2, yc, sill + wh / 2), rotation=(0, math.radians(-90), 0))
        p = bpy.context.active_object
        p.data.shape = 'RECTANGLE'
        p.data.size = wh
        p.data.size_y = ww
        p.data.cycles.is_portal = True
        if portal_strength:
            # Дополнительный мягкий свет из окна (для пасмурного северного дня)
            bpy.ops.object.light_add(type='AREA', location=(-W / 2 + 0.05, yc, sill + wh / 2), rotation=(0, math.radians(-90), 0))
            a = bpy.context.active_object
            a.data.shape = 'RECTANGLE'
            a.data.size = wh
            a.data.size_y = ww
            a.data.energy = portal_strength
            a.data.color = srgb('#e9f0f4')
            a.rotation_euler = Vector((1, 0, 0)).to_track_quat('-Z', 'Y').to_euler()


def area(loc, rot, size, energy, color='#ffe2bd', size_y=None):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=tuple(math.radians(a) for a in rot))
    a = bpy.context.active_object
    a.data.shape = 'RECTANGLE' if size_y else 'SQUARE'
    a.data.size = size
    if size_y:
        a.data.size_y = size_y
    a.data.energy = energy
    a.data.color = srgb(color)
    return a


def point(loc, energy, color='#ffcf96', radius=0.05):
    bpy.ops.object.light_add(type='POINT', location=loc)
    p = bpy.context.active_object
    p.data.energy = energy
    p.data.color = srgb(color)
    p.data.shadow_soft_size = radius
    return p


def camera(loc, look_at, lens=22, shift_y=0.0):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object
    d = Vector(look_at) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    c.data.shift_y = shift_y
    c.data.sensor_width = 36
    bpy.context.scene.camera = c
    return c


def render(path, w=1600, h=1200, samples=128, exposure=0.0):
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.view_settings.exposure = exposure
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ───────────────────────── Мебель и детали ─────────────────────────

def pendant(x, y, H, drop=0.9, r=0.22, shade='#1d1b18', inner='#fff1d6', power=18):
    m = mat('pend_' + shade, shade, rough=0.35, metal=0.6)
    cyl('pend_cord', 0.004, drop, (x, y, H - drop), mat('cord', '#111111'))
    cyl('pend_shade', r, r * 0.65, (x, y, H - drop - r * 0.65), m, r2=0.03)
    sphere('pend_bulb', 0.045, (x, y, H - drop - r * 0.5), mat_emit('bulb', inner, 30))
    point((x, y, H - drop - r * 0.75), power, '#ffcf96', 0.05)


def plant(x, y, h=1.1, pot='#efe8dc'):
    cyl('pot', 0.2, 0.42, (x, y, 0), mat('pot', pot, rough=0.6), r2=0.16, bevel=0.01)
    leaf = mat('leaf', '#2f4a43', rough=0.5, sheen=0.3)
    import random
    rnd = random.Random(7)
    for i in range(16):
        a = i / 16 * math.tau + rnd.random() * 0.4
        tilt = 0.35 + rnd.random() * 0.5
        L = h * (0.55 + rnd.random() * 0.45)
        cx = x + math.cos(a) * math.sin(tilt) * L / 2
        cy = y + math.sin(a) * math.sin(tilt) * L / 2
        cz = 0.4 + math.cos(tilt) * L / 2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(cx, cy, cz), segments=16, ring_count=8)
        o = bpy.context.active_object
        o.scale = (0.035, 0.11, L / 2)
        o.rotation_euler = (math.sin(a) * tilt * -1, math.cos(a) * tilt, a)
        for p in o.data.polygons:
            p.use_smooth = True
        o.data.materials.append(leaf)


def rug(x, y, w, d, color='#e6ddd0'):
    o = box('rug', (w, d, 0.01), (x, y, 0.013), mat_noise('rug', color, '#d9cfbf', scale=60, rough=0.95, bump=0.15), bevel=0.004)
    return o


def frame_art(x, y, z, w, h, colors=('#b6774b', '#2f4a43')):
    box('art_frame', (w, 0.03, h), (x, y, z), mat('art_frame', '#15130f', rough=0.4), bevel=0.003)
    box('art_canvas', (w - 0.06, 0.01, h - 0.06), (x, y - 0.016, z + 0.03), mat('canvas', '#f2ede4', rough=0.9))
    sphere('art_sun', 0.12 * w, (x - w * 0.12, y - 0.025, z + h * 0.58), mat('art_c1', colors[0], rough=0.9), scale=(1, 0.05, 1))
    box('art_band', (w * 0.55, 0.012, h * 0.16), (x + w * 0.04, y - 0.024, z + h * 0.22), mat('art_c2', colors[1], rough=0.9))


def mat_plank(name='plank', light='#c9a37a', dark='#93673f', rough=0.4):
    """Материал доски: волокна вдоль Y + случайный тон для каждой доски (Object Info → Random)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, n, l, b = _nodes(m)
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (38, 1.2, 38)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 8
    nz.inputs['Distortion'].default_value = 0.6
    l.new(mp.outputs['Vector'], nz.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[0].color = (*srgb(dark), 1)
    ramp.color_ramp.elements[1].color = (*srgb(light), 1)
    l.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    info = n.new('ShaderNodeObjectInfo')
    hsv = n.new('ShaderNodeHueSaturation')
    l.new(ramp.outputs['Color'], hsv.inputs['Color'])
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.8
    mr.inputs['To Max'].default_value = 1.12
    l.new(info.outputs['Random'], mr.inputs['Value'])
    l.new(mr.outputs['Result'], hsv.inputs['Value'])
    l.new(hsv.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = 0.2
    b.inputs['Coat Roughness'].default_value = 0.25
    return m


def plank_floor(W, D, m, pw=0.19, gap=0.002, seed=3, x0=None, y0=-0.6):
    """Пол из отдельных досок вдоль оси Y со смещёнными стыками."""
    rnd = random.Random(seed)
    x = -W / 2 if x0 is None else x0
    while x < W / 2:
        w = min(pw, W / 2 - x)
        y = y0 - rnd.random() * 1.2
        while y < D:
            L = rnd.choice((1.2, 1.5, 1.8))
            y1 = min(y + L, D)
            ya = max(y, y0)
            if y1 - ya > 0.05:
                box('plank', (w - gap, y1 - ya - gap, 0.012), (x + w / 2, (ya + y1) / 2, 0), m, bevel=0.0015)
            y = y1
        x += pw
