---
name: lp-handoff
description: Finish a Liber Primus lab session - ledger entries, backlog status, handoff note, regenerated indexes, commit, push and a pull request. Use at the end of every session, including ones that stop early.
---

# lp-handoff

1. **Ledger**: every experiment run this session has its own `docs/ledger/E####-slug.yaml` with control
   and null filled in (lp-experiment step 9). Partial runs are recorded as `inconclusive` with what is missing.
2. **Backlog item**: in its own file set `status: done` (or back to `open` with `claimed_by: ""` if you
   stopped early), list the new ledger ids under `ledger:`, and add a short `## Outcome` section.
   New ideas you found go in new `docs/backlog/B##-slug.md` files (next free number, `status: open`).
3. **Handoff note** `docs/sessions/YYYY-MM-DD-<branch>.md` (branch with `/` replaced by `-`):

```markdown
# YYYY-MM-DD <branch>

Item: Bxx <title>  |  Status: done / partial / blocked
Ledger: E####, E####

## What I did
- ...

## Results (control / null / best)
- ...

## Next steps (most useful first)
- ...

## Do not repeat
- ...

## Needs a human
- (Windows tools, files, decisions) or "nothing"
```

4. `python3 scripts/build_index.py` (must print `index ok`), then `python3 -m pytest -q tests/`.
5. `git fetch origin main && git merge origin/main` (resolve conflicts; generated tables: just rebuild).
6. Commit with a clear message, `git push -u origin <branch>`, and open a draft PR describing the item,
   ledger ids, and the verdict in one line each. Do not commit `data/`, keys or large binaries.
