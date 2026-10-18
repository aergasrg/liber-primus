"""Positive controls: plant a known key into known plaintext, then recover it through the SAME pipeline.

Pattern for every experiment:
    Plain = ControlPlaintext(Length)
    Cipher = PlantRaw(Plain, Key)            # or PlantChain(Plain, Key28)
    ControlScore = Pipeline(Cipher)           # identical code path as the real run
    assert ControlScore clearly above the null ceiling, else the experiment is not informative.
"""
import random

from .ciphers import ApplyKeyStream, ChainEncrypt
from .data import BaselineWords, SolvedPlaintext


def ControlPlaintext(Length, Source="solved", Seed=3301):
    """Known English plaintext in runes. 'solved' = LP's own solved pages, 'baseline' = English corpus."""
    if Source == "solved":
        Plain = SolvedPlaintext()
        if Length > len(Plain):
            raise ValueError(f"only {len(Plain)} solved runes; use Source='baseline'")
        return Plain[:Length]
    Rng = random.Random(Seed)
    Words = BaselineWords()
    Index = Rng.randrange(len(Words) - 50000)
    Out = []
    while len(Out) < Length:
        Out += Words[Index]
        Index += 1
    return Out[:Length]


def PlantRaw(Plain, Key, Sign=1, FSkipEvery=0, Seed=29):
    """Raw-form plant: c = p + Sign*k (mod 29).

    FSkipEvery > 0 inserts realistic F-skips: roughly one plaintext F in FSkipEvery is left as a
    ciphertext F that does not consume key (the solved-page convention). Returns (Cipher, SkipIndices).
    """
    Rng = random.Random(Seed)
    Skips = set()
    if FSkipEvery:
        Skips = {I for I, V in enumerate(Plain) if V == 0 and Rng.randrange(FSkipEvery) == 0}
    Cipher = ApplyKeyStream(Plain, Key, Sign, PassThrough=Skips)
    return Cipher, Skips


def PlantChain(Plain, Key28, Start=5):
    """Chain-form plant (no doublets). Returns len(Plain) + 1 runes."""
    return ChainEncrypt(Plain, Key28, Start)


def Shuffled(Values, Seed=1):
    """Noise ceiling helper: same symbols, order destroyed."""
    Out = list(Values)
    random.Random(Seed).shuffle(Out)
    return Out
