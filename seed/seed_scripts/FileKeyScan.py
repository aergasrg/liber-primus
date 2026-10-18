"""2013 Cicada OS files as running keys (raw form, both signs), every byte offset, via FFT.

Files: 761.MP3, _560.00, 560.17, 560.13, wisdom (= folly), forwards and byte-reversed.
Score: English unigram log-likelihood ratio over the first 300 runes of each section, with the
key byte taken mod 29. Assumes no F-skip inside those 300 runes.
"""
import collections
import math
import sys
import time

import numpy as np

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403

Window = 300
Base = "/tmp/scream/assets/2013/cicados"
Files = ["AUDIO/761.MP3", "DATA/_560.00", "DATA/560.17", "DATA/560.13", "tmp/wisdom"]

EnglishCounts = collections.Counter()
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    EnglishCounts.update(RuneIndex[C] for C in Line.strip() if C in RuneIndex)
Total = sum(EnglishCounts.values())
LogRatio = np.array([math.log((EnglishCounts[R] + 1) / Total * 29) for R in range(29)])

Sections = [(S["Name"], np.array(S["Runes"][:Window])) for S in LoadAllUnsolved()]


def ScanKey(KeyValues, Targets):
    """Return best (score, offset, label) over all offsets for every (section, sign) target."""
    Length = len(KeyValues)
    if Length < Window + 1:
        return None
    Size = 1 << int(math.ceil(math.log2(Length + Window)))
    Results = []
    for Name, Cipher in Targets:
        for Sign in (1, -1):
            Accumulator = np.zeros(Size // 2 + 1, dtype=np.complex128)
            for Symbol in range(29):
                Indicator = (KeyValues == Symbol).astype(np.float64)
                Weights = LogRatio[(Cipher - Sign * Symbol) % 29]
                Accumulator += np.fft.rfft(Indicator, Size) * np.conj(np.fft.rfft(Weights, Size))
            Scores = np.fft.irfft(Accumulator, Size)[: Length - Window + 1]
            Best = int(np.argmax(Scores))
            Results.append((float(Scores[Best]) / Window, Best, f"{Name} sign {Sign:+d}"))
    return max(Results)


# Positive control: plant a 300-byte slice of 761.MP3 (offset 1,234,567) over English plaintext
Mp3 = np.frombuffer(open(f"{Base}/AUDIO/761.MP3", "rb").read(), dtype=np.uint8).astype(np.int64) % 29
Solved = []
for SolvedName in ["solved_0_loss_of_divinity", "solved_0_koan_1", "solved_0_welcome"]:
    Solved += LoadSection(SolvedName)["Runes"]
Planted = (np.array(Solved[:Window]) + Mp3[1234567:1234567 + Window]) % 29
Started = time.time()
print("CONTROL planted at 1234567:", ScanKey(Mp3, [("CTRL", Planted)]), f"({time.time() - Started:.0f}s)")
print("reference: English text scores about +0.41 per rune, random about -0.6")

for FileName in Files:
    Data = np.frombuffer(open(f"{Base}/{FileName}", "rb").read(), dtype=np.uint8).astype(np.int64) % 29
    for Direction, Values in (("forward", Data), ("reversed", Data[::-1].copy())):
        Started = time.time()
        Best = ScanKey(Values, Sections)
        if Best is None:
            # short file: try it as a repeating key instead
            Repeated = np.resize(Values, Window + len(Values))
            Best = ScanKey(Repeated, Sections)
            Direction += " (repeated)"
        print(f"{FileName:16} {Direction:20} best LLR/rune {Best[0]:+.3f} at offset {Best[1]} on {Best[2]}  ({time.time() - Started:.0f}s)", flush=True)
