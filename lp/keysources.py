"""Key sources: integer sequences, bit-exact PRNGs, hash pads, base-29 digits.

PRNGs are validated against the real implementations by ValidateGenerators() (needs perl and libc):
  * Perl rand() = drand48: int(rand(n)) = (state * n) >> 48 after one LCG step; srand(s) seeds
    state = (s << 16) | 0x330E.
  * glibc rand() (TYPE_3 additive feedback): k-th output is r[k + 344] >> 1.
  * Python random (MT19937): Py3 randrange(n), Py2-style int(random() * n).
"""
import ctypes
import hashlib
import math
import random
import subprocess

import numpy as np

from .gematria import FirstPrimes

Mask48 = np.uint64((1 << 48) - 1)
A48 = np.uint64(0x5DEECE66D)
C48 = np.uint64(0xB)

PiDigits = ("31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
            "82148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964"
            "42881097566593344612847564823378678316527120190914564856692346034861045432664821339360726024914127372"
            "45870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330"
            "57270365759591953092186117381932611793105118548074462379962749567351885752724891227938183011949129833"
            "67336244065664308602139494639522473719070217986094370277053921717629317675238467481846766940513200056"
            "81271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199"
            "56112129021960864034418159813629774771309960518707211349999998372978049951059731732816096318595024459"
            "45534690830264252230825334468503526193118817101000313783875288658753320838142061717766914730359825349"
            "04287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989")


def Sequences(Length):
    """Yield (name, list) for the nine sequences used in seed StructureTests (ledger E0017, E0018)."""
    Primes = FirstPrimes(Length)
    Fib = [0, 1]
    while len(Fib) < Length:
        Fib.append(Fib[-1] + Fib[-2])
    yield "primes", Primes
    yield "totient(p)=p-1", [P - 1 for P in Primes]
    yield "naturals", list(range(Length))
    yield "squares", [N * N for N in range(Length)]
    yield "triangular", [N * (N + 1) // 2 for N in range(Length)]
    yield "fibonacci", Fib[:Length]
    yield "pi digits", [int(D) for D in PiDigits[:Length]]
    yield "prime gaps", [B - A for A, B in zip(Primes, Primes[1:])]
    yield "euler phi(n)", [EulerPhi(N) for N in range(1, Length + 1)]


def EulerPhi(N):
    Result = N
    P = 2
    M = N
    while P * P <= M:
        if M % P == 0:
            while M % P == 0:
                M //= P
            Result -= Result // P
        P += 1
    if M > 1:
        Result -= Result // M
    return Result


def Drand48Ints(Seeds, Length, Modulus):
    """Perl int(rand(Modulus)) after srand(seed), vectorised over Seeds. Shape (len(Seeds), Length)."""
    Seeds = np.asarray(Seeds)
    State = ((Seeds.astype(np.uint64) & np.uint64(0xFFFFFFFF)) << np.uint64(16)) | np.uint64(0x330E)
    Out = np.empty((len(Seeds), Length), dtype=np.int64)
    for Index in range(Length):
        State = (State * A48 + C48) & Mask48
        Out[:, Index] = ((State * np.uint64(Modulus)) >> np.uint64(48)).astype(np.int64)
    return Out


def GlibcRand(Seeds, Length):
    """glibc rand() outputs after srand(seed), vectorised over Seeds. Shape (len(Seeds), Length)."""
    Seeds = np.asarray(Seeds).astype(np.int64).copy()
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
    return R[:, 344:344 + Length] >> 1


def PythonMt(Seed, Length, Modulus, Variant="py3"):
    """Python random seeded with Seed: py3 randrange(Modulus) or py2 int(random() * Modulus)."""
    Gen = random.Random(Seed)
    if Variant == "py3":
        return [Gen.randrange(Modulus) for _ in range(Length)]
    return [int(Gen.random() * Modulus) for _ in range(Length)]


def ValidateGenerators():
    """Compare against real perl and libc. Returns dict of name -> bool (None if tool missing)."""
    Result = {}
    try:
        Perl = subprocess.run(["perl", "-e", 'srand(3301); print join(",", map {int(rand(29))} 1..10)'],
                              capture_output=True, text=True, timeout=30).stdout
        Result["drand48"] = Perl == ",".join(str(X) for X in Drand48Ints([3301], 10, 29)[0])
    except (OSError, subprocess.SubprocessError):
        Result["drand48"] = None
    try:
        Libc = ctypes.CDLL("libc.so.6")
        Libc.srand(1033)
        Reference = [Libc.rand() for _ in range(5)]
        Result["glibc"] = Reference == [int(X) for X in GlibcRand([1033], 5)[0]]
    except OSError:
        Result["glibc"] = None
    return Result


HashNames = ["md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512", "blake2b"]


def HashPadBytes(Seed, HashName, Mode, Needed):
    """Mode: chain (digest of digest), hexchain (digest of hex string), counter (H(seed + str(n)))."""
    Out = b""
    Hash = lambda Data: hashlib.new(HashName, Data)  # noqa: E731
    if Mode == "chain":
        Digest = Hash(Seed.encode()).digest()
        while len(Out) < Needed:
            Out += Digest
            Digest = Hash(Digest).digest()
    elif Mode == "hexchain":
        Hex = Hash(Seed.encode()).hexdigest()
        while len(Out) < Needed:
            Out += bytes.fromhex(Hex)
            Hex = Hash(Hex.encode()).hexdigest()
    elif Mode == "counter":
        Counter = 0
        while len(Out) < Needed:
            Out += Hash((Seed + str(Counter)).encode()).digest()
            Counter += 1
    else:
        raise ValueError(Mode)
    return Out[:Needed]


def Base29Digits(Number):
    """Most-significant digit first."""
    Digits = []
    while Number:
        Number, Digit = divmod(Number, 29)
        Digits.append(Digit)
    return Digits[::-1] or [0]


def HashBase29Pad(Seed, HashName, Needed):
    """Base-29 digits of int(digest), chaining digests until Needed digits."""
    Digest = hashlib.new(HashName, Seed.encode()).digest()
    Digits = []
    while len(Digits) < Needed:
        Digits += Base29Digits(int.from_bytes(Digest, "big"))
        Digest = hashlib.new(HashName, Digest).digest()
    return Digits[:Needed]


def ShannonEntropy(Data):
    Counts = np.bincount(np.frombuffer(bytes(Data), dtype=np.uint8), minlength=256)
    P = Counts[Counts > 0] / len(Data)
    return float(-(P * np.log2(P)).sum())


Digits60 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"


def Grid60Bytes():
    """The 8x32 grid of two-character tokens in p40-53, each read as base 60 -> 256 bytes (LEADS)."""
    import re

    from .data import ReadPage, UnsolvedNames
    Tokens = []
    for Name in UnsolvedNames:
        for Line in ReadPage(Name).split("\n"):
            Found = re.findall(r"(?<![0-9A-Za-z])([0-4][0-9A-Za-x])(?![0-9A-Za-z])", Line)
            if len(Found) == 8:
                Tokens += Found
    return bytes(Digits60.index(T[0]) * 60 + Digits60.index(T[1]) for T in Tokens)
