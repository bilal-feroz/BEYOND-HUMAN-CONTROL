#!/usr/bin/env bash
# Overnight finals: two chains in parallel, then S11 alone (heaviest: break + motion blur).
cd "$(dirname "$0")/.."
A="--anim --ver f001 --out finals --pct 100 --samples 40 --quality final --note final"
python 05_scripts/run_shots.py --shots S01 S02 S03 S04 S05 S06 $A > 06_renders/finals_chainA.txt 2>&1 &
sleep 30
python 05_scripts/run_shots.py --shots S07 S08 S09 S10 S12 $A > 06_renders/finals_chainB.txt 2>&1 &
wait
python 05_scripts/run_shots.py --shots S11 $A > 06_renders/finals_S11.txt 2>&1
echo "FINALS DONE"
cat 06_renders/finals_chainA.txt 06_renders/finals_chainB.txt 06_renders/finals_S11.txt
