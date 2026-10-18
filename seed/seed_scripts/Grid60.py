"""The 8-column grid of 2-character tokens inside the unsolved pages: read each token as base 60."""
import collections, math, re, sys
sys.path.insert(0, ".")
from LpCore import *
Digits60 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
Tokens = []
for Name in UnsolvedNames:
    for Line in open(f"/tmp/LiberPrayground/pages/{Name}.txt", encoding="utf-8"):
        Found = re.findall(r"(?<![0-9A-Za-z])([0-4][0-9A-Za-x])(?![0-9A-Za-z])", Line)
        if len(Found) == 8:
            Tokens += Found
            Where = Name
Values = [Digits60.index(T[0]) * 60 + Digits60.index(T[1]) for T in Tokens]
print("section:", Where, "| tokens:", len(Tokens), "| min/max value:", min(Values), max(Values))
Data = bytes(Values)
Counts = collections.Counter(Data)
Entropy = -sum(N / len(Data) * math.log2(N / len(Data)) for N in Counts.values())
print("distinct bytes:", len(Counts), "| entropy bits/byte:", round(Entropy, 2), "(random 256 bytes ~7.2)")
print("hex:", Data.hex())
open("grid60.bin", "wb").write(Data)
