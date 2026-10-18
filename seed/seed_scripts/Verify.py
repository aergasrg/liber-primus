"""Reproduce the basic fingerprint and two solved pages from the raw transcription."""
import collections
import sys

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403

TotalRunes = TotalDoublets = 0
AllSteps = []
print(f"{'section':8} {'runes':>6} {'words':>6} {'IoC':>6} {'doublets':>8} {'rate%':>6}")
for Section in LoadAllUnsolved():
    Values = Section["Runes"]
    Doubles = DoubletCount(Values)
    TotalRunes += len(Values)
    TotalDoublets += Doubles
    AllSteps += Steps(Values)
    print(f"{Section['Name']:8} {len(Values):6d} {len(set(Section['WordId'])):6d} {Ioc(Values):6.3f} {Doubles:8d} {100 * Doubles / (len(Values) - 1):6.2f}")
print(f"TOTAL    {TotalRunes:6d}        doublets {TotalDoublets} ({100 * TotalDoublets / TotalRunes:.2f}% vs 3.45% random)")
StepCounts = collections.Counter(AllSteps)
print("step histogram:", [StepCounts[S] for S in range(29)])

# --- Walk the solved steps: Welcome (Vigenere DIVINITY with F pass-through) ---
Welcome = LoadSection("0_welcome")["Runes"]
Key = LatinToRunes("DIVINITY")
FPassThrough = {4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25}  # 1-based count of F runes in the ciphertext
Out, KeyPos, FSeen = [], 0, 0
for Value in Welcome:
    if Value == 0:
        FSeen += 1
        if FSeen in FPassThrough:
            Out.append(0)
            continue
    Out.append((Value - Key[KeyPos % len(Key)]) % 29)
    KeyPos += 1
print("\nWELCOME ->", ToLatin(Out)[:120])

# --- An End: subtract (prime - 1), one F pass-through ---
AnEnd = LoadSection("p56_an_end")["Runes"]
Primes = FirstPrimes(len(AnEnd) + 5)
for Skip in range(1, 8):
    Out, KeyPos, FSeen = [], 0, 0
    for Value in AnEnd:
        if Value == 0:
            FSeen += 1
            if FSeen == Skip:
                Out.append(0)
                continue
        Out.append((Value - (Primes[KeyPos] - 1)) % 29)
        KeyPos += 1
    Text = ToLatin(Out)
    if "DEEPWEB" in Text:
        print(f"AN END (F pass-through at F #{Skip}) ->", Text[:160])
        break

# --- Koan 1: atbash then +3 ---
Koan = LoadSection("0_koan_1")["Runes"]
print("KOAN 1 ->", ToLatin([(28 - V + 3) % 29 for V in Koan])[:100])
