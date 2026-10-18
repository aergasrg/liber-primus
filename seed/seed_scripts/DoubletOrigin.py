"""Where could the 86 ciphertext doublets come from?

Hypothesis A: a rare plaintext letter maps to a zero step (repo's EA model) -> compare
              the word-position profile of every rune in English with the doublet profile.
Hypothesis B: step = (p_i - p_{i-1}) * m_i with a non-zero keyed multiplier -> ciphertext doublets
              would sit exactly on plaintext doubled letters; compare rates and position profiles.
"""
import collections
import math
import sys

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403


def PositionBucket(Position):
    return min(Position, 7)


# Ciphertext doublet profile (position of the SECOND rune of the pair within its word)
CipherProfile = collections.Counter()
for Section in LoadAllUnsolved():
    Values = Section["Runes"]
    for Index in range(1, len(Values)):
        if Values[Index] == Values[Index - 1]:
            CipherProfile[PositionBucket(Section["PosInWord"][Index])] += 1
CipherTotal = sum(CipherProfile.values())
print("cipher doublet profile (pos of 2nd rune 0..7+):", [CipherProfile[B] for B in range(8)], "total", CipherTotal)

# English baseline in runes (War and Peace, one word per line)
Words = [Line.strip() for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8") if Line.strip()]
WordRunes = [[RuneIndex[C] for C in W if C in RuneIndex] for W in Words]
WordRunes = [W for W in WordRunes if W]
Stream, StreamPos = [], []
for W in WordRunes:
    for Position, V in enumerate(W):
        Stream.append(V)
        StreamPos.append(Position)
TotalLetters = len(Stream)

# Hypothesis B: doubled letters in plaintext
DoubleProfile = collections.Counter()
for Index in range(1, TotalLetters):
    if Stream[Index] == Stream[Index - 1]:
        DoubleProfile[PositionBucket(StreamPos[Index])] += 1
DoubleRate = sum(DoubleProfile.values()) / (TotalLetters - 1)
print(f"\nEnglish (runes) doubled-letter rate: {100 * DoubleRate:.2f}%  profile:",
      [round(100 * DoubleProfile[B] / sum(DoubleProfile.values()), 1) for B in range(8)])

Solved = []
for Name in ["solved_0_warning", "solved_0_welcome", "solved_0_wisdom", "solved_0_koan_1",
             "solved_0_loss_of_divinity", "solved_p56_an_end", "solved_p57_parable"]:
    Solved += LoadSection(Name)["Runes"]
print(f"Solved LP plaintext doubled-letter rate: {100 * DoubletCount(Solved) / (len(Solved) - 1):.2f}% over {len(Solved)} runes")


def ChiSquare(Observed, ExpectedShare):
    Total = sum(Observed.values())
    Score = 0.0
    for Bucket in range(8):
        Expected = Total * ExpectedShare.get(Bucket, 1e-9)
        Score += (Observed[Bucket] - Expected) ** 2 / max(Expected, 1e-9)
    return Score


Shares = {B: DoubleProfile[B] / sum(DoubleProfile.values()) for B in range(8)}
print(f"chi2 (df 7) cipher doublets vs English doubled letters: {ChiSquare(CipherProfile, Shares):.1f}")

# Hypothesis A: each single rune as the 'zero-step' letter
print("\nrune  freq%   chi2(df7)  position profile % (0..7+)")
Rows = []
for Rune in range(29):
    Profile = collections.Counter(PositionBucket(P) for V, P in zip(Stream, StreamPos) if V == Rune)
    Count = sum(Profile.values())
    if Count == 0:
        continue
    Share = {B: Profile[B] / Count for B in range(8)}
    Rows.append((ChiSquare(CipherProfile, Share), Rune, 100 * Count / TotalLetters, Share))
for Score, Rune, Freq, Share in sorted(Rows)[:10]:
    print(f"{LatinNames[Rune]:4} {Freq:6.2f}  {Score:9.1f}  ", [round(100 * Share[B]) for B in range(8)])
print("(critical chi2 at p=0.01 with df 7 is 18.5)")
