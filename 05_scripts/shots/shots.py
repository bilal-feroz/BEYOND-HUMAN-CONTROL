"""All 12 shots on the shared master layout (production document, section 5).

Usage (headless):
  blender -b --factory-startup --python-exit-code 1 -P 05_scripts/shots/shots.py -- --shot S05 [--anim]
      [--pct 50 --samples 12 --quality preview --ver p001 --out previews] [--frame N] [--start N --end N]

Each shot = master layout kwargs + a camera function. Nothing about the environment is rebuilt per shot.
"""
import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402
from bhc import core, env, layout  # noqa: E402


# ---------------------------------------------------------------- camera helpers

def _smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _look(cam, loc, target, roll=0.0):
    cam.location = loc
    q = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y')
    if roll:
        q = q @ Matrix.Rotation(math.radians(roll), 4, 'Z').to_quaternion()
    prev = cam.rotation_euler.copy()
    cam.rotation_euler = q.to_euler('XYZ', prev)


def move(cam, f0, f1, loc0, tgt0, loc1, tgt1, step=4, focus=None):
    """Eased dolly between two framings, keyed every `step` frames (keys are linear by default)."""
    for f in list(range(f0, f1, step)) + [f1]:
        k = _smooth((f - f0) / max(f1 - f0, 1))
        _look(cam, Vector(loc0).lerp(Vector(loc1), k), Vector(tgt0).lerp(Vector(tgt1), k))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        if focus:
            cam.data.dof.focus_distance = focus[0] + (focus[1] - focus[0]) * k
            cam.data.dof.keyframe_insert("focus_distance", frame=f)


def new_cam(M, name, lens, fstop=None, focus=5.0):
    cam = core.camera(name, M["C"]["CAMS"], (0, 0, 10), (0, 1, 10), lens=lens, fstop=fstop, focus=focus)
    M["scene"].camera = cam
    return cam


def water_z(M, x, y, frame):
    z, _ = env.water_height(M["ocean"], x, y, frame)
    return z


def world(ob, local):
    bpy.context.view_layer.update()
    return ob.matrix_world @ Vector(local)


# ---------------------------------------------------------------- shots

def s01(M, f0, f1):
    cam = new_cam(M, "CAM_S01", 50, 2.8, 1.0)
    move(cam, f0, f1, (5.78, 2.78, 1.96), (4.55, 1.5, 1.72), (5.5, 2.5, 1.9), (4.55, 1.5, 1.72), focus=(1.05, 0.95))
    return cam


def s02(M, f0, f1):
    cam = new_cam(M, "CAM_S02", 18, 5.6, 2.5)
    zc = water_z(M, 6.3, 1.4, (f0 + f1) // 2)
    move(cam, f0, f1, (6.3, 1.4, zc + 0.12), (2.4, -0.6, 1.45), (6.3, 1.4, zc + 0.55), (2.4, -0.6, 1.8), focus=(2.5, 2.6))
    return cam


def s03(M, f0, f1):
    r = M["uav1"]["root"]
    cam = new_cam(M, "CAM_S03", 35, 2.8, 1.4)
    move(cam, f0, f1, world(r, (0.25, 1.45, 0.08)), world(r, (0.05, 0.0, -0.12)),
         world(r, (-0.02, 0.95, 0.0)), world(r, (-0.1, 0.0, -0.11)), focus=(1.45, 0.98))
    tame_glare(0.2)
    return cam


def tame_glare(k):
    """Close-ups of the robots: lamps and nav LEDs scaled down so the hardware reads."""
    for n in ("BHC_SearchLens", "BHC_LED_Red", "BHC_LED_Green", "BHC_LED_White"):
        m = bpy.data.materials.get(n)
        if m:
            for nd in m.node_tree.nodes:
                if nd.bl_idname == "ShaderNodeEmission":
                    nd.inputs["Strength"].default_value *= k
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and "_NavL" in o.name:
            o.data.energy *= k


def s04(M, f0, f1):
    cam = new_cam(M, "CAM_S04", 35, 4.0, 8.0)
    zc = water_z(M, -9.0, -12.6, (f0 + f1) // 2)
    u = M["usv"]["root"]
    tgt = world(u, (0.6, 0, 1.3))
    a0, a1 = Vector((-9.0, -12.6, zc + 0.5)), Vector((-8.3, -12.8, zc + 0.6))     # aft quarter: hull profile, crest beyond
    move(cam, f0, f1, a0, tgt, a1, tgt + Vector((0.3, 0.1, 0.1)), focus=((tgt - a0).length, (tgt - a1).length))
    tame_glare(0.5)
    return cam


def s05(M, f0, f1):
    cam = new_cam(M, "CAM_S05", 20, 4.0, 3.0)
    move(cam, f0, f1, (-1.9, -4.6, -5.6), (3.4, -1.2, -1.2), (-1.55, -4.25, -5.35), (3.5, -1.0, -0.9))
    return cam


def s06(M, f0, f1):
    cam = new_cam(M, "CAM_S06", 16, 8.0, 2.4)
    zc = water_z(M, 5.9, 1.6, (f0 + f1) // 2)
    M["s06_zc"] = zc
    bpy.data.objects["AUV_1_Light"].data.energy = 320     # it faces the camera here: a soft backlight, not a flood
    # x/y/rotation keyed; z is left unkeyed so each dome-port pass can set it (+/- 3 cm)
    for f in list(range(f0, f1, 4)) + [f1]:
        k = _smooth((f - f0) / (f1 - f0))
        _look(cam, Vector((5.9, 1.6, zc)).lerp(Vector((5.55, 1.4, zc)), k), (2.6, -1.2, zc))
        cam.keyframe_insert("location", index=0, frame=f)
        cam.keyframe_insert("location", index=1, frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    return cam


def s07(M, f0, f1):
    cam = new_cam(M, "CAM_S07", 35, None)
    u2 = Vector(layout.POS["uav2"])
    tgt0, tgt1 = Vector((2.5, -1.0, 0.0)), Vector((3.4, -0.4, 0.0))
    d = (tgt0 - u2).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    loc0 = u2 - 4.8 * d - 1.2 * side + Vector((0, 0, 1.4))
    loc1 = loc0 + 6.0 * d
    move(cam, f0, f1, loc0, tgt0, loc1, tgt1)
    return cam


def s08(M, f0, f1):
    u = M["usv"]["root"]
    cam = new_cam(M, "CAM_S08", 40, 2.8, 1.5)
    tgt0, tgt1 = world(u, (-0.62, -0.12, 3.0)), world(u, (-0.66, -0.14, 3.02))
    move(cam, f0, f1, world(u, (0.55, -1.2, 3.25)), tgt0, world(u, (0.4, -1.0, 3.2)), tgt1, focus=(1.7, 1.45))
    tame_glare(0.4)
    return cam


def s09(M, f0, f1):
    # elevated oblique across the crest: the closest machine (left), the breaking lip, the person (right)
    cam = new_cam(M, "CAM_S09", 24, 8.0, 19.0)     # 10 m up: the line of sight to the person clears the crest
    move(cam, f0, f1, (-3.6, -17.6, 10.6), (-0.5, -2.6, 0.0), (-3.1, -16.9, 10.1), (-0.3, -2.4, 0.1))
    return cam


def s10(M, f0, f1):
    cam = new_cam(M, "CAM_S10", 28, 4.0, 10.5)
    move(cam, f0, f1, (1.95, 3.45, 10.55), (4.5, 0.3, 0.2), (2.2, 3.1, 10.25), (4.3, 0.1, 0.2))
    return cam


def s11(M, f0, f1):
    """Real time, handheld, riding the water: the wave lifts the camera as it breaks past."""
    cam = new_cam(M, "CAM_S11", 28, 5.6, 7.0)
    sc = M["scene"]
    p = M["person"]["root"]
    for f in range(f0, f1 + 1):
        T = core.real_time(f)
        sc.frame_set(f)
        hit = _smooth((T - 0.45) / 0.3) * (1 - _smooth((T - 1.6) / 0.8))      # shake peaks as the break passes
        amp = 0.03 + 0.12 * hit
        jit = Vector((amp * math.sin(13.1 * T) + 0.6 * amp * math.sin(31.7 * T),
                      amp * math.sin(11.3 * T + 1.0) + 0.6 * amp * math.sin(27.9 * T),
                      amp * math.sin(17.9 * T + 2.0)))
        loc = Vector((10.8, 3.6, 1.7)) + jit
        tgt = p.matrix_world.to_translation() + Vector((0, 0, 0.35)) + 2.5 * jit
        _look(cam, loc, tgt, roll=4.0 * hit * math.sin(9.0 * T))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    return cam


def s12(M, f0, f1):
    cam = new_cam(M, "CAM_S12", 35, 5.6, 15.0)
    move(cam, f0, f1, (2.0, -14.5, 4.5), (3.6, 0.6, 2.5), (2.05, -14.35, 4.45), (3.6, 0.6, 2.4))
    return cam


SPECS = {
    # shot: (camera fn, placement frame, build kwargs, cull radius, motion blur)
    "S01": (s01, 60, dict(local_mist=(3500, (3.9, 0.7, 1.0), (5.3, 2.3, 2.6), 0.0008, 0.0026)), 0.12, False),
    "S02": (s02, 168, dict(), 1.2, False),
    "S03": (s03, 264, dict(local_mist=(5000, (1.5, 0.5, 7.8), (4.6, 3.6, 10.2), 0.0006, 0.002)), 0.25, False),
    "S04": (s04, 348, dict(local_mist=(3000, (-8.5, -7.5, -0.5), (-3.0, -2.0, 3.0), 0.0006, 0.002)), 0.8, False),
    "S05": (s05, 432, dict(underwater=True), 0.5, False),
    "S06": (s06, 540, dict(underwater=True, flatten=((5.9, 1.6), 2.0)), 1.0, False),
    "S07": (s07, 648, dict(), 1.0, False),
    "S08": (s08, 732, dict(local_mist=(3000, (-8.0, -6.5, 1.5), (-4.0, -3.0, 4.5), 0.0006, 0.0018)), 0.3, False),
    "S09": (s09, 816, dict(), 1.5, False),
    "S10": (s10, 924, dict(), 0.8, False),
    "S11": (s11, 1000, dict(realtime_range=(985, 1056), spray_count=100000), 0.6, True),
    "S12": (s12, 1128, dict(realtime_range=(1057, 1200), heli=True), 1.5, True),
}


# ---------------------------------------------------------------- S06 dome-port composite

def _load(path):
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    a = np.array(img.pixels[:], np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return a


def dome_composite(above, below, out, split=0.5, soft=6):
    a, b = _load(above), _load(below)
    h, w = a.shape[:2]
    y = np.arange(h, dtype=np.float32)[:, None]
    line = h * split + (3.0 * h / 1080) * np.sin(np.linspace(0, 9, w))[None, :]
    m = np.clip((y - line) / (soft * h / 1080) + 0.5, 0, 1)[..., None]
    c = a * m + b * (1 - m)
    s = h / 1080
    band = np.exp(-((y - line) / (2.2 * s)) ** 2)[..., None]
    hi = np.exp(-((y - line - 3.5 * s) / (1.2 * s)) ** 2)[..., None]
    c[..., :3] = c[..., :3] * (1 - 0.65 * band) + 0.08 * hi
    img = bpy.data.images.new("dome", w, h, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(c.astype(np.float32).ravel())
    img.filepath_raw = out
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


# ---------------------------------------------------------------- main

def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", required=True)
    ap.add_argument("--frame", type=int, default=None)
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--pct", type=int, default=50)
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--quality", default="preview")
    ap.add_argument("--ver", default="p001")
    ap.add_argument("--out", default="previews")
    ap.add_argument("--anim", action="store_true")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--res", default=None, help="WxH, e.g. 1080x1920 for the vertical cut, 2400x3600 for posters")
    ap.add_argument("--frames", default=None, help="comma list of stills to render (posters)")
    a = ap.parse_args(argv)
    shot = a.shot
    cam_fn, place, kw, cull, mblur = SPECS[shot]
    f0, f1 = core.SHOTS[shot]
    t0 = time.time()
    M = layout.build_master(place, **kw)
    cam = cam_fn(M, f0, f1)
    layout.cull_near(M, cam, cull)
    sc = M["scene"]
    sc.frame_start, sc.frame_end = (a.start or f0), (a.end or f1)
    res = tuple(int(v) for v in a.res.split("x")) if a.res else (1920, 1080)
    core.render_setup(sc, res=res, pct=a.pct, samples=a.samples, quality=a.quality, motion_blur=mblur)
    if a.res:
        cam.data.sensor_fit = 'AUTO'          # portrait: the long side keeps the 16:9 horizontal field
    sc.eevee.motion_blur_steps = 1
    core.comp_setup(sc)
    frame = a.frame or (f0 + f1) // 2
    sc.frame_set(frame)
    core.save(core.path("04_scenes", f"{shot}_{a.ver}.blend"))
    if a.norender:
        print(f"RESULT shot={shot} build_s={time.time() - t0:.1f}")
        return
    t1 = time.time()
    passes = [("", None)]
    if shot == "S06":
        passes = [("above", 0.03), ("below", -0.03)]
    outs = {}
    for side, dz in passes:
        if dz is not None:
            cam.location.z = M["s06_zc"] + dz
            for n in ("BHC_Underwater", "BHC_Particulates", "BHC_Ping1", "BHC_Echo1", "BHC_Ping2", "BHC_Echo2"):
                o = bpy.data.objects.get(n)
                if o:
                    o.hide_render = side == "above"
        sub = f"_{side}" if side else ""
        if a.anim:
            sc.render.filepath = core.path("06_renders", a.out, shot + sub, f"{shot}{sub}_####")
            bpy.ops.render.render(animation=True)
            outs[side] = os.path.dirname(sc.render.filepath)
        elif a.frames:
            for fr in (int(v) for v in a.frames.split(",")):
                p = core.path("06_renders", a.out, f"{shot}_{a.ver}{sub}_f{fr:04d}.png")
                sc.render.filepath = p
                sc.frame_set(fr)
                bpy.ops.render.render(write_still=True)
                outs[side] = p
        else:
            p = core.path("06_renders", a.out, f"{shot}_{a.ver}{sub}_f{frame:04d}.png")
            sc.render.filepath = p
            sc.frame_set(frame)
            bpy.ops.render.render(write_still=True)
            outs[side] = p
    if shot == "S06":
        if a.anim:
            dst = os.path.dirname(core.path("06_renders", a.out, shot, "x"))
            for f in range(sc.frame_start, sc.frame_end + 1):
                dome_composite(os.path.join(outs["above"], f"S06_above_{f:04d}.png"),
                               os.path.join(outs["below"], f"S06_below_{f:04d}.png"),
                               os.path.join(dst, f"S06_{f:04d}.png"))
            outs[""] = dst
            import shutil
            for side in ("above", "below"):
                shutil.rmtree(outs[side], ignore_errors=True)     # disk: keep only the composite
        else:
            outs[""] = core.path("06_renders", a.out, f"{shot}_{a.ver}_f{frame:04d}.png")
            dome_composite(outs["above"], outs["below"], outs[""])
    print(f"RESULT shot={shot} frames={sc.frame_start}-{sc.frame_end if a.anim else frame} "
          f"build_s={t1 - t0:.1f} render_s={time.time() - t1:.1f} out={outs['']}")


if __name__ == "__main__":
    main()
