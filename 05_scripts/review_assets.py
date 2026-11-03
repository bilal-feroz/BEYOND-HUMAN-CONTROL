"""Asset review: every robot and prop under neutral studio light, one sheet per run."""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from bhc import core, assets  # noqa: E402


def main():
    sc = core.reset_scene()
    C = core.collection("REVIEW")
    w = bpy.data.worlds.new("Studio")
    sc.world = w
    if w.node_tree is None:
        w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.bl_idname == "ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.05, 0.055, 0.06, 1)
    bg.inputs["Strength"].default_value = 1.0
    P = assets.palette()
    usv = assets.build_usv(C, "USV_1", P)
    usv["root"].location = (0, 0, 0)
    usv["root"].rotation_euler = (0, 0, math.radians(-25))
    uav = assets.build_uav(C, "UAV_1", P, "search")
    uav["root"].location = (5.6, -0.6, 1.4)
    uav["root"].rotation_euler = (math.radians(8), 0, math.radians(-35))
    uav["root"].scale = (1.6, 1.6, 1.6)
    uav2 = assets.build_uav(C, "UAV_2", P, "relay")
    uav2["root"].location = (5.8, 2.4, 2.2)
    uav2["root"].rotation_euler = (0, 0, math.radians(20))
    uav2["root"].scale = (1.6, 1.6, 1.6)
    auv = assets.build_auv(C, "AUV_1", P)
    auv["root"].location = (2.0, 3.6, 0.6)
    auv["root"].rotation_euler = (0, 0, math.radians(-15))
    auv["root"].scale = (1.6, 1.6, 1.6)
    per = assets.build_person(C, "Person", P)
    per["root"].location = (7.6, 0.8, 1.6)
    per["root"].rotation_euler = (0, 0, math.radians(200))
    cap = assets.build_capsized(C, "Capsized", P)
    cap["root"].location = (-1.0, 5.5, 0.0)
    cap["root"].rotation_euler = (0, 0, math.radians(10))
    for o in C.objects:
        if o.type == 'LIGHT' and o.data.type == 'SPOT':
            o.data.energy *= 0.05
    key = core.spot_light("Key", C, (6, -9, 9), Vector((-2, 9, -8)), 9000, angle_deg=55, blend=0.8, temp=5600, radius=1.5)
    core.spot_light("Rim", C, (-6, 8, 6), Vector((7, -6, -5)), 6000, angle_deg=60, blend=0.8, temp=6500, radius=1.0)
    core.point_light("Fill", C, (10, 4, 3), (0.9, 0.95, 1.0), 800, radius=2.0)
    cam = core.camera("CAM_Review", C, (10.5, -9.5, 5.2), (3.2, 1.2, 0.6), lens=35, fstop=None)
    sc.camera = cam
    core.render_setup(sc, res=(1920, 1080), samples=64)
    sc.view_settings.exposure = 0.0
    sc.render.filepath = core.path("06_renders", "tests", "asset_review_v002.png")
    bpy.ops.render.render(write_still=True)
    print("RESULT", sc.render.filepath)


main()
