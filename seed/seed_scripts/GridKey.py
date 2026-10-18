"""Use the 256 decoded grid bytes as a running key at every offset of every unsolved section."""
import random, sys
sys.path.insert(0, ".")
from LpCore import *
Data = list(open("grid60.bin", "rb").read())
def Scan(Key29, Key28):
    Best = (0, "")
    for Section in LoadAllUnsolved():
        Raw = Section["Runes"]
        StepU = [S - 1 for S in Steps(Raw) if S != 0]
        for Offset in range(0, len(Raw) - len(Key29) + 1):
            Window = Raw[Offset:Offset + len(Key29)]
            for Sign in (1, -1):
                Score = Ioc([(V - Sign * K) % 29 for V, K in zip(Window, Key29)])
                if Score > Best[0]: Best = (Score, f"{Section['Name']} raw offset {Offset} sign {Sign:+d}")
        for Offset in range(0, len(StepU) - len(Key28) + 1):
            Window = StepU[Offset:Offset + len(Key28)]
            for Sign in (1, -1):
                Score = Ioc([(V - Sign * K) % 28 for V, K in zip(Window, Key28)], 28)
                if Score > Best[0]: Best = (Score, f"{Section['Name']} chain offset {Offset} sign {Sign:+d}")
    return Best
Real = []
for Label, Key in (("bytes", Data), ("reversed", Data[::-1])):
    Real.append((Scan([B % 29 for B in Key], [B % 28 for B in Key]), Label))
print("grid as key:", Real)
Rng = random.Random(5)
Null = sorted(Scan(*(lambda K: ([B % 29 for B in K], [B % 28 for B in K]))([Rng.randrange(256) for _ in range(256)]))[0] for _ in range(6))
print("null (random 256-byte keys, same scan):", [round(N, 3) for N in Null])
