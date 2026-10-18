"""E0028 (B12): structure of the doublet event process.

Hypothesis under test (H0): the 86 doublets (zero chain steps) sit at positions that are uniform within
each section, i.e. an independent rare gate with no memory, no packet or line structure, no period and
no rune preference. Alternatives are planted (tier 1) to say which departures this data could see.

Doublet at global index i means Runes[i] == Runes[i-1] with i and i-1 in the same section (candidates per
section: local 1..n-1). Corpus = the 9 unsolved sections concatenated in UnsolvedNames order.

Statistics (one value per corpus; the family-wise p uses the min-p over all of them):
    GapKS        KS distance of within-section gaps to the null gap CDF (upper)
    MinGap       smallest within-section gap (two-sided)
    GapCV        coefficient of variation of the gaps (two-sided)
    AutoChi2     chi2 of within-section pair counts at lags 1..20 vs null means (upper)
    ShortPairs   within-section pairs at distance 1..20 (two-sided)
    WordPairs    W = sum over words of C(D_w, 2) (two-sided)
    Pk16/29/32   aligned packets (from section start) holding >= 2 doublets (two-sided)
    PkLine       printed lines holding >= 2 doublets (two-sided)
    Fano200      variance/mean of counts in aligned 200-position windows (two-sided)
    PeriodRes    max over L = 2..300 of z(max residue count of corpus position mod L) (upper)
    PeriodPairs  max over L = 2..300 of z(within-section pairs at distance = 0 mod L) (upper)
    PeriodColl   max over L = 2..300 of z(corpus-wide pairs, across section breaks, at distance = 0 mod L,
                 i.e. sum over residues of C(n_r, 2) of corpus position mod L) (upper; added after the
                 18 Oct preliminary, whose L = 215 signal is this form)
    RuneChi2     chi2 of doublet runes vs null means (upper)
    LineStart    doublets whose pair spans a line break (two-sided)
    PageStart    doublets whose pair spans a page break (two-sided)
    WordStart    doublets whose pair spans a word break (two-sided)
SectionChi2 (per-section counts vs a multinomial in candidate counts) has its own null, since the
within-section permutation fixes the per-section counts.

Usage: python3 experiments/E0028_doublet_event_process.py [--null 100000] [--plants 100]
Outputs: results/E0028/{summary.txt, real.json, power.jsonl, doublets.tsv}; checkpoints
(results/E0028/checkpoint_*) are gitignored and let a reclaimed VM resume.
"""
import argparse
import json
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.ciphers import ChainEncrypt  # noqa: E402
from lp.controls import ControlPlaintext, PlantRaw  # noqa: E402
from lp.data import LoadAllUnsolved, RepoRoot, UnsolvedNames  # noqa: E402

OutDir = os.path.join(RepoRoot, "results", "E0028")
LogPath = os.path.join(OutDir, "run.log")
PilotTrials = 20000
Chunk = 2000
MaxLag = 20
Periods = np.arange(2, 301)
FanoWindow = 200
PacketSizes = (16, 29, 32)
Alpha = 0.01
StatNames = ["GapKS", "MinGap", "GapCV", "AutoChi2", "ShortPairs", "WordPairs", "Pk16", "Pk29", "Pk32",
             "PkLine", "Fano200", "PeriodRes", "PeriodPairs", "PeriodColl", "RuneChi2", "LineStart", "PageStart",
             "WordStart"]
UpperOnly = {"GapKS", "AutoChi2", "PeriodRes", "PeriodPairs", "PeriodColl", "RuneChi2"}


def Log(Message):
    Line = time.strftime("%H:%M:%S ") + Message
    with open(LogPath, "a") as Handle:
        Handle.write(Line + "\n")
    print(Line, flush=True)


def StableSeed(*Parts):
    return zlib.crc32("|".join(map(str, Parts)).encode())


def BuildLayout():
    Sections = LoadAllUnsolved()
    Lay = {"Lengths": [], "Offsets": []}
    Cols = {K: [] for K in ("Runes", "WordG", "LineG", "PageG", "Local", "Section")}
    Offset = WordBase = LineBase = PageBase = 0
    for S, Sec in enumerate(Sections):
        N = len(Sec["Runes"])
        Lay["Lengths"].append(N)
        Lay["Offsets"].append(Offset)
        Cols["Runes"] += Sec["Runes"]
        Cols["WordG"] += [WordBase + W for W in Sec["WordId"]]
        Cols["LineG"] += [LineBase + L for L in Sec["LineId"]]
        Cols["PageG"] += [PageBase + P for P in Sec["PageId"]]
        Cols["Local"] += list(range(N))
        Cols["Section"] += [S] * N
        WordBase += max(Sec["WordId"]) + 1
        LineBase += max(Sec["LineId"]) + 1
        PageBase += max(Sec["PageId"]) + 1
        Offset += N
    for Key, Values in Cols.items():
        Lay[Key] = np.array(Values, dtype=np.int64)
    Lay["Total"] = Offset
    Lay["Lengths"] = np.array(Lay["Lengths"])
    Lay["Offsets"] = np.array(Lay["Offsets"])
    Prev = np.roll(np.arange(Offset), 1)
    IsCandidate = Lay["Local"] > 0
    Lay["IsCandidate"] = IsCandidate
    Lay["WordStart"] = IsCandidate & (Lay["WordG"] != Lay["WordG"][Prev])
    Lay["LineStart"] = IsCandidate & (Lay["LineG"] != Lay["LineG"][Prev])
    Lay["PageStart"] = IsCandidate & (Lay["PageG"] != Lay["PageG"][Prev])
    Lay["Candidates"] = [np.arange(O + 1, O + N) for O, N in zip(Lay["Offsets"], Lay["Lengths"])]
    Lay["Packets"] = {}
    for Size in PacketSizes:
        Lay["Packets"][f"Pk{Size}"] = Lay["Section"] * 100000 + Lay["Local"] // Size
    Lay["Packets"]["PkLine"] = Lay["LineG"]
    WindowCount = Lay["Lengths"] // FanoWindow
    WindowBase = np.concatenate([[0], np.cumsum(WindowCount)[:-1]])
    Win = Lay["Local"] // FanoWindow
    Complete = Win < WindowCount[Lay["Section"]]
    Lay["NumWindows"] = int(WindowCount.sum())
    Lay["Window"] = np.where(Complete, WindowBase[Lay["Section"]] + Win, Lay["NumWindows"])
    return Lay


def ExtractDoublets(Runes, Lay):
    """Global indices i with Runes[i] == Runes[i-1] inside one section (identical for real and plants)."""
    Same = np.zeros(Lay["Total"], dtype=bool)
    Same[1:] = Runes[1:] == Runes[:-1]
    return np.flatnonzero(Same & Lay["IsCandidate"])


def SetColumns(Lay, Counts):
    """Column structure for a fixed per-section count vector: gap and pair index arrays."""
    ColSection = np.repeat(np.arange(len(Counts)), Counts)
    Starts = np.concatenate([[0], np.cumsum(Counts)[:-1]])
    GapA = np.array([J for S, C in enumerate(Counts) for J in range(Starts[S], Starts[S] + C - 1)])
    PairA, PairB = [], []
    for S, C in enumerate(Counts):
        for J in range(Starts[S], Starts[S] + C):
            for K in range(J + 1, Starts[S] + C):
                PairA.append(J)
                PairB.append(K)
    Lay["Counts"] = np.array(Counts)
    Lay["ColSection"] = ColSection
    Lay["GapA"] = GapA
    Lay["PairA"] = np.array(PairA)
    Lay["PairB"] = np.array(PairB)
    MaxDist = int(Lay["Lengths"].max())
    Lay["MaxDist"] = MaxDist
    Dist = np.arange(MaxDist + 1)[:, None]
    Lay["MultMatrix"] = ((Dist % Periods[None, :] == 0) & (Dist > 0)).astype(np.float32)


def RowBincount(Labels, Width):
    """Per-row histogram of non-negative integer labels < Width; Labels (N, K)."""
    N = Labels.shape[0]
    Flat = (np.arange(N, dtype=np.int64)[:, None] * Width + Labels).ravel()
    return np.bincount(Flat, minlength=N * Width).reshape(N, Width)


def RawQuantities(Pos, RuneAtPos, Lay):
    """Everything the statistics need before reference values are applied."""
    Gaps = Pos[:, Lay["GapA"] + 1] - Pos[:, Lay["GapA"]]
    Dists = Pos[:, Lay["PairB"]] - Pos[:, Lay["PairA"]]
    Q = {"Gaps": Gaps}
    Q["GapCdf"] = np.cumsum(RowBincount(Gaps, Lay["MaxDist"] + 1), axis=1) / Gaps.shape[1]
    Q["LagCounts"] = RowBincount(np.where(Dists <= MaxLag, Dists, 0), MaxLag + 1)[:, 1:]
    Hist = RowBincount(Dists, Lay["MaxDist"] + 1).astype(np.float32)
    Q["PairMult"] = Hist @ Lay["MultMatrix"]
    ResMax = np.empty((Pos.shape[0], len(Periods)))
    Coll = np.empty((Pos.shape[0], len(Periods)))
    for J, L in enumerate(Periods):
        Residues = RowBincount(Pos % L, int(L))
        ResMax[:, J] = Residues.max(axis=1)
        Coll[:, J] = (Residues * (Residues - 1) // 2).sum(axis=1)
    Q["ResMax"] = ResMax
    Q["Coll"] = Coll
    Q["RuneCounts"] = RowBincount(RuneAtPos, 29)
    return Q


def MakeReference(Lay, Rng):
    """Null means (and sds) of the raw quantities from a separate pilot of PilotTrials permutations."""
    Sums, Squares = {}, {}
    for _ in range(PilotTrials // Chunk):
        Pos = PermutedPositions(Lay, Chunk, Rng)
        Q = RawQuantities(Pos, Lay["Runes"][Pos], Lay)
        for Key in ("GapCdf", "LagCounts", "PairMult", "ResMax", "Coll", "RuneCounts"):
            Sums[Key] = Sums.get(Key, 0) + Q[Key].sum(0)
            Squares[Key] = Squares.get(Key, 0) + (Q[Key].astype(float) ** 2).sum(0)
    Mean = {K: V / PilotTrials for K, V in Sums.items()}
    Sd = {K: np.sqrt(np.maximum(Squares[K] / PilotTrials - Mean[K] ** 2, 0)) for K in Sums}
    return {"GapCdf": Mean["GapCdf"], "LagMean": Mean["LagCounts"], "MultMean": Mean["PairMult"],
            "MultSd": Sd["PairMult"], "ResMean": Mean["ResMax"], "ResSd": Sd["ResMax"],
            "CollMean": Mean["Coll"], "CollSd": Sd["Coll"],
            "RuneMean": Mean["RuneCounts"]}


def PacketsWithTwo(Labels):
    Eq = Labels[:, 1:] == Labels[:, :-1]
    Prev = np.concatenate([np.zeros((Eq.shape[0], 1), dtype=bool), Eq[:, :-1]], axis=1)
    return (Eq & ~Prev).sum(axis=1)


def Statistics(Pos, RuneAtPos, Lay, Ref):
    """Pos (N, 86) global doublet indices, sorted within each section block. Returns (N, len(StatNames))."""
    Q = RawQuantities(Pos, RuneAtPos, Lay)
    Gaps = Q["Gaps"].astype(float)
    Out = {}
    Out["GapKS"] = np.abs(Q["GapCdf"] - Ref["GapCdf"]).max(axis=1)
    Out["MinGap"] = Gaps.min(axis=1)
    Out["GapCV"] = Gaps.std(axis=1) / Gaps.mean(axis=1)
    Out["AutoChi2"] = ((Q["LagCounts"] - Ref["LagMean"]) ** 2 / Ref["LagMean"]).sum(axis=1)
    Out["ShortPairs"] = Q["LagCounts"].sum(axis=1)
    WordG = Lay["WordG"][Pos]
    Out["WordPairs"] = (WordG[:, Lay["PairA"]] == WordG[:, Lay["PairB"]]).sum(axis=1)
    for Name, Labels in Lay["Packets"].items():
        Out[Name] = PacketsWithTwo(Labels[Pos])
    WinCounts = RowBincount(Lay["Window"][Pos], Lay["NumWindows"] + 1)[:, :-1].astype(float)
    Out["Fano200"] = WinCounts.var(axis=1) / np.maximum(WinCounts.mean(axis=1), 1e-9)
    Out["PeriodRes"] = ((Q["ResMax"] - Ref["ResMean"]) / Ref["ResSd"]).max(axis=1)
    Out["PeriodPairs"] = ((Q["PairMult"] - Ref["MultMean"]) / np.maximum(Ref["MultSd"], 1e-9)).max(axis=1)
    CollZ = (Q["Coll"] - Ref["CollMean"]) / Ref["CollSd"]
    Out["PeriodColl"] = CollZ.max(axis=1)
    Out["RuneChi2"] = ((Q["RuneCounts"] - Ref["RuneMean"]) ** 2 / Ref["RuneMean"]).sum(axis=1)
    for Name in ("LineStart", "PageStart", "WordStart"):
        Out[Name] = Lay[Name][Pos].sum(axis=1)
    Extra = {"BestCollL": Periods[np.argmax(CollZ, axis=1)],
             "BestResL": Periods[np.argmax((Q["ResMax"] - Ref["ResMean"]) / Ref["ResSd"], axis=1)],
             "BestPairL": Periods[np.argmax((Q["PairMult"] - Ref["MultMean"]) / np.maximum(Ref["MultSd"], 1e-9), axis=1)]}
    return np.column_stack([Out[Name] for Name in StatNames]), Extra


def PermutedPositions(Lay, N, Rng):
    Blocks = []
    for Cand, D in zip(Lay["Candidates"], Lay["Counts"]):
        Keys = Rng.random((N, len(Cand)))
        Pick = np.sort(np.argpartition(Keys, D - 1, axis=1)[:, :D], axis=1)
        Blocks.append(Cand[Pick])
    return np.concatenate(Blocks, axis=1)


def PValues(Values, SortedNull):
    """Values (M, K) against SortedNull (N, K) per column; upper or two-sided per StatNames."""
    N = SortedNull.shape[0]
    P = np.empty(Values.shape)
    for K, Name in enumerate(StatNames):
        Col = SortedNull[:, K]
        Up = (1 + N - np.searchsorted(Col, Values[:, K] - 1e-12, side="left")) / (1 + N)
        if Name in UpperOnly:
            P[:, K] = Up
        else:
            Low = (1 + np.searchsorted(Col, Values[:, K] + 1e-12, side="right")) / (1 + N)
            P[:, K] = np.minimum(1.0, 2 * np.minimum(Up, Low))
    return P


def SectionChi2(Counts, Lay):
    Share = (Lay["Lengths"] - 1) / (Lay["Lengths"] - 1).sum()
    Expected = Counts.sum(axis=-1, keepdims=True) * Share
    return ((Counts - Expected) ** 2 / Expected).sum(axis=-1)


# ---------------------------------------------------------------- plants (tier 1)

def SynthesizeChain(Pos, Lay, Rng):
    """Chain ciphertext with zero steps exactly at Pos and uniform steps 1..28 elsewhere."""
    Steps = Rng.integers(1, 29, Lay["Total"])
    Steps[Lay["Offsets"]] = 0
    Steps[Pos] = 0
    Cum = np.cumsum(Steps)
    Start = Rng.integers(0, 29, len(Lay["Lengths"]))
    Base = (Start - Cum[Lay["Offsets"]])[Lay["Section"]]
    return (Base + Cum) % 29


def SynthesizeRunePreference(Lay, Weight, Rng):
    """Base chain with no doublets, then D_s duplicates inserted at points chosen by rune weight."""
    Runes = []
    for N, D in zip(Lay["Lengths"], Lay["Counts"]):
        Base = (Rng.integers(0, 29) + np.cumsum(np.r_[0, Rng.integers(1, 29, N - D - 1)])) % 29
        W = Weight[Base].astype(float)
        At = np.sort(Rng.choice(N - D, D, replace=False, p=W / W.sum()))
        Runes.append(np.insert(Base, At + 1, Base[At]))
    return np.concatenate(Runes)


def UniformIn(Pool, D, Rng, Weights=None):
    P = None if Weights is None else Weights / Weights.sum()
    return Rng.choice(Pool, D, replace=False, p=P)


def PlantPositions(Kind, Param, Lay, Rng):
    Out = []
    if Kind.startswith("Period"):
        Fraction, Lo, Hi = Param
    if Kind in ("PeriodGlobal", "PeriodAllowed"):
        L = int(Rng.integers(Lo, Hi + 1))
        R = int(Rng.integers(0, L))
    for S, (Cand, D) in enumerate(zip(Lay["Candidates"], Lay["Counts"])):
        N = len(Cand)
        if Kind == "Uniform":
            Pick = UniformIn(Cand, D, Rng)
        elif Kind == "Refractory":
            Slots = np.sort(Rng.choice(N - (Param - 1) * (D - 1), D, replace=False))
            Pick = Cand[Slots + (Param - 1) * np.arange(D)]
        elif Kind == "Regime":
            Pick = None
            while Pick is None:
                PiOn = 0.193
                StayOn = 1 - 1 / Param
                StayOff = 1 - (1 - StayOn) * PiOn / (1 - PiOn)
                On = np.empty(N, dtype=bool)
                State = Rng.random() < PiOn
                Flip = Rng.random(N)
                for I in range(N):
                    On[I] = State
                    State = State if Flip[I] < (StayOn if State else StayOff) else not State
                if On.sum() >= D:
                    Pick = UniformIn(Cand[On], D, Rng)
        elif Kind == "Packet":
            Labels = Lay["Packets"][Param][Cand]
            Unique = np.unique(Labels)
            Chosen = Rng.choice(Unique, D, replace=False)
            Pick = np.array([Rng.choice(Cand[Labels == U]) for U in Chosen])
        elif Kind == "PeriodAllowed":
            Allowed = Rng.permutation(L)[: max(1, int(round(Fraction * L)))]
            Pick = UniformIn(Cand[np.isin(Cand % L, Allowed)], D, Rng)
        elif Kind.startswith("Period"):
            if Kind == "PeriodSection":
                L = int(Rng.integers(Lo, Hi + 1))
                R = int(Rng.integers(0, L))
            OnRes = Cand[Cand % L == R]
            K = min(Rng.binomial(D, Fraction), len(OnRes))
            First = UniformIn(OnRes, K, Rng)
            Rest = UniformIn(np.setdiff1d(Cand, First), D - K, Rng)
            Pick = np.r_[First, Rest]
        elif Kind == "WordSubset":
            Words = np.unique(Lay["WordG"][Cand])
            Rng.shuffle(Words)
            Sizes = np.array([np.sum(Lay["WordG"][Cand] == W) for W in Words])
            Keep = Words[: np.searchsorted(np.cumsum(Sizes), Param * N) + 1]
            Pick = UniformIn(Cand[np.isin(Lay["WordG"][Cand], Keep)], D, Rng)
        elif Kind in ("LineStart", "PageStart"):
            Starts = Cand[Lay[Kind][Cand]]
            K = min(Rng.binomial(D, Param), len(Starts))
            First = UniformIn(Starts, K, Rng)
            Rest = UniformIn(np.setdiff1d(Cand, First), D - K, Rng)
            Pick = np.r_[First, Rest]
        elif Kind == "WordStart":
            Pick = UniformIn(Cand, D, Rng, np.where(Lay["WordStart"][Cand], Param, 1.0))
        else:
            raise ValueError(Kind)
        Out.append(np.sort(Pick))
    return np.concatenate(Out)


Conditions = [("Uniform", 0, "none (calibration)")]
Conditions += [("Refractory", R, "MinGap") for R in (3, 5, 7, 10, 15, 20)]
Conditions += [("Regime", Run, "GapCV/Fano200") for Run in (5, 20, 100, 300)]
Conditions += [("Packet", Name, Name) for Name in ("Pk16", "Pk29", "Pk32", "PkLine")]
Conditions += [(Kind, (F, Lo, Hi), Stat) for Kind, Stat in (("PeriodGlobal", "PeriodRes"),
                                                            ("PeriodSection", "PeriodPairs"))
               for F in (0.1, 0.25, 0.5) for Lo, Hi in ((2, 30), (31, 300))]
Conditions += [("PeriodAllowed", (Q, Lo, Hi), "PeriodColl") for Q in (0.25, 0.5, 0.75)
               for Lo, Hi in ((2, 30), (31, 300))]
Conditions += [("WordSubset", Q, "WordPairs") for Q in (0.1, 0.25, 0.5)]
Conditions += [("LineStart", F, "LineStart") for F in (0.05, 0.1, 0.2)]
Conditions += [("PageStart", F, "PageStart") for F in (0.05, 0.1)]
Conditions += [("WordStart", M, "WordStart") for M in (1.5, 2.0)]
Conditions += [("RunePref", M, "RuneChi2") for M in (2.0, 3.0)]


def RunPlantCondition(Kind, Param, Lay, Ref, SortedNull, NullMinP, Plants):
    Rng = np.random.default_rng(StableSeed("E0028", Kind, Param))
    PosRows, RuneRows = [], []
    for _ in range(Plants):
        if Kind == "RunePref":
            Preferred = Rng.choice(29, 7, replace=False)
            Weight = np.ones(29)
            Weight[Preferred] = Param
            Runes = SynthesizeRunePreference(Lay, Weight, Rng)
        else:
            Planted = PlantPositions(Kind, Param, Lay, Rng)
            Runes = SynthesizeChain(Planted, Lay, Rng)
        Found = ExtractDoublets(Runes, Lay)
        Counts = np.bincount(Lay["Section"][Found], minlength=len(Lay["Lengths"]))
        assert np.array_equal(Counts, Lay["Counts"]), (Kind, Param, Counts)
        if Kind != "RunePref":
            assert np.array_equal(Found, Planted)
        PosRows.append(Found)
        RuneRows.append(Runes[Found])
    Values, _ = Statistics(np.array(PosRows), np.array(RuneRows), Lay, Ref)
    P = PValues(Values, SortedNull)
    FamilyP = (1 + np.searchsorted(NullMinP, P.min(axis=1), side="right")) / (1 + len(NullMinP))
    return Values, P, FamilyP


def SectionPower(Lay, Sigma, Plants, NullChi2, Rng):
    Hits = 0
    Share = (Lay["Lengths"] - 1).astype(float)
    for _ in range(Plants):
        Rates = Share * np.exp(Rng.normal(0, Sigma, len(Share)))
        Counts = Rng.multinomial(int(Lay["Counts"].sum()), Rates / Rates.sum())
        P = (1 + np.sum(NullChi2 >= SectionChi2(Counts, Lay) - 1e-12)) / (1 + len(NullChi2))
        Hits += P <= Alpha
    return Hits


def StrictRules(RealPos, Lay):
    """Deterministic checks: which strict placement rules can produce the real positions at all."""
    Gaps = RealPos[Lay["GapA"] + 1] - RealPos[Lay["GapA"]]
    PageLocal = np.zeros(Lay["Total"], dtype=np.int64)
    Starts = np.flatnonzero(np.r_[True, Lay["PageG"][1:] != Lay["PageG"][:-1]])
    for A, B in zip(Starts, np.r_[Starts[1:], Lay["Total"]]):
        PageLocal[A:B] = np.arange(B - A)
    Lines = [f"Strict refractory rule (gap >= R): consistent for R <= {int(Gaps.min())} only "
             f"(smallest gaps {sorted(Gaps.tolist())[:6]})",
             "Strict one-doublet-per-packet rule, packets of P positions with alignment offset a:",
             "  P   section-aligned offsets consistent   page-aligned offsets consistent"]
    MaxConsistent = {"section": 0, "page": 0}
    for Size in range(2, 129):
        Row = []
        for Name, Index, Group in (("section", Lay["Local"], Lay["Section"]), ("page", PageLocal, Lay["PageG"])):
            Good = 0
            for Offset in range(Size):
                Labels = Group[RealPos] * 100000 + (Index[RealPos] + Offset) // Size
                Good += len(np.unique(Labels)) == len(RealPos)
            Row.append(Good)
            if Good:
                MaxConsistent[Name] = Size
        if any(Row):
            Lines.append(f"{Size:>3}   {Row[0]:>3}/{Size:<3}                              {Row[1]:>3}/{Size}")
    Lines.append(f"Largest P with any consistent offset: section-aligned {MaxConsistent['section']}, "
                 f"page-aligned {MaxConsistent['page']}")
    LineCounts = np.bincount(Lay["LineG"][RealPos])
    Lines.append(f"One per printed line: {'consistent' if LineCounts.max() < 2 else 'excluded'} "
                 f"({int(np.sum(LineCounts >= 2))} lines hold 2+ doublets)")
    with open(os.path.join(OutDir, "strict_rules.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    return MaxConsistent


def ColumnCoincidence(Symbols, Index, L):
    """Pairs of equal symbols inside the same column Index mod L."""
    Table = np.bincount((Index % L) * 29 + Symbols, minlength=L * 29)
    return float((Table * (Table - 1) // 2).sum())


def TopPeriodRecheck(RealPos, Lay, Ref, Trials=200):
    """Step 7 recheck of the best corpus-wide collision period on the rest of the data.

    A key of period L running through the corpus in reading order would also structure the non-zero
    steps and the raw runes by column (corpus position mod L). For every L = 2..300 the column
    coincidence count is standardised against Trials shuffles of the same symbols; reported: z at the
    best L, and its rank among all L. Also the decomposition of the doublet collisions at that L.
    """
    Q = RawQuantities(RealPos[None, :], Lay["Runes"][RealPos][None, :], Lay)
    Z = ((Q["Coll"][0] - Ref["CollMean"]) / Ref["CollSd"])
    Best = int(Periods[np.argmax(Z)])
    Res = RealPos % Best
    Counts = np.bincount(Res, minlength=Best)
    Cross = sum(1 for R in range(Best) for A in RealPos[Res == R] for B in RealPos[Res == R]
                if A < B and Lay["Section"][A] != Lay["Section"][B])
    Lines = [f"Best corpus-wide collision period L {Best}: z {Z.max():.2f}; collisions "
             f"{int((Counts * (Counts - 1) // 2).sum())} (null mean {Ref['CollMean'][Best - 2]:.1f}), "
             f"{Cross} of them across section breaks",
             f"Residues holding k doublets: {dict((int(K), int(np.sum(Counts == K))) for K in range(Counts.max() + 1))}",
             f"Top L by collision z: {[(int(Periods[K]), round(float(Z[K]), 2)) for K in np.argsort(-Z)[:6]]}"]
    for Drop in (1, 2, 3):
        Keep = ~np.isin(Res, np.argsort(-Counts)[:Drop])
        C = np.bincount(Res[Keep], minlength=Best)
        Scale = Keep.sum() * (Keep.sum() - 1) / (len(RealPos) * (len(RealPos) - 1))
        Lines.append(f"  drop the {Drop} fullest residue(s) ({int((~Keep).sum())} doublets): z ~"
                     f"{((C * (C - 1) // 2).sum() - Ref['CollMean'][Best - 2] * Scale) / (Ref['CollSd'][Best - 2] * np.sqrt(Scale)):.2f}")
    Cand = np.flatnonzero(Lay["IsCandidate"])
    Steps = (Lay["Runes"][Cand] - Lay["Runes"][Cand - 1]) % 29
    NonZero = Steps != 0
    Rng = np.random.default_rng(StableSeed("E0028", "recheck"))
    for Name, Symbols, Index in (("non-zero steps", Steps[NonZero], Cand[NonZero]),
                                 ("raw runes", Lay["Runes"], np.arange(Lay["Total"]))):
        Real = np.array([ColumnCoincidence(Symbols, Index, L) for L in Periods])
        Null = np.array([[ColumnCoincidence(Rng.permutation(Symbols), Index, L) for L in Periods]
                         for _ in range(Trials)])
        ZCol = (Real - Null.mean(0)) / Null.std(0)
        NullMax = ((Null - Null.mean(0)) / Null.std(0)).max(axis=1)
        Lines.append(f"{Name}: column-coincidence z at L {Best} = {ZCol[Best - 2]:.2f} (rank "
                     f"{int(np.sum(ZCol > ZCol[Best - 2])) + 1} of {len(Periods)}); best L "
                     f"{int(Periods[np.argmax(ZCol)])} z {ZCol.max():.2f}; null max-over-L 99% "
                     f"{np.quantile(NullMax, 0.99):.2f} ({Trials} shuffles)")
    # Positive control: a period-Best key through the same column test (English plaintext, real layout).
    Plain = np.array(ControlPlaintext(Lay["Total"], Source="baseline"))
    Key = Rng.integers(0, 29, Best)
    Raw = np.array(PlantRaw(Plain.tolist(), Key.tolist(), Sign=1)[0])
    Chain = np.array(ChainEncrypt(Plain[1:].tolist(), (Key % 28).tolist()))
    for Name, Runes in (("raw Vigenere plant", Raw), ("chain plant", Chain)):
        PlantSteps = (Runes[Cand] - Runes[Cand - 1]) % 29
        for View, Symbols, Index in (("steps", PlantSteps, Cand), ("raw", Runes, np.arange(Lay["Total"]))):
            Real = ColumnCoincidence(Symbols, Index, Best)
            Null = np.array([ColumnCoincidence(Rng.permutation(Symbols), Index, Best) for _ in range(50)])
            Lines.append(f"control {Name}, {View} view: z at L {Best} = {(Real - Null.mean()) / Null.std():.1f}")
    with open(os.path.join(OutDir, "top_period_recheck.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    return Lines


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("--null", type=int, default=100000)
    Parser.add_argument("--plants", type=int, default=100)
    Args = Parser.parse_args()
    os.makedirs(OutDir, exist_ok=True)
    Lay = BuildLayout()
    RealPos = ExtractDoublets(Lay["Runes"], Lay)
    Counts = np.bincount(Lay["Section"][RealPos], minlength=len(Lay["Lengths"]))
    SetColumns(Lay, Counts)
    Log(f"doublets {len(RealPos)} per section {Counts.tolist()}")

    RefPath = os.path.join(OutDir, "checkpoint_ref.npz")
    if os.path.exists(RefPath):
        Ref = dict(np.load(RefPath))
    else:
        Ref = MakeReference(Lay, np.random.default_rng(StableSeed("E0028", "pilot")))
        np.savez(RefPath, **Ref)
    Log("reference ready")

    NullBlocks = []
    for K in range(Args.null // Chunk):
        Path = os.path.join(OutDir, f"checkpoint_null_{K:03d}.npy")
        if not os.path.exists(Path):
            Rng = np.random.default_rng(StableSeed("E0028", "null", K))
            Pos = PermutedPositions(Lay, Chunk, Rng)
            Values, _ = Statistics(Pos, Lay["Runes"][Pos], Lay, Ref)
            np.save(Path, Values)
            if K % 5 == 0:
                Log(f"null chunk {K + 1}/{Args.null // Chunk}")
        NullBlocks.append(np.load(Path))
    Null = np.concatenate(NullBlocks)
    SortedNull = np.sort(Null, axis=0)
    NullMinP = np.sort(PValues(Null, SortedNull).min(axis=1))
    Log(f"null ready: {len(Null)} permutations")

    RealValues, RealExtra = Statistics(RealPos[None, :], Lay["Runes"][RealPos][None, :], Lay, Ref)
    RealP = PValues(RealValues, SortedNull)[0]
    RealFamilyP = (1 + np.searchsorted(NullMinP, RealP.min(), side="right")) / (1 + len(NullMinP))
    SecRng = np.random.default_rng(StableSeed("E0028", "sections"))
    Share = (Lay["Lengths"] - 1) / (Lay["Lengths"] - 1).sum()
    NullSec = SectionChi2(SecRng.multinomial(len(RealPos), Share, size=Args.null), Lay)
    RealSec = float(SectionChi2(Counts, Lay))
    SecP = (1 + np.sum(NullSec >= RealSec - 1e-12)) / (1 + len(NullSec))

    RealGaps = (RealPos[Lay["GapA"] + 1] - RealPos[Lay["GapA"]]).tolist()
    Real = {"Doublets": int(len(RealPos)), "PerSection": dict(zip(UnsolvedNames, Counts.tolist())),
            "Stats": {N: float(V) for N, V in zip(StatNames, RealValues[0])},
            "NullMean": {N: float(V) for N, V in zip(StatNames, Null.mean(0))},
            "NullQ01_Q99": {N: [float(np.quantile(Null[:, K], 0.01)), float(np.quantile(Null[:, K], 0.99))]
                            for K, N in enumerate(StatNames)},
            "P": {N: float(V) for N, V in zip(StatNames, RealP)},
            "FamilyP": float(RealFamilyP), "MinP": float(RealP.min()),
            "BestCollL": int(RealExtra["BestCollL"][0]), "BestResL": int(RealExtra["BestResL"][0]), "BestPairL": int(RealExtra["BestPairL"][0]),
            "SectionChi2": RealSec, "SectionP": float(SecP), "Gaps": RealGaps,
            "Permutations": int(len(Null))}
    with open(os.path.join(OutDir, "real.json"), "w") as Handle:
        json.dump(Real, Handle, indent=1)
    with open(os.path.join(OutDir, "doublets.tsv"), "w") as Handle:
        Handle.write("global\tsection\tlocal\tline\tword_start\tline_start\tpage_start\trune\n")
        for I in RealPos:
            Handle.write(f"{I}\t{UnsolvedNames[Lay['Section'][I]]}\t{Lay['Local'][I]}\t{Lay['LineG'][I]}\t"
                         f"{int(Lay['WordStart'][I])}\t{int(Lay['LineStart'][I])}\t{int(Lay['PageStart'][I])}\t"
                         f"{Lay['Runes'][I]}\n")
    Log(f"real: family p {RealFamilyP:.4f}, min p {RealP.min():.4f} ({StatNames[int(RealP.argmin())]}), "
        f"section p {SecP:.4f}")

    for Line in TopPeriodRecheck(RealPos, Lay, Ref):
        Log(Line)
    Strict = StrictRules(RealPos, Lay)
    Log(f"strict one-per-packet consistent up to P {Strict}")

    PowerPath = os.path.join(OutDir, "power.jsonl")
    Done = {}
    if os.path.exists(PowerPath):
        for Line in open(PowerPath):
            Record = json.loads(Line)
            Done[(Record["Kind"], str(Record["Param"]))] = Record
    for Kind, Param, Designated in Conditions:
        if (Kind, str(Param)) in Done:
            continue
        Values, P, FamilyP = RunPlantCondition(Kind, Param, Lay, Ref, SortedNull, NullMinP, Args.plants)
        Record = {"Kind": Kind, "Param": str(Param), "Designated": Designated, "Plants": Args.plants,
                  "FamilyRecovered": int(np.sum(FamilyP <= Alpha)),
                  "MedianFamilyP": float(np.median(FamilyP))}
        if Designated in StatNames:
            Record["DesignatedRecovered"] = int(np.sum(P[:, StatNames.index(Designated)] <= Alpha))
        elif Designated == "GapCV/Fano200":
            Record["DesignatedRecovered"] = int(np.sum(np.minimum(P[:, StatNames.index("GapCV")],
                                                                  P[:, StatNames.index("Fano200")]) <= Alpha / 2))
        Record["MedianStats"] = {N: float(V) for N, V in zip(StatNames, np.median(Values, axis=0))}
        with open(PowerPath, "a") as Handle:
            Handle.write(json.dumps(Record) + "\n")
        Done[(Kind, str(Param))] = Record
        Log(f"plant {Kind} {Param}: family {Record['FamilyRecovered']}/{Args.plants}, "
            f"designated {Record.get('DesignatedRecovered', '-')}")
    SecRng = np.random.default_rng(StableSeed("E0028", "section-plants"))
    SectionHits = {Sigma: int(SectionPower(Lay, Sigma, Args.plants, NullSec, SecRng)) for Sigma in (0.3, 0.5, 0.8)}

    WriteSummary(Real, Done, SectionHits, Args.plants)
    Log("done")


def WriteSummary(Real, Done, SectionHits, Plants):
    Lines = ["E0028 (B12) doublet event process", "",
             f"Doublets {Real['Doublets']}; per section {Real['PerSection']}",
             f"Null: {Real['Permutations']} within-section permutations of the doublet positions", "",
             "stat          real      null mean   null 1%..99%       p"]
    for N in StatNames:
        Q = Real["NullQ01_Q99"][N]
        Lines.append(f"{N:<12} {Real['Stats'][N]:9.3f} {Real['NullMean'][N]:10.3f}   "
                     f"{Q[0]:7.3f}..{Q[1]:<8.3f} {Real['P'][N]:.4f}")
    Lines += ["", f"min p {Real['MinP']:.4f}; family-wise p (min-p over {len(StatNames)} stats) "
              f"{Real['FamilyP']:.4f}",
              f"best period: residue L {Real['BestResL']}, pair-distance L {Real['BestPairL']}, "
              f"corpus collision L {Real['BestCollL']}",
              f"per-section counts chi2 {Real['SectionChi2']:.2f} on 8 df, multinomial p {Real['SectionP']:.4f}",
              "", f"Tier 1 power ({Plants} plants each; recovered = family-wise p <= {Alpha}; designated = "
              f"that statistic alone at p <= {Alpha})",
              "kind           param   family  designated  (designated stat)"]
    for Kind, Param, Designated in Conditions:
        R = Done[(Kind, str(Param))]
        Lines.append(f"{Kind:<14} {str(Param):<7} {R['FamilyRecovered']:>4}    "
                     f"{str(R.get('DesignatedRecovered', '-')):>6}      {Designated}")
    Lines.append("SectionRates   sigma   " + ", ".join(f"{S}: {H}/{Plants}" for S, H in SectionHits.items())
                 + "  (SectionChi2 alone)")
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")


if __name__ == "__main__":
    Main()
