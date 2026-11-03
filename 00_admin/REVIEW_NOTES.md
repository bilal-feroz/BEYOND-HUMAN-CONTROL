# Preview / animatic review notes

Shot-by-shot notes from the half-res previews (p001), written as each shot landed. "FINAL" marks a fix
that goes into the full-resolution render; "OK" means no change.

| Shot | Verdict | Notes |
|---|---|---|
| S01 | OK, minor | Spray drifts visibly (~13 cm/40 frames at the lens); USV mast and amber light bokeh behind. Droplets read more as dust than glass beads. FINAL: none required. |
| S03 | OK | Push-and-arc round UAV-1; blades visibly turning; nav lights; searchlight housing glows; reads as industrial hardware. |
| S11 | FAILED, fixed | GPU out of memory at frame 998: ~2M whitewater instances right after the snap. Capped (peak ~290k, then 12–30k). Re-render alone. |
| S12 | Fix | Real-time swell, jacket in its light pool, vessel standing by, beam column from the drone. FINAL: the jacket sits on the bottom edge, so tilt down; the vessel is too close and dominant, so move it to (11.5, 7); the helicopter doesn't read, so fly it lower (15–18 m) so its beam crosses the dense low haze; the haze is muddy brown, so desaturate the coast glow globally. |
| S05 | Fix | AUV foreground, its light up to the silhouetted person; the sonar front reads as a sweep of glinting sediment (subtle, physical); echo pulse follows. FINAL: the capsized hull's underside reads as a big slab top-right, so frame left; the AUV beam is blocky only at preview volume settings. |
| S02 | Fix (minor) | The crane rise reveals the person in the beam pool under the crest. Checkered fog is preview sampling only. FINAL: start the crane 12 cm higher so chop never clips the lens. |
| S07 | OK | Relay overview: the strobe fires on the message (f614), the camera descends past UAV-2 along the message path, and the layout reads from above (beam pool with the jacket, vessel, capsized hull, crest foam). |
| S04 | Fix | Vessel reads (mast, radar, nav and amber lights, collar), crest behind with lip whitewater. FINAL: the camera is nearly dead astern and the flat transom dominates, so move to the aft quarter (-9, -12.6) for the hull profile with the crest beyond. |
| S09 | REDESIGN | Fails: the vessel is cut off at the left edge, the person is hidden behind the near swell, and the decision geometry doesn't read. FINAL: elevated oblique (6 m) across the crest: vessel left on the back slope (amber bid/withdraw pulses), lip centre, person right in the beam pool. Verify with a check frame before finals. |
| S11 | Fix | The story reads: jacket in the light pool → the dark wall of the crest swallows the frame (handheld, motion blur) → the jacket reappears in its light, vessel turning away. Strong ending frame. FINAL: post-break foam clumps read as brown rocks on a white sheet, so after the break the foam is shader-only and patchier. |
| S06 | Fix | The dome-port split works: person above, sea-smoke, beam reflection. But the legs vanished underwater: the darker night murk left dark legs in dark water. FINAL: underwater scatter lifted part-way (0.13/0.26/0.21, density 0.15) and the AUV light raised to 1,600 W so the legs silhouette against the glow. Checker in the murk is preview sampling only. |
| S08 | Fix (minor) | Works: the amber light on its bracket pulses bright on the fused estimate (f716), lighting the mast, GNSS pucks and EO/IR ball. FINAL: idle amber reads white, so rest emission 12 → 3.5; light spheres faceted, so 24 segments. |
| S10 | OK | The searchlight slews across the water and settles on the jacket by 40.6 s ("assigned"); top-down over the drone, props turning. |

## Animatic v001 review (09_edit/BHC_animatic_v001.mp4, 50.000 s, 960x540, 24 fps)

**Continuity.**
- Geography holds across every angle, because every shot is the same master layout: the crest along Y, the person at its foot, USV-1 behind the crest, UAV-1 above, UAV-2 high, AUV-1 below.
- The beam stays offset from the person until S10, then on it.
- One colour break: shots facing the coast glow (S09, S12) went brown, the others grey-silver. Fixed globally by desaturating the coast glow.

**Pacing.**
- Shots of 3–5 s on a 41 s slow-motion arc, then 2.5 s of real time, 0.5 s of black, 3 s of aftermath, and the end card.
- The slow section is deliberate and carried by the VO cadence and the message clicks. The cut rhythm follows the message events from S07 on.

**Clarity.**
- The person always reads (orange only).
- S09's decision geometry did not read and was redesigned as an elevated oblique (check frame verified).
- S06 lost the legs and was fixed (verified).
- S05, S04 and S12 were reframed (verified).

**The four capabilities, without HUD.**
1. PERCEPTION: each sensor is shown with what it can't resolve (S03 spray at the camera, S04 radar on the crest, S05 sonar front glinting through the water), each with one data line.
2. COMMUNICATION: the relay strobe fires; status lights pulse on every message (19 events, each with a click); the fused-confidence pulse in S08.
3. DECISION: in S09 the closest machine's amber light pulses as it bids, then again as it withdraws, with "wave impact risk" on screen and the crest above it explaining why; in S10 the beam slews and lands on "assigned".
4. ACTION: the beam holds through the snap (S11); USV-1 turns away; S12 holds the jacket in light as the helicopter comes in.

Read with the VO, all four are understandable on first viewing.

**Verdict:** approved for finals with the fixes above (all applied in code and verified on check frames where the framing changed).
