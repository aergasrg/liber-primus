#!/usr/bin/env bash
# Download the running-key sources re-run by B01 (ledger E0008, E0012, E0024) into data/ (gitignored).
# Public-domain texts go in data/texts/, Cicada files in data/keyfiles/. Safe to re-run.
# Usage: bash scripts/fetch_keysources.sh [--images]   (--images also fetches the 75 LP page jpgs, ~25 MB)
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/texts data/keyfiles/cicados data/keyfiles/lp-images
Fetch() {
  local Url="$1" Out="$2" Try
  [ -s "$Out" ] && return 0
  for Try in 1 2 3 4; do
    if curl -fsSL --retry 2 -o "$Out.part" "$Url"; then mv "$Out.part" "$Out"; return 0; fi
    sleep $((2 ** Try))
  done
  echo "FAILED: $Url" >&2; return 1
}
# Emerson, Essays First Series (contains Self-Reliance); Lady Charlotte Guest, The Mabinogion
Fetch "https://www.gutenberg.org/cache/epub/2944/pg2944.txt" "data/texts/emerson_essays1.txt"
Fetch "https://www.gutenberg.org/cache/epub/5160/pg5160.txt" "data/texts/mabinogion.txt"
# B03: public-domain Cicada texts (Blake, Marriage of Heaven and Hell; Liber AL vel Legis and the 1911 Britannica "Cicada" via Wikisource raw wikitext)
Fetch "https://www.gutenberg.org/cache/epub/45315/pg45315.txt" "data/texts/blake_marriage.txt"
Fetch "https://en.wikisource.org/w/index.php?title=Liber_AL_vel_Legis&action=raw" "data/texts/liber_al.txt"
Fetch "https://en.wikisource.org/w/api.php?action=parse&page=1911_Encyclop%C3%A6dia_Britannica/Cicada&prop=text&format=json&formatversion=2" "data/texts/britannica_cicada.json"
# 2013 Cicada OS files and the 2014 notes holding the growing string (scream314/cicada3301)
Scream="https://raw.githubusercontent.com/scream314/cicada3301/master"
for F in AUDIO/761.MP3 DATA/_560.00 DATA/560.17 DATA/560.13 tmp/wisdom; do
  Fetch "$Scream/assets/2013/cicados/$F" "data/keyfiles/cicados/$(basename "$F")"
done
Fetch "$Scream/2014.md" "data/keyfiles/scream314_2014.md"
# B04: the full OEIS, first terms of every sequence (stripped.gz, ~30 MB)
mkdir -p data/keyfiles/oeis
Fetch "https://oeis.org/stripped.gz" "data/keyfiles/oeis/stripped.gz"
if [ "${1:-}" = "--images" ]; then
  for N in $(seq -w 0 74); do
    Fetch "$Scream/assets/2014/liber-primus-complete/$N.jpg" "data/keyfiles/lp-images/$N.jpg"
  done
fi
echo "texts: $(ls data/texts | wc -l), cicados: $(ls data/keyfiles/cicados | wc -l), images: $(ls data/keyfiles/lp-images | wc -l)"
