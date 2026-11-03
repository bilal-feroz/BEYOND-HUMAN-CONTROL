# BEYOND HUMAN CONTROL — Deliverables Checklist

Updated 2026-11-03 · Legend: ✅ done · 🟡 in progress · ⬜ not started

## Deliverables (non-negotiable)

| # | Deliverable | Status | Notes |
|---|---|---|---|
| D1 | Main film, 50 s, 16:9 | 🟡 | Environment and assets built; S02 and S06 test frames pass the technical review; 0/12 shots rendered |
| D2 | Social cut, 15 s, 9:16 | ⬜ | Re-renders S01, S06, S10, S11, S12 with 9:16 cameras |
| D3 | Teaser, 6 s | ⬜ | S01 + S11 snap + end card |
| D4 | Posters ×3 | ⬜ | Frames from S02, S06, S10 at 4K |
| D5 | Research explainer, 20–30 s | ⬜ | S07 plate plus motion graphics |
| D6 | LinkedIn creatives ×3 | ⬜ | Poster frames plus one line each |
| D7 | Original voiceover | 🟡 | Script final (62 words); voice not cast or recorded yet |
| D8 | Original sound design | ⬜ | Time-stretched single-second design; ElevenLabs SFX plus ffmpeg |
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
| FX-02 crest mist | 🟡 | Follows the crest line; still barely visible; needs a lip whitewater sheet |
| FX-03 underwater particulates | ✅ v1 | Too small to read yet |
| FX-04 sonar pressure shell | ⬜ | S05, S06 |
| FX-05 breaking white water (real time) | ⬜ | S11 |
| FX-06 helicopter searchlight | ⬜ | S12 |
| RB-01 UAV-1 / UAV-2 | ✅ v1 | Reviewed in `06_renders/tests/asset_review_v002.png` |
| RB-02 USV-1 | ✅ v1 | Bow fixed; console detail pass before S04 and S08 |
| RB-03 AUV-1 | ✅ v1 | |
| PR-01/02 life jacket + person | ✅ v1 | Reads as a person in S02 and S06; no face |
| PR-03 capsized hull | ✅ v1 | Keel droplet clock still to add (S09/S10) |
| Test frame S02 | ✅ | `06_renders/tests/S02_v009_f0168.png`, 7.0 s/frame |
| Test frame S06 | ✅ | `06_renders/tests/S06_v009_f0540.png`, 15.3 s/frame (two passes + composite) |
| Shot scripts S01, S03–S05, S07–S12 | ⬜ | |
| Preview pass, all shots (50 %, 16 smp) | ⬜ | |
| Final renders | ⬜ | ~3–4 h estimated |

## Stage 4: post

- ⬜ Assembly / animatic with temp VO
- ⬜ Typography (timecode + data lines, IBM Plex Mono)
- ⬜ Grade: grain/dither mandatory (8-bit banding in dark gradients otherwise)
- ⬜ VO record, sound design, mix
- ⬜ Master encode (ProRes 422 HQ + H.264)
