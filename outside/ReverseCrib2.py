"""Reverse crib v2: common-word dictionary (War and Peace corpus words seen 3+ times, plus LP solved vocabulary),
every word checked (chain forms check the first word minus its unknown first rune against suffixes)."""
import sys, re, collections, time
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as Windows
sys.path.insert(0, ".")
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from CribTest import TitleCipher, Families, RunesOf, Pages
from LpCore import *

Freq = collections.Counter()
for Line in open("/tmp/LiberPrayground/data/baseline-rune-words.txt", encoding="utf-8"):
    W = tuple(RunesOf(Line.strip()))
    if W:
        Freq[W] += 1
Common = {W for W, N in Freq.items() if N >= 3}
for F in ["solved_0_warning", "solved_0_welcome", "solved_0_wisdom", "solved_0_koan_1", "solved_0_loss_of_divinity", "solved_jpg107-167", "solved_jpg229", "solved_p56_an_end", "solved_p57_parable"]:
    for W in re.split(r"[•⁘⁚⁜\s|]+", open(Pages + F + ".txt", encoding="utf-8").read()):
        R = tuple(RunesOf(W))
        if R:
            Common.add(R)
            Freq[R] += 3
Pow = 29 ** np.arange(13, dtype=np.int64)
def Code(W): return sum(int(V) * int(Pow[I]) for I, V in enumerate(W))
Full = collections.defaultdict(set); Suffix = collections.defaultdict(set)
for W in Common:
    if len(W) <= 12:
        Full[len(W)].add(Code(W))
        if len(W) >= 2:
            Suffix[len(W)].add(Code(W[1:]))
Full = {L: np.array(sorted(S)) for L, S in Full.items()}
Suffix = {L: np.array(sorted(S)) for L, S in Suffix.items()}
print("common words by length:", {L: len(S) for L, S in sorted(Full.items())})

Titles = {N: TitleCipher(N) for N in ["p0-2", "p3-7", "p15-22", "p23-26", "p27-32", "p33-39", "p54-55"]}
Counts = collections.Counter(); Hits = []

def Check(P, Pos, WL, Chain, First):
    if Chain and First:
        if WL == 1: return np.ones(P.shape[0], bool)
        C = (P[:, Pos + 1:Pos + WL] * Pow[:WL - 1]).sum(axis=1)
        return np.isin(C, Suffix.get(WL, np.array([], dtype=np.int64)))
    C = (P[:, Pos:Pos + WL] * Pow[:WL]).sum(axis=1)
    return np.isin(C, Full.get(WL, np.array([], dtype=np.int64)))

def Scan(KeySeq, Label, Titles, Hits):
    for Name, Words in Titles.items():
        C = np.array(sum(Words, []), dtype=np.int64); L = len(C)
        if len(KeySeq) < L: continue
        K = Windows(KeySeq, L); Lens = [len(W) for W in Words]
        Steps = np.concatenate([[0], (C[1:] - C[:-1]) % 29])
        for Form in ("c-k", "k-c", "c+k", "s-k", "k-s", "s+k"):
            P = {"c-k": C - K, "k-c": K - C, "c+k": C + K, "s-k": Steps - K, "k-s": K - Steps, "s+k": Steps + K}[Form] % 29
            Chain = Form in ("s-k", "k-s", "s+k")
            Ok = np.ones(P.shape[0], bool); Pos = 0
            for WI, WL in enumerate(Lens):
                Ok &= Check(P, Pos, WL, Chain, WI == 0); Pos += WL
                if not Ok.any(): break
            for Idx in np.nonzero(Ok)[0]:
                Text = list(P[Idx]); Pos = 0; Score = 0.0; Parts = []
                for WI, WL in enumerate(Lens):
                    W = tuple(Text[Pos:Pos + WL]); Pos += WL
                    Parts.append(("?" if Chain and WI == 0 else "") + ToLatin(list(W[1:] if Chain and WI == 0 else W)))
                    Score += np.log(1 + Freq.get(W, 0)) if not (Chain and WI == 0) else 0
                Hits.append((round(Score, 1), Name, Form, Label, int(Idx), " ".join(Parts)))

Started = time.time()
for FamName, Arr in Families.items():
    Strides = [1, 2, 3, 5, 7, 11, 13, 17] if FamName.startswith("solved") else range(1, 17)
    for D in Strides:
        for R in range(D):
            for Dir in (1, -1):
                Scan(Arr[R::D][::Dir] % 29, f"{FamName} s{D} r{R} d{Dir}", Titles, Hits)
print(f"scanned in {time.time() - Started:.0f}s; hits: {len(Hits)}")
print("hits by title/form:", collections.Counter((H[1], H[2]) for H in Hits).most_common(20))
for H in sorted(Hits, reverse=True)[:25]:
    print("  ", H)
Ctrl = LatinToRunes("A") + LatinToRunes("REMINDER")
Key = (Families["primes"][0::3] % 29)[500:509]
CtrlTitles = {"CONTROL": [[(Ctrl[0] + Key[0]) % 29], [(Ctrl[I] + Key[I]) % 29 for I in range(1, 9)]]}
CH = []; Scan(Families["primes"][0::3] % 29, "primes s3", CtrlTitles, CH)
print("control:", [H for H in CH if H[4] == 500])
