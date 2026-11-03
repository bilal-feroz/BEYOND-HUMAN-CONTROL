"""RB-01..03, PR-01..03: robots and props, procedural hard-surface in metres.

Design rule: saturated orange is reserved for the life jacket. Robots are white/grey/graphite with
silver retroreflective tape and conventional navigation lights.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

from . import core
from .core import (bm_box, bm_cyl, bm_sphere, bm_lathe, obj_from_bm, bevel, subsurf, empty,
                   principled, emissive, point_light, spot_light, align_z_to, setp, log)

ROT_X90 = Matrix.Rotation(math.radians(90), 4, 'X')
ROT_Y90 = Matrix.Rotation(math.radians(90), 4, 'Y')


# ---------------------------------------------------------------- palette

def _weathered(name, base, rough, coat=0.0, metal=0.0, grime=0.18, scale=6.0):
    m = principled(name, base=base, rough=rough, coat=coat, metal=metal)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 10
    nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = 0.35
    mr.inputs["From Max"].default_value = 0.7
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 1.0 - grime
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 1.0
    core.sock(mix.inputs, "A").default_value = (*base, 1)
    cc = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(mr.outputs["Result"], cc.inputs[i])
    nt.links.new(cc.outputs["Color"], core.sock(mix.inputs, "B"))
    nt.links.new(core.sock(mix.outputs, "Result"), b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    rr.inputs["To Min"].default_value = max(0.02, rough - 0.12)
    rr.inputs["To Max"].default_value = min(1.0, rough + 0.18)
    nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    return m


def palette():
    P = {}
    P["white"] = _weathered("BHC_RobotWhite", (0.56, 0.58, 0.58), 0.42, coat=0.25)
    P["graphite"] = _weathered("BHC_Graphite", (0.032, 0.034, 0.038), 0.36, coat=0.3, grime=0.1)
    P["carbon"] = principled("BHC_Carbon", (0.018, 0.018, 0.02), rough=0.28, coat=0.4)
    P["metal"] = principled("BHC_MetalDark", (0.2, 0.2, 0.21), rough=0.32, metal=1.0)
    P["retro"] = principled("BHC_Retro", (0.8, 0.8, 0.8), rough=0.2, metal=0.85)
    P["lens"] = principled("BHC_LensGlass", (0.004, 0.005, 0.007), rough=0.02, coat=1.0)
    P["collar"] = _weathered("BHC_Collar", (0.055, 0.06, 0.065), 0.55, grime=0.12, scale=3)
    P["gelcoat"] = _gelcoat()
    P["deck"] = _weathered("BHC_Deck", (0.07, 0.075, 0.08), 0.85, grime=0.2, scale=12)
    P["jacket"] = principled("BHC_Jacket", (0.95, 0.115, 0.0), rough=0.48, coat=0.45)
    P["cloth"] = principled("BHC_Clothing", (0.012, 0.014, 0.017), rough=0.45, coat=0.6)
    P["fiberglass"] = _weathered("BHC_Fiberglass", (0.46, 0.47, 0.44), 0.45, grime=0.35, scale=2.5)
    P["teal"] = _weathered("BHC_HullTeal", (0.012, 0.085, 0.075), 0.4, grime=0.3, scale=2.5)
    P["led_red"] = emissive("BHC_LED_Red", (1.0, 0.03, 0.015), 60)
    P["led_green"] = emissive("BHC_LED_Green", (0.05, 1.0, 0.25), 60)
    P["led_white"] = emissive("BHC_LED_White", (1.0, 0.96, 0.9), 80)
    P["led_amber"] = emissive("BHC_LED_Amber", (1.0, 0.5, 0.04), 60)
    P["searchlens"] = emissive("BHC_SearchLens", (1.0, 0.95, 0.88), 400)
    return P


def _gelcoat():
    """White gelcoat topsides, graphite antifouling below the boot stripe (object-space z)."""
    m = _weathered("BHC_Gelcoat", (0.6, 0.61, 0.6), 0.28, coat=0.35, grime=0.2, scale=1.5)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    src = b.inputs["Base Color"].links[0].from_socket
    tc = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    lt = nt.nodes.new("ShaderNodeMath")
    lt.operation = 'LESS_THAN'
    nt.links.new(sep.outputs["Z"], lt.inputs[0])
    lt.inputs[1].default_value = -0.08
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'RGBA'
    nt.links.new(lt.outputs[0], mix.inputs["Factor"])
    nt.links.new(src, core.sock(mix.inputs, "A"))
    core.sock(mix.inputs, "B").default_value = (0.03, 0.033, 0.038, 1)
    nt.links.new(core.sock(mix.outputs, "Result"), b.inputs["Base Color"])
    return m


# ---------------------------------------------------------------- RB-01 UAV

def build_uav(coll, name, P, variant="search"):
    """1.2 m industrial quad. variant 'search' (UAV-1, searchlight gimbal) or 'relay' (UAV-2)."""
    root = empty(name, coll, size=0.6)
    parts = {}

    bm = bmesh.new()
    bm_box(bm, (0.44, 0.30, 0.13))
    bm_box(bm, (0.10, 0.20, 0.07), loc=(-0.23, 0, -0.01))
    parts["body"] = o = obj_from_bm(f"{name}_Body", bm, coll, P["white"], root)
    bevel(o, 0.022, 3)

    bm = bmesh.new()
    bm_box(bm, (0.30, 0.22, 0.04), loc=(0.01, 0, 0.083))
    bm_box(bm, (0.14, 0.09, 0.05), loc=(-0.05, 0.06, 0.12))
    bm_box(bm, (0.14, 0.09, 0.05), loc=(-0.05, -0.06, 0.12))
    o = obj_from_bm(f"{name}_Top", bm, coll, P["graphite"], root)
    bevel(o, 0.012, 2)

    arms, motors, props, tape = bmesh.new(), bmesh.new(), [], bmesh.new()
    leds = []
    R = 0.62
    for i, deg in enumerate((45, 135, 225, 315)):
        a = math.radians(deg)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        tip = d * R
        mid = d * (0.17 + (R - 0.17) / 2)
        rot = align_z_to(d)
        bm_cyl(arms, 0.019, R - 0.17, loc=mid + Vector((0, 0, 0.0)), rot=rot, segs=16)
        bm_box(arms, (0.06, 0.06, 0.05), loc=d * 0.2)
        bm_cyl(motors, 0.043, 0.05, loc=tip + Vector((0, 0, 0.03)))
        bm_cyl(motors, 0.034, 0.016, loc=tip + Vector((0, 0, 0.063)))
        bm_cyl(motors, 0.03, 0.06, loc=tip + Vector((0, 0, -0.02)), r2=0.022)
        # retroreflective band on each arm
        bm_cyl(tape, 0.0205, 0.05, loc=d * 0.42, rot=rot, segs=16)
        # two-blade prop, pivot on the motor axis
        pb = bmesh.new()
        for side in (1, -1):
            bm_box(pb, (0.19, 0.03, 0.004), loc=(0.1 * side, 0, 0), rot=Matrix.Rotation(math.radians(12), 4, 'X'))
        bm_cyl(pb, 0.016, 0.02)
        p = obj_from_bm(f"{name}_Prop{i}", pb, coll, P["carbon"], root)
        p.location = tip + Vector((0, 0, 0.083))
        p["spin_dir"] = 1 if i % 2 == 0 else -1
        props.append(p)
        # nav lights: port (+Y) front red, starboard (-Y) front green, rear white
        led_mat = P["led_red"] if deg == 45 else P["led_green"] if deg == 315 else P["led_white"]
        led_col = (1, 0.03, 0.015) if deg == 45 else (0.05, 1, 0.25) if deg == 315 else (1, 0.95, 0.9)
        lb = bmesh.new()
        bm_sphere(lb, 0.011, loc=tip + Vector((0, 0, -0.055)), segs=12, rings=6)
        obj_from_bm(f"{name}_Nav{i}", lb, coll, led_mat, root)
        leds.append(point_light(f"{name}_NavL{i}", coll, tip + Vector((0, 0, -0.07)), led_col, 0.35, 0.01, root))
    o = obj_from_bm(f"{name}_Arms", arms, coll, P["graphite"], root)
    bevel(o, 0.006, 2)
    o = obj_from_bm(f"{name}_Motors", motors, coll, P["metal"], root)
    bevel(o, 0.004, 2)
    obj_from_bm(f"{name}_Tape", tape, coll, P["retro"], root)

    # landing gear
    lg = bmesh.new()
    for s in (1, -1):
        for xx in (0.12, -0.12):
            bm_cyl(lg, 0.009, 0.2, loc=(xx, 0.13 * s, -0.16), rot=Matrix.Rotation(math.radians(-14 * s), 4, 'X'), segs=10)
        bm_cyl(lg, 0.011, 0.42, loc=(0, 0.16 * s, -0.255), rot=ROT_Y90, segs=10)
    obj_from_bm(f"{name}_Gear", lg, coll, P["graphite"], root)

    # sensing camera under the rear
    cam = bmesh.new()
    bm_sphere(cam, 0.045, loc=(-0.12, 0, -0.105), segs=20, rings=10)
    obj_from_bm(f"{name}_CamBall", cam, coll, P["graphite"], root)
    lens = bmesh.new()
    bm_cyl(lens, 0.02, 0.012, loc=(-0.08, 0, -0.105), rot=ROT_Y90, segs=16)
    obj_from_bm(f"{name}_CamLens", lens, coll, P["lens"], root)

    out = {"root": root, "props": props, "leds": leds}
    out["status"] = _status_led(coll, root, f"{name}", (0.13, 0, 0.112), 0.012)
    dmat = _prop_disc_material()
    discs = []
    for i, p in enumerate(props):
        db = bmesh.new()
        bm_cyl(db, 0.19, 0.003, segs=40)
        d = obj_from_bm(f"{name}_PropDisc{i}", db, coll, dmat, root, smooth=False)
        d.location = p.location.copy()
        d.hide_render = True
        discs.append(d)
    out["discs"] = discs
    if variant == "search":
        gim = empty(f"{name}_Gimbal", coll, (0.14, 0, -0.1), root, size=0.1)
        y = bmesh.new()
        bm_box(y, (0.03, 0.15, 0.05), loc=(0, 0, 0.02))
        obj_from_bm(f"{name}_Yoke", y, coll, P["graphite"], gim)
        hb = bmesh.new()
        bm_cyl(hb, 0.06, 0.13, loc=(0, 0, -0.03), rot=ROT_Y90, segs=24)
        bm_cyl(hb, 0.064, 0.02, loc=(0.06, 0, -0.03), rot=ROT_Y90, segs=24)
        h = obj_from_bm(f"{name}_SearchHousing", hb, coll, P["white"], gim)
        bevel(h, 0.006, 2)
        lb = bmesh.new()
        bm_cyl(lb, 0.052, 0.006, loc=(0.072, 0, -0.03), rot=ROT_Y90, segs=24)
        obj_from_bm(f"{name}_SearchLens", lb, coll, P["searchlens"], gim)
        sp = spot_light(f"{name}_Searchlight", coll, (0.08, 0, -0.03), (1, 0, 0), 5000, angle_deg=14,
                        blend=0.45, temp=5000, radius=0.05, parent=gim)
        out.update(gimbal=gim, spot=sp)
    else:
        top = bmesh.new()
        for s in (1, -1):
            bm_cyl(top, 0.006, 0.28, loc=(-0.12, 0.07 * s, 0.25), segs=8)
        bm_cyl(top, 0.03, 0.03, loc=(0.0, 0, 0.16), segs=16)
        obj_from_bm(f"{name}_Antennas", top, coll, P["graphite"], root)
        st = bmesh.new()
        bm_sphere(st, 0.018, loc=(0.0, 0, 0.185), segs=12, rings=6)
        smat = emissive(f"BHC_Strobe_{name}", (1.0, 0.96, 0.92), 0.0)
        obj_from_bm(f"{name}_Strobe", st, coll, smat, root)
        sl = point_light(f"{name}_StrobeL", coll, (0, 0, 0.21), (1, 0.97, 0.93), 0.0, 0.02, root)
        out["strobe"] = (smat.node_tree.nodes["Emission"].inputs["Strength"], sl)
    return out


def _status_led(coll, root, name, loc, r):
    mat = emissive(f"BHC_Status_{name}", (1.0, 0.55, 0.12), 1.5)
    b = bmesh.new()
    bm_sphere(b, r, loc=loc, segs=24, rings=12)
    obj_from_bm(f"{name}_StatusLED", b, coll, mat, root)
    light = point_light(f"{name}_StatusL", coll, Vector(loc) + Vector((0, 0, 0.03)), (1.0, 0.55, 0.12), 0.05, 0.01, root)
    return (mat.node_tree.nodes["Emission"].inputs["Strength"], light)


def _prop_disc_material():
    m = core.material("BHC_PropDisc")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = (0.05, 0.05, 0.055, 1)
    gl.inputs["Roughness"].default_value = 0.35
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.2
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    setp(m, "surface_render_method", 'BLENDED')
    return m


def realtime_props(uav):
    """Real-time shots: 133 rev/s blades become motion-blurred discs."""
    for p in uav["props"]:
        p.hide_render = True
    for d in uav["discs"]:
        d.hide_render = False


def spin_props(props, rev_per_s=133.0):
    for p in props:
        d = p.get("spin_dir", 1)
        phase = (hash(p.name) % 360) * math.pi / 180
        core.key_time_linear(p, "rotation_euler[2]", lambda t, d=d, ph=phase: ph + d * 2 * math.pi * rev_per_s * t)


# ---------------------------------------------------------------- hull loft (RB-02, PR-03)

def _half_beam(t, B):
    """Planform: full beam aft, V-taper over the forward 45% to a pointed bow (RHIB-like)."""
    if t < 0.55:
        return B / 2 * (0.88 + 0.12 * math.sin(t / 0.55 * math.pi / 2))
    u = (t - 0.55) / 0.45
    return B / 2 * max(0.0, 1 - u) ** 0.85


def _hull_bm(L=7.5, B=2.6, keel=0.5, sheer0=0.55, sheer_rise=0.3, stations=44, deck=True):
    bm = bmesh.new()
    sections = []
    for si in range(stations):
        t = si / (stations - 1)
        x = -L / 2 + t * L
        b = max(_half_beam(t, B), 0.012)
        zg = sheer0 + sheer_rise * t ** 2.5
        zk = -keel * (1 - 0.95 * t ** 4)          # stem rises to a cutwater
        dr = math.radians(20 + 26 * t ** 2)
        zc = zk + 0.82 * b * math.tan(dr)
        zc = min(zc, zg - 0.08)
        half = [(0.0, zk), (0.28 * b, zk + 0.28 * b * math.tan(dr)), (0.55 * b, zk + 0.55 * b * math.tan(dr)),
                (0.82 * b, zc), (0.87 * b, zc + 0.015), (0.94 * b, zc + (zg - zc) * 0.45), (b, zg)]
        loop = [Vector((x, yy, zz)) for yy, zz in half]
        if deck:
            loop += [Vector((x, 0.95 * b, zg)), Vector((x, 0.0, zg + 0.03))]
            loop += [Vector((x, -0.95 * b, zg))]
        else:
            loop += [Vector((x, 0.0, zg + 0.02))]
        loop += [Vector((x, -yy, zz)) for yy, zz in reversed(half[1:])]
        sections.append([bm.verts.new(v) for v in loop])
    n = len(sections[0])
    for a, b2 in zip(sections[:-1], sections[1:]):
        for i in range(n):
            bm.faces.new([a[i], a[(i + 1) % n], b2[(i + 1) % n], b2[i]])
    bm.faces.new(list(reversed(sections[0])))
    bm.faces.new(sections[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def _gunwale_points(L, B, sheer0, sheer_rise, n=40, out=0.1, drop=-0.02):
    pts = []
    for side in (1, -1):
        rng = range(n) if side == 1 else range(n - 1, -1, -1)
        for i in rng:
            t = 0.03 + 0.93 * i / (n - 1)
            b = _half_beam(t, B)
            pts.append(((-L / 2 + t * L), side * (b + out * (1 - t ** 4)), sheer0 + sheer_rise * t ** 2.5 + drop, t))
    return pts


def build_usv(coll, name, P):
    """USV-1: 7.5 m uncrewed RHIB-type survey/rescue vessel, bow +X."""
    root = empty(name, coll, size=1.0)
    L, B, sheer0, rise = 7.5, 2.6, 0.55, 0.3
    hull = obj_from_bm(f"{name}_Hull", _hull_bm(L, B, 0.5, sheer0, rise), coll, P["gelcoat"], root)
    try:
        hull.data.set_sharp_from_angle(angle=math.radians(28))
    except Exception as e:
        log("sharp edges", e)

    # collar tube (grey, not orange)
    cu = bpy.data.curves.new(f"{name}_Collar", "CURVE")
    cu.dimensions = '3D'
    cu.bevel_depth = 0.2
    cu.bevel_resolution = 5
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    pts = _gunwale_points(L, B, sheer0, rise, out=0.14, drop=0.0)
    sp.points.add(len(pts) - 1)
    for p, (x, y, z, t) in zip(sp.points, pts):
        p.co = (x, y, z, 1)
        p.radius = 1.0 - 0.35 * t ** 3
    col = bpy.data.objects.new(f"{name}_Collar", cu)
    coll.objects.link(col)
    col.parent = root
    cu.materials.append(P["collar"])

    # deck furniture: console, electronics box, mast, radar, antennas
    bm = bmesh.new()
    bm_box(bm, (1.5, 1.2, 0.95), loc=(-0.4, 0, sheer0 + 0.52))
    bm_box(bm, (1.1, 1.0, 0.32), loc=(-0.55, 0, sheer0 + 1.15))
    bm_box(bm, (0.9, 1.5, 0.35), loc=(-2.9, 0, sheer0 + 0.25))
    con = obj_from_bm(f"{name}_Console", bm, coll, P["white"], root)
    bevel(con, 0.035, 3)
    bm = bmesh.new()
    mast_x = -0.7
    bm_cyl(bm, 0.055, 1.5, loc=(mast_x, 0, sheer0 + 2.05), segs=16)
    bm_box(bm, (0.36, 0.5, 0.06), loc=(mast_x, 0, sheer0 + 2.3))
    bm_cyl(bm, 0.09, 0.14, loc=(mast_x + 0.15, 0, sheer0 + 1.55), rot=ROT_Y90, segs=20)
    for s in (1, -1):
        bm_cyl(bm, 0.009, 2.4, loc=(-3.2, 0.62 * s, sheer0 + 1.6), rot=Matrix.Rotation(math.radians(-8), 4, 'Y'), segs=8)
        bm_cyl(bm, 0.06, 0.06, loc=(mast_x, 0.2 * s, sheer0 + 2.37), segs=14)
    bm_box(bm, (0.5, 0.35, 0.12), loc=(-3.6, 0, sheer0 + 0.12))
    mast = obj_from_bm(f"{name}_Mast", bm, coll, P["graphite"], root)
    bevel(mast, 0.008, 2)
    rb = bmesh.new()
    bm_box(rb, (0.14, 1.25, 0.16))
    radar = obj_from_bm(f"{name}_Radar", rb, coll, P["white"], root)
    bevel(radar, 0.02, 2)
    radar.location = (mast_x, 0, sheer0 + 2.82)
    pivot = bmesh.new()
    bm_cyl(pivot, 0.08, 0.2, loc=(mast_x, 0, sheer0 + 2.68), segs=16)
    obj_from_bm(f"{name}_RadarPivot", pivot, coll, P["graphite"], root)
    lens = bmesh.new()
    bm_cyl(lens, 0.05, 0.01, loc=(mast_x + 0.225, 0, sheer0 + 1.55), rot=ROT_Y90, segs=16)
    obj_from_bm(f"{name}_CamLens", lens, coll, P["lens"], root)
    tape = bmesh.new()
    for s in (1, -1):
        bm_box(tape, (1.2, 0.01, 0.06), loc=(-0.4, 0.605 * s, sheer0 + 0.75))
    obj_from_bm(f"{name}_Tape", tape, coll, P["retro"], root)

    # COLREG lights + amber autonomy light
    lights = {}
    for key, loc, mat, col, pw in (
        ("mast", (mast_x, 0, sheer0 + 2.95), P["led_white"], (1, 0.95, 0.88), 2.0),
        ("port", (0.36, 0.62, sheer0 + 0.75), P["led_red"], (1, 0.03, 0.015), 1.2),
        ("stbd", (0.36, -0.62, sheer0 + 0.75), P["led_green"], (0.05, 1, 0.25), 1.2),
        ("stern", (-3.65, 0, sheer0 + 0.42), P["led_white"], (1, 0.95, 0.88), 1.0),
        ("amber", (mast_x, -0.15, sheer0 + 2.5), P["led_amber"], (1, 0.5, 0.04), 1.6),   # on a bracket, clear of the mast
    ):
        lb = bmesh.new()
        bm_sphere(lb, 0.03, loc=loc, segs=24, rings=12)
        obj_from_bm(f"{name}_Light_{key}", lb, coll, mat, root)
        lights[key] = point_light(f"{name}_L_{key}", coll, Vector(loc) + Vector((0, 0, 0.04)), col, pw, 0.02, root)
    core.key_time_linear(radar, "rotation_euler[2]", lambda t: 2 * math.pi * 0.4 * t)
    amber = emissive("BHC_Status_USV_1", (1.0, 0.5, 0.06), 3.5)
    bpy.data.objects[f"{name}_Light_amber"].data.materials[0] = amber
    lights["amber"].data.energy = 1.0
    _usv_details(coll, root, P, sheer0, mast_x)
    return {"root": root, "radar": radar, "lights": lights,
            "status": (amber.node_tree.nodes["Emission"].inputs["Strength"], lights["amber"])}


def _usv_details(coll, root, P, z0, mast_x):
    """Close-up detail for S04/S08: sensor glass band, louvres, rails, sensor heads, deck hardware, ID."""
    steel = principled("BHC_Stainless", (0.62, 0.63, 0.65), rough=0.22, metal=1.0)
    g = bmesh.new()
    bm_box(g, (1.52, 1.22, 0.09), loc=(-0.4, 0, z0 + 0.88))        # sensor glass band
    bm_box(g, (1.12, 1.02, 0.05), loc=(-0.55, 0, z0 + 1.2))         # upper band
    obj_from_bm("USV_1_GlassBand", g, coll, P["lens"], root, smooth=False)
    lv = bmesh.new()
    for s in (1, -1):
        for i in range(7):
            bm_box(lv, (0.46, 0.014, 0.022), loc=(-0.62, 0.603 * s, z0 + 0.3 + i * 0.055),
                   rot=Matrix.Rotation(math.radians(25 * s), 4, 'X'))
        bm_box(lv, (0.5, 0.008, 0.42), loc=(-0.62, 0.598 * s, z0 + 0.46))  # louvre frame backing
    o = obj_from_bm("USV_1_Louvres", lv, coll, P["graphite"], root, smooth=False)
    rails = bmesh.new()
    for s in (1, -1):
        bm_cyl(rails, 0.016, 1.3, loc=(-0.4, 0.68 * s, z0 + 0.95), rot=ROT_Y90, segs=12)
        for xx in (-1.0, 0.2):
            bm_cyl(rails, 0.014, 0.16, loc=(xx, 0.64 * s, z0 + 0.9), rot=Matrix.Rotation(math.radians(90), 4, 'X'), segs=10)
        bm_cyl(rails, 0.013, 1.0, loc=(-2.9, 0.78 * s, z0 + 0.5), rot=ROT_Y90, segs=10)   # aft rail
    obj_from_bm("USV_1_Rails", rails, coll, steel, root)
    sens = bmesh.new()
    bm_cyl(sens, 0.06, 0.08, loc=(0.2, 0, z0 + 1.42), segs=24)                 # lidar puck
    bm_cyl(sens, 0.064, 0.012, loc=(0.2, 0, z0 + 1.47), segs=24)
    bm_sphere(sens, 0.1, loc=(mast_x + 0.24, 0, z0 + 2.1), segs=24, rings=12)  # EO/IR ball
    bm_box(sens, (0.1, 0.06, 0.1), loc=(mast_x + 0.12, 0, z0 + 2.2))           # ball yoke
    bm_cyl(sens, 0.012, 1.3, loc=(mast_x - 0.07, 0.05, z0 + 1.8), segs=8)      # cable conduit
    for i, yy in enumerate((-0.3, 0.0, 0.3)):
        bm_cyl(sens, 0.009, 0.26 + 0.08 * i, loc=(-0.85, yy, z0 + 1.45 + 0.04 * i), segs=8)  # stub antennas
    for s in (1, -1):
        bm_box(sens, (0.08, 0.06, 0.07), loc=(0.36, 0.62 * s, z0 + 0.7))         # nav light housings
    bm_box(sens, (0.07, 0.12, 0.05), loc=(mast_x, -0.08, z0 + 2.45))             # amber light bracket
    obj_from_bm("USV_1_Sensors", sens, coll, P["graphite"], root)
    ln = bmesh.new()
    bm_cyl(ln, 0.045, 0.01, loc=(mast_x + 0.34, 0, z0 + 2.1), rot=ROT_Y90, segs=20)
    bm_cyl(ln, 0.061, 0.03, loc=(0.2, 0, z0 + 1.4), segs=24)
    obj_from_bm("USV_1_SensorGlass", ln, coll, P["lens"], root)
    dk = bmesh.new()
    for x, y in ((2.2, 0.55), (2.2, -0.55), (-3.3, 0.7), (-3.3, -0.7)):
        bm_box(dk, (0.2, 0.05, 0.05), loc=(x, y, z0 + 0.06 + 0.3 * max(0, x / 3.75) ** 2.5))  # cleats
    bm_box(dk, (0.7, 0.6, 0.012), loc=(1.4, 0, z0 + 0.06))                               # hatch
    bm_cyl(dk, 0.035, 0.08, loc=(3.5, 0, z0 + 0.32), rot=ROT_Y90, segs=16)              # tow eye
    obj_from_bm("USV_1_DeckHardware", dk, coll, steel, root)
    ink = principled("BHC_HullInk", (0.03, 0.032, 0.035), rough=0.4)
    for s, rz in ((1, math.pi), (-1, 0.0)):
        cu = bpy.data.curves.new(f"USV_1_ID{s}", "FONT")
        cu.body = "USV-01"
        cu.size = 0.16
        cu.extrude = 0.002
        cu.align_x = 'CENTER'
        t = bpy.data.objects.new(f"USV_1_ID{s}", cu)
        coll.objects.link(t)
        t.parent = root
        t.location = (-0.4, 0.612 * s, z0 + 0.7)
        t.rotation_euler = (math.pi / 2, 0, rz)
        cu.materials.append(ink)


# ---------------------------------------------------------------- RB-03 AUV

def build_auv(coll, name, P):
    root = empty(name, coll, size=0.5)
    prof = [(-0.95, 0.0), (-0.95, 0.045), (-0.88, 0.07), (-0.62, 0.12), (0.6, 0.12), (0.74, 0.115),
            (0.84, 0.098), (0.91, 0.07), (0.95, 0.035), (0.96, 0.0)]
    bm = bmesh.new()
    bm_lathe(bm, prof, segs=40)
    body = obj_from_bm(f"{name}_Body", bm, coll, P["white"], root)
    bm = bmesh.new()
    bm_lathe(bm, [(-0.62, 0.0), (-0.62, 0.122), (-0.25, 0.122), (-0.25, 0.0)], segs=40)
    obj_from_bm(f"{name}_TailSection", bm, coll, P["graphite"], root)
    fins = bmesh.new()
    for k in range(4):
        rot = Matrix.Rotation(math.radians(45 + 90 * k), 4, 'X')
        bm_box(fins, (0.16, 0.004, 0.13), loc=rot @ Vector((-0.78, 0, 0.13)), rot=rot)
    ring = bmesh.new()
    bmesh.ops.create_cone(ring, cap_ends=False, segments=32, radius1=0.095, radius2=0.09, depth=0.09,
                          matrix=Matrix.Translation((-0.93, 0, 0)) @ ROT_Y90)
    bmesh.ops.solidify(ring, geom=ring.faces[:], thickness=0.008)
    obj_from_bm(f"{name}_Fins", fins, coll, P["graphite"], root)
    obj_from_bm(f"{name}_Shroud", ring, coll, P["graphite"], root)
    son = bmesh.new()
    for s in (1, -1):
        bm_box(son, (0.42, 0.01, 0.07), loc=(0.15, 0.121 * s, -0.02))
    obj_from_bm(f"{name}_Sonar", son, coll, P["graphite"], root)
    mastb = bmesh.new()
    bm_box(mastb, (0.12, 0.012, 0.09), loc=(-0.1, 0, 0.16))
    obj_from_bm(f"{name}_Mast", mastb, coll, P["graphite"], root)
    lb = bmesh.new()
    bm_cyl(lb, 0.03, 0.008, loc=(0.958, 0, 0), rot=ROT_Y90, segs=20)
    obj_from_bm(f"{name}_Lamp", lb, coll, P["searchlens"], root)
    sp = spot_light(f"{name}_Light", coll, (0.97, 0, 0), (1, 0, 0), 1600, angle_deg=34, blend=0.6, temp=5200, radius=0.03, parent=root)
    return {"root": root, "spot": sp, "status": _status_led(coll, root, name, (-0.1, 0, 0.212), 0.01)}


# ---------------------------------------------------------------- PR-01/02 life jacket + person

def build_person(coll, name, P):
    """Origin at the waterline. Faces +X. Static: no character animation."""
    root = empty(name, coll, size=0.4)
    # PR-02 silhouette via skin modifier
    verts = [(0, 0, 0.25), (0, 0, 0.09), (0.02, 0, -0.18), (0.02, 0, -0.6),           # head, neck, chest, pelvis
             (0.02, 0.2, -0.02), (0.12, 0.42, -0.1), (0.24, 0.52, -0.04),              # left arm, hand at surface
             (0.02, -0.2, -0.02), (0.12, -0.42, -0.1), (0.24, -0.52, -0.04),           # right arm, hand at surface
             (0.06, 0.1, -0.66), (0.2, 0.13, -1.05), (0.06, 0.15, -1.45),             # left leg
             (0.06, -0.1, -0.66), (0.14, -0.13, -1.06), (-0.02, -0.15, -1.44)]        # right leg
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 6), (1, 7), (7, 8), (8, 9),
             (3, 10), (10, 11), (11, 12), (3, 13), (13, 14), (14, 15)]
    radii = [0.11, 0.055, 0.15, 0.15, 0.06, 0.045, 0.04, 0.06, 0.045, 0.04, 0.085, 0.06, 0.045, 0.085, 0.06, 0.045]
    me = bpy.data.meshes.new(f"{name}_Body")
    me.from_pydata(verts, edges, [])
    me.validate()
    body = bpy.data.objects.new(f"{name}_Body", me)
    coll.objects.link(body)
    body.parent = root
    sk = body.modifiers.new("Skin", "SKIN")
    if not me.skin_vertices:
        me.skin_vertices.new()
    for i, r in enumerate(radii):
        sv = me.skin_vertices[0].data[i]
        sv.radius = (r, r * (1.15 if i in (2, 3) else 1.0))
    me.skin_vertices[0].data[3].use_root = True
    subsurf(body, 2)
    me.materials.append(P["cloth"])

    # PR-01 inflatable yoke jacket: U-tube around the neck, lobes down the chest
    cu = bpy.data.curves.new(f"{name}_Jacket", "CURVE")
    cu.dimensions = '3D'
    cu.bevel_depth = 0.075
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    # big inflated collar behind the head: the shape that reads as "life jacket" from behind
    pts = [((0.17, 0.1, -0.28), 1.3), ((0.13, 0.17, -0.04), 1.15), ((0.0, 0.19, 0.04), 1.05),
           ((-0.13, 0.0, 0.07), 1.15), ((0.0, -0.19, 0.04), 1.05), ((0.13, -0.17, -0.04), 1.15),
           ((0.17, -0.1, -0.28), 1.3)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, (co, r) in zip(sp.bezier_points, pts):
        bp.co = co
        bp.radius = r
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    jk = bpy.data.objects.new(f"{name}_Jacket", cu)
    coll.objects.link(jk)
    jk.parent = root
    cu.materials.append(P["jacket"])
    tape = bmesh.new()
    for s in (1, -1):
        bm_box(tape, (0.01, 0.06, 0.035), loc=(0.235, 0.1 * s, -0.25))
        bm_box(tape, (0.03, 0.05, 0.02), loc=(0.02, 0.17 * s, 0.155))
    obj_from_bm(f"{name}_JacketTape", tape, coll, P["retro"], root)
    lb = bmesh.new()
    bm_cyl(lb, 0.018, 0.035, loc=(0.06, 0.2, 0.15), segs=12)
    obj_from_bm(f"{name}_JacketLight", lb, coll, P["led_white"], root)
    light = point_light(f"{name}_JacketL", coll, (0.06, 0.2, 0.19), (1, 0.97, 0.92), 1.5, 0.015, root)
    return {"root": root, "light": light}


def build_capsized(coll, name, P):
    """6 m fishing boat, overturned. Origin at the waterline; keel up."""
    root = empty(name, coll, size=0.8)
    hull = obj_from_bm(f"{name}_Hull", _hull_bm(6.2, 2.1, 0.45, 0.6, 0.25, 36, deck=False), coll, P["fiberglass"], root)
    hull.rotation_euler = (math.pi, 0, 0)
    hull.location = (0, 0, 0.1)
    try:
        hull.data.set_sharp_from_angle(angle=math.radians(28))
    except Exception as e:
        log("sharp edges", e)
    stripe = bmesh.new()
    for s in (1, -1):
        bm_box(stripe, (5.0, 0.012, 0.09), loc=(-0.3, 0.99 * s, -0.08))
    obj_from_bm(f"{name}_Stripe", stripe, coll, P["teal"], root)
    return {"root": root}
