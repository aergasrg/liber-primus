"""Detectors: IoC (raw mod 29, chain mod 28), English unigram/bigram log-likelihood, FFT running-key scan.

Which detector for which form (pitfall): log-likelihood needs letter identities, so it only works
on the raw form. The chain form's step-to-letter mapping is unknown, so use IoC there.
"""
import collections
import functools
import math

import numpy as np

from .data import BaselineWords
from .gematria import Alphabet
from .stats import Ioc


def RawIoc(Values):
    return Ioc(Values, Alphabet)


def ChainIoc(Units):
    return Ioc(Units, 28)


def BatchIoc(Values, Modulus):
    """Row-wise normalised IoC of a 2-D integer array (rows = candidates)."""
    Rows, Cols = Values.shape
    Index = (np.arange(Rows)[:, None] * Modulus + Values).ravel()
    Counts = np.bincount(Index, minlength=Rows * Modulus).reshape(Rows, Modulus)
    return Modulus * (Counts * (Counts - 1)).sum(axis=1) / (Cols * (Cols - 1))


@functools.lru_cache(maxsize=1)
def EnglishModel():
    """Return (UnigramCounts, BigramCounts, Total) from the baseline corpus (words joined end to end)."""
    Uni = collections.Counter()
    Bi = collections.Counter()
    Previous = None
    for Word in BaselineWords():
        for Value in Word:
            Uni[Value] += 1
            if Previous is not None:
                Bi[(Previous, Value)] += 1
            Previous = Value
    return Uni, Bi, sum(Uni.values())


@functools.lru_cache(maxsize=1)
def UnigramLogRatio():
    """log(P_english / P_uniform) per rune, add-one smoothed (seed convention)."""
    Uni, _, Total = EnglishModel()
    return np.array([math.log((Uni[R] + 1) / Total * Alphabet) for R in range(Alphabet)])


def UnigramLlr(Values):
    """Mean log-likelihood ratio per rune vs uniform. English ~ +0.40, uniform random ~ -0.6 to -0.84."""
    Ratio = UnigramLogRatio()
    return float(np.mean(Ratio[np.asarray(Values, dtype=np.int64)]))


def BigramGain(Values):
    """Mean bigram log-likelihood gain over unigram. English ~ +0.5, letters with no sequence ~ 0."""
    Uni, Bi, Total = EnglishModel()
    Pairs = list(zip(Values, Values[1:]))
    return sum(math.log((Bi[(A, B)] + 1) / (Uni[A] + Alphabet)) - math.log((Uni[B] + 1) / Total)
               for A, B in Pairs) / max(1, len(Pairs))


def FftRunningKeyScan(KeyValues, Cipher, Sign=-1, Weights=None):
    """Score Cipher against a running key at every offset in one pass.

    Returns an array Scores[o] = mean_i Weights[(Cipher[i] + Sign * KeyValues[o + i]) % 29], for
    o in 0..len(Key)-len(Cipher). Default Weights = English unigram log ratio. No F-skips.
    """
    KeyValues = np.asarray(KeyValues, dtype=np.int64) % Alphabet
    Cipher = np.asarray(Cipher, dtype=np.int64)
    Weights = UnigramLogRatio() if Weights is None else np.asarray(Weights)
    Length, Window = len(KeyValues), len(Cipher)
    if Length < Window:
        raise ValueError("key shorter than ciphertext window")
    Size = 1 << int(math.ceil(math.log2(Length + Window)))
    Accumulator = np.zeros(Size // 2 + 1, dtype=np.complex128)
    for Symbol in range(Alphabet):
        Indicator = (KeyValues == Symbol).astype(np.float64)
        SymbolWeights = Weights[(Cipher + Sign * Symbol) % Alphabet]
        Accumulator += np.fft.rfft(Indicator, Size) * np.conj(np.fft.rfft(SymbolWeights, Size))
    return np.fft.irfft(Accumulator, Size)[: Length - Window + 1] / Window
