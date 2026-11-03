"""Second check sheet: whitewater band far too wide (snow/hail look), sonar shell reads as a HUD circle,
S08 unreadable, S12 framing."""
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
    # whitewater only on the top of the lip, in broken patches
    ('''    thr = g.math("MULTIPLY_ADD", brk, -0.25, 0.62)          # lip only before the snap, more of the face after
    w = g.math("MULTIPLY", g.math("POWER", g.math("MAXIMUM", g.math("SUBTRACT", c, thr), 0.0), 1.2), dens)''',
     '''    thr = g.math("MULTIPLY_ADD", brk, -0.3, 0.84)           # the lip only before the snap, spilling after
    w = g.math("MULTIPLY", g.math("MAXIMUM", g.math("SUBTRACT", c, thr), 0.0), g.math("MULTIPLY", dens, 6.0))
    nz = g.n("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.9
    nz.inputs["Detail"].default_value = 4
    g.link(g.n("GeometryNodeInputPosition").outputs[0], nz.inputs["Vector"])
    patchy = g.math("MAXIMUM", g.math("MULTIPLY", g.math("SUBTRACT", nz.outputs["Fac"], 0.45), 4.0), 0.0)
    w = g.math("MULTIPLY", w, patchy)'''),
    # shader foam on the crest: a narrow lip line instead of a broad band
    ('''cr.inputs["From Min"].default_value = 0.45; cr.inputs["From Max"].default_value = 0.9''',
     '''cr.inputs["From Min"].default_value = 0.8; cr.inputs["From Max"].default_value = 1.0'''),
])

patch("05_scripts/bhc/layout.py", [
    # sonar: particles carry the pressure front; a geometric shell read as a HUD circle
    ('''        for nm, o, t0 in (("BHC_Ping1", nose, t1), ("BHC_Echo1", legs, te1), ("BHC_Ping2", nose, t2), ("BHC_Echo2", legs, te2)):
            fx.build_sonar_shell(C["FX"], nm, o, t0)
''', ''),
    ('''        return 7.4 - 0.07 * dt, 2.7 - 0.05 * dt, 205.0''', '''        return 9.4 - 0.06 * dt, 5.4 - 0.05 * dt, 215.0'''),
])

patch("05_scripts/bhc/fx.py", [
    # brighter pulse so the front reads on the particles alone
    ('''    mul.inputs[1].default_value = 9.0''', '''    mul.inputs[1].default_value = 22.0'''),
])

patch("05_scripts/shots/shots.py", [
    # S08: from aft of the mast, looking forward: mast head silhouetted against the beam glow
    ('''    cam = new_cam(M, "CAM_S08", 35, 2.8, 1.9)
    tgt = world(u, (-0.62, 0.0, 2.75))
    move(cam, f0, f1, world(u, (1.05, -1.0, 3.3)), tgt, world(u, (0.85, -0.8, 3.22)), tgt, focus=(2.0, 1.7))''',
     '''    cam = new_cam(M, "CAM_S08", 40, 2.8, 1.5)
    tgt0, tgt1 = world(u, (-0.55, 0.05, 2.62)), world(u, (-0.6, 0.0, 2.7))
    move(cam, f0, f1, world(u, (-2.15, -0.75, 2.95)), tgt0, world(u, (-1.9, -0.6, 2.98)), tgt1, focus=(1.7, 1.45))'''),
    # S12: from a vessel's deck height, wider: drone + beam + jacket + helicopter in one frame
    ('''    cam = new_cam(M, "CAM_S12", 50, 5.6, 14.0)
    move(cam, f0, f1, (2.0, -14.5, 3.0), (4.4, 0.5, 2.6), (2.05, -14.4, 3.0), (4.4, 0.5, 2.55))''',
     '''    cam = new_cam(M, "CAM_S12", 35, 5.6, 15.0)
    move(cam, f0, f1, (2.0, -14.5, 4.5), (4.4, 0.6, 3.4), (2.05, -14.35, 4.45), (4.4, 0.6, 3.3))'''),
])
print("fix_checks_02 applied")
