"""Load relikd's transcription keeping word, sentence, line and page positions.

Run scripts/fetch_data.sh first. Format: runes, "•" word break, "⁘" sentence end, "⁚" colon,
"⁜" heading end, blank line = page break (UNRELIABLE, see the lp-data skill), digits and Latin
letters are not runes (digits do end a word).
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


def ReadPage(Name):
    Path = os.path.join(PagesDir, Name + ".txt")
    if not os.path.exists(Path):
        raise FileNotFoundError(f"{Path} missing: run `bash scripts/fetch_data.sh`")
    with open(Path, encoding="utf-8") as Handle:
        return Handle.read()


def LoadSection(Name):
    """Return a dict of parallel lists, one entry per rune.

    Keys: Runes, WordId, PosInWord, SentenceId, PosInSentence, LineId, PosInLine, PageId,
    PosInPage, WordLen, plus Name. PageId counts blank lines and is wrong for some sections.
    """
    Text = ReadPage(Name)
    Section = collections.defaultdict(list)
    WordId = SentenceId = LineId = PageId = 0
    PosInWord = PosInSentence = PosInPage = 0
    WordOpen = False
    for LineText in Text.split("\n"):
        if LineText.strip() == "":
            PageId += 1
            PosInPage = 0
            continue
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
