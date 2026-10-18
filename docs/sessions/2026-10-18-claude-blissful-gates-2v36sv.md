# 2026-10-18 claude/blissful-gates-2v36sv

Item: B01 Skip-tolerant running-key engine  |  Status: done (CPU sources); GPU sources ready to run
Ledger: E0029

## What I did
- **Pre-item 1, page map cross-check** (`scripts/crosscheck_rtkd.py`, `results/crosscheck_rtkd.txt`):
  - rtkd/iddqd's transcription, with explicit % page and / line marks, is fetched by `fetch_data.sh`.
  - All 12,956 unsolved runes are identical to relikd's. There are 0 page and 0 line boundary
    disagreements, so `lp.data.PageLines` needed no change.
  - The only difference anywhere is in solved Koan 1, runes 142-143 and 279-280: relikd has W S
    ("WHAT YOU ARE"), rtkd has EA ("WHO YOU ARE", the known wording). Left as is, because relikd's
    cipher and plain files agree with each other. Recorded in STATE.md.
- **Pre-item 2, Koan 2 in the gate**: Vigenere FIRFUMFERENFE with the 2nd and 3rd of 5 ciphertext Fs
  skipped. This is the only subset of <= 3 skips that works. The gate now has 20 tests: Koan 2, plus
  an engine test that recovers Koan 2's key hidden in filler text.
- **Engine** `lp/runningkey.py`:
  - An exact DP over source position, vectorised over every start, with no skip-count dimension.
  - Any ciphertext F may skip. In the step views a skip may be literal or transparent.
  - English sources are a lattice: TH, NG/ING, EO, OE, AE, IA/IO, EA as one rune or as letters.
  - 4 views x 4 polarities x 2 directions, run page-local with an independent offset per page.
  - Includes a traceback (start, skips, plaintext) and PlantPage (the model's inverse).
  - Speed is about 3 ns per update for text and 1.4 ns for bytes. A full 32-form search takes about
    160 s on the Mabinogion (4 cores).
- **E0029** (`experiments/E0029_skip_tolerant_running_key.py`): stages controls / real / null / power /
  rigid / report / import-gpu.
  - The 7 CPU sources: LP solved plain, LP solved cipher, Self-Reliance, Mabinogion, growing string,
    560.13 and wisdom (`scripts/fetch_keysources.sh`).
- **GPU job** `gpu/E0029_bytes_gpu.py` + `gpu/README.md`, for 761.MP3, _560.00, 560.17 and the 75 page
  images (59 M bytes, too slow for this VM).
  - Self-contained torch.
  - Planted-key control first; it aborts on failure.
  - Checkpoints every unit (resume = rerun) and asserts < 5 GB of GPU memory.
  - Writes one results file of about 1 MB.
  - Checked against `lp.runningkey` on CPU: 96/96 scores and end pointers identical. A `--quick` run
    passed end to end.
- Renumbered E0028 -> E0029 mid-session: main got E0028 (B12) while this ran.

## Results (control / null / best)
- **Controls**: Koan 2 and Welcome, with their keys hidden in the Mabinogion, are found by the full
  search at the exact start, Gumbel z 49 and 61; the per-page threshold is 11.
  - Koan 2: exact skips and exact plaintext.
  - Welcome: 9/11 skips exact; the other two sit on FF pairs (a near tie).
- **Tier 1**, 100 plants per view x skip pattern x length bin:
  - pages >= 221 runes: 100/100 everywhere;
  - pages 141-220 runes: >= 99/100;
  - pages <= 140 runes (p14, p22, p32, p49, p51, p55): 50-86/100, not identifiable.
  - Rigid FFT, even given the true tokenisation, recovers 25-61/100 with a mid or early skip.
- **Null**: 20 shuffled-source replicates of the whole search per source. The Gumbel fit is checked.
  The threshold is standardised 11.01 (family-wise 0.01 over 55 pages x 11 sources).
- **Real**: negative. Best page per source is standardised 2.2-5.0, and every null p is >= 0.29. No
  page reached the skeptic.
- So these sources are excluded as page-local keys on the 49 pages of >= 141 runes, in the 32 forms.

## Next steps (most useful first)
- **GPU job ready**: the human runs `gpu/E0029_bytes_gpu.py` overnight (see `gpu/README.md`) and uploads
  `results_E0029_gpu.json`. Then run `python3 experiments/E0029_skip_tolerant_running_key.py import-gpu
  --file <path>`, then `report`, and write a new ledger entry for those four sources.
- B03 (public-domain Cicada texts as running keys) can now use `lp.runningkey` directly. It needs about
  20 null reps per source, and sources over ~1 M letters belong on the GPU.
- B22 (new): short pages via cross-page continuation and bigram scoring.
- Branch claude/eloquent-hopper-k6fff6 (B21) also calls its experiment E0028, which collides with main.
  It must renumber; E0029 is taken by this branch.

## Do not repeat
- Rigid running-key scans of these sources, or a page-local skip-tolerant rerun of the 7 CPU sources in
  these 32 forms (E0029).
- The page-map cross-check (rtkd agrees exactly).

## Needs a human
- Run the GPU job (about 8-12 h, ~60 MB download, < 2 GB GPU memory) and upload the results file.
- Nothing else.
