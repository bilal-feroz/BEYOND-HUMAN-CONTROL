"""The film's timeline as data (no bpy): shared by the Blender layout and the edit/sound scripts,
so lights, clicks, pings, voice and on-screen text stay in sync. Times are film seconds."""

FPS = 24
DURATION = 50.0
SNAP = 41.0            # real time resumes
BLACK = (43.5, 44.0)   # hard cut to black after the snap
FADE_OUT = 46.7        # into the end card
TITLE_IN = 47.3

# Message events -> robot whose status light pulses (and a dry click in the mix)
EVENTS = [
    (17.8, "AUV_1"),
    (22.65, "AUV_1"),
    (25.5, "UAV_2"), (25.65, "UAV_1"), (25.65, "USV_1"), (25.7, "AUV_1"),
    (27.4, "USV_1"), (27.55, "UAV_2"),
    (29.6, "UAV_2"), (29.75, "USV_1"), (29.75, "UAV_1"),
    (32.9, "USV_1"), (33.05, "UAV_2"),
    (34.6, "USV_1"), (34.75, "UAV_2"),
    (36.8, "UAV_2"), (36.95, "UAV_1"),
    (39.6, "UAV_1"), (39.75, "UAV_2"),
]
PINGS = (16.6, 21.5)            # sonar pings (echo returns ~1.1 s later on screen)
ECHO_DELAY = 1.13               # film seconds: 2 x 6.2 m at 1,500 m/s, slowed 136.7x
SWING = (37.0, 40.6)            # searchlight slides onto the jacket

VO = [
    ("V01", 1.5, "Three hundred milliseconds."),
    ("V02", 5.5, "About the time it takes you to blink."),
    ("V03", 10.0, "Four machines see the same moment."),
    ("V04", 21.0, "None of them sees all of it."),
    ("V05", 25.5, "So they tell each other what they know..."),
    ("V06", 29.5, "...and how sure they are."),
    ("V07", 32.5, "The obvious choice is the closest machine."),
    ("V08", 37.0, "The wave makes it the wrong one."),
    ("V09", 44.5, "No one could decide this fast."),
    ("V10", 47.5, "So we spend years deciding how they should."),
]

DATA_LINES = [
    (5.4, 8.8, "Arabian Gulf · 41 km offshore · wind NW 24 kn"),
    (10.8, 12.9, "UAV-1 · camera · person not visible · spray"),
    (13.4, 15.9, "USV-1 · radar · breaking crest 3.1 m · no return from person"),
    (17.85, 19.9, "AUV-1 · sonar · contact 6.2 m · bearing 041°"),
    (25.6, 27.3, "UAV-2 → all · request position reports"),
    (27.7, 28.9, "UAV-2 · relay · 3 reports received"),
    (29.8, 31.9, "fused estimate · person · confidence 0.94"),
    (32.95, 34.5, "USV-1 · bid 0.41"),
    (34.65, 35.9, "USV-1 · bid withdrawn · wave impact risk"),
    (36.9, 40.9, "UAV-1 · light and track · assigned"),
    (44.6, 46.6, "decision time · 0.300 s"),
]

TITLE = "BEYOND HUMAN CONTROL"
SUBTITLE = "Technology Innovation Institute  ·  Autonomous Robotics Research Center"
DISCLAIMER = "Dramatization inspired by ARRC's public research in perception, communication, decision-making and swarm coordination."


def timecode(t):
    """On-screen clock for film time t (None when hidden)."""
    if t < SNAP:
        ms = int(t * 300 / SNAP)
        return f"21:47:03.{ms:03d}"
    if t < BLACK[0]:
        total = 300 + int((t - SNAP) * 1000)
        return f"21:47:{3 + total // 1000:02d}.{total % 1000:03d}"
    if BLACK[1] <= t < FADE_OUT:
        total = int((t - BLACK[1]) * 1000)
        return f"21:47:{14 + total // 1000:02d}.{total % 1000:03d}"
    return None
