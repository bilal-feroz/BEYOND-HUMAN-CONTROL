"""Render one frame under several setting toggles and tile them into a labelled contact sheet."""
import bpy, os, sys, numpy as np
out_dir = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
sc.render.resolution_percentage = 25
ee = sc.eevee
base = dict(taa=16, rt=True, rts='2', tile='8', vshadow=True, fog=True, mist=True)
variants = [
    ("A base preview", {}),
    ("B 64 samples", dict(taa=64)),
    ("C raytrace off", dict(rt=False)),
    ("D rt full res", dict(rts='1')),
    ("E vol shadows off", dict(vshadow=False)),
    ("F tile 4 + 64smp", dict(tile='4', taa=64)),
    ("G fog hidden", dict(fog=False)),
    ("H fog+mist hidden", dict(fog=False, mist=False)),
]
tiles = []
for label, v in variants:
    c = dict(base, **v)
    ee.taa_render_samples = c["taa"]
    ee.use_raytracing = c["rt"]
    ee.ray_tracing_options.resolution_scale = c["rts"]
    ee.volumetric_tile_size = c["tile"]
    ee.use_volumetric_shadows = c["vshadow"]
    for n in ("BHC_AirFog",):
        bpy.data.objects[n].hide_render = not c["fog"]
    for n in ("BHC_CrestMist",):
        bpy.data.objects[n].hide_render = not c["mist"]
    p = os.path.join(out_dir, f"bisect_{label[0]}.png")
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(p, check_existing=False)
    w, h = img.size
    a = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, :3]
    tiles.append((label, a))
    print("VARIANT", label, "mean", float(a.mean()))
h, w = tiles[0][1].shape[:2]
sheet = np.zeros((h * 2, w * 4, 3), np.float32)
for i, (label, a) in enumerate(tiles):
    r, cidx = divmod(i, 4)
    sheet[r * h:(r + 1) * h, cidx * w:(cidx + 1) * w] = a
im = bpy.data.images.new("sheet", w * 4, h * 2)
rgba = np.concatenate([sheet[::-1], np.ones((h * 2, w * 4, 1), np.float32)], axis=2)
im.pixels.foreach_set(rgba.ravel())
im.filepath_raw = os.path.join(out_dir, "bisect_sheet.png")
im.file_format = 'PNG'
im.save()
print("RESULT sheet", im.filepath_raw)
