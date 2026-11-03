"""Assemble the 12 shots into the film: grade, typography (timecode, data lines, end card), sound.

  python 05_scripts/edit/assemble.py --src previews --mix BHC_mix_temp_v001 --out 09_edit/BHC_animatic_v001.mp4
  python 05_scripts/edit/assemble.py --src finals --mix BHC_mix_v001 --out 10_deliverables/main_16x9/BHC_main_16x9_v001.mp4 --crf 14

Typography follows production rule 3: one small monospace clock, at most one data line, no HUD.
Missing shot frames are replaced with black and reported (logged to 00_admin/RENDER_LOG.md).
"""
import argparse
import datetime
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "05_scripts"))
from bhc import story as S  # noqa: E402

SHOTS = {"S01": (1, 120), "S02": (121, 216), "S03": (217, 312), "S04": (313, 384), "S05": (385, 480),
         "S06": (481, 600), "S07": (601, 696), "S08": (697, 768), "S09": (769, 864), "S10": (865, 984),
         "S11": (985, 1056), "S12": (1057, 1200)}


def ass_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TC,Consolas,25,&H40F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,1,96,96,70,1
Style: DATA,Consolas,25,&H22F2F2F2,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,1,96,96,108,1
Style: TITLE,Bahnschrift,66,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,16,0,1,0,0,5,0,0,0,1
Style: SUB,Bahnschrift,23,&H40F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: DISC,Bahnschrift,15,&H80F4F4F4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,2,0,0,58,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    # clock: one event per change of the displayed value, frame-accurate
    n = int(S.DURATION * S.FPS)
    cur, t_start = None, 0.0
    for f in range(n + 1):
        t = f / S.FPS
        tc = S.timecode(t) if f < n else None
        if tc != cur:
            if cur is not None:
                ev.append(f"Dialogue: 0,{ass_time(t_start)},{ass_time(t)},TC,,0,0,0,,{cur}")
            cur, t_start = tc, t
    for a, b, text in S.DATA_LINES:
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},DATA,,0,0,0,,{{\\fad(180,260)}}{text}")
    ev.append(f"Dialogue: 1,{ass_time(S.TITLE_IN)},{ass_time(S.DURATION)},TITLE,,0,0,0,,{{\\fad(900,0)\\pos(960,505)}}{S.TITLE}")
    ev.append(f"Dialogue: 1,{ass_time(S.TITLE_IN + 0.7)},{ass_time(S.DURATION)},SUB,,0,0,0,,{{\\fad(700,0)\\pos(960,585)}}{S.SUBTITLE}")
    ev.append(f"Dialogue: 1,{ass_time(S.TITLE_IN + 1.1)},{ass_time(S.DURATION)},DISC,,0,0,0,,{{\\fad(700,0)}}{S.DISCLAIMER}")
    with open(path, "w", encoding="utf-8-sig") as fh:
        fh.write(head + "\n".join(ev) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="previews")
    ap.add_argument("--mix", default="BHC_mix_temp_v001")
    ap.add_argument("--out", default="09_edit/BHC_animatic_v001.mp4")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--grain", type=float, default=6.0)
    ap.add_argument("--notext", action="store_true")
    a = ap.parse_args()
    work = os.path.join(ROOT, "09_edit", "work")
    os.makedirs(work, exist_ok=True)
    ass = os.path.join(work, "titles.ass")
    build_ass(ass)
    inputs, missing, total = [], [], 0
    for shot, (f0, f1) in SHOTS.items():
        d = os.path.join(ROOT, "06_renders", a.src, shot)
        have = [f for f in range(f0, f1 + 1) if os.path.exists(os.path.join(d, f"{shot}_{f:04d}.png"))]
        total += len(have) if len(have) == f1 - f0 + 1 else 0
        if len(have) == f1 - f0 + 1:
            inputs += ["-framerate", str(S.FPS), "-start_number", str(f0), "-i", os.path.join(d, f"{shot}_%04d.png")]
        else:
            missing.append(f"{shot} ({len(have)}/{f1 - f0 + 1})")
            inputs += ["-f", "lavfi", "-i", f"color=c=black:s=960x540:r={S.FPS}:d={(f1 - f0 + 1) / S.FPS}"]
    w = 960 if a.src == "previews" else 1920
    h = w * 9 // 16
    chain = "".join(f"[{i}:v]scale={w}:{h},format=rgb48le,setsar=1[s{i}];" for i in range(12))
    chain += "".join(f"[s{i}]" for i in range(12)) + "concat=n=12:v=1:a=0[cat];"
    chain += (f"[cat]noise=c0s={a.grain}:c1s={a.grain}:c2s={a.grain}:allf=t,format=yuv420p,"
              f"vignette=angle=PI/5,fade=t=in:st=0:d=1.2,"
              f"drawbox=enable='between(t,{S.BLACK[0]},{S.BLACK[1]})':c=black:t=fill,"
              f"fade=t=out:st={S.FADE_OUT}:d=0.6")
    chain += "[g];[g]null[out]" if a.notext else ",subtitles=titles.ass[out]"
    mix = os.path.join(ROOT, "08_audio", "mix", f"{a.mix}.wav")
    out = os.path.join(ROOT, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg", "-loglevel", "error", "-y"] + inputs + ["-i", mix, "-filter_complex", chain,
           "-map", "[out]", "-map", "12:a", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
           "-pix_fmt", "yuv420p", "-r", str(S.FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out]
    rc = subprocess.call(cmd, cwd=work)
    note = ("missing: " + ", ".join(missing)) if missing else ""
    with open(os.path.join(ROOT, "00_admin", "RENDER_LOG.md"), "a", encoding="utf-8") as fh:
        fh.write(f"| {datetime.datetime.now():%m-%d %H:%M} | EDIT | {os.path.basename(out)} | assemble | "
                 f"{'OK' if rc == 0 else 'FAILED'} | {total}/1200 | | {note} |\n")
    print("RESULT", "OK" if rc == 0 else "FAILED", out, note)


main()
