# BEYOND HUMAN CONTROL: Production Breakdown

**Film:** BEYOND HUMAN CONTROL, concept *300 MILLISECONDS*. 50 s, 16:9, 1920×1080, 24 fps.
**For:** Technology Innovation Institute (TII), Autonomous Robotics Research Center (ARRC). A dramatization inspired by ARRC's public research areas; it claims no specific TII capability.
**Made with:** Blender 5.2.3 (EEVEE) driven headless from Python, ffmpeg (libass, rubberband), and numpy sound synthesis. Every image and sound is generated from the code in this repository: no stock footage, no downloaded models, no simulation caches.

---

## 1. Creative decisions

| Decision | Why |
|---|---|
| One decision, 0.300 s long, slowed 136.7× to fill 41 s | The form is the argument: autonomy matters because some decisions happen faster than a person can react. "A 50-second film about a third of a second." |
| The title reads as "beyond human *speed*" | It turns a provocative title into a responsible position: control moves earlier, into design ("So we spend years deciding how they should"). |
| A mixed swarm of 2 drones, a surface vessel and an underwater vehicle; no humanoids | It matches ARRC's public research (aerial, marine, underwater; hybrid swarms) and avoids the generic humanoid cliché. |
| Night Gulf in a shamal, search and rescue | A real Gulf condition and a real ARRC application area. Night lets light carry the story. |
| **Orange means human** | Only the life jacket is saturated orange; robots are white, grey and graphite. The eye always finds the person. |
| Physics sets the motion | At 137×, rotors turn ~1 rev/s, the crest creeps ~5 cm/s, spray drifts, and sonar crosses the frame at walking pace. Only information is fast. |
| Information is shown only by physical cues | Amber status LEDs pulse per message, the relay drone's strobe fires, a sonar front makes suspended sediment glint. No HUD, no reticles, no glowing UI. A geometric sonar ring was tried and cut because it read as a HUD. |
| Typography: one clock, one data line | A small monospace clock (`21:47:03.000` → `.300`) and at most one machine line at a time, written like a flight-data recorder. |
| No music | The sound design is the score: one stretched second of sea, slowed rotors, dry message clicks, then real time at full volume, then silence. |
| A female, low-register, unhurried narrator | It reads like an investigator's finding and avoids the deep-male trailer voice. |

## 2. Story map (film seconds)

| Shot | Time | Research idea | What moves |
|---|---|---|---|
| S01 Spray | 0–5 | the instant | camera drift through suspended spray; droplets drift cm/s |
| S02 The Wave | 5–9 | stakes, geography | crest creep, spray, crane up |
| S03 UAV-1 | 9–13 | Perception | rotors ~1 rev/s, spray around the sensor, push in, focus pull |
| S04 USV-1 | 13–16 | Perception | vessel on the back of the crest, spray, lateral dolly |
| S05 AUV-1 | 16–20 | Perception | sonar ping crosses to the person and echoes back (particles glint); status pulse on the echo |
| S06 Waterline | 20–25 | the complete view | dome-port split, second ping passes the legs, push in |
| S07 Relay | 25–29 | Communication | relay strobe, status pulses on the swarm, camera follows the message path down |
| S08 Confidence | 29–32 | Communication | amber autonomy light pulses as the fused estimate arrives |
| S09 Obvious choice | 32–36 | Decision | USV-1 bids then withdraws (amber pulses); the crest above it explains why |
| S10 Assigned | 36–41 | Decision → Action | the searchlight slews onto the jacket |
| S11 Snap | 41–44 | Action | real time: the lip pitches and breaks, whitewater spreads, USV-1 turns away, handheld camera; black at 43.5 |
| S12 Aftermath | 44–50 | Action, resolution | time cut to 21:47:14: drone holds the jacket in light, USV-1 waits down-drift, helicopter searchlight approaches; end card |

## 3. Pipeline

```
05_scripts/bhc/core.py      time model (film frame → real seconds, slow-mo, snap, time cut), bpy/GN helpers, render settings
05_scripts/bhc/story.py     timeline as data: events, pings, swing, VO cues, data lines, clock (no bpy)
05_scripts/bhc/env.py       sky, moon, FFT ocean + Gerstner hero wave (GN), breaking, fog, crest mist, whitewater, underwater
05_scripts/bhc/fx.py        spray (steady-state ballistic), mist, particulates with sonar fronts
05_scripts/bhc/assets.py    UAV ×2, USV, AUV, life jacket + person proxy, capsized hull (procedural hard-surface)
05_scripts/bhc/layout.py    master layout + choreography (status pulses, searchlight decision, floating bodies, rescue)
05_scripts/shots/shots.py   12 shots = master layout + camera + flags; S06 renders two passes and composites
05_scripts/run_shots.py     renders shots headless and logs every run (00_admin/RENDER_LOG.md)
05_scripts/edit/            VO (temp/scratch), sound.py (synthesis + mix), assemble.py (film), campaign.py (deliverables)
```

**Time model.** `real_time(frame)` maps film frames to real seconds: 0–0.300 s across frames 1–984, real time from frame 985 (the snap), and a jump to 21:47:14 at frame 1057. The ocean (keyed), Geometry Nodes (Scene Time), spray, mist and lights all read the same function, so every element agrees on "now".

**The wave.** A Blender Ocean modifier (FFT chop, shortest wavelength 0.9 m) plus a Geometry Nodes Gerstner hero wave:
- λ 26 m, A 1.7 m, sharpness 0.82, forward lean 1.8 m: a near-vertical front face without mesh folding
- the crest line wanders (two sine phase terms)
- after the snap the lip pitches forward (+35 %) and the wave loses 42 % of its height over 1.6 s
- a non-uniform grid gives ~0.35 m spacing at the action and ~20 m at the horizon, as one seamless mesh

**Spray.** Each droplet is a closed-form ballistic arc from the crest lip with a 1.6 s life. That holds still at 137× and streams in real time with no cache. Droplets are recycled only after they re-enter the sea, so nothing pops.

**Sonar.** A pressure front at 1,500 m/s (scaled by the time model) makes suspended particles glint where it passes, out to the person and back as an echo.

**The dome-port waterline (S06).** A pinhole camera can't see above and below the surface at once. The shot renders twice, 3 cm above and 3 cm below a locally flattened surface, and composites the halves with a meniscus line.

## 4. Look and rendering

**EEVEE settings:**
- 1920×1080; 64 TAA samples (tests), 48 (finals)
- screen-space ray tracing
- volumetrics: 4 px tiles, 64 slices, end 220 m, volumetric shadows on
- AgX, Medium High Contrast look, exposure +1.8
- compositor bloom
- 16-bit PNG output

**Lessons from the test frames:**

| Problem | Cause | Fix |
|---|---|---|
| Black sky | A world volume is infinite in EEVEE and absorbs the sky | Fog is a mesh volume box with height falloff |
| Diagonal striping through air and sky | A volume material on the wavy ocean mesh | Surface-only ocean; underwater murk is a separate box, shown only in underwater passes |
| Faceted rectangles at grazing angles | The ocean mesh was flat-shaded | Smooth shading |
| Striations on the water | FFT wavelengths shorter than the grid | `wave_scale_min` 0.9 m; two bump octaves in the shader |
| Banding in dark gradients after 8-bit | 8-bit quantization (the 16-bit data is smooth) | Grain is applied before the 8-bit conversion in every encode |
| Dark specks, then snow | Probe-refracted droplets, then opaque defocused droplets | Screen-space refractive water beads with a little forward scatter; droplets culled near the lens |
| Whitewater read as rocks, then hail | Clumps too big, band too wide | Fine froth on the very lip only, patchy noise; spreads after the break |
| Crash in S11 | Post-break foam instances on a 4 GB GPU | Post-break foam count cut 93 %, spray 130k → 100k |

## 5. Edit, grade and sound

- **Assembly:** `assemble.py` concatenates the 12 shot sequences and grades them: luma/chroma grain in 16-bit, then 8-bit, vignette, fade in, hard black at 43.5–44.0, fade to the end card. ASS typography is burned in with libass: Consolas for the clock and data lines, Bahnschrift for titles.
- **Sound:** `sound.py` builds every layer from `story.py`:
  - stretched sub bed with a 41 Hz tone
  - 1 Hz rotor thumps
  - glassy droplet ticks
  - a dry click per radio message, panned by robot
  - 1.15 kHz sonar pings with echoes
  - a confidence tone (S08), crest groan (S09), servo whine and rising sub (S10)
  - the snap: crash with a falling low-pass, 48 Hz boom, real-time rotor whine; then 0.5 s of silence
  - sea, drone hum and helicopter thump, and a 55/110 Hz title tone
  - the VO is ducked into the bed with a soft limiter, peaking at −1 dBFS
- **Voiceover:** the script and cues are final. The recorded voice is a placeholder (see section 7).

## 6. Deliverables

See `00_admin/CHECKLIST.md` for status. Files are in `10_deliverables/`: main film, 15 s 9:16 social cut, 6 s teaser, 3 posters (2400×3600), 25 s research explainer, 3 LinkedIn creatives (1080×1350).

## 7. Known limitations

- **Voiceover is a placeholder.** ElevenLabs credits ran out (10 left; 380 needed). The narration is a Windows SAPI voice, pitched and EQ'd. To replace it, put the real take as `08_audio/vo/final/V01..V10.wav` (one line per file, the cues in `story.py`), then run `sound.py --vo final --out BHC_mix_v002` and `assemble.py`.
- **The person is a stylized proxy** (skin-modifier body, no face, by design). It reads at the planned framings but would not hold a close-up.
- **The breaking wave is a steepened Gerstner with whitewater, not a fluid simulation.** It sells the instant, but a true plunging barrel would need FLIP simulation, which is not feasible on a 4 GB GPU in 24 h.
- **The TII logo lockup is not included;** space is reserved on the end card for the official asset.

## 8. Reproduce

```bash
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 -P 05_scripts/shots/shots.py -- --shot S05 --anim --pct 100 --samples 48 --ver f001 --out finals
```

```bash
python 05_scripts/run_shots.py --shots S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 --anim --ver f001 --out finals --pct 100 --samples 48
```

```bash
"C:/Program Files/Blender Foundation/Blender 5.2/5.2/python/bin/python.exe" 05_scripts/edit/sound.py --vo scratch --out BHC_mix_v001
```

```bash
python 05_scripts/edit/assemble.py --src finals --mix BHC_mix_v001 --out 10_deliverables/main_16x9/BHC_main_16x9_v001.mp4 --crf 14
```
