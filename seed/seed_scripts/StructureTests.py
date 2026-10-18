"""Tests of three ideas not found in the published exclusion ledgers.

1. Key resets on layout units (word, sentence, line, page): any key, raw and chain form.
   Detector: coincidence rate of runes (or steps) that share the same position inside a unit.
2. Mathematical sequence keys aligned to the END of a section (key runs backwards).
3. Shift arithmetic done in Latin-alphabetical rune order instead of Gematria order.
Every detector is first run on a synthetic positive control.
"""
import collections
import math
import random
import sys

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403

random.seed(3301)
Sections = LoadAllUnsolved()

# English rune stream (War and Peace) used for synthetic controls
EnglishWords = []
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    Word = [RuneIndex[C] for C in Line.strip() if C in RuneIndex]
    if Word:
        EnglishWords.append(Word)


def AlignedCoincidence(Values, Keys):
    """Pairs sharing a key that also share a value; returns (rate, z vs 1/29)."""
    Groups = collections.defaultdict(list)
    for Value, Key in zip(Values, Keys):
        Groups[Key].append(Value)
    Pairs = Same = 0
    for Members in Groups.values():
        Count = len(Members)
        Pairs += Count * (Count - 1) // 2
        Same += sum(N * (N - 1) // 2 for N in collections.Counter(Members).values())
    if Pairs == 0:
        return float("nan"), float("nan")
    Expected = 1 / 29
    Rate = Same / Pairs
    # conservative z: treat effective sample as number of runes, not pairs
    Effective = len(Values)
    Z = (Rate - Expected) / math.sqrt(Expected * (1 - Expected) * 2 / Effective) if Effective else float("nan")
    return Rate, Z


def SyntheticLike(Section):
    """English plaintext poured into the section's own word/sentence/line/page structure."""
    Stream = []
    WordIndex = random.randrange(len(EnglishWords) - 5000)
    while len(Stream) < len(Section["Runes"]):
        Stream += EnglishWords[WordIndex]
        WordIndex += 1
    return Stream[: len(Section["Runes"])]


def EncryptResetPerUnit(Plain, UnitPositions, Chain, KeyLength=40):
    Key = [random.randrange(29) for _ in range(KeyLength)]
    Out = []
    Previous = random.randrange(29)
    for Value, Position in zip(Plain, UnitPositions):
        K = Key[Position % KeyLength]
        if Chain:
            Previous = (Previous + 1 + (Value + K) % 28) % 29
            Out.append(Previous)
        else:
            Out.append((Value + K) % 29)
    return Out


Units = [("word position", "PosInWord"), ("sentence position", "PosInSentence"),
         ("line position", "PosInLine"), ("page position", "PosInPage")]

print("=== 1. Key reset on layout units (rate of coincidence; random = 0.0345) ===")
Control = Sections[7]  # p40-53, the largest section
for Label, Field in Units:
    Positions = Control[Field]
    Plain = SyntheticLike(Control)
    RawCtl = EncryptResetPerUnit(Plain, Positions, Chain=False)
    ChainCtl = EncryptResetPerUnit(Plain, Positions, Chain=True)
    RawRate, RawZ = AlignedCoincidence(RawCtl, Positions)
    StepRate, StepZ = AlignedCoincidence(Steps(ChainCtl), Positions[1:])
    print(f"CONTROL {Label:18} raw {RawRate:.4f} (z {RawZ:5.1f})   chain-steps {StepRate:.4f} (z {StepZ:5.1f})")
for Label, Field in Units:
    for Section in Sections:
        Positions = Section[Field]
        RawRate, RawZ = AlignedCoincidence(Section["Runes"], Positions)
        StepRate, StepZ = AlignedCoincidence(Steps(Section["Runes"]), Positions[1:])
        Keyed = [(L, P) for L, P in zip(Section["WordLen"], Section["PosInWord"])]
        if Field == "PosInWord":
            LenRate, LenZ = AlignedCoincidence(Section["Runes"], Keyed)
            Extra = f"  (len,pos) raw {LenRate:.4f} z {LenZ:5.1f}"
        else:
            Extra = ""
        print(f"{Section['Name']:7} {Label:18} raw {RawRate:.4f} (z {RawZ:5.1f})   chain-steps {StepRate:.4f} (z {StepZ:5.1f}){Extra}")


# ---------------- 2. Sequences aligned to the end of each section ----------------
def Sequences(Length):
    Primes = FirstPrimes(Length + 200)
    Fib = [0, 1]
    while len(Fib) < Length + 200:
        Fib.append(Fib[-1] + Fib[-2])
    Pi = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"
    yield "primes", Primes
    yield "totient(p)=p-1", [P - 1 for P in Primes]
    yield "naturals", list(range(Length + 200))
    yield "squares", [N * N for N in range(Length + 200)]
    yield "triangular", [N * (N + 1) // 2 for N in range(Length + 200)]
    yield "fibonacci", Fib
    yield "pi digits", [int(D) for D in Pi]
    yield "prime gaps", [B - A for A, B in zip(Primes, Primes[1:])]
    yield "euler phi(n)", [sum(1 for K in range(1, N + 1) if math.gcd(K, N) == 1) for N in range(1, Length + 201)]


def BestReverseSequenceIoc(Values, Window=300, MaxOffset=60):
    Reversed = list(reversed(Values))[:Window]
    StepsReversed = Steps(list(reversed(Values)))[:Window]
    Best = (0, "")
    for Name, Seq in Sequences(Window + MaxOffset + 5):
        for Offset in range(MaxOffset):
            for Sign in (1, -1):
                Raw = [(V - Sign * Seq[I + Offset]) % 29 for I, V in enumerate(Reversed)]
                ChainU = [((S - 1) - Sign * Seq[I + Offset]) % 28 for I, S in enumerate(StepsReversed) if S != 0]
                for Form, Out, Mod in (("raw", Raw, 29), ("chain", ChainU, 28)):
                    Score = Ioc(Out, Mod)
                    if Score > Best[0]:
                        Best = (Score, f"{Name} offset {Offset} sign {Sign:+d} {Form}")
    return Best


print("\n=== 2. Sequence keys running backwards from the end of each section ===")
Plain = SyntheticLike(Sections[0])
Primes = FirstPrimes(len(Plain) + 10)
KeyRev = [P - 1 for P in Primes][: len(Plain)][::-1]  # totient key applied from the end
ControlCipher = [(V + K) % 29 for V, K in zip(Plain, KeyRev)]
print("CONTROL (totient key from the end):", BestReverseSequenceIoc(ControlCipher))
for Section in Sections:
    Score, Label = BestReverseSequenceIoc(Section["Runes"])
    print(f"{Section['Name']:7} best IoC {Score:.3f}  {Label}")

# ---------------- 3. Latin-alphabetical rune order ----------------
AlphaOrder = sorted(range(29), key=lambda I: LatinNames[I])
ToAlpha = {Old: New for New, Old in enumerate(AlphaOrder)}
Keywords = ["DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE", "CIRCUMFERENCES", "INSTAR", "EMERGE", "PARABLE",
            "CICADA", "PRIMES", "TOTIENT", "SACRED", "PILGRIM", "WISDOM", "KOAN", "LIBERPRIMUS", "DEEPWEB",
            "ENLIGHTENMENT", "CONSCIOUSNESS", "SHADOWS", "AETHEREAL", "MOBIUS", "CABAL", "OBSCURA", "THREETHREEZEROONE"]


def BestKeywordIoc(Values, Mod=29):
    Best = (0, "")
    for Word in Keywords:
        KeyIdx = [ToAlpha[V] for V in LatinToRunes(Word)]
        for Sign in (1, -1):
            Out = [(V - Sign * KeyIdx[I % len(KeyIdx)]) % 29 for I, V in enumerate(Values)]
            Score = Ioc(Out)
            if Score > Best[0]:
                Best = (Score, f"{Word} sign {Sign:+d}")
    return Best


print("\n=== 3. Shifts in Latin-alphabetical order (keywords + forward sequences) ===")
Plain = SyntheticLike(Sections[0])
PlainAlpha = [ToAlpha[V] for V in Plain]
KeyIdx = [ToAlpha[V] for V in LatinToRunes("DIVINITY")]
ControlAlpha = [(V + KeyIdx[I % len(KeyIdx)]) % 29 for I, V in enumerate(PlainAlpha)]
print("CONTROL (DIVINITY in alpha order):", BestKeywordIoc(ControlAlpha))
for Section in Sections:
    AlphaValues = [ToAlpha[V] for V in Section["Runes"]]
    Score, Label = BestKeywordIoc(AlphaValues[:600])
    SeqBest = (0, "")
    for Name, Seq in Sequences(700):
        for Offset in range(40):
            for Sign in (1, -1):
                Out = [(V - Sign * Seq[I + Offset]) % 29 for I, V in enumerate(AlphaValues[:600])]
                S = Ioc(Out)
                if S > SeqBest[0]:
                    SeqBest = (S, f"{Name} off {Offset} sign {Sign:+d}")
    print(f"{Section['Name']:7} keyword best {Score:.3f} ({Label})   sequence best {SeqBest[0]:.3f} ({SeqBest[1]})")
