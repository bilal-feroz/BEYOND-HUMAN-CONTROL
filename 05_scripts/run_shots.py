"""Render shots one Blender process at a time and log every run to 00_admin/RENDER_LOG.md.

  python 05_scripts/run_shots.py --shots S01 S02 ... [--anim] [--ver p001] [--out previews] [extra blender args]

Logs: 06_renders/<out>/logs/<shot>_<ver>.log (full stdout) and one table row per run in RENDER_LOG.md
(status OK / FAILED / MISSING FRAMES, frame count, wall time).
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SHOTS = {"S01": (1, 120), "S02": (121, 216), "S03": (217, 312), "S04": (313, 384), "S05": (385, 480),
         "S06": (481, 600), "S07": (601, 696), "S08": (697, 768), "S09": (769, 864), "S10": (865, 984),
         "S11": (985, 1056), "S12": (1057, 1200)}
LOG = os.path.join(ROOT, "00_admin", "RENDER_LOG.md")


def log_row(row):
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as f:
        if new:
            f.write("# Render log\n\n| When | Shot | Ver | Mode | Status | Frames | Wall s | Notes |\n|---|---|---|---|---|---|---|---|\n")
        f.write("| " + " | ".join(str(c) for c in row) + " |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", nargs="+", default=list(SHOTS))
    ap.add_argument("--anim", action="store_true")
    ap.add_argument("--ver", default="p001")
    ap.add_argument("--out", default="previews")
    ap.add_argument("--note", default="")
    a, extra = ap.parse_known_args()
    os.makedirs(os.path.join(ROOT, "06_renders", a.out, "logs"), exist_ok=True)
    for shot in a.shots:
        cmd = [BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "-P",
               os.path.join(ROOT, "05_scripts", "shots", "shots.py"), "--",
               "--shot", shot, "--ver", a.ver, "--out", a.out] + (["--anim"] if a.anim else []) + extra
        logf = os.path.join(ROOT, "06_renders", a.out, "logs", f"{shot}_{a.ver}{'_anim' if a.anim else ''}.log")
        t = time.time()
        with open(logf, "w", encoding="utf-8", errors="replace") as fh:
            rc = subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT)
        dt = time.time() - t
        text = open(logf, encoding="utf-8", errors="replace").read()
        res = re.findall(r"^RESULT .*$", text, re.M)
        errs = re.findall(r"^(?:Error|Traceback|.*Exception).*$", text, re.M)
        status, frames, note = ("OK" if rc == 0 and res else "FAILED"), "", a.note
        if a.anim and status == "OK":
            f0, f1 = SHOTS[shot]
            d = os.path.join(ROOT, "06_renders", a.out, shot)
            have = [f for f in range(f0, f1 + 1) if os.path.exists(os.path.join(d, f"{shot}_{f:04d}.png"))]
            frames = f"{len(have)}/{f1 - f0 + 1}"
            if len(have) != f1 - f0 + 1:
                status = "MISSING FRAMES"
        if status != "OK":
            note = (note + " " + "; ".join(errs[-2:])).strip()[:160]
        when = datetime.datetime.now().strftime("%m-%d %H:%M")
        log_row([when, shot, a.ver, "anim" if a.anim else "still", status, frames, f"{dt:.0f}", note.replace("|", "/")])
        print(f"{shot}: {status} {frames} {dt:.0f}s {res[-1] if res else ''}", flush=True)


if __name__ == "__main__":
    main()
