"""B04 preview: Astra's candidate titles as cribs, implied key fragments, exact search in bounded key families."""
import sys, re
import numpy as np
from sympy import primerange, totient
sys.path.insert(0, ".")
from LpCore import *

Pages = "/tmp/LiberPrayground/pages/"
Marks = set("•⁘⁚⁜ \t\n|") 

def RunesOf(Text):
    return [RuneIndex[C] for C in Text if C in RuneIndex]

def TitleCipher(Name):
    Text = open(Pages + Name + ".txt", encoding="utf-8").read()
    if Text.startswith("⁜"):
        Text = Text[1:]
    Head = Text.split("⁜")[0]
    Words = [RunesOf(W) for W in re.split(r"[•\s|]+", Head) if RunesOf(W)]
    return Words

Candidates = {
 "p0-2": "DIVINITY WITHIN|INTERNAL TRUTHS|INFINITE CYCLE|ESOTERIC ORDER|ABSOLUTE LIGHT|ULTIMATE CAUSE|IMMORTAL LIGHT|INFINITE SPACE|PERSONAL CHAOS|OBSCURED SIGNS|ABSOLUTE UNITY|INFINITE ORDER|ULTIMATE LIMIT|NUMINOUS LIGHT|PHYSICAL WORLD",
 "p3-7": "THE TRANSCENDENT ONE|THE UNDISCOVERED KEY|THE UNANSWERABLE WHY|THE INEXTRICABLE WEB|THE UNCONDITIONAL LAW|THE TRANSFIGURED ONE|THE INCALCULABLE SUM|THE INACCESSIBLE WEB|THE UNDECIPHERED MAP|THE UNRESTRICTED WAY|THE INCOMPARABLE ONE|THE INEXPLICABLE END|THE UNQUESTIONED LAW|THE UNRECOGNIZED GOD|TO METAMORPHOSE ALL",
 "p15-22": "PRIME ARRAY|MAGIC TABLE|PRIME ORDER|RUNIC TABLE|MAGIC CROSS|PRIME CYCLE|MAGIC SIGIL|FIRST PRIME|COUNT RUNES|INNER ORDER|RUNIC ORDER|PRIME CROSS|FIRST CAUSE|ORDER CHAOS|INNER LIGHT",
 "p23-26": "THE CIRCLE AND POINT|THE INSTAR HAS ENDED|THE SPIRIT AND FLESH|THE PRIMES ARE SIGNS|THE MASTER AND SLAVE|THE SECRET YOU CARRY|THE MIRROR AND IMAGE|THE DIVINE AND HUMAN|THE SYMBOL AND SIGIL|THE PRIMES AND UNITY|THE CIPHER AND CHAOS|OF PRIMES AND CHAOS|THE RITUAL AND CHANT|THE SECRET YOU GUARD|THE FOREST AND TREES",
 "p27-32": "OUR TRANSCENDENT SELF|ONE UNANSWERABLE KOAN|OUR UNRESTRICTED WILL|ONE UNDECIPHERED WORD|OUR TRANSFIGURED SELF|ALL UNDISCOVERED PATHS|ONE UNCONDITIONAL RULE|ONE TRANSCENDENT MIND|OUR INEXTRICABLE FATE|ONE INACCESSIBLE DOOR|OUR UNDISCOVERED SELF|ONE INEXPLICABLE SIGN|ONE UNQUESTIONED RULE|OUR INCALCULABLE DEBT|ONE INCOMPARABLE SOUL",
 "p33-39": "ON DIVINITY|THE AWAKENED|TO QUESTION|AN ASCENSION|THE INFINITE|ON IDENTITY|AN INQUIRY|THE ABSOLUTE|AN EMANATION|THE DOCTRINE|THE COVENANT|ON INFINITY|OF ILLUSIONS|TO ILLUMINE|THE EMERGENT",
 "p54-55": "A REMINDER|A QUESTION|A DOCTRINE|A COVENANT|A DECEPTION|A DIALECTIC|A PARADIGM|A JUDGMENT|A RESPONSE|A DISCIPLE|A SELECTION|A SENTENCE|A REJECTION|A TALISMAN|A CATALYST",
}

# ---- 1. recount runes with our transliteration ----
Fits = {}
for Name, Text in Candidates.items():
    Pattern = [len(W) for W in TitleCipher(Name)]
    Good = []
    for Title in Text.split("|"):
        Words = [LatinToRunes(W) for W in Title.split()]
        Lens = [len(W) for W in Words]
        if Lens == Pattern:
            Good.append((Title, sum(Words, [])))
        else:
            print(f"   count mismatch {Name}: {Title} -> {Lens} vs {Pattern}")
    Fits[Name] = Good
    print(f"{Name}: pattern {Pattern}, {len(Good)}/15 candidates fit")

# ---- 2. key families as integer arrays mod 29 ----
def Stream(Files):
    Out = []
    for F in Files:
        Out += RunesOf(open(Pages + F + ".txt", encoding="utf-8").read())
    return np.array(Out, dtype=np.int64)
SolvedOrder = ["warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity", "jpg107-167", "jpg229", "p56_an_end", "p57_parable"]
Plain = Stream(["solved_0_warning", "solved_0_welcome", "solved_0_wisdom", "solved_0_koan_1", "solved_0_loss_of_divinity", "solved_jpg107-167", "solved_jpg229", "solved_p56_an_end", "solved_p57_parable"])
CipherSolved = Stream(["0_warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity", "jpg107-167", "jpg229", "p56_an_end", "p57_parable"])
Gp = np.array(GpPrimes)
Primes = np.array(list(primerange(2, 1400000)), dtype=np.int64)[:100400]
Phi = np.array([0] + [int(totient(N)) for N in range(1, 100400)], dtype=np.int64)
PhiPhi = np.array([0] + [int(totient(int(Phi[N]))) if Phi[N] > 0 else 0 for N in range(1, 100400)], dtype=np.int64)
Families = {
    "solved plaintext idx": Plain, "solved plaintext gematria": Gp[Plain] % 29,
    "solved cipher idx": CipherSolved, "solved cipher gematria": Gp[CipherSolved] % 29,
    "primes": Primes % 29, "prime-1": (Primes - 1) % 29, "prime gaps": np.diff(Primes) % 29,
    "phi(n)": Phi % 29, "phi(phi(n))": PhiPhi % 29, "n-phi(n)": (np.arange(len(Phi)) - Phi) % 29,
}
Strided = {}
for FamName, Arr in Families.items():
    MaxStride = 17 if FamName.startswith("solved") else 16
    Strides = [1, 2, 3, 5, 7, 11, 13, 17] if FamName.startswith("solved") else range(1, 17)
    Strided[FamName] = []
    for D in Strides:
        for R in range(D):
            for Dir in (1, -1):
                Seq = Arr[R::D][::Dir]
                Strided[FamName].append(bytes((Seq % 29).astype(np.uint8)))

def Found(Fragment):
    Frag = bytes([F % 29 for F in Fragment])
    return [Fam for Fam, Seqs in Strided.items() if any(Frag in S for S in Seqs)]

# ---- 3. implied key fragments under six forms, exact search ----
Hits, Tested = [], 0
for Name, Good in Fits.items():
    C = sum(TitleCipher(Name), [])
    for Title, P in Good:
        Forms = {
            "raw c-p": [(c - p) % 29 for c, p in zip(C, P)],
            "raw p-c": [(p - c) % 29 for c, p in zip(C, P)],
            "raw c+p": [(c + p) % 29 for c, p in zip(C, P)],
        }
        S = [(C[I] - C[I - 1]) % 29 for I in range(1, len(C))]
        Forms["chain s-p"] = [(s - p) % 29 for s, p in zip(S, P[1:])]
        Forms["chain p-s"] = [(p - s) % 29 for s, p in zip(S, P[1:])]
        Forms["chain s+p"] = [(s + p) % 29 for s, p in zip(S, P[1:])]
        for Form, K in Forms.items():
            Tested += 1
            # also test every key family with prime-index (gematria) of the key fragment's runes
            F = Found(K)
            if F:
                Hits.append((Name, Title, Form, F, K))
print(f"\nTested {Tested} title x form fragments (lengths 8-19) against {len(Families)} families, all strides and directions")
print("exact hits:", Hits if Hits else "none")
# chance-level check: random fragments of the same lengths
Rng = np.random.default_rng(29)
Random = sum(1 for _ in range(300) if Found(list(Rng.integers(0, 29, 9))))
print(f"null: random 9-rune fragments found by chance: {Random}/300")

# ---- 4. periodic-key families (repeated words, phrases, digit keys, square routes): any implied fragment periodic? ----
Periodic = []
for Name, Good in Fits.items():
    C = sum(TitleCipher(Name), [])
    for Title, P in Good:
        S = [(C[I] - C[I - 1]) % 29 for I in range(1, len(C))]
        for Form, K in {"raw c-p": [(c - p) % 29 for c, p in zip(C, P)], "raw p-c": [(p - c) % 29 for c, p in zip(C, P)],
                        "raw c+p": [(c + p) % 29 for c, p in zip(C, P)], "chain s-p": [(s - p) % 29 for s, p in zip(S, P[1:])],
                        "chain p-s": [(p - s) % 29 for s, p in zip(S, P[1:])], "chain s+p": [(s + p) % 29 for s, p in zip(S, P[1:])]}.items():
            for Per in range(1, len(K) - 2):
                if all(K[I] == K[I + Per] for I in range(len(K) - Per)):
                    Periodic.append((Name, Title, Form, Per))
                    break
print("periodic implied keys (period with >=3 checks):", Periodic if Periodic else "none")
