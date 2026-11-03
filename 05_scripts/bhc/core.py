"""BEYOND HUMAN CONTROL: shared constants, time model and bpy helpers (Blender 5.2, headless)."""
import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FPS = 24
SLOW_SECONDS = 41.0                      # film seconds that cover the frozen decision
DECISION = 0.300                         # real seconds of the decision
SLOW = SLOW_SECONDS / DECISION           # ~136.67x
SNAP_FRAME = int(round(SLOW_SECONDS * FPS)) + 1   # 985: first real-time frame
FILM_END = 50 * FPS                      # 1200
TIME_CUT_FRAME = 1057                    # S12 opens after a time cut...
TIME_CUT_T = 11.0                        # ...at 21:47:14.000
KEY_FRAMES = (1, SNAP_FRAME, TIME_CUT_FRAME - 1, TIME_CUT_FRAME, FILM_END)
OCEAN_T0 = 20.0                          # seed time of the FFT ocean
G = 9.81

SHOTS = {
    "S01": (1, 120), "S02": (121, 216), "S03": (217, 312), "S04": (313, 384),
    "S05": (385, 480), "S06": (481, 600), "S07": (601, 696), "S08": (697, 768),
    "S09": (769, 864), "S10": (865, 984), "S11": (985, 1056), "S12": (1057, 1200),
}


def real_time(frame):
    """Seconds after 21:47:03.000 for a 1-based film frame."""
    if frame >= TIME_CUT_FRAME:
        return TIME_CUT_T + (frame - TIME_CUT_FRAME) / FPS
    f = frame - 1
    snap = SNAP_FRAME - 1
    if f <= snap:
        return f / FPS / SLOW
    return DECISION + (f - snap) / FPS


def log(*a):
    print("[bhc]", *a, flush=True)


def setp(obj, attr, value):
    try:
        setattr(obj, attr, value)
        return True
    except Exception as e:  # property renamed between versions: log and continue
        log(f"skip {type(obj).__name__}.{attr}={value!r}: {e}")
        return False


def path(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ---------------------------------------------------------------- scene / collections

def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    prefs = bpy.context.preferences
    setp(prefs.edit, "keyframe_new_interpolation_type", 'LINEAR')
    return bpy.context.scene


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    parent = parent or bpy.context.scene.collection
    if c.name not in parent.children:
        parent.children.link(c)
    return c


def empty(name, coll, loc=(0, 0, 0), parent=None, size=0.3):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = size
    coll.objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def obj_from_bm(name, bm, coll, mat=None, parent=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    if mat:
        me.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def bevel(o, width=0.01, segments=3, angle=35):
    m = o.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    setp(m, "harden_normals", True)
    return m


def subsurf(o, levels=1):
    m = o.modifiers.new("Subsurf", "SUBSURF")
    m.levels = levels
    m.render_levels = levels
    return m


def look_rot(direction, up='Y', track='-Z'):
    return Vector(direction).normalized().to_track_quat(track, up).to_euler()


def align_z_to(direction):
    """Rotation matrix mapping local +Z onto direction."""
    return Vector(direction).normalized().to_track_quat('Z', 'Y').to_matrix().to_4x4()


# ---------------------------------------------------------------- bmesh primitives (metres)

def bm_box(bm, size, loc=(0, 0, 0), rot=None):
    sx, sy, sz = size
    M = Matrix.Translation(loc) @ (rot or Matrix.Identity(4)) @ Matrix.Diagonal((sx, sy, sz, 1))
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)


def bm_cyl(bm, r1, depth, loc=(0, 0, 0), rot=None, r2=None, segs=24):
    M = Matrix.Translation(loc) @ (rot or Matrix.Identity(4))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=r1, radius2=r1 if r2 is None else r2, depth=depth, matrix=M)


def bm_sphere(bm, r, loc=(0, 0, 0), segs=24, rings=12, scale=(1, 1, 1)):
    M = Matrix.Translation(loc) @ Matrix.Diagonal((*scale, 1))
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r, matrix=M)


def bm_lathe(bm, profile, segs=32, axis='X'):
    """profile: [(x, r)] from tail to nose; r == 0 closes to a point."""
    rings = []
    for x, r in profile:
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            if axis == 'X':
                ring.append(bm.verts.new((x, r * math.cos(a), r * math.sin(a))))
            if r == 0:
                break
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 or len(b) == 1:
            tip, ring = (a[0], b) if len(a) == 1 else (b[0], a)
            for i in range(segs):
                f = [tip, ring[i], ring[(i + 1) % segs]] if len(a) == 1 else [ring[i], ring[(i + 1) % segs], tip]
                bm.faces.new(f)
        else:
            for i in range(segs):
                bm.faces.new([a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]])
    for ring in (rings[0], rings[-1]):
        if len(ring) > 2:
            bm.faces.new(ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


# ---------------------------------------------------------------- materials

def material(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    return m


def principled(name, base=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, spec=0.5, coat=0.0,
               emit=None, emit_strength=0.0, transmission=0.0, ior=1.45, alpha=1.0):
    m = material(name)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    m.diffuse_color = (*base, 1)
    return m


def emissive(name, color, strength):
    m = material(name)
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m


def sock(sockets, key):
    """Socket by identifier, else first available socket with that name."""
    for s in sockets:
        if s.identifier == key and not s.is_unavailable:
            return s
    for s in sockets:
        if s.name == key and not s.is_unavailable:
            return s
    raise KeyError(key)


# ---------------------------------------------------------------- geometry-nodes helpers

class GN:
    """Small builder for geometry node trees."""

    def __init__(self, name):
        old = bpy.data.node_groups.get(name)
        if old:
            bpy.data.node_groups.remove(old)
        self.ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
        self.ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        self.ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        self.nodes = self.ng.nodes
        self.inp = self.nodes.new("NodeGroupInput")
        self.out = self.nodes.new("NodeGroupOutput")
        self.x = 0

    def n(self, idname, **props):
        nd = self.nodes.new(idname)
        self.x += 1
        nd.location = (self.x * 40 % 4000, -(self.x // 100) * 300)
        for k, v in props.items():
            setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.ng.links.new(a, b)

    def val(self, socket_or_value, target):
        if isinstance(socket_or_value, bpy.types.NodeSocket):
            self.link(socket_or_value, target)
        else:
            target.default_value = socket_or_value

    # math ---------------------------------------------------------------
    def math(self, op, a, b=None, c=None):
        nd = self.n("ShaderNodeMath", operation=op)
        self.val(a, nd.inputs[0])
        if b is not None:
            self.val(b, nd.inputs[1])
        if c is not None:
            self.val(c, nd.inputs[2])
        return nd.outputs[0]

    def vmath(self, op, a, b=None, scale=None):
        nd = self.n("ShaderNodeVectorMath", operation=op)
        self.val(a, nd.inputs[0])
        if b is not None:
            self.val(b, nd.inputs[1])
        if scale is not None:
            self.val(scale, sock(nd.inputs, "Scale"))
        return nd.outputs["Value"] if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else nd.outputs["Vector"]

    def xyz(self, x=0.0, y=0.0, z=0.0):
        nd = self.n("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            self.val(v, nd.inputs[i])
        return nd.outputs[0]

    def sep(self, v):
        nd = self.n("ShaderNodeSeparateXYZ")
        self.link(v, nd.inputs[0])
        return nd.outputs["X"], nd.outputs["Y"], nd.outputs["Z"]

    def rand(self, lo, hi, seed, kind='FLOAT', id_sock=None):
        nd = self.n("FunctionNodeRandomValue", data_type=kind)
        self.val(lo, sock(nd.inputs, "Min"))
        self.val(hi, sock(nd.inputs, "Max"))
        sock(nd.inputs, "Seed").default_value = seed
        if id_sock is not None:
            self.link(id_sock, sock(nd.inputs, "ID"))
        return sock(nd.outputs, "Value")

    def real_time(self):
        """Seconds after 21:47:03.000, from the scene frame (matches core.real_time)."""
        st = self.n("GeometryNodeInputSceneTime")
        f = self.math("SUBTRACT", st.outputs["Frame"], 1.0)
        slow = self.math("DIVIDE", self.math("MINIMUM", f, float(SNAP_FRAME - 1)), FPS * SLOW)
        real = self.math("DIVIDE", self.math("MAXIMUM", self.math("SUBTRACT", f, float(SNAP_FRAME - 1)), 0.0), float(FPS))
        t = self.math("ADD", slow, real)
        # time cut into S12
        t_cut = self.math("ADD", self.math("DIVIDE", self.math("SUBTRACT", st.outputs["Frame"], float(TIME_CUT_FRAME)), float(FPS)), TIME_CUT_T)
        cut = self.math("GREATER_THAN", st.outputs["Frame"], TIME_CUT_FRAME - 0.5)
        return self.math("ADD", t, self.math("MULTIPLY", cut, self.math("SUBTRACT", t_cut, t)))

    def ramp(self, T, t0, t1):
        """0 before t0, 1 after t1, linear between (real seconds)."""
        return self.math("MINIMUM", self.math("MAXIMUM", self.math("DIVIDE", self.math("SUBTRACT", T, t0), t1 - t0), 0.0), 1.0)

    def add_input(self, name, stype, default=None):
        s = self.ng.interface.new_socket(name=name, in_out="INPUT", socket_type=stype)
        if default is not None:
            s.default_value = default
        return self.inp.outputs[name]

    def check(self):
        bad = [l for l in self.ng.links if not l.is_valid]
        assert not bad, f"{self.ng.name}: {len(bad)} invalid links"
        return self.ng


def gn_modifier(o, ng, **inputs):
    m = o.modifiers.new(ng.name, "NODES")
    m.node_group = ng
    for name, v in inputs.items():
        item = next(i for i in ng.interface.items_tree if getattr(i, "name", None) == name and i.in_out == "INPUT")
        getattr(m.properties.inputs, item.identifier).value = v
    return m


# ---------------------------------------------------------------- animation helpers

def key_time_linear(o, data_path, fn, frames=KEY_FRAMES):
    """Key a property so it follows fn(real_time) piecewise-linearly across the film."""
    owner, prop = data_path.rsplit(".", 1) if "." in data_path else ("", data_path)
    target = o.path_resolve(owner) if owner else o
    for f in frames:
        val = fn(real_time(f))
        if prop.endswith("]"):
            name, idx = prop[:-1].split("[")
            getattr(target, name)[int(idx)] = val
            full = f"{owner}.{name}" if owner else name
            o.keyframe_insert(data_path=full, index=int(idx), frame=f)
        else:
            setattr(target, prop, val)
            o.keyframe_insert(data_path=data_path, frame=f)


# ---------------------------------------------------------------- cameras and lights

def camera(name, coll, loc, target, lens=35.0, fstop=4.0, focus=None, sensor=36.0, clip=(0.02, 3000)):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = sensor
    cd.clip_start, cd.clip_end = clip
    o = bpy.data.objects.new(name, cd)
    coll.objects.link(o)
    o.location = loc
    o.rotation_euler = look_rot(Vector(target) - Vector(loc))
    cd.dof.use_dof = fstop is not None
    if fstop:
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        cd.dof.focus_distance = focus if isinstance(focus, (int, float)) else (Vector(target) - Vector(loc)).length
        if isinstance(focus, bpy.types.Object):
            cd.dof.focus_object = focus
    return o


def point_light(name, coll, loc, color, power, radius=0.02, parent=None, volume=1.0):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color = color
    ld.energy = power
    ld.shadow_soft_size = radius
    ld.volume_factor = volume
    o = bpy.data.objects.new(name, ld)
    coll.objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def spot_light(name, coll, loc, direction, power, angle_deg=20, blend=0.3, temp=5200, radius=0.04, parent=None):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = power
    ld.spot_size = math.radians(angle_deg)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    if setp(ld, "use_temperature", True):
        setp(ld, "temperature", temp)
    o = bpy.data.objects.new(name, ld)
    coll.objects.link(o)
    o.location = loc
    o.rotation_euler = look_rot(direction)
    if parent:
        o.parent = parent
    return o


# ---------------------------------------------------------------- render settings

def render_setup(scene, res=(1920, 1080), pct=100, samples=64, quality="final", motion_blur=False):
    scene.render.engine = 'BLENDER_EEVEE'
    r = scene.render
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = pct
    r.fps = FPS
    r.film_transparent = False
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.image_settings.color_depth = '16'
    r.image_settings.compression = 90          # lossless; disk is the constraint (8.8 MB/frame at 15)
    ee = scene.eevee
    ee.taa_render_samples = samples
    setp(ee, "use_raytracing", True)
    setp(ee, "ray_tracing_method", 'SCREEN')
    rto = ee.ray_tracing_options
    setp(rto, "resolution_scale", '2' if quality != "final" else '1')
    setp(rto, "trace_max_roughness", 0.4)
    setp(rto, "use_denoise", True)
    setp(ee, "use_shadows", True)
    setp(ee, "shadow_ray_count", 1)
    setp(ee, "shadow_step_count", 6)
    setp(ee, "volumetric_tile_size", '4' if quality == "final" else '8')
    setp(ee, "volumetric_samples", 64 if quality == "final" else 32)
    setp(ee, "volumetric_sample_distribution", 0.85)
    setp(ee, "volumetric_start", 0.05)
    setp(ee, "volumetric_end", 220.0)
    setp(ee, "use_volumetric_shadows", True)
    setp(ee, "volumetric_shadow_samples", 16 if quality == "final" else 8)
    setp(ee, "volumetric_light_clamp", 0.0)
    setp(ee, "use_overscan", True)
    setp(ee, "overscan_size", 0.03)
    setp(ee, "bokeh_max_size", 60.0)
    r.use_motion_blur = motion_blur
    setp(r, "motion_blur_shutter", 0.5)
    vs = scene.view_settings
    setp(vs, "view_transform", 'AgX')
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Base Contrast"):
        if setp(vs, "look", look):
            break
    vs.exposure = 1.8
    log("color", vs.view_transform, vs.look)


def comp_setup(scene, bloom_strength=0.35, threshold=0.9):
    try:
        ng = bpy.data.node_groups.get("BHC_Comp") or bpy.data.node_groups.new("BHC_Comp", "CompositorNodeTree")
        ng.nodes.clear()
        if not any(i.in_out == "OUTPUT" for i in ng.interface.items_tree if hasattr(i, "in_out")):
            ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        for v in ("BLOOM", "Bloom"):
            try:
                gl.inputs["Type"].default_value = v
                break
            except Exception:
                pass
        for key, v in (("Highlights Threshold", threshold), ("Strength", bloom_strength), ("Size", 0.7)):
            try:
                sock(gl.inputs, key).default_value = v
            except Exception as e:
                log("glare input", key, e)
        go = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], go.inputs[0])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
    except Exception as e:
        log("compositor disabled:", e)
        scene.render.use_compositing = False


def film_frame(seconds):
    """1-based film frame at a film time in seconds."""
    return int(round(seconds * FPS)) + 1


def key_socket(sock_, values):
    """values: [(frame, value)] keyed on a node socket's default_value."""
    for f, v in values:
        sock_.default_value = v
        sock_.keyframe_insert("default_value", frame=f)


def flash(mat_sock, light, f_on, frames=3, base=(0.0, 0.0), peak=(80.0, 4.0)):
    """Instant LED pulse: emission socket and point light energy jump up for a few frames."""
    for f, (e, w) in ((f_on - 1, base), (f_on, peak), (f_on + frames, peak), (f_on + frames + 1, base)):
        if mat_sock is not None:
            mat_sock.default_value = e
            mat_sock.keyframe_insert("default_value", frame=f)
        if light is not None:
            light.data.energy = w
            light.data.keyframe_insert("energy", frame=f)


def save(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=True)
    log("saved", filepath)
