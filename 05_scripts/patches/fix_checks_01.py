"""Fixes from the 12-frame check sheet (2026-11-04): whitewater read as rocks, sonar shell too strong,
S03 glare, unreadable S11, S12 into the moon, weak S04/S07/S08 framings."""
import os, sys
ROOT = sys.argv[1]


def patch(rel, reps):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in reps:
        assert a in s, (rel, a[:90])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)


patch("05_scripts/bhc/env.py", [
    # whitewater: fine froth on the lip only, not fist-sized clumps
    ('''    b.inputs["Base Color"].default_value = (0.78, 0.80, 0.80, 1)
    b.inputs["Roughness"].default_value = 0.6''', '''    b.inputs["Base Color"].default_value = (0.9, 0.92, 0.92, 1)
    b.inputs["Roughness"].default_value = 0.9'''),
    ('''    dens = g.add_input("Density", "NodeSocketFloat", 260.0)''', '''    dens = g.add_input("Density", "NodeSocketFloat", 4000.0)'''),
    ('''    w = g.math("MULTIPLY", g.math("POWER", g.math("MAXIMUM", g.math("SUBTRACT", c, 0.35), 0.0), 1.6), dens)''',
     '''    T = g.real_time()
    brk = g.ramp(T, core.DECISION, core.DECISION + 0.25)
    thr = g.math("MULTIPLY_ADD", brk, -0.25, 0.62)          # lip only before the snap, more of the face after
    w = g.math("MULTIPLY", g.math("POWER", g.math("MAXIMUM", g.math("SUBTRACT", c, thr), 0.0), 1.2), dens)
    w = g.math("MULTIPLY", w, g.math("MULTIPLY_ADD", brk, -0.65, 1.0))'''),
    ('''    g.link(g.vmath("SCALE", dp.outputs["Normal"], scale=g.rand(0.0, 0.05, 3)), sp.inputs["Offset"])''',
     '''    g.link(g.vmath("SCALE", dp.outputs["Normal"], scale=g.rand(0.0, 0.03, 3)), sp.inputs["Offset"])'''),
    ('''    s = g.rand(0.015, 0.075, 4)
    g.link(g.xyz(s, s, g.math("MULTIPLY", s, 0.45)), iop.inputs["Scale"])''',
     '''    s = g.math("MULTIPLY", g.math("POWER", g.rand(0.0, 1.0, 4), 2.0), g.math("MULTIPLY_ADD", brk, 0.02, 0.012))
    s = g.math("ADD", s, 0.003)
    g.link(g.xyz(s, s, g.math("MULTIPLY", s, 0.5)), iop.inputs["Scale"])'''),
    ('''def build_whitewater(coll, ocean, density=260.0):''', '''def build_whitewater(coll, ocean, density=4000.0):'''),
])

patch("05_scripts/bhc/fx.py", [
    # sonar shell: a faint grazing rim, not a glass dome
    ('''    pw = N("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0''',
     '''    pw = N("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 8.0'''),
    ('''    mul2 = N("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = 1.6''',
     '''    mul2 = N("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = 0.5'''),
    ('''                                            "Radius Min": 0.0012, "Radius Max": 0.006})''',
     '''                                            "Radius Min": 0.0006, "Radius Max": 0.0026})'''),
])

patch("05_scripts/bhc/layout.py", [
    # S12: hold station north-east of the person (out of the moon side); helicopter from the coast
    ('''        return 8.2 - 0.12 * dt, -3.6 + 0.08 * dt, 150.0''', '''        return 7.4 - 0.07 * dt, 2.7 - 0.05 * dt, 205.0'''),
    ('''    a, b = Vector((-170.0, -95.0, 34.0)), Vector((-105.0, -58.0, 27.0))''',
     '''    a, b = Vector((-25.0, 175.0, 32.0)), Vector((-12.0, 105.0, 26.0))'''),
])

patch("05_scripts/shots/shots.py", [
    ('''def s01(M, f0, f1):
    cam = new_cam(M, "CAM_S01", 50, 2.0, 1.0)''', '''def s01(M, f0, f1):
    cam = new_cam(M, "CAM_S01", 50, 2.8, 1.0)'''),
    ('''    "S01": (s01, 60, dict(local_mist=(7000, (3.9, 0.7, 1.0), (5.3, 2.3, 2.6), 0.0008, 0.003)), 0.12, False),''',
     '''    "S01": (s01, 60, dict(local_mist=(3500, (3.9, 0.7, 1.0), (5.3, 2.3, 2.6), 0.0008, 0.0026)), 0.12, False),'''),
    # S03: side-on to the drone; tame close-up glare
    ('''def s03(M, f0, f1):
    r = M["uav1"]["root"]
    cam = new_cam(M, "CAM_S03", 35, 2.8, 1.0)
    move(cam, f0, f1, world(r, (0.75, 1.05, -0.12)), world(r, (0.02, 0.0, -0.1)),
         world(r, (0.5, 0.72, -0.1)), world(r, (0.0, -0.1, -0.16)), focus=(1.25, 2.6))
    return cam''', '''def s03(M, f0, f1):
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
            o.data.energy *= k'''),
    # S04: pull back so the vessel reads against the crest
    ('''    cam = new_cam(M, "CAM_S04", 28, 4.0, 5.0)
    zc = water_z(M, -9.8, -7.6, (f0 + f1) // 2)
    u = M["usv"]["root"]
    tgt = world(u, (0.3, 0, 1.0))
    move(cam, f0, f1, (-9.9, -7.8, zc + 0.55), tgt, (-9.3, -8.2, zc + 0.7), tgt + Vector((0.4, 0, 0.15)),
         focus=((tgt - Vector((-9.9, -7.8, zc))).length, (tgt - Vector((-9.3, -8.2, zc))).length))''',
     '''    cam = new_cam(M, "CAM_S04", 35, 4.0, 8.0)
    zc = water_z(M, -12.6, -9.9, (f0 + f1) // 2)
    u = M["usv"]["root"]
    tgt = world(u, (0.6, 0, 1.3))
    a0, a1 = Vector((-12.6, -9.9, zc + 0.5)), Vector((-12.1, -10.3, zc + 0.6))
    move(cam, f0, f1, a0, tgt, a1, tgt + Vector((0.3, 0.1, 0.1)), focus=((tgt - a0).length, (tgt - a1).length))
    tame_glare(0.5)'''),
    # S07: UAV-2 small in the lower-left third, the swarm below
    ('''    loc0 = u2 - 2.6 * d - 0.55 * side + Vector((0, 0, 0.55))
    loc1 = loc0 + 7.0 * d''', '''    loc0 = u2 - 4.8 * d - 1.2 * side + Vector((0, 0, 1.4))
    loc1 = loc0 + 6.0 * d'''),
    # S08: the mast head: amber light, EO/IR ball, radar above, spray beyond
    ('''    cam = new_cam(M, "CAM_S08", 50, 2.8, 1.4)
    tgt = world(u, (-0.7, 0.0, 3.03))
    move(cam, f0, f1, world(u, (0.45, -1.25, 2.95)), tgt, world(u, (0.3, -1.0, 3.0)), tgt, focus=(1.7, 1.4))''',
     '''    cam = new_cam(M, "CAM_S08", 35, 2.8, 1.9)
    tgt = world(u, (-0.62, 0.0, 2.75))
    move(cam, f0, f1, world(u, (1.05, -1.0, 3.3)), tgt, world(u, (0.85, -0.8, 3.22)), tgt, focus=(2.0, 1.7))
    tame_glare(0.4)'''),
    # S11: handheld from a fixed point above the water, looking at the jacket in the beam as the break rolls through
    ('''        z = water_z(M, 8.4, 2.6, f)
        hit''', '''        hit'''),
    ('''        loc = Vector((8.4, 2.6, z + 0.55)) + jit''', '''        loc = Vector((10.8, 3.6, 1.7)) + jit'''),
    ('''    cam = new_cam(M, "CAM_S11", 24, 5.6, 4.5)''', '''    cam = new_cam(M, "CAM_S11", 28, 5.6, 7.0)'''),
    # S12: away from the moon; heli light from the coast side, top-left
    ('''    move(cam, f0, f1, (16.5, 8.5, 3.0), (4.2, -0.3, 2.62), (16.4, 8.45, 3.0), (4.2, -0.3, 2.6))''',
     '''    move(cam, f0, f1, (2.0, -14.5, 3.0), (4.4, 0.5, 2.6), (2.05, -14.4, 3.0), (4.4, 0.5, 2.55))'''),
])
print("fix_checks_01 applied")
