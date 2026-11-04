# BEYOND HUMAN CONTROL — Deliverables Checklist

Updated 2026-11-04 04:30 · Legend: ✅ done · 🟡 done with a known placeholder · ⬜ not started
Videos: GitHub release **v1.0** (https://github.com/bilal-feroz/BEYOND-HUMAN-CONTROL/releases/tag/v1.0) · Images: `10_deliverables/`

## Deliverables (non-negotiable)

| # | Deliverable | Status | File(s) |
|---|---|---|---|
| D1 | Main film, 50 s, 16:9, 1920×1080, 24 fps | ✅ | `BHC_main_16x9_v001_web.mp4` (10 Mbps) · `BHC_main_16x9_v001.mp4` (crf 16 master) |
| D2 | Social cut, 15 s, 9:16, 1080×1920 | ✅ | `BHC_social_15s_9x16_v001_web.mp4` · `…_v001.mp4` (S01 → S06 → S10 → S11 → S12 + title; native vertical renders) |
| D3 | Teaser, 6 s | ✅ | `BHC_teaser_6s_v001_web.mp4` · `…_v001.mp4` (frozen spray → snap → title + "0.300 s") |
| D4 | Posters ×3, 2400×3600 | ✅ | `posters/BHC_P1_the_instant`, `BHC_P2_waterline`, `BHC_P3_assigned` (.png + .jpg) |
| D5 | Research explainer, 25 s | ✅ | `BHC_explainer_25s_v001_web.mp4`: perception, communication, decision, action over the overhead plate, with labels on projected robot positions |
| D6 | LinkedIn creatives ×3, 1080×1350 | ✅ | `linkedin/BHC_LinkedIn_L1` "0.300 s" · `L2` "Four machines. One picture." · `L3` "The closest machine is not always the right one." |
| D7 | Original voiceover | 🟡 | Script and cues final. **The recorded voice is a placeholder** (processed Windows SAPI). ElevenLabs credits ran out (10 left, 380 needed). Replace `08_audio/vo/final/V01..V10.wav` and rebuild |
| D8 | Original sound design | ✅ | `edit/sound.py`, synthesized from the story timeline; mix `08_audio/mix/BHC_mix_v001.wav` |
| D9 | Production breakdown | ✅ | `11_docs/PRODUCTION_BREAKDOWN.md` + `00_admin/PRODUCTION_DOCUMENT.md`, `REVIEW_NOTES.md`, `RENDER_LOG.md` |

## Stage 2: pre-production
- ✅ Final script and VO, 12-shot storyboard, geography, asset list, reuse map, render plan, campaign derivation
- ✅ Production folder structure

## Stage 3: production
- ✅ Environment: FFT ocean + Gerstner hero wave with breaking, fog, crest mist, lip whitewater, underwater murk
- ✅ FX: steady-state spray, mist, sonar fronts on particulates, status-light message pulses, helicopter searchlight
- ✅ Assets: UAV-1/UAV-2, USV-1 (detailed console, hull ID), AUV-1, life jacket + person proxy, capsized hull
- ✅ 12 shot scripts on one master layout (`05_scripts/shots/shots.py`)
- ✅ 12 previews (`09_edit/previews/*.mp4`) → animatic v001 → review → fixes verified on check frames
- ✅ Finals: 1,200 frames, 1080p EEVEE, 40 samples; 3.8 h machine time over two parallel chains
- ✅ Campaign renders: 412 native 9:16 frames, 3 poster stills at 2400×3600

## Stage 4: post
- ✅ Animatic v001 (`09_edit/BHC_animatic_v001.mp4`)
- ✅ Grade: grain before the 8-bit conversion (no banding), vignette, fades, hard black after the snap
- ✅ Typography: frame-accurate clock, 11 data lines, end card (Consolas / Bahnschrift via libass)
- ✅ Sound design and mix; 🟡 VO placeholder
- ✅ Master + web encodes; GitHub release v1.0

## Known follow-ups
1. **Record or generate the real voiceover** (top up ElevenLabs: about 380 credits for one take of the full script with voice "Cherine Hani – Warm Storyteller", or book a human VO). Then run `sound.py --vo final --out BHC_mix_v002` and `assemble.py --src finals --mix BHC_mix_v002 --out 10_deliverables/main_16x9/BHC_main_16x9_v002.mp4 --crf 16`, and rebuild teaser and social with `campaign.py`.
2. Insert TII's official logo lockup on the end card and posters (space reserved; never redrawn).
3. Optional polish: a true plunging-barrel lip (FLIP simulation) and a sculpted person for any close-up use.
