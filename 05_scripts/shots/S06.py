"""S06 Waterline: split dome-port view, 16 mm. The only complete picture, which no single machine has.

A pinhole camera cannot see both worlds at once, so the shot renders twice (lens 3 cm above and
3 cm below the flattened surface) and composites the halves with a meniscus, like a dome port.
"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotlib  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from bhc import core, env, layout  # noqa: E402

SHOT = "S06"
CAM_XY = (5.9, 1.6)
HALF = 0.03


def load(path):
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.array(img.pixels[:], np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return a


def composite(above, below, out, split=0.5, soft=6):
    a, b = load(above), load(below)
    h, w = a.shape[:2]
    y = np.arange(h, dtype=np.float32)[:, None]          # row 0 = bottom (Blender pixel order)
    line = h * split + 3.0 * np.sin(np.linspace(0, 9, w))[None, :]   # slight meniscus wobble
    m = np.clip((y - line) / soft + 0.5, 0, 1)[..., None]  # 1 above the line
    c = a * m + b * (1 - m)
    band = np.exp(-((y - line) / 2.2) ** 2)[..., None]     # dark meniscus edge with a thin highlight
    hi = np.exp(-((y - line - 3.5) / 1.2) ** 2)[..., None]
    c[..., :3] = c[..., :3] * (1 - 0.65 * band) + 0.08 * hi
    img = bpy.data.images.new("S06_comp", w, h, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(c.astype(np.float32).ravel())
    img.filepath_raw = out
    img.file_format = 'PNG'
    img.save()


def main():
    a = shotlib.args(default_frame=540)
    t0 = time.time()
    M = layout.build_master(a.frame, underwater=True, flatten=(CAM_XY, 2.0))
    f0, f1 = core.SHOTS[SHOT]
    zc, _ = env.water_height(M["ocean"], *CAM_XY, a.frame)
    cam = core.camera("CAM_S06", M["C"]["CAMS"], (CAM_XY[0], CAM_XY[1], zc + HALF),
                      (2.6, -1.2, zc + HALF), lens=16, fstop=8.0, focus=2.4)
    # slow push toward the person (x/y only; z is set per pass)
    for i in (0, 1):
        cam.keyframe_insert("location", index=i, frame=f0)
    cam.location.x -= 0.35
    cam.location.y -= 0.2
    for i in (0, 1):
        cam.keyframe_insert("location", index=i, frame=f1)
    sc = M["scene"]
    sc.camera = cam
    if a.norender:
        shotlib.finish(SHOT, a, t0)
        return
    sc.frame_start, sc.frame_end = f0, f1
    core.render_setup(sc, pct=a.pct, samples=a.samples, quality=a.quality)
    core.comp_setup(sc)
    sc.frame_set(a.frame)
    core.save(core.path("04_scenes", f"{SHOT}_{a.ver}.blend"))
    t1 = time.time()
    outs = {}
    for side, dz in (("above", HALF), ("below", -HALF)):
        cam.location.z = zc + dz
        # murk only exists in the underwater pass (above, it leaks into the air over the troughs)
        for n in ("BHC_Underwater", "BHC_Particulates"):
            bpy.data.objects[n].hide_render = side == "above"
        if a.anim:
            sc.render.filepath = core.path("06_renders", a.out, SHOT, side, f"{SHOT}_{side}_####")
            bpy.ops.render.render(animation=True)
        else:
            p = core.path("06_renders", a.out, f"{SHOT}_{a.ver}_{side}_f{a.frame:04d}.png")
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            outs[side] = p
    if a.anim:
        print(f"RESULT shot={SHOT} anim passes rendered; composite in 07_comp")
        return
    out = core.path("06_renders", a.out, f"{SHOT}_{a.ver}_f{a.frame:04d}.png")
    composite(outs["above"], outs["below"], out)
    print(f"RESULT shot={SHOT} frame={a.frame} build_s={t1 - t0:.1f} render_s={time.time() - t1:.1f} out={out}")


main()
