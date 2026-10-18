"""Urquhart-style test: the 256 grid numbers as a book code into Liber Primus's own words."""
import collections, math, random, sys
sys.path.insert(0, ".")
from LpCore import *
Grid = list(open("grid60.bin", "rb").read())
Counts = collections.Counter()
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    Counts.update(RuneIndex[C] for C in Line.strip() if C in RuneIndex)
Total = sum(Counts.values()); LogRatio = [math.log((Counts[R] + 1) / Total * 29) for R in range(29)]
def Words(Name):
    S = LoadSection(Name); Out = collections.defaultdict(list)
    for V, W in zip(S["Runes"], S["WordId"]): Out[W].append(V)
    return [Out[K] for K in sorted(Out)]
SolvedOrder = ["solved_0_warning","solved_0_welcome","solved_0_wisdom","solved_0_koan_1","solved_0_loss_of_divinity","solved_p56_an_end","solved_p57_parable"]
Corpora = {"solved plaintext": [W for N in SolvedOrder for W in Words(N)],
           "unsolved cipher words": [W for N in UnsolvedNames for W in Words(N)],
           "p40-53 cipher words": Words("p40-53"), "p54-55 cipher words": Words("p54-55")}
def Score(Letters): return sum(LogRatio[L] for L in Letters) / len(Letters)
Rows = []
for Name, Corpus in Corpora.items():
    N = len(Corpus)
    for Base in (0, 1):
        for Pick, Fn in (("first", lambda W: W[0]), ("last", lambda W: W[-1])):
            for Mode in ("index", "running"):
                Letters, Pos = [], 0
                for V in Grid:
                    if Mode == "index": Idx = (V - Base) % N
                    else: Pos = (Pos + V) % N; Idx = Pos
                    Letters.append(Fn(Corpus[Idx]))
                Rows.append((Score(Letters), Name, Base, Pick, Mode, ToLatin(Letters[:40])))
Rows.sort(reverse=True)
for R in Rows[:5]: print(f"LLR {R[0]:+.3f}  {R[1]}, base {R[2]}, {R[3]} letter, {R[4]}: {R[5]}")
# Control: encode real plaintext as a book code into the solved corpus, then score
Corpus = Corpora["solved plaintext"]; Plain = [V for W in Corpus[300:400] for V in W][:256]
ByFirst = collections.defaultdict(list)
for I, W in enumerate(Corpus[:256]): ByFirst[W[0]].append(I)
Code = [random.choice(ByFirst[L]) for L in Plain if ByFirst[L]]
print(f"control (real book code): LLR {Score([Corpus[I][0] for I in Code]):+.3f}; random numbers: {Score([Corpus[random.randrange(256)][0] for _ in range(256)]):+.3f}")

# Proper detector: English bigram log-likelihood, compared with random index sequences through the same mapping
Big = collections.Counter(); Prev = None
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    W = [RuneIndex[C] for C in Line.strip() if C in RuneIndex]
    for V in W:
        if Prev is not None: Big[(Prev, V)] += 1
        Prev = V
Uni = Counts
def Bi(L): return sum(math.log((Big[(A, B)] + 1) / (Uni[A] + 29)) - math.log((Uni[B] + 1) / Total) for A, B in zip(L, L[1:])) / (len(L) - 1)
Rng = random.Random(1)
print("\nbigram test (gain over unigram; English text ~ +0.5, letters with no sequence ~ 0):")
for Name, Corpus in Corpora.items():
    N = len(Corpus)
    for Pick, Fn in (("first", lambda W: W[0]), ("last", lambda W: W[-1])):
        Real = max(Bi([Fn(Corpus[(V - B) % N]) for V in Grid]) for B in (0, 1))
        Null = sorted(Bi([Fn(Corpus[Rng.randrange(N)]) for _ in Grid]) for _ in range(200))
        print(f"  {Name:22} {Pick:5}: grid {Real:+.3f}   random 99th pct {Null[197]:+.3f}")
Ctrl = [Corpora["solved plaintext"][I][0] for I in Code]
print(f"  control book code: {Bi(Ctrl):+.3f}")
