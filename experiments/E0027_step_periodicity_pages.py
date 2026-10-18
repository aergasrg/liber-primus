"""E0027 (B18): page-local periodic keys in raw, step and chain-unit views, with bounded F-skip masks.

Hypothesis: each LP page (real page map, lp.data.PageLines) is enciphered with its own periodic key of
period L <= n/2, applied to the raw runes (Vigenere) or to the chain steps, with up to 11 ciphertext Fs
passing through without consuming key.

Views per page (first edge of every page omitted; Fs and every step touching an F are left out of the
columns, which makes the two chain conventions for a skipped F - literal F becomes the chain state, or
the F is transparent - shift the key phase identically):
  raw29     c_i mod 29
  step29    s_i = c_i - c_(i-1) mod 29 (zero steps kept as a symbol, consume key)
  unit28z1  u_i = s_i - 1 mod 28 over non-zero steps; a zero step consumes a key symbol
  unit28z2  the same; a zero step does not consume a key symbol
Detector: pair-weighted column IoC as a z score, z = (C - P q) / sqrt(P q (1 - q)), C = same-symbol
pairs in the same column, P = pairs in the same column, q = coincidence rate of the page's own symbols
(for a uniform alphabet, pair coincidences sharing a symbol are uncorrelated, so the binomial variance
is exact under the null).
Skips: a skip mask over a page's ciphertext Fs shifts the phase of every later symbol by one. Pairs are
tabulated per (segment pair, t_j - t_i mod L), so any mask scores in one lookup per segment pair.
Masks: every subset with <= 11 skips if that is <= 4096 subsets, else all subsets with <= K skips, K the
largest that fits in 4096. Skip masks are searched at the top 4 no-skip periods and the top 4
within-segment periods (skip-invariant) of each view.
Statistics of the whole search:
  S1 page-local: max over pages of the page's best z, standardised by that page's surrogate mean and sd
  S2 section-wide: periods 2-300, no skips, max over sections, standardised the same way
  S3 shared period: max over views and L of sum over pages of no-skip z / sqrt(pages)
Null (tier 2): surrogate corpora that permute the non-zero steps within each page (zero positions and
page lengths kept), re-integrated from a random first rune; Fs recomputed. The whole search runs on each.
Control (tier 1): periodic plants in solved plaintext poured into real page layouts (length and doublet
positions), raw Vigenere and chain forms, both skip and zero conventions, 100 plants per condition.

Usage:
  python3 experiments/E0027_step_periodicity_pages.py real
  python3 experiments/E0027_step_periodicity_pages.py surrogates --count 999
  python3 experiments/E0027_step_periodicity_pages.py power --plants 100
  python3 experiments/E0027_step_periodicity_pages.py report
Outputs: results/E0027/ (small text); checkpoints in results/E0027/checkpoint_*/ (gitignored).
"""
import argparse
import itertools
import json
import math
import multiprocessing
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.data import LoadAllUnsolved, Pages, RepoRoot, SolvedPlaintext, SolvedPlainNames  # noqa: E402

OutDir = os.path.join(RepoRoot, "results", "E0027")
CheckpointDir = os.path.join(OutDir, "checkpoint_runs")
ViewNames = ["raw29", "step29", "unit28z1", "unit28z2"]
ViewModulus = {"raw29": 29, "step29": 29, "unit28z1": 28, "unit28z2": 28}
MaxSkips = 11
MaskCap = 4096
CandidatesPerView = 4
PageMaxPeriod = 138
SectionMaxPeriod = 300
WelcomeOrdinals = {4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25}
MaskCache = {}


def BuildViews(Runes):
    """(Symbols, KeyIndex, Segment) per view; Segment = number of ciphertext Fs before the symbol."""
    C = np.asarray(Runes, dtype=np.int64)
    N = len(C)
    FPos = np.flatnonzero(C == 0)
    Index = np.arange(N)
    Views = {}
    Keep = C != 0
    Views["raw29"] = (C[Keep], Index[Keep], np.searchsorted(FPos, Index[Keep]))
    StepIndex = np.arange(1, N)
    S = (C[1:] - C[:-1]) % 29
    Clean = (C[1:] != 0) & (C[:-1] != 0)
    Segment = np.searchsorted(FPos, StepIndex)
    Views["step29"] = (S[Clean], StepIndex[Clean] - 1, Segment[Clean])
    NonZero = Clean & (S != 0)
    Views["unit28z1"] = ((S[NonZero] - 1) % 28, StepIndex[NonZero] - 1, Segment[NonZero])
    ZerosBefore = np.cumsum(S == 0) - (S == 0)
    Views["unit28z2"] = ((S[NonZero] - 1) % 28, (StepIndex - 1 - ZerosBefore)[NonZero], Segment[NonZero])
    return Views, len(FPos)


def CoincidenceRate(Symbols, Modulus):
    N = len(Symbols)
    if N < 2:
        return 1.0 / Modulus
    Counts = np.bincount(Symbols, minlength=Modulus)
    return float((Counts * (Counts - 1)).sum()) / (N * (N - 1))


def ZScore(Same, Pairs, Q):
    Same = np.asarray(Same, dtype=float)
    Pairs = np.asarray(Pairs, dtype=float)
    Denominator = np.sqrt(np.maximum(Pairs * Q * (1 - Q), 1e-12))
    return np.where(Pairs > 0, (Same - Pairs * Q) / Denominator, np.nan)


def RunPairs(Keys, Divisor, Count):
    """Sum over distinct keys of n(n-1)/2, grouped by key // Divisor."""
    Keys = np.sort(Keys)
    Starts = np.flatnonzero(np.r_[True, Keys[1:] != Keys[:-1]])
    Sizes = np.diff(np.r_[Starts, len(Keys)])
    return np.bincount(Keys[Starts] // Divisor, weights=Sizes * (Sizes - 1) / 2.0, minlength=Count)


def ColumnZ(Symbols, KeyIndex, Group, Periods, Modulus):
    """No-skip column z for each period; columns are (Group, KeyIndex mod L)."""
    Periods = np.asarray(Periods, dtype=np.int64)
    if len(Periods) == 0 or len(Symbols) < 2:
        return np.full(len(Periods), np.nan)
    Groups = int(Group.max()) + 1
    Width = Groups * int(Periods.max())
    Column = (np.arange(len(Periods))[:, None] * Groups + Group[None, :]) * int(Periods.max()) \
        + KeyIndex[None, :] % Periods[:, None]
    Pairs = RunPairs(Column.ravel(), Width, len(Periods))
    Same = RunPairs((Column * Modulus + Symbols[None, :]).ravel(), Width * Modulus, len(Periods))
    return ZScore(Same, Pairs, CoincidenceRate(Symbols, Modulus))


def SkipMasks(NumF):
    """(Masks bool [m, NumF], MaxK) with every subset of <= MaxK skips, MaxK <= 11, m <= 4096."""
    if NumF not in MaskCache:
        MaxK = min(MaxSkips, NumF)
        while sum(math.comb(NumF, K) for K in range(MaxK + 1)) > MaskCap:
            MaxK -= 1
        Rows = []
        for K in range(MaxK + 1):
            for Combo in itertools.combinations(range(NumF), K):
                Row = np.zeros(NumF, dtype=bool)
                Row[list(Combo)] = True
                Rows.append(Row)
        Masks = np.array(Rows).reshape(len(Rows), NumF)
        Drift = np.concatenate([np.zeros((len(Rows), 1), dtype=np.int64), np.cumsum(Masks, axis=1)], axis=1)
        MaskCache[NumF] = (Masks, Drift, MaxK)
    return MaskCache[NumF]


def SkipSearch(Symbols, KeyIndex, Segment, Periods, Modulus, Drift):
    """Best z over all skip masks at each period; returns list of (z, mask row)."""
    N = len(Symbols)
    First, Second = np.triu_indices(N, 1)
    Delta = KeyIndex[Second] - KeyIndex[First]
    Same = (Symbols[First] == Symbols[Second]).astype(float)
    PairCodes, PairIndex = np.unique(Segment[First] * 1000 + Segment[Second], return_inverse=True)
    PairIndex = PairIndex.ravel()
    SegFirst, SegSecond = PairCodes // 1000, PairCodes % 1000
    Shift = Drift[:, SegSecond] - Drift[:, SegFirst]
    Q = CoincidenceRate(Symbols, Modulus)
    Out = []
    Rows = np.arange(len(PairCodes))[None, :]
    for L in Periods:
        Cell = PairIndex * L + Delta % L
        TableSame = np.bincount(Cell, weights=Same, minlength=len(PairCodes) * L).reshape(-1, L)
        TableAll = np.bincount(Cell, minlength=len(PairCodes) * L).reshape(-1, L)
        Phase = Shift % L
        Z = ZScore(TableSame[Rows, Phase].sum(axis=1), TableAll[Rows, Phase].sum(axis=1), Q)
        Best = int(np.nanargmax(Z))
        Out.append((float(Z[Best]), Best))
    return Out


def SearchPage(Runes, WithSkips=True):
    """Full page search. Returns dict: Best, BestAt (view, L, skips), NoSkip {view: z over L=2..138}."""
    Views, NumF = BuildViews(Runes)
    Masks, Drift, MaxK = SkipMasks(NumF)
    Result = {"Best": -np.inf, "BestAt": None, "NoSkip": {}, "MaxK": MaxK, "NumF": NumF}
    for View in ViewNames:
        Symbols, KeyIndex, Segment = Views[View]
        Modulus = ViewModulus[View]
        Top = min(len(Symbols) // 2, PageMaxPeriod)
        Periods = np.arange(2, Top + 1)
        ZFlat = ColumnZ(Symbols, KeyIndex, np.zeros_like(Segment), Periods, Modulus)
        Padded = np.full(PageMaxPeriod - 1, np.nan)
        Padded[:len(ZFlat)] = ZFlat
        Result["NoSkip"][View] = Padded
        if len(ZFlat) == 0:
            continue
        Index = int(np.nanargmax(ZFlat))
        if ZFlat[Index] > Result["Best"]:
            Result["Best"], Result["BestAt"] = float(ZFlat[Index]), (View, int(Periods[Index]), 0)
        if not WithSkips or NumF == 0:
            continue
        ZWithin = ColumnZ(Symbols, KeyIndex, Segment, Periods, Modulus)
        Order = lambda Z: [int(Periods[I]) for I in np.argsort(-np.nan_to_num(Z, nan=-1e9))[:CandidatesPerView]]
        Candidates = sorted(set(Order(ZFlat)) | set(Order(ZWithin)))
        for L, (Z, Row) in zip(Candidates, SkipSearch(Symbols, KeyIndex, Segment, Candidates, Modulus, Drift)):
            if Z > Result["Best"]:
                Result["Best"], Result["BestAt"] = Z, (View, L, int(Masks[Row].sum()))
    return Result


def SearchSection(Runes):
    """Section-wide periodic key, periods 2-300, no skips. Returns (best z, (view, L))."""
    Views, _ = BuildViews(Runes)
    Best, BestAt = -np.inf, None
    for View in ViewNames:
        Symbols, KeyIndex, Segment = Views[View]
        Periods = np.arange(2, min(len(Symbols) // 2, SectionMaxPeriod) + 1)
        Z = ColumnZ(Symbols, KeyIndex, np.zeros_like(Segment), Periods, ViewModulus[View])
        Index = int(np.nanargmax(Z))
        if Z[Index] > Best:
            Best, BestAt = float(Z[Index]), (View, int(Periods[Index]))
    return Best, BestAt


def SharedPeriod(NoSkipList, MinPages=5):
    """S3: max over views and L of sum over pages of no-skip z / sqrt(number of pages)."""
    Best, BestAt = -np.inf, None
    for View in ViewNames:
        Stack = np.array([R[View] for R in NoSkipList])
        Count = np.sum(np.isfinite(Stack), axis=0)
        Sum = np.nansum(Stack, axis=0)
        Score = np.where(Count >= MinPages, Sum / np.sqrt(np.maximum(Count, 1)), -np.inf)
        Index = int(np.argmax(Score))
        if Score[Index] > Best:
            Best, BestAt = float(Score[Index]), (View, Index + 2)
    return Best, BestAt


def RealLayout():
    """[(SectionName, [(PageNumber, runes)])] in reading order."""
    return [(S["Name"], Pages(S)) for S in LoadAllUnsolved()]


def SearchCorpus(Layout):
    PageResults, SectionResults = [], []
    for _, PageList in Layout:
        Runes = []
        for _, PageRunes in PageList:
            PageResults.append(SearchPage(PageRunes))
            Runes += list(PageRunes)
        SectionResults.append(SearchSection(Runes))
    S3, S3At = SharedPeriod([R["NoSkip"] for R in PageResults])
    return {"PageBest": [R["Best"] for R in PageResults], "PageAt": [R["BestAt"] for R in PageResults],
            "SectionBest": [B for B, _ in SectionResults], "SectionAt": [A for _, A in SectionResults],
            "S3": S3, "S3At": S3At}


def SurrogateLayout(Layout, Seed):
    Rng = np.random.default_rng(Seed)
    Out = []
    for Name, PageList in Layout:
        NewPages = []
        for Number, PageRunes in PageList:
            C = np.asarray(PageRunes)
            Steps = (C[1:] - C[:-1]) % 29
            NonZero = np.flatnonzero(Steps)
            Steps[NonZero] = Rng.permutation(Steps[NonZero])
            Start = int(Rng.integers(29))
            NewPages.append((Number, np.r_[Start, (Start + np.cumsum(Steps)) % 29]))
        Out.append((Name, NewPages))
    return Out


def SurrogateJob(Seed):
    Result = SearchCorpus(SurrogateLayout(RealLayout(), Seed))
    return {"Seed": Seed, "PageBest": [round(X, 4) for X in Result["PageBest"]],
            "SectionBest": [round(X, 4) for X in Result["SectionBest"]], "S3": round(Result["S3"], 4)}


# ---------- tier 1 plants ----------

def PlantText(Length, Rng):
    Plain = SolvedPlaintext(tuple(SolvedPlainNames))
    Start = int(Rng.integers(len(Plain) - Length))
    return Plain[Start:Start + Length]


def SkipSet(Plain, SkipType, Rng):
    """Indices of plaintext Fs that pass through without consuming key."""
    FIndex = [I for I, P in enumerate(Plain) if P == 0]
    if SkipType == "welcome":
        return {I for Ordinal, I in enumerate(FIndex, 1) if Ordinal in WelcomeOrdinals}
    if SkipType == "random":
        Chosen = [I for I in FIndex if Rng.random() < 0.5]
        return set(Chosen[:MaxSkips])
    return set()


def PlantPage(Model, LayoutRunes, L, SkipType, Rng, Plain=None):
    """Model: raw | chain-literal-z1 | chain-transparent-z2. Doublets at the layout's doublet positions."""
    N = len(LayoutRunes)
    Plain = PlantText(N, Rng) if Plain is None else Plain[:N]
    Skips = SkipSet(Plain, SkipType, Rng)
    Doublets = {I for I in range(1, N) if LayoutRunes[I] == LayoutRunes[I - 1]}
    Out, KeyPos = [], 0
    if Model == "raw":
        Key = Rng.integers(29, size=L)
        for I, P in enumerate(Plain):
            if I in Skips:
                Out.append(0)
            else:
                Out.append(int((P + Key[KeyPos % L]) % 29))
                KeyPos += 1
        return Out
    Key = Rng.integers(28, size=L)
    State = int(Rng.integers(29))
    for I, P in enumerate(Plain):
        if I in Doublets and Out:
            Out.append(Out[-1])
            State = Out[-1]
            if Model.endswith("z1"):
                KeyPos += 1
        elif I in Skips:
            Out.append(0)
            if "literal" in Model:
                State = 0
        else:
            State = int((State + 1 + (P % 28 + Key[KeyPos % L]) % 28) % 29)
            Out.append(State)
            KeyPos += 1
    return Out


def StableSeed(*Parts):
    return zlib.crc32(json.dumps(Parts).encode())


def PowerPageJob(Args):
    Model, PageNumber, L, SkipType, Plants = Args
    Layout = dict((N, R) for _, PageList in RealLayout() for N, R in PageList)[PageNumber]
    Rng = np.random.default_rng(StableSeed(Model, PageNumber, L, SkipType))
    Scores, Periods = [], []
    for _ in range(Plants):
        Result = SearchPage(PlantPage(Model, Layout, L, SkipType, Rng))
        Scores.append(round(Result["Best"], 4))
        Periods.append(Result["BestAt"][1])
    return {"Kind": "page", "Model": Model, "Page": PageNumber, "L": L, "Skips": SkipType,
            "Scores": Scores, "Periods": Periods}


def PowerSectionJob(Args):
    Model, SectionName, L, Plants = Args
    Layout = [V for Name, PageList in RealLayout() if Name == SectionName for _, R in PageList for V in R]
    Length = len(Layout)
    Rng = np.random.default_rng(StableSeed(Model, SectionName, L))
    Scores, Periods = [], []
    for _ in range(Plants):
        Plain = []
        while len(Plain) < Length:
            Plain += PlantText(min(Length - len(Plain), 2000), Rng)
        Runes = PlantPage(Model, Layout, L, "none", Rng, Plain=Plain)
        Best, At = SearchSection(Runes)
        Scores.append(round(Best, 4))
        Periods.append(At[1])
    return {"Kind": "section", "Model": Model, "Section": SectionName, "L": L, "Scores": Scores, "Periods": Periods}


def PowerSharedJob(Args):
    Model, L, Plants, Seed = Args
    Rng = np.random.default_rng(Seed)
    Layout = RealLayout()
    Scores, Periods = [], []
    for _ in range(Plants):
        NoSkip = []
        for _, PageList in Layout:
            for _, R in PageList:
                NoSkip.append(SearchPage(PlantPage(Model, R, L, "none", Rng), WithSkips=False)["NoSkip"])
        Best, At = SharedPeriod(NoSkip)
        Scores.append(round(Best, 4))
        Periods.append(At[1])
    return {"Kind": "shared", "Model": Model, "L": L, "Scores": Scores, "Periods": Periods}


# ---------- drivers ----------

def AppendJson(Path, Record):
    with open(Path, "a") as Handle:
        Handle.write(json.dumps(Record) + "\n")


def ReadJson(Path):
    if not os.path.exists(Path):
        return []
    with open(Path) as Handle:
        return [json.loads(Line) for Line in Handle if Line.strip()]


def Log(Message):
    Stamp = time.strftime("%H:%M:%S")
    with open(os.path.join(OutDir, "run.log"), "a") as Handle:
        Handle.write(f"{Stamp} {Message}\n")


def RunReal():
    Start = time.time()
    Result = SearchCorpus(RealLayout())
    Result["Seconds"] = round(time.time() - Start, 1)
    with open(os.path.join(OutDir, "real.json"), "w") as Handle:
        json.dump(Result, Handle)
    Log(f"real done in {Result['Seconds']} s")


def RunSurrogates(Count, Workers):
    Path = os.path.join(CheckpointDir, "surrogates.jsonl")
    Done = {R["Seed"] for R in ReadJson(Path)}
    Seeds = [100000 + K for K in range(Count) if 100000 + K not in Done]
    Log(f"surrogates: {len(Done)} done, {len(Seeds)} to run")
    with multiprocessing.Pool(Workers) as Pool:
        for K, Record in enumerate(Pool.imap_unordered(SurrogateJob, Seeds)):
            AppendJson(Path, Record)
            if (K + 1) % 25 == 0:
                Log(f"surrogates: {len(Done) + K + 1}/{Count}")
    Log("surrogates done")


def PowerTasks(Plants):
    Layout = dict((N, R) for _, PageList in RealLayout() for N, R in PageList)
    Tasks = []
    for PageNumber in (55, 14, 3, 25):
        N = len(Layout[PageNumber])
        Periods = sorted({L for L in (3, 8, 13, 29, 60, 100) if L <= N // 2} | {N // 2 - 2})
        for Model in ("raw", "chain-literal-z1", "chain-transparent-z2"):
            for L in Periods:
                for SkipType in ("none", "random", "welcome"):
                    Tasks.append(("page", (Model, PageNumber, L, SkipType, Plants)))
    for Model in ("raw", "chain-literal-z1"):
        for SectionName in ("p54-55", "p3-7"):
            for L in (7, 60, 250):
                Tasks.append(("section", (Model, SectionName, L, Plants)))
    for Model in ("chain-literal-z1", "raw"):
        for L in (5, 20, 60):
            for Part in range(4):
                Tasks.append(("shared", (Model, L, Plants // 4, 7000 + L * 10 + Part)))
    return Tasks


def PowerJob(Task):
    Kind, Args = Task
    return {"page": PowerPageJob, "section": PowerSectionJob, "shared": PowerSharedJob}[Kind](Args)


def RunPower(Plants, Workers):
    Path = os.path.join(CheckpointDir, "power.jsonl")
    Done = {json.dumps(R["Key"]) for R in ReadJson(Path)}
    Tasks = [T for T in PowerTasks(Plants) if json.dumps(list(T[1])) not in Done]
    Log(f"power: {len(Done)} done, {len(Tasks)} tasks to run")
    with multiprocessing.Pool(Workers) as Pool:
        for K, Record in enumerate(Pool.imap_unordered(PowerJobKeyed, Tasks)):
            AppendJson(Path, Record)
            if (K + 1) % 10 == 0:
                Log(f"power: {K + 1}/{len(Tasks)}")
    Log("power done")


def PowerJobKeyed(Task):
    Record = PowerJob(Task)
    Record["Key"] = list(Task[1])
    return Record


def Standardise(Values, Surrogates):
    Mean, Sd = np.mean(Surrogates, axis=0), np.std(Surrogates, axis=0, ddof=1)
    return (np.asarray(Values) - Mean) / Sd, Mean, Sd


def PValue(Real, Null):
    Null = np.asarray(Null)
    return (1 + int(np.sum(Null >= Real))) / (1 + len(Null))


def Report():
    Real = json.load(open(os.path.join(OutDir, "real.json")))
    Surr = ReadJson(os.path.join(CheckpointDir, "surrogates.jsonl"))
    PageSurr = np.array([R["PageBest"] for R in Surr])
    SectionSurr = np.array([R["SectionBest"] for R in Surr])
    S3Surr = np.array([R["S3"] for R in Surr])
    NSurr = len(Surr)
    PageStdSurr, PageMean, PageSd = Standardise(PageSurr, PageSurr)
    SectionStdSurr, SectionMean, SectionSd = Standardise(SectionSurr, SectionSurr)
    S1Surr, S2Surr = PageStdSurr.max(axis=1), SectionStdSurr.max(axis=1)
    PageStdReal = (np.array(Real["PageBest"]) - PageMean) / PageSd
    SectionStdReal = (np.array(Real["SectionBest"]) - SectionMean) / SectionSd
    S1, S2, S3 = float(PageStdReal.max()), float(SectionStdReal.max()), Real["S3"]
    P = [PValue(S1, S1Surr), PValue(S2, S2Surr), PValue(S3, S3Surr)]
    # family-wise: min p of the three, calibrated on the surrogates themselves
    def RankP(Values):
        Order = np.argsort(np.argsort(-Values, kind="stable"), kind="stable")
        return (1 + Order) / (1 + len(Values))
    SurrMinP = np.minimum.reduce([RankP(S1Surr), RankP(S2Surr), RankP(S3Surr)])
    FamilyP = (1 + int(np.sum(SurrMinP <= min(P)))) / (1 + NSurr)
    Level = 1 - 0.01 / 3
    Thresholds = {"S1": float(np.quantile(S1Surr, Level)), "S2": float(np.quantile(S2Surr, Level)),
                  "S3": float(np.quantile(S3Surr, Level))}
    Lines = [f"E0027 report: {NSurr} surrogate corpora (whole search on each)", ""]
    Lines.append("Real data (standardised by each page's / section's surrogate mean and sd):")
    Lines.append(f"  S1 page-local      {S1:6.2f}  surrogate p {P[0]:.3f}  tier-1 threshold {Thresholds['S1']:.2f}")
    Lines.append(f"  S2 section-wide    {S2:6.2f}  surrogate p {P[1]:.3f}  tier-1 threshold {Thresholds['S2']:.2f}")
    Lines.append(f"  S3 shared period   {S3:6.2f}  surrogate p {P[2]:.3f}  tier-1 threshold {Thresholds['S3']:.2f}  at {Real['S3At']}")
    Lines.append(f"  family-wise p (min of the three, calibrated on surrogates) {FamilyP:.3f}")
    Lines.append(f"  surrogate S1 99th pct {np.quantile(S1Surr, 0.99):.2f}, max {S1Surr.max():.2f}; raw page best z: real max "
                 f"{max(Real['PageBest']):.2f}, surrogate mean of max {PageSurr.max(axis=1).mean():.2f}")
    Lines.append("")
    Lines.append("Top 8 pages (standardised, raw z, view, period, skips):")
    PageNumbers = [N for _, PageList in RealLayout() for N, _ in PageList]
    for I in np.argsort(-PageStdReal)[:8]:
        Lines.append(f"  p{PageNumbers[I]:<3} {PageStdReal[I]:6.2f}  z {Real['PageBest'][I]:6.2f}  {Real['PageAt'][I]}")
    Lines.append("Sections (standardised, raw z, view, period):")
    for I, (Name, _) in enumerate(RealLayout()):
        Lines.append(f"  {Name:<7} {SectionStdReal[I]:6.2f}  z {Real['SectionBest'][I]:6.2f}  {Real['SectionAt'][I]}")
    Power = ReadJson(os.path.join(CheckpointDir, "power.jsonl"))
    PageIndex = {N: I for I, N in enumerate(PageNumbers)}
    PageLengths = {N: len(R) for _, PageList in RealLayout() for N, R in PageList}
    SectionIndex = {Name: I for I, (Name, _) in enumerate(RealLayout())}
    Rows = []
    Shared = {}
    for R in Power:
        if R["Kind"] == "page":
            I = PageIndex[R["Page"]]
            Std = (np.array(R["Scores"]) - PageMean[I]) / PageSd[I]
            Hits = int(np.sum(Std >= Thresholds["S1"]))
            Right = sum(1 for Pd in R["Periods"] if Pd % R["L"] == 0 or R["L"] % Pd == 0)
            Rows.append(("S1", R["Model"], f"p{R['Page']} n={PageLengths[R['Page']]}", R["L"], R["Skips"], Hits, len(Std), Right))
        elif R["Kind"] == "section":
            I = SectionIndex[R["Section"]]
            Std = (np.array(R["Scores"]) - SectionMean[I]) / SectionSd[I]
            Hits = int(np.sum(Std >= Thresholds["S2"]))
            Right = sum(1 for Pd in R["Periods"] if Pd % R["L"] == 0 or R["L"] % Pd == 0)
            Rows.append(("S2", R["Model"], R["Section"], R["L"], "none", Hits, len(Std), Right))
        else:
            Key = (R["Model"], R["L"])
            Old = Shared.get(Key, ([], []))
            Shared[Key] = (Old[0] + R["Scores"], Old[1] + R["Periods"])
    for (Model, L), (Scores, Periods) in sorted(Shared.items()):
        Hits = int(np.sum(np.array(Scores) >= Thresholds["S3"]))
        Right = sum(1 for Pd in Periods if Pd % L == 0 or L % Pd == 0)
        Rows.append(("S3", Model, "all pages", L, "none", Hits, len(Scores), Right))
    Lines.append("")
    Lines.append("Tier 1 power (recovered = plant reaches the family threshold, surrogate quantile 1 - 0.01/3):")
    Lines.append("  stat model                 layout     L    skips    recovered  period-right")
    for Stat, Model, Where, L, Skips, Hits, Total, Right in sorted(Rows, key=lambda R: (R[0], R[1], str(R[2]), R[3], R[4])):
        Flag = "" if Hits >= 0.95 * Total else "  NOT IDENTIFIABLE"
        Lines.append(f"  {Stat}   {Model:<21} {str(Where):<10} {L:<4} {Skips:<8} {Hits:>3}/{Total:<3}     {Right:>3}{Flag}")
    Text = "\n".join(Lines) + "\n"
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write(Text)
    print(Text)


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("mode", choices=["real", "surrogates", "power", "report", "time"])
    Parser.add_argument("--count", type=int, default=999)
    Parser.add_argument("--plants", type=int, default=100)
    Parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2)))
    Args = Parser.parse_args()
    os.makedirs(CheckpointDir, exist_ok=True)
    if Args.mode == "real":
        RunReal()
    elif Args.mode == "surrogates":
        RunSurrogates(Args.count, Args.workers)
    elif Args.mode == "power":
        RunPower(Args.plants, Args.workers)
    elif Args.mode == "report":
        Report()
    else:
        Start = time.time()
        SurrogateJob(1)
        print(f"one surrogate corpus: {time.time() - Start:.1f} s")


if __name__ == "__main__":
    Main()
