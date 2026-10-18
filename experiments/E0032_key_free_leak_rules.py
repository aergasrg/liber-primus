"""E0032 (B25): key-free tests of the council's repeat-avoiding leak rules.

Common core under test (council midpoint, docs/council/2026-10-18/08): each ciphertext rune is drawn from the
28 runes other than an excluded symbol h; normally h = c_(i-1) (no doublets); a control law sometimes moves
h, and only then can a doublet appear (1/28). The laws differ in when h moves. H0 for every statistic: the
symmetric memoryless chain (doublets at independent positions, non-zero steps iid uniform on 1..28).

Preregistered family (fixed in this file and committed before the real stage ran). Doublet at global
index i: c_i = c_(i-1), both in one section. All quantities stay inside sections.
  T1 LagCoinc   R_k = #{c_i = c_(i-k)}, k = 2..10, pooled over sections; z_k from the Markov null mean and
                sd; T1 = -min_k z_k (deficit, upper). Rule (stale register, h = c_(i-4) one time in five):
                R_4 deficit. Also per-lag z, per-section R_4, and E0027's surrogate (non-zero steps permuted
                within pages) as a second null for T1.
  T2 PrevGate   3 conditioning variables at the doublets: s_(i-1), s_(i+1), c_(i-2) (undefined at section
                edges: dropped). For each, chi2 of the 29-bin histogram at the doublets against the exposure
                histogram of all candidate positions, and a scan: max over the 29 contiguous 5-sets
                {a..a+4} mod 29 of (observed - expected). T2 = min-p over these 6 (calibrated in the null).
  T3 Checksum   running states z_i, the state before c_i: sum_(j<i) c_j mod 29 (from section start),
                sum_(j<i) prime(c_j) mod 29, local index i mod 29 from section start, and from page start.
                Per section, max over 29 phases of the doublets with z in {a..a+4}; summed over sections.
                T3 = min-p over the 4 states.
  T4 StepBand   among non-zero steps, z of the {1..5} share and of the {24..28} share against 5/28
                (binomial, exact under H0); T4 = max |z| (two-sided).
  T5 Guard/word T5a: renewal fit of within-section gaps G = R + Geom(q) on {1,2,..}; LR = 2 (logL(R=5) -
                logL(R=0)) (upper). T5b: same-word doublet pairs whose in-word separation is not divisible
                by 5 (rule: 0); identifiable only if the expected number of same-word pairs at the observed
                rate, from the real word lengths, is >= 3, else reported "not identifiable" and left out.
Nulls:
  Placement statistics (T2, T3, T5): 10^5 within-section permutations of the real doublet positions over
  the real ciphertext (E0028 PermutedPositions), variables recomputed at the permuted positions.
  Ciphertext statistics (T1, T4): 10^4 synthetic corpora from the memoryless Markov chain at the observed
  rate P(stay) = 86/12947, real section lengths; T1 also against 10^4 E0027 surrogates.
  Family-wise: (i) Bonferroni, per-statistic p <= 0.01/5 = 0.002; (ii) joint min-p over T1..T5 computed
  on the same 10^4 Markov corpora (every statistic is defined on any corpus).
Positive control (tier 1, before the real data): the common core, plaintext = relikd's solved
plaintext prefix-coded into 28 digits (r <= 26 -> r; 27 -> 27,0; 28 -> 27,1), from a random offset,
tiled; c_i = A[(digit + U_i) mod 28], A = 0..28 minus h, U_i seeded uniform; real section lengths, page
and word layout. Laws, each with 100 plants (stale: 1000, for the R_4 distribution):
  memoryless  selector 5 of 29: h moved to a random rune != c_(i-1)  (construction 1, the calibration)
  stale       with prob 1/5: h = c_(i-4)                              (construction 4) -> T1
  prevstep    s_(i-1) in a random contiguous 5-set: h moved randomly  (construction 2) -> T2
  checksum    (a + sum_(j<i) c_j) mod 29 in {0..4}, a per section: h moved randomly (construction 3) -> T3
  band        selector 5 of 29: h = c_(i-1) + d, d uniform 1..5      (construction 7) -> T4
  guard       memoryless, but no move within 5 runes after a doublet  (construction 8) -> T5a
  wordlane    per word phase b in 0..4: h moved randomly at in-word index j = b mod 5 (construction 5) -> T5b
Checks: (a) doublet rate 0.53-0.82%; (b) the matching statistic at p <= 0.002 (Markov-null critical value)
in >= 95/100, else "not identifiable" for that law; (c) memoryless flagged at about the nominal rate;
also each law's own distribution of its statistic, and where the real value falls in it.
Stages: control, real, report.  Usage: python3 experiments/E0032_key_free_leak_rules.py STAGE
Outputs: results/E0032/ (small JSON/text); checkpoints gitignored.
"""
import importlib.util
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.data import LoadAllUnsolved, LoadSection, Pages, RepoRoot  # noqa: E402
from lp.gematria import GpPrimes  # noqa: E402


def LoadExperiment(Name, File):
    Spec = importlib.util.spec_from_file_location(Name, os.path.join(RepoRoot, "experiments", File))
    Mod = importlib.util.module_from_spec(Spec)
    Spec.loader.exec_module(Mod)
    return Mod


E28 = LoadExperiment("E0028", "E0028_doublet_event_process.py")
E27 = LoadExperiment("E0027", "E0027_step_periodicity_pages.py")

OutDir = os.path.join(RepoRoot, "results", "E0032")
CheckDir = os.path.join(OutDir, "checkpoint")
Lags = np.arange(2, 11)
MarkovCount = 10000
PermCount = 100000
SurrogateCount = 10000
Plants = 100
StalePlants = 1000
PerStatAlpha = 0.01 / 5
Laws = ["memoryless", "stale", "prevstep", "checksum", "band", "guard", "wordlane"]
Matching = {"memoryless": None, "stale": "T1", "prevstep": "T2", "checksum": "T3", "band": "T4",
            "guard": "T5a", "wordlane": "T5b"}
SubT2 = ["PrevChi2", "PrevScan", "NextChi2", "NextScan", "Back2Chi2", "Back2Scan"]
SubT3 = ["SumIdx", "SumPrime", "PosSection", "PosPage"]
Primes29 = np.array(GpPrimes, dtype=np.int64) % 29
SolvedNames = ["solved_0_warning", "solved_0_welcome", "solved_0_wisdom", "solved_0_koan_1",
               "solved_0_loss_of_divinity", "solved_jpg107-167", "solved_jpg229", "solved_p56_an_end",
               "solved_p57_parable"]


def Log(Message):
    print(time.strftime("%H:%M:%S"), Message, flush=True)


def SaveJson(Path, Obj):
    os.makedirs(os.path.dirname(Path), exist_ok=True)
    with open(Path + ".tmp", "w") as Handle:
        json.dump(Obj, Handle, separators=(",", ":"), default=lambda X: X.item() if hasattr(X, "item") else X.tolist())
    os.replace(Path + ".tmp", Path)


def BuildLayout():
    """E0028's layout plus page-local index and in-word index per position."""
    Lay = E28.BuildLayout()
    PageLocal, WordIndex = [], []
    for S in LoadAllUnsolved():
        for _, Runes in Pages(S):
            PageLocal += list(range(len(Runes)))
        Prev, J = None, 0
        for W in S["WordId"]:
            J = J + 1 if W == Prev else 0
            WordIndex.append(J)
            Prev = W
    Lay["PageLocal"] = np.array(PageLocal, dtype=np.int64)
    Lay["WordIndex"] = np.array(WordIndex, dtype=np.int64)
    Lay["Starts"] = np.concatenate([[0], np.cumsum(Lay["Lengths"])])
    Lay["Real"] = np.asarray(Lay["Runes"], dtype=np.int64)
    return Lay


# ---------------------------------------------------------------- statistics

def Doublets(Runes, Lay):
    return E28.ExtractDoublets(Runes, Lay)


def LagCounts(Runes, Lay):
    """R_k pooled over sections, k in Lags, and per-section R_4."""
    Out = np.zeros(len(Lags), dtype=np.int64)
    Per4 = []
    for A, B in zip(Lay["Starts"][:-1], Lay["Starts"][1:]):
        C = Runes[A:B]
        for K, Lag in enumerate(Lags):
            Same = int(np.sum(C[Lag:] == C[:-Lag]))
            Out[K] += Same
            if Lag == 4:
                Per4.append(Same)
    return Out, Per4


def StepBand(Runes, Lay):
    Counts = np.zeros(29, dtype=np.int64)
    for A, B in zip(Lay["Starts"][:-1], Lay["Starts"][1:]):
        C = Runes[A:B]
        Counts += np.bincount((C[1:] - C[:-1]) % 29, minlength=29)
    N = Counts[1:].sum()
    P = 5 / 28
    Sd = math.sqrt(N * P * (1 - P))
    Low, High = (Counts[1:6].sum() - N * P) / Sd, (Counts[24:29].sum() - N * P) / Sd
    return float(max(abs(Low), abs(High))), float(Low), float(High), Counts


def ConditioningArrays(Runes, Lay):
    """Per position: s_(i-1), s_(i+1), c_(i-2) (-1 where undefined) and the exposure mask."""
    N = Lay["Total"]
    Local = Lay["Local"]
    SecLen = Lay["Lengths"][Lay["Section"]]
    Prev = np.full(N, -1)
    Next = np.full(N, -1)
    Back2 = np.full(N, -1)
    Ok = Local >= 2
    Idx = np.flatnonzero(Ok)
    Prev[Idx] = (Runes[Idx - 1] - Runes[Idx - 2]) % 29
    Back2[Idx] = Runes[Idx - 2]
    Ok2 = (Local >= 1) & (Local <= SecLen - 2)
    Idx = np.flatnonzero(Ok2)
    Next[Idx] = (Runes[Idx + 1] - Runes[Idx]) % 29
    return [Prev, Next, Back2]


def RunningStates(Runes, Lay):
    """Per position: the 4 running states before c_i (mod 29)."""
    SumIdx = np.zeros(Lay["Total"], dtype=np.int64)
    SumPrime = np.zeros(Lay["Total"], dtype=np.int64)
    for A, B in zip(Lay["Starts"][:-1], Lay["Starts"][1:]):
        C = Runes[A:B]
        SumIdx[A:B] = np.r_[0, np.cumsum(C)[:-1]] % 29
        SumPrime[A:B] = np.r_[0, np.cumsum(Primes29[C])[:-1]] % 29
    return [SumIdx, SumPrime, Lay["Local"] % 29, Lay["PageLocal"] % 29]


def WindowSums(Hist):
    """(..., 29) -> (..., 29): sums over the circular 5-sets {a..a+4}."""
    return sum(np.roll(Hist, -K, axis=-1) for K in range(5))


def PrevGateSubs(PosBatch, Cond, Exposure):
    """PosBatch (M, D) global positions -> (M, 6) sub-statistics of T2."""
    Out = []
    for V, (Share, Valid) in zip(Cond, Exposure):
        Vals = V[PosBatch]
        Ok = Vals >= 0
        Hist = np.zeros((PosBatch.shape[0], 29))
        Rows = np.repeat(np.arange(PosBatch.shape[0]), PosBatch.shape[1])
        np.add.at(Hist, (Rows[Ok.ravel()], Vals.ravel()[Ok.ravel()]), 1)
        Expected = Ok.sum(axis=1, keepdims=True) * Share
        Chi2 = np.sum(np.where(Valid, (Hist - Expected) ** 2 / np.maximum(Expected, 1e-12), 0), axis=1)
        Scan = WindowSums(Hist - Expected).max(axis=1)
        Out += [Chi2, Scan]
    return np.column_stack(Out)


def ExposureShares(Cond, Lay):
    Out = []
    Cand = Lay["IsCandidate"]
    for V in Cond:
        Vals = V[Cand & (V >= 0)]
        Share = np.bincount(Vals, minlength=29) / len(Vals)
        Out.append((Share, Share > 0))
    return Out


def ChecksumSubs(PosBatch, States, Lay):
    """(M, D) -> (M, 4): per state, sum over sections of max over phases of doublets in a 5-window."""
    SecOf = Lay["Section"][PosBatch]
    Out = []
    M = PosBatch.shape[0]
    Rows = np.repeat(np.arange(M), PosBatch.shape[1])
    for St in States:
        Hist = np.zeros((M, len(Lay["Lengths"]), 29))
        np.add.at(Hist, (Rows, SecOf.ravel(), St[PosBatch].ravel()), 1)
        Out.append(WindowSums(Hist).max(axis=2).sum(axis=1))
    return np.column_stack(Out)


def GuardLR(PosBatch, Lay):
    """(M, D) sorted positions -> (M,) LR of R = 5 against R = 0 on within-section gaps."""
    Sec = Lay["Section"][PosBatch]
    Gaps = np.diff(PosBatch, axis=1)
    Same = Sec[:, 1:] == Sec[:, :-1]
    Out = np.empty(PosBatch.shape[0])
    for M in range(PosBatch.shape[0]):
        G = Gaps[M][Same[M]].astype(np.float64)
        Out[M] = 2 * (GeomLogL(G - 5) - GeomLogL(G)) if G.min() > 5 else -np.inf
    return Out


def GeomLogL(X):
    """Max log-likelihood of X (all >= 1) under Geom(q) on {1, 2, ...}."""
    N, S = len(X), X.sum()
    Q = N / S
    return N * math.log(Q) + (S - N) * math.log(1 - Q) if Q < 1 else 0.0


def WordLane(Pos, Lay):
    """(same-word doublet pairs, those with separation not divisible by 5)."""
    InWord = Pos[Lay["WordG"][Pos] == Lay["WordG"][Pos - 1]]
    Pairs = Bad = 0
    Words = Lay["WordG"][InWord]
    for W in np.unique(Words):
        J = Lay["WordIndex"][InWord[Words == W]]
        for A in range(len(J)):
            for B in range(A + 1, len(J)):
                Pairs += 1
                Bad += (J[B] - J[A]) % 5 != 0
    return Pairs, Bad


def WordLanePower(Lay, Pos):
    """Expected same-word doublet pairs at the observed in-word rate, from the real word lengths."""
    InWordPairs = Lay["IsCandidate"] & (Lay["WordG"] == np.roll(Lay["WordG"], 1))
    Rate = np.sum(Lay["WordG"][Pos] == Lay["WordG"][Pos - 1]) / InWordPairs.sum()
    _, Lengths = np.unique(Lay["WordG"], return_counts=True)
    Slots = Lengths - 1
    return float(np.sum(Slots * (Slots - 1) / 2) * Rate ** 2), float(Rate)


def CorpusStats(Runes, Lay, Ref):
    """Raw values of every statistic on one corpus (its own doublets)."""
    Pos = Doublets(Runes, Lay)
    R, Per4 = LagCounts(Runes, Lay)
    Cond = ConditioningArrays(Runes, Lay)
    Exposure = ExposureShares(Cond, Lay)
    Out = {"D": len(Pos), "R": R.tolist(), "R4PerSection": Per4}
    Out["T2Subs"] = PrevGateSubs(Pos[None, :], Cond, Exposure)[0].tolist() if len(Pos) else [0.0] * 6
    Out["T3Subs"] = ChecksumSubs(Pos[None, :], RunningStates(Runes, Lay), Lay)[0].tolist() if len(Pos) else [0.0] * 4
    Out["T4"], Out["BandLow"], Out["BandHigh"], _ = StepBand(Runes, Lay)
    Out["T5a"] = float(GuardLR(Pos[None, :], Lay)[0]) if len(Pos) > 2 else -np.inf
    Out["T5b"] = list(WordLane(Pos, Lay))
    if Ref is not None:
        Out["Z"] = ((R - Ref["RMean"]) / Ref["RSd"]).tolist()
        Out["T1"] = float(-min(Out["Z"]))
    return Out


# ---------------------------------------------------------------- generators

def MarkovCorpus(Lay, Rng, Stay):
    Steps = np.where(Rng.random(Lay["Total"]) < Stay, 0, Rng.integers(1, 29, Lay["Total"]))
    Out = np.empty(Lay["Total"], dtype=np.int64)
    for A, B in zip(Lay["Starts"][:-1], Lay["Starts"][1:]):
        S = Steps[A:B].copy()
        S[0] = Rng.integers(29)
        Out[A:B] = np.cumsum(S) % 29
    return Out


def SurrogateCorpus(Lay, Seed):
    """E0027's surrogate (non-zero steps permuted within pages) as one global array."""
    Layout = E27.SurrogateLayout(E27.RealLayout(), Seed)
    return np.concatenate([np.asarray(R) for _, PageList in Layout for _, R in PageList]).astype(np.int64)


def PlainDigits():
    Plain = []
    for Name in SolvedNames:
        Plain += LoadSection(Name)["Runes"]
    Digits = []
    for R in Plain:
        Digits += [R] if R <= 26 else [27, R - 27]
    return np.array(Digits, dtype=np.int64)


def PlantCorpus(Law, Lay, Rng, Digits):
    Total = Lay["Total"]
    Start = int(Rng.integers(len(Digits)))
    D = np.resize(np.roll(Digits, -Start), Total)
    U = Rng.integers(0, 28, Total)
    Sel = Rng.integers(0, 29, Total)
    Move = Rng.integers(1, 29, Total)  # random displacement of h away from c_(i-1)
    Band = Rng.integers(1, 6, Total)
    Stale = Rng.random(Total) < 0.2
    GateA = int(Rng.integers(29))
    Phase = Rng.integers(0, 29, len(Lay["Lengths"])).tolist()
    WordPhase = Rng.integers(0, 5, int(Lay["WordG"].max()) + 1).tolist()
    D, U, Sel, Move, Band, Stale = (X.tolist() for X in (D, U, Sel, Move, Band, Stale))
    WordIndex, WordG = Lay["WordIndex"].tolist(), Lay["WordG"].tolist()
    Out = np.empty(Total, dtype=np.int64)
    for S, (A, B) in enumerate(zip(Lay["Starts"][:-1], Lay["Starts"][1:])):
        C = [0] * (B - A)
        C[0] = int(Rng.integers(29))
        Sum = int(C[0])
        Guard = 0
        for I in range(1, B - A):
            G = A + I
            Prev = C[I - 1]
            H = Prev
            if Law == "memoryless" or (Law == "guard" and Guard == 0):
                if Sel[G] < 5:
                    H = (Prev + Move[G]) % 29
            elif Law == "stale":
                if Stale[G] and I >= 4:
                    H = C[I - 4]
            elif Law == "prevstep":
                if I >= 2 and (C[I - 1] - C[I - 2] - GateA) % 29 < 5:
                    H = (Prev + Move[G]) % 29
            elif Law == "checksum":
                if (Phase[S] + Sum) % 29 < 5:
                    H = (Prev + Move[G]) % 29
            elif Law == "band":
                if Sel[G] < 5:
                    H = (Prev + Band[G]) % 29
            elif Law == "wordlane":
                if WordIndex[G] % 5 == WordPhase[WordG[G]]:
                    H = (Prev + Move[G]) % 29
            X = (D[G] + U[G]) % 28
            C[I] = X if X < H else X + 1
            Sum += C[I]
            if Law == "guard":
                Guard = 5 if C[I] == Prev else max(0, Guard - 1)
        Out[A:B] = C
    return Out


# ---------------------------------------------------------------- null tables

def MarkovReference(Lay, Stay):
    """10^4 Markov corpora: R mean/sd, and every statistic's null values (checkpointed)."""
    Path = os.path.join(CheckDir, "markov.json")
    if os.path.exists(Path):
        Ref = json.load(open(Path))
        for K in ("RMean", "RSd"):
            Ref[K] = np.array(Ref[K])
        return Ref
    Rng = np.random.default_rng(32)
    Rows = []
    T = time.time()
    for M in range(MarkovCount):
        Rows.append(CorpusStats(MarkovCorpus(Lay, Rng, Stay), Lay, None))
        if (M + 1) % 1000 == 0:
            Log(f"markov {M + 1}/{MarkovCount} ({time.time() - T:.0f}s)")
    R = np.array([Row["R"] for Row in Rows], dtype=np.float64)
    Ref = {"RMean": R.mean(axis=0), "RSd": R.std(axis=0, ddof=1)}
    Z = (R - Ref["RMean"]) / Ref["RSd"]
    Table = {"D": [Row["D"] for Row in Rows], "T1": (-Z.min(axis=1)).tolist(),
             "T2Subs": [Row["T2Subs"] for Row in Rows], "T3Subs": [Row["T3Subs"] for Row in Rows],
             "T4": [Row["T4"] for Row in Rows], "T5a": [Row["T5a"] for Row in Rows],
             "R4": R[:, list(Lags).index(4)].tolist()}
    Out = {"RMean": Ref["RMean"].tolist(), "RSd": Ref["RSd"].tolist(), "Table": Table}
    SaveJson(Path, Out)
    Out["RMean"], Out["RSd"] = Ref["RMean"], Ref["RSd"]
    return Out


def UpperP(Value, Null):
    Null = np.asarray(Null, dtype=np.float64)
    return float((1 + np.sum(Null >= Value - 1e-12)) / (1 + len(Null)))


def MinPCombine(Subs, NullSubs):
    """Min over columns of upper p (vs NullSubs), and the null distribution of that min-p (rank based)."""
    NullSubs = np.asarray(NullSubs, dtype=np.float64)
    N = NullSubs.shape[0]
    Ranks = np.empty_like(NullSubs)
    for K in range(NullSubs.shape[1]):
        Col = NullSubs[:, K]
        Order = np.sort(Col)
        Ranks[:, K] = (1 + N - np.searchsorted(Order, Col - 1e-12, side="left")) / (1 + N)
    NullMinP = Ranks.min(axis=1)
    Subs = np.atleast_2d(Subs)
    P = np.array([[UpperP(V, NullSubs[:, K]) for K, V in enumerate(Row)] for Row in Subs])
    return P.min(axis=1), P, NullMinP


def LowerP(Value, Null):
    Null = np.asarray(Null, dtype=np.float64)
    return float((1 + np.sum(Null <= Value + 1e-12)) / (1 + len(Null)))


def StatPValues(Stats, Ref):
    """Markov-null p of T1..T5a for one corpus (T2, T3 via their min-p calibration)."""
    Tab = Ref["Table"]
    T2MinP, _, T2Null = MinPCombine(Stats["T2Subs"], Tab["T2Subs"])
    T3MinP, _, T3Null = MinPCombine(Stats["T3Subs"], Tab["T3Subs"])
    return {"T1": UpperP(Stats["T1"], Tab["T1"]), "T2": LowerP(T2MinP[0], T2Null),
            "T3": LowerP(T3MinP[0], T3Null), "T4": UpperP(Stats["T4"], Tab["T4"]),
            "T5a": UpperP(Stats["T5a"], Tab["T5a"])}


# ---------------------------------------------------------------- stages

def Setup():
    Lay = BuildLayout()
    RealPos = Doublets(Lay["Real"], Lay)
    Pairs = int(Lay["IsCandidate"].sum())
    Stay = len(RealPos) / Pairs
    return Lay, RealPos, Stay


def StageControl():
    Lay, RealPos, Stay = Setup()
    Ref = MarkovReference(Lay, Stay)
    Digits = PlainDigits()
    Expected, InRate = WordLanePower(Lay, RealPos)
    Log(f"word lanes: expected same-word doublet pairs {Expected:.2f} (in-word rate {InRate:.4f})")
    Path = os.path.join(CheckDir, "plants.json")
    Done = json.load(open(Path)) if os.path.exists(Path) else {}
    for Law in Laws:
        Count = StalePlants if Law == "stale" else Plants
        Rows = Done.get(Law, [])
        Rng = np.random.default_rng(320 + Laws.index(Law) * 7919 + len(Rows))
        T = time.time()
        while len(Rows) < Count:
            Stats = CorpusStats(PlantCorpus(Law, Lay, Rng, Digits), Lay, Ref)
            Stats["P"] = StatPValues(Stats, Ref)
            Rows.append(Stats)
            if len(Rows) % 50 == 0:
                Done[Law] = Rows
                SaveJson(Path, Done)
                Log(f"plants {Law} {len(Rows)}/{Count} ({time.time() - T:.0f}s)")
        Done[Law] = Rows
        SaveJson(Path, Done)
    Summary = {"word_lane_expected_pairs": Expected, "word_lane_identifiable": Expected >= 3}
    for Law in Laws:
        Rows = Done[Law]
        Rates = [Row["D"] / int(Lay["IsCandidate"].sum()) for Row in Rows]
        Flags = {K: int(sum(Row["P"][K] <= PerStatAlpha for Row in Rows[:Plants])) for K in ("T1", "T2", "T3", "T4", "T5a")}
        Flags["T5b_zero_bad_of_pairs"] = int(sum(Row["T5b"][1] == 0 and Row["T5b"][0] > 0 for Row in Rows[:Plants]))
        Summary[Law] = {"plants": len(Rows), "rate_min": round(min(Rates) * 100, 3), "rate_max": round(max(Rates) * 100, 3),
                        "rate_mean": round(float(np.mean(Rates)) * 100, 3), "flagged_of_100": Flags,
                        "matching": Matching[Law]}
        Log(f"{Law}: rate {Summary[Law]['rate_mean']}% [{Summary[Law]['rate_min']}, {Summary[Law]['rate_max']}], flagged {Flags}")
    SaveJson(os.path.join(OutDir, "control.json"), Summary)


def StageReal():
    Lay, RealPos, Stay = Setup()
    Ref = MarkovReference(Lay, Stay)
    Real = CorpusStats(Lay["Real"], Lay, Ref)
    Real["P_markov"] = StatPValues(Real, Ref)
    Tab = Ref["Table"]
    # E0027 surrogates for T1
    SurPath = os.path.join(CheckDir, "surrogate_R.json")
    SurR = json.load(open(SurPath)) if os.path.exists(SurPath) else []
    T = time.time()
    while len(SurR) < SurrogateCount:
        SurR.append(LagCounts(SurrogateCorpus(Lay, 27000 + len(SurR)), Lay)[0].tolist())
        if len(SurR) % 1000 == 0:
            SaveJson(SurPath, SurR)
            Log(f"surrogates {len(SurR)}/{SurrogateCount} ({time.time() - T:.0f}s)")
    Sur = np.array(SurR, dtype=np.float64)
    SurZ = (Sur - Sur.mean(axis=0)) / Sur.std(axis=0, ddof=1)
    RealSurZ = (np.array(Real["R"]) - Sur.mean(axis=0)) / Sur.std(axis=0, ddof=1)
    Real["SurrogateZ"] = RealSurZ.tolist()
    Real["SurrogateMean"] = Sur.mean(axis=0).tolist()
    Real["P_T1_surrogate"] = UpperP(-RealSurZ.min(), -SurZ.min(axis=1))
    # permutation null for the placement statistics
    PermPath = os.path.join(CheckDir, "perm.npz")
    Cond = ConditioningArrays(Lay["Real"], Lay)
    Exposure = ExposureShares(Cond, Lay)
    States = RunningStates(Lay["Real"], Lay)
    Lay["Counts"] = np.bincount(Lay["Section"][RealPos], minlength=len(Lay["Lengths"]))
    if os.path.exists(PermPath):
        Saved = np.load(PermPath)
        Blocks = [Saved["Subs"]]
    else:
        Blocks = []
    Rng = np.random.default_rng(3205 + sum(len(B) for B in Blocks))
    T = time.time()
    while sum(len(B) for B in Blocks) < PermCount:
        Pos = E28.PermutedPositions(Lay, 2000, Rng)
        Pos.sort(axis=1)
        Blocks.append(np.column_stack([PrevGateSubs(Pos, Cond, Exposure), ChecksumSubs(Pos, States, Lay), GuardLR(Pos, Lay)]))
        np.savez(PermPath, Subs=np.concatenate(Blocks))
        Log(f"permutations {sum(len(B) for B in Blocks)}/{PermCount} ({time.time() - T:.0f}s)")
    Perm = np.concatenate(Blocks)[:PermCount]
    T2MinP, T2SubP, T2Null = MinPCombine(Real["T2Subs"], Perm[:, :6])
    T3MinP, T3SubP, T3Null = MinPCombine(Real["T3Subs"], Perm[:, 6:10])
    Real["P_perm"] = {"T2": LowerP(T2MinP[0], T2Null), "T2Subs": dict(zip(SubT2, T2SubP[0].tolist())),
                      "T3": LowerP(T3MinP[0], T3Null), "T3Subs": dict(zip(SubT3, T3SubP[0].tolist())),
                      "T5a": UpperP(Real["T5a"], Perm[:, 10])}
    # joint family-wise min-p on the Markov table
    Expected, _ = WordLanePower(Lay, RealPos)
    Keys = ["T1", "T2", "T3", "T4", "T5a"]
    NullP = np.column_stack([NullStatP(Tab, K) for K in Keys])
    NullMinP = NullP.min(axis=1)
    Primary = {"T1": Real["P_markov"]["T1"], "T2": Real["P_perm"]["T2"], "T3": Real["P_perm"]["T3"],
               "T4": Real["P_markov"]["T4"], "T5a": Real["P_perm"]["T5a"]}
    Real["Primary"] = Primary
    Real["FamilyMinP"] = min(Primary.values())
    Real["FamilyP_joint_markov"] = LowerP(min(Real["P_markov"].values()), NullMinP)
    Real["FamilyP_bonferroni"] = min(1.0, 5 * Real["FamilyMinP"])
    Real["WordLaneExpectedPairs"] = Expected
    Real["NullR4"] = {"mean": float(Ref["RMean"][list(Lags).index(4)]), "sd": float(Ref["RSd"][list(Lags).index(4)])}
    SaveJson(os.path.join(OutDir, "real.json"), Real)
    Log(f"real: R {Real['R']}, z {np.round(Real['Z'], 2).tolist()}, primary p {Primary}")


def NullStatP(Tab, Key):
    """Markov-null p of each null replicate for one statistic (rank based)."""
    if Key in ("T2", "T3"):
        _, _, NullMinP = MinPCombine(np.zeros((1, len(Tab[Key + "Subs"][0]))), Tab[Key + "Subs"])
        Values = -NullMinP  # smaller min-p is more extreme
    else:
        Values = np.asarray(Tab[Key], dtype=np.float64)
    Order = np.sort(Values)
    N = len(Values)
    return (1 + N - np.searchsorted(Order, Values - 1e-12, side="left")) / (1 + N)


def StageReport():
    Real = json.load(open(os.path.join(OutDir, "real.json")))
    Control = json.load(open(os.path.join(OutDir, "control.json")))
    Plants = json.load(open(os.path.join(CheckDir, "plants.json")))
    Lines = ["E0032 (B25): key-free tests of repeat-avoiding leak rules", ""]
    Lines.append(f"Doublets {Real['D']}; word-lane expected same-word pairs {Real['WordLaneExpectedPairs']:.2f} "
                 f"({'identifiable' if Real['WordLaneExpectedPairs'] >= 3 else 'not identifiable: T5b left out'})")
    Lines.append("")
    Lines.append("T1 lag-k coincidences (Markov null mean; z vs Markov; z vs E0027 surrogate):")
    for K, Lag in enumerate(Lags):
        Lines.append(f"    k={Lag}: R {Real['R'][K]}, Markov z {Real['Z'][K]:+.2f}, surrogate z {Real['SurrogateZ'][K]:+.2f}")
    Lines.append(f"    Markov null R_4 mean {Real['NullR4']['mean']:.1f} sd {Real['NullR4']['sd']:.1f}; per-section R_4 {Real['R4PerSection']}")
    Lines.append(f"    T1 = {Real['T1']:.2f}: p Markov {Real['P_markov']['T1']:.4f}, p surrogate {Real['P_T1_surrogate']:.4f}")
    StaleR4 = np.array([Row["R"][list(Lags).index(4)] for Row in Plants["stale"]])
    R4 = Real["R"][list(Lags).index(4)]
    Lines.append(f"    stale-register plants ({len(StaleR4)}): R_4 mean {StaleR4.mean():.1f} sd {StaleR4.std(ddof=1):.1f}, "
                 f"max {StaleR4.max()}; plants with R_4 >= {R4}: {int(np.sum(StaleR4 >= R4))} "
                 f"(real is {(R4 - StaleR4.mean()) / StaleR4.std(ddof=1):+.1f} SD from the rule's prediction)")
    Lines.append("")
    Lines.append(f"T2 preceding-step gate: p perm {Real['P_perm']['T2']:.4f} (Markov {Real['P_markov']['T2']:.4f}); "
                 "subs " + ", ".join(f"{K} {V:.3f}" for K, V in Real["P_perm"]["T2Subs"].items()))
    Lines.append(f"T3 running checksum: p perm {Real['P_perm']['T3']:.4f} (Markov {Real['P_markov']['T3']:.4f}); "
                 f"values {Real['T3Subs']} of {Real['D']}; subs " + ", ".join(f"{K} {V:.3f}" for K, V in Real["P_perm"]["T3Subs"].items()))
    Lines.append(f"T4 step band: z(1..5) {Real['BandLow']:+.2f}, z(24..28) {Real['BandHigh']:+.2f}; p Markov {Real['P_markov']['T4']:.4f}")
    Lines.append(f"T5a guard LR(R=5 vs 0) {Real['T5a']:.2f}: p perm {Real['P_perm']['T5a']:.4f} (Markov {Real['P_markov']['T5a']:.4f})")
    Lines.append(f"T5b same-word pairs {Real['T5b'][0]}, not divisible by 5: {Real['T5b'][1]}")
    Lines.append("")
    Lines.append(f"Family: primary p {Real['Primary']}; min-p {Real['FamilyMinP']:.4f}; Bonferroni {Real['FamilyP_bonferroni']:.4f}; "
                 f"joint Markov min-p {Real['FamilyP_joint_markov']:.4f}")
    Lines.append("")
    Lines.append(f"Positive controls (100 plants per law; flagged = matching p <= {PerStatAlpha}):")
    for Law in Laws:
        C = Control[Law]
        Lines.append(f"    {Law}: doublet rate {C['rate_mean']}% [{C['rate_min']}, {C['rate_max']}]; matching {C['matching']}; flagged {C['flagged_of_100']}")
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    print("\n".join(Lines))


if __name__ == "__main__":
    os.makedirs(CheckDir, exist_ok=True)
    {"control": StageControl, "real": StageReal, "report": StageReport}[sys.argv[1]]()
