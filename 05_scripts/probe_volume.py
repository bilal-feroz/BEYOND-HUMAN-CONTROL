# Checks how EEVEE 5.2 treats a camera inside a mesh volume, and whether a world volume darkens the sky.
import bpy, bmesh, os, tempfile
from mathutils import Vector

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = sc.render.resolution_y = 48
sc.eevee.taa_render_samples = 8
sc.view_settings.view_transform = 'Standard'
print("VIEW TRANSFORM", sc.view_settings.view_transform)

w = bpy.data.worlds.new("W")
sc.world = w
if w.node_tree is None:
    w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.bl_idname == "ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.2, 0.2, 0.2, 1)
bg.inputs["Strength"].default_value = 1.0

me = bpy.data.meshes.new("box")
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=10.0); bm.to_mesh(me); bm.free()
box = bpy.data.objects.new("box", me); sc.collection.objects.link(box)
m = bpy.data.materials.new("vol")
nt = m.node_tree
for n in list(nt.nodes):
    if n.bl_idname == "ShaderNodeBsdfPrincipled":
        nt.nodes.remove(n)
outn = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")
pv = nt.nodes.new("ShaderNodeVolumePrincipled")
pv.inputs["Density"].default_value = 0.3
pv.inputs["Color"].default_value = (1, 0, 0, 1)
pv.inputs["Emission Strength"].default_value = 1.0
pv.inputs["Emission Color"].default_value = (1, 0, 0, 1)
nt.links.new(pv.outputs["Volume"], outn.inputs["Volume"])
me.materials.append(m)

cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam)
sc.camera = cam

def render_mean(tag):
    path = os.path.join(tempfile.gettempdir(), f"bhc_probe_{tag}.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path, check_existing=False)
    px = list(img.pixels)
    n = len(px) // 4
    r = sum(px[0::4]) / n; g = sum(px[1::4]) / n; b = sum(px[2::4]) / n
    print(f"PROBE {tag} mean r={r:.3f} g={g:.3f} b={b:.3f}")

for method in ("FAST", "ACCURATE"):
    m.volume_intersection_method = method
    cam.location = (0, 0, 0); cam.rotation_euler = (1.5708, 0, 0)
    render_mean(f"inside_{method}")
    cam.location = (0, -20, 0)
    render_mean(f"outside_{method}")

box.hide_render = True
cam.location = (0, 0, 0)
render_mean("sky_novol")
wv = w.node_tree.nodes.new("ShaderNodeVolumePrincipled")
wv.inputs["Density"].default_value = 0.004
wout = next(n for n in w.node_tree.nodes if n.bl_idname == "ShaderNodeOutputWorld")
w.node_tree.links.new(wv.outputs["Volume"], wout.inputs["Volume"])
render_mean("sky_worldvol")
print("RESULT probe_volume ok")
