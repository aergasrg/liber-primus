"""The gate: must pass before any experiment. Run `python3 -m pytest -q tests/` (or `python3 tests/test_gate.py`).

Checks that the loader, gematria and cipher conventions reproduce known solved pages and the
published unsolved fingerprint exactly. If any of these fail, no experiment result is meaningful.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lp.ciphers import ApplyKeyStream, Atbash, ChainEncrypt, ChainUnits, FSkipPositions, Shift, TotientStream, Vigenere  # noqa: E402
from lp.data import LoadAllUnsolved, LoadSection, Pages  # noqa: E402
from lp.keysources import ValidateGenerators  # noqa: E402
from lp.stats import DoubletCount, StepHistogram  # noqa: E402

WelcomeFSkips = [4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25]
ExpectedSections = {"p0-2": (729, 4), "p3-7": (1145, 6), "p8-14": (1729, 9), "p15-22": (1903, 10),
                    "p23-26": (1021, 11), "p27-32": (1433, 13), "p33-39": (1680, 12), "p40-53": (3008, 18),
                    "p54-55": (308, 3)}
ExpectedSteps = [86, 459, 504, 440, 438, 446, 430, 470, 426, 510, 497, 454, 449, 503, 474, 469, 448, 404, 433,
                 474, 467, 462, 421, 486, 467, 467, 457, 475, 431]


def test_welcome_divinity_with_f_skips():
    Cipher = LoadSection("0_welcome")["Runes"]
    Plain = LoadSection("solved_0_welcome")["Runes"]
    assert Vigenere(Cipher, "DIVINITY", FSkips=WelcomeFSkips) == Plain


def test_koan2_firfumferenfe_with_two_f_skips():
    # Koan 2 (relikd jpg107-167): Vigenere FIRFUMFERENFE; the 2nd and 3rd of its 5 ciphertext Fs pass
    # through (the only subset of <= 3 skips that reproduces the plaintext). B01's real-world control.
    Cipher = LoadSection("jpg107-167")["Runes"]
    assert Vigenere(Cipher, "FIRFUMFERENFE", FSkips=[2, 3]) == LoadSection("solved_jpg107-167")["Runes"]


def test_koan1_atbash_plus_3():
    Cipher = LoadSection("0_koan_1")["Runes"]
    assert Shift(Atbash(Cipher), 3) == LoadSection("solved_0_koan_1")["Runes"]


def test_warning_atbash():
    assert Atbash(LoadSection("0_warning")["Runes"]) == LoadSection("solved_0_warning")["Runes"]


def test_an_end_totient_with_one_f_skip():
    Cipher = LoadSection("p56_an_end")["Runes"]
    Plain = ApplyKeyStream(Cipher, TotientStream(len(Cipher)), -1, PassThrough=FSkipPositions(Cipher, [4]))
    assert Plain == LoadSection("solved_p56_an_end")["Runes"]


def test_unsolved_fingerprint():
    Sections = LoadAllUnsolved()
    Got = {S["Name"]: (len(S["Runes"]), DoubletCount(S["Runes"])) for S in Sections}
    assert Got == ExpectedSections
    assert sum(R for R, _ in Got.values()) == 12956
    assert sum(D for _, D in Got.values()) == 86
    assert sum(len(set(S["WordId"])) for S in Sections) == 2896  # see docs/STATE.md on 2,921
    Steps = [0] * 29
    for S in Sections:
        Steps = [A + B for A, B in zip(Steps, StepHistogram(S["Runes"]))]
    assert Steps == ExpectedSteps


def test_page_map():
    # Runes per LP page from lp.data.PageLines (page images, 2026-10-18); page 50 holds digits only.
    Got = {Number: len(Runes) for S in LoadAllUnsolved() for Number, Runes in Pages(S)}
    assert sorted(Got) == [N for N in range(56) if N != 50]
    assert [Got[N] for N in (0, 3, 7, 15, 33, 39, 49, 51, 53, 55)] == [262, 217, 208, 159, 214, 240, 66, 92, 179, 76]
    assert sum(Got.values()) == 12956


def test_chain_roundtrip():
    Plain = LoadSection("solved_0_welcome")["Runes"][:200]
    Key = [(7 * I + 3) % 28 for I in range(200)]
    Cipher = ChainEncrypt(Plain, Key)
    Units, _ = ChainUnits(Cipher)
    assert DoubletCount(Cipher) == 0
    assert [(U - K) % 28 for U, K in zip(Units, Key)] == [P % 28 for P in Plain]


def test_prngs_bit_exact():
    Result = ValidateGenerators()
    assert Result["drand48"] in (True, None)
    assert Result["glibc"] in (True, None)


if __name__ == "__main__":
    Failed = 0
    for Name, Fn in list(globals().items()):
        if Name.startswith("test_"):
            try:
                Fn()
                print("PASS", Name)
            except AssertionError:
                Failed += 1
                print("FAIL", Name)
    sys.exit(1 if Failed else 0)
