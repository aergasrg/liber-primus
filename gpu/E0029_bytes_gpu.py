"""E0029 (B01) GPU job: skip-tolerant, page-local running-key search of the 55 unsolved Liber Primus pages
against the large byte sources (2013 Cicada OS files 761.MP3, _560.00, 560.17, and the 75 original LP
page images), byte % 29, in 4 views x 4 polarities x 2 directions.

Self-contained (Python 3.10+, PyTorch; CUDA used when available). It downloads what it needs into
./cache next to this file, then:
  1. planted-key control: keys from each source planted (with F-skips) into real page layouts must be
     found by the full search at the planted offset and form, or the job stops;
  2. the real search (best score per page and form, every source);
  3. tier-1 plants (16 conditions x 100 per source; scores only, thresholds are applied in the lab);
  4. shuffled-source null replicates, round-robin over sources, until done or --hours runs out.
Progress is saved after every unit (a few minutes at most) to ./results_E0029_gpu.json; rerunning the
same command resumes. Upload that one file. GPU memory stays under about 2 GB (asserted < 5 GB).

The algorithm mirrors lp/runningkey.py in the lab repository (same events, tables and DP); the lab's
CPU version was checked against this file on small sources before release.
Usage: python E0029_bytes_gpu.py [--hours 15] [--reps 10] [--image-reps 6] [--quick]
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request

import numpy as np
import torch

Here = os.path.dirname(os.path.abspath(__file__))
Cache = os.path.join(Here, "cache")
ResultsPath = os.path.join(Here, "results_E0029_gpu.json")
Relikd = "https://raw.githubusercontent.com/relikd/LiberPrayground/main"
Scream = "https://raw.githubusercontent.com/scream314/cicada3301/master/assets"
RuneString = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
RuneIndex = {R: I for I, R in enumerate(RuneString)}
RuneIndex["ᛂ"] = 11
UnsolvedNames = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32", "p33-39", "p40-53", "p54-55"]
PageLines = {  # copy of lp.data.PageLines (lines per real page)
    "p0-2": [12, 12, 9], "p3-7": [11, 12, 12, 10, 10], "p8-14": [12, 12, 12, 12, 12, 12, 7],
    "p15-22": [12, 12, 12, 12, 12, 12, 12, 6], "p23-26": [10, 12, 12, 12], "p27-32": [11, 12, 12, 12, 12, 6],
    "p33-39": [11, 12, 12, 11, 11, 11, 12], "p40-53": [11, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 12, 9],
    "p54-55": [11, 4]}
SourceFiles = {"c560_17": ["2013/cicados/DATA/560.17"], "c560_00": ["2013/cicados/DATA/_560.00"],
               "mp3_761": ["2013/cicados/AUDIO/761.MP3"],
               "lp_images": [f"2014/liber-primus-complete/{N:02d}.jpg" for N in range(75)]}
SourceOrder = ["c560_17", "c560_00", "mp3_761", "lp_images"]
Views = ["raw29", "step29", "unit28z1", "unit28z2"]
ViewModulus = {"raw29": 29, "step29": 29, "unit28z1": 28, "unit28z2": 28}
Polarities = [(1, -1), (-1, 1), (1, 1), (-1, -1)]
LengthEdges = [(0, 140), (141, 220), (221, 999)]
Combos = [(Rev, M, B) for Rev in (False, True) for M in (29, 28) for B in (-1, 1)]
Device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NegInf = float("-inf")


def Log(Message):
    print(time.strftime("%H:%M:%S"), Message, flush=True)


def Download(Url, Path):
    if os.path.exists(Path) and os.path.getsize(Path) > 0:
        return
    os.makedirs(os.path.dirname(Path), exist_ok=True)
    for Try in range(5):
        try:
            with urllib.request.urlopen(Url, timeout=120) as Response, open(Path + ".part", "wb") as Out:
                Out.write(Response.read())
            os.replace(Path + ".part", Path)
            return
        except Exception as Error:  # network hiccup: back off and retry
            Log(f"download retry {Try + 1}: {Url} ({Error})")
            time.sleep(2 ** (Try + 1))
    raise SystemExit(f"could not download {Url}")


def LoadPages():
    """55 real pages as rune lists (page map identical to lp.data.PageLines)."""
    Pages = []
    for Name in UnsolvedNames:
        Path = os.path.join(Cache, "pages", Name + ".txt")
        Download(f"{Relikd}/pages/{Name}.txt", Path)
        with open(Path, encoding="utf-8") as Handle:
            Lines = [L for L in Handle.read().split("\n") if L.strip()]
        Counts = PageLines[Name]
        if len(Lines) != sum(Counts):
            raise SystemExit(f"{Name}: line count changed upstream; stop")
        Index = 0
        for Count in Counts:
            Runes = [RuneIndex[C] for L in Lines[Index:Index + Count] for C in L if C in RuneIndex]
            Index += Count
            if Runes:
                Pages.append(Runes)
    if len(Pages) != 55 or sum(map(len, Pages)) != 12956 or len(Pages[0]) != 262:
        raise SystemExit("page map self-check failed (expected 55 pages, 12956 runes)")
    return Pages


def LoadEnglish():
    """(Weights29, Weights28, PlantCorpus) from relikd's baseline English corpus in runes."""
    Path = os.path.join(Cache, "baseline-rune-words.txt")
    Download(f"{Relikd}/data/baseline-rune-words.txt", Path)
    Counts = np.zeros(29)
    Corpus = []
    with open(Path, encoding="utf-8") as Handle:
        for Line in Handle:
            Word = [RuneIndex[C] for C in Line.strip() if C in RuneIndex]
            Corpus += Word
            for V in Word:
                Counts[V] += 1
    Total = Counts.sum()
    W29 = np.log((Counts + 1) / Total * 29)
    C28 = Counts[:28].copy()
    C28[0] += Counts[28]
    W28 = np.log((C28 + 1) / Total * 28)
    return W29, W28, np.array(Corpus, dtype=np.int64)


def LoadSource(Name):
    Data = b""
    for Rel in SourceFiles[Name]:
        Path = os.path.join(Cache, "sources", Rel.replace("/", "_"))
        Download(f"{Scream}/{Rel}", Path)
        with open(Path, "rb") as Handle:
            Data += Handle.read()
    return np.frombuffer(Data, dtype=np.uint8).astype(np.int64) % 29


def PageEvents(Runes, View, SkipScore):
    """Same events as lp.runningkey.PageEvents: list of (CipherIndex, [(Atoms, Const), ...]).
    In the step views each F of an F-run is keyed, a literal skip or a transparent skip (B24)."""
    C = list(Runes)
    N = len(C)
    if View == "raw29":
        return [(I, [((0,), 0.0), ((), SkipScore)] if V == 0 else [((V,), 0.0)]) for I, V in enumerate(C)]

    def Atom(Step):
        Step %= 29
        if View == "step29":
            return (Step,)
        if Step:
            return ((Step - 1) % 28,)
        return (-1,) if View == "unit28z1" else ()

    Events = []
    I = 1
    while I < N:
        if C[I] != 0:
            Events.append((I, [(Atom(C[I] - C[I - 1]), 0.0)]))
            I += 1
            continue
        J = I
        while J < N and C[J] == 0:
            J += 1
        Paths = [(C[I - 1], (), 0)]  # (State, Atoms, Skips), first-seen order
        for K in range(I, J):
            Next = []
            for State, Atoms, Skips in Paths:
                for Item in [(0, Atoms + Atom(0 - State), Skips), (0, Atoms, Skips + 1), (State, Atoms, Skips + 1)]:
                    if Item not in Next:
                        Next.append(Item)
            Paths = Next
        Options = []
        for State, Atoms, Skips in Paths:
            if J < N:
                Atoms = Atoms + Atom(C[J] - State)
            if (Atoms, Skips) not in Options:
                Options.append((Atoms, Skips))
        Options.sort(key=lambda Key: (Key[1], len(Key[0])))
        Events.append((I, [(Atoms, Skips * SkipScore) for Atoms, Skips in Options]))
        I = J + 1
    return Events


class Engine:
    """Forward DP over every start offset of one token tensor (bytes: no tokenisation lattice)."""

    def __init__(self, Tokens, W29, W28):
        self.Tok = torch.as_tensor(np.ascontiguousarray(Tokens), dtype=torch.int64, device=Device)
        self.W = {29: W29, 28: W28}
        self.Length = len(Tokens)

    def SetCombo(self, Modulus, B):
        W = self.W[Modulus]
        Tokens = np.arange(29) % Modulus
        Tab = np.zeros((Modulus + 1, 29), dtype=np.float32)
        for X in range(Modulus):
            Tab[X] = W[(X + B * Tokens) % Modulus]
        self.Tab = torch.as_tensor(Tab, device=Device)
        self.Modulus = Modulus

    def Apply(self, V, Atom, A, Out):
        Out[0] = NegInf
        if Atom < 0:
            Out[1:] = V[:-1]
        else:
            torch.add(V[:-1], torch.take(self.Tab[(A * Atom) % self.Modulus], self.Tok), out=Out[1:])
        return Out

    def Run(self, Events, A):
        V = torch.zeros(self.Length + 1, dtype=torch.float32, device=Device)
        Spare = torch.empty_like(V)
        for _, Options in Events:
            if len(Options) == 1 and len(Options[0][0]) == 1 and not Options[0][1]:
                Spare = self.Apply(V, Options[0][0][0], A, Spare)
                V, Spare = Spare, V
                continue
            Best = None
            for Atoms, Const in Options:
                Cur = V
                for Atom in Atoms:
                    Cur = self.Apply(Cur, Atom, A, torch.empty_like(V))
                if Const:
                    Cur = Cur + Const
                Best = Cur if Best is None else torch.maximum(Best, Cur)
            V = Best
        Score, End = torch.max(V, dim=0)
        return float(Score), int(End)


def FormKey(View, A, B, Rev):
    return f"{View}|{A:+d}{B:+d}|{'rev' if Rev else 'fwd'}"


def SearchCombo(Eng, PageList, Rev, Modulus, B, Skip):
    Eng.SetCombo(Modulus, B)
    Out = {}
    for View in [V for V in Views if ViewModulus[V] == Modulus]:
        for Page, Runes in enumerate(PageList):
            Events = PageEvents(Runes, View, Skip[Modulus])
            for A in (1, -1):
                Out[FormKey(View, A, B, Rev) + f"|{Page}"] = Eng.Run(Events, A)
    return Out


def PlantPage(Plain, Key, View, A, B, SkipAt, Doublets, Rng, Start):
    """Same as lp.runningkey.PlantPage."""
    Key = iter(Key)
    if View == "raw29":
        Out = []
        for I, P in enumerate(Plain):
            Out.append(0 if I in SkipAt else (A * (P - B * next(Key))) % 29)
        return Out
    Out, State = [Start], Start
    for I, P in enumerate(Plain):
        if View != "step29" and I in Doublets:
            Out.append(Out[-1])
            State = Out[-1]
            if View == "unit28z1":
                next(Key)
        if I in SkipAt:
            Out.append(0)
            if Rng.random() < 0.5:
                State = 0
            continue
        K = next(Key)
        Step = (A * (P - B * K)) % 29 if View == "step29" else 1 + (A * (P % 28 - B * K)) % 28
        State = (State + Step) % 29
        Out.append(State)
    return Out


def MakePlant(Rng, Corpus, Page, View, Pattern, SourceLength):
    """Plaintext + skip mask in a real page layout (same patterns as the lab's E0029 power stage)."""
    N = len(Page)
    Dbl = [I for I in range(1, N) if Page[I] == Page[I - 1]] if View.startswith("unit") else []
    PlainLength = N if View == "raw29" else N - 1 - len(Dbl)
    DblPlain = {I - 1 - K for K, I in enumerate(Dbl)}
    for _ in range(200):
        Off = Rng.randrange(len(Corpus) - PlainLength)
        Plain = [int(V) for V in Corpus[Off:Off + PlainLength]]
        Fs = [I for I, P in enumerate(Plain) if P == 0]
        if Pattern == "none":
            Skips = set()
        elif Pattern in ("early", "mid"):
            First = [I for I in Fs if (I < 50 if Pattern == "early" else 80 <= I <= 130)]
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
        return None
    A, B = Rng.choice(Polarities)
    Rev = Rng.random() < 0.5
    Need = PlainLength + len(Dbl) + 5
    Start = Rng.randrange(0, SourceLength - Need - 10)
    return Plain, Skips, DblPlain, (View, A, B, Rev), Start, Need


def SaveResults(Results):
    Tmp = ResultsPath + ".tmp"
    with open(Tmp, "w") as Handle:
        json.dump(Results, Handle, separators=(",", ":"))
    os.replace(Tmp, ResultsPath)


def CheckMemory(Results):
    if Device.type == "cuda":
        Peak = torch.cuda.max_memory_allocated() / 2 ** 30
        Results["env"]["peak_gpu_gb"] = round(Peak, 2)
        if Peak > 5:
            raise SystemExit(f"GPU memory {Peak:.1f} GB > 5 GB; stop")


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("--hours", type=float, default=15.0, help="stop starting new null units after this")
    Parser.add_argument("--reps", type=int, default=10, help="null replicates per small source")
    Parser.add_argument("--image-reps", type=int, default=6, help="null replicates for lp_images")
    Parser.add_argument("--plants", type=int, default=100)
    Parser.add_argument("--quick", action="store_true", help="5-minute smoke test on small slices")
    Args = Parser.parse_args()
    Began = time.time()
    torch.set_grad_enabled(False)
    Results = json.load(open(ResultsPath)) if os.path.exists(ResultsPath) and not Args.quick else {}
    Results.setdefault("env", {})
    Results["env"].update({"device": str(Device), "torch": torch.__version__, "python": sys.version.split()[0],
                           "gpu": torch.cuda.get_device_name(0) if Device.type == "cuda" else None})
    Results.setdefault("control", {})
    Results.setdefault("real", {})
    Results.setdefault("power", {})
    Results.setdefault("null", {})
    Results.setdefault("done_units", [])
    Log(f"device {Device}; results -> {ResultsPath}")
    Pages = LoadPages()
    W29, W28, Corpus = LoadEnglish()
    Skip = {29: float(W29[0]), 28: float(W28[0])}
    Names = SourceOrder
    Sources = {}
    for Name in Names:
        Tokens = LoadSource(Name)
        if Args.quick:
            Tokens = Tokens[:200_000]
        Sources[Name] = Tokens
        Results["env"].setdefault("source_lengths", {})[Name] = int(len(Tokens))
    PageList = Pages[:3] if Args.quick else Pages
    Plants = 5 if Args.quick else Args.plants
    Done = set(Results["done_units"])

    def Finish(Unit):
        Done.add(Unit)
        Results["done_units"] = sorted(Done)
        CheckMemory(Results)
        SaveResults(Results)

    # 1. planted-key controls: full search of a planted page over the whole source, all 32 forms
    Rng = random.Random(3301)
    for Name in Names:
        Unit = f"control|{Name}"
        if Unit in Done:
            continue
        T = time.time()
        Rows = []
        for View, Pattern in (("raw29", "early"), ("unit28z1", "mid")):
            Plant = None
            while not Plant:
                Page = Pages[Rng.randrange(len(Pages))]
                Plant = MakePlant(Rng, Corpus, Page, View, Pattern, len(Sources[Name]))
            Plain, Skips, Dbl, (V, A, B, Rev), Start, Need = Plant
            Tok = Sources[Name][::-1] if Rev else Sources[Name]
            Cipher = PlantPage(Plain, Tok[Start:Start + Need], V, A, B, Skips, Dbl, Rng, Page[0])
            Eng = Engine(Tok, W29, W28)
            Scores = {}
            for Rv, M, Bb in Combos:
                Eng.Tok = torch.as_tensor(Sources[Name][::-1].copy() if Rv else Sources[Name], device=Device)
                Scores.update(SearchCombo(Eng, [Cipher], Rv, M, Bb, Skip))
            Top = max(Scores, key=lambda K: Scores[K][0])
            # found = the planted form wins and its path ends inside the planted key span
            Ok = Top.rsplit("|", 1)[0] == FormKey(V, A, B, Rev) and Start < Scores[Top][1] <= Start + Need
            Rows.append({"view": V, "pattern": Pattern, "form": FormKey(V, A, B, Rev), "top": Top,
                         "score": round(Scores[Top][0], 2), "start": Start, "end_found": Scores[Top][1],
                         "skips": len(Skips), "ok": bool(Ok)})
        Results["control"][Name] = Rows
        Log(f"control {Name}: {[R['ok'] for R in Rows]} scores {[R['score'] for R in Rows]} ({time.time() - T:.0f}s)")
        if not all(R["ok"] for R in Rows):
            SaveResults(Results)
            raise SystemExit("planted-key control FAILED; nothing else is meaningful. Upload the results file.")
        Finish(Unit)

    # 2. real search
    for Name in Names:
        Eng = Engine(Sources[Name], W29, W28)
        Results["real"].setdefault(Name, {})
        for Rev, M, B in Combos:
            Unit = f"real|{Name}|{Rev}|{M}|{B}"
            if Unit in Done:
                continue
            T = time.time()
            Eng.Tok = torch.as_tensor(Sources[Name][::-1].copy() if Rev else Sources[Name], device=Device)
            Out = SearchCombo(Eng, PageList, Rev, M, B, Skip)
            Results["real"][Name].update({K: [round(S, 3), E] for K, (S, E) in Out.items()})
            Log(f"real {Name} rev={Rev} mod={M} b={B}: {time.time() - T:.0f}s")
            Finish(Unit)
        del Eng

    # 3. tier-1 plants (windowed scores; the lab applies the null thresholds)
    for Name in Names:
        Unit = f"power|{Name}"
        if Unit in Done:
            continue
        T = time.time()
        Rng = random.Random(28)
        Rows = []
        for View in Views:
            for Pattern in ("none", "early", "mid", "late"):
                for BinLo, BinHi in LengthEdges:  # 100 plants per page-length bin, as in the lab
                    InBin = [I for I, R in enumerate(PageList) if BinLo <= len(R) <= BinHi]
                    for _ in range(Plants if InBin else 0):
                        for Attempt in range(50):
                            PageIndex = Rng.choice(InBin)
                            Page = PageList[PageIndex]
                            Plant = MakePlant(Rng, Corpus, Page, View, Pattern, len(Sources[Name]))
                            if Plant:
                                break
                        else:
                            break  # the pattern cannot be placed on these pages
                        Plain, Skips, Dbl, (V, A, B, Rev), Start, Need = Plant
                        Tok = Sources[Name][::-1] if Rev else Sources[Name]
                        Cipher = PlantPage(Plain, Tok[Start:Start + Need], V, A, B, Skips, Dbl, Rng, Page[0])
                        Lo, Hi = max(0, Start - 30), min(len(Tok), Start + Need + 30)
                        Eng = Engine(Tok[Lo:Hi].copy(), W29, W28)
                        Eng.SetCombo(ViewModulus[V], B)
                        Score, End = Eng.Run(PageEvents(Cipher, V, Skip[ViewModulus[V]]), A)
                        Rows.append([V, Pattern, PageIndex, round(Score, 3), len(Skips), f"{BinLo}-{BinHi}"])
        Results["power"][Name] = Rows
        Log(f"power {Name}: {len(Rows)} plants ({time.time() - T:.0f}s)")
        Finish(Unit)

    # 4. null replicates, round-robin so every source gets some before the time runs out
    MaxReps = max(Args.reps, Args.image_reps)
    for Rep in range(1 if Args.quick else MaxReps):
        for Name in Names:
            if Rep >= (Args.image_reps if Name == "lp_images" else Args.reps):
                continue
            Unit = f"null|{Name}|{Rep}"
            if Unit in Done:
                continue
            if (time.time() - Began) / 3600 > Args.hours:
                Log("time budget reached; stopping cleanly (rerun to continue)")
                SaveResults(Results)
                return
            T = time.time()
            Gen = torch.Generator().manual_seed(1000 + Rep)
            Shuffled = Sources[Name][torch.randperm(len(Sources[Name]), generator=Gen).numpy()]
            Eng = Engine(Shuffled, W29, W28)
            Partial = Results.setdefault("null_partial", {}).setdefault(f"{Name}|{Rep}", {})
            for Rev, M, B in Combos:
                Part = f"{Rev}|{M}|{B}"
                if Part in Partial:
                    continue
                Eng.Tok = torch.as_tensor(Shuffled[::-1].copy() if Rev else Shuffled, device=Device)
                Best = [NegInf] * len(PageList)
                for Key, (S, _) in SearchCombo(Eng, PageList, Rev, M, B, Skip).items():
                    Page = int(Key.rsplit("|", 1)[1])
                    Best[Page] = max(Best[Page], S)
                Partial[Part] = [round(S, 3) for S in Best]
                CheckMemory(Results)
                SaveResults(Results)
            del Eng
            Results["null"].setdefault(Name, []).append([max(Col) for Col in zip(*Partial.values())])
            del Results["null_partial"][f"{Name}|{Rep}"]
            Log(f"null {Name} rep {Rep + 1}: {time.time() - T:.0f}s")
            Finish(Unit)
    Results["env"]["finished"] = True
    SaveResults(Results)
    Log("ALL DONE. Upload " + ResultsPath)


if __name__ == "__main__":
    Main()
