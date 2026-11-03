"""Project story objects into a shot camera's frame (1920x1080, y down) for motion-graphics overlays.

  blender -b --factory-startup --python-exit-code 1 -P 05_scripts/tools/project_points.py -- --shot S07 --frame 650
Writes 09_edit/work/<shot>_f<frame>_points.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "shots"))

import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402
from bhc import core, env, layout  # noqa: E402
import shots  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    shot = argv[argv.index("--shot") + 1]
    frame = int(argv[argv.index("--frame") + 1])
    cam_fn, place, kw, _, _ = shots.SPECS[shot]
    f0, f1 = core.SHOTS[shot]
    M = layout.build_master(place, **kw)
    cam = cam_fn(M, f0, f1)
    sc = M["scene"]
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.frame_set(frame)
    bpy.context.view_layer.update()
    T = core.real_time(frame)
    k, om = env.wave_k(), env.wave_omega()
    crest_x = lambda y: (om * T) / k + env.WAVE["lean"] * 0.95  # noqa: E731  approximate lip line
    pts = {
        "UAV_1": M["uav1"]["root"].matrix_world.to_translation(),
        "UAV_2": M["uav2"]["root"].matrix_world.to_translation(),
        "USV_1": M["usv"]["root"].matrix_world @ Vector((0, 0, 1.0)),
        "AUV_1": M["auv"]["root"].matrix_world.to_translation(),
        "PERSON": M["person"]["root"].matrix_world.to_translation(),
        "CAPSIZED": M["capsized"]["root"].matrix_world.to_translation(),
        "BEAM_SPOT": M["person"]["root"].matrix_world.to_translation() + layout.SEARCH_OFFSET,
        "CREST_A": Vector((crest_x(-12), -12, 1.5)),
        "CREST_B": Vector((crest_x(12), 12, 1.5)),
    }
    out = {}
    for name, p in pts.items():
        v = world_to_camera_view(sc, cam, p)
        out[name] = {"x": round(v.x * 1920, 1), "y": round((1 - v.y) * 1080, 1), "depth": round(v.z, 2),
                     "world": [round(c, 2) for c in p]}
    path = core.path("09_edit", "work", f"{shot}_f{frame:04d}_points.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print("RESULT", path, json.dumps({k_: (v["x"], v["y"]) for k_, v in out.items()}))


main()
