"""Basic statistics: IoC, doublets, steps, chi-square, permutation nulls."""
import collections
import random

from .gematria import Alphabet


def Ioc(Values, Modulus=Alphabet):
    """Normalised index of coincidence (random = 1.0, English in runes ~1.78)."""
    Counts = collections.Counter(Values)
    Total = sum(Counts.values())
    if Total < 2:
        return float("nan")
    return Modulus * sum(N * (N - 1) for N in Counts.values()) / (Total * (Total - 1))


def DoubletCount(Values):
    return sum(1 for A, B in zip(Values, Values[1:]) if A == B)


def Steps(Values, Modulus=Alphabet):
    """c_i - c_(i-1) mod 29."""
    return [(B - A) % Modulus for A, B in zip(Values, Values[1:])]


def StepHistogram(Values, Modulus=Alphabet):
    Counts = collections.Counter(Steps(Values, Modulus))
    return [Counts[S] for S in range(Modulus)]


def ChiSquareUniform(Counts):
    Total = sum(Counts)
    Expected = Total / len(Counts)
    return sum((C - Expected) ** 2 / Expected for C in Counts)


def ChiSquare(Observed, ExpectedShares):
    """Observed: list of counts. ExpectedShares: list of probabilities, same length."""
    Total = sum(Observed)
    return sum((O - Total * P) ** 2 / max(Total * P, 1e-9) for O, P in zip(Observed, ExpectedShares))


def PermutationNull(Statistic, Values, Trials=200, Seed=3301):
    """Distribution of Statistic(shuffled Values). Use instead of normal z for p = 1/29 tails."""
    Rng = random.Random(Seed)
    Work = list(Values)
    Out = []
    for _ in range(Trials):
        Rng.shuffle(Work)
        Out.append(Statistic(Work))
    return sorted(Out)


def Percentile(SortedValues, Fraction):
    Index = min(len(SortedValues) - 1, max(0, int(round(Fraction * (len(SortedValues) - 1)))))
    return SortedValues[Index]
