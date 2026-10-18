"""Seeded pseudo-random keystreams (never listed in the published ledgers).

Generators reproduced bit-exactly:
  * Perl rand() = drand48 (Perl_drand48 / glibc drand48), int(rand(29)) and int(rand(28))
  * glibc rand() (TYPE_3 additive generator), rand()%29 and rand()%28
  * Python Mersenne Twister, randrange(29) (Py3) and int(random()*29) (Py2) -- separate script part
Each keystream is applied at the start of every unsolved section in four forms:
  raw c-k, raw c+k (mod 29) and chain (step-1)-k, (step-1)+k (mod 28).
Detector: normalised IoC of the first 300 output symbols (random ~1.00 +- 0.03, English ~1.7).
"""
import ctypes
import sys
import time

import numpy as np

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403

Window = 300
SeedCount = 1 << 20
Chunk = 8192
Mask48 = np.uint64((1 << 48) - 1)
A48 = np.uint64(0x5DEECE66D)
C48 = np.uint64(0xB)


def Drand48Ints(Seeds, Length, Modulus):
    State = ((Seeds.astype(np.uint64) & np.uint64(0xFFFFFFFF)) << np.uint64(16)) | np.uint64(0x330E)
    Out = np.empty((len(Seeds), Length), dtype=np.int64)
    for Index in range(Length):
        State = (State * A48 + C48) & Mask48
        Out[:, Index] = ((State * np.uint64(Modulus)) >> np.uint64(48)).astype(np.int64)
    return Out


def GlibcRand(Seeds, Length):
    Seeds = Seeds.astype(np.int64).copy()
    Seeds[Seeds == 0] = 1
    Total = 344 + Length
    R = np.zeros((len(Seeds), 34 + Total), dtype=np.int64)
    R[:, 0] = Seeds
    for I in range(1, 31):
        Hi = R[:, I - 1] // 127773
        Lo = R[:, I - 1] % 127773
        Word = 16807 * Lo - 2836 * Hi
        Word = np.where(Word < 0, Word + 2147483647, Word)
        R[:, I] = Word
    for I in range(31, 34):
        R[:, I] = R[:, I - 31]
    for I in range(34, 34 + Total):
        R[:, I] = (R[:, I - 31] + R[:, I - 3]) & 0xFFFFFFFF
    return R[:, 344:344 + Length] >> 1  # k-th output is r[k + 344] >> 1


def ValidateGenerators():
    import subprocess
    Perl = subprocess.run(["perl", "-e", 'srand(3301); print join(",", map {int(rand(29))} 1..10)'],
                          capture_output=True, text=True).stdout
    Mine = ",".join(str(X) for X in Drand48Ints(np.array([3301]), 10, 29)[0])
    print("drand48 vs perl:", Mine == Perl, Mine)
    Libc = ctypes.CDLL("libc.so.6")
    Libc.srand(1033)
    Reference = [Libc.rand() for _ in range(5)]
    MineRand = list(GlibcRand(np.array([1033]), 5)[0])
    print("glibc rand vs libc:", Reference == MineRand, MineRand)
    return Mine == Perl and Reference == MineRand


def SectionInputs():
    Inputs = []
    for Section in LoadAllUnsolved():
        Raw = np.array(Section["Runes"][:Window], dtype=np.int64)
        StepValues = [S - 1 for S in Steps(Section["Runes"]) if S != 0][:Window]
        Inputs.append((Section["Name"], Raw, np.array(StepValues, dtype=np.int64)))
    return Inputs


def BatchIoc(Values, Modulus):
    Rows, Cols = Values.shape
    Index = (np.arange(Rows)[:, None] * Modulus + Values).ravel()
    Counts = np.bincount(Index, minlength=Rows * Modulus).reshape(Rows, Modulus)
    return Modulus * (Counts * (Counts - 1)).sum(axis=1) / (Cols * (Cols - 1))


def Score(Inputs, Key29, Key28):
    """Return max IoC per row across sections and forms, plus argmax label."""
    Best = np.zeros(Key29.shape[0])
    BestLabel = np.zeros(Key29.shape[0], dtype=np.int64)
    Label = 0
    for Name, Raw, StepValues in Inputs:
        N = len(Raw)
        M = len(StepValues)
        Forms = [((Raw[None, :] - Key29[:, :N]) % 29, 29), ((Raw[None, :] + Key29[:, :N]) % 29, 29),
                 ((StepValues[None, :] - Key28[:, :M]) % 28, 28), ((StepValues[None, :] + Key28[:, :M]) % 28, 28)]
        for Values, Modulus in Forms:
            Ioc29 = BatchIoc(Values, Modulus)
            Better = Ioc29 > Best
            Best = np.where(Better, Ioc29, Best)
            BestLabel = np.where(Better, Label, BestLabel)
            Label += 1
    return Best, BestLabel


def Sweep(Name, Generator, Inputs, Seeds):
    Started = time.time()
    Overall = []
    for Start in range(0, len(Seeds), Chunk):
        Batch = Seeds[Start:Start + Chunk]
        Key29, Key28 = Generator(Batch)
        Best, Labels = Score(Inputs, Key29, Key28)
        Top = np.argsort(Best)[-3:]
        Overall += [(float(Best[T]), int(Batch[T]), int(Labels[T])) for T in Top]
    Overall.sort(reverse=True)
    Print = [(round(S, 3), Seed, Inputs[L // 4][0] + ["/raw-", "/raw+", "/chain-", "/chain+"][L % 4]) for S, Seed, L in Overall[:5]]
    print(f"{Name}: {len(Seeds)} seeds in {time.time() - Started:.0f}s, top: {Print}")
    return Overall


if __name__ == "__main__":
    assert ValidateGenerators()
    Inputs = SectionInputs()

    def PerlGen(Batch):
        return Drand48Ints(Batch, Window, 29), Drand48Ints(Batch, Window, 28)

    def PerlGen29Only(Batch):
        K = Drand48Ints(Batch, Window, 29)
        return K, K % 28

    def GlibcGen(Batch):
        R = GlibcRand(Batch, Window)
        return R % 29, R % 28

    # Positive control: plant a drand48 keystream (seed 777777) into a copy of the first section
    Solved = []
    for SolvedName in ["solved_0_loss_of_divinity", "solved_0_koan_1", "solved_0_welcome"]:
        Solved += LoadSection(SolvedName)["Runes"]
    Plain = np.array(Solved[:Window + 1])
    Key = Drand48Ints(np.array([777777]), Window + 1, 29)[0]
    PlantedRaw = (Plain + Key) % 29
    Key28 = Drand48Ints(np.array([777777]), Window + 1, 28)[0]
    Chain = [5]
    for P, K in zip(Plain, Key28):
        Chain.append((Chain[-1] + 1 + (P % 28 + K) % 28) % 29)
    PlantedChainSteps = np.array([S - 1 for S in Steps(Chain) if S != 0][:Window])
    Noise = np.random.default_rng(29).integers(0, 29, Window)
    NoiseSteps = np.random.default_rng(31).integers(0, 28, Window)
    ControlInputs = [("CTRL-raw", PlantedRaw[:Window], NoiseSteps), ("CTRL-chain", Noise, PlantedChainSteps)]
    Sweep("CONTROL perl drand48 seed 777777 planted", PerlGen, ControlInputs, np.arange(777000, 778000))

    Seeds = np.arange(SeedCount, dtype=np.int64)
    Special = np.array([3301, 1033, 761, 167, 1231507051321 & 0xFFFFFFFF, 0x7A35090F, 0x181F01E5, 1595277641, 845145127,
                        509, 503, 563, 569, 2012, 2013, 2014, 2016, 3258, 33013301, 1033 * 3301, 29, 3301 * 29], dtype=np.int64)
    Sweep("perl int(rand(29))/int(rand(28))", PerlGen, Inputs, Seeds)
    Sweep("perl int(rand(29)) with k%28 for chain", PerlGen29Only, Inputs, Seeds)
    Sweep("glibc rand()%29 / rand()%28", GlibcGen, Inputs, Seeds)
    Sweep("special seeds (perl)", PerlGen, Inputs, Special)
    Sweep("special seeds (glibc)", GlibcGen, Inputs, Special)
