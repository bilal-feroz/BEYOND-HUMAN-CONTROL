#!/usr/bin/env bash
# Campaign renders from the same scenes: 9:16 shots for the social cut (frame ranges from
# edit/campaign.py SOCIAL) and three 2400x3600 poster stills. S11 vertical runs after the S11 final.
cd "$(dirname "$0")/.."
V="--anim --ver v001 --out vertical --pct 100 --samples 32 --quality final --res 1080x1920 --depth 8 --note vertical"
python 05_scripts/run_shots.py --shots S01 $V --start 29 --end 76
python 05_scripts/run_shots.py --shots S06 $V --start 500 --end 559
python 05_scripts/run_shots.py --shots S10 $V --start 889 --end 950
python 05_scripts/run_shots.py --shots S12 $V --start 1057 --end 1195
P="--ver post --out posters --pct 100 --samples 96 --quality final --res 2400x3600 --note poster"
python 05_scripts/run_shots.py --shots S02 $P --frames 168
python 05_scripts/run_shots.py --shots S06 $P --frames 540
python 05_scripts/run_shots.py --shots S10 $P --frames 980
echo "CAMPAIGN RENDERS DONE"
