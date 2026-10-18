# 2026-10-18 claude/stoic-feynman-g6muzj

Item: council kickoff phase (lp-council; no backlog item)  |  Status: done
Ledger: none (the council runs no experiments)

## What I did
- Key-lock check: no reserved budget entry, no open PR, no other branch touching docs/council.
  `--list-models` showed no undescribed id; docs/models/openai.md is 1 day old. Gate: 17 tests pass.
- Briefs in docs/council/2026-10-18/: `brief.md` (fingerprint, solved-page methods, leads with exact
  values, 19 ledger lines), plus the three prompts. Three gpt-6-astra calls, all completed:
  02 cryptanalyst (medium, 13,291 tokens), 03 designer (medium, 14,353), 04 negatives audit of E0002,
  E0008, E0019 (high, 24,181). Phase total 51,825; remaining 118,125 general / 168,125 with reserve.
- Deduped 24 ideas and the audit against the ledger; filed B12-B20 and extended B01 (see
  docs/council/2026-10-18/README.md for the mapping and the drops).
- Corrected docs/LEADS.md and B10: the page-15 square is |3301 - B| with B the primes at 0-based
  Fibonacci indices (2, 3, 5, ..., 7817), in a spiral. The designer call's "correction" was wrong.
- Measured for B13: the five rarest plaintext runes total 0.34% of solved text (baseline 0.37%),
  six total 0.87% (0.80%); the doublet rate is 0.664%.

## Results (control / null / best)
- No experiments. The audit's main finding: none of E0002, E0008, E0019 excludes the combined model
  "page-local key, chain arithmetic, irregular F-skips", because none of their scans or plants had
  those features. Quantified: a first skip after 100 runes drops a 300-rune IoC to about 1.09 (ceiling
  1.20-1.25); E0019's "1.23 then 1.01 on the whole section" is also what a correct first-page key
  followed by a page change looks like.

## Next steps (most useful first)
- Merge this PR before any other council phase (one key-using session at a time).
- First wave, one item per session: B01 (with the council additions; it is the engine B18/B19/B14
  need), B18 (cheap, step-domain periodicity page by page), B12 (cheap, doublet event process).
  B18 step 1 (the real page map in `lp.data`) is a prerequisite shared by B01, B18 and B19: do it first.
- Adopt the audit's null rule in lp-experiment (999 surrogate corpora, max-search p <= 0.01, plants
  recovered in >= 95 of 100): a human decision, since it changes a skill.
- Midpoint council after the first wave is merged (65k planned).

## Do not repeat
- Rigid whole-section running-key or PRNG scans, raw mod-29 PRNG sweeps, more period scans on raw
  runes: the audit lists why in B18, B19 and B01.
- The kickoff calls themselves; their replies are saved in docs/council/2026-10-18/.

## Needs a human
- Decide whether to write the audit's null rule into .claude/skills/lp-experiment/SKILL.md.
- Nothing else; the proxy injects the API credential.
