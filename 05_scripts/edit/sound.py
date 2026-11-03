"""Placeholder sound design + VO mix for the animatic, synthesized from the shared story timeline.

Run with Blender's bundled Python (numpy):
  "C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" 05_scripts/edit/sound.py [--vo temp|final] [--out name]

Design (production document §5): no music. One real second of sea, stretched, is the bed; rotors pulse
once a second; every radio message is a dry click; sonar pings ring and echo; the snap is everything at
once at full scale, then silence; the aftermath is real sea, a distant helicopter and one low tone.
"""
import argparse
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "05_scripts"))
from bhc import story as S  # noqa: E402

SR = 48000
N = int(S.DURATION * SR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def db(x):
    return 10 ** (x / 20)


def fft_filter(x, lo=None, hi=None, slope=4):
    """Smooth band-limit in the frequency domain (fast for whole-film signals)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * slope))
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * slope))
    return np.fft.irfft(X * g, len(x))


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def span(a, b):
    return slice(int(a * SR), min(int(b * SR), N))


def envelope(points):
    """Piecewise-linear gain over the film: [(t, gain_db or None for silence)]."""
    ts = [p[0] for p in points]
    gs = [db(p[1]) if p[1] is not None else 0.0 for p in points]
    return np.interp(t_all, ts, gs)


def place(bus, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    n = min(len(sig), N - i)
    bus[:, i:i + n] += gain * sig[:, :n] if sig.ndim == 2 else gain * sig[:n]


def stereo(x, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r])


def read_wav(path):
    with wave.open(path) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    if sr != SR:
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a


def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    return a[max(idx[0] - int(0.03 * SR), 0): idx[-1] + int(0.12 * SR)]


# ---------------------------------------------------------------- layers

def bed():
    """The stretched wave: sub-bass tide + a breath of stretched wind, until the snap."""
    brown = np.cumsum(rng.standard_normal(N))
    sub = fft_filter(brown, lo=18, hi=140)
    sub = norm(sub) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t_all))
    tone = np.sin(2 * np.pi * 41 * t_all + 0.6 * np.sin(2 * np.pi * 0.11 * t_all)) * 0.35
    air = norm(fft_filter(rng.standard_normal(N), lo=300, hi=1500)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t_all + 1)) * 0.25
    x = sub + tone + air
    g = envelope([(0, -60), (0.4, -60), (2.5, -20), (16, -21), (20, -23), (36, -19), (40.9, -15), (41.0, None), (50, None)])
    out = stereo(x * g)
    out[1] = np.roll(out[1], 240)                       # a little width
    return out


def underwater():
    x = norm(fft_filter(rng.standard_normal(N), lo=40, hi=380)) * 0.8
    g = envelope([(0, None), (15.9, None), (16.3, -24), (24.6, -26), (25.0, None), (50, None)])
    return stereo(x * g)


def rotors():
    """Slowed rotors: one soft thump per second (8,000 rpm at 137x)."""
    out = np.zeros((2, N))
    thump_n = int(0.12 * SR)
    tt = np.arange(thump_n) / SR
    for k in range(5, 41):
        burst = fft_filter(rng.standard_normal(thump_n), lo=40, hi=260) * np.exp(-tt / 0.035)
        place(out, stereo(norm(burst), 0.1 * np.sin(k)), k + 0.13)
    g = envelope([(0, None), (4.9, None), (5.0, -34), (9, -34), (9.2, -20), (12.8, -20), (13, -34), (25, -34),
                  (25.2, -26), (28.8, -26), (29, -34), (36, -30), (36.5, -20), (40.9, -18), (41, None), (50, None)])
    return out * g


def droplets():
    out = np.zeros((2, N))
    for _ in range(26):
        t0 = rng.uniform(0.6, 5.0)
        n = int(0.05 * SR)
        tt = np.arange(n) / SR
        f = rng.uniform(2500, 6500)
        place(out, stereo(np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.012), rng.uniform(-0.7, 0.7)), t0, db(-34))
    return out


def click(level=-18, pan=0.0, band=(1500, 5000), dur=0.006):
    n = int(dur * SR)
    c = fft_filter(np.concatenate([rng.standard_normal(n), np.zeros(n * 4)]), lo=band[0], hi=band[1])
    return stereo(norm(c) * db(level), pan)


def messages():
    out = np.zeros((2, N))
    pans = {"UAV_1": 0.4, "UAV_2": -0.5, "USV_1": -0.2, "AUV_1": 0.2}
    for t, who in S.EVENTS:
        place(out, click(-17, pans.get(who, 0)), t)
    for t0, _, _ in S.DATA_LINES:
        place(out, click(-28, 0.0, (2500, 7000), 0.003), t0)
    return out


def sonar():
    out = np.zeros((2, N))
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    f = 1150 * (1 - 0.04 * tt)
    ping = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.32) * (1 - np.exp(-tt / 0.004))
    ping = fft_filter(ping, hi=2500)
    for p in S.PINGS:
        place(out, stereo(norm(ping), -0.3), p, db(-16))
        place(out, stereo(norm(fft_filter(ping, hi=1400)), 0.3), p + S.ECHO_DELAY, db(-24))
    return out


def decision_layers():
    out = np.zeros((2, N))
    # S08: confidence resolving upward as estimates fuse
    s = span(29.6, 31.9)
    tt = t_all[s] - 29.6
    f = 392 + (523 - 392) * np.clip(tt / 1.6, 0, 1)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 2.3) ** 2
    out[:, s] += stereo(tone * db(-31))
    # S09: crest stress, a low groan
    s = span(32.0, 36.0)
    tt = t_all[s] - 32.0
    groan = norm(fft_filter(rng.standard_normal(len(tt)), lo=45, hi=190)) * np.sin(np.pi * tt / 4.0) ** 2
    out[:, s] += stereo(groan * db(-22))
    # S10: slowed servo whine as the searchlight swings + rising sub into the snap
    s = span(S.SWING[0], S.SWING[1])
    tt = t_all[s] - S.SWING[0]
    f = 150 + 60 * tt / (S.SWING[1] - S.SWING[0])
    ph = 2 * np.pi * np.cumsum(f) / SR
    servo = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * np.sin(np.pi * tt / (S.SWING[1] - S.SWING[0])) ** 0.5
    out[:, s] += stereo(servo * db(-30), 0.3)
    s = span(36.0, 41.0)
    tt = t_all[s] - 36.0
    f = 30 + 15 * tt / 5
    out[:, s] += stereo(np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / 5) ** 2 * db(-14))
    return out


def snap():
    """Real time: everything at once, at full scale, for two and a half seconds."""
    out = np.zeros((2, N))
    a, b = S.SNAP, S.BLACK[0]
    n = int((b - a) * SR)
    tt = np.arange(n) / SR
    env = (1 - np.exp(-tt / 0.004)) * np.exp(-tt / 1.1)
    for ch in (0, 1):
        crash = rng.standard_normal(n)
        # lowpass sweeping down: blend a bright and a dark version over time
        bright = fft_filter(crash, lo=60, hi=11000)
        dark = fft_filter(crash, lo=40, hi=1500)
        k = np.clip(tt / 1.6, 0, 1)
        out[ch, int(a * SR):int(a * SR) + n] += norm(bright * (1 - k) + dark * k) * env * db(-3)
    boom_f = 48 - 13 * np.clip(tt / 1.2, 0, 1)
    boom = np.sin(2 * np.pi * np.cumsum(boom_f) / SR) * np.exp(-tt / 0.7) * (1 - np.exp(-tt / 0.01))
    out[:, int(a * SR):int(a * SR) + n] += stereo(boom * db(-4))
    rot_ph = 2 * np.pi * 133 * tt
    rot = (np.sin(rot_ph) + 0.5 * np.sin(2 * rot_ph) + 0.3 * np.sin(3 * rot_ph)) * (0.6 + 0.4 * rng.standard_normal(n).cumsum() / np.sqrt(n))
    out[:, int(a * SR):int(a * SR) + n] += stereo(norm(rot) * db(-15) * (1 - np.exp(-tt / 0.02)), 0.5)
    out[:, int(b * SR):int(S.BLACK[1] * SR)] = 0.0
    return out


def aftermath():
    out = np.zeros((2, N))
    s = span(S.BLACK[1], S.DURATION)
    tt = t_all[s] - S.BLACK[1]
    n = len(tt)
    pink = np.cumsum(rng.standard_normal(n)) * 0.02 + rng.standard_normal(n)
    sea = norm(fft_filter(pink, lo=60, hi=1500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * tt))
    sea_g = np.interp(tt, [0, 0.4, 6], [db(-40), db(-21), db(-22)])
    out[:, s] += stereo(sea * sea_g)
    hum_ph = 2 * np.pi * 133 * tt
    hum = (np.sin(hum_ph) + 0.4 * np.sin(2 * hum_ph)) * db(-33)
    out[:, s] += stereo(hum, 0.3)
    heli = norm(fft_filter(rng.standard_normal(n), lo=40, hi=320)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11 * tt)))
    heli_g = np.interp(tt, [0, 0.8, 5.0, 6.0], [0, db(-34), db(-22), db(-24)])
    out[:, s] += stereo(fft_filter(heli, hi=500) * heli_g, -0.4)
    s2 = span(47.2, S.DURATION)
    t2 = t_all[s2] - 47.2
    tone = (np.sin(2 * np.pi * 55 * t2) + 0.5 * np.sin(2 * np.pi * 110 * t2) + 0.15 * np.sin(2 * np.pi * 165 * t2))
    out[:, s2] += stereo(tone * np.clip(t2 / 1.2, 0, 1) * np.exp(-np.maximum(t2 - 1.5, 0) / 1.4) * db(-17))
    return out


def vo_track(kind):
    """Each line at its cue, trimmed; nudged earlier only if it would collide with the next cue or the end."""
    d = os.path.join(ROOT, "08_audio", "vo", kind)
    out = np.zeros(N)
    cues = list(S.VO)
    for i, (vid, t0, _) in enumerate(cues):
        p = os.path.join(d, f"{vid}.wav")
        if not os.path.exists(p):
            print("MISSING VO", p)
            continue
        a = trim(read_wav(p))
        a = a / max(np.max(np.abs(a)), 1e-6) * db(-4)
        limit = cues[i + 1][1] - 0.15 if i + 1 < len(cues) else S.DURATION - 0.35
        start = min(t0, limit - len(a) / SR)
        if start < t0:
            print(f"VO {vid}: moved {t0:.2f} -> {start:.2f} s to fit")
        i0 = int(start * SR)
        out[i0:i0 + len(a)] += a[:N - i0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", default="temp")
    ap.add_argument("--out", default="BHC_mix_temp_v001")
    a = ap.parse_args()
    fx = bed() + underwater() + rotors() + droplets() + messages() + sonar() + decision_layers() + snap() + aftermath()
    vo = vo_track(a.vo)
    duck = np.convolve(np.abs(vo), np.ones(int(0.15 * SR)) / (0.15 * SR), mode="same")
    duck = 1 - 0.45 * np.clip(duck / 0.05, 0, 1)
    mix = fx * duck + stereo(vo)
    mix[:, -int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / np.max(np.abs(mix)) * db(-1)
    out = os.path.join(ROOT, "08_audio", "mix", f"{a.out}.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pcm = (mix.T * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("RESULT", out, f"{N / SR:.1f}s")


main()
