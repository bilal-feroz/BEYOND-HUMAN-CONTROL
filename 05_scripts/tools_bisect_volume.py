"""Full-res crops of the sky/fog region under volumetric setting variants; prints a banding metric."""
import bpy, os, sys, numpy as np
out_dir = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
ee = sc.eevee
sc.render.use_border = True
sc.render.use_crop_to_border = True
sc.render.border_min_x, sc.render.border_max_x = 0.30, 0.55
sc.render.border_min_y, sc.render.border_max_y = 0.40, 0.75
base = dict(vs=64, end=220.0, tile='4', dist=0.85, vsh=True, taa=64)
variants = [("a current", {}), ("b vsamples128", dict(vs=128)), ("c end120", dict(end=120.0)),
            ("d vs128 end120", dict(vs=128, end=120.0)), ("e volshadow off", dict(vsh=False)),
            ("f tile2", dict(tile='2')), ("g taa128", dict(taa=128)), ("h dist0.95 vs128 end120", dict(vs=128, end=120.0, dist=0.95))]
crops = []
for label, v in variants:
    c = dict(base, **v)
    ee.volumetric_samples = c["vs"]; ee.volumetric_end = c["end"]; ee.volumetric_tile_size = c["tile"]
    ee.volumetric_sample_distribution = c["dist"]; ee.use_volumetric_shadows = c["vsh"]; ee.taa_render_samples = c["taa"]
    p = os.path.join(out_dir, f"vol_{label[0]}.png")
    sc.render.filepath = p
    import time; t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    img = bpy.data.images.load(p, check_existing=False)
    w, h = img.size
    a = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, :3].mean(axis=2)
    # banding: energy of the row-to-row second derivative after removing smooth gradient
    d2 = np.abs(np.diff(a, n=2, axis=0)).mean() / max(a.mean(), 1e-6)
    d2x = np.abs(np.diff(a, n=2, axis=1)).mean() / max(a.mean(), 1e-6)
    print(f"VOL {label:28s} band_y={d2:.4f} band_x={d2x:.4f} t={dt:.1f}s")
    crops.append(a)
h, w = crops[0].shape
sheet = np.zeros((h * 2, w * 4), np.float32)
for i, a in enumerate(crops):
    r, cc = divmod(i, 4)
    sheet[r*h:(r+1)*h, cc*w:(cc+1)*w] = a
sheet = sheet / np.percentile(sheet, 99.5)
sheet = np.clip(sheet, 0, 1) ** (1 / 2.2)
im = bpy.data.images.new("vsheet", w * 4, h * 2)
rgba = np.stack([sheet[::-1]] * 3 + [np.ones_like(sheet)], axis=2)
im.pixels.foreach_set(rgba.ravel()); im.filepath_raw = os.path.join(out_dir, "vol_sheet.png"); im.file_format = 'PNG'; im.save()
print("RESULT", im.filepath_raw)
