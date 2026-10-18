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


def test_running_key_engine_recovers_koan2():
    # lp.runningkey (B01): Koan 2's key hidden mid-source in filler words must come back with the exact
    # start, the two F-skips (cipher indices 49 and 58) and the exact plaintext.
    import numpy as np
    from lp.data import Words
    from lp.gematria import ToLatin
    from lp.runningkey import LatinSource, PageEvents, RunEvents, Tables, Trace
    Filler = [ToLatin(W) for W in Words(LoadSection("solved_0_loss_of_divinity"))]
    Text = " ".join(Filler[:60] + ["FIRFUMFERENFE"] * 25 + Filler[60:])
    Src = LatinSource("filler+koan2", Text)
    Cipher = LoadSection("jpg107-167")["Runes"]
    V = RunEvents(PageEvents(Cipher, "raw29"), Tables(Src, 29, -1), 1)
    Result = Trace(Cipher, Src, "raw29", 1, -1, int(np.argmax(V)))
    assert Result["StartY"] == len("".join(Src.Chunks[:60]))
    assert [I for I, _ in Result["Skips"]] == [49, 58]
    assert Result["Plain"] == LoadSection("solved_jpg107-167")["Runes"]


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


def test_running_key_f_runs_in_step_views():
    # B24: an F inside an FF run must be able to skip in the step views. Before the fix only isolated
    # Fs could skip, and this plant (two skipped Fs in a row, a 3-token source) scored -inf.
    import random
    import numpy as np
    from lp.runningkey import PageEvents, PlantPage, RunEvents, RuneSource, Tables, Trace, Weights
    Plain = [0, 0, 1, 1, 1]
    Cipher, Used = PlantPage(Plain, [0, 0, 0], "step29", 1, -1, {0, 1}, Rng=random.Random(0), Start=5)
    assert Cipher == [5, 0, 0, 6, 7, 8] and Used == 3
    Src = RuneSource("k", [[0, 0, 0]])
    V = RunEvents(PageEvents(Cipher, "step29"), Tables(Src, 29, -1), 1)
    W = Weights(29)
    assert abs(float(V.max()) - (2 * W[0] + 3 * W[1])) < 1e-4
    Result = Trace(Cipher, Src, "step29", 1, -1, int(np.argmax(V)))
    assert Result["Plain"] == Plain and [I for I, _ in Result["Skips"]] == [1, 2]


def test_running_key_step_views_match_brute_force():
    # Every keyed / literal / transparent assignment of the Fs (runs up to 3) against the DP, on random
    # pages with a short rune source (no lattice): the DP must equal the brute-force optimum exactly.
    import itertools
    import random
    import numpy as np
    from lp.runningkey import PageEvents, RunEvents, RuneSource, Tables, ViewModulus, Weights
    Rng = random.Random(24)
    for Trial in range(60):
        View = ["step29", "unit28z1", "unit28z2"][Trial % 3]
        M = ViewModulus[View]
        W = Weights(M)
        Page = [Rng.choice([0, 0, 0, 3, 7, 7, 12]) for _ in range(9)]
        Key = [Rng.randrange(29) for _ in range(14)]
        Src = RuneSource("k", [Key])
        A, B = Rng.choice([1, -1]), Rng.choice([1, -1])
        Got = float(RunEvents(PageEvents(Page, View), Tables(Src, M, B), A).max())
        Fs = [I for I in range(1, len(Page)) if Page[I] == 0]
        Best = -np.inf
        for Choice in itertools.product("KLT", repeat=len(Fs)):
            Mode = dict(zip(Fs, Choice))
            State, Atoms, Skips = Page[0], [], 0
            for I in range(1, len(Page)):
                if Mode.get(I, "K") == "K":
                    Step = (Page[I] - State) % 29
                    if View == "step29":
                        Atoms.append(Step)
                    elif Step:
                        Atoms.append(Step - 1)
                    elif View == "unit28z1":
                        Atoms.append(-1)
                    State = Page[I]
                else:
                    Skips += 1
                    State = 0 if Mode[I] == "L" else State
            for Start in range(len(Key) - len(Atoms) + 1):
                Score = Skips * W[0] + sum(0.0 if X < 0 else W[(A * X + B * Key[Start + J]) % M]
                                           for J, X in enumerate(Atoms))
                Best = max(Best, Score)
        assert abs(Got - Best) < 1e-3, (Trial, View, Page, Got, Best)


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
