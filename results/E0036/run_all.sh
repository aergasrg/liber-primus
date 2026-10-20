#!/usr/bin/env bash
# E0036 full run, resumable: each stage checkpoints (real_<title>.json, power.jsonl, null.jsonl).
set -e
cd "$(dirname "$0")/../.."
python3 experiments/E0036_title_cribs.py real
python3 experiments/E0036_title_cribs.py power --plants 100
python3 experiments/E0036_title_cribs.py null --reps 50
python3 experiments/E0036_title_cribs.py report
