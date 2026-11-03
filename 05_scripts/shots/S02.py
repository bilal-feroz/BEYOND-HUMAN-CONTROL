"""S02 The Wave: wide, 20 mm, low at the waterline. Geography of the whole decision."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotlib  # noqa: E402
from bhc import core, env, layout  # noqa: E402

SHOT = "S02"
CAM = (6.3, 1.4, 0.25, 2.4, -0.6, 1.6, 18.0)


def main():
    a = shotlib.args(default_frame=168)
    t0 = time.time()
    M = layout.build_master(a.frame)
    f0, f1 = core.SHOTS[SHOT]
    cx, cy, h, tx, ty, tz, lens = CAM
    if a.cam:
        cx, cy, h, tx, ty, tz, lens = (float(v) for v in a.cam.split(","))
    zc, _ = env.water_height(M["ocean"], cx, cy, a.frame)
    px, py = layout.POS["person"]
    focus = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
    cam = core.camera("CAM_S02", M["C"]["CAMS"], (cx, cy, zc + h), (tx, ty, tz), lens=lens, fstop=5.6, focus=focus)
    # slow 0.5 m crane up across the shot (keys around the test frame so it stays at its framing)
    k = (a.frame - f0) / (f1 - f0)
    cam.location.z = zc + h - 0.5 * k
    cam.keyframe_insert("location", index=2, frame=f0)
    cam.location.z = zc + h + 0.5 * (1 - k)
    cam.keyframe_insert("location", index=2, frame=f1)
    M["scene"].camera = cam
    shotlib.finish(SHOT, a, t0)


main()
