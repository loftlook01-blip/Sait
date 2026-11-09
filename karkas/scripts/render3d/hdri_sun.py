"""Находит направление на солнце в equirect-HDRI: python hdri_sun.py file.hdr …"""
import sys, math, bpy
import numpy as np
for path in sys.argv[1:]:
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    lum = px[..., :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    y, x = np.unravel_index(np.argmax(lum), lum.shape)
    u, v = (x + 0.5) / w, (y + 0.5) / h  # v от низа
    elev = (v - 0.5) * 180
    # Blender: u = atan2(dir.y, -dir.x) / 2π + 0.5
    phi = (u - 0.5) * 2 * math.pi
    d = (-math.cos(phi), math.sin(phi))
    az = math.degrees(math.atan2(d[0], d[1]))  # 0 = +Y, 90 = +X
    print(f'{path.split("/")[-1]}: max {lum.max():.0f}, mean {lum.mean():.2f}, elev {elev:.1f}°, azimuth(from +Y toward +X) {az:.1f}°, u={u:.3f}')
