"""E0031 (B24): rerun of E0029's step views on the four pages with an FF run, after the F-run fix.

Bug (B24 item 1): lp.runningkey.PageEvents only let an *isolated* ciphertext F skip in the step views
(step29, unit28z1, unit28z2), so a skip inside an FF run, or beside a keyed F, could not be scored.
The fix builds one event per F-run in which each F is keyed, a literal skip or a transparent skip.
The fix only adds options, so every old path is still scored: fixed scores >= old scores, and only pages
with an FF run (real pages 9, 29, 32, 36) can change. raw29 handles every F alone and is unaffected.

Stages:
  parity   gpu/E0029_bytes_gpu.py vs lp.runningkey: identical events on the 55 real pages and 2,000
           random F-heavy pages in every view; with PyTorch installed, Engine.Run equals RunEvents
           (score and end pointer) on all 55 pages x 4 views x 2 a-signs, b = +-1, both directions,
           on the c560_13 source (tiled) and on a shuffled copy
  rerun    the 3 step views x 4 polarities x 2 directions on pages 9, 29, 32, 36 for the 7 CPU sources:
           the real source and E0029's 20 null seeds (1000..1019), same sources as E0029
  power    tier-1 plants that need the fix: two plaintext Fs in a row both skipped (all step views), and
           in unit28 a skipped F followed by a doublet; on the four real FF pages, 100 plants per view
           and pattern, Mabinogion key (E0029's hardest source), scored by the fixed engine against the
           updated thresholds; also the same plants scored by the old engine (git show of E0029's code)
  report   merge with results/E0029 (page best = max(old, new step-view best), real and null), new
           pooled Gumbel thresholds, standardised scores and p, results/E0031/summary.txt
Usage: python3 experiments/E0031_f_run_step_view_rerun.py STAGE
"""
import importlib.util
import json
import math
import multiprocessing
import os
import random
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.data import RepoRoot  # noqa: E402
from lp import runningkey as Rk  # noqa: E402

E29Path = os.path.join(RepoRoot, "experiments", "E0029_skip_tolerant_running_key.py")
Spec = importlib.util.spec_from_file_location("E0029", E29Path)
E29 = importlib.util.module_from_spec(Spec)
Spec.loader.exec_module(E29)

OutDir = os.path.join(RepoRoot, "results", "E0031")
CheckDir = os.path.join(OutDir, "checkpoint")
FFPages = [9, 29, 32, 36]
StepViews = ["step29", "unit28z1", "unit28z2"]
NullSeeds = [1000 + R for R in range(20)]
Plants = 100


def Log(Message):
    print(time.strftime("%H:%M:%S"), Message, flush=True)


def LoadGpuModule():
    Path = os.path.join(RepoRoot, "gpu", "E0029_bytes_gpu.py")
    Spec = importlib.util.spec_from_file_location("E0029gpu", Path)
    Mod = importlib.util.module_from_spec(Spec)
    Spec.loader.exec_module(Mod)
    return Mod


def StageParity():
    try:
        import torch  # noqa: F401
        HaveTorch = True
    except ImportError:
        HaveTorch = False
    if not HaveTorch:  # the event builder is pure Python; load it without the torch import
        Src = open(os.path.join(RepoRoot, "gpu", "E0029_bytes_gpu.py")).read()
        Body = Src[Src.index("def PageEvents("):Src.index("class Engine:")]
        Gpu = type("Gpu", (), {})
        Namespace = {}
        exec(Body, Namespace)
        Gpu.PageEvents = staticmethod(Namespace["PageEvents"])
    else:
        Gpu = LoadGpuModule()
    Pages = [R for _, R in E29.RealPages()]
    Rng = random.Random(31)
    Random = [[Rng.choice([0, 0, 0] + list(range(1, 29))) for _ in range(Rng.randrange(2, 40))] for _ in range(2000)]
    Mismatch = 0
    for View in Rk.Views:
        Skip = float(Rk.Weights(Rk.ViewModulus[View])[0])
        for Page in Pages + Random:
            Cpu = Rk.PageEvents(Page, View)
            Other = Gpu.PageEvents(Page, View, Skip)
            Mismatch += Cpu != Other
    Report = {"event_mismatches": Mismatch, "pages_checked": (len(Pages) + len(Random)) * len(Rk.Views)}
    Log(f"events: {Mismatch} mismatches over {Report['pages_checked']} (page, view)")
    if HaveTorch:
        GpuPages = Gpu.LoadPages()
        W29, W28, _ = Gpu.LoadEnglish()
        Report["pages_identical"] = GpuPages == [list(R) for R in Pages]
        Report["max_weight_diff"] = float(max(np.abs(W29 - Rk.Weights(29)).max(), np.abs(W28 - Rk.Weights(28)).max()))
        Log(f"pages identical {Report['pages_identical']}, max weight diff {Report['max_weight_diff']:.2e}")
        Skip = {29: float(W29[0]), 28: float(W28[0])}
        Worst, EndDiff, Runs = 0.0, 0, 0
        for Shuffle in (False, True):
            Base = E29.BuildSource("c560_13", 7 if Shuffle else None)
            for Rev in (False, True):
                S = Base.Reverse() if Rev else Base
                Eng = Gpu.Engine(S.Tok1.astype(np.int64), W29, W28)
                for M in (29, 28):
                    for B in (-1, 1):
                        Tab = Rk.Tables(S, M, B)
                        Eng.SetCombo(M, B)
                        for View in [V for V in Rk.Views if Rk.ViewModulus[V] == M]:
                            for Page in Pages:
                                Events = Rk.PageEvents(Page, View)
                                for A in (1, -1):
                                    V = Rk.RunEvents(Events, Tab, A)
                                    Score, End = Eng.Run(Gpu.PageEvents(Page, View, Skip[M]), A)
                                    Worst = max(Worst, abs(Score - float(V.max())))
                                    EndDiff += End != int(np.argmax(V))
                                    Runs += 1
        Report.update({"engine_runs": Runs, "max_abs_score_diff": Worst, "end_pointer_mismatches": EndDiff})
        Log(f"engine: {Runs} runs, max |score diff| {Worst:.2e}, end mismatches {EndDiff}")
    else:
        Report["engine"] = "torch not installed: events only"
    E29.SaveJson(os.path.join(OutDir, "parity.json"), Report)


def _Job(Args):
    Name, Seed, Rev, M, B = Args
    Src = E29.BuildSource(Name, Seed)
    PageList = {P: R for P, R in E29.RealPages()}
    Views = [V for V in StepViews if Rk.ViewModulus[V] == M]
    Out = Rk.SearchCombo([PageList[P] for P in FFPages], Src, Rev, M, B, Views)
    return {E29.FormKey(V, A, Bb, R) + f"|{FFPages[P]}": [round(S, 3), E] for (P, V, A, Bb, R), (S, E) in Out.items()}


def StageRerun():
    os.makedirs(CheckDir, exist_ok=True)
    Combos = [C for C in Rk.Combos() if C[1] in (29, 28)]
    with multiprocessing.Pool(E29.Workers) as Pool:
        for Name in E29.CpuSources:
            for Seed in [None] + NullSeeds:
                Path = os.path.join(CheckDir, f"{Name}_{Seed}.json")
                if os.path.exists(Path):
                    continue
                T = time.time()
                Out = {}
                for Res in Pool.map(_Job, [(Name, Seed, Rev, M, B) for Rev, M, B in Combos], chunksize=1):
                    Out.update(Res)
                E29.SaveJson(Path, Out)
                Log(f"rerun {Name} seed {Seed}: {len(Out)} scores, {time.time() - T:.0f}s")


def OldPageEvents():
    """E0029's PageEvents as committed before the fix (for the power comparison)."""
    Src = subprocess.run(["git", "show", "c3bb27d:lp/runningkey.py"], cwd=RepoRoot, capture_output=True,
                         text=True, check=True).stdout
    Body = Src[Src.index("def PageEvents("):Src.index("class Tables:")]
    Namespace = {"Weights": Rk.Weights, "ViewModulus": Rk.ViewModulus}
    exec(Body, Namespace)
    return Namespace["PageEvents"]


def FFPlant(Rng, Corpus, Page, View, Pattern, Src):
    """A plant in a real FF page layout whose decryption needs an F-run option. 'ff': plaintext F F at
    a random place, both skipped; 'fd' (unit28): a skipped F followed by a doublet. Other plaintext Fs
    are skipped with probability 0.3. Doublets follow the real page, as in E0029."""
    N = len(Page)
    Dbl = [I for I in range(1, N) if Page[I] == Page[I - 1]] if View.startswith("unit") else []
    PlainLength = N - 1 - len(Dbl)
    DblPlain = {I - 1 - K for K, I in enumerate(Dbl)}
    Off = Rng.randrange(len(Corpus) - PlainLength)
    Plain = [int(V) for V in Corpus[Off:Off + PlainLength]]
    while True:
        At = Rng.randrange(5, PlainLength - 5)
        if not ({At, At + 1} & DblPlain):
            break
    Skips = {I for I, P in enumerate(Plain) if P == 0 and Rng.random() < 0.3}
    Dbls = set(DblPlain)
    if Pattern == "ff":
        Plain[At] = Plain[At + 1] = 0
        Skips |= {At, At + 1}
    else:
        Plain[At] = 0
        Skips.add(At)
        Skips.discard(At + 1)
        Dbls.add(At + 1)
    Skips -= Dbls  # a plaintext index is a doublet or a skip, never both
    A, B = Rng.choice(Rk.Polarities)
    Rev = Rng.random() < 0.5
    S = Src.Reverse() if Rev else Src
    Need = PlainLength + len(Dbls) + 5
    Start = Rng.randrange(0, S.Length - 3 * Need - 10)
    Key, Letters = Rk.RandomTokens(S, Start, Need, Rng)
    Cipher, _ = Rk.PlantPage(Plain, Key, View, A, B, Skips, Dbls, Rng, Start=Page[0])
    return Cipher, (View, A, B, Rev), Start, Letters


def StagePower():
    Thr = MergedThresholds("mabinogion")
    Rng = random.Random(31)
    Corpus = E29.PlantCorpus()
    Src = E29.BuildSource("mabinogion")
    PageList = {P: R for P, R in E29.RealPages()}
    Old = OldPageEvents()
    Rows = []
    for View in StepViews:
        for Pattern in (["ff"] if View == "step29" else ["ff", "fd"]):
            for Page in FFPages:
                Hits, OldHits, Margins = 0, 0, []
                for _ in range(Plants):
                    Cipher, (V, A, B, Rev), Start, Letters = FFPlant(Rng, Corpus, PageList[Page], View, Pattern, Src)
                    S = Src.Reverse() if Rev else Src
                    Window = S.Slice(max(0, Start - 30), min(S.Length, Start + Letters + 30))
                    Tab = Rk.Tables(Window, Rk.ViewModulus[V], B)
                    Score = float(Rk.RunEvents(Rk.PageEvents(Cipher, V), Tab, A).max())
                    OldScore = float(Rk.RunEvents(Old(Cipher, V), Tab, A).max())
                    Margins.append(Score - Thr[Page])
                    Hits += Score > Thr[Page]
                    OldHits += OldScore > Thr[Page]
                Rows.append({"view": View, "pattern": Pattern, "page": Page, "length": len(PageList[Page]),
                             "recovered": int(Hits), "old_engine_recovered": int(OldHits), "plants": Plants,
                             "min_margin": round(min(Margins), 1)})
                Log(f"power {View} {Pattern} p{Page}: fixed {Hits}/{Plants}, old {OldHits}/{Plants}, min margin {min(Margins):.1f}")
    E29.SaveJson(os.path.join(OutDir, "power_mabinogion.json"), {"rows": Rows})


def Merged(Name):
    """(Real page best [55], Null matrix [20 x 55], Forms [55]) after merging the fixed step views."""
    Real = E29.LoadJson(os.path.join(E29.OutDir, f"real_{Name}.json"))
    PageNumbers = Real["pages"]
    Scores = {K: V for K, V in Real["scores"].items()}
    Fixed = E29.LoadJson(os.path.join(CheckDir, f"{Name}_None.json"))
    Changed = 0
    for K, (S, E) in Fixed.items():
        Form, Page = K.rsplit("|", 1)
        Key = f"{Form}|{PageNumbers.index(int(Page))}"
        assert S >= Scores[Key][0] - 1e-3, (Name, K, S, Scores[Key])  # the fix only adds options
        Changed += S > Scores[Key][0] + 1e-3
        Scores[Key] = [S, E]
    Best = E29.PageBest({K: (V[0], V[1]) for K, V in Scores.items()}, len(PageNumbers))
    Null = np.array(E29.LoadJson(os.path.join(E29.OutDir, f"null_{Name}.json"))["best"], dtype=np.float64)
    NullChanged = 0
    for R, Seed in enumerate(NullSeeds):
        Rep = E29.LoadJson(os.path.join(CheckDir, f"{Name}_{Seed}.json"))
        for K, (S, _) in Rep.items():
            Col = PageNumbers.index(int(K.rsplit("|", 1)[1]))
            if S > Null[R, Col] + 1e-3:
                NullChanged += 1
                Null[R, Col] = S
    return Best, Null, PageNumbers, Changed, NullChanged


def MergedThresholds(Name):
    Best, Null, PageNumbers, _, _ = Merged(Name)
    Path = os.path.join(CheckDir, f"merged_null_{Name}.json")
    E29.SaveJson(Path, {"best": Null.tolist()})
    Lengths = [len(R) for _, R in E29.RealPages()]
    Threshold, *_ = E29.Thresholds(Name, Lengths, E29.PageAlpha(), Path=Path)
    return {P: Threshold[PageNumbers.index(P)] for P in FFPages}


def StageReport():
    Lengths = [len(R) for _, R in E29.RealPages()]
    Lines = ["E0031 (B24): E0029 step views rerun on the FF pages 9, 29, 32, 36 after the F-run fix", ""]
    Parity = E29.LoadJson(os.path.join(OutDir, "parity.json"))
    Lines.append(f"CPU/GPU parity: {Parity}")
    Out = {}
    for Name in E29.CpuSources:
        Best, Null, PageNumbers, Changed, NullChanged = Merged(Name)
        Path = os.path.join(CheckDir, f"merged_null_{Name}.json")
        E29.SaveJson(Path, {"best": Null.tolist()})
        Threshold, Location, Scale, Standardised, Reps = E29.Thresholds(Name, Lengths, E29.PageAlpha(), Path=Path)
        Z = [(Best[I][0] - Location[I]) / Scale[I] for I in range(len(Best))]
        NullMax = Standardised.max(axis=1)
        Top = int(np.argmax(Z))
        P = (1 + int(np.sum(NullMax >= Z[Top]))) / (1 + Reps)
        Above = [PageNumbers[I] for I in range(len(Z)) if Best[I][0] > Threshold[I]]
        FF = {f"p{Pg}": {"z": round(Z[PageNumbers.index(Pg)], 2), "form": Best[PageNumbers.index(Pg)][1],
                         "threshold_margin": round(Best[PageNumbers.index(Pg)][0] - Threshold[PageNumbers.index(Pg)], 1)}
              for Pg in FFPages}
        Out[Name] = {"real_step_scores_raised": Changed, "null_page_bests_raised": NullChanged,
                     "best_page": PageNumbers[Top], "best_z": round(Z[Top], 2), "best_form": Best[Top][1],
                     "p_vs_null_max": round(P, 3), "above_threshold": Above, "ff_pages": FF}
        Lines.append(f"{Name}: {Changed} real step-view scores raised, {NullChanged} null page bests raised; "
                     f"best page p{PageNumbers[Top]} z {Z[Top]:.2f} ({Best[Top][1]}), p {P:.3f}; above threshold: "
                     f"{Above or 'none'}")
        Lines.append("    FF pages: " + ", ".join(f"{K} z {V['z']} margin {V['threshold_margin']}" for K, V in FF.items()))
    PowerPath = os.path.join(OutDir, "power_mabinogion.json")
    if os.path.exists(PowerPath):
        Lines.append("")
        Lines.append("Tier-1 plants needing an F-run option (Mabinogion key, fixed engine vs old engine, updated thresholds):")
        for R in E29.LoadJson(PowerPath)["rows"]:
            Lines.append(f"    {R['view']} {R['pattern']} p{R['page']} ({R['length']} runes): fixed {R['recovered']}/{R['plants']}, "
                         f"old {R['old_engine_recovered']}/{R['plants']}, min margin {R['min_margin']}")
    E29.SaveJson(os.path.join(OutDir, "summary.json"), Out)
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    print("\n".join(Lines))


if __name__ == "__main__":
    os.makedirs(OutDir, exist_ok=True)
    Stage = sys.argv[1]
    {"parity": StageParity, "rerun": StageRerun, "power": StagePower, "report": StageReport}[Stage]()
