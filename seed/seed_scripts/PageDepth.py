"""Are any two pages encrypted 'in depth' (same keystream from the top of the page)?

For every pair of unsolved pages, count positions where the runes agree when both pages are
aligned at their first rune, and compare with the 1/29 chance rate. Also scan every relative
shift for the strongest pair to see whether shift 0 is special.
"""
import itertools
import math
import sys

sys.path.insert(0, "/tmp/claude-0/-home-claude/cdb599b0-10b3-556e-8f0c-243658092bba/scratchpad")
from LpCore import *  # noqa: E402,F401,F403

Pages = []  # (label, runes)
PageOffset = 0
for Section in LoadAllUnsolved():
    PagesInSection = sorted(set(Section["PageId"]))
    First = int(Section["Name"][1:].split("-")[0])
    for Page in PagesInSection:
        Runes = [V for V, P in zip(Section["Runes"], Section["PageId"]) if P == Page]
        Pages.append((f"p{First + Page}", Runes))
print("pages:", len(Pages), "sizes:", [len(R) for _, R in Pages])


def Agreement(A, B, Shift=0):
    if Shift >= 0:
        Pairs = list(zip(A[Shift:], B))
    else:
        Pairs = list(zip(A, B[-Shift:]))
    Same = sum(1 for X, Y in Pairs if X == Y)
    N = len(Pairs)
    Expected = N / 29
    Sd = math.sqrt(N * (1 / 29) * (28 / 29)) if N else 1
    return Same, N, (Same - Expected) / Sd


Results = []
for (NameA, A), (NameB, B) in itertools.combinations(Pages, 2):
    Same, N, Z = Agreement(A, B)
    Results.append((Z, NameA, NameB, Same, N))
Results.sort(reverse=True)
print("\nTop page pairs aligned at their first rune (z vs 1/29):")
for Z, NameA, NameB, Same, N in Results[:8]:
    print(f"  {NameA}-{NameB}: {Same}/{N} agree, z {Z:.2f}")
Zs = [R[0] for R in Results]
print(f"pairs tested: {len(Zs)}, mean z {sum(Zs) / len(Zs):.3f}, count z>3: {sum(1 for Z in Zs if Z > 3)} (expected by chance ~{len(Zs) * 0.00135:.1f})")

# Shift scan for p54 vs p55
Lookup = dict(Pages)
A, B = Lookup["p54"], Lookup["p55"]
ShiftZ = [(Agreement(A, B, S)[2], S) for S in range(-len(B) + 40, len(A) - 40)]
ShiftZ.sort(reverse=True)
print("\np54 vs p55, best relative shifts:", [(S, round(Z, 2)) for Z, S in ShiftZ[:6]])
Rank = [S for Z, S in ShiftZ].index(0) + 1
print(f"shift 0 rank: {Rank} of {len(ShiftZ)}")
