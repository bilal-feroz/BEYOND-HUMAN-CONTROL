"""Shared CLI handling for shot scripts: build, save a versioned .blend, render a frame or a range."""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bpy  # noqa: E402
from bhc import core  # noqa: E402


def args(default_frame):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=int, default=default_frame)
    ap.add_argument("--pct", type=int, default=100)
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--quality", default="final")
    ap.add_argument("--ver", default="v001")
    ap.add_argument("--out", default="tests")
    ap.add_argument("--anim", action="store_true", help="render the whole shot range")
    ap.add_argument("--norender", action="store_true")
    ap.add_argument("--exposure", type=float, default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--cam", default=None, help="x,y,height,tx,ty,tz,lens override")
    return ap.parse_args(argv)


def finish(shot, a, t0):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = core.SHOTS[shot]
    core.render_setup(sc, pct=a.pct, samples=a.samples, quality=a.quality)
    core.comp_setup(sc)
    if a.exposure is not None:
        sc.view_settings.exposure = a.exposure
    sc.frame_set(a.frame)
    core.save(core.path("04_scenes", f"{shot}_{a.ver}.blend"))
    if a.norender:
        print(f"RESULT shot={shot} built_s={time.time() - t0:.1f}")
        return
    t1 = time.time()
    if a.anim:
        sc.render.filepath = core.path("06_renders", a.out, shot, f"{shot}_####")
        bpy.ops.render.render(animation=True)
        out = os.path.dirname(sc.render.filepath)
    else:
        out = core.path("06_renders", a.out, f"{shot}_{a.ver}{a.tag}_f{a.frame:04d}.png")
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    print(f"RESULT shot={shot} frame={a.frame} build_s={t1 - t0:.1f} render_s={time.time() - t1:.1f} out={out}")
