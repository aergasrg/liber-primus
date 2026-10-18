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
- Use subagents only when the prompt asks for them; each starts cold and re-reads context. Workers help
  only inside the session's own claimed item; parallel waves are 2-3 separate sessions, one item each.

## OpenAI (second opinions only)

- Read `docs/models/openai.md` first: the models are newer than Claude's training data. Apply its
  refresh rule (over 30 days old, or `--list-models` shows an undescribed id -> look it up, update the file).
- Every call goes through `tools/ask_other_model.py` (background Responses API, shared budget ledger
  `budget/openai/ledger.jsonl`, outputs in `docs/council/<date>/`). Never bypass it; never print, log
  or commit keys. `--list-models` costs no tokens; `--dry-run` checks the budget without sending.
- Model: gpt-6-astra (our limit is tokens, not dollars). gpt-6.1-sol only when Astra flags a request
  or the key can't reach Astra. Skip the others.
- **Service tier, never changed.** Every request sends `"service_tier": "default"` (Standard speed and
  price). Never Fast, Ultrafast, priority or flex, and never omit the field (a project can default
  untagged requests to a pricier tier). The value is pinned from a live call (2026-10-18: Standard
  reports `default`). If any response reports another tier, or the final response reports none, the
  tool cancels it, logs `tier-violation`, writes `budget/openai/STOP` and refuses every call (exit 2)
  while that file exists locally or on origin/main. Only a human deletes it.
- **Text only.** Never enable hosted tools (code interpreter, web search, file search, shell, or any
  `tools` field); the request body is whitelisted in the tool.
- Budget: a rolling 24-hour window. Cap = min(`OPENAI_TOKEN_CAP` or 230000, 230000) - 10000 = 220000
  per 24 h; the tool sums ledger entries from the last 24 hours. There is no reserve: verify calls
  simply go first on any day. Hidden reasoning tokens are billed as output and count;
  `--max-output` bounds reasoning plus answer.
- Effort policy:

| use | effort | max-output |
| --- | --- | --- |
| brainstorming lists of hypotheses | medium | 16000 |
| attacking a test design, hunting bugs, checking a claimed hit, an exact test spec | high | 25000 |
| the single hardest question of a phase | xhigh | 40000 |
| pro mode, at most once per 24 h, only with 60k+ left in the window | high + `--mode pro` | 40000 |

- Never max effort (7+ minutes to a first token in a public run) and never low or none (do small jobs
  yourself). Deadlines: medium 8 min, high 12, xhigh 20, pro 30; a pro call that times out or fails
  falls back once to standard mode, the only automatic retry.
- Only one key-using session at a time; council phases follow the lp-council skill.
- Briefs use rune numbers or Latin letters, stay under 5,000 tokens, and never include copyrighted text.
