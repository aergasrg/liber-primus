# Liber Primus lab

A long-running research notebook on the unsolved pages of Cicada 3301's *Liber Primus* (LP), worked
by many Claude Code cloud sessions over several weeks. Chances of solving it are really slim; the aim
is a clean, honest, reproducible record of what has been tried, with real new negatives (or a lucky hit).

## Quick start

```bash
pip install numpy pyyaml pytest
bash scripts/fetch_data.sh          # relikd's transcription into data/ (gitignored)
python3 -m pytest -q tests/         # the gate: must pass before any experiment
python3 experiments/port_check.py   # ~10 s sanity run of the PRNG control
python3 scripts/build_index.py      # regenerate docs/LEDGER.md and docs/BACKLOG.md
```

The gate reproduces Welcome (Vigenere DIVINITY with 11 F-skips), Koan 1 (Atbash then +3), A Warning,
An End (prime - 1 with one F-skip), the unsolved fingerprint (12,956 runes, 86 doublets, the exact step
histogram) and the bit-exact Perl/glibc PRNGs.

## Layout

| Path | What |
| --- | --- |
| `CLAUDE.md` | Rules every session follows |
| `docs/STATE.md` | Everything known, compact |
| `docs/HISTORY.md`, `docs/LEADS.md` | Puzzle trail 2012-2017; unused clues with exact values |
| `docs/ledger/E####-*.yaml` | One file per experiment (append-only) |
| `docs/backlog/B##-*.md` | One file per idea, with status open / claimed / done |
| `docs/LEDGER.md`, `docs/BACKLOG.md` | Generated tables (never hand-edited) |
| `docs/sessions/` | Handoff notes, one per session |
| `lp/` | Library: gematria, loader, statistics, ciphers, detectors, controls, key sources |
| `experiments/`, `results/` | Experiment scripts and their small text outputs |
| `seed/` | Session-one scripts and prompts (historical) |
| `.claude/skills/`, `.claude/agents/` | Session workflow (lp-start, lp-experiment, lp-handoff, lp-budget, lp-data, lp-council) and the skeptic, council and worker agents |
| `tools/ask_other_model.py` | OpenAI wrapper: budgeted background calls (see `docs/models/openai.md`) |
| `budget/openai/ledger.jsonl`, `docs/council/` | Shared OpenAI token ledger; saved prompts and replies |

## How sessions work

1. A session starts with **lp-start**: reads CLAUDE.md, STATE and the generated indexes, picks the top
   open backlog item (or the one it was given) and claims it in that item's file.
2. It runs the item with **lp-experiment**: hypothesis, coverage, positive control, null ceiling, run,
   re-check top hits on full sections, record a ledger YAML.
3. Anything above its noise ceiling goes to the **skeptic** agent before anyone believes it.
4. It ends with **lp-handoff**: ledger entries, item status, a note in `docs/sessions/`, rebuild the
   index, commit, push, open a PR.

Ledger and backlog are one file per entry, so parallel sessions never edit the same file. Merge PRs
between waves.

Worker prompt to paste into a new session:

```text
Run the lp-start skill. Work on <B0X | the top open item>. Follow lp-experiment exactly and finish
with lp-handoff.
```

## Credits and licences

Transcription: [relikd/LiberPrayground](https://github.com/relikd/LiberPrayground). Prior exclusions
are cited from relikd, the Cicada wiki, jbo's cicada_tools and
[LiberPrimusAnalysis](https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis) (proprietary source-available:
cited only, no code copied). No copyrighted text is stored here.
