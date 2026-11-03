# BEYOND HUMAN CONTROL — Production Document

TII · Autonomous Robotics Research Center (ARRC) · Concept: **300 MILLISECONDS**
Sprint start: 2026-11-03 · Delivery: 2026-11-04 · Status: **Production**

---

## 1. Locked decisions (approved by director, 2026-11-03)

| Item | Decision |
|---|---|
| Organization | Technology Innovation Institute (TII) |
| Center | Autonomous Robotics Research Center (ARRC) |
| Title | BEYOND HUMAN CONTROL |
| Concept | 300 MILLISECONDS: beyond human speed |
| Main film | 50 s, 16:9, 1920×1080, 24 fps |
| Setting | Arabian Gulf at night, shamal wind |
| Story | A mixed autonomous swarm coordinates a search-and-rescue decision |
| Style | Photorealistic, cinematic, restrained, technically grounded |
| Human indicator | Visible orange life jacket; no faces, no complex human animation |
| Exclusions | No humanoids, no military look, no generic futuristic HUDs, no capability claims beyond ARRC's public research |
| Renderer | EEVEE primary; Blender 5.2, headless Python (no MCP connected) |

## 2. Production rules (set by Claude under sprint autonomy)

1. **Orange means human.** Saturated orange appears only on the life jacket. Robots are white, grey and graphite with silver retroreflective tape.
2. **Each camera move follows how information travels:** robot to robot, or sensor to subject. No decorative orbits.
3. **Typography only:** a persistent timecode plus at most one data line at a time. Small monospace, bottom-left. No boxes, reticles, scan lines or glowing UI.
4. **Real light conventions.** Port red, starboard green, white masthead and stern lights, an amber flashing light marking the autonomous vessel, and a white anti-collision strobe on the drones.
5. **No faces.** The person is the jacket, a static silhouette from below, and the jacket's light.
6. **Physics sets the motion** (section 3). Nothing moves faster than the time scale allows.

## 3. Time model and physics bible

- The frozen section runs from film 0:00 to 0:41 (984 frames) and covers **0.300 s** of real time, a slowdown of **136.7×**. The snap to real time happens at **frame 985**.
- `real_time(frame) = (frame-1)/24/136.67` up to frame 984. After that, real time = 0.300 + seconds since the snap.

| Phenomenon | Real | On screen at 137× |
|---|---|---|
| Drone rotor, 8,000 rpm | 133 rev/s | ~1 rev/s (blades visible) |
| Wave crest (λ 36 m, c ≈ 7.5 m/s) | advances 2.25 m during the decision | ~5.5 cm/s creep |
| Sonar in water, 1,500 m/s | — | ~11 m/s expanding shell |
| Spray droplets, 5–12 m/s | — | 4–9 cm/s drift |
| A droplet falling from the capsized keel (0.44 m) | lands at exactly 0.300 s | the hidden clock in S09/S10, paying off at the snap |
| Radio message round (~25 ms incl. processing) | — | one exchange every ~3.4 s, which sets the cut rhythm |

## 4. Final script and voiceover

**Voice:** a female voice, mid-30s to 40s, low register, unhurried. International English with a light Gulf Arabic inflection. Close-miked, dry, no reverb. She delivers like a flight-safety investigator reading a finding, not a trailer narrator. A female voice also avoids the deep-male-trailer cliché.

| # | In | Line |
|---|---|---|
| V1 | 0:01.5 | Three hundred milliseconds. |
| V2 | 0:05.5 | About the time it takes you to blink. |
| V3 | 0:10.0 | Four machines see the same moment. |
| V4 | 0:21.0 | None of them sees all of it. |
| V5 | 0:25.5 | So they tell each other what they know… |
| V6 | 0:29.5 | …and how sure they are. |
| V7 | 0:32.5 | The obvious choice is the closest machine. |
| V8 | 0:37.0 | The wave makes it the wrong one. |
| — | 0:41–0:44 | *(no voice: the snap)* |
| V9 | 0:44.5 | No one could decide this fast. |
| V10 | 0:47.5 | So we spend years deciding how they should. |

62 words, about 28 s of speech in a 50 s film.

**On-screen text** (IBM Plex Mono, OFL, ~1.6% of frame height, 70% white):

- Timecode, persistent bottom-left, 0:00–0:44: `21:47:03.000`, ticking to `.300` at 0:41, then racing in real time. S12 shows `21:47:14` after the time cut.
- S02 `Arabian Gulf · 41 km offshore · wind NW 24 kn`
- S03 `UAV-1 · camera · person not visible · spray`
- S04 `USV-1 · radar · breaking crest 3.1 m · no return from person`
- S05 `AUV-1 · sonar · contact 6.2 m · bearing 041°`
- S07 `UAV-2 · relay · 3 reports received`
- S08 `fused estimate · person · confidence 0.94`
- S09 `USV-1 · bid 0.41 · withdrawn · wave impact risk`
- S10 `UAV-1 · light and track · assigned`
- S12 `decision time · 0.300 s`

**End card (0:47–0:50):** BEYOND HUMAN CONTROL / Technology Innovation Institute · Autonomous Robotics Research Center. Small line: *Dramatization inspired by ARRC's public research in perception, communication, decision-making and swarm coordination.* Reserve space for TII's official logo lockup (supplied by TII; never redrawn).

## 5. Storyboard: 12 shots

Film frames are 1-based at 24 fps. "Real t" is seconds after 21:47:03.000.

| Shot | Time | Frames | Real t | Shot / lens | Action and camera | Text | VO | Sound |
|---|---|---|---|---|---|---|---|---|
| **S01 Spray** | 0:00–0:05 | 1–120 | .000–.037 | ECU macro, 50 mm, f/2 | Fade from black. Camera drifts 0.3 m forward through a curtain of suspended droplets lit hard from above. Amber bokeh deep behind. Realization: nothing is falling. | timecode in at 0:03 | V1 | One wave crash stretched into a sub-bass tide; glassy droplet ticks |
| **S02 The Wave** | 0:05–0:09 | 121–216 | .037–.066 | Wide, 24 mm, low at the waterline | Geography. A 3 m crest leans over the orange jacket. The searchlight cone falls through mist. USV mast lights peek over the crest. Capsized hull downwave. Slow 0.5 m crane up. | location line | V2 | Stretched wind roar; distant rotor pulse at 1 Hz |
| **S03 UAV-1 sees** | 0:09–0:13 | 217–312 | .066–.095 | MCU, 35 mm, beside the drone | Rotors turn about once a second. Spray hangs in front of the gimbal lens; focus pulls from the lens to the droplets blocking it. | S03 line | V3 | Close rotor pulse; servo hum; tick on the text |
| **S04 USV-1 sees** | 0:13–0:16 | 313–384 | .095–.117 | MW, 28 mm, off the bow | The USV sits angled on the back of the crest; the radar bar is nearly still. Salt spray hangs around the antennas. | S04 line | — | Hull groan; radar sweep as a slow filtered breath |
| **S05 AUV-1 hears** | 0:16–0:20 | 385–480 | .117–.146 | Wide underwater, 20 mm, looking up | Green-black water with suspended particles. Above: the jacket and dangling legs silhouetted against the surface glow. A sonar shell crosses the frame at walking pace. | S05 line | — | Pressure, muffled air world; a stretched sonar ping |
| **S06 Waterline** | 0:20–0:25 | 481–600 | .146–.183 | Split dome-port, 24 mm | The only complete view, which no single machine has. Top half: jacket, crest, beam. Bottom half: legs, AUV light far below. Slow push. | — | V4 | Dome-port mix: air on top, water below; the ping passes |
| **S07 Relay** | 0:25–0:29 | 601–696 | .183–.212 | High wide, 35 mm, from UAV-2 at 35 m | The whole scene from above: crest line, USV, jacket, beam. UAV-2's strobe fires (the message leaves); camera pushes down along the message path. | S07 line | V5 | One dry click per message; high rotor |
| **S08 Confidence** | 0:29–0:32 | 697–768 | .212–.234 | CU, 50 mm, USV mast | The amber autonomy light and antenna array, with droplets on the whip antenna. The light catches the suspended spray. | S08 line | V6 | Click; a soft tone resolving upward as estimates fuse |
| **S09 The obvious choice** | 0:32–0:36 | 769–864 | .234–.263 | Low wide, 28 mm, at the surface | USV in the foreground, crest above it, jacket ahead. The geometry makes the danger readable. A droplet hangs from the capsized keel. | S09 line | V7 | Crest stress groan; withdrawn click |
| **S10 Assigned** | 0:36–0:41 | 865–984 | .263–.300 | Over UAV-1, 35 mm, looking down | The searchlight gimbal swings; the beam slides across the water onto the orange jacket. The keel droplet nears the surface. | S10 line | V8 | Slowed servo whine; rising sub; assigned click |
| **S11 The Snap** | 0:41–0:44 | 985–1056 | real time | Handheld, 24 mm, 180° shutter | Real time. The crest breaks; white water fills the frame; the USV veers down-drift; the beam holds. 2.5 s, then a hard cut to black for 0.5 s. | timecode races | — | Everything at once at full volume, then silence |
| **S12 Aftermath + title** | 0:44–0:50 | 1057–1200 | real, 21:47:14 | Locked wide, 50 mm | Calmer water. UAV-1 holds the jacket in a pool of white light; the USV waits down-drift. A distant helicopter searchlight approaches through haze. Fade to the end card at 0:47. | S12 line, end card | V9, V10 | Real sea; distant helicopter; one low tone under the title |

## 6. Scene geography (world metres; the wave travels +X)

| Element | Position at t=0 | Notes |
|---|---|---|
| Hero crest line | x = 0, along Y | Gerstner λ 36 m, height ~2.8–3.1 m, steep front face toward +X |
| Life jacket and person | (3.5, 0) | At the foot of the front face |
| USV-1 | (-6, -5), bow toward +X | Behind the crest; the closest machine, and the wrong one |
| UAV-1 | (3, 2, 9) | Searchlight, initially aimed 3 m off the person |
| UAV-2 | (-10, 12, 35) | Relay, white strobe |
| AUV-1 | (8, 3, -5) | Facing the person, bearing 041° |
| Capsized hull | (12, -6) | Overturned 6 m fishing boat; its keel drips |
| Coast glow | azimuth +Y/-X horizon | Warm sodium haze from the distant coast |
| Helicopter (S12) | (400, 300, 80) | A light only |

## 7. Asset list

| ID | Asset | Build | Shots |
|---|---|---|---|
| ENV-01 | Night Gulf surface: Ocean modifier (FFT chop) plus a Geometry Nodes Gerstner hero wave, foam attributes, a closed water body | Procedural | all |
| ENV-02 | Underwater: the water-body volume (absorption plus scatter), surface underside, seabed at -22 m | Procedural | S05, S06 |
| ENV-03 | Sky: overcast night, horizon coast glow, moon behind cloud (sun light), world fog | Procedural | all |
| FX-01 | Spray droplets: Geometry Nodes, ballistic and driven by real time (scrubbable, no simulation) | GN | S01–S04, S06–S11 |
| FX-02 | Crest mist: a noise-shaped volume hugging the crest | Volume | S02, S04, S07, S09 |
| FX-03 | Underwater particulates | GN | S05, S06 |
| FX-04 | Sonar pressure shell, expanding at the scaled speed of sound | GN/shader | S05, S06 |
| FX-05 | Breaking white water (real time) | Procedural plus comp | S11 |
| FX-06 | Helicopter searchlight | Light | S12 |
| RB-01 | UAV chassis (1.2 m quad, two-blade props). Variant a: UAV-1 searchlight gimbal. Variant b: UAV-2 relay mast and strobe | Procedural hard-surface | S01–S03, S07, S10–S12 |
| RB-02 | USV-1: 7.5 m uncrewed RHIB-type hull, grey collar, sensor mast, radar bar, nav lights | Procedural | S02, S04, S07–S09, S11, S12 |
| RB-03 | AUV-1: 1.9 m torpedo AUV with shrouded thruster, fins, forward light | Procedural (lathe) | S05, S06 |
| PR-01 | Life jacket: inflatable yoke in SOLAS orange with retroreflective patches and a white light | Procedural | S02, S05, S06, S09, S10, S12 |
| PR-02 | Person silhouette: static skin-modifier proxy, dark clothing, no face | Procedural | S05, S06 |
| PR-03 | Capsized fishing boat, 6 m, overturned and dripping | Procedural (shares the hull loft with RB-02) | S02, S09, S10, S12 |
| GFX-01 | Timecode and data lines | Comp / edit | all |
| GFX-02 | End card | Comp / edit | S12 |

## 8. Reuse map

- **One master layout** (`bhc.layout.build_master`) builds every element at the coordinates above. Each shot script only adds its camera, render settings and frame range, so every shot shares the same geometry and lighting.
- **Surface mode** (ENV-01 + ENV-03): S01, S02, S03, S04, S07, S08, S09, S10, S11, S12.
- **Underwater mode** (ENV-02 on): S05, and S06 (both modes at once).
- **Frozen-time reuse:** S03, S08 and S10 use the same frozen spray state as S02, with different cameras. The spray is a function of time, so there is nothing to re-simulate.
- **Campaign reuse:** posters come from S02, S06 and S10 frames re-rendered at 4K. The teaser is S01 + S11 + the end card. The vertical cut uses 9:16 cameras on S01, S06, S10, S11 and S12. The explainer is the S07 overhead plate frozen under motion-graphics overlays.

## 9. Render plan

| Pass | Resolution | EEVEE samples | Target |
|---|---|---|---|
| Test frames | 1920×1080 | 64 | quality and time check |
| Previews | 960×540 | 16 | layout and timing for every shot |
| Finals | 1920×1080 | 64–128 | ≤ 30 s per frame, ~10 h for 1,200 frames |
| Posters | 3840×2160 | 256 | 3 stills |
| Vertical | 1080×1920 | 64 | ~360 frames |

Finals render as 16-bit PNG sequences to `06_renders/finals/Sxx/`. The grade and typography happen in the edit. Encodes: H.264 for review, ProRes 422 HQ for the master.

## 10. Campaign derivation

| Deliverable | Build |
|---|---|
| Social cut, 15 s, 9:16 | S01 (2 s) → S06 (3 s) → S10 (3 s) → S11 (2 s) → S12 + title (5 s); VO V1, V4, V9, V10 |
| Teaser, 6 s | S01 with timecode `.000` (3 s) → snap S11 (1.5 s) → title + `0.300 s` (1.5 s) |
| Posters ×3 | "The Instant" (S02) · "Waterline" (S06) · "Assigned" (S10) |
| Research explainer, 25 s | S07 overhead plate frozen; motion graphics show four partial views, the message exchange, the auction bids and the assignment; tied to ARRC's four research areas |
| LinkedIn ×3 | The poster frames with one line each: "0.300 s" · "Four machines. One picture." · "The closest machine is not always the right one." |

## 11. Technical log (test frames, 2026-11-03)

**Pipeline.** Blender 5.2.3 runs headless with `--factory-startup`. The scene is fully procedural and rebuilt from `05_scripts/bhc/` on every run. Each shot script saves a versioned `.blend` to `04_scenes/` before rendering.

**Render settings (finals).**
- EEVEE, 1920×1080, 64 TAA samples
- Screen-space ray tracing
- Volumetrics: 4 px tiles, 64 slices, end 220 m, volumetric shadows on
- AgX, Medium High Contrast look, exposure +1.8
- Compositor bloom
- 16-bit PNG output

**Measured render times.** S02: 7.0 s/frame. S06: 15.3 s/frame, because it renders two passes and composites them. Projected main-film render: about 3–4 h.

| Finding | Fix |
|---|---|
| A world volume turns the sky fully black (EEVEE treats it as infinite) | Air fog is a mesh volume box with height falloff |
| A volume on the wavy ocean mesh caused diagonal striping in the air, including the sky | Ocean is surface-only; underwater murk is a separate box, shown only in underwater passes |
| Ocean mesh was flat-shaded, so faceted rectangles showed at grazing angles | Ocean mesh is smooth-shaded |
| FFT wavelengths shorter than the 0.35 m grid aliased into striations | `wave_scale_min` = 0.9 m; fine ripples come from two bump octaves in the shader |
| Dark gradients band once reduced to 8-bit (the 16-bit data is smooth: 678 levels over 700 px) | **Grain/dither is mandatory in the grade** before any 8-bit encode |
| A pinhole camera cannot see above and below water at once | S06 renders lens +3 cm and −3 cm passes, composited with a meniscus line (dome-port method) |
| Foam stretched into smoke at the dome port (one grid quad covers hundreds of px) | Foam is suppressed inside the flattened dome-port zone (`flat_w` attribute) |
| A 36 m swell read as a horizon line | Hero wave changed to λ 26 m, A 1.7 m, sharpness 0.82, lean 1.8 m: a near-vertical front face, checked so the mesh does not fold |
| Transmissive droplets rendered as dark specks (EEVEE refracts the dark night probe) | Droplets are translucent + glossy + 40 % transparent |
| The collar hid the head from behind, so the person read as a buoy | Head raised, collar reduced, person turned three-quarters to camera (heading 120°) |

**Open look issues (next pass).**
- The crest lip has no visible whitewater or spray sheet.
- The crest mist barely reads.
- Out-of-focus droplets near the lens read slightly as snow.
- Underwater particulates are too small.
- The sonar shell is not built.
- The USV console needs detail before its hero shots (S04, S08).

## 12. Decision log

| Date | Decision | By |
|---|---|---|
| 2026-11-03 | Concept A locked; 50 s; Gulf at night; SAR swarm | Director |
| 2026-11-03 | Blender MCP not connected; headless Python scripts in `05_scripts/` (versioned) | Claude, per brief fallback |
| 2026-11-03 | Orange reserved for the human; robots in white/grey/graphite | Claude |
| 2026-11-03 | Slowdown 136.7× (0.300 s over 41 s); snap at frame 985 | Claude |
| 2026-11-03 | Droplet clock moved from the swimmer's hand to the capsized keel, to avoid human animation | Claude |
| 2026-11-03 | Female low-register VO; no music score; sound design is the score | Claude |
| 2026-11-03 | Hero wave λ 26 m (was 36 m) so the crest reads as about to break | Claude |
| 2026-11-03 | S06 waterline made with a two-pass dome-port composite | Claude |
| 2026-11-03 | Film grain/dither is part of the grade, not optional | Claude |
| 2026-11-03 | S02 camera: low at the foot of the face, 18 mm, (6.3, 1.4) → crest lip | Claude |
| 2026-11-04 | Story timeline as shared data (`bhc/story.py`): one source for status-light pulses, clicks, pings, VO cues and data lines | Claude |
| 2026-11-04 | Information is shown only by physical cues: amber status LEDs pulse on each message, the relay drone's strobe fires, sonar fronts make suspended particles glint. A geometric sonar shell was tried and removed because it read as a HUD circle | Claude |
| 2026-11-04 | Whitewater: fine froth on the very lip, broken by noise; it spreads down the face only after the snap. Large clumps read as rocks | Claude |
| 2026-11-04 | Breaking: after 0.300 s the lip pitches forward (+35 % lean) and the wave loses 42 % of its height over 1.6 s; spray rate and speed rise | Claude |
| 2026-11-04 | S12 is a time cut to 21:47:14: the wave has passed, UAV-1 holds the jacket in light, USV-1 waits down-drift, and a helicopter searchlight approaches from the coast side (lights only) | Claude |
| 2026-11-04 | The keel-droplet clock is not in the 12-shot cut (too small to read at any planned framing); the timecode carries the clock | Claude |
| 2026-11-04 | ElevenLabs credits ran out (10 left, 380 needed). The film carries a processed SAPI scratch VO (pitched −2.6 st, EQ, compression). **It must be replaced before release**; swap the WAVs in `08_audio/vo/final/` and rebuild with `sound.py --vo final` | Claude |
| 2026-11-04 | Project moved from the session scratch folder to `Desktop/BEYOND-HUMAN-CONTROL` and pushed to GitHub; render frames and .blend files are git-ignored (disk: 15 GB free) | Claude |
