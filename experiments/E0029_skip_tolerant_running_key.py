"""E0029 (B01): skip-tolerant, page-local running-key search over the text and file sources of E0008,
E0012 and E0024, with the lattice, view and polarity coverage of the council audit.

Hypothesis: each LP page is enciphered with a running key read from one of these sources, starting
anywhere (independently per page), with any ciphertext F possibly a non-consuming F-skip, in one of
4 views (raw29, step29, unit28z1, unit28z2), 4 polarities and 2 reading directions (32 forms).
Engine: lp.runningkey (exact DP over source position; any start, any skip set, any tokenisation).

Sources (CPU here; the byte files over 1 MB run in gpu/, see gpu/README.md):
  lp_plain       relikd's 9 solved plaintext files in book order (runes, no lattice)
  lp_cipher      the 9 solved ciphertext files in book order (runes)
  self_reliance  Emerson, Self-Reliance (Gutenberg 2944, the essay only; Latin with lattice)
  mabinogion     Guest's Mabinogion (Gutenberg 5160 body; Latin with lattice)
  growing_string the 2014 onion-3/4 growing string, 256 bytes, mod 29, tiled cyclically
  c560_13        2013 Cicada OS DATA/560.13 (134 bytes, mod 29, tiled)
  wisdom         2013 Cicada OS tmp/wisdom (3,368 bytes, mod 29)
  Bytes in the mod-28 views use (byte % 29) % 28.
Stages:
  controls  Koan 2 and Welcome (real solved pages with F-skips) with their keys hidden in the Mabinogion:
            full 32-form search, traceback, 20 shuffled-source nulls, rigid FFT comparison
  real      the 55 real pages, all forms, one source
  null      R shuffled-source replicates of the whole search (words permuted; bytes permuted before tiling)
  power     tier 1: 16 conditions (4 views x skip pattern none/early/mid/late) x 100 plants per source
  report    thresholds, verdicts, summary.txt
Usage: python3 experiments/E0029_skip_tolerant_running_key.py STAGE [--source NAME] [--reps R]
Outputs: results/E0029/ (small text/JSON); checkpoints in results/E0029/checkpoint/ (gitignored).
"""
import argparse
import json
import math
import multiprocessing
import os
import random
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.data import BaselineWords, DataDir, LoadAllUnsolved, LoadSection, Pages, RepoRoot, Words  # noqa: E402
from lp.detectors import FftRunningKeyScan  # noqa: E402
from lp.gematria import LatinToRunes  # noqa: E402
from lp import runningkey as Rk  # noqa: E402

OutDir = os.path.join(RepoRoot, "results", "E0029")
CheckDir = os.path.join(OutDir, "checkpoint")
BookOrder = ["0_warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity", "jpg107-167", "jpg229",
             "p56_an_end", "p57_parable"]
CpuSources = ["lp_plain", "lp_cipher", "self_reliance", "growing_string", "c560_13", "wisdom", "mabinogion"]
GpuSources = ["mp3_761", "c560_00", "c560_17", "lp_images"]
MinTiled = 4000
Workers = min(4, os.cpu_count() or 1)
FamilyAlpha = 0.01
FormNames = [(V, A, B, Rev) for Rev in (False, True) for V in Rk.Views for A, B in Rk.Polarities]


def FormKey(View, A, B, Rev):
    return f"{View}|{A:+d}{B:+d}|{'rev' if Rev else 'fwd'}"


def GutenbergBody(Path):
    with open(Path, encoding="utf-8") as Handle:
        Text = Handle.read()
    Start = Text.index("*** START OF")
    Start = Text.index("\n", Start) + 1
    return Text[Start:Text.index("*** END OF")]


def RawSource(Name):
    """(Kind, Chunks) of a named source before any null shuffle."""
    if Name in ("lp_plain", "lp_cipher"):
        Prefix = "solved_" if Name == "lp_plain" else ""
        return "runes", [W for N in BookOrder for W in Words(LoadSection(Prefix + N))]
    if Name == "self_reliance":
        Lines = GutenbergBody(os.path.join(DataDir, "texts", "emerson_essays1.txt")).split("\n")
        First = Lines.index("SELF-RELIANCE")
        Last = Lines.index("COMPENSATION", First)
        return "latin", "\n".join(Lines[First:Last])
    if Name == "mabinogion":
        return "latin", GutenbergBody(os.path.join(DataDir, "texts", "mabinogion.txt"))
    if Name == "growing_string":
        with open(os.path.join(DataDir, "keyfiles", "scream314_2014.md"), encoding="utf-8") as Handle:
            Lines = Handle.read().split("\n")
        Last = max(I for I, L in enumerate(Lines) if L == "\t<!--1033-->")  # the final, full string
        Hex = Lines[Last + 1].strip()
        assert len(Hex) == 512
        return "bytes", bytes.fromhex(Hex)
    Files = {"c560_13": "cicados/560.13", "wisdom": "cicados/wisdom", "mp3_761": "cicados/761.MP3",
             "c560_00": "cicados/_560.00", "c560_17": "cicados/560.17"}
    if Name in Files:
        with open(os.path.join(DataDir, "keyfiles", Files[Name]), "rb") as Handle:
            return "bytes", Handle.read()
    if Name == "lp_images":
        Data = b""
        for N in range(75):
            with open(os.path.join(DataDir, "keyfiles", "lp-images", f"{N:02d}.jpg"), "rb") as Handle:
                Data += Handle.read()
        return "bytes", Data
    raise KeyError(Name)


def BuildSource(Name, NullSeed=None, Extra=None):
    """Source object; NullSeed permutes words (or bytes, before tiling). Extra = Latin words appended
    at a fixed point (used by the controls to hide a key)."""
    Kind, Raw = RawSource(Name)
    if Kind == "latin":
        Chunks = [W for W in (Rk.NormaliseLatin(P) for P in Raw.split()) if W]
        if Extra:
            Mid = len(Chunks) // 2
            Chunks = Chunks[:Mid] + [Rk.NormaliseLatin(W) for W in Extra] + Chunks[Mid:]
    elif Kind == "runes":
        Chunks = [list(W) for W in Raw]
    else:
        Chunks = np.frombuffer(Raw, dtype=np.uint8).copy()
    if NullSeed is not None:
        Rng = np.random.default_rng(NullSeed)
        Chunks = Rng.permutation(Chunks) if Kind == "bytes" else [Chunks[I] for I in Rng.permutation(len(Chunks))]
    if Kind == "bytes" and len(Chunks) < MinTiled:
        Chunks = np.tile(Chunks, MinTiled // len(Chunks) + 2)
    Tag = Name if NullSeed is None else f"{Name}#null{NullSeed}"
    return Rk.Source(Tag, Kind, Chunks)


def PageAlpha():
    """Per-page level: family-wise FamilyAlpha over 55 pages x every source (CPU and GPU)."""
    return FamilyAlpha / (55 * len(CpuSources + GpuSources))


def RealPages():
    """List of (PageNumber, Runes) over the 9 unsolved sections."""
    return [(Number, Runes) for S in LoadAllUnsolved() for Number, Runes in Pages(S)]


_Cache = {}


def _Job(Args):
    Name, NullSeed, Rev, Modulus, B, PageList, Extra = Args
    Key = (Name, NullSeed, bool(Extra))
    if Key not in _Cache:
        _Cache.clear()
        _Cache[Key] = BuildSource(Name, NullSeed, Extra)
    Out = Rk.SearchCombo(PageList, _Cache[Key], Rev, Modulus, B)
    return {FormKey(V, A, Bb, R) + f"|{P}": S for (P, V, A, Bb, R), S in Out.items()}


def FullSearch(Name, PageList, NullSeeds=(None,), Extra=None, Pool=None):
    """Run every combo for every seed; returns {seed: {formkey|page: (score, endY)}}."""
    Jobs = [(Name, Seed, Rev, M, B, PageList, Extra) for Seed in NullSeeds for Rev, M, B in Rk.Combos()]
    Results = Pool.map(_Job, Jobs, chunksize=1) if Pool else list(map(_Job, Jobs))
    Out = {Seed: {} for Seed in NullSeeds}
    for Job, Res in zip(Jobs, Results):
        Out[Job[1]].update(Res)
    return Out


def PageBest(Scores, PageCount):
    """Per page: best score over forms and the form."""
    Best = [(-math.inf, None)] * PageCount
    for Key, (Score, _) in Scores.items():
        Form, Page = Key.rsplit("|", 1)
        Page = int(Page)
        if Score > Best[Page][0]:
            Best[Page] = (Score, Form)
    return Best


def SaveJson(Path, Obj):
    os.makedirs(os.path.dirname(Path), exist_ok=True)
    Tmp = Path + ".tmp"
    with open(Tmp, "w") as Handle:
        json.dump(Obj, Handle, indent=None, separators=(",", ":"))
    os.replace(Tmp, Path)


def LoadJson(Path):
    with open(Path) as Handle:
        return json.load(Handle)


def Log(Message):
    print(time.strftime("%H:%M:%S"), Message, flush=True)


# ---------------------------------------------------------------- stages

def StageReal(Name, Pool):
    PageList = [R for _, R in RealPages()]
    T = time.time()
    Scores = FullSearch(Name, PageList, Pool=Pool)[None]
    SaveJson(os.path.join(OutDir, f"real_{Name}.json"),
             {"source": Name, "pages": [N for N, _ in RealPages()],
              "scores": {K: [round(S, 3), E] for K, (S, E) in Scores.items()}})
    Log(f"real {Name}: {time.time() - T:.0f}s")


def StageNull(Name, Reps, Pool):
    PageList = [R for _, R in RealPages()]
    for Rep in range(Reps):
        Path = os.path.join(CheckDir, f"null_{Name}_{Rep:03d}.json")
        if os.path.exists(Path):
            continue
        T = time.time()
        Scores = FullSearch(Name, PageList, NullSeeds=(1000 + Rep,), Pool=Pool)[1000 + Rep]
        Best = PageBest(Scores, len(PageList))
        SaveJson(Path, {"best": [round(S, 3) for S, _ in Best], "form": [F for _, F in Best]})
        Log(f"null {Name} rep {Rep + 1}/{Reps}: {time.time() - T:.0f}s")
    Reps = sorted(F for F in os.listdir(CheckDir) if F.startswith(f"null_{Name}_"))
    Matrix = [LoadJson(os.path.join(CheckDir, F))["best"] for F in Reps]
    SaveJson(os.path.join(OutDir, f"null_{Name}.json"), {"source": Name, "reps": len(Matrix), "best": Matrix})


def Thresholds(Name, PageLengths, Alpha, Path=None):
    """Per-page Gumbel threshold at per-page level Alpha from the null replicates.

    Location per page from the replicate mean; scale pooled across pages as Kappa * sqrt(n) (the
    replicate sd of 20 values is too noisy to extrapolate on its own)."""
    Null = np.array(LoadJson(Path or os.path.join(OutDir, f"null_{Name}.json"))["best"])  # reps x pages
    Lengths = np.asarray(PageLengths, dtype=np.float64)
    Sd = Null.std(axis=0, ddof=1)
    Kappa = math.sqrt(np.mean(Sd ** 2 / Lengths))
    Scale = Kappa * np.sqrt(Lengths) * math.sqrt(6) / math.pi
    Location = Null.mean(axis=0) - 0.5772156649 * Scale
    Z = -math.log(-math.log(1 - Alpha))
    Standardised = (Null - Location) / Scale
    return Location + Z * Scale, Location, Scale, Standardised, Null.shape[0]


def PlantCorpus():
    return np.array([V for W in BaselineWords() for V in W], dtype=np.int64)


def MakePlant(Rng, Corpus, Page, View, Pattern, Src):
    """One plant in a real page layout. Returns (CipherRunes, Form, KeyStart, KeyLetters, Skips, KeyTokens)."""
    N = len(Page)
    Dbl = []
    if View.startswith("unit"):
        Dbl = [I for I in range(1, N) if Page[I] == Page[I - 1]]
    PlainLength = N if View == "raw29" else N - 1 - len(Dbl)
    DblPlain = {I - 1 - K for K, I in enumerate(Dbl)}
    for _ in range(200):
        Off = Rng.randrange(len(Corpus) - PlainLength)
        Plain = [int(V) for V in Corpus[Off:Off + PlainLength]]
        Fs = [I for I, P in enumerate(Plain) if P == 0]
        if Pattern == "none":
            Skips = set()
        elif Pattern == "early":
            First = [I for I in Fs if I < 50]
            if not First:
                continue
            Skips = {First[0]} | {I for I in Fs if I > First[0] and Rng.random() < 0.3}
        elif Pattern == "mid":
            First = [I for I in Fs if 80 <= I <= 130]
            if not First:
                continue
            Skips = {First[0]} | {I for I in Fs if I > First[0] and Rng.random() < 0.3}
        else:
            Late = [I for I in Fs if I >= PlainLength - 70]
            if not Late:
                continue
            Skips = {Late[0]} | {I for I in Late[1:] if Rng.random() < 0.5}
        break
    else:
        raise RuntimeError("no plaintext with the required F layout")
    A, B = Rng.choice(Rk.Polarities)
    Rev = Rng.random() < 0.5
    S = Src.Reverse() if Rev else Src
    Need = PlainLength + len(Dbl) + 5
    Start = Rng.randrange(0, S.Length - 3 * Need - 10)
    Key, Letters = Rk.RandomTokens(S, Start, Need, Rng)
    Cipher, _ = Rk.PlantPage(Plain, Key, View, A, B, Skips, DblPlain, Rng, Start=Page[0])
    return Cipher, (View, A, B, Rev), Start, Letters, Skips, Key


LengthEdges = [(0, 140), (141, 220), (221, 999)]


def LengthBins(PerPlant):
    """Recovered/plants per page-length bin from [[length, margin], ...]."""
    Out = {}
    for Lo, Hi in LengthEdges:
        In = [M for N, M in PerPlant if Lo <= N <= Hi]
        if In:
            Out[f"{Lo}-{Hi}"] = [int(sum(M > 0 for M in In)), len(In)]
    return Out


def StagePower(Name, Plants, Pool):
    Rng = random.Random(28)
    Corpus = PlantCorpus()
    Src = BuildSource(Name)
    PageItems = RealPages()
    Threshold, *_ = Thresholds(Name, [len(R) for _, R in PageItems], PageAlpha())
    RigidPath = os.path.join(OutDir, f"rigidnull_{Name}.json")
    RigidThreshold = None
    if os.path.exists(RigidPath):
        RigidThreshold, *_ = Thresholds(Name, [len(R) for _, R in PageItems], PageAlpha(), Path=RigidPath)
    W29 = Rk.Weights(29)
    Rows = []
    for View, Pattern, (BinLo, BinHi) in [(V, P, E) for V in Rk.Views for P in ("none", "early", "mid", "late")
                                          for E in LengthEdges]:
        InBin = [I for I, (_, R) in enumerate(PageItems) if BinLo <= len(R) <= BinHi]
        Hits, Margins, Exact, RigidHits, PerPlant = 0, [], 0, 0, []
        for Index in range(Plants):
            for Attempt in range(50):  # a page that can host the pattern (mid needs an F at plaintext 80-130)
                PageIndex = Rng.choice(InBin)
                Page = PageItems[PageIndex][1]
                try:
                    Cipher, (V, A, B, Rev), Start, Letters, Skips, Key = MakePlant(Rng, Corpus, Page, View, Pattern, Src)
                    break
                except RuntimeError:
                    continue
            else:
                break
            S = Src.Reverse() if Rev else Src
            Lo, Hi = max(0, Start - 30), min(S.Length, Start + Letters + 30)
            Window = S.Slice(Lo, Hi)
            Tab = Rk.Tables(Window, Rk.ViewModulus[V], B)
            Vec = Rk.RunEvents(Rk.PageEvents(Cipher, V), Tab, A)
            End = int(np.argmax(Vec))
            Score = float(Vec[End])
            Margin = float(Score - Threshold[PageIndex])
            Hits += int(Margin > 0)
            Margins.append(Margin)
            if Index < 3:
                Tr = Rk.Trace(Cipher, Window, V, A, B, End)
                Exact += Lo + Tr["StartY"] == Start
            if V == "raw29" and RigidThreshold is not None:
                # best case for rigid: it is given the plant's own tokens, padded with single-letter
                # tokens of the neighbouring source, and every offset in between
                Ext = np.array(list(S.Tok1[max(0, Start - 40):Start]) + Key + list(S.Tok1[Start + Letters:Start + Letters + 40]), dtype=np.int64)
                Ci = np.asarray(Cipher)
                Rigid = max(float(W29[(A * Ci + B * Ext[O:O + len(Ci)]) % 29].sum())
                            for O in range(0, len(Ext) - len(Ci) + 1))
                RigidHits += int(Rigid > RigidThreshold[PageIndex])
            PerPlant.append([len(Page), round(Margin, 1)])
        if not Margins:
            Log(f"power {Name} {View} {Pattern} {BinLo}-{BinHi}: pattern impossible on these pages")
            continue
        Rows.append({"view": View, "pattern": Pattern, "bin": f"{BinLo}-{BinHi}", "recovered": Hits, "plants": len(Margins),
                     "min_margin": round(min(Margins), 1), "median_margin": round(float(np.median(Margins)), 1),
                     "start_exact_of_3": Exact,
                     "rigid_recovered": RigidHits if (V == "raw29" and RigidThreshold is not None) else None,
                     "by_page_length": LengthBins(PerPlant)})
        Log(f"power {Name} {View} {Pattern} {BinLo}-{BinHi}: {Hits}/{len(Margins)}, min margin {min(Margins):.1f}"
            + (f", rigid {RigidHits}" if V == "raw29" and RigidThreshold is not None else ""))
    SaveJson(os.path.join(OutDir, f"power_{Name}.json"), {"source": Name, "rows": Rows})


def _RigidJob(Args):
    Name, Seed, Page = Args
    Src = BuildSource(Name, Seed)
    return max(RigidScan(Page, S, A, B)[0] for S in (Src, Src.Reverse()) for A, B in Rk.Polarities)


def RigidScan(Cipher, Src, A, B):
    """Rigid FFT running-key scan, no skips: best total over offsets. Latin sources use greedy
    LatinToRunes tokens (read backwards for a reversed source)."""
    if Src.Kind == "latin":
        Key = LatinToRunes(" ".join(Src.Chunks))
        Key = Key[::-1] if Src.Reversed else Key
    else:
        Key = list(Src.Tok1)
    C = (A * np.asarray(Cipher)) % 29
    Scores = FftRunningKeyScan(np.asarray(Key), C, Sign=B)
    return float(Scores.max() * len(Cipher)), int(np.argmax(Scores))


def StageRigidNull(Name, Reps, Pool):
    """Rigid-FFT null per page (raw29, 4 polarities x 2 directions) on shuffled sources, for the
    rigid-vs-engine comparison in the power stage."""
    PageList = [R for _, R in RealPages()]
    Jobs = [(Name, 1000 + Rep, Page) for Rep in range(Reps) for Page in PageList]
    Flat = Pool.map(_RigidJob, Jobs, chunksize=4)
    Matrix = [Flat[Rep * len(PageList):(Rep + 1) * len(PageList)] for Rep in range(Reps)]
    SaveJson(os.path.join(OutDir, f"rigidnull_{Name}.json"), {"source": Name, "reps": Reps, "best": Matrix})
    Log(f"rigid null {Name}: {Reps} reps")


def StageControls(Pool, Reps=20):
    """Koan 2 (FIRFUMFERENFE, F-skips 2,3) and Welcome (DIVINITY, 11 F-skips) as real-world controls."""
    Cases = [("koan2", "jpg107-167", "FIRFUMFERENFE", 25, [2, 3]),
             ("welcome", "0_welcome", "DIVINITY", 66, [4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25])]
    Out = {}
    for Tag, File, Key, Repeat, Ordinals in Cases:
        Cipher = LoadSection(File)["Runes"]
        Plain = LoadSection("solved_" + File)["Runes"]
        Extra = [Key] * Repeat
        Src = BuildSource("mabinogion", Extra=Extra)
        Scores = FullSearch("mabinogion", [Cipher], Extra=Extra, Pool=Pool)[None]
        Ranked = sorted(Scores.items(), key=lambda KV: -KV[1][0])
        (TopKey, (TopScore, TopEnd)), (SecondKey, (SecondScore, _)) = Ranked[0], Ranked[1]
        View, Pol, Dirn, _ = TopKey.split("|")
        A, B = int(Pol[:2]), int(Pol[2:])
        Tr = Rk.Trace(Cipher, Src if Dirn == "fwd" else Src.Reverse(), View, A, B, TopEnd)
        FPositions = [I for I, V in enumerate(Cipher) if V == 0]
        Truth = sorted(FPositions[O - 1] for O in Ordinals)
        GotSkips = [I for I, _ in Tr["Skips"]]
        Mid = len([W for W in (Rk.NormaliseLatin(P) for P in RawSource("mabinogion")[1].split()) if W]) // 2
        KeyStart = sum(len(W) for W in Src.Chunks[:Mid])
        # null: identical full search with the (key-hiding) source word-shuffled
        NullBest = []
        for Rep in range(Reps):
            NullScores = FullSearch("mabinogion", [Cipher], NullSeeds=(500 + Rep,), Extra=Extra, Pool=Pool)[500 + Rep]
            NullBest.append(max(S for S, _ in NullScores.values()))
        Loc, Scale = Rk.GumbelFromMoments(NullBest)
        Z = (TopScore - Loc) / Scale
        RigidReal = max(RigidScan(Cipher, Src, A, B)[0] for A, B in Rk.Polarities)
        RigidNull = [max(RigidScan(Cipher, BuildSource("mabinogion", 500 + Rep, Extra), A, B)[0]
                         for A, B in Rk.Polarities) for Rep in range(Reps)]
        Stream = LatinToRunes(" ".join(Src.Chunks))
        KeyRunes = LatinToRunes(Rk.NormaliseLatin(Key) * Repeat)
        Pos = next(I for I in range(len(Stream)) if Stream[I:I + 40] == KeyRunes[:40])
        RigidTrue = float(sum(Rk.Weights(29)[(C - Stream[Pos + I]) % 29] for I, C in enumerate(Cipher)))
        RLoc, RScale = Rk.GumbelFromMoments(RigidNull)
        Row = {"case": Tag, "runes": len(Cipher), "top_form": TopKey.rsplit("|", 1)[0], "top_score": round(TopScore, 1),
               "second": [SecondKey.rsplit("|", 1)[0], round(SecondScore, 1)],
               "start_found": Tr["StartY"], "start_true": KeyStart, "skips_found": GotSkips, "skips_true": Truth,
               "plain_exact": Tr["Plain"] == Plain, "null_max": [round(min(NullBest), 1), round(max(NullBest), 1)],
               "gumbel_z": round(Z, 1), "rigid_best": round(RigidReal, 1), "rigid_at_true_offset": round(RigidTrue, 1),
               "rigid_null": [round(min(RigidNull), 1), round(max(RigidNull), 1)],
               "rigid_gumbel_z": round((RigidReal - RLoc) / RScale, 1)}
        Out[Tag] = Row
        Log(f"control {Tag}: {Row}")
    SaveJson(os.path.join(OutDir, "controls.json"), Out)


def StageImportGpu(Path):
    """Turn gpu/E0029_bytes_gpu.py's results file into real_/null_/power_ files for the report."""
    Gpu = LoadJson(Path)
    Pages = RealPages()
    Lengths = [len(R) for _, R in Pages]
    Lines = [f"gpu env: {Gpu['env']}", f"gpu controls: {json.dumps(Gpu['control'])}"]
    for Name, Scores in Gpu["real"].items():
        if len(Scores) < 32 * len(Pages):
            Lines.append(f"{Name}: real search incomplete ({len(Scores)} of {32 * len(Pages)}); skipped")
            continue
        SaveJson(os.path.join(OutDir, f"real_{Name}.json"), {"source": Name, "pages": [N for N, _ in Pages],
                                                            "scores": Scores, "via": "gpu"})
        Null = Gpu["null"].get(Name, [])
        if len(Null) < 2:
            Lines.append(f"{Name}: {len(Null)} null reps; need >= 2")
            continue
        SaveJson(os.path.join(OutDir, f"null_{Name}.json"), {"source": Name, "reps": len(Null), "best": Null, "via": "gpu"})
        Threshold, *_ = Thresholds(Name, Lengths, PageAlpha())
        Rows = []
        for View in Rk.Views:
            for Pattern in ("none", "early", "mid", "late"):
                for BinLo, BinHi in LengthEdges:
                    Bin = f"{BinLo}-{BinHi}"
                    Plants = [R for R in Gpu["power"].get(Name, []) if R[0] == View and R[1] == Pattern and R[5] == Bin]
                    Margins = [R[3] - Threshold[R[2]] for R in Plants]
                    if Margins:
                        Rows.append({"view": View, "pattern": Pattern, "bin": Bin,
                                     "recovered": int(sum(M > 0 for M in Margins)), "plants": len(Margins),
                                     "min_margin": round(min(Margins), 1), "median_margin": round(float(np.median(Margins)), 1)})
        SaveJson(os.path.join(OutDir, f"power_{Name}.json"), {"source": Name, "rows": Rows, "via": "gpu"})
        Lines.append(f"{Name}: imported ({len(Null)} null reps)")
    with open(os.path.join(OutDir, "gpu_import.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    print("\n".join(Lines))


def StageReport():
    PageItems = RealPages()
    Lengths = [len(R) for _, R in PageItems]
    Numbers = [N for N, _ in PageItems]
    Sources = [S for S in CpuSources + GpuSources if os.path.exists(os.path.join(OutDir, f"null_{S}.json"))
               and os.path.exists(os.path.join(OutDir, f"real_{S}.json"))]
    Alpha = PageAlpha()
    Lines = ["E0029 (B01) skip-tolerant page-local running-key search: summary", ""]
    if os.path.exists(os.path.join(OutDir, "controls.json")):
        Lines.append("Real-world controls (key hidden in the Mabinogion, full 32-form search):")
        for Tag, Row in LoadJson(os.path.join(OutDir, "controls.json")).items():
            Lines.append(f"  {Tag}: top {Row['top_form']} score {Row['top_score']} (null max {Row['null_max']}, "
                         f"Gumbel z {Row['gumbel_z']}); start {Row['start_found']} vs true {Row['start_true']}; "
                         f"skips {Row['skips_found']} vs true {Row['skips_true']}; plaintext exact {Row['plain_exact']}")
            Lines.append(f"      rigid FFT best {Row['rigid_best']} (null {Row['rigid_null']}, z {Row['rigid_gumbel_z']}); "
                         f"rigid score at the true offset {Row['rigid_at_true_offset']}")
        Lines.append("")
    Lines.append(f"Per-page threshold: Gumbel at per-page alpha {Alpha:.2e} (family-wise 0.01 over 55 pages x "
                 f"{len(CpuSources + GpuSources)} sources); location from replicate mean, scale pooled as k*sqrt(n).")
    Summary = {}
    for Name in Sources:
        Threshold, Location, Scale, Std, Reps = Thresholds(Name, Lengths, Alpha)
        Real = LoadJson(os.path.join(OutDir, f"real_{Name}.json"))["scores"]
        Best = PageBest({K: tuple(V) for K, V in Real.items()}, len(PageItems))
        RealStd = np.array([(S - L) / Sc for (S, _), L, Sc in zip(Best, Location, Scale)])
        Top = int(np.argmax(RealStd))
        NullMax = Std.max(axis=1)
        P = (1 + int(np.sum(NullMax >= RealStd.max()))) / (1 + Reps)
        Above = [Numbers[I] for I in range(len(PageItems)) if Best[I][0] > Threshold[I]]
        Line = (f"{Name}: {Reps} null reps; best page p{Numbers[Top]} ({Best[Top][1]}) Gumbel-standardised "
                f"{RealStd[Top]:.2f} (threshold {-math.log(-math.log(1 - Alpha)):.2f}); null max-over-pages "
                f"{NullMax.min():.2f}..{NullMax.max():.2f}, p {P:.3f}; pages above threshold: {Above or 'none'}")
        Power = os.path.join(OutDir, f"power_{Name}.json")
        if os.path.exists(Power):
            Rows = LoadJson(Power)["rows"]
            for Bin in sorted({R.get("bin", "all") for R in Rows}):
                In = [R for R in Rows if R.get("bin", "all") == Bin]
                Worst = min(In, key=lambda R: R["recovered"] / R["plants"])
                Line += (f"\n    power, pages {Bin} runes: worst {Worst['recovered']}/{Worst['plants']} ({Worst['view']}/{Worst['pattern']}); "
                         + ", ".join(f"{R['view'][:6]}/{R['pattern']} {R['recovered']}/{R['plants']}"
                                     + (f" rigid {R['rigid_recovered']}" if R.get("rigid_recovered") is not None else "")
                                     for R in In))
        Lines.append(Line)
        Summary[Name] = {"best_page": Numbers[Top], "best_form": Best[Top][1], "best_std": round(float(RealStd[Top]), 2),
                         "p_vs_null_reps": round(P, 3), "above_threshold": Above}
    SaveJson(os.path.join(OutDir, "summary.json"), Summary)
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    print("\n".join(Lines))


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("stage", choices=["controls", "real", "null", "power", "report", "all", "import-gpu", "rigid"])
    Parser.add_argument("--file", default=os.path.join(RepoRoot, "gpu", "results_E0029_gpu.json"))
    Parser.add_argument("--source", default=None)
    Parser.add_argument("--reps", type=int, default=20)
    Parser.add_argument("--plants", type=int, default=100)
    Args = Parser.parse_args()
    os.makedirs(CheckDir, exist_ok=True)
    if Args.stage == "import-gpu":
        StageImportGpu(Args.file)
        return
    Names = [Args.source] if Args.source else CpuSources
    with multiprocessing.get_context("fork").Pool(Workers) as Pool:
        if Args.stage in ("controls", "all") and not (Args.stage == "all" and os.path.exists(os.path.join(OutDir, "controls.json"))):
            StageControls(Pool)
        for Name in Names:
            if Args.stage in ("real", "all") and not (Args.stage == "all" and os.path.exists(os.path.join(OutDir, f"real_{Name}.json"))):
                StageReal(Name, Pool)
            if Args.stage in ("null", "all"):
                StageNull(Name, Args.reps, Pool)
            if Args.stage == "rigid":
                StageRigidNull(Name, Args.reps, Pool)
            if Args.stage in ("power", "all") and not (Args.stage == "all" and os.path.exists(os.path.join(OutDir, f"power_{Name}.json"))):
                StagePower(Name, Args.plants, Pool)
    if Args.stage in ("report", "all"):
        StageReport()


if __name__ == "__main__":
    Main()
