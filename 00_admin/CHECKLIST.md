# BEYOND HUMAN CONTROL — Deliverables Checklist

Updated 2026-11-03 · Legend: ✅ done · 🟡 in progress · ⬜ not started

## Deliverables (non-negotiable)

| # | Deliverable | Status | Notes |
|---|---|---|---|
| D1 | Main film, 50 s, 16:9 | 🟡 | 12 previews rendered and reviewed; animatic v001 assembled and reviewed; full-res finals rendering overnight |
| D2 | Social cut, 15 s, 9:16 | ⬜ | Re-renders S01, S06, S10, S11, S12 with 9:16 cameras |
| D3 | Teaser, 6 s | ⬜ | S01 + S11 snap + end card |
| D4 | Posters ×3 | ⬜ | Frames from S02, S06, S10 at 4K |
| D5 | Research explainer, 20–30 s | ⬜ | S07 plate plus motion graphics |
| D6 | LinkedIn creatives ×3 | ⬜ | Poster frames plus one line each |
| D7 | Original voiceover | 🟡 | Script final. ElevenLabs credits exhausted (10 left) → processed SAPI scratch VO in the mix; must be replaced before release |
| D8 | Original sound design | ✅ v1 | Synthesized from the story timeline (`edit/sound.py`): bed, rotors, message clicks, sonar, decision layers, snap, aftermath |
| D9 | Production breakdown | 🟡 | `00_admin/PRODUCTION_DOCUMENT.md` kept current |

## Stage 2: pre-production

- ✅ Final script and VO (`PRODUCTION_DOCUMENT.md` §4)
- ✅ 12-shot storyboard with timestamps, frames and real time (§5)
- ✅ Scene geography (§6), asset list (§7), reuse map (§8), render plan (§9), campaign derivation (§10)
- ✅ Production folder structure

## Stage 3: production

| Item | Status | Notes |
|---|---|---|
| ENV-01 ocean + hero wave | ✅ v1 | FFT chop + Gerstner crest (λ 26 m, ~3.0 m crest–trough, near-vertical face) |
| ENV-02 underwater | ✅ v1 | Separate murk volume; underwater pass only |
| ENV-03 sky, moon, fog | ✅ v1 | Mesh fog volume (a world volume blacks out the sky) |
| FX-01 spray / mist droplets | ✅ v1 | Closed-form ballistic, driven by real time |
| FX-02 crest mist + whitewater | ✅ | Mist follows the crest line; froth on the lip |
| FX-03 underwater particulates | ✅ v1 | Too small to read yet |
| FX-04 sonar pressure front | ✅ | Particles glint as the front passes (a geometric shell was cut: it read as a HUD) |
| FX-05 breaking white water (real time) | ✅ | Lip pitches, wave decays, shader foam spreads; instanced clumps capped (GPU) |
| FX-06 helicopter searchlight | ✅ | Lights only, approaching from the coast side |
| RB-01 UAV-1 / UAV-2 | ✅ v1 | Reviewed in `06_renders/tests/asset_review_v002.png` |
| RB-02 USV-1 | ✅ v2 | Pointed bow, console glass band, louvres, rails, lidar, EO/IR ball, deck hardware, hull ID, amber status light |
| RB-03 AUV-1 | ✅ v1 | |
| PR-01/02 life jacket + person | ✅ v1 | Reads as a person in S02 and S06; no face |
| PR-03 capsized hull | ✅ v1 | Keel droplet clock still to add (S09/S10) |
| Test frame S02 | ✅ | `06_renders/tests/S02_v009_f0168.png`, 7.0 s/frame |
| Test frame S06 | ✅ | `06_renders/tests/S06_v009_f0540.png`, 15.3 s/frame (two passes + composite) |
| Shot scripts S01–S12 | ✅ | `05_scripts/shots/shots.py` on one master layout |
| Preview pass, all 12 shots (50 %, 8 smp) | ✅ | `09_edit/previews/Sxx_p001.mp4`; S11 crashed once (GPU), fixed and re-rendered |
| Final renders (100 %, 40 smp) | 🟡 | Running overnight: two chains + S11 alone; logged in RENDER_LOG.md |

## Stage 4: post

- ✅ Animatic v001 with scratch VO and placeholder sound design (`09_edit/BHC_animatic_v001.mp4`), reviewed in `REVIEW_NOTES.md`
- ✅ Typography: frame-accurate clock, 11 data lines, end card (ASS via libass; Consolas / Bahnschrift)
- ⬜ Grade: grain/dither mandatory (8-bit banding in dark gradients otherwise)
- ⬜ VO record, sound design, mix
- ⬜ Master encode (ProRes 422 HQ + H.264)
