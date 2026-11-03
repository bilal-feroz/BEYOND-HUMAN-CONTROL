# BEYOND HUMAN CONTROL

A 50-second cinematic film, **300 MILLISECONDS**, inspired by the public research areas of the Technology Innovation Institute's Autonomous Robotics Research Center (ARRC).

At night, in a shamal on the Arabian Gulf, a mixed robot swarm (two drones, an uncrewed surface vessel and an underwater vehicle) makes one search-and-rescue decision in 0.300 s. The film slows that third of a second to 41 seconds, so the only things moving fast are information.

> A dramatization. It does not claim that TII has developed any capability shown.

## Where things are

| Folder | Contents |
|---|---|
| `00_admin/` | Production document (all approved decisions), deliverables checklist, render log |
| `05_scripts/bhc/` | Procedural Blender 5.2 library: time model, ocean and hero wave, fog, spray, sonar, robots, layout and choreography |
| `05_scripts/shots/shots.py` | All 12 shots on one shared master layout |
| `05_scripts/run_shots.py` | Renders shots headless and logs every run |
| `05_scripts/edit/` | Animatic and film assembly: VO placement, sound design, typography, grade |
| `06_renders/` | Test frames (JPG); render frames are local only (git-ignored) |
| `09_edit/`, `10_deliverables/` | Animatic and final deliverables |

## Rebuild a shot

```bash
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 -P 05_scripts/shots/shots.py -- --shot S02 --anim --pct 50 --samples 12 --ver p001 --out previews
```

Everything is generated from code: no external assets, and no simulation caches.
