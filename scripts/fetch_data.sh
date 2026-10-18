#!/usr/bin/env bash
# Download the Liber Primus transcription (relikd/LiberPrayground) into data/ (gitignored).
# Usage: bash scripts/fetch_data.sh        (safe to re-run; skips files already present)
set -euo pipefail
cd "$(dirname "$0")/.."
Base="https://raw.githubusercontent.com/relikd/LiberPrayground/main"
mkdir -p data/pages data/texts
Pages="p0-2 p3-7 p8-14 p15-22 p23-26 p27-32 p33-39 p40-53 p54-55
0_warning 0_welcome 0_wisdom 0_koan_1 0_loss_of_divinity p56_an_end p57_parable jpg107-167 jpg229
solved_0_warning solved_0_welcome solved_0_wisdom solved_0_koan_1 solved_0_loss_of_divinity
solved_p56_an_end solved_p57_parable solved_jpg107-167 solved_jpg229"
Fetch() {
  local Url="$1" Out="$2" Try
  [ -s "$Out" ] && return 0
  for Try in 1 2 3 4; do
    if curl -fsSL --retry 2 -o "$Out.part" "$Url"; then mv "$Out.part" "$Out"; return 0; fi
    sleep $((2 ** Try))
  done
  echo "FAILED: $Url" >&2; return 1
}
for Name in $Pages; do Fetch "$Base/pages/$Name.txt" "data/pages/$Name.txt"; done
Fetch "$Base/data/baseline-rune-words.txt" "data/baseline-rune-words.txt"
# Independent transcription with explicit page (%) and line (/) markers (scripts/crosscheck_rtkd.py)
mkdir -p data/rtkd
Fetch "https://raw.githubusercontent.com/rtkd/iddqd/master/liber-primus__transcription--master/liber-primus__transcription--master.txt" "data/rtkd/transcription.txt"
echo "data/: $(ls data/pages | wc -l) page files, baseline $(wc -l < data/baseline-rune-words.txt) words"
