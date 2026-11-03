"""FX-01 / FX-03 / FX-04: spray, air mist, underwater particulates and sonar.

Every droplet is a closed-form function of real time, so frozen shots and the real-time snap come
from the same system with no simulation cache.
"""
import bpy

from . import core, env
from .core import GN, sock, setp

SOUND_IN_WATER = 1500.0


def droplet_material():
    """Water beads: screen-space refraction of what is behind them, a glint, a little forward scatter.
    (Opaque translucent droplets read as snow once they defocus near the lens.)"""
    m = core.material("BHC_Droplet")
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N("ShaderNodeOutputMaterial")
    pb = N("ShaderNodeBsdfPrincipled")
    pb.inputs["Base Color"].default_value = (1, 1, 1, 1)
    pb.inputs["Roughness"].default_value = 0.02
    pb.inputs["IOR"].default_value = 1.333
    pb.inputs["Transmission Weight"].default_value = 1.0
    pb.inputs["Specular IOR Level"].default_value = 0.8
    tl = N("ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = (0.9, 0.93, 0.93, 1)
    mix = N("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 0.12
    nt.links.new(pb.outputs[0], mix.inputs[1])
    nt.links.new(tl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    setp(m, "use_raytrace_refraction", True)
    setp(m, "thickness_mode", 'SPHERE')
    setp(m, "use_transparent_shadow", True)
    return m


def particulate_material():
    """Suspended sediment; glints as the sonar pressure front passes ('pulse' from the GN)."""
    m = core.principled("BHC_Particulate", base=(0.55, 0.62, 0.56), rough=0.85, spec=0.2)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_type = 'INSTANCER'
    at.attribute_name = "pulse"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 9.0
    nt.links.new(at.outputs["Fac"], mul.inputs[0])
    b.inputs["Emission Color"].default_value = (0.78, 0.95, 0.86, 1)
    nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    return m


def _instancer(g, points, radius, mat, subdiv=2):
    ico = g.n("GeometryNodeMeshIcoSphere")
    ico.inputs["Radius"].default_value = 1.0
    ico.inputs["Subdivisions"].default_value = subdiv
    sm = g.n("GeometryNodeSetShadeSmooth")
    g.link(ico.outputs["Mesh"], sm.inputs[0])
    sms = g.n("GeometryNodeSetMaterial")
    g.link(sm.outputs[0], sms.inputs["Geometry"])
    sms.inputs["Material"].default_value = mat
    iop = g.n("GeometryNodeInstanceOnPoints")
    g.link(points, iop.inputs["Points"])
    g.link(sms.outputs[0], iop.inputs["Instance"])
    g.link(g.xyz(radius, radius, radius), iop.inputs["Scale"])
    return iop.outputs[0]


def _cull(g, geo):
    """Remove droplets within a radius of the shot camera (defocused orbs near the lens)."""
    cobj = g.add_input("Cull Object", "NodeSocketObject")
    crad = g.add_input("Cull Radius", "NodeSocketFloat", 0.0)
    oi = g.n("GeometryNodeObjectInfo", transform_space='ORIGINAL')
    g.link(cobj, oi.inputs["Object"])
    d = g.vmath("DISTANCE", g.n("GeometryNodeInputPosition").outputs[0], oi.outputs["Location"])
    dele = g.n("GeometryNodeDeleteGeometry")
    g.link(geo, dele.inputs["Geometry"])
    g.link(g.math("LESS_THAN", d, crad), dele.inputs["Selection"])
    return dele.outputs[0]


def crest_spray_gn(mat):
    """Spray torn off the crest lip and blown forward by the shamal.

    Steady-state emission: each droplet cycles on a 1.6 s life, so the same system holds still at
    137x and streams in real time. Life is long enough that every droplet is back in the sea
    before it recycles (no visible pops). After the snap more droplets leave, faster."""
    g = GN("BHC_CrestSpray")
    count = g.add_input("Count", "NodeSocketInt", 90000)
    seed = 11
    W = env.WAVE
    k, om = env.wave_k(), env.wave_omega()
    period = 1.6
    T = g.real_time()
    brk = g.ramp(T, core.DECISION, core.DECISION + 0.25)
    idx = g.n("GeometryNodeInputIndex").outputs[0]
    y0 = g.rand(-30.0, 30.0, seed + 1, id_sock=idx)
    ey = g.math("EXPONENT", g.math("DIVIDE", g.math("MULTIPLY", g.math("MULTIPLY", y0, y0), -1.0), 2 * W["sigma_y"] ** 2))
    Fy = g.math("MULTIPLY", g.math("MULTIPLY_ADD", ey, 0.55, 0.45), env.crest_gain(g, y0))
    ph = g.rand(0.0, 1.0, seed + 2, id_sock=idx)
    age = g.math("MULTIPLY", g.math("FRACT", g.math("ADD", g.math("DIVIDE", T, period), ph)), period)
    te = g.math("SUBTRACT", T, age)
    x0 = g.math("DIVIDE", g.math("SUBTRACT", g.math("MULTIPLY", te, om), env.crest_phase(g, y0)), k)
    xe = g.math("ADD", g.math("MULTIPLY_ADD", Fy, W["lean"], x0), g.rand(-0.5, 0.9, seed + 3, id_sock=idx))
    ze = g.math("ADD", g.math("MULTIPLY", Fy, W["A"]), g.rand(-0.35, 0.25, seed + 4, id_sock=idx))
    boost = g.math("MULTIPLY_ADD", brk, 0.7, 1.0)
    vx = g.math("MULTIPLY", g.math("MULTIPLY", g.rand(5.0, 13.0, seed + 5, id_sock=idx), g.math("MULTIPLY_ADD", Fy, 0.4, 0.6)), boost)
    vy = g.rand(-1.2, 1.2, seed + 6, id_sock=idx)
    vz = g.math("MULTIPLY", g.math("MULTIPLY", g.rand(0.3, 5.0, seed + 7, id_sock=idx), Fy), boost)
    px = g.math("ADD", xe, g.math("MULTIPLY", vx, age))
    py = g.math("ADD", y0, g.math("MULTIPLY", vy, age))
    pz = g.math("SUBTRACT", g.math("ADD", ze, g.math("MULTIPLY", vz, age)),
                g.math("MULTIPLY", g.math("MULTIPLY", age, age), 0.5 * core.G))
    pts = g.n("GeometryNodePoints")
    g.link(count, pts.inputs["Count"])
    g.link(g.xyz(px, py, pz), pts.inputs["Position"])
    zz = g.sep(g.n("GeometryNodeInputPosition").outputs[0])[2]
    visible = g.math("MULTIPLY_ADD", brk, 0.55, 0.45)
    rank = g.rand(0.0, 1.0, seed + 9)
    gone = g.math("MAXIMUM", g.math("LESS_THAN", zz, -0.4), g.math("GREATER_THAN", rank, visible))
    dele = g.n("GeometryNodeDeleteGeometry")
    g.link(pts.outputs[0], dele.inputs["Geometry"])
    g.link(gone, dele.inputs["Selection"])
    culled = _cull(g, dele.outputs[0])
    r = g.rand(0.0, 1.0, seed + 8)
    radius = g.math("MULTIPLY_ADD", g.math("POWER", r, 4.0), 0.010, 0.0012)
    g.link(_instancer(g, culled, radius, mat), g.out.inputs["Geometry"])
    return g.check()


def _pulse(g, T, pos, origin, t0, width=0.25, reach=10.0):
    """Gaussian band at the sonar pressure front: radius = c * (T - t0), fading with distance."""
    r = g.math("MULTIPLY", g.math("SUBTRACT", T, t0), SOUND_IN_WATER)
    d = g.vmath("DISTANCE", pos, origin)
    q = g.math("DIVIDE", g.math("SUBTRACT", d, r), width)
    band = g.math("EXPONENT", g.math("MULTIPLY", g.math("MULTIPLY", q, q), -1.0))
    alive = g.math("MULTIPLY", g.math("GREATER_THAN", r, 0.0), g.math("MAXIMUM", g.math("SUBTRACT", 1.0, g.math("DIVIDE", r, reach)), 0.0))
    return g.math("MULTIPLY", band, alive)


def box_mist_gn(name, mat, seed=21, subdiv=2, sonar=False):
    """Droplets/particles in a box, drifting with a wind vector and wrapping inside the box."""
    g = GN(name)
    count = g.add_input("Count", "NodeSocketInt", 20000)
    bmin = g.add_input("Box Min", "NodeSocketVector", (-20.0, -20.0, 0.0))
    bmax = g.add_input("Box Max", "NodeSocketVector", (25.0, 20.0, 12.0))
    wind = g.add_input("Wind", "NodeSocketVector", (11.0, 0.0, -0.6))
    rmin = g.add_input("Radius Min", "NodeSocketFloat", 0.0008)
    rmax = g.add_input("Radius Max", "NodeSocketFloat", 0.003)
    T = g.real_time()
    idx = g.n("GeometryNodeInputIndex").outputs[0]
    p0 = g.rand(bmin, bmax, seed, kind='FLOAT_VECTOR', id_sock=idx)
    p = g.vmath("ADD", p0, g.vmath("SCALE", wind, scale=T))
    wrap = g.n("ShaderNodeVectorMath", operation='WRAP')
    g.link(p, wrap.inputs[0])
    g.link(bmax, wrap.inputs[1])
    g.link(bmin, wrap.inputs[2])
    pts = g.n("GeometryNodePoints")
    g.link(count, pts.inputs["Count"])
    g.link(wrap.outputs["Vector"], pts.inputs["Position"])
    geo = pts.outputs[0]
    if sonar:
        ping_o = g.add_input("Ping Origin", "NodeSocketVector", (0.0, 0.0, 0.0))
        ping_t = g.add_input("Ping T", "NodeSocketFloat", -1.0)
        echo_o = g.add_input("Echo Origin", "NodeSocketVector", (0.0, 0.0, 0.0))
        echo_t = g.add_input("Echo T", "NodeSocketFloat", -1.0)
        ping2_t = g.add_input("Ping2 T", "NodeSocketFloat", -1.0)
        echo2_t = g.add_input("Echo2 T", "NodeSocketFloat", -1.0)
        pos = g.n("GeometryNodeInputPosition").outputs[0]
        pulse = g.math("MAXIMUM",
                       g.math("MAXIMUM", _pulse(g, T, pos, ping_o, ping_t), _pulse(g, T, pos, echo_o, echo_t, reach=7.0)),
                       g.math("MAXIMUM", _pulse(g, T, pos, ping_o, ping2_t), _pulse(g, T, pos, echo_o, echo2_t, reach=7.0)))
        st = g.n("GeometryNodeStoreNamedAttribute", data_type='FLOAT', domain='POINT')
        g.link(geo, st.inputs["Geometry"])
        st.inputs["Name"].default_value = "pulse"
        g.link(pulse, sock(st.inputs, "Value"))
        geo = st.outputs[0]
    geo = _cull(g, geo)
    r = g.rand(0.0, 1.0, seed + 1)
    radius = g.math("ADD", rmin, g.math("MULTIPLY", g.math("POWER", r, 3.0), g.math("SUBTRACT", rmax, rmin)))
    g.link(_instancer(g, geo, radius, mat, subdiv), g.out.inputs["Geometry"])
    return g.check()


def sonar_shell_material():
    """A faint pressure front: only the grazing rim shows, like refraction in the murk."""
    m = core.material("BHC_SonarShell")
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N("ShaderNodeOutputMaterial")
    lw = N("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.3
    pw = N("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    fa = N("ShaderNodeAttribute"); fa.attribute_name = "fade"
    mul = N("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    nt.links.new(pw.outputs[0], mul.inputs[0]); nt.links.new(fa.outputs["Fac"], mul.inputs[1])
    mul2 = N("ShaderNodeMath"); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = 1.6
    nt.links.new(mul.outputs[0], mul2.inputs[0])
    em = N("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.75, 0.95, 0.86, 1)
    nt.links.new(mul2.outputs[0], em.inputs["Strength"])
    tr = N("ShaderNodeBsdfTransparent")
    add = N("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    setp(m, "surface_render_method", 'BLENDED')
    return m


def sonar_shell_gn(name, mat, reach=9.0):
    g = GN(name)
    origin = g.add_input("Origin", "NodeSocketVector", (0.0, 0.0, 0.0))
    t0 = g.add_input("T0", "NodeSocketFloat", -1.0)
    T = g.real_time()
    r = g.math("MAXIMUM", g.math("MULTIPLY", g.math("SUBTRACT", T, t0), SOUND_IN_WATER), 0.001)
    ico = g.n("GeometryNodeMeshIcoSphere")
    g.link(r, ico.inputs["Radius"])
    ico.inputs["Subdivisions"].default_value = 5
    tr = g.n("GeometryNodeTransform")
    g.link(ico.outputs["Mesh"], tr.inputs["Geometry"])
    g.link(origin, tr.inputs["Translation"])
    st = g.n("GeometryNodeStoreNamedAttribute", data_type='FLOAT', domain='POINT')
    g.link(tr.outputs[0], st.inputs["Geometry"])
    st.inputs["Name"].default_value = "fade"
    g.link(g.math("MAXIMUM", g.math("SUBTRACT", 1.0, g.math("DIVIDE", r, reach)), 0.0), sock(st.inputs, "Value"))
    # only underwater, and only while travelling
    z = g.sep(g.n("GeometryNodeInputPosition").outputs[0])[2]
    dead = g.math("MAXIMUM", g.math("LESS_THAN", r, 0.05), g.math("GREATER_THAN", r, reach))
    dele = g.n("GeometryNodeDeleteGeometry")
    g.link(st.outputs[0], dele.inputs["Geometry"])
    g.link(g.math("MAXIMUM", g.math("GREATER_THAN", z, -0.15), dead), dele.inputs["Selection"])
    sm = g.n("GeometryNodeSetMaterial")
    g.link(dele.outputs[0], sm.inputs["Geometry"])
    sm.inputs["Material"].default_value = mat
    g.link(sm.outputs[0], g.out.inputs["Geometry"])
    return g.check()


def _carrier(name, coll):
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    o.visible_shadow = False
    return o


def build_crest_spray(coll, count=90000):
    o = _carrier("BHC_CrestSpray", coll)
    core.gn_modifier(o, crest_spray_gn(droplet_material()), Count=count)
    return o


def build_mist(coll, name, count, bmin, bmax, wind=(11.0, 0.0, -0.6), rmin=0.0006, rmax=0.0018):
    o = _carrier(name, coll)
    ng = bpy.data.node_groups.get("BHC_BoxMist") or box_mist_gn("BHC_BoxMist", droplet_material())
    core.gn_modifier(o, ng, Count=count, **{"Box Min": bmin, "Box Max": bmax, "Wind": wind,
                                            "Radius Min": rmin, "Radius Max": rmax})
    return o


def build_particulates(coll, count, bmin, bmax):
    o = _carrier("BHC_Particulates", coll)
    ng = bpy.data.node_groups.get("BHC_Particles") or box_mist_gn("BHC_Particles", particulate_material(), seed=41, subdiv=1, sonar=True)
    core.gn_modifier(o, ng, Count=count, **{"Box Min": bmin, "Box Max": bmax, "Wind": (0.25, 0.08, 0.02),
                                            "Radius Min": 0.0012, "Radius Max": 0.006})
    return o


def build_sonar_shell(coll, name, origin, t0):
    o = _carrier(name, coll)
    core.gn_modifier(o, sonar_shell_gn(f"{name}_GN", sonar_shell_material()), Origin=origin, T0=t0)
    return o


def set_inputs(o, **values):
    """Set GN modifier inputs by socket name on every NODES modifier that has them."""
    for m in o.modifiers:
        if m.type != 'NODES' or not m.node_group:
            continue
        for item in m.node_group.interface.items_tree:
            if getattr(item, "in_out", None) == "INPUT" and item.name in values:
                getattr(m.properties.inputs, item.identifier).value = values[item.name]
