"""E0030 (B21): page-local periodic keys scored by best-shift English likelihood per column.

Hypothesis: each LP page (real page map) is enciphered with its own periodic key of period L 2..20,
applied to the raw runes (Vigenere) or to the chain units (u = s - 1 mod 28), with up to 11 ciphertext
Fs passing through without consuming key.

New vs E0027 (same family, same views, page map, skip masks and surrogate generator, imported):
  - detector: each column (page, view, L, mask) is scored by the English unigram log-likelihood ratio of
    its symbols at the best of M shifts (M = 29 raw; M = 28 chain units, F and EA merged as p mod 28),
    so letter identities are used instead of column IoC;
  - skip masks are searched at EVERY period, not only at 8 candidate periods per view;
  - periods 2..min(20, n // 3) only (E0027 2..138), which lowers the multiplicity of the search;
  - views raw29, unit28z1, unit28z2 (step29 dropped: under the chain model it is unit28z1 plus a zero
    symbol, under raw Vigenere its column is a difference of letters, not shifted English).
Page score: z = (sum_j S_j - sum_j mu(n_j)) / sqrt(sum_j var(n_j)), S_j the best-shift LLR of column j
with n_j symbols, mu/var from uniform symbols (Monte Carlo table). Page best = max over views, L, masks.
S1 = max over pages of the page best standardised by that page's surrogate mean and sd (as E0027).
Null (tier 2): 999 surrogate corpora (E0027 SurrogateLayout: non-zero steps permuted within each page),
whole search on each. Threshold = surrogate quantile 0.99 of S1.
Control (tier 1): E0027 PlantPage (raw, chain literal-F z1, chain transparent-F z2; skips none / random /
Welcome ordinals) on real layouts, 100 plants per condition, standardised by the page's surrogate stats.

Usage:
  python3 experiments/E0030_column_shift_llr_pages.py time|real|surrogates|power|report
Outputs: results/E0030/ (small text); checkpoints in results/E0030/checkpoint_runs/ (gitignored).
"""
import argparse
import json
import multiprocessing
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp.data import RepoRoot  # noqa: E402
from lp.detectors import EnglishModel  # noqa: E402
from lp.gematria import ToLatin  # noqa: E402
import E0027_step_periodicity_pages as E27  # noqa: E402

OutDir = os.path.join(RepoRoot, "results", "E0030")
CheckpointDir = os.path.join(OutDir, "checkpoint_runs")
ViewNames = ["raw29", "unit28z1", "unit28z2"]
ViewModulus = {"raw29": 29, "unit28z1": 28, "unit28z2": 28}
MaxPeriod = 20
NullDraws = 20000
Level = 0.99
PowerPages = (25, 3, 14, 55)
PowerPeriods = (3, 5, 8, 10, 12, 13, 16, 20)
Models = ("raw", "chain-literal-z1", "chain-transparent-z2")
SkipTypes = ("none", "random", "welcome")
Tables = {}


def LogRatio(Modulus):
    """English log(P / uniform) per symbol, add-one smoothed; mod 28 merges F (0) and EA (28)."""
    Uni, _, Total = EnglishModel()
    Counts = np.array([Uni[R] + 1 for R in range(29)], dtype=float)
    if Modulus == 28:
        Counts = np.r_[Counts[0] + Counts[28], Counts[1:28]]
    return np.log(Counts / Counts.sum() * Modulus)


def ShiftMatrix(Modulus):
    """W[x, k] = LogRatio[(x - k) mod M]: Counts @ W scores every key shift k of a column."""
    Ratio = LogRatio(Modulus)
    X, K = np.meshgrid(np.arange(Modulus), np.arange(Modulus), indexing="ij")
    return Ratio[(X - K) % Modulus]


def NullTable(Modulus, MaxN=160):
    """(Mu, Var) of the best-shift column LLR for n uniform symbols, n = 0..MaxN (Monte Carlo, cached)."""
    if Modulus in Tables:
        return Tables[Modulus]
    Path = os.path.join(CheckpointDir, f"null_table_{Modulus}.json")
    if os.path.exists(Path):
        Data = json.load(open(Path))
        Tables[Modulus] = (np.array(Data["Mu"]), np.array(Data["Var"]))
        return Tables[Modulus]
    Rng = np.random.default_rng(28000 + Modulus)
    W = ShiftMatrix(Modulus)
    Mu, Var = np.zeros(MaxN + 1), np.ones(MaxN + 1)
    for N in range(1, MaxN + 1):
        Counts = Rng.multinomial(N, np.full(Modulus, 1.0 / Modulus), size=NullDraws)
        Best = (Counts @ W).max(axis=1)
        Mu[N], Var[N] = Best.mean(), Best.var(ddof=1)
    os.makedirs(CheckpointDir, exist_ok=True)
    with open(Path + ".part", "w") as Handle:
        json.dump({"Mu": Mu.tolist(), "Var": Var.tolist()}, Handle)
    os.replace(Path + ".part", Path)
    Tables[Modulus] = (Mu, Var)
    return Tables[Modulus]


def ScoreView(Symbols, KeyIndex, Segment, Modulus, L, Drift):
    """Best z over skip masks at period L. Returns (z, mask row, column shifts)."""
    W = ShiftMatrix(Modulus)
    Mu, Var = NullTable(Modulus)
    Groups = Drift.shape[1]
    Counts = np.zeros((Groups, L, Modulus))
    np.add.at(Counts, (Segment, KeyIndex % L, Symbols), 1)
    Offsets = (np.arange(L)[None, :] + np.arange(L)[:, None]) % L
    Rolled = Counts[:, Offsets]  # Rolled[g, d, c] = counts of segment g in key column (c + d) mod L
    RolledScore = (Rolled @ W).astype(np.float32)  # column scores are linear in counts: shift W first
    RolledSize = Rolled.sum(axis=3).astype(np.int64)
    Phase, Inverse = np.unique(Drift % L, axis=0, return_inverse=True)
    Inverse = Inverse.ravel()
    Score = np.zeros((len(Phase), L, Modulus), dtype=np.float32)
    Sizes = np.zeros((len(Phase), L), dtype=np.int64)
    for G in np.flatnonzero(Counts.sum(axis=(1, 2))):
        Score += RolledScore[G, Phase[:, G]]
        Sizes += RolledSize[G, Phase[:, G]]
    Best = Score.max(axis=2).astype(float)
    Z = (Best.sum(axis=1) - Mu[Sizes].sum(axis=1)) / np.sqrt(Var[Sizes].sum(axis=1))
    Index = int(np.argmax(Z))
    Shifts = Score[Index].argmax(axis=1)
    Row = int(np.flatnonzero(Inverse == Index)[0])
    return float(Z[Index]), Row, Shifts


def SearchPage(Runes, Detail=False):
    """Best z over views, L = 2..min(20, n // 3) and every skip mask. Detail adds the decryption."""
    Views, NumF = E27.BuildViews(Runes)
    Masks, Drift, MaxK = E27.SkipMasks(NumF)
    Result = {"Best": -np.inf, "BestAt": None, "MaxK": MaxK, "NumF": NumF}
    Top = min(MaxPeriod, len(Runes) // 3)
    for View in ViewNames:
        Symbols, KeyIndex, Segment = Views[View]
        for L in range(2, Top + 1):
            Z, Row, Shifts = ScoreView(Symbols, KeyIndex, Segment, ViewModulus[View], L, Drift)
            if Z > Result["Best"]:
                Result["Best"], Result["BestAt"] = Z, (View, L, int(Masks[Row].sum()))
                if Detail:
                    Column = (KeyIndex - Drift[Row][Segment]) % L
                    Plain = (Symbols - Shifts[Column]) % ViewModulus[View]
                    Result["Text"] = "".join(ToLatin(Plain[:80].tolist()))
    return Result


def SearchCorpus(Layout, Detail=False):
    Results = [SearchPage(R, Detail) for _, PageList in Layout for _, R in PageList]
    Out = {"PageBest": [R["Best"] for R in Results], "PageAt": [R["BestAt"] for R in Results]}
    if Detail:
        Out["Text"] = [R["Text"] for R in Results]
    return Out


def SurrogateJob(Seed):
    Result = SearchCorpus(E27.SurrogateLayout(E27.RealLayout(), Seed))
    return {"Seed": Seed, "PageBest": [round(X, 4) for X in Result["PageBest"]]}


def PowerJob(Args):
    Model, PageNumber, L, SkipType, Plants = Args
    Layout = dict((N, R) for _, PageList in E27.RealLayout() for N, R in PageList)[PageNumber]
    # seed label "E0028": the id this run had before renumbering; kept so the recorded plants reproduce
    Rng = np.random.default_rng(E27.StableSeed("E0028", Model, PageNumber, L, SkipType))
    Scores, Periods, Views = [], [], []
    for _ in range(Plants):
        Result = SearchPage(E27.PlantPage(Model, Layout, L, SkipType, Rng))
        Scores.append(round(Result["Best"], 4))
        Views.append(Result["BestAt"][0])
        Periods.append(Result["BestAt"][1])
    return {"Key": list(Args), "Scores": Scores, "Periods": Periods, "Views": Views}


def Log(Message):
    with open(os.path.join(OutDir, "run.log"), "a") as Handle:
        Handle.write(f"{time.strftime('%H:%M:%S')} {Message}\n")


def RunReal():
    Start = time.time()
    Result = SearchCorpus(E27.RealLayout(), Detail=True)
    Result["Seconds"] = round(time.time() - Start, 1)
    with open(os.path.join(OutDir, "real.json"), "w") as Handle:
        json.dump(Result, Handle)
    Log(f"real done in {Result['Seconds']} s")


def RunPool(Name, Job, Tasks, Keyer, Workers):
    Path = os.path.join(CheckpointDir, f"{Name}.jsonl")
    Done = {json.dumps(Keyer(R)) for R in E27.ReadJson(Path)}
    Todo = [T for T in Tasks if json.dumps(T) not in Done]
    Log(f"{Name}: {len(Done)} done, {len(Todo)} to run")
    with multiprocessing.Pool(Workers) as Pool:
        for K, Record in enumerate(Pool.imap_unordered(Job, Todo)):
            E27.AppendJson(Path, Record)
            if (K + 1) % 20 == 0:
                Log(f"{Name}: {len(Done) + K + 1}/{len(Tasks)}")
    Log(f"{Name} done")


def PowerTasks(Plants):
    return [[Model, Page, L, Skips, Plants] for Page in PowerPages for L in PowerPeriods
            for Model in Models for Skips in SkipTypes]


def Report():
    Real = json.load(open(os.path.join(OutDir, "real.json")))
    Surr = E27.ReadJson(os.path.join(CheckpointDir, "surrogates.jsonl"))
    PageSurr = np.array([R["PageBest"] for R in Surr])
    NSurr = len(Surr)
    StdSurr, Mean, Sd = E27.Standardise(PageSurr, PageSurr)
    S1Surr = StdSurr.max(axis=1)
    StdReal = (np.array(Real["PageBest"]) - Mean) / Sd
    S1 = float(StdReal.max())
    P = E27.PValue(S1, S1Surr)
    Threshold = float(np.quantile(S1Surr, Level))
    Numbers = [N for _, PageList in E27.RealLayout() for N, _ in PageList]
    Lengths = {N: len(R) for _, PageList in E27.RealLayout() for N, R in PageList}
    Lines = [f"E0030 report: {NSurr} surrogate corpora (whole search on each)", "",
             f"Real S1 (max over pages, standardised by each page's surrogate mean/sd) {S1:.2f}",
             f"  surrogate p {P:.3f}; tier-1 threshold (surrogate quantile {Level}) {Threshold:.2f};"
             f" surrogate S1 median {np.median(S1Surr):.2f}, max {S1Surr.max():.2f}", "",
             "Top 8 pages (standardised, raw z, (view, L, skips), first 80 symbols at the best shifts):"]
    for I in np.argsort(-StdReal)[:8]:
        Lines.append(f"  p{Numbers[I]:<3} {StdReal[I]:6.2f}  z {Real['PageBest'][I]:6.2f}  {tuple(Real['PageAt'][I])}")
        Lines.append(f"       {Real['Text'][I][:100]}")
    Index = {N: I for I, N in enumerate(Numbers)}
    Rows = []
    for R in E27.ReadJson(os.path.join(CheckpointDir, "power.jsonl")):
        Model, Page, L, Skips, _ = R["Key"]
        Std = (np.array(R["Scores"]) - Mean[Index[Page]]) / Sd[Index[Page]]
        Hits = int(np.sum(Std >= Threshold))
        Right = sum(1 for Pd in R["Periods"] if Pd % L == 0 or L % Pd == 0)
        Rows.append([Model, Page, Lengths[Page], L, Skips, Hits, len(Std), Right, float(np.median(Std))])
    Rows.sort(key=lambda R: (-R[2], R[0], R[3], R[4]))
    Lines += ["", f"Tier 1 power (recovered = plant's standardised page score >= {Threshold:.2f}):",
              "  model                 page  n    L   skips    recovered  period-right  median std"]
    for Model, Page, N, L, Skips, Hits, Total, Right, Median in Rows:
        Flag = "" if Hits >= 0.95 * Total else "  NOT IDENTIFIABLE"
        Lines.append(f"  {Model:<21} p{Page:<4} {N:<4} {L:<3} {Skips:<8} {Hits:>3}/{Total:<3}    {Right:>3}"
                     f"           {Median:6.2f}{Flag}")
    Region = {}
    for Model, Page, N, L, Skips, Hits, Total, Right, Median in Rows:
        if Hits >= 0.95 * Total:
            Region.setdefault((Model, f"p{Page} n={N}", Skips), []).append(f"{L}({Hits})")
    Lines += ["", "Lab-verified negative region (>= 95/100 at the threshold, real data null):"]
    for Key in sorted(Region, key=lambda K: (K[1], K[0], K[2])):
        Lines.append(f"  {Key[0]:<21} {Key[1]:<11} skips {Key[2]:<8} L = {', '.join(Region[Key])}")
    with open(os.path.join(OutDir, "analysis.json"), "w") as Handle:
        json.dump({"Surrogates": NSurr, "S1": S1, "P": P, "Threshold": Threshold, "Rows": Rows}, Handle)
    Text = "\n".join(Lines) + "\n"
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write(Text)
    print(Text[:3000])


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("mode", choices=["time", "real", "surrogates", "power", "report"])
    Parser.add_argument("--count", type=int, default=999)
    Parser.add_argument("--plants", type=int, default=100)
    Parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 2))
    Args = Parser.parse_args()
    os.makedirs(CheckpointDir, exist_ok=True)
    NullTable(28)
    NullTable(29)
    if Args.mode == "time":
        Start = time.time()
        SurrogateJob(1)
        print(f"one surrogate corpus: {time.time() - Start:.1f} s")
        Layout = dict((N, R) for _, PageList in E27.RealLayout() for N, R in PageList)
        for Page in PowerPages:
            Rng = np.random.default_rng(1)
            Start = time.time()
            Result = SearchPage(E27.PlantPage("raw", Layout[Page], 8, "random", Rng))
            print(f"plant p{Page} raw L 8: z {Result['Best']:.2f} at {Result['BestAt']} ({time.time() - Start:.2f} s)")
    elif Args.mode == "real":
        RunReal()
    elif Args.mode == "surrogates":
        Seeds = [100000 + K for K in range(Args.count)]
        RunPool("surrogates", SurrogateJob, Seeds, lambda R: R["Seed"], Args.workers)
    elif Args.mode == "power":
        RunPool("power", PowerJob, PowerTasks(Args.plants), lambda R: R["Key"], Args.workers)
    else:
        Report()


if __name__ == "__main__":
    Main()
