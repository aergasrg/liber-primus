---
name: lp-experiment
description: Run one Liber Primus experiment the lab's way - hypothesis, coverage, positive control, null ceiling, background run with checkpoints, full-section recheck of top hits, and a ledger YAML. Use for any test of a key source or cipher hypothesis.
---

# lp-experiment

A result without a passing positive control and a null ceiling is not a result. Record both.

1. **Hypothesis**: one sentence saying which mechanism produces the ciphertext and what key it uses.
2. **Coverage**: exactly what is enumerated (sources, offsets, signs, forms raw/chain, skips, sections,
   window length). Be precise enough that the next session can tell whether a variant is new.
3. **Write the script** `experiments/E####_slug.py` using `lp/` (do not copy library code). Outputs go to
   `results/E####/` as small text/JSON files. PascalCase variables.
4. **Positive control first** (`lp.controls`): plant a key from the same family into known plaintext
   (`ControlPlaintext`), with realistic F-skips if the method claims to handle them, and push it through
   the IDENTICAL pipeline (same function, same window, same scoring). It must be recovered clearly
   above the null. If it is not, the experiment cannot produce a negative: fix the pipeline.
5. **Null / noise ceiling**: the best score the same search finds on noise. Prefer permutation nulls
   (shuffled ciphertext, random keys of the same length through the same scan) over normal z
   (binomial tails at p = 1/29 are skewed). The ceiling must reflect the number of trials: a max over
   10^6 windows of 300 runes reaches IoC ~1.2-1.25 by chance.
6. **Run**. Anything over ~5 minutes runs in the background (`nohup ... > results/E####/run.log 2>&1 &`
   or the Bash tool's background mode), logs progress every few percent, and checkpoints partial
   results to disk so a paused or reclaimed VM can resume. Print only summaries.
7. **Recheck top hits on full sections**: re-score the top N candidates over the whole section (and the
   other sections where the key would continue). Window maxima that collapse to ~1.0 are noise.
8. **Anything above the ceiling** after the recheck: run the skeptic agent (`.claude/agents/skeptic.md`)
   before believing or announcing it.
9. **Record** `docs/ledger/E####-slug.yaml` (next free id after `git fetch origin main`):

```yaml
id: E0027
title: Short title
family: running-key-text        # reuse an existing family name when it fits (see docs/LEDGER.md)
hypothesis: ...
coverage: ...
detector: ...
control: {method: ..., score: ...}
null: {method: ..., ceiling: ...}
result: {best: ..., verdict: negative}   # negative | positive | inconclusive
skips_handled: "yes: drift DP at every ciphertext F"   # or "no"
source: <branch name>
date: 'YYYY-MM-DD'
artifacts: [experiments/E0027_slug.py, results/E0027/summary.txt]
notes: what is new vs earlier entries; anything the next session must know
```

Never edit another session's ledger file; if an old entry is wrong, add a new entry that supersedes it
and say so in `notes`.
