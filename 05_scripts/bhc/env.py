"""ENV-01..03: night sky, moon, FFT ocean with a Gerstner hero wave, closed water body, air fog, crest mist."""
import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Matrix, Euler

from . import core
from .core import GN, sock, setp, log

# Hero wave (Gerstner), shared with fx.py so spray leaves the same crest.
WAVE = dict(A=1.7, L=26.0, sharp=0.82, lean=1.8, sigma_x=14.0, sigma_y=26.0)
SEABED = -22.0
MOON_DIR = Vector((-0.80, -0.35, 0.36)).normalized()
COAST_DIR = Vector((-0.50, 0.86, 0.0)).normalized()


def crest_phase(g, y):
    """Phase offset along the crest so the line wanders instead of running ruler-straight."""
    s1 = g.math("SINE", g.math("MULTIPLY_ADD", y, 0.21, 0.0))
    s2 = g.math("SINE", g.math("MULTIPLY_ADD", y, 0.53, 1.3))
    return g.math("ADD", g.math("MULTIPLY", s1, 0.35), g.math("MULTIPLY", s2, 0.18))


def crest_gain(g, y):
    return g.math("MULTIPLY_ADD", g.math("SINE", g.math("MULTIPLY_ADD", y, 0.37, 0.5)), 0.12, 0.92)


def wave_k():
    return 2 * math.pi / WAVE["L"]


def wave_omega():
    k = wave_k()
    return math.sqrt(core.G * k * math.tanh(k * -SEABED))


# ---------------------------------------------------------------- sky, moon

def build_world(scene):
    w = bpy.data.worlds.get("BHC_NightSky") or bpy.data.worlds.new("BHC_NightSky")
    scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    out = N("ShaderNodeOutputWorld")
    bg = N("ShaderNodeBackground")
    tc = N("ShaderNodeTexCoord")
    nrm = N("ShaderNodeVectorMath"); nrm.operation = 'NORMALIZE'
    L(tc.outputs["Generated"], nrm.inputs[0])
    sep = N("ShaderNodeSeparateXYZ"); L(nrm.outputs["Vector"], sep.inputs[0])

    # horizon band: 1 at the horizon, 0 by ~25 deg elevation; fades below the horizon
    band = N("ShaderNodeMapRange"); band.interpolation_type = 'SMOOTHSTEP'
    L(sep.outputs["Z"], band.inputs["Value"])
    band.inputs["From Min"].default_value = 0.42
    band.inputs["From Max"].default_value = -0.02
    below = N("ShaderNodeMapRange"); below.interpolation_type = 'SMOOTHSTEP'
    L(sep.outputs["Z"], below.inputs["Value"])
    below.inputs["From Min"].default_value = -0.25
    below.inputs["From Max"].default_value = -0.01
    bandm = N("ShaderNodeMath"); bandm.operation = 'MULTIPLY'
    L(band.outputs["Result"], bandm.inputs[0]); L(below.outputs["Result"], bandm.inputs[1])
    bandp = N("ShaderNodeMath"); bandp.operation = 'POWER'
    L(bandm.outputs[0], bandp.inputs[0]); bandp.inputs[1].default_value = 2.2

    # coast glow azimuth
    dot = N("ShaderNodeVectorMath"); dot.operation = 'DOT_PRODUCT'
    L(nrm.outputs["Vector"], dot.inputs[0]); dot.inputs[1].default_value = COAST_DIR
    az = N("ShaderNodeMapRange"); az.interpolation_type = 'SMOOTHSTEP'
    L(dot.outputs["Value"], az.inputs["Value"])
    az.inputs["From Min"].default_value = -0.3
    az.inputs["From Max"].default_value = 1.0
    az.inputs["To Min"].default_value = 0.18
    glow = N("ShaderNodeMath"); glow.operation = 'MULTIPLY'
    L(bandp.outputs[0], glow.inputs[0]); L(az.outputs["Result"], glow.inputs[1])

    # clouds modulate everything a little
    cl = N("ShaderNodeTexNoise"); cl.inputs["Scale"].default_value = 2.2; cl.inputs["Detail"].default_value = 6
    L(nrm.outputs["Vector"], cl.inputs["Vector"])
    clr = N("ShaderNodeMapRange")
    L(cl.outputs["Fac"], clr.inputs["Value"])
    clr.inputs["From Min"].default_value = 0.35; clr.inputs["From Max"].default_value = 0.7
    clr.inputs["To Min"].default_value = 0.55; clr.inputs["To Max"].default_value = 1.25

    # moon glow behind cloud
    mdot = N("ShaderNodeVectorMath"); mdot.operation = 'DOT_PRODUCT'
    L(nrm.outputs["Vector"], mdot.inputs[0]); mdot.inputs[1].default_value = MOON_DIR
    mg = N("ShaderNodeMapRange"); mg.interpolation_type = 'SMOOTHERSTEP'
    L(mdot.outputs["Value"], mg.inputs["Value"])
    mg.inputs["From Min"].default_value = 0.84; mg.inputs["From Max"].default_value = 1.0
    mgp = N("ShaderNodeMath"); mgp.operation = 'POWER'
    L(mg.outputs["Result"], mgp.inputs[0]); mgp.inputs[1].default_value = 3.0

    # colours (linear radiance)
    zen = (0.0035, 0.0042, 0.0050, 1)
    hor = (0.0220, 0.0210, 0.0200, 1)
    coast = (0.070, 0.030, 0.0090, 1)
    moon = (0.090, 0.094, 0.098, 1)
    m1 = N("ShaderNodeMix"); m1.data_type = 'RGBA'
    L(bandp.outputs[0], m1.inputs["Factor"])
    sock(m1.inputs, "A").default_value = zen; sock(m1.inputs, "B").default_value = hor
    a1 = N("ShaderNodeMix"); a1.data_type = 'RGBA'; a1.blend_type = 'ADD'
    L(glow.outputs[0], a1.inputs["Factor"]); L(sock(m1.outputs, "Result"), sock(a1.inputs, "A")); sock(a1.inputs, "B").default_value = coast
    a2 = N("ShaderNodeMix"); a2.data_type = 'RGBA'; a2.blend_type = 'ADD'
    L(mgp.outputs[0], a2.inputs["Factor"]); L(sock(a1.outputs, "Result"), sock(a2.inputs, "A")); sock(a2.inputs, "B").default_value = moon
    mul = N("ShaderNodeMix"); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
    mul.inputs["Factor"].default_value = 1.0
    L(sock(a2.outputs, "Result"), sock(mul.inputs, "A"))
    cc = N("ShaderNodeCombineColor")
    for i in range(3):
        L(clr.outputs["Result"], cc.inputs[i])
    L(cc.outputs["Color"], sock(mul.inputs, "B"))
    L(sock(mul.outputs, "Result"), bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    L(bg.outputs["Background"], out.inputs["Surface"])
    return w


def build_moon(coll):
    ld = bpy.data.lights.new("BHC_Moon", "SUN")
    ld.energy = 0.45
    ld.angle = math.radians(4.0)
    ld.color = (0.82, 0.86, 0.92)
    ld.volume_factor = 0.3
    o = bpy.data.objects.new("BHC_Moon", ld)
    coll.objects.link(o)
    o.rotation_euler = (-MOON_DIR).to_track_quat('-Z', 'Y').to_euler()
    return o


# ---------------------------------------------------------------- ocean surface + water body

def _ocean_grid(n=600, half_inner=105.0, half_outer=2500.0, center=(3.0, 0.0)):
    """Non-uniform grid: ~0.35 m spacing at the action, ~20 m at the horizon, one seamless mesh."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=1.0)
    me = bpy.data.meshes.new("BHC_Ocean")
    bm.to_mesh(me)
    bm.free()
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.attributes["position"].data.foreach_get("vector", co)
    co = co.reshape(-1, 3)
    u = co[:, :2] / np.abs(co[:, :2]).max()
    A = half_inner
    B = half_outer - half_inner
    xy = A * u + B * u ** 5
    co[:, 0] = xy[:, 0] + center[0]
    co[:, 1] = xy[:, 1] + center[1]
    co[:, 2] = 0.0
    me.attributes["position"].data.foreach_set("vector", co.ravel())
    me.update()
    me.shade_smooth()           # flat quads read as faceted rectangles at grazing angles
    return me


def _hero_wave_gn():
    g = GN("BHC_HeroWave")
    flat_c = g.add_input("Flatten Center", "NodeSocketVector", (0.0, 0.0, 0.0))
    flat_r = g.add_input("Flatten Radius", "NodeSocketFloat", 0.0)
    walls = g.add_input("Close Body", "NodeSocketBool", True)
    W = WAVE
    k = wave_k()
    om = wave_omega()
    T = g.real_time()
    pos = g.n("GeometryNodeInputPosition").outputs[0]
    x, y, z = g.sep(pos)
    # theta = k x - w T ; crest travels +X
    theta = g.math("ADD", g.math("SUBTRACT", g.math("MULTIPLY", x, k), g.math("MULTIPLY", T, om)), crest_phase(g, y))
    xc = g.math("MULTIPLY", T, om / k)
    dx = g.math("SUBTRACT", x, xc)
    ex = g.math("EXPONENT", g.math("DIVIDE", g.math("MULTIPLY", g.math("MULTIPLY", dx, dx), -1.0), 2 * W["sigma_x"] ** 2))
    ey = g.math("EXPONENT", g.math("DIVIDE", g.math("MULTIPLY", g.math("MULTIPLY", y, y), -1.0), 2 * W["sigma_y"] ** 2))
    fx = g.math("MULTIPLY_ADD", ex, 0.65, 0.35)
    fy = g.math("MULTIPLY_ADD", ey, 0.55, 0.45)
    brk = g.ramp(T, core.DECISION, core.DECISION + 0.25)          # lip pitches forward
    decay = g.ramp(T, core.DECISION, core.DECISION + 1.6)         # wave loses height breaking
    F = g.math("MULTIPLY", g.math("MULTIPLY", fx, fy), crest_gain(g, y))
    F = g.math("MULTIPLY", F, g.math("MULTIPLY_ADD", decay, -0.42, 1.0))
    lean_eff = g.math("MULTIPLY", g.math("MULTIPLY_ADD", g.math("MULTIPLY", brk, g.math("SUBTRACT", 1.0, decay)), 0.35, 1.0), W["lean"])
    cos_t = g.math("COSINE", theta)
    sin_t = g.math("SINE", theta)
    z_add = g.math("MULTIPLY", g.math("MULTIPLY", cos_t, F), W["A"])
    zn = g.math("MULTIPLY_ADD", cos_t, 0.5, 0.5)
    zn3 = g.math("POWER", zn, 3.0)
    x_gerst = g.math("MULTIPLY", g.math("MULTIPLY", sin_t, F), -W["sharp"] / k)
    x_lean = g.math("MULTIPLY", g.math("MULTIPLY", zn3, F), lean_eff)
    x_add = g.math("ADD", x_gerst, x_lean)
    # crest mask; after the snap the whitewater spreads down the face
    crest = g.math("MULTIPLY", g.math("POWER", zn, g.math("MULTIPLY_ADD", brk, -2.5, 4.0)), F)
    crest = g.math("MULTIPLY", crest, g.math("MULTIPLY_ADD", brk, 0.8, 1.0))

    sp = g.n("GeometryNodeSetPosition")
    g.link(g.inp.outputs["Geometry"], sp.inputs["Geometry"])
    g.link(g.xyz(x_add, 0.0, z_add), sp.inputs["Offset"])
    st = g.n("GeometryNodeStoreNamedAttribute", data_type='FLOAT', domain='POINT')
    g.link(sp.outputs[0], st.inputs["Geometry"])
    st.inputs["Name"].default_value = "crest"
    g.link(crest, sock(st.inputs, "Value"))

    # dome-port flatten (S06): pull z toward the centre height inside the radius
    pos2 = g.n("GeometryNodeInputPosition").outputs[0]
    x2, y2, z2 = g.sep(pos2)
    cx, cy, cz = g.sep(flat_c)
    d = g.vmath("LENGTH", g.xyz(g.math("SUBTRACT", x2, cx), g.math("SUBTRACT", y2, cy), 0.0))
    r = g.math("MAXIMUM", flat_r, 0.001)
    mr = g.n("ShaderNodeMapRange", interpolation_type='SMOOTHSTEP')
    g.link(d, mr.inputs["Value"])
    g.link(g.math("MULTIPLY", r, 0.45), mr.inputs["From Min"])
    g.link(r, mr.inputs["From Max"])
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    on = g.math("GREATER_THAN", flat_r, 0.0005)
    wgt = g.math("MULTIPLY", mr.outputs["Result"], on)
    z_new = g.math("ADD", z2, g.math("MULTIPLY", wgt, g.math("SUBTRACT", cz, z2)))
    sp2 = g.n("GeometryNodeSetPosition")
    g.link(st.outputs[0], sp2.inputs["Geometry"])
    g.link(g.xyz(x2, y2, z_new), sp2.inputs["Position"])
    # the shader drops foam inside the flattened zone (grid quads span hundreds of px there)
    st2 = g.n("GeometryNodeStoreNamedAttribute", data_type='FLOAT', domain='POINT')
    g.link(sp2.outputs[0], st2.inputs["Geometry"])
    st2.inputs["Name"].default_value = "flat_w"
    g.link(wgt, sock(st2.inputs, "Value"))
    surface = st2.outputs[0]

    # close the body: hang walls from the boundary down to the seabed, add a seabed
    en = g.n("GeometryNodeInputMeshEdgeNeighbors").outputs["Face Count"]
    boundary = g.math("COMPARE", en, 1.0, 0.1)
    ex = g.n("GeometryNodeExtrudeMesh", mode='EDGES')
    g.link(surface, ex.inputs["Mesh"])
    g.link(boundary, ex.inputs["Selection"])
    pz = g.sep(g.n("GeometryNodeInputPosition").outputs[0])[2]
    g.link(g.xyz(0.0, 0.0, g.math("SUBTRACT", SEABED, pz)), ex.inputs["Offset"])
    bed = g.n("GeometryNodeMeshGrid")
    bed.inputs["Size X"].default_value = 5000.0
    bed.inputs["Size Y"].default_value = 5000.0
    bed.inputs["Vertices X"].default_value = 2
    bed.inputs["Vertices Y"].default_value = 2
    bt = g.n("GeometryNodeTransform")
    g.link(bed.outputs["Mesh"], bt.inputs["Geometry"])
    bt.inputs["Translation"].default_value = (3.0, 0.0, SEABED)
    flip = g.n("GeometryNodeFlipFaces")
    g.link(bt.outputs[0], flip.inputs["Mesh"])
    join = g.n("GeometryNodeJoinGeometry")
    g.link(flip.outputs[0], join.inputs[0])
    g.link(ex.outputs["Mesh"], join.inputs[0])
    sw = g.n("GeometryNodeSwitch", input_type='GEOMETRY')
    g.link(walls, sock(sw.inputs, "Switch"))
    g.link(surface, sock(sw.inputs, "False"))
    g.link(join.outputs[0], sock(sw.inputs, "True"))
    g.link(sw.outputs[0], g.out.inputs["Geometry"])
    return g.check()


def water_material():
    m = core.material("BHC_Water")
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    L = nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tc = N("ShaderNodeTexCoord")
    # foam from the ocean modifier and from the hero crest
    af = N("ShaderNodeAttribute"); af.attribute_name = "foam"
    ac = N("ShaderNodeAttribute"); ac.attribute_name = "crest"
    streak_map = N("ShaderNodeMapping")
    streak_map.inputs["Scale"].default_value = (0.35, 1.6, 1.0)
    L(tc.outputs["Object"], streak_map.inputs["Vector"])
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.4; nz.inputs["Detail"].default_value = 8
    nz.inputs["Roughness"].default_value = 0.62
    L(streak_map.outputs["Vector"], nz.inputs["Vector"])
    nzr = N("ShaderNodeMapRange"); L(nz.outputs["Fac"], nzr.inputs["Value"])
    nzr.inputs["From Min"].default_value = 0.42; nzr.inputs["From Max"].default_value = 0.68
    f1 = N("ShaderNodeMath"); f1.operation = 'MULTIPLY'; f1.use_clamp = True
    L(af.outputs["Fac"], f1.inputs[0]); L(nzr.outputs["Result"], f1.inputs[1])
    cr = N("ShaderNodeMapRange"); L(ac.outputs["Fac"], cr.inputs["Value"])
    cr.inputs["From Min"].default_value = 0.45; cr.inputs["From Max"].default_value = 0.9
    f2 = N("ShaderNodeMath"); f2.operation = 'MULTIPLY'; f2.use_clamp = True
    L(cr.outputs["Result"], f2.inputs[0]); L(nzr.outputs["Result"], f2.inputs[1])
    f2b = N("ShaderNodeMath"); f2b.operation = 'MULTIPLY_ADD'; f2b.use_clamp = True
    L(cr.outputs["Result"], f2b.inputs[0]); f2b.inputs[1].default_value = 0.5; L(f2.outputs[0], f2b.inputs[2])
    foam0 = N("ShaderNodeMath"); foam0.operation = 'MAXIMUM'
    L(f1.outputs[0], foam0.inputs[0]); L(f2b.outputs[0], foam0.inputs[1])
    afw = N("ShaderNodeAttribute"); afw.attribute_name = "flat_w"
    keep = N("ShaderNodeMath"); keep.operation = 'SUBTRACT'; keep.inputs[0].default_value = 1.0
    L(afw.outputs["Fac"], keep.inputs[1])
    foam = N("ShaderNodeMath"); foam.operation = 'MULTIPLY'; foam.use_clamp = True
    L(foam0.outputs[0], foam.inputs[0]); L(keep.outputs[0], foam.inputs[1])

    bsdf = N("ShaderNodeBsdfPrincipled")
    col = N("ShaderNodeMix"); col.data_type = 'RGBA'
    L(foam.outputs[0], col.inputs["Factor"])
    sock(col.inputs, "A").default_value = (0.0035, 0.0105, 0.0105, 1)
    sock(col.inputs, "B").default_value = (0.72, 0.75, 0.74, 1)
    L(sock(col.outputs, "Result"), bsdf.inputs["Base Color"])
    rgh = N("ShaderNodeMapRange"); L(foam.outputs[0], rgh.inputs["Value"])
    rgh.inputs["To Min"].default_value = 0.045; rgh.inputs["To Max"].default_value = 0.75
    L(rgh.outputs["Result"], bsdf.inputs["Roughness"])
    bsdf.inputs["IOR"].default_value = 1.333
    # ripples
    rn = N("ShaderNodeTexNoise"); rn.inputs["Scale"].default_value = 3.0; rn.inputs["Detail"].default_value = 12
    rn.inputs["Roughness"].default_value = 0.55
    L(tc.outputs["Object"], rn.inputs["Vector"])
    bump = N("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.05
    L(rn.outputs["Fac"], bump.inputs["Height"])
    rn2 = N("ShaderNodeTexNoise"); rn2.inputs["Scale"].default_value = 14.0; rn2.inputs["Detail"].default_value = 6
    L(tc.outputs["Object"], rn2.inputs["Vector"])
    bump2 = N("ShaderNodeBump"); bump2.inputs["Strength"].default_value = 0.12; bump2.inputs["Distance"].default_value = 0.01
    L(rn2.outputs["Fac"], bump2.inputs["Height"]); L(bump.outputs["Normal"], bump2.inputs["Normal"])
    L(bump2.outputs["Normal"], bsdf.inputs["Normal"])

    # underside: Snell window / total internal reflection
    lw = N("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    tir = N("ShaderNodeMapRange"); L(lw.outputs["Facing"], tir.inputs["Value"])
    tir.inputs["From Min"].default_value = 0.30; tir.inputs["From Max"].default_value = 0.42
    tr = N("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (0.85, 0.95, 0.92, 1)
    gl = N("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.08
    gl.inputs["Color"].default_value = (0.25, 0.40, 0.36, 1)
    under = N("ShaderNodeMixShader")
    L(tir.outputs["Result"], under.inputs["Fac"]); L(tr.outputs[0], under.inputs[1]); L(gl.outputs[0], under.inputs[2])
    geo = N("ShaderNodeNewGeometry")
    side = N("ShaderNodeMixShader")
    L(geo.outputs["Backfacing"], side.inputs["Fac"])
    L(bsdf.outputs[0], side.inputs[1]); L(under.outputs[0], side.inputs[2])
    L(side.outputs[0], out.inputs["Surface"])

    # No volume on the surface itself: a volume on the wavy ocean mesh made EEVEE evaluate murk in
    # the air above it (diagonal striping, even in the sky). Underwater murk is build_underwater().
    setp(m, "use_transparent_shadow", True)
    return m


def build_underwater(coll, top_z=-0.35, density=0.18):
    """ENV-02 murk: turbid Gulf water at night, as a separate box below a flat top."""
    def dens(nt, pv):
        pv.inputs["Color"].default_value = (0.07, 0.15, 0.12, 1)
        pv.inputs["Absorption Color"].default_value = (0.22, 0.52, 0.42, 1)
        pv.inputs["Density"].default_value = density
        pv.inputs["Anisotropy"].default_value = 0.72
    m = _volume_material("BHC_Underwater", dens)
    depth = top_z - SEABED
    bm = bmesh.new()
    core.bm_box(bm, (120, 120, depth), loc=(3, 0, top_z - depth / 2))
    o = core.obj_from_bm("BHC_Underwater", bm, coll, m, smooth=False)
    o.visible_shadow = False
    return o


def build_ocean(coll, flatten=None):
    me = _ocean_grid()
    o = bpy.data.objects.new("BHC_Ocean", me)
    coll.objects.link(o)
    oc = o.modifiers.new("Ocean", "OCEAN")
    oc.geometry_mode = 'DISPLACE'
    oc.resolution = 12
    oc.viewport_resolution = 6
    oc.spatial_size = 70
    oc.size = 1.0
    oc.wave_scale = 0.9
    oc.wave_scale_min = 0.9          # shortest wavelength (m): shorter waves alias on the 0.35 m grid
    oc.choppiness = 1.3
    oc.wind_velocity = 12.0
    oc.wave_alignment = 0.45
    oc.wave_direction = 0.0
    oc.damping = 0.4
    oc.depth = -SEABED
    oc.random_seed = 7
    oc.use_normals = False
    oc.use_foam = True
    oc.foam_layer_name = "foam"
    oc.foam_coverage = 0.18
    core.key_time_linear(o, 'modifiers["Ocean"].time', lambda t: core.OCEAN_T0 + t)
    ng = _hero_wave_gn()
    kw = {}
    if flatten:
        kw = {"Flatten Center": Vector(flatten[0]), "Flatten Radius": float(flatten[1])}
    kw["Close Body"] = False
    core.gn_modifier(o, ng, **kw)
    me.materials.append(water_material())
    o.visible_shadow = False          # let the beam and moon light the water column
    return o


def water_height(ocean, x, y, frame):
    """Surface z and normal at (x, y) for a frame, from the evaluated ocean."""
    sc = bpy.context.scene
    sc.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, nrm, _ = ocean.ray_cast(Vector((x, y, 40.0)), Vector((0, 0, -1)), distance=200.0, depsgraph=dg)
    if not hit:
        return 0.0, Vector((0, 0, 1))
    return loc.z, nrm.normalized()


def float_on(ocean, ob, x, y, frame, draft=0.0, tilt=1.0, heading_deg=0.0):
    z, n = water_height(ocean, x, y, frame)
    up = Vector((0, 0, 1)).lerp(n, tilt).normalized()
    tilt_q = Vector((0, 0, 1)).rotation_difference(up)
    rot = tilt_q.to_matrix().to_4x4() @ Euler((0, 0, math.radians(heading_deg))).to_matrix().to_4x4()
    ob.matrix_world = Matrix.Translation((x, y, z - draft)) @ rot
    return z


# ---------------------------------------------------------------- air fog and crest mist

def _volume_material(name, density_fn):
    m = core.material(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    density_fn(nt, pv)
    nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    return m


def build_air_fog(coll):
    """Height fog over the sea (sea-spray haze). A mesh volume: a world volume would black out the sky."""
    def dens(nt, pv):
        N = nt.nodes.new
        L = nt.links.new
        geo = N("ShaderNodeNewGeometry")
        sep = N("ShaderNodeSeparateXYZ"); L(geo.outputs["Position"], sep.inputs[0])
        h = N("ShaderNodeMath"); h.operation = 'MAXIMUM'; L(sep.outputs["Z"], h.inputs[0]); h.inputs[1].default_value = 0.0
        e = N("ShaderNodeMath"); e.operation = 'MULTIPLY'; L(h.outputs[0], e.inputs[0]); e.inputs[1].default_value = -1 / 5.0
        ex = N("ShaderNodeMath"); ex.operation = 'EXPONENT'; L(e.outputs[0], ex.inputs[0])
        d = N("ShaderNodeMath"); d.operation = 'MULTIPLY_ADD'; L(ex.outputs[0], d.inputs[0])
        d.inputs[1].default_value = 0.007; d.inputs[2].default_value = 0.0008
        nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.035; nz.inputs["Detail"].default_value = 3
        L(geo.outputs["Position"], nz.inputs["Vector"])
        nm = N("ShaderNodeMapRange"); L(nz.outputs["Fac"], nm.inputs["Value"])
        nm.inputs["To Min"].default_value = 0.45; nm.inputs["To Max"].default_value = 1.6
        d2 = N("ShaderNodeMath"); d2.operation = 'MULTIPLY'; L(d.outputs[0], d2.inputs[0]); L(nm.outputs["Result"], d2.inputs[1])
        L(d2.outputs[0], pv.inputs["Density"])
        pv.inputs["Color"].default_value = (0.92, 0.92, 0.90, 1)
        pv.inputs["Anisotropy"].default_value = 0.62
    m = _volume_material("BHC_AirFog", dens)
    bm = bmesh.new()
    core.bm_box(bm, (900, 900, 150), loc=(3, 0, 72.5))
    o = core.obj_from_bm("BHC_AirFog", bm, coll, m, smooth=False)
    o.visible_shadow = False
    return o


def build_crest_mist(coll, crest_x=1.8, crest_z=1.7):
    """Spray mist torn off the hero crest. Density follows the same crest line as the GN wave;
    the material's 'T' value node holds real time (set per shot, keyed for real-time shots)."""
    W = WAVE
    k, om = wave_k(), wave_omega()

    def dens(nt, pv):
        N = nt.nodes.new
        L = nt.links.new

        def M(op, a, b=None):
            n = N("ShaderNodeMath"); n.operation = op
            for i, v in enumerate((a, b)):
                if v is None:
                    continue
                if isinstance(v, (int, float)):
                    n.inputs[i].default_value = v
                else:
                    L(v, n.inputs[i])
            return n.outputs[0]
        geo = N("ShaderNodeNewGeometry")
        sep = N("ShaderNodeSeparateXYZ"); L(geo.outputs["Position"], sep.inputs[0])
        X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
        tn = N("ShaderNodeValue"); tn.name = tn.label = "T"; tn.outputs[0].default_value = 0.05
        gn_ = N("ShaderNodeValue"); gn_.name = gn_.label = "Gain"; gn_.outputs[0].default_value = 1.0
        phase = M("ADD", M("MULTIPLY", M("SINE", M("MULTIPLY", Y, 0.21)), 0.35),
                  M("MULTIPLY", M("SINE", M("ADD", M("MULTIPLY", Y, 0.53), 1.3)), 0.18))
        gain = M("ADD", M("MULTIPLY", M("SINE", M("ADD", M("MULTIPLY", Y, 0.37), 0.5)), 0.12), 0.92)
        fy = M("ADD", M("MULTIPLY", M("EXPONENT", M("DIVIDE", M("MULTIPLY", M("MULTIPLY", Y, Y), -1.0), 2 * W["sigma_y"] ** 2)), 0.55), 0.45)
        F = M("MULTIPLY", fy, gain)
        xc = M("ADD", M("DIVIDE", M("SUBTRACT", M("MULTIPLY", tn.outputs[0], om), phase), k), M("MULTIPLY", F, W["lean"]))
        zc = M("MULTIPLY", F, W["A"])

        def gauss(v, c, w):
            q = M("DIVIDE", M("SUBTRACT", v, c), w)
            return M("EXPONENT", M("MULTIPLY", M("MULTIPLY", q, q), -1.0))
        gx = gauss(X, M("ADD", xc, 0.9), 1.3)
        gz = gauss(Z, M("ADD", zc, 0.5), 0.45)
        gy = M("POWER", F, 2.0)
        m2 = M("MULTIPLY", M("MULTIPLY", gx, gz), gy)

        def gauss(sock_, c, w):
            s = N("ShaderNodeMath"); s.operation = 'SUBTRACT'; L(sock_, s.inputs[0]); s.inputs[1].default_value = c
            q = N("ShaderNodeMath"); q.operation = 'DIVIDE'; L(s.outputs[0], q.inputs[0]); q.inputs[1].default_value = w
            sq = N("ShaderNodeMath"); sq.operation = 'MULTIPLY'; L(q.outputs[0], sq.inputs[0]); L(q.outputs[0], sq.inputs[1])
            ng = N("ShaderNodeMath"); ng.operation = 'MULTIPLY'; L(sq.outputs[0], ng.inputs[0]); ng.inputs[1].default_value = -1
            ex = N("ShaderNodeMath"); ex.operation = 'EXPONENT'; L(ng.outputs[0], ex.inputs[0])
            return ex.outputs[0]
        nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 8
        nz.inputs["Roughness"].default_value = 0.65
        L(geo.outputs["Position"], nz.inputs["Vector"])
        nm = N("ShaderNodeMapRange"); L(nz.outputs["Fac"], nm.inputs["Value"])
        nm.inputs["From Min"].default_value = 0.4; nm.inputs["From Max"].default_value = 0.75
        m3 = N("ShaderNodeMath"); m3.operation = 'MULTIPLY'; L(m2, m3.inputs[0]); L(nm.outputs["Result"], m3.inputs[1])
        m4 = N("ShaderNodeMath"); m4.operation = 'MULTIPLY'; L(m3.outputs[0], m4.inputs[0]); L(gn_.outputs[0], m4.inputs[1])
        L(m4.outputs[0], pv.inputs["Density"])
        pv.inputs["Color"].default_value = (0.95, 0.96, 0.95, 1)
        pv.inputs["Anisotropy"].default_value = 0.5
    m = _volume_material("BHC_CrestMist", dens)
    bm = bmesh.new()
    core.bm_box(bm, (16, 90, 9), loc=(crest_x + 1.5, 0, 1.5))   # bottom below the sea: no visible box edge
    o = core.obj_from_bm("BHC_CrestMist", bm, coll, m, smooth=False)
    o.visible_shadow = False
    return o


# ---------------------------------------------------------------- whitewater (look pass 2)

def foam_material():
    m = core.material("BHC_Foam")
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.78, 0.80, 0.80, 1)
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Subsurface Weight"].default_value = 0.35
    b.inputs["Subsurface Radius"].default_value = (0.08, 0.1, 0.1)
    b.inputs["Specular IOR Level"].default_value = 0.6
    return m


def _whitewater_gn(ocean, mat):
    """Foam clumps on the lip (and down the face after the snap), from the ocean's 'crest' mask."""
    g = GN("BHC_Whitewater")
    dens = g.add_input("Density", "NodeSocketFloat", 260.0)
    oi = g.n("GeometryNodeObjectInfo", transform_space='RELATIVE')
    oi.inputs["Object"].default_value = ocean
    na = g.n("GeometryNodeInputNamedAttribute", data_type='FLOAT')
    na.inputs["Name"].default_value = "crest"
    c = na.outputs["Attribute"]
    w = g.math("MULTIPLY", g.math("POWER", g.math("MAXIMUM", g.math("SUBTRACT", c, 0.35), 0.0), 1.6), dens)
    dp = g.n("GeometryNodeDistributePointsOnFaces", distribute_method='RANDOM')
    g.link(oi.outputs["Geometry"], dp.inputs["Mesh"])
    g.link(w, dp.inputs["Density"])
    sock(dp.inputs, "Seed").default_value = 5
    # lift each clump slightly off the surface along the normal
    sp = g.n("GeometryNodeSetPosition")
    g.link(dp.outputs["Points"], sp.inputs["Geometry"])
    g.link(g.vmath("SCALE", dp.outputs["Normal"], scale=g.rand(0.0, 0.05, 3)), sp.inputs["Offset"])
    ico = g.n("GeometryNodeMeshIcoSphere")
    ico.inputs["Radius"].default_value = 1.0
    ico.inputs["Subdivisions"].default_value = 1
    smm = g.n("GeometryNodeSetMaterial")
    g.link(ico.outputs["Mesh"], smm.inputs["Geometry"])
    smm.inputs["Material"].default_value = mat
    iop = g.n("GeometryNodeInstanceOnPoints")
    g.link(sp.outputs[0], iop.inputs["Points"])
    g.link(smm.outputs[0], iop.inputs["Instance"])
    g.link(dp.outputs["Rotation"], iop.inputs["Rotation"])
    s = g.rand(0.015, 0.075, 4)
    g.link(g.xyz(s, s, g.math("MULTIPLY", s, 0.45)), iop.inputs["Scale"])
    g.link(iop.outputs[0], g.out.inputs["Geometry"])
    return g.check()


def build_whitewater(coll, ocean, density=260.0):
    me = bpy.data.meshes.new("BHC_Whitewater")
    o = bpy.data.objects.new("BHC_Whitewater", me)
    coll.objects.link(o)
    core.gn_modifier(o, _whitewater_gn(ocean, foam_material()), Density=density)
    return o
