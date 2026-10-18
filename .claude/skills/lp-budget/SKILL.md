---
name: lp-budget
description: Token and compute frugality rules for the Liber Primus lab, plus how (and how much) to use the OpenAI second-opinion wrapper. Use before long jobs, large outputs, or any call to another model.
---

# lp-budget

## Claude tokens

- Never print whole data files, transcriptions, keystreams or long result tables. Print counts, top 5,
  and a path to the file holding the rest.
- Read files with offsets/limits or grep; read a ledger entry, not the whole ledger directory.
- Write results to `results/E####/`; keep each committed file small (text, < ~200 KB).
- Long jobs (> ~5 min): run in the background, log progress to a file, checkpoint so they resume.
  Idle cloud VMs pause and can be reclaimed; an unsaved in-memory sweep is lost work.
- Vectorise with numpy (`lp.detectors.BatchIoc`, `FftRunningKeyScan`) before reaching for brute force.
- Use subagents only when the prompt asks for them; each starts cold and re-reads context.

## OpenAI (second opinions only)

- Every call goes through `tools/ask_other_model.py`. It is a stub ("not set up yet") until the
  "OpenAI helper v3" session builds it; until then, do not call OpenAI at all.
- Never print, log or commit API keys. The environment injects credentials; scripts never read them aloud.
- The cap is `OPENAI_TOKEN_CAP` (default 230,000 tokens for the whole project, minus 10k margin, with
  50k held back for verifying claimed hits). The wrapper enforces it with a shared ledger in
  `budget/openai/`; never bypass it.
- Use it for: attacking a test design, hunting bugs in an engine, an independent critique of a claimed
  hit (after the skeptic agent). Not for small jobs you can do yourself.
- Briefs use rune numbers or Latin letters, stay under 5,000 tokens, and never include copyrighted text.
