"""Core helpers for Liber Primus analysis (Gematria Primus, loading, statistics).

Variables are PascalCase on purpose.
"""
import collections
import math
import os
import random

RuneString = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LatinNames = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", "X",
              "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IO", "EA"]
RuneIndex = {Rune: Index for Index, Rune in enumerate(RuneString)}
RuneIndex["ᛂ"] = 11  # variant glyph for J used by some transcriptions
Alphabet = 29


def FirstPrimes(Count):
    Found = []
    Candidate = 2
    while len(Found) < Count:
        if all(Candidate % P for P in Found if P * P <= Candidate):
            Found.append(Candidate)
        Candidate += 1
    return Found


GpPrimes = FirstPrimes(29)
PagesDir = "/tmp/LiberPrayground/pages"
UnsolvedNames = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32", "p33-39", "p40-53", "p54-55"]
WordBreaks = set("•⁘⁚⁜ \t")
SentenceBreaks = set("⁘⁜")


def LoadSection(Name):
    """Return a dict of parallel lists describing every rune in a section."""
    Text = open(os.path.join(PagesDir, Name + ".txt"), encoding="utf-8").read()
    Section = collections.defaultdict(list)
    WordId = SentenceId = LineId = PageId = 0
    PosInWord = PosInSentence = PosInLine = PosInPage = 0
    WordOpen = False
    Lines = Text.split("\n")
    for LineText in Lines:
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
    return Section


def Ioc(Values, Modulus=Alphabet):
    """Normalised index of coincidence (random = 1.0)."""
    Counts = collections.Counter(Values)
    Total = sum(Counts.values())
    if Total < 2:
        return float("nan")
    return Modulus * sum(N * (N - 1) for N in Counts.values()) / (Total * (Total - 1))


def DoubletCount(Values):
    return sum(1 for A, B in zip(Values, Values[1:]) if A == B)


def Steps(Values, Modulus=Alphabet):
    return [(B - A) % Modulus for A, B in zip(Values, Values[1:])]


def ToLatin(Values):
    return "".join(LatinNames[V] for V in Values)


def LatinToRunes(Text):
    """Transliterate Latin text into Gematria Primus indices (greedy, longest match first)."""
    Text = Text.upper()
    Text = Text.replace("QU", "CW").replace("Q", "C").replace("K", "C").replace("V", "U").replace("Z", "S")
    Multi = [("ING", 21), ("NG", 21), ("TH", 2), ("EO", 12), ("OE", 22), ("AE", 25), ("IA", 27), ("IO", 27), ("EA", 28)]
    Single = {Name: Index for Index, Name in enumerate(LatinNames) if len(Name) == 1}
    Out = []
    Position = 0
    while Position < len(Text):
        for Key, Index in Multi:
            if Text.startswith(Key, Position):
                Out.append(Index)
                Position += len(Key)
                break
        else:
            Char = Text[Position]
            if Char in Single:
                Out.append(Single[Char])
            Position += 1
    return Out


def LoadAllUnsolved():
    return [LoadSection(Name) for Name in UnsolvedNames]
