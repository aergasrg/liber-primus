import itertools, math, random, sys
sys.path.insert(0, ".")
from LpCore import *
random.seed(1033)
Pages = []
for Section in LoadAllUnsolved():
    for Page in sorted(set(Section["PageId"])):
        Runes = [V for V, P in zip(Section["Runes"], Section["PageId"]) if P == Page]
        if len(Runes) >= 60:
            Pages.append(Runes)
def CountHigh(PageList, Threshold=3.0):
    High = 0
    for A, B in itertools.combinations(PageList, 2):
        N = min(len(A), len(B))
        Same = sum(1 for X, Y in zip(A, B) if X == Y)
        Z = (Same - N / 29) / math.sqrt(N * (1 / 29) * (28 / 29))
        High += Z > Threshold
    return High
Real = CountHigh(Pages)
Null = []
for _ in range(40):
    Shuffled = [random.sample(P, len(P)) for P in Pages]
    Null.append(CountHigh(Shuffled))
Null.sort()
print("pages >=60 runes:", len(Pages), "| real pairs with z>3:", Real, "| shuffled null: median", Null[len(Null)//2], "95th pct", Null[int(0.95*len(Null))], "max", Null[-1])
