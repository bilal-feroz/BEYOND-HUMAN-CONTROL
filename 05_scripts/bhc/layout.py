"""Master layout and story choreography (production document, sections 3, 5 and 6).

Every shot calls build_master(); shot scripts only add a camera, a frame range and render settings.
The same timeline drives every shot: message events (status LEDs), sonar pings, the searchlight
decision, and, in real time, the break, the withdrawal and the rescue.
"""
import math

import bpy
from mathutils import Vector, Matrix

from . import core, env, fx, assets

POS = {
    "person": (4.2, 0.0),
    "usv": (-6.0, -5.0),
    "uav1": (3.0, 2.0, 9.0),
    "uav1_rescue": (4.6, 1.0, 7.6),   # S12: repositioned overhead, holding the jacket in light
    "uav2": (-10.0, 12.0, 35.0),
    "auv": (0.5, -3.0, -4.8),         # 6.2 m from the person, below the crest
    "capsized": (8.5, -4.0),
}
SEARCH_OFFSET = Vector((1.0, 1.3, 0.0))   # beam edge only grazes the person until S10
from .story import EVENTS, PINGS, SWING  # noqa: E402  (shared with the edit scripts)


def aim(obj, target, axis='X', up='Z'):
    bpy.context.view_layer.update()
    loc = obj.matrix_world.to_translation()
    q = (Vector(target) - loc).to_track_quat(axis, up)
    obj.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()


def heading_to(src, dst):
    return math.degrees(math.atan2(dst[1] - src[1], dst[0] - src[0]))


def _smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _hit(ocean, dg, x, y):
    hit, loc, nrm, _ = ocean.ray_cast(Vector((x, y, 40.0)), Vector((0, 0, -1)), distance=200.0, depsgraph=dg)
    return (loc.z, nrm.normalized()) if hit else (0.0, Vector((0, 0, 1)))


def _place(ob, x, y, z, n, tilt, heading_deg, draft, frame=None):
    up = Vector((0, 0, 1)).lerp(n, tilt).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(up).to_matrix().to_4x4() @ Matrix.Rotation(math.radians(heading_deg), 4, 'Z')
    prev = ob.rotation_euler.copy()
    ob.matrix_world = Matrix.Translation((x, y, z - draft)) @ rot
    ob.rotation_euler = ob.matrix_world.to_euler('XYZ', prev)
    if frame is not None:
        ob.keyframe_insert("location", frame=frame)
        ob.keyframe_insert("rotation_euler", frame=frame)


def _key_gimbal(gim, target, frame):
    gim.rotation_mode = 'QUATERNION'
    aim(gim, target)
    gim.keyframe_insert("rotation_quaternion", frame=frame)


def _usv_path(T):
    """S11: withdraws, turning away to starboard. S12: holds station down-drift of the person."""
    if T >= core.TIME_CUT_T:
        dt = T - core.TIME_CUT_T
        return 11.6 - 0.08 * dt, 7.2 - 0.06 * dt, 220.0
    x, y = POS["usv"]
    h = 18.0
    t = core.DECISION
    while t < T - 1e-6:
        dt = min(0.02, T - t)
        h = 18.0 - 68.0 * _smooth((t - core.DECISION) / 1.5)
        v = 3.5 * _smooth((t - core.DECISION) / 0.3)
        x += v * dt * math.cos(math.radians(h))
        y += v * dt * math.sin(math.radians(h))
        t += dt
    return x, y, h


def _gust(T, seed):
    return Vector((0.05 * math.sin(2.1 * T + seed) + 0.03 * math.sin(5.3 * T + 2 * seed),
                   0.05 * math.sin(1.7 * T + 3 * seed) + 0.03 * math.sin(4.1 * T + seed),
                   0.04 * math.sin(2.9 * T + 5 * seed)))


def build_heli(coll, f0, f1, target):
    """FX-06: a rescue helicopter's searchlight approaching through the haze (S12)."""
    root = core.empty("Heli", coll, (0, 0, 0), size=2.0)
    a, b = Vector((-30.0, 170.0, 18.0)), Vector((-14.0, 100.0, 15.0))
    for f, p in ((f0, a), (f1, b)):
        root.location = p
        root.keyframe_insert("location", frame=f)
    # at 120-180 m at night only its lights and beam read; no body
    spot = core.spot_light("Heli_Searchlight", coll, (0, 0, -1.2), (1, 0, -0.3), 450000, angle_deg=6,
                           blend=0.35, temp=5600, radius=0.25, parent=root)
    spot.rotation_mode = 'QUATERNION'
    for f in range(f0, f1 + 1, 6):
        bpy.context.scene.frame_set(f)
        T = core.real_time(f)
        sweep = Vector((6 * math.sin(0.7 * T), 5 * math.cos(0.5 * T), 0.0))
        aim(spot, Vector(target) + sweep)
        spot.keyframe_insert("rotation_quaternion", frame=f)
    core.point_light("Heli_NavRed", coll, (0, 1.1, 0), (1, 0.03, 0.02), 40, 0.1, root)
    core.point_light("Heli_NavGreen", coll, (0, -1.1, 0), (0.05, 1, 0.25), 40, 0.1, root)
    strobe = core.point_light("Heli_Strobe", coll, (-2.6, 0, 0.4), (1, 0.97, 0.93), 0.0, 0.1, root)
    t = core.real_time(f0)
    f = f0
    while f <= f1:
        core.flash(None, strobe, f, frames=2, base=(0, 0), peak=(0, 900))
        f += int(1.2 * core.FPS)
    return root


def cull_near(M, cam, radius):
    """Drop spray/mist droplets within `radius` of the camera (defocused orbs read as snow)."""
    for name in ("BHC_CrestSpray", "BHC_AirMist", "BHC_LocalMist"):
        o = bpy.data.objects.get(name)
        if o:
            fx.set_inputs(o, **{"Cull Object": cam, "Cull Radius": radius})


def build_master(frame, underwater=False, flatten=None, spray_count=90000, air_mist=25000,
                 local_mist=None, realtime_range=None, heli=False, whitewater=True):
    sc = core.reset_scene()
    C = {k: core.collection(f"BHC_{k}") for k in ("ENV", "FX", "ROBOTS", "PROPS", "LIGHTS", "CAMS")}
    env.build_world(sc)
    env.build_moon(C["LIGHTS"])
    ocean = env.build_ocean(C["ENV"])
    zf = None
    if flatten:
        (fx_, fy_), radius = flatten
        zf, _ = env.water_height(ocean, fx_, fy_, frame)
        fx.set_inputs(ocean, **{"Flatten Center": Vector((fx_, fy_, zf)), "Flatten Radius": radius})

    # ---- robots and props
    P = assets.palette()
    uav1 = assets.build_uav(C["ROBOTS"], "UAV_1", P, "search")
    uav2 = assets.build_uav(C["ROBOTS"], "UAV_2", P, "relay")
    assets.spin_props(uav1["props"] + uav2["props"])
    usv = assets.build_usv(C["ROBOTS"], "USV_1", P)
    auv = assets.build_auv(C["ROBOTS"], "AUV_1", P)
    person = assets.build_person(C["PROPS"], "Person", P)
    cap = assets.build_capsized(C["PROPS"], "Capsized", P)
    px, py = POS["person"]
    uav2["root"].location = POS["uav2"]
    uav2["root"].rotation_euler = (0, 0, math.radians(heading_to(POS["uav2"], (px, py))))
    auv["root"].location = POS["auv"]

    if realtime_range is None:
        # frozen time: bodies sit where the water holds them at this shot's frame
        sc.frame_set(frame)
        dg = bpy.context.evaluated_depsgraph_get()
        pz, n = _hit(ocean, dg, px, py)
        _place(person["root"], px, py, pz, n, 0.5, 120, -0.1)
        z, n = _hit(ocean, dg, *POS["usv"])
        _place(usv["root"], *POS["usv"], z, n, 0.85, 18, 0.12)
        z, n = _hit(ocean, dg, *POS["capsized"])
        _place(cap["root"], *POS["capsized"], z, n, 0.6, 35, 0.0)
        uav1["root"].location = POS["uav1"]
        uav1["root"].rotation_euler = (0, 0, math.radians(heading_to(POS["uav1"], (px, py))))
        # the searchlight decision: offset until SWING, eased slide onto the jacket, then held
        on = Vector((px, py, pz + 0.1))
        off = on + SEARCH_OFFSET
        s0, s1 = core.film_frame(SWING[0]), core.film_frame(SWING[1])
        _key_gimbal(uav1["gimbal"], off, 1)
        for f in range(s0, s1 + 1, 2):
            _key_gimbal(uav1["gimbal"], off.lerp(on, _smooth((f - s0) / (s1 - s0))), f)
        _key_gimbal(uav1["gimbal"], on, core.SNAP_FRAME - 1)
        aim(auv["root"], (px, py, pz - 0.9))
    else:
        # real time: every frame, bodies ride the passing wave; the drone tracks the jacket
        f0, f1 = realtime_range
        assets.realtime_props(uav1)
        assets.realtime_props(uav2)
        aim(auv["root"], (px, py, -0.9))
        pz = 0.0
        for f in range(f0, f1 + 1):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            T = core.real_time(f)
            pz, n = _hit(ocean, dg, px, py)
            _place(person["root"], px, py, pz, n, 0.6, 120 + 6 * math.sin(0.4 * T), -0.1, f)
            ux, uy, uh = _usv_path(T)
            z, n = _hit(ocean, dg, ux, uy)
            _place(usv["root"], ux, uy, z, n, 0.85, uh, 0.12, f)
            z, n = _hit(ocean, dg, *POS["capsized"])
            _place(cap["root"], *POS["capsized"], z, n, 0.6, 35, 0.0, f)
            base = Vector(POS["uav1_rescue"] if T >= core.TIME_CUT_T else POS["uav1"])
            r = uav1["root"]
            r.location = base + _gust(T, 1.3)
            r.rotation_euler = (0.03 * math.sin(2.3 * T), 0.03 * math.sin(1.9 * T + 1), math.radians(heading_to(base, (px, py))))
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
            _key_gimbal(uav1["gimbal"], (px, py, pz + 0.1), f)
        sc.frame_set(frame)

    # ---- message events: status lights pulse (radio itself is invisible)
    robots = {"UAV_1": uav1["status"], "UAV_2": uav2["strobe"], "USV_1": usv["status"], "AUV_1": auv["status"]}
    for t, name in EVENTS:
        sock_, light = robots[name]
        if name == "UAV_2":
            core.flash(sock_, light, core.film_frame(t), frames=2, base=(0.0, 0.0), peak=(900.0, 40.0))
        else:
            idle = 3.5 if name == "USV_1" else 1.5
            core.flash(sock_, light, core.film_frame(t), frames=3, base=(idle, 0.05), peak=(60.0, 2.5))

    # ---- atmosphere and water FX (built after the floats so sampling above stays fast)
    env.build_air_fog(C["ENV"])
    mist = env.build_crest_mist(C["FX"])
    nodes = mist.active_material.node_tree.nodes
    core.key_socket(nodes["T"].outputs[0], [(f, core.real_time(f)) for f in core.KEY_FRAMES])
    core.key_socket(nodes["Gain"].outputs[0], [(1, 1.0), (core.SNAP_FRAME, 1.0), (core.SNAP_FRAME + 6, 3.5),
                                               (core.TIME_CUT_FRAME - 1, 2.0), (core.TIME_CUT_FRAME, 0.0)])
    fx.build_crest_spray(C["FX"], spray_count)
    if whitewater:
        env.build_whitewater(C["FX"], ocean)
    if air_mist:
        fx.build_mist(C["FX"], "BHC_AirMist", air_mist, (-15.0, -15.0, -0.5), (22.0, 15.0, 12.0))
    if local_mist:
        n_, bmin, bmax, rmin, rmax = local_mist
        fx.build_mist(C["FX"], "BHC_LocalMist", n_, bmin, bmax, rmin=rmin, rmax=rmax)
    if underwater:
        top = (zf - 0.01) if flatten else -0.35
        env.build_underwater(C["ENV"], top_z=top)
        parts = fx.build_particulates(C["FX"], 70000, (-4.0, -10.0, -12.0), (16.0, 10.0, top - 0.02))
        bpy.context.view_layer.update()
        nose = auv["root"].matrix_world @ Vector((0.96, 0, 0))
        legs = person["root"].matrix_world @ Vector((0.1, 0, -1.0))
        d = (legs - nose).length
        t1, t2 = (core.real_time(core.film_frame(s)) for s in PINGS)
        te1, te2 = t1 + d / fx.SOUND_IN_WATER, t2 + d / fx.SOUND_IN_WATER
        fx.set_inputs(parts, **{"Ping Origin": nose, "Ping T": t1, "Echo Origin": legs, "Echo T": te1,
                                "Ping2 T": t2, "Echo2 T": te2})
    if heli and realtime_range:
        build_heli(C["LIGHTS"], realtime_range[0], realtime_range[1], (px, py, 0.0))
    bpy.context.view_layer.update()
    sc.frame_set(frame)
    return {"scene": sc, "C": C, "ocean": ocean, "uav1": uav1, "uav2": uav2, "usv": usv, "auv": auv,
            "person": person, "capsized": cap, "person_z": pz}
