"""More keystream sources not covered by the published ledgers.

A. Hash-derived pads seeded with Cicada words/numbers (md5, sha1, sha256, sha512, sha3, blake2b;
   digest chain, hex chain, counter mode; byte%29 or base-29 digits).
B. Never-used Cicada numbers written in base 29 (the 2012 P.S. semiprime and its factors, the 2013
   cookies, the page-56 hash, Parable number...) as running keys at each section start.
C. Python Mersenne Twister seeded 0..2^18 (Py3 randrange and Py2 int(random()*n)).
"""
import hashlib
import math
import random
import sys
import time

import numpy as np

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403
from PrngSweep import BatchIoc, Score, SectionInputs, Window  # noqa: E402

Inputs = SectionInputs()
Labels = [Name + Form for Name, _, _ in Inputs for Form in ("/raw-", "/raw+", "/chain-", "/chain+")]

# ---------------- A. hash pads ----------------
Words = ["3301", "1033", "cicada", "Cicada", "CICADA", "cicada3301", "Cicada 3301", "divinity", "DIVINITY", "Divinity",
         "circumference", "CIRCUMFERENCE", "circumferences", "instar", "INSTAR", "emergence", "The Instar Emergence",
         "parable", "PARABLE", "Liber Primus", "liberprimus", "LIBER PRIMUS", "primus", "Self-Reliance", "welcome",
         "pilgrim", "koan", "Interconnectedness", "7A35090F", "181F01E57A35090F", "761", "167", "1231507051321",
         "845145127", "1595277641", "deep web", "deepweb", "totient", "the primes are sacred", "THE PRIMES ARE SACRED",
         "all things should be encrypted", "Good luck.", "find the divinity within and emerge", "emerge",
         "like the instar tunneling to the surface", "a warning", "an end", "sacred", "wisdom", "enlightenment",
         "Mabinogion", "Agrippa", "Liber AL vel Legis", "Godel Escher Bach", "magic square", "FIRFUMFERENFE",
         "firfumferenfe", "obscura", "shadows", "aethereal", "mobius", "cabal", "analog", "void", "carnal", "mournful",
         "buffers", "form", "3301 1033", "ᛞᛁᚢᛁᚾᛁᛏᚣ", "ᛈᚪᚱᚪᛒᛚᛖ", "ᛁᚾᛋᛏᚪᚱ", "ᚳᛁᚳᚪᛞᚪ", "ᛚᛁᛒᛖᚱ ᛈᚱᛁᛗᚢᛋ",
         "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4",
         "6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6",
         "7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5", "1033 3301", "33011033", "10333301",
         "sq6wmgv2zcsrix6t", "p7amjopgric7dfdi", "ky2khlqdf7qdznac", "auqgnxjtvdbll3pv", "the path lies empty",
         "epiphany seeks the devoted", "Liber Primus is the way", "seek and you will be found", "a koan", "an instruction",
         "some wisdom", "the loss of divinity", "consumption", "preservation", "adherence", "question all things"]
HashNames = ["md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512", "blake2b"]


def PadBytes(Seed, HashName, Mode, Needed):
    Out = b""
    H = lambda Data: hashlib.new(HashName, Data)  # noqa: E731
    if Mode == "chain":
        Digest = H(Seed.encode()).digest()
        while len(Out) < Needed:
            Out += Digest
            Digest = H(Digest).digest()
    elif Mode == "hexchain":
        Hex = H(Seed.encode()).hexdigest()
        while len(Out) < Needed:
            Out += bytes.fromhex(Hex)
            Hex = H(Hex.encode()).hexdigest()
    else:  # counter
        Counter = 0
        while len(Out) < Needed:
            Out += H((Seed + str(Counter)).encode()).digest()
            Counter += 1
    return Out


def Base29Digits(Number):
    Digits = []
    while Number:
        Number, Digit = divmod(Number, 29)
        Digits.append(Digit)
    return Digits[::-1] or [0]


Rows29, Rows28, RowLabels = [], [], []
for Seed in Words:
    for HashName in HashNames:
        for Mode in ("chain", "hexchain", "counter"):
            Data = PadBytes(Seed, HashName, Mode, 4 * Window)
            Rows29.append([B % 29 for B in Data[:Window]])
            Rows28.append([B % 28 for B in Data[:Window]])
            RowLabels.append(f"{HashName}/{Mode}/bytes/{Seed[:24]}")
            Digest = hashlib.new(HashName, Seed.encode()).digest()
            Digits = []
            while len(Digits) < Window:
                Digits += Base29Digits(int.from_bytes(Digest, "big"))
                Digest = hashlib.new(HashName, Digest).digest()
            Rows29.append(Digits[:Window])
            Rows28.append([D % 28 for D in Digits[:Window]])
            RowLabels.append(f"{HashName}/{Mode}/base29/{Seed[:24]}")
Key29 = np.array(Rows29, dtype=np.int64)
Key28 = np.array(Rows28, dtype=np.int64)
Best, Where = Score(Inputs, Key29, Key28)
Order = np.argsort(Best)[::-1][:5]
print(f"A. hash pads: {len(RowLabels)} keystreams x 9 sections x 4 forms; top:")
for I in Order:
    print(f"   IoC {Best[I]:.3f}  {RowLabels[I]}  on {Labels[Where[I]]}")
# control: plant one pad into solved plaintext
Solved = []
for SolvedName in ["solved_0_loss_of_divinity", "solved_0_koan_1", "solved_0_welcome"]:
    Solved += LoadSection(SolvedName)["Runes"]
Plain = np.array(Solved[:Window])
Planted = (Plain + Key29[123]) % 29
print(f"   control (planted {RowLabels[123]}): IoC after removal {BatchIoc(((Planted - Key29[123]) % 29)[None, :], 29)[0]:.3f}")

# ---------------- B. unused numbers in base 29 ----------------
PsNumber = int("1041279065891998535982789873959431895640442510695567564373922695237268242385295908173983439037037447576486341520342349935710871363" + "1")
Numbers = {
    "2012 P.S. number": PsNumber,
    "P.S. factor 1": 99554414790940424414351515490472769096534141749790794321708050837,
    "P.S. factor 2": 104593961812606247801193807142122161186583731774511103180935025763,
    "cookie 167": int("6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6", 16),
    "cookie 761": int("7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5", 16),
    "page-56 hash": int("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4", 16),
    "parable 1595277641": 1595277641,
    "845145127": 845145127,
    "1231507051321": 1231507051321,
    "PGP key id 181F01E57A35090F": 0x181F01E57A35090F,
}
EnglishCounts = collections.Counter()
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    EnglishCounts.update(RuneIndex[C] for C in Line.strip() if C in RuneIndex)
Total = sum(EnglishCounts.values())
LogRatio = [math.log((EnglishCounts[R] + 1) / Total * 29) for R in range(29)]  # log P_eng / P_uniform
print(f"\nB. unused numbers as base-29 running keys (English log-likelihood ratio; English text ~ +{sum(EnglishCounts[R] / Total * LogRatio[R] for R in range(29)):.2f}/rune, random ~ -0.6/rune)")
Rng = random.Random(7)
for Label, Number in Numbers.items():
    Digits = Base29Digits(Number)
    BestRow = (-9, "")
    for Order_ in ("msd", "lsd"):
        Key = Digits if Order_ == "msd" else Digits[::-1]
        for Name, Raw, _ in Inputs:
            for Sign in (1, -1):
                Out = [(int(V) - Sign * K) % 29 for V, K in zip(Raw, Key)]
                Llr = sum(LogRatio[O] for O in Out) / len(Out)
                if Llr > BestRow[0]:
                    BestRow = (Llr, f"{Name} {Order_} sign {Sign:+d}")
    NullBest = []
    for _ in range(200):
        Key = [Rng.randrange(29) for _ in Digits]
        NullBest.append(max(sum(LogRatio[(int(V) - S * K) % 29] for V, K in zip(Raw, Key)) / len(Key)
                            for _, Raw, _ in Inputs for S in (1, -1)))
    NullBest.sort()
    print(f"   {Label:28} digits {len(Digits):3d}  best LLR {BestRow[0]:+.3f} ({BestRow[1]})  null 99th pct {NullBest[197]:+.3f}")

# ---------------- C. Python Mersenne Twister ----------------
print("\nC. Python MT seeds 0..2^18")
Started = time.time()
Gen = random.Random()
BestOverall = []
ChunkSeeds = 4096
for Start in range(0, 1 << 18, ChunkSeeds):
    Py2_29, Py2_28, Py3_29, Py3_28 = [], [], [], []
    for SeedValue in range(Start, Start + ChunkSeeds):
        Gen.seed(SeedValue)
        Floats = [Gen.random() for _ in range(Window)]
        Py2_29.append([int(F * 29) for F in Floats])
        Py2_28.append([int(F * 28) for F in Floats])
        Gen.seed(SeedValue)
        Py3_29.append([Gen.randrange(29) for _ in range(Window)])
        Gen.seed(SeedValue)
        Py3_28.append([Gen.randrange(28) for _ in range(Window)])
    for Variant, K29, K28 in (("py2", Py2_29, Py2_28), ("py3", Py3_29, Py3_28)):
        Best, Where = Score(Inputs, np.array(K29), np.array(K28))
        I = int(np.argmax(Best))
        BestOverall.append((float(Best[I]), Start + I, Variant, Labels[Where[I]]))
BestOverall.sort(reverse=True)
print(f"   {time.time() - Started:.0f}s; top:", [(round(S, 3), Seed, V, L) for S, Seed, V, L in BestOverall[:5]])
