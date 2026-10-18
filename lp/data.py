"""Load relikd's transcription keeping word, sentence, line and page positions.

Run scripts/fetch_data.sh first. Format: runes, "•" word break, "⁘" sentence end, "⁚" colon,
"⁜" heading end, blank line = page OR paragraph break, digits and Latin letters are not runes
(digits do end a word). Real page breaks of the unsolved sections come from PageLines below.
"""
import collections
import os

from .gematria import RuneIndex

RepoRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DataDir = os.environ.get("LP_DATA_DIR", os.path.join(RepoRoot, "data"))
PagesDir = os.path.join(DataDir, "pages")
TextsDir = os.path.join(DataDir, "texts")
BaselinePath = os.path.join(DataDir, "baseline-rune-words.txt")

UnsolvedNames = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32", "p33-39", "p40-53", "p54-55"]
SolvedCipherNames = ["0_warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity",
                     "p56_an_end", "p57_parable", "jpg107-167", "jpg229"]
SolvedPlainNames = ["solved_" + Name for Name in SolvedCipherNames]
WordBreaks = set("•⁘⁚⁜ \t")
SentenceBreaks = set("⁘⁜")

# Real page layout of the unsolved sections: (first LP page number, lines on each page). A line is a
# non-blank line of relikd's file (= a line on the page image, digit-only lines included). Derived on
# 2026-10-18 by merging blank-line blocks so the line counts match the page images (relikd pages/pN.jpg,
# text bands counted per image; p3, p7, p33, p34, p38, p39 checked by eye). Blank lines inside a page are
# paragraph breaks: p3 = 6+5, p7 = 9+1, p15 = 5+7 (digit square first), p33 = 5+6, p39 = 6+6,
# p49 = 3 rune + 10 digit lines, p50 = 13 digit lines, p51 = 9 digit + 4 rune lines.
PageLines = {
    "p0-2": (0, [12, 12, 9]),
    "p3-7": (3, [11, 12, 12, 10, 10]),
    "p8-14": (8, [12, 12, 12, 12, 12, 12, 7]),
    "p15-22": (15, [12, 12, 12, 12, 12, 12, 12, 6]),
    "p23-26": (23, [10, 12, 12, 12]),
    "p27-32": (27, [11, 12, 12, 12, 12, 6]),
    "p33-39": (33, [11, 12, 12, 11, 11, 11, 12]),
    "p40-53": (40, [11, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 12, 9]),
    "p54-55": (54, [11, 4]),
}


def ReadPage(Name):
    Path = os.path.join(PagesDir, Name + ".txt")
    if not os.path.exists(Path):
        raise FileNotFoundError(f"{Path} missing: run `bash scripts/fetch_data.sh`")
    with open(Path, encoding="utf-8") as Handle:
        return Handle.read()


def LoadSection(Name):
    """Return a dict of parallel lists, one entry per rune.

    Keys: Runes, WordId, PosInWord, SentenceId, PosInSentence, LineId, PosInLine, PageId,
    PosInPage, PageNumber, BlockId, WordLen, plus Name. For sections in PageLines, PageId is the
    real page (0-based within the section) and PageNumber the LP page number; for other sections
    PageId falls back to BlockId (blank-line blocks) and PageNumber is -1.
    """
    Text = ReadPage(Name)
    Layout = PageLines.get(Name)
    if Layout:
        LinePage = [P for P, Count in enumerate(Layout[1]) for _ in range(Count)]
        if sum(1 for L in Text.split("\n") if L.strip()) != len(LinePage):
            raise ValueError(f"{Name}: line count does not match PageLines; transcription changed?")
    Section = collections.defaultdict(list)
    WordId = SentenceId = LineId = BlockId = PageId = 0
    PosInWord = PosInSentence = PosInPage = 0
    WordOpen = False
    for LineText in Text.split("\n"):
        if LineText.strip() == "":
            BlockId += 1
            if not Layout:
                PageId += 1
                PosInPage = 0
            continue
        if Layout and LinePage[LineId] != PageId:
            PageId = LinePage[LineId]
            PosInPage = 0
        PosInLine = 0
        for Char in LineText:
            if Char in RuneIndex:
                if not WordOpen:
                    WordOpen = True
                    PosInWord = 0
                Section["Runes"].append(RuneIndex[Char])
                Section["WordId"].append(WordId)
                Section["PosInWord"].append(PosInWord)
                Section["SentenceId"].append(SentenceId)
                Section["PosInSentence"].append(PosInSentence)
                Section["LineId"].append(LineId)
                Section["PosInLine"].append(PosInLine)
                Section["PageId"].append(PageId)
                Section["PosInPage"].append(PosInPage)
                Section["PageNumber"].append(Layout[0] + PageId if Layout else -1)
                Section["BlockId"].append(BlockId)
                PosInWord += 1
                PosInSentence += 1
                PosInLine += 1
                PosInPage += 1
            elif Char in WordBreaks or Char.isdigit():
                if WordOpen:
                    WordOpen = False
                    WordId += 1
                if Char in SentenceBreaks:
                    SentenceId += 1
                    PosInSentence = 0
        LineId += 1
    if WordOpen:
        WordId += 1
    Lengths = collections.Counter(Section["WordId"])
    Section["WordLen"] = [Lengths[W] for W in Section["WordId"]]
    Section["Name"] = Name
    return dict(Section)


def LoadAllUnsolved():
    return [LoadSection(Name) for Name in UnsolvedNames]


def Pages(Section):
    """List of (PageNumber, runes on that page) in reading order, using Section["PageId"]."""
    Grouped = collections.OrderedDict()
    for Value, PageId, Number in zip(Section["Runes"], Section["PageId"], Section["PageNumber"]):
        Grouped.setdefault((PageId, Number), []).append(Value)
    return [(Number, Runes) for (_, Number), Runes in Grouped.items()]


def Words(Section):
    """List of words (each a list of rune indices) in reading order."""
    Grouped = collections.defaultdict(list)
    for Value, WordId in zip(Section["Runes"], Section["WordId"]):
        Grouped[WordId].append(Value)
    return [Grouped[Key] for Key in sorted(Grouped)]


def SolvedPlaintext(Names=("solved_0_loss_of_divinity", "solved_0_koan_1", "solved_0_welcome")):
    """Concatenated solved plaintext runes; the seed controls used these three sections."""
    Out = []
    for Name in Names:
        Out += LoadSection(Name)["Runes"]
    return Out


def BaselineWords():
    """English corpus (one word per line, in runes) from relikd's repo."""
    Out = []
    with open(BaselinePath, encoding="utf-8") as Handle:
        for Line in Handle:
            Word = [RuneIndex[C] for C in Line.strip() if C in RuneIndex]
            if Word:
                Out.append(Word)
    return Out
