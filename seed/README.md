# Liber Primus seed bundle (17 Oct 2026)

Scripts from the first research session. Unzip into `seed/` in the new repo; the bootstrap
session ports them into the `lp/` package and `experiments/`. Variables are PascalCase on purpose.

Hard-coded paths to fix when porting:

- Transcription: `/tmp/LiberPrayground/pages/*.txt` (github.com/relikd/LiberPrayground, branch `main`)
- English rune corpus: `/tmp/LiberPrayground/data/baseline-rune-words.txt`
- 2013 Cicada OS files: `/tmp/scream/assets/2013/cicados/...` (github.com/scream314/cicada3301, branch `master`)
- `sys.path.insert(...)` lines point at the old scratchpad; replace with a package import.

| Script | What it does | Result recorded |
| --- | --- | --- |
| LpCore.py | Gematria Primus, section loader (word, sentence, line, page positions), IoC, doublets, steps, Latin to runes | library |
| Verify.py | Per-section stats; reproduces Welcome (DIVINITY + 11 F-skips), Koan 1 (Atbash +3), An End (prime - 1) | 12,956 runes, 86 doublets, step histogram |
| DoubletOrigin.py | Tests whether doublets are plaintext doubled letters or one rare letter | Neither fits (chi2 255 vs doubled letters) |
| StructureTests.py | Key resets per word/sentence/line/page; sequences run from the section end; Latin-alphabetical arithmetic | All negative, controls z 5.6-6.1 / IoC 1.76-1.93 |
| PageDepth.py, PageDepthNull.py | Every page pair sharing a key from its first rune, with a permutation null | 7 pairs above z 3 = null median 7 |
| PrngSweep.py | Perl drand48 and glibc rand() seeds 0..2^20 (bit-exact, validated), 4 forms | Max 1.23 on 300 runes, ~1.01 on full sections |
| HashAndMt.py | 4,032 hash-derived pads (96 words), unused numbers in base 29, Python MT seeds 0..2^18 | All negative |
| Grid60.py | Decodes the 8x32 token grid (base 60) into 256 bytes | 0..255, entropy 7.17 bits/byte |
| GridKey.py | The 256 bytes as a running key at every offset | Inside random-key null |
| FileKeyScan.py | 2013 Cicada OS files as running keys via FFT (LLR scoring) | Best -0.28/rune vs English +0.40 |
| GridBookCode.py | Urquhart-style test: the 256 grid numbers as word indices into LP's own words | Negative vs random-index null; control +0.35 |
| Recheck.py | Re-scores top seed hits on whole sections; chain-form control | Hits collapse to ~1.0 |

None of these handle F-skips inside running keys. That is backlog item B01.
