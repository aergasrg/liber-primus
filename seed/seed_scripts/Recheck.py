"""Re-score the top seed candidates on whole sections; also confirm the chain-form control."""
import random, sys
import numpy as np
sys.path.insert(0, ".")
from LpCore import *
from PrngSweep import Drand48Ints, GlibcRand
Sections = {S["Name"]: S for S in LoadAllUnsolved()}
def Full(Name, Key29, Key28, Form):
    Raw = Sections[Name]["Runes"]
    StepU = [S - 1 for S in Steps(Raw) if S != 0]
    if Form == "raw-": return Ioc([(V - K) % 29 for V, K in zip(Raw, Key29)])
    if Form == "raw+": return Ioc([(V + K) % 29 for V, K in zip(Raw, Key29)])
    if Form == "chain-": return Ioc([(V - K) % 28 for V, K in zip(StepU, Key28)], 28)
    return Ioc([(V + K) % 28 for V, K in zip(StepU, Key28)], 28)
Checks = [("glibc", 740062, "p3-7", "raw+"), ("glibc", 363774, "p3-7", "raw-"), ("perl", 254994, "p33-39", "chain+"), ("perl", 431309, "p3-7", "raw-")]
for Gen, Seed, Name, Form in Checks:
    N = len(Sections[Name]["Runes"])
    if Gen == "perl":
        K29, K28 = Drand48Ints(np.array([Seed]), N, 29)[0], Drand48Ints(np.array([Seed]), N, 28)[0]
    else:
        R = GlibcRand(np.array([Seed]), N)[0]; K29, K28 = R % 29, R % 28
    print(f"{Gen} seed {Seed} {Name}/{Form}: first-300 score was ~1.2, whole section ({N} runes) IoC = {Full(Name, K29, K28, Form):.3f}")
Gen = random.Random(85098); F = [Gen.random() for _ in range(2000)]
StepU = [S - 1 for S in Steps(Sections["p8-14"]["Runes"]) if S != 0]
print(f"python seed 85098 p8-14/chain-: whole section IoC = {Ioc([(V - int(X * 28)) % 28 for V, X in zip(StepU, F)], 28):.3f}")
# chain-form control with the planted drand48 stream
Solved = []
for N_ in ["solved_0_loss_of_divinity", "solved_0_koan_1", "solved_0_welcome"]: Solved += LoadSection(N_)["Runes"]
K28 = Drand48Ints(np.array([777777]), 301, 28)[0]; Chain = [5]
for P, K in zip(Solved[:301], K28): Chain.append((Chain[-1] + 1 + (P % 28 + K) % 28) % 29)
U = [S - 1 for S in Steps(Chain) if S != 0][:300]
print(f"chain control, right seed: IoC28 = {Ioc([(V - K) % 28 for V, K in zip(U, K28)], 28):.3f}; wrong seed: {Ioc([(V - K) % 28 for V, K in zip(U, Drand48Ints(np.array([777778]), 301, 28)[0])], 28):.3f}")
