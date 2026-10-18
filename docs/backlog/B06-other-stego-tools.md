---
id: B06
title: Other stego tools on page images
status: open
claimed_by: ""
rank: 6
ledger: [E0011]
---

# B06 Other stego tools on page images

## Why
Only OutGuess has been checked. Cicada also used other tools in earlier rounds.

## Test design
1. Fetch page images (relikd repo pages/*.jpg) into data/images/ by script.
2. steghide and JPHide (jphs) with no password and the 96-word list from E0011/E0021.
3. OpenPuff needs Windows: write the password list to docs/ and ask the human to run it (handoff).
4. Inspect JPEG quantization tables and the fixed black dots on some pages.
5. Control: embed a payload with each tool in a page image and recover it; null: random-noise false-positive rate.

## Notes
Some steps need a human (OpenPuff).
