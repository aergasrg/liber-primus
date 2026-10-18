"""Cross-check lp.data (relikd + PageLines) against rtkd/iddqd's transcription, which marks pages (%) and
lines (/) explicitly. Run `bash scripts/fetch_data.sh` first (it fetches data/rtkd/transcription.txt).

Reports, per section: rune differences (difflib opcodes), and for the unsolved sections every page or
line boundary that disagrees. Output: results/crosscheck_rtkd.txt (small).
Usage: python3 scripts/crosscheck_rtkd.py
"""
import difflib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.data import DataDir, LoadSection, PageLines, RepoRoot, SolvedCipherNames, UnsolvedNames  # noqa: E402
from lp.gematria import RuneIndex, ToLatin  # noqa: E402

RtkdPath = os.path.join(DataDir, "rtkd", "transcription.txt")
OutPath = os.path.join(RepoRoot, "results", "crosscheck_rtkd.txt")


def ParseRtkd(Path):
    """Return parallel lists Runes, PageNo, LineNo (0-based running counters over the whole file)."""
    with open(Path, encoding="utf-8", errors="replace") as Handle:
        Text = Handle.read()
    Body = Text[Text.index("Page     : %") + len("Page     : %"):]
    Runes, PageNo, LineNo = [], [], []
    Page = Line = 0
    for Char in Body:
        if Char in RuneIndex:
            Runes.append(RuneIndex[Char])
            PageNo.append(Page)
            LineNo.append(Line)
        elif Char == "/":
            Line += 1
        elif Char == "%":
            Page += 1
    return Runes, PageNo, LineNo


def Boundaries(Ids):
    """Rune positions i where a new page/line starts (Ids[i] != Ids[i-1])."""
    return {I for I in range(1, len(Ids)) if Ids[I] != Ids[I - 1]}


def Main():
    Runes, PageNo, LineNo = ParseRtkd(RtkdPath)
    Stream = "".join(chr(65 + R) for R in Runes)
    Out = [f"rtkd: {len(Runes)} runes, {PageNo[-1] + 1} pages, {LineNo[-1] + 1} lines"]
    TotalPageDiff = TotalLineDiff = 0
    for Name in SolvedCipherNames + UnsolvedNames:
        Section = LoadSection(Name)
        Mine = Section["Runes"]
        Key = "".join(chr(65 + R) for R in Mine)
        Start = Stream.find(Key[:40])
        End = Stream.find(Key[-40:], max(Start, 0)) + 40
        Theirs = Runes[Start:End]
        Ops = [Op for Op in difflib.SequenceMatcher(None, Mine, Theirs, autojunk=False).get_opcodes()
               if Op[0] != "equal"]
        Line = f"{Name}: lp {len(Mine)} runes, rtkd {len(Theirs)} at {Start}; rune diffs {len(Ops)}"
        for Tag, I1, I2, J1, J2 in Ops[:10]:
            Line += f"\n    {Tag} lp[{I1}:{I2}]={ToLatin(Mine[I1:I2]) or '-'} rtkd={ToLatin(Theirs[J1 - 0:J2]) or '-'}"
        Out.append(Line)
        if Name not in PageLines or Ops:
            continue
        RtkdPages = PageNo[Start:End]
        RtkdLines = LineNo[Start:End]
        for Label, MineIds, TheirIds in (("page", Section["PageId"], RtkdPages),
                                         ("line", Section["LineId"], RtkdLines)):
            A, B = Boundaries(MineIds), Boundaries(TheirIds)
            OnlyMine, OnlyTheirs = sorted(A - B), sorted(B - A)
            if Label == "page":
                TotalPageDiff += len(OnlyMine) + len(OnlyTheirs)
            else:
                TotalLineDiff += len(OnlyMine) + len(OnlyTheirs)
            Out.append(f"    {Label} breaks: lp {len(A)}, rtkd {len(B)}, only lp {OnlyMine[:12]}, only rtkd {OnlyTheirs[:12]}")
        # runes per page side by side
        Counts = lambda Ids: [sum(1 for X in Ids if X == V) for V in sorted(set(Ids), key=Ids.index)]
        Out.append(f"    runes/page lp {Counts(list(Section['PageId']))}")
        Out.append(f"    runes/page rtkd {Counts(list(RtkdPages))}")
    Out.append(f"TOTAL unsolved boundary disagreements: page {TotalPageDiff}, line {TotalLineDiff}")
    os.makedirs(os.path.dirname(OutPath), exist_ok=True)
    with open(OutPath, "w") as Handle:
        Handle.write("\n".join(Out) + "\n")
    print("\n".join(L for L in Out if "diffs" in L and not L.endswith("diffs 0") or "TOTAL" in L or "only" in L and ("[]" not in L.split("only lp")[1].split("only rtkd")[0] or not L.endswith("[]"))))


if __name__ == "__main__":
    Main()
