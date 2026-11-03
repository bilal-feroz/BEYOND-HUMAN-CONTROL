"""Campaign deliverables built from the film's renders and master (Blender's Python: numpy).

  PY="C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe"
  $PY 05_scripts/edit/campaign.py teaser|social|posters|linkedin|explainer

Same typography system as the film: Consolas for machine text, Bahnschrift for titles, orange only for
the person, amber for machine messages, no HUD boxes.
"""
import json
import math
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "05_scripts"))
from bhc import story as S  # noqa: E402

WORK = os.path.join(ROOT, "09_edit", "work")
DELIV = os.path.join(ROOT, "10_deliverables")
MASTER = os.path.join(DELIV, "main_16x9", "BHC_main_16x9_v001.mp4")
MIX = os.path.join(ROOT, "08_audio", "mix", "BHC_mix_v001.wav")
WHITE, AMBER, ORANGE = "&HF2F2F2&", "&H1F8CFF&", "&H005FFA&"


def run(cmd, cwd=WORK):
    os.makedirs(cwd, exist_ok=True)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit(f"ffmpeg failed: {' '.join(cmd[:6])}...")


def at(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ass_header(w, h, styles):
    base = ("[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
    return base.format(w=w, h=h) + "".join(f"Style: {s}\n" for s in styles) + \
        "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"


def ev(t0, t1, style, text, layer=0):
    return f"Dialogue: {layer},{at(t0)},{at(t1)},{style},,0,0,0,,{text}\n"


def circle_path(r, n=48, cx=0.0, cy=0.0, reverse=False):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    if reverse:
        pts = pts[::-1]
    return "m {:.1f} {:.1f} ".format(*pts[0]) + "l " + " ".join(f"{x:.1f} {y:.1f}" for x, y in pts[1:])


def ring(x, y, r, color, t0, t1, w=2.0, alpha="&H30&"):
    shape = circle_path(r) + " " + circle_path(r - w, reverse=True)
    return ev(t0, t1, "DRAW", f"{{\\an7\\pos({x:.0f},{y:.0f})\\1c{color}\\1a{alpha}\\fad(250,300)\\p1}}{shape}{{\\p0}}", 2)


def line(x1, y1, x2, y2, color, t0, t1, w=1.6, dash=False, draw=0.5, alpha="&H40&"):
    """A thin line drawn on from (x1,y1) over `draw` seconds (animated clip)."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    segs = []
    n = int(L // 14) if dash else 1
    for i in range(n):
        a, b = (i / n, (i + 0.55) / n) if dash else (0.0, 1.0)
        ax, ay, bx, by = x1 + dx * a, y1 + dy * a, x1 + dx * b, y1 + dy * b
        segs.append(f"m {ax + nx:.1f} {ay + ny:.1f} l {bx + nx:.1f} {by + ny:.1f} {bx - nx:.1f} {by - ny:.1f} {ax - nx:.1f} {ay - ny:.1f}")
    xmin, xmax = sorted((x1, x2))
    ymin, ymax = sorted((y1, y2))
    c0 = f"\\clip({x1 - 2:.0f},{y1 - 2:.0f},{x1 + 2:.0f},{y1 + 2:.0f})"
    c1 = f"\\clip({xmin - 4:.0f},{ymin - 4:.0f},{xmax + 4:.0f},{ymax + 4:.0f})"
    ms = int(draw * 1000)
    return ev(t0, t1, "DRAW", f"{{\\an7\\pos(0,0)\\1c{color}\\1a{alpha}{c0}\\t(0,{ms},{c1})\\fad(0,300)\\p1}}{' '.join(segs)}{{\\p0}}", 1)


def label(x, y, text, t0, t1, style="LBL", color=WHITE, an=7):
    return ev(t0, t1, style, f"{{\\an{an}\\pos({x:.0f},{y:.0f})\\1c{color}\\fad(250,300)}}{text}", 3)


def write(path, text):
    with open(path, "w", encoding="utf-8-sig") as fh:
        fh.write(text)


def wav_write(path, x, sr=48000):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.stack([x, x]).T * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- explainer

def explainer():
    """25 s: the four research capabilities, drawn over the overhead plate (S07) where they happen."""
    P = json.load(open(os.path.join(WORK, "S07_f0650_points.json")))
    p = {k: (v["x"], v["y"]) for k, v in P.items()}
    plate = os.path.join(ROOT, "06_renders", "finals", "S07", "S07_0650.png")
    if not os.path.exists(plate):
        plate = os.path.join(ROOT, "06_renders", "previews", "S07", "S07_0650.png")
    styles = [
        "H1,Bahnschrift,34,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,7,96,96,84,1",
        "H2,Bahnschrift,22,&H40F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,96,96,132,1",
        "LBL,Consolas,22,&H10F2F2F2,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2,7,0,0,0,1",
        "PANEL,Consolas,24,&H10F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        "DRAW,Consolas,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        "TITLE,Bahnschrift,60,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,14,0,1,0,0,5,0,0,0,1",
        "SUB,Bahnschrift,24,&H40F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1",
        "DISC,Bahnschrift,16,&H80F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,2,0,0,60,1",
    ]
    e = []
    # 0-3 title
    e.append(ev(0.3, 2.9, "TITLE", "{\\fad(600,400)\\pos(960,505)}300 MILLISECONDS"))
    e.append(ev(0.8, 2.9, "SUB", "{\\fad(600,400)\\pos(960,580)}How four machines make one decision"))
    # 01 perception (3.0-8.4)
    A, B = 3.0, 8.4
    e.append(ev(A, B, "H1", "{\\fad(300,300)}01   PERCEPTION"))
    e.append(ev(A + 0.2, B, "H2", "{\\fad(300,300)}Each machine senses part of the scene. None senses all of it."))
    for i, (key, txt, dx, dy) in enumerate([
            ("UAV_1", "UAV-1 · camera — person hidden by spray", -40, -64),
            ("USV_1", "USV-1 · radar — sees the crest, not the person", 34, 10),
            ("AUV_1", "AUV-1 (−4.8 m) · sonar — contact at 6.2 m", 34, 26)]):
        t = A + 0.5 + i * 1.0
        x, y = p[key]
        e.append(ring(x, y, 22, WHITE, t, B + 10.6 if key != "AUV_1" else B + 10.6))
        e.append(line(x + 16, y + (dy > 0) * 10 - (dy < 0) * 16, x + dx, y + dy, WHITE, t, B))
        e.append(label(x + dx + 6, y + dy - 12 if dy > 0 else y + dy - 26, txt, t + 0.2, B))
    x, y = p["PERSON"]
    e.append(ring(x, y, 16, ORANGE, A + 3.4, 19.0, w=2.4, alpha="&H00&"))
    e.append(label(x - 250, y + 26, "person in the water", A + 3.6, B, color=ORANGE))
    (ax, ay), (bx, by) = p["CREST_A"], p["CREST_B"]
    e.append(line(ax, ay, bx, by, WHITE, A + 4.2, B, dash=True, draw=1.0, alpha="&H70&"))
    e.append(label(ax + 20, ay + 6, "breaking crest · 3 m · moving 6.4 m/s", A + 4.6, B))
    # 02 communication (8.4-13.4)
    A, B = 8.4, 13.4
    e.append(ev(A, B, "H1", "{\\fad(300,300)}02   COMMUNICATION"))
    e.append(ev(A + 0.2, B, "H2", "{\\fad(300,300)}They share what they see, and how sure they are."))
    u2 = p["UAV_2"]
    e.append(ring(*u2, 22, WHITE, A + 0.2, 19.0))
    e.append(label(u2[0] - 330, u2[1] + 24, "UAV-2 · relay, 35 m up", A + 0.4, B))
    for i, (a_, b_, dash, note) in enumerate([("AUV_1", "USV_1", True, "acoustic"), ("USV_1", "UAV_2", False, "radio"),
                                              ("UAV_1", "UAV_2", False, "radio")]):
        t = A + 0.8 + i * 0.8
        (x1, y1), (x2, y2) = p[a_], p[b_]
        e.append(line(x1, y1, x2, y2, AMBER, t, B, dash=dash, draw=0.6, alpha="&H20&"))
    e.append(ev(A + 3.3, B, "PANEL", f"{{\\an1\\pos(96,980)\\fad(300,300)}}3 partial views  →  1 shared estimate"))
    e.append(ev(A + 3.8, B, "PANEL", f"{{\\an1\\pos(96,1020)\\fad(300,300)\\1c{AMBER}}}person position · confidence 0.94"))
    # 03 decision (13.4-19.0)
    A, B = 13.4, 19.0
    e.append(ev(A, B, "H1", "{\\fad(300,300)}03   DECISION"))
    e.append(ev(A + 0.2, B, "H2", "{\\fad(300,300)}A task auction, not a leader. The closest machine is not the right one."))
    rows = [(0.6, "task   light and track the person", WHITE),
            (1.4, "USV-1  bid 0.41   closest — withdrawn: wave impact risk", AMBER),
            (2.4, "UAV-1  bid 0.88   assigned", WHITE),
            (3.2, "AUV-1  bid 0.22   holds acoustic contact", WHITE)]
    for i, (dt, txt, col) in enumerate(rows):
        e.append(ev(A + dt, B, "PANEL", f"{{\\an1\\pos(96,{900 + i * 40})\\fad(250,300)\\1c{col}}}{txt}"))
    x, y = p["UAV_1"]
    e.append(ring(x, y, 30, AMBER, A + 2.4, B, w=3, alpha="&H00&"))
    sx, sy = p["BEAM_SPOT"]
    px, py = p["PERSON"]
    e.append(line(sx, sy, px, py, AMBER, A + 3.8, B, draw=1.0, alpha="&H10&"))
    e.append(label(sx - 300, sy - 40, "searchlight → person", A + 4.0, B, color=AMBER))
    # 04 action (19-23): footage
    e.append(ev(19.0, 23.0, "H1", "{\\fad(300,300)}04   ACTION"))
    e.append(ev(19.2, 23.0, "H2", "{\\fad(300,300)}Real time resumes. UAV-1 lights the person; USV-1 holds down-drift; the rescue comes in."))
    # 23-25 end card
    e.append(ev(23.0, 25.0, "SUB", "{\\fad(400,0)\\pos(960,470)}ARRC RESEARCH AREAS"))
    e.append(ev(23.2, 25.0, "PANEL", "{\\an5\\fad(400,0)\\pos(960,540)}Perception & Computer Vision  ·  Communication & Networking"))
    e.append(ev(23.2, 25.0, "PANEL", "{\\an5\\fad(400,0)\\pos(960,585)}Control & Decision Making  ·  Swarm & Coordination"))
    e.append(ev(23.4, 25.0, "DISC", "{\\fad(400,0)}Dramatization inspired by ARRC's public research areas. Values shown are illustrative."))
    ass = os.path.join(WORK, "explainer.ass")
    write(ass, ass_header(1920, 1080, styles) + "".join(e))
    # picture: plate 0-19 s (darkened), S12 footage 19-23 s, black 23-25 s
    s12 = os.path.join(ROOT, "06_renders", "finals", "S12")
    if not os.path.exists(os.path.join(s12, "S12_1060.png")):
        s12 = os.path.join(ROOT, "06_renders", "previews", "S12")
    vf = (f"[0:v]scale=1920:1080,format=rgb48le,eq=brightness=-0.04:saturation=0.85,trim=duration=19,setpts=PTS-STARTPTS[a];"
          f"[1:v]scale=1920:1080,format=rgb48le,trim=duration=4,setpts=PTS-STARTPTS[b];"
          f"[2:v]format=rgb48le[c];[a][b][c]concat=n=3:v=1:a=0,noise=c0s=5:c1s=5:c2s=5:allf=t,format=yuv420p,"
          f"vignette=angle=PI/5,fade=t=in:st=0:d=0.6,fade=t=out:st=24.4:d=0.6,subtitles=explainer.ass[v]")
    audio = os.path.join(WORK, "explainer_audio.wav")
    explainer_audio(audio)
    out = os.path.join(DELIV, "explainer", "BHC_explainer_25s_v001.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "24", "-t", "19", "-i", plate,
         "-framerate", "24", "-start_number", "1060", "-i", os.path.join(s12, "S12_%04d.png"),
         "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=24:d=2", "-i", audio,
         "-filter_complex", vf, "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out])
    print("RESULT explainer", out)


def explainer_audio(path, sr=48000, dur=25.0):
    rng = np.random.default_rng(3)
    n = int(sr * dur)
    t = np.arange(n) / sr
    brown = np.cumsum(rng.standard_normal(n))
    X = np.fft.rfft(brown)
    f = np.fft.rfftfreq(n, 1 / sr)
    X *= 1 / np.sqrt(1 + (f / 150) ** 8) / np.sqrt(1 + (20 / np.maximum(f, 1e-3)) ** 8)
    bed = np.fft.irfft(X, n)
    bed = bed / np.max(np.abs(bed)) * 0.12 * np.clip(t / 1.5, 0, 1) * np.clip((dur - t) / 1.5, 0, 1)
    bed += 0.05 * np.sin(2 * np.pi * 41 * t) * np.clip(t / 2, 0, 1) * np.clip((dur - t) / 2, 0, 1)

    def click(t0, lvl=0.18):
        i = int(t0 * sr)
        m = int(0.004 * sr)
        bed[i:i + m] += rng.standard_normal(m) * lvl * np.exp(-np.arange(m) / (0.0015 * sr))
    for t0 in (3.5, 4.5, 5.5, 6.6, 7.2, 8.6, 9.2, 10.0, 10.8, 11.7, 13.6, 14.0, 14.8, 15.8, 16.6):
        click(t0)
    i = int(5.5 * sr)
    m = int(1.2 * sr)
    tt = np.arange(m) / sr
    bed[i:i + m] += 0.09 * np.sin(2 * np.pi * 1150 * tt) * np.exp(-tt / 0.3)
    i = int(19.0 * sr)
    m = int(4.0 * sr)
    tt = np.arange(m) / sr
    sea = rng.standard_normal(m)
    Y = np.fft.rfft(sea)
    ff = np.fft.rfftfreq(m, 1 / sr)
    Y *= 1 / np.sqrt(1 + (ff / 1200) ** 6)
    sea = np.fft.irfft(Y, m)
    bed[i:i + m] += sea / np.max(np.abs(sea)) * 0.08
    i = int(23.0 * sr)
    m = n - i
    tt = np.arange(m) / sr
    bed[i:] += 0.12 * (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 110 * tt)) * np.clip(tt / 0.8, 0, 1) * np.clip((dur - 23 - tt) / 0.6, 0, 1)
    wav_write(path, bed)


# ---------------------------------------------------------------- teaser

def teaser():
    """6 s: the frozen instant, the snap, the title."""
    styles = ["TITLE,Bahnschrift,62,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,14,0,1,0,0,5,0,0,0,1",
              "TC,Consolas,30,&H20F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1",
              "SUB,Bahnschrift,20,&H50F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,2,0,0,64,1"]
    e = [ev(4.25, 6.0, "TITLE", "{\\fad(500,0)\\pos(960,505)}BEYOND HUMAN CONTROL"),
         ev(4.6, 6.0, "TC", "{\\fad(500,0)\\pos(960,580)}0.300 s"),
         ev(4.8, 6.0, "SUB", "{\\fad(500,0)}Technology Innovation Institute  ·  Autonomous Robotics Research Center")]
    ass = os.path.join(WORK, "teaser.ass")
    write(ass, ass_header(1920, 1080, styles) + "".join(e))
    out = os.path.join(DELIV, "teaser_6s", "BHC_teaser_6s_v001.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fc = ("[0:v]trim=1.4:3.9,setpts=PTS-STARTPTS[a];[0:a]atrim=1.4:3.9,asetpts=PTS-STARTPTS[aa];"
          "[0:v]trim=41.0:42.75,setpts=PTS-STARTPTS[b];[0:a]atrim=41.0:42.75,asetpts=PTS-STARTPTS,afade=t=out:st=1.45:d=0.3[ba];"
          "[1:v]trim=duration=1.75,setpts=PTS-STARTPTS[c];"
          "[2:a]atrim=duration=1.75,asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st=1.2:d=0.55,volume=0.5[ca];"
          "[a][aa][b][ba][c][ca]concat=n=3:v=1:a=1[v0][ao];[v0]fade=t=in:d=0.5,subtitles=teaser.ass[v]")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", MASTER, "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=24:d=2",
         "-f", "lavfi", "-i", "sine=f=55:d=2:sample_rate=48000", "-filter_complex", fc, "-map", "[v]", "-map", "[ao]",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", out])
    print("RESULT teaser", out)


# ---------------------------------------------------------------- social 9:16

SOCIAL = [  # (shot, first frame, last frame) from the vertical renders, film-time order
    ("S01", 29, 76), ("S06", 500, 559), ("S10", 889, 950), ("S11", 985, 1027), (None, 0, 7), ("S12", 1057, 1195)]


def social():
    """15 s vertical: the instant, the waterline, the assignment, the snap, the aftermath + title."""
    vdir = os.path.join(ROOT, "06_renders", "vertical")
    inputs, chain, segs = [], "", []
    t = 0.0
    film_ranges = []
    for i, (shot, a, b) in enumerate(SOCIAL):
        n = b - a + 1
        if shot is None:
            inputs += ["-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r=24:d={n / 24}"]
            film_ranges.append((S.BLACK[0], S.BLACK[0] + n / 24))
        else:
            inputs += ["-framerate", "24", "-start_number", str(a), "-i", os.path.join(vdir, shot, f"{shot}_%04d.png")]
            film_ranges.append(((a - 1) / 24, b / 24))
        chain += f"[{i}:v]scale=1080:1920,format=rgb48le,setsar=1,trim=end_frame={n},setpts=PTS-STARTPTS[s{i}];"
        segs.append((t, shot, a, b))
        t += n / 24
    dur = t
    chain += "".join(f"[s{i}]" for i in range(len(SOCIAL))) + f"concat=n={len(SOCIAL)}:v=1:a=0,noise=c0s=6:c1s=6:c2s=6:allf=t,format=yuv420p,vignette=angle=PI/5,fade=t=in:d=0.6"
    t_s12 = segs[-1][0]
    fade_at = t_s12 + (S.FADE_OUT - S.BLACK[1])
    chain += f",fade=t=out:st={fade_at:.2f}:d=0.6,subtitles=social.ass[v]"
    # sound: the master mix, cut at the same film times
    aparts = "".join(f"[{len(SOCIAL)}:a]atrim={fa:.3f}:{fb:.3f},asetpts=PTS-STARTPTS[x{i}];" for i, (fa, fb) in enumerate(film_ranges))
    aparts += "".join(f"[x{i}]" for i in range(len(SOCIAL))) + f"concat=n={len(SOCIAL)}:v=0:a=1,afade=t=out:st={dur - 0.6:.2f}:d=0.6[a]"
    styles = ["TC,Consolas,34,&H40F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,1,72,72,150,1",
              "DATA,Consolas,32,&H22F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,1,72,72,200,1",
              "TITLE,Bahnschrift,72,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,8,0,1,0,0,5,0,0,0,1",
              "SUB,Bahnschrift,28,&H40F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1"]
    e = []
    for (t0, shot, a, b), (fa, fb) in zip(segs, film_ranges):
        n = int(round((fb - fa) * 24))
        cur, ts = None, t0
        for k in range(n + 1):
            tt = fa + k / 24
            tc = S.timecode(tt) if k < n else None
            if tc != cur:
                if cur:
                    e.append(ev(ts, t0 + k / 24, "TC", cur))
                cur, ts = tc, t0 + k / 24
        for da, db, txt in S.DATA_LINES:
            if fa <= da < fb and "assigned" in txt:
                e.append(ev(t0 + da - fa, t0 + min(db, fb) - fa, "DATA", "{\\fad(180,200)}" + txt))
    title_t = t_s12 + (S.TITLE_IN - S.BLACK[1])
    e.append(ev(title_t, dur, "TITLE", "{\\fad(800,0)\\pos(540,900)}BEYOND{\\N}HUMAN{\\N}CONTROL"))
    e.append(ev(title_t + 0.6, dur, "SUB", "{\\fad(700,0)\\pos(540,1180)}TII  ·  Autonomous Robotics Research Center"))
    write(os.path.join(WORK, "social.ass"), ass_header(1080, 1920, styles) + "".join(e))
    out = os.path.join(DELIV, "social_9x16", "BHC_social_15s_9x16_v001.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run(["ffmpeg", "-loglevel", "error", "-y"] + inputs + ["-i", MIX, "-filter_complex", chain + ";" + aparts,
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-r", "24", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    print("RESULT social", out, f"{dur:.2f}s")


# ---------------------------------------------------------------- posters and LinkedIn

POSTERS = [
    ("P1_the_instant", "S02_post_f0168.png", "0.300 SECONDS. FOUR MACHINES. ONE DECISION."),
    ("P2_waterline", "S06_post_f0540.png", "NONE OF THEM SEES ALL OF IT."),
    ("P3_assigned", "S10_post_f0980.png", "NO ONE COULD DECIDE THIS FAST."),
]
LINKEDIN = [
    ("L1", "P1_the_instant", "0.300 s", "The time a robot swarm needs to see, share, decide and act. About the time it takes you to blink."),
    ("L2", "P2_waterline", "Four machines. One picture.", "A drone, a surface vessel and an underwater vehicle each see part of the scene. Together they see all of it."),
    ("L3", "P3_assigned", "The closest machine is not always the right one.", "A task auction, not a leader: the swarm assigns each job to the machine best placed to do it."),
]


def posters():
    src = os.path.join(ROOT, "06_renders", "posters")
    out_dir = os.path.join(DELIV, "posters")
    os.makedirs(out_dir, exist_ok=True)
    styles = ["TITLE,Bahnschrift,150,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,26,0,1,0,0,5,0,0,0,1",
              "TAG,Consolas,46,&H30F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,5,0,0,0,1",
              "CRED,Bahnschrift,40,&H40F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,0,0,5,0,0,0,1",
              "DISC,Bahnschrift,26,&H80F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,2,0,0,90,1"]
    for name, still, tag in POSTERS:
        e = [ev(0, 10, "TAG", f"{{\\pos(1200,2700)}}{tag}"),
             ev(0, 10, "TITLE", "{\\pos(1200,2900)}BEYOND HUMAN CONTROL"),
             ev(0, 10, "CRED", "{\\pos(1200,3120)}TECHNOLOGY INNOVATION INSTITUTE  ·  AUTONOMOUS ROBOTICS RESEARCH CENTER"),
             ev(0, 10, "DISC", "A dramatization inspired by ARRC's public research areas.")]
        write(os.path.join(WORK, f"{name}.ass"), ass_header(2400, 3600, styles) + "".join(e))
        out = os.path.join(out_dir, f"BHC_{name}_2400x3600.png")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(src, still), "-vf",
             f"format=rgb48le,noise=c0s=5:c1s=5:c2s=5,format=rgb24,vignette=angle=PI/4.5,"
             f"drawbox=y=ih*0.70:w=iw:h=ih*0.30:c=black@0.0:t=fill,subtitles={name}.ass", "-frames:v", "1", out])
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-q:v", "2", out.replace(".png", ".jpg")])
        print("RESULT poster", out)


def linkedin():
    out_dir = os.path.join(DELIV, "linkedin")
    os.makedirs(out_dir, exist_ok=True)
    styles = ["HEAD,Bahnschrift,62,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,7,72,72,0,1",
              "BODY,Bahnschrift,30,&H30F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,72,72,0,1",
              "CRED,Consolas,22,&H50F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,1,72,72,60,1"]
    for name, poster, head, body in LINKEDIN:
        src = os.path.join(ROOT, "06_renders", "posters", dict((p[0], p[1]) for p in POSTERS)[poster])
        e = [ev(0, 10, "HEAD", f"{{\\pos(72,1000)}}{head}"),
             ev(0, 10, "BODY", f"{{\\pos(72,1090)\\q0}}{body}"),
             ev(0, 10, "CRED", "BEYOND HUMAN CONTROL  ·  TII · ARRC")]
        write(os.path.join(WORK, f"{name}.ass"), ass_header(1080, 1350, styles) + "".join(e))
        out = os.path.join(out_dir, f"BHC_LinkedIn_{name}_1080x1350.png")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf",
             "crop=iw:iw*1.25:0:(ih-iw*1.25)*0.35,scale=1080:1350,format=rgb48le,noise=c0s=5:c1s=5:c2s=5,format=rgb24,"
             f"vignette=angle=PI/4.5,drawbox=y=ih*0.66:w=iw:h=ih*0.34:c=black@0.45:t=fill,subtitles={name}.ass",
             "-frames:v", "1", out])
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-q:v", "2", out.replace(".png", ".jpg")])
        print("RESULT linkedin", out)


if __name__ == "__main__":
    {"explainer": explainer, "teaser": teaser, "social": social, "posters": posters, "linkedin": linkedin}[sys.argv[1]]()
