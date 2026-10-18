"""Gematria Primus: rune index (0..28), Latin value and prime value.

Ported from seed/seed_scripts/LpCore.py. Variables are PascalCase on purpose.
"""

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


GpPrimes = FirstPrimes(29)  # prime value of rune index i is GpPrimes[i]


def ToLatin(Values):
    return "".join(LatinNames[V] for V in Values)


def ToRunes(Values):
    return "".join(RuneString[V] for V in Values)


def LatinToRunes(Text):
    """Transliterate Latin text into rune indices (greedy, longest match first).

    Q->C, K->C, V->U, Z->S; ING/NG, TH, EO, OE, AE, IA/IO, EA are single runes. Non-letters dropped.
    """
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


def RunesToValues(Text):
    """Rune characters to indices, ignoring everything that is not a rune."""
    return [RuneIndex[Char] for Char in Text if Char in RuneIndex]


# Latin-alphabetical order of the rune names (used by ledger E0018)
AlphaOrder = sorted(range(Alphabet), key=lambda Index: LatinNames[Index])
ToAlpha = {Old: New for New, Old in enumerate(AlphaOrder)}
