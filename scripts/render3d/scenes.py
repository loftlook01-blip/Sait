"""Сцены интерьеров. Каждая функция строит сцену; raw=True — та же комната в черновой отделке («до»)."""
import math
import random
import bpy
from lib import (mat_plank, plank_floor, box, cyl, sphere, soft, plane, room, daylight, area, point, camera, mat, mat_wood, mat_noise,
                 mat_brick, mat_emit, mat_glass, pendant, plant, rug, frame_art, srgb)

PAPER = '#efe9df'


def raw_room(W, D, H, window):
    """Черновая отделка: бетон, штукатурка по маякам, голая лампочка, стремянка."""
    concrete = mat_noise('concrete', '#9c978f', '#b9b4ac', scale=3, rough=0.92, bump=0.25)
    plaster = mat_noise('plaster_raw', '#b9b2a6', '#cfc8bc', scale=2.2, rough=0.95, bump=0.3)
    room(W, D, H, plaster, concrete, concrete, window=window)
    # маяки
    beacon = mat('beacon', '#8d8a85', rough=0.5, metal=0.6)
    for i in range(6):
        box(f'beacon{i}', (0.02, 0.01, H - 0.2), (-W / 2 + 0.7 + i * (W - 1.4) / 5, D - 0.02, 0.1), beacon)
    cyl('cord', 0.004, 0.5, (0.2, D / 2, H - 0.5), mat('cord', '#111111'))
    sphere('bulb', 0.05, (0.2, D / 2, H - 0.55), mat_emit('bulb_raw', '#fff2d8', 40))
    point((0.2, D / 2, H - 0.6), 25, '#ffd9a8')
    # стремянка, мешки, ведро
    al = mat('alu', '#b8b8b4', rough=0.35, metal=1.0)
    for dx in (-0.22, 0.22):
        box('leg', (0.04, 0.05, 1.6), (W / 2 - 1.0 + dx, D - 1.4, 0), al, rot=(math.radians(-12), 0, 0))
        box('leg2', (0.04, 0.05, 1.6), (W / 2 - 1.0 + dx, D - 1.05, 0), al, rot=(math.radians(12), 0, 0))
    for k in range(4):
        box('step', (0.48, 0.12, 0.03), (W / 2 - 1.0, D - 1.38 + k * 0.035, 0.32 + k * 0.33), al)
    bag = mat_noise('bag', '#d8cfbd', '#c9bfa9', scale=20, rough=0.95, bump=0.1)
    for k, (x, y, z) in enumerate([(-0.9, 1.9, 0), (-0.35, 1.85, 0), (-0.62, 1.95, 0.16)]):
        soft(box(f'bag{k}', (0.5, 0.36, 0.16), (x, y, z), bag, bevel=0.04), 1)
    cyl('bucket', 0.16, 0.34, (0.6, 1.6, 0), mat('bucket', '#e9e6e1', rough=0.4), r2=0.13)


# ───────────────────────── Гостиная ─────────────────────────

def living(raw=False, wall_hex='#e6ded2', floor_tone='oak', cam='std'):
    W, D, H = 5.8, 5.2, 2.85
    win = (2.4, 2.1, 0.45, 2.15)
    if raw:
        raw_room(W, D, H, win)
    else:
        wall = mat_noise('wall', wall_hex, wall_hex, scale=4, rough=0.85, bump=0.01)
        floors = {
            'oak': ('#c9a37a', '#93673f'),
            'light': ('#ddc5a5', '#b9976f'),
            'walnut': ('#8a6142', '#4f3523'),
        }
        room(W, D, H, wall, mat('subfloor', '#3a2a1e', rough=0.9), mat('ceil', '#f6f3ee', rough=0.9), window=win)
        plank_floor(W, D, mat_plank('floor', *floors[floor_tone]))
        # дубовые рейки на правой стене
        oak = mat_wood('oak_slat', '#c79c71', '#94683f', scale=3, axis='Z')
        for i in range(26):
            box(f'slat{i}', (0.035, 0.04, H), (W / 2 - 0.03, 2.5 + i * 0.09, 0), oak, bevel=0.004)
        box('slat_back', (0.02, 2.4, H), (W / 2 - 0.01, 3.6, 0), mat('slat_bg', '#2a2622', rough=0.8))
        # диван
        fab = mat_noise('fabric', '#b9ab97', '#ab9c87', scale=90, rough=0.95, bump=0.12)
        fab2 = mat_noise('fabric2', '#c5b8a5', '#b8aa95', scale=90, rough=0.95, bump=0.12)
        sx, sy, sw = -0.2, D - 0.62, 2.7
        box('sofa_base', (sw, 0.98, 0.24), (sx, sy, 0.1), fab, bevel=0.03)
        for k in range(3):
            soft(box(f'seat{k}', (sw / 3 - 0.04, 0.82, 0.2), (sx - sw / 3 + k * sw / 3, sy - 0.06, 0.33), fab2, bevel=0.05), 1)
            soft(box(f'back{k}', (sw / 3 - 0.06, 0.24, 0.48), (sx - sw / 3 + k * sw / 3, sy + 0.33, 0.42), fab2, bevel=0.07), 1)
        for dx in (-1, 1):
            soft(box(f'arm{dx}', (0.2, 0.98, 0.52), (sx + dx * (sw / 2 - 0.1), sy, 0.1), fab, bevel=0.06), 1)
        for dx in (-1.1, 1.1):
            for dy in (-0.4, 0.4):
                cyl('sofa_leg', 0.02, 0.1, (sx + dx, sy + dy, 0), mat('blackmetal', '#1b1a18', rough=0.45, metal=0.7))
        soft(box('pillow1', (0.48, 0.14, 0.42), (sx - 0.85, sy + 0.12, 0.52), mat_noise('pillow_g', '#2f4a43', '#3b5a51', scale=80, rough=0.9, bump=0.1), bevel=0.06), 2)
        soft(box('pillow2', (0.44, 0.14, 0.4), (sx + 0.78, sy + 0.14, 0.52), mat_noise('pillow_c', '#b6774b', '#a9693f', scale=80, rough=0.9, bump=0.1), bevel=0.06), 2)
        # ковёр и столик
        rug(sx, sy - 1.5, 3.0, 2.1, color='#d9cebd')
        top = mat('travertine', '#e2d6c4', rough=0.35)
        cyl('table_top', 0.55, 0.05, (sx, sy - 1.45, 0.36), top, bevel=0.01)
        cyl('table_base', 0.32, 0.36, (sx, sy - 1.45, 0), mat('stone2', '#cfc1ad', rough=0.5), r2=0.26)
        cyl('vase', 0.07, 0.2, (sx + 0.15, sy - 1.5, 0.41), mat('ceramic', '#1d1b18', rough=0.3), r2=0.05)
        box('book', (0.24, 0.18, 0.04), (sx - 0.2, sy - 1.35, 0.41), mat('book', '#b6774b', rough=0.7))
        # комод у окна
        box('sideboard', (0.45, 1.6, 0.6), (-W / 2 + 0.3, D - 1.3, 0), oak, bevel=0.01)
        cyl('lamp_base', 0.09, 0.32, (-W / 2 + 0.3, D - 0.85, 0.6), mat('ceramic2', '#e9e1d4', rough=0.4), r2=0.06)
        cyl('lamp_shade', 0.2, 0.24, (-W / 2 + 0.3, D - 0.85, 0.92), mat('shade', '#f4ead9', rough=0.9, transmission=0.3), r2=0.16)
        point((-W / 2 + 0.3, D - 0.85, 1.02), 12, '#ffcf96', 0.08)
        # картина и растение
        frame_art(sx, D - 0.02, 1.25, 1.2, 0.85)
        plant(W / 2 - 0.55, D - 0.5, h=1.5)
        pendant(sx + 0.9, sy - 1.6, H, drop=1.2, r=0.26, power=14)
    daylight(sun_dir=(0.85, 0.45, -0.42), sun_strength=4.0, window=win, W=W, sky_strength=0.8, portal_strength=120)
    if cam == 'wide':
        camera((0.9, 0.15, 1.25), (0.0, D, 1.15), lens=17)
    else:
        camera((0.55, 0.2, 1.3), (0.15, D, 1.1), lens=18)
    return dict(exposure=0.0 if not raw else 0.4)


# ───────────────────────── Кухня-гостиная в стиле лофт ─────────────────────────

def kitchen(raw=False):
    W, D, H = 6.2, 5.6, 3.0
    win = (2.0, 2.0, 0.6, 2.2)
    if raw:
        raw_room(W, D, H, win)
    else:
        wall = mat_noise('wall', '#e4ddd2', '#e4ddd2', scale=4, rough=0.85, bump=0.01)
        room(W, D, H, wall, mat('subfloor', '#3a2a1e'), mat('ceil', '#f4f1ec', rough=0.9), window=win, back_wall=mat_brick())
        plank_floor(W, D, mat_plank('floor', '#c29a70', '#8a5f3b'))
        dark = mat('graphite_front', '#2a2825', rough=0.55, coat=0.1)
        oak = mat_wood('oak_top', '#c9a077', '#93673f', scale=3)
        steel = mat('blacksteel', '#141413', rough=0.4, metal=0.85)
        # нижние шкафы вдоль задней стены
        x0, n = -2.35, 6
        for i in range(n):
            box(f'base{i}', (0.595, 0.6, 0.8), (x0 + i * 0.6, D - 0.32, 0.1), dark, bevel=0.003)
        box('plinth', (n * 0.6, 0.55, 0.1), (x0 + (n - 1) * 0.3, D - 0.34, 0), mat('plinth', '#1a1918'))
        box('counter', (n * 0.6 + 0.04, 0.64, 0.04), (x0 + (n - 1) * 0.3, D - 0.33, 0.9), oak, bevel=0.003)
        box('sink', (0.5, 0.42, 0.01), (x0 + 1.5, D - 0.33, 0.941), mat('sinkm', '#1d1c1a', rough=0.3))
        cyl('tap', 0.012, 0.32, (x0 + 1.5, D - 0.12, 0.94), steel)
        box('tap_spout', (0.02, 0.2, 0.02), (x0 + 1.5, D - 0.22, 1.24), steel)
        # открытые полки на чёрных кронштейнах
        for k, z in enumerate((1.55, 1.95)):
            box(f'shelf{k}', (2.2, 0.28, 0.04), (x0 + 1.0, D - 0.15, z), oak, bevel=0.003)
            for dx in (-0.9, 0.9):
                box('bracket', (0.02, 0.26, 0.04), (x0 + 1.0 + dx, D - 0.15, z - 0.04), steel)
        cer = [mat('cer1', '#efe9df', rough=0.3), mat('cer2', '#1d1b18', rough=0.3), mat('cer3', '#b6774b', rough=0.4)]
        rnd = random.Random(2)
        for k in range(9):
            z = 1.59 if k < 5 else 1.99
            xx = x0 + 0.1 + (k % 5) * 0.42 + rnd.random() * 0.1
            cyl(f'jar{k}', 0.05 + rnd.random() * 0.03, 0.12 + rnd.random() * 0.12, (xx, D - 0.15, z), rnd.choice(cer), r2=None)
        # колонна с духовкой справа
        box('column', (0.62, 0.62, 2.4), (x0 + n * 0.6 + 0.02, D - 0.32, 0), dark, bevel=0.003)
        box('oven', (0.56, 0.02, 0.58), (x0 + n * 0.6 + 0.02, D - 0.64, 0.95), mat('oven_glass', '#0d0d0c', rough=0.08, coat=1))
        # остров
        ix, iy = -0.3, D - 2.15
        box('island', (2.3, 0.95, 0.86), (ix, iy, 0.04), dark, bevel=0.004)
        box('island_top', (2.45, 1.05, 0.05), (ix, iy, 0.9), oak, bevel=0.004)
        # табуреты
        for k in range(3):
            sx = ix - 0.75 + k * 0.75
            cyl(f'stool_seat{k}', 0.19, 0.05, (sx, iy - 0.85, 0.7), mat('leather', '#a2693f', rough=0.55), bevel=0.01)
            for a in range(4):
                ang = a * math.pi / 2 + math.pi / 4
                box('stool_leg', (0.02, 0.02, 0.7), (sx + math.cos(ang) * 0.13, iy - 0.85 + math.sin(ang) * 0.13, 0), steel)
            cyl('stool_ring', 0.15, 0.015, (sx, iy - 0.85, 0.28), steel)
        for k in range(3):
            pendant(ix - 0.75 + k * 0.75, iy, H, drop=1.15, r=0.13, power=10)
        # лофт-перегородка справа: чёрная рама + стекло
        px = W / 2 - 1.1
        glass = mat_glass('pglass', '#e9eeee')
        box('pglass', (0.012, 3.0, H), (px, 2.3, 0), glass)
        for k in range(5):
            box(f'pv{k}', (0.05, 0.04, H), (px, 0.8 + k * 0.75, 0), steel)
        for z in (0.0, 0.95, 1.95, H - 0.05):
            box('ph', (0.05, 3.0, 0.05), (px, 2.3, z), steel)
        plant(px - 0.5, D - 1.0, h=1.2, pot='#2a2825')
    daylight(sun_dir=(0.8, 0.5, -0.45), sun_strength=3.5, window=win, W=W, sky_strength=0.8, portal_strength=130)
    camera((1.2, 0.3, 1.45), (-0.4, D, 1.1), lens=18)
    return dict(exposure=0.0 if not raw else 0.4)


# ───────────────────────── Ванная в микроцементе ─────────────────────────

def bath(raw=False):
    W, D, H = 3.6, 3.8, 2.75
    win = (1.6, 0.9, 1.1, 1.2)
    if raw:
        raw_room(W, D, H, win)
    else:
        micro = mat_noise('microcement', '#d9cfc2', '#cfc4b5', scale=2.5, rough=0.55, bump=0.03)
        room(W, D, H, micro, micro, mat('ceil', '#f4f1ec', rough=0.9), window=win)
        oak = mat_wood('oak_v', '#c9a077', '#93673f', scale=3)
        # отдельностоящая ванна
        tub = cyl('tub', 0.36, 0.56, (0.15, 1.75, 0), mat('acryl', '#f7f5f1', rough=0.15, coat=0.6), verts=96, r2=0.42, bevel=0.03)
        tub.scale = (1.0, 2.0, 1.0)
        water = cyl('tub_in', 0.375, 0.01, (0.15, 1.75, 0.555), mat('water', '#b9c9cb', rough=0.03, coat=1))
        water.scale = (1.0, 1.95, 1.0)
        steel = mat('blackmetal', '#151413', rough=0.35, metal=0.9)
        cyl('ftap', 0.014, 1.0, (0.75, 1.75, 0), steel)
        box('ftap_spout', (0.24, 0.02, 0.02), (0.64, 1.75, 0.98), steel)
        # подвесная тумба, накладная раковина, круглое зеркало с подсветкой
        box('vanity', (0.5, 1.2, 0.36), (W / 2 - 0.27, D - 1.0, 0.5), oak, bevel=0.003)
        cyl('basin', 0.2, 0.13, (W / 2 - 0.27, D - 1.0, 0.86), mat('basinm', '#f7f5f1', rough=0.15, coat=0.6), r2=0.17, bevel=0.01)
        cyl('mirror_back', 0.42, 0.01, (W / 2 - 0.035, D - 1.0, 1.6), mat_emit('mirror_glow', '#ffd9a8', 6), rot=(0, math.radians(90), 0))
        cyl('mirror', 0.4, 0.02, (W / 2 - 0.05, D - 1.0, 1.6), mat('mirrorm', '#d9dcdc', rough=0.02, metal=1.0), rot=(0, math.radians(90), 0))
        cyl('mtap', 0.01, 0.2, (W / 2 - 0.05, D - 1.0, 1.08), steel, rot=(0, math.radians(90), 0))
        # ниша с подсветкой на задней стене
        box('niche', (1.2, 0.02, 0.4), (-0.3, D - 0.015, 1.2), mat('niche_bg', '#cbbfb0', rough=0.6))
        box('niche_led', (1.2, 0.02, 0.01), (-0.3, D - 0.03, 1.59), mat_emit('led', '#ffd9a8', 25))
        box('niche_shelf', (1.2, 0.16, 0.03), (-0.3, D - 0.08, 1.2), oak)
        for k, (c, h) in enumerate([('#2f4a43', 0.18), ('#efe9df', 0.13), ('#b6774b', 0.1)]):
            cyl(f'bottle{k}', 0.035, h, (-0.65 + k * 0.22, D - 0.08, 1.23), mat(f'b{k}', c, rough=0.3))
        # полотенцесушитель цвета «зелёный мох»
        rail = mat('ral6005', '#1f3d33', rough=0.4, metal=0.3)
        for x in (-W / 2 + 0.03, -W / 2 + 0.03):
            pass
        for k in range(2):
            cyl(f'rail_v{k}', 0.012, 1.2, (-0.9 + k * 0.5, D - 0.06, 0.4), rail)
        for k in range(5):
            cyl(f'rail_h{k}', 0.01, 0.5, (-0.65, D - 0.06, 0.55 + k * 0.22), rail, rot=(0, math.radians(90), 0))
        soft(box('towel', (0.36, 0.05, 0.55), (-0.65, D - 0.1, 0.8), mat_noise('towel', '#e8dfd2', '#ddd2c3', scale=120, rough=1, bump=0.2), bevel=0.02), 1)
        # трап
        box('drain', (0.7, 0.06, 0.003), (-0.9, 0.9, 0.0), steel)
        rug(0.15, 0.95, 0.9, 0.5, color='#d6ccbd')
        cyl('stool', 0.17, 0.45, (-0.75, 1.3, 0), oak, bevel=0.01)
        soft(box('towel2', (0.3, 0.3, 0.06), (-0.75, 1.3, 0.45), mat_noise('towel2', '#2f4a43', '#36554b', scale=120, rough=1, bump=0.2), bevel=0.03), 1)
        plant(-W / 2 + 0.35, D - 0.35, h=1.0, pot='#e9e1d4')
        area((0, D / 2, H - 0.02), (0, 0, 0), 0.6, 60, '#ffe6c8')
    daylight(sun_dir=(0.7, 0.4, -0.6), sun_strength=2.5, window=win, W=W, sky_strength=0.8, portal_strength=60)
    camera((0.9, 0.12, 1.4), (-0.15, D, 0.95), lens=17)
    return dict(exposure=0.1 if not raw else 0.5)


# ───────────────────────── Спальня ─────────────────────────

def bedroom(raw=False):
    W, D, H = 4.8, 4.8, 2.8
    win = (2.0, 1.6, 0.6, 1.9)
    if raw:
        raw_room(W, D, H, win)
    else:
        wall = mat_noise('wall', '#e3d9cc', '#e3d9cc', scale=4, rough=0.9, bump=0.01)
        room(W, D, H, wall, mat('subfloor', '#3a2a1e'), mat('ceil', '#f4f1ec', rough=0.9), window=win)
        plank_floor(W, D, mat_plank('floor', '#d1b08a', '#9f7650'))
        uph = mat_noise('uph', '#cdbfad', '#c2b39f', scale=80, rough=0.95, bump=0.12)
        # мягкие панели изголовья во всю стену
        for i in range(14):
            soft(box(f'panel{i}', (0.31, 0.08, 1.35), (-W / 2 + 0.2 + i * 0.315 + 0.16, D - 0.05, 0.25), uph, bevel=0.03), 1)
        oak = mat_wood('oak_n', '#c9a077', '#93673f', scale=3)
        bx, by = 0.0, D - 1.15
        box('bed_base', (1.9, 2.15, 0.3), (bx, by, 0.05), oak, bevel=0.01)
        soft(box('mattress', (1.8, 2.05, 0.24), (bx, by, 0.33), mat('linen', '#f3efe7', rough=0.95), bevel=0.05), 1)
        soft(box('duvet', (1.86, 1.45, 0.09), (bx, by - 0.33, 0.52), mat_noise('duvet', '#2f4a43', '#3a5a50', scale=40, rough=0.95, bump=0.15), bevel=0.04), 2)
        for dx in (-0.45, 0.45):
            soft(box('pillow', (0.75, 0.36, 0.16), (bx + dx, D - 0.42, 0.55), mat('pil', '#faf7f1', rough=0.95), bevel=0.07), 2)
        soft(box('throw', (1.9, 0.5, 0.05), (bx, by - 0.85, 0.6), mat_noise('throw', '#b6774b', '#a8693f', scale=60, rough=1, bump=0.2), bevel=0.02), 1)
        for dx in (-1.35, 1.35):
            box('night', (0.5, 0.42, 0.5), (bx + dx, D - 0.3, 0), oak, bevel=0.006)
            sphere('sconce', 0.07, (bx + dx, D - 0.12, 1.25), mat_emit('sconce', '#ffe0b0', 18))
            point((bx + dx, D - 0.25, 1.25), 8, '#ffcf96', 0.06)
        cyl('vase_n', 0.06, 0.2, (bx - 1.4, D - 0.3, 0.5), mat('cer', '#efe9df', rough=0.3), r2=0.04)
        # шкаф с плоскими фасадами справа
        front = mat('wardrobe', '#ece5da', rough=0.5)
        for k in range(4):
            box(f'wd{k}', (0.6, 0.6, H - 0.05), (W / 2 - 0.3, 0.45 + k * 0.605, 0), front, bevel=0.002)
            box(f'wdh{k}', (0.015, 0.02, 0.4), (W / 2 - 0.61, 0.45 + k * 0.605 + 0.22, 1.0), mat('brass', '#b08a5a', rough=0.3, metal=1))
        rug(bx, by - 1.2, 2.6, 1.4, color='#ddd3c4')
    daylight(sun_dir=(0.85, 0.3, -0.42), sun_strength=3.0, window=win, W=W, sky_strength=0.8, portal_strength=100)
    camera((0.55, 0.15, 1.35), (-0.1, D, 0.9), lens=18)
    return dict(exposure=0.0 if not raw else 0.4)


# ───────────────────────── Офис ─────────────────────────

def office(raw=False):
    W, D, H = 7.4, 7.0, 3.2
    win = (3.0, 3.6, 0.6, 2.3)
    if raw:
        raw_room(W, D, H, win)
    else:
        wall = mat_noise('wall', '#e6e2db', '#e6e2db', scale=4, rough=0.9, bump=0.01)
        floor = mat_noise('carpet', '#8f8b84', '#9b978f', scale=80, rough=1, bump=0.15)
        room(W, D, H, wall, floor, mat('ceil_dark', '#2a2926', rough=0.9), window=win)
        steel = mat('blacksteel', '#141413', rough=0.4, metal=0.85)
        glass = mat_glass('og', '#eaf0f0')
        oak = mat_wood('oak_d', '#c9a077', '#93673f', scale=3)
        # переговорная из стекла у задней стены
        gy = D - 2.3
        box('meet_glass', (4.6, 0.012, H), (-0.4, gy, 0), glass)
        for k in range(6):
            box(f'mv{k}', (0.04, 0.05, H), (-2.7 + k * 0.92, gy, 0), steel)
        for z in (0, 1.0, H - 0.05):
            box('mh', (4.6, 0.05, 0.05), (-0.4, gy, z), steel)
        box('meet_table', (2.6, 1.1, 0.05), (-0.4, gy + 1.1, 0.72), oak, bevel=0.004)
        box('meet_leg', (2.2, 0.08, 0.72), (-0.4, gy + 1.1, 0), steel)
        chair = mat('chair', '#2f4a43', rough=0.8)
        for k in range(4):
            for side in (-1, 1):
                soft(box('chair', (0.48, 0.48, 0.45), (-1.4 + k * 0.66, gy + 1.1 + side * 0.75, 0.0), chair, bevel=0.05), 1)
        box('screen', (1.6, 0.04, 0.9), (-0.4, D - 0.05, 1.0), mat('screen', '#0e1214', rough=0.1, coat=1))
        # стол open-space
        box('desk', (4.2, 0.9, 0.04), (-0.6, 2.4, 0.73), oak, bevel=0.003)
        for dx in (-2.5, 1.3):
            box('desk_leg', (0.05, 0.8, 0.73), (dx, 2.4, 0), steel)
        for k in range(3):
            mx = -2.0 + k * 1.4
            box(f'mon{k}', (0.62, 0.025, 0.38), (mx, 2.65, 0.95), mat('monitor', '#121212', rough=0.2))
            box(f'mon_s{k}', (0.6, 0.012, 0.35), (mx, 2.636, 0.965), mat_emit('ui', '#9fb4c0', 1.5))
            box(f'stand{k}', (0.05, 0.05, 0.2), (mx, 2.67, 0.77), steel)
            soft(box(f'oc{k}', (0.52, 0.5, 0.48), (mx, 1.7, 0), mat('chair2', '#1f1d1b', rough=0.7), bevel=0.05), 1)
        # линейные светильники
        for k in range(3):
            box(f'lin{k}', (0.06, 4.5, 0.05), (-1.8 + k * 1.6, 3.5, H - 0.4), mat_emit('lin', '#ffe9cc', 12))
            cyl('lin_cord', 0.003, 0.35, (-1.8 + k * 1.6, 3.5, H - 0.35), mat('cord', '#111111'))
        plant(W / 2 - 0.6, 1.8, h=1.6, pot='#1b1a18')
        plant(-W / 2 + 0.7, D - 3.0, h=1.3, pot='#1b1a18')
    daylight(sun_dir=(0.8, 0.45, -0.4), sun_strength=3.0, window=win, W=W, sky_strength=0.9, portal_strength=220)
    camera((1.4, 0.2, 1.55), (-0.4, D, 1.05), lens=18)
    return dict(exposure=0.1 if not raw else 0.4)


# ───────────────────────── Дом из бруса ─────────────────────────

def house(raw=False):
    W, D, H = 6.6, 6.4, 4.6
    win = (2.6, 2.4, 0.5, 3.4)
    if raw:
        raw_room(W, D, H, win)
    else:
        logs = mat_wood('logs', '#dcc4a2', '#b8956c', scale=1.5, rough=0.7)
        room(W, D, H, logs, mat('subfloor', '#3a2a1e'), mat_wood('ceil_wood', '#d8bf9b', '#b48e64', scale=2, rough=0.7), window=win)
        plank_floor(W, D, mat_plank('floor', '#a87a50', '#6f4a2c'))
        # швы бруса на стенах
        seam = mat('seam', '#8c6b4b', rough=0.9)
        for z in [0.18 * k for k in range(1, int(H / 0.18))]:
            box('seam_b', (W, 0.012, 0.01), (0, D - 0.004, z), seam)
            box('seam_r', (0.012, D, 0.01), (W / 2 - 0.004, D / 2, z), seam)
        beam = mat_wood('beam', '#9a6d45', '#6e4a2c', scale=2)
        for k in range(4):
            box(f'beam{k}', (W, 0.18, 0.24), (0, 0.9 + k * 1.6, H - 0.24), beam)
        steel = mat('blacksteel', '#141413', rough=0.4, metal=0.85)
        oak = mat_wood('oak_s', '#c79c71', '#94683f', scale=3)
        # лестница на металлическом косоуре вдоль задней стены
        n = 14
        for k in range(n):
            box(f'step{k}', (0.3, 0.95, 0.05), (W / 2 - 0.6 - k * 0.27, D - 0.6, 0.2 + k * 0.2), oak, bevel=0.004)
        L = math.hypot(n * 0.27, n * 0.2)
        ang = math.atan2(n * 0.2, n * 0.27)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(W / 2 - 0.6 - n * 0.27 / 2, D - 0.6, 0.1 + n * 0.2 / 2), rotation=(0, ang, 0))
        st = bpy.context.active_object
        st.scale = (L, 0.12, 0.08)
        st.data.materials.append(steel)
        for k in range(0, n, 2):
            cyl(f'bal{k}', 0.012, 0.95, (W / 2 - 0.6 - k * 0.27, D - 1.06, 0.25 + k * 0.2), steel)
        # камин
        box('fire_box', (1.4, 0.6, 1.3), (-1.4, D - 0.3, 0), mat('fire_body', '#1c1a18', rough=0.6), bevel=0.01)
        box('fire_hole', (0.9, 0.02, 0.55), (-1.4, D - 0.61, 0.35), mat('fire_dark', '#050505', rough=1))
        sphere('flame', 0.12, (-1.4, D - 0.45, 0.48), mat_emit('flame', '#ff9a3c', 40), scale=(1.6, 0.6, 1.2))
        point((-1.4, D - 0.75, 0.55), 60, '#ff9a4c', 0.2)
        cyl('chimney', 0.25, H - 1.3, (-1.4, D - 0.3, 1.3), mat('fire_body', '#1c1a18', rough=0.6))
        # кресло и ковёр
        green = mat_noise('velvet', '#2f4a43', '#36554b', scale=90, rough=0.8, bump=0.1)
        soft(box('arm_base', (0.85, 0.85, 0.42), (-1.2, 2.6, 0.08), green, bevel=0.08), 1)
        soft(box('arm_back', (0.85, 0.22, 0.45), (-1.2, 2.95, 0.48), green, bevel=0.08), 1)
        rug(-0.6, 2.8, 2.8, 2.0, color='#e2d8c8')
        cyl('side_t', 0.25, 0.5, (-0.4, 2.4, 0), oak)
        pendant(-0.3, 2.6, H, drop=1.8, r=0.3, power=16)
    daylight(sun_dir=(0.8, 0.45, -0.4), sun_strength=3.5, window=win, W=W, sky_strength=0.9, portal_strength=200)
    camera((1.4, 0.25, 1.5), (-0.5, D, 1.9), lens=17)
    return dict(exposure=0.1 if not raw else 0.4)


# ───────────────────────── Прихожая ─────────────────────────

def hall(raw=False):
    W, D, H = 3.2, 4.4, 2.75
    if raw:
        raw_room(W, D, H, None)
    else:
        wall = mat_noise('wall', '#e7e0d5', '#e7e0d5', scale=4, rough=0.9, bump=0.01)
        room(W, D, H, wall, mat('subfloor', '#3a2a1e'), mat('ceil', '#f4f1ec', rough=0.9))
        plank_floor(W, D, mat_plank('floor', '#c9a37a', '#93673f'))
        front = mat('wardrobe', '#e9e2d7', rough=0.5)
        # встроенный шкаф во всю левую стену
        for k in range(5):
            box(f'wd{k}', (0.6, 0.6, H - 0.03), (-W / 2 + 0.3, 0.6 + k * 0.605, 0), front, bevel=0.002)
        box('wd_led', (0.02, 3.0, 0.01), (-W / 2 + 0.62, 1.8, 0.05), mat_emit('wd_led', '#ffd9a8', 20))
        # скрытая дверь в задней стене — тонкий теневой шов
        shadow = mat('shadow_gap', '#3a3530', rough=1)
        for (sx, sz, x, z) in [(0.006, 2.1, -0.45, 0), (0.006, 2.1, 0.45, 0), (0.9, 0.006, 0, 2.1)]:
            box('gap', (sx, 0.01, sz), (x, D - 0.004, z), shadow)
        box('handle', (0.012, 0.03, 0.25), (0.35, D - 0.02, 0.95), mat('brass', '#b08a5a', rough=0.3, metal=1))
        # зеркало и скамья
        mir = cyl('mirror', 0.32, 0.02, (W / 2 - 0.02, 2.6, 1.0), mat('mirrorm', '#d6dada', rough=0.02, metal=1.0), rot=(0, math.radians(90), 0))
        mir.scale = (2.4, 1, 1)
        oak = mat_wood('oak_b', '#c9a077', '#93673f', scale=3)
        box('bench', (0.4, 1.2, 0.06), (W / 2 - 0.25, 1.4, 0.42), oak, bevel=0.004)
        for dy in (-0.5, 0.5):
            box('bench_leg', (0.36, 0.04, 0.42), (W / 2 - 0.25, 1.4 + dy, 0), mat('blackmetal', '#151413', rough=0.4, metal=0.85))
        soft(box('bench_cush', (0.38, 1.1, 0.06), (W / 2 - 0.25, 1.4, 0.48), mat('cush', '#b6774b', rough=0.9), bevel=0.02), 1)
        # вешалка
        steel = mat('blackmetal', '#151413', rough=0.4, metal=0.85)
        cyl('rack', 0.015, 1.8, (W / 2 - 0.35, D - 0.5, 0), steel)
        for a in range(3):
            box('hook', (0.25, 0.015, 0.015), (W / 2 - 0.35 + math.cos(a * 2.1) * 0.12, D - 0.5 + math.sin(a * 2.1) * 0.12, 1.75), steel, rot=(0, 0, a * 2.1))
        soft(box('coat', (0.36, 0.2, 0.9), (W / 2 - 0.35, D - 0.4, 0.85), mat_noise('coat', '#2f4a43', '#36554b', scale=70, rough=0.95, bump=0.1), bevel=0.06), 1)
        for k in range(3):
            cyl(f'spot{k}', 0.04, 0.02, (0, 1.0 + k * 1.2, H - 0.02), mat_emit('spot', '#fff0d8', 30))
            area((0, 1.0 + k * 1.2, H - 0.05), (0, 0, 0), 0.15, 25, '#ffe6c8')
    sc = bpy.context.scene
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.05
    sc.world = world
    camera((0.2, 0.15, 1.45), (0.0, D, 1.05), lens=18)
    return dict(exposure=0.4 if not raw else 0.6)


# ───────────────────────── Производство ─────────────────────────

def _hall(W=12, D=12, H=6):
    concrete = mat_noise('shopfloor', '#5f5c57', '#77736d', scale=1.5, rough=0.55, bump=0.05)
    panels = mat('sandwich', '#4a4844', rough=0.7)
    room(W, D, H, panels, concrete, mat('roof', '#3b3a37', rough=0.8), window=(5.0, 6.0, 2.6, 2.2))
    # горизонтальные стыки сэндвич-панелей
    for z in (1.2, 2.4, 3.6, 4.8):
        box('pj', (W, 0.01, 0.01), (0, D - 0.005, z), mat('pjm', '#2f2d2a'))
    steel = mat('trussm', '#4d4b47', rough=0.5, metal=0.7)
    for k in range(4):
        box(f'truss{k}', (W, 0.2, 0.35), (0, 2 + k * 3, H - 0.6), steel)
    for k in range(3):
        for j in range(3):
            box(f'lamp{k}{j}', (0.25, 1.4, 0.08), (-3 + k * 3, 2.5 + j * 3.5, H - 0.9), mat_emit('shoplamp', '#ffe6c2', 14))
            area((-3 + k * 3, 2.5 + j * 3.5, H - 0.95), (0, 0, 0), 0.25, 220, '#ffd9a8', size_y=1.4)
    # жёлтая разметка проходов
    box('lane', (0.08, D, 0.003), (-2.6, D / 2, 0), mat('lane', '#d9a62b', rough=0.6))
    daylight(sun_dir=(0.85, 0.4, -0.45), sun_strength=1.6, window=(5.0, 6.0, 2.6, 2.2), W=W, sky_strength=0.4, portal_strength=80)
    return W, D, H


def workshop_wood(raw=False):
    W, D, H = _hall()
    mdf = mat('mdf', '#c9a982', rough=0.7)
    oak = mat_wood('oak_w', '#d4b28a', '#a57d55', scale=2)
    steel = mat('machine', '#d7d5cf', rough=0.4, metal=0.4)
    green = mat('machine_g', '#2f4a43', rough=0.5)
    # форматно-раскроечный станок
    box('saw_table', (3.2, 1.6, 0.08), (0.6, 5.0, 0.84), steel, bevel=0.01)
    box('saw_body', (1.0, 1.0, 0.84), (0.6, 5.0, 0), green, bevel=0.02)
    box('saw_wing', (0.1, 1.6, 0.84), (-0.9, 5.0, 0), green)
    cyl('blade', 0.16, 0.004, (0.6, 5.0, 0.86), mat('blade', '#bdbdbd', rough=0.2, metal=1), rot=(math.radians(90), 0, 0))
    box('fence', (3.2, 0.06, 0.1), (0.6, 4.3, 0.92), mat('fence', '#9a9892', metal=0.8, rough=0.3))
    box('sheet_on', (1.8, 1.0, 0.018), (0.2, 5.1, 0.92), mdf)
    box('hood', (0.4, 0.3, 0.25), (0.6, 5.0, 1.6), green)
    cyl('hood_pipe', 0.08, H - 1.85, (0.6, 5.0, 1.85), mat('pipe', '#9a9892', metal=0.8, rough=0.4))
    # стопки плит на поддонах
    for k in range(2):
        box(f'pallet{k}', (2.8, 1.25, 0.14), (-3.6, 4.0 + k * 1.6, 0), mat_wood('pallet', '#b89c74', '#8f7552', scale=1))
        for j in range(18):
            box(f'stack{k}{j}', (2.75, 1.2, 0.018), (-3.6, 4.0 + k * 1.6, 0.14 + j * 0.019), mdf if (j + k) % 3 else oak)
    # верстак с готовыми фасадами
    box('bench', (2.6, 0.9, 0.05), (3.6, 8.2, 0.86), oak, bevel=0.005)
    for dx in (-1.2, 1.2):
        box('bench_leg', (0.08, 0.8, 0.86), (3.6 + dx, 8.2, 0), steel)
    for k in range(4):
        box(f'front{k}', (0.5, 0.02, 0.72), (2.7 + k * 0.6, 8.6, 0.91), mat('front_mat', '#2a2825', rough=0.5), rot=(math.radians(-8), 0, 0))
    box('edge_bander', (4.0, 0.9, 1.0), (1.2, 9.6, 0), mat('eb', '#e3e1db', rough=0.4, metal=0.3), bevel=0.02)
    box('eb_top', (4.0, 0.3, 0.12), (1.2, 9.3, 1.0), green)
    for k in range(4):
        box(f'rack_up{k}', (0.08, 0.08, 2.6), (-5.2 + k * 1.1, 9.8, 0), mat('rackm', '#2a2926', metal=0.6, rough=0.5))
    for k in range(10):
        box(f'board{k}', (3.4, 0.02, 2.0), (-3.55, 9.4 + k * 0.05, 0.3), mdf if k % 2 else oak, rot=(math.radians(-6), 0, 0))
    # опилки в луче света
    rnd = random.Random(4)
    dust = mat_emit('dust', '#fff2d8', 1.5)
    for k in range(120):
        sphere('dust', 0.004 + rnd.random() * 0.004, (0.3 + rnd.random() * 1.2, 4.6 + rnd.random() * 1.0, 0.95 + rnd.random() * 0.8), dust)
    camera((2.4, 1.9, 1.65), (-0.5, 6.8, 0.9), lens=20)
    return dict(exposure=0.2)


def workshop_metal(raw=False):
    W, D, H = _hall()
    steel = mat('steelraw', '#6d6b67', rough=0.35, metal=1.0)
    darksteel = mat('steeltable', '#3a3936', rough=0.5, metal=0.9)
    # сварочный стол с отверстиями
    box('wtable', (2.6, 1.3, 0.08), (0.4, 5.4, 0.86), darksteel, bevel=0.005)
    for dx in (-1.1, 1.1):
        for dy in (-0.5, 0.5):
            box('wleg', (0.1, 0.1, 0.86), (0.4 + dx, 5.4 + dy, 0), darksteel)
    for i in range(10):
        for j in range(5):
            cyl('hole', 0.014, 0.002, (-0.65 + i * 0.23, 4.95 + j * 0.23, 0.94), mat('holem', '#0a0a0a'))
    # каркас лофт-перегородки на столе
    fr = (2.0, 0.9)
    for (sx, sy, x, y) in [(fr[0], 0.04, 0.4, 5.0), (fr[0], 0.04, 0.4, 5.9), (0.04, fr[1], -0.6, 5.45), (0.04, fr[1], 1.4, 5.45), (0.04, fr[1], 0.4, 5.45)]:
        box('frame', (sx, sy, 0.04), (x, y, 0.94), steel)
    # искры сварки
    rnd = random.Random(9)
    spark = mat_emit('spark', '#ffb347', 60)
    for k in range(70):
        a = rnd.random() * math.tau
        r = 0.05 + rnd.random() * 0.6
        z = 0.98 + rnd.random() * 0.5
        L = 0.03 + rnd.random() * 0.1
        cyl('spark', 0.002, L, (0.4 + math.cos(a) * r, 5.45 + math.sin(a) * r, z - r * 0.4), spark, verts=6,
            rot=(rnd.random() * 1.2, rnd.random() * 1.2, a))
    sphere('arc', 0.03, (0.4, 5.45, 1.0), mat_emit('arc', '#e8f3ff', 200))
    point((0.4, 5.45, 1.05), 300, '#ffb35a', 0.05)
    # сварщик: маска и перчатка — только силуэт за столом
    box('screen', (2.0, 0.03, 1.8), (-1.6, 7.0, 0), mat('wscreen', '#7a2f1f', rough=0.6, transmission=0.2))
    # стеллаж профиля
    for dx in (-1.55, 1.55):
        box('rack_post', (0.06, 0.5, 2.4), (-3.8 + dx, 8.6, 0), darksteel)
    for k in range(5):
        box(f'rack{k}', (3.2, 0.5, 0.04), (-3.8, 8.6, 0.4 + k * 0.45), darksteel)
        for j in range(6):
            box(f'prof{k}{j}', (3.1, 0.04, 0.04), (-3.8, 8.42 + j * 0.07, 0.44 + k * 0.45), steel)
    camera((2.0, 2.7, 1.6), (0.2, 5.8, 0.95), lens=24)
    return dict(exposure=0.1)


def workshop_powder(raw=False):
    W, D, H = _hall()
    booth = mat('booth', '#d8d6d0', rough=0.5)
    filt = mat_noise('filter', '#9b9890', '#8a877f', scale=40, rough=1, bump=0.3)
    # открытая камера напыления
    bx, by = 0.6, 6.4
    box('booth_back', (3.6, 0.1, 2.8), (bx, by + 1.3, 0), filt)
    box('booth_l', (0.1, 2.6, 2.8), (bx - 1.8, by, 0), booth)
    box('booth_r', (0.1, 2.6, 2.8), (bx + 1.8, by, 0), booth)
    box('booth_top', (3.6, 2.6, 0.1), (bx, by, 2.8), booth)
    box('booth_light', (3.0, 0.15, 0.04), (bx, by, 2.75), mat_emit('booth_l', '#fff6e8', 30))
    area((bx, by, 2.7), (0, 0, 0), 1.0, 400, '#fff4e4', size_y=2.0)
    # монорельс с изделиями в цветах RAL
    box('rail', (6.0, 0.06, 0.06), (bx - 1.0, by, 2.35), mat('railm', '#555350', metal=0.8, rough=0.4))
    colors = ['#1b1a18', '#b6774b', '#2f4a43', '#e9e4dc', '#1a2b3c', '#5e2028']
    for k, c in enumerate(colors):
        x = bx - 3.6 + k * 0.85
        cyl('hook', 0.006, 0.4, (x, by, 1.95), mat('hookm', '#777777', metal=1))
        part = mat(f'ral{k}', c, rough=0.45, coat=0.4)
        box(f'part{k}', (0.6, 0.04, 1.0), (x, by, 0.95), part, bevel=0.004)
        box(f'partf{k}', (0.6, 0.3, 0.04), (x, by - 0.15, 0.95), part)
    # облако порошка у пистолета
    rnd = random.Random(5)
    powder = mat('powder', '#c8875a', rough=1)
    for k in range(220):
        r = rnd.random() ** 0.6 * 0.45
        a = rnd.random() * math.tau
        sphere('pw', 0.004 + rnd.random() * 0.005, (bx + 0.4 + math.cos(a) * r, by - 0.5 + rnd.random() * 0.4, 1.4 + math.sin(a) * r * 0.6), powder)
    box('gun', (0.35, 0.06, 0.06), (bx + 0.95, by - 0.55, 1.4), mat('gunm', '#d9d7d1', metal=0.5, rough=0.3), rot=(0, 0, math.radians(20)))
    # печь полимеризации справа
    box('oven', (2.4, 2.0, 2.6), (W / 2 - 1.8, 4.5, 0), mat('ovenm', '#bcbab4', rough=0.4, metal=0.5), bevel=0.02)
    box('oven_door', (0.02, 1.8, 2.3), (W / 2 - 3.01, 4.5, 0.1), mat('ovend', '#a9a7a1', rough=0.4, metal=0.6))
    camera((1.2, 0.6, 1.65), (0.2, 7.4, 1.1), lens=22)
    return dict(exposure=0.1)
