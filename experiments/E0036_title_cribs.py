"""E0036 (B04): the seven unsolved section titles as word-level cribs against bounded key families and the OEIS.

Reverse crib: every key window of every source decrypts each title under six additive forms; a hit is a
window under which every title word is a common English/LP word (chain forms leave the first decrypted
rune unknown and match it as a wildcard). Ported from outside/CribTest.py and outside/ReverseCrib2.py
(run outside the lab on 2026-10-19) and extended with F-skip variants and the full OEIS.

Usage (from the repo root):
  python3 experiments/E0036_title_cribs.py real      # scan the real titles (checkpoint per title)
  python3 experiments/E0036_title_cribs.py control   # named 'A REMINDER' control + port check
  python3 experiments/E0036_title_cribs.py power  [--plants 100]
  python3 experiments/E0036_title_cribs.py null   [--reps 50]
  python3 experiments/E0036_title_cribs.py report
"""
import argparse, collections, gzip, json, math, os, re, sys, time
from multiprocessing import Pool
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.gematria import Alphabet, GpPrimes, RuneIndex, ToLatin, LatinToRunes
from lp.data import ReadPage, LoadSection, BaselinePath, DataDir, RepoRoot
from lp.keysources import EulerPhi
from lp.detectors import UnigramLogRatio

OutDir = os.path.join(RepoRoot, "results", "E0036")
OeisPath = os.path.join(DataDir, "keyfiles", "oeis", "stripped.gz")
TitleNames = ["p0-2", "p3-7", "p15-22", "p23-26", "p27-32", "p33-39", "p54-55"]
# outside/CribTest.py order of the solved pages (differs from lp.data.SolvedCipherNames)
SolvedOrder = ["0_warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity", "jpg107-167", "jpg229",
               "p56_an_end", "p57_parable"]
OutsideSolvedStrides = [1, 2, 3, 5, 7, 11, 13, 17]
NumberTerms = 100400
OeisTerms = 100
MaxWordLen = 12
ContinueLen = 200
# Form: (sign on cipher value or step, sign on key, chain?)  plaintext = (Sc * X + Sk * K) mod 29
Forms = {"c-k": (1, -1, False), "k-c": (-1, 1, False), "c+k": (1, 1, False),
         "s-k": (1, -1, True), "k-s": (-1, 1, True), "s+k": (1, 1, True)}
Pow = 29 ** np.arange(MaxWordLen + 1, dtype=np.int64)


def RunesOf(Text):
    return [RuneIndex[C] for C in Text if C in RuneIndex]


def TitleWords(Name):
    """Cipher words of the heading (text before the first heading mark), as in outside/CribTest.py."""
    Text = ReadPage(Name)
    if Text.startswith("⁜"):
        Text = Text[1:]
    Head = Text.split("⁜")[0]
    return [RunesOf(W) for W in re.split(r"[•\s|]+", Head) if RunesOf(W)]


def TitleBody(Name, Length):
    """Cipher runes of the section after its title (for the continuation recheck)."""
    Runes = LoadSection(Name)["Runes"]
    Skip = sum(len(W) for W in TitleWords(Name))
    return Runes[Skip:Skip + Length]


# ---------------------------------------------------------------- dictionary

def BuildDictionary():
    """War and Peace words seen 3+ times plus every solved-LP word (frequency +3), as in ReverseCrib2.py."""
    Freq = collections.Counter()
    with open(BaselinePath, encoding="utf-8") as Handle:
        for Line in Handle:
            Word = tuple(RunesOf(Line.strip()))
            if Word:
                Freq[Word] += 1
    Common = {W for W, N in Freq.items() if N >= 3}
    for Name in SolvedOrder:
        for Chunk in re.split(r"[•⁘⁚⁜\s|]+", ReadPage("solved_" + Name)):
            Word = tuple(RunesOf(Chunk))
            if Word:
                Common.add(Word)
                Freq[Word] += 3
    ByLen = collections.defaultdict(list)
    for W in Common:
        if len(W) <= MaxWordLen:
            ByLen[len(W)].append(W)
    return {L: np.array(sorted(Ws), dtype=np.int64) for L, Ws in ByLen.items()}, Freq


Dict, Freq = None, None
TableCache = {}


def EnsureDictionary():
    global Dict, Freq
    if Dict is None:
        Dict, Freq = BuildDictionary()


def Table(WordLen, Unknown, Fixed):
    """Sorted codes (over the non-unknown, non-fixed offsets) of dictionary words consistent with Fixed."""
    Key = (WordLen, Unknown, Fixed)
    if Key not in TableCache:
        Words = Dict.get(WordLen, np.zeros((0, WordLen), dtype=np.int64))
        Ok = np.ones(len(Words), bool)
        for Off, Val in Fixed:
            Ok &= Words[:, Off] == Val
        Free = [O for O in range(WordLen) if O not in Unknown and O not in dict(Fixed)]
        Codes = (Words[Ok][:, Free] * Pow[:len(Free)]).sum(axis=1) if Free else np.zeros(int(Ok.sum()), np.int64)
        Codes = np.unique(Codes)
        # prefix bitmap over the first <= 5 free offsets: a cheap exact prefilter before np.isin
        Bitmap = None
        if Free:
            Prefix = min(5, len(Free))
            Bitmap = np.zeros(29 ** Prefix, bool)
            Bitmap[Codes % 29 ** Prefix] = True
        TableCache[Key] = (Codes, len(Codes) / float(29 ** len(Free)) if Free else float(len(Codes) > 0), Bitmap)
    return TableCache[Key]


# ---------------------------------------------------------------- key sources

def Sieve(Limit):
    Flags = np.ones(Limit, bool)
    Flags[:2] = False
    for P in range(2, int(Limit ** 0.5) + 1):
        if Flags[P]:
            Flags[P * P::P] = False
    return np.nonzero(Flags)[0].astype(np.int64)


def TotientUpTo(Limit):
    Phi = np.arange(Limit, dtype=np.int64)
    for P in Sieve(Limit):
        Phi[P::P] -= Phi[P::P] // P
    return Phi


def BoundedFamilies():
    """The ten bounded families of outside/CribTest.py, as int arrays (not yet reduced)."""
    Plain = np.array(sum((RunesOf(ReadPage("solved_" + N)) for N in SolvedOrder), []), dtype=np.int64)
    Cipher = np.array(sum((RunesOf(ReadPage(N)) for N in SolvedOrder), []), dtype=np.int64)
    Gp = np.array(GpPrimes, dtype=np.int64)
    Primes = Sieve(1400000)[:NumberTerms]
    Phi = TotientUpTo(NumberTerms)
    Phi[0] = 0
    assert all(int(Phi[N]) == EulerPhi(N) for N in (1, 2, 30, 97, 3301, 99991))
    PhiPhi = np.zeros_like(Phi)
    PhiPhi[1:] = Phi[Phi[1:]]
    return {
        "solved plaintext idx": Plain, "solved plaintext gematria": Gp[Plain],
        "solved cipher idx": Cipher, "solved cipher gematria": Gp[Cipher],
        "primes": Primes, "prime-1": Primes - 1, "prime gaps": np.diff(Primes),
        "phi(n)": Phi, "phi(phi(n))": PhiPhi, "n-phi(n)": np.arange(len(Phi)) - Phi,
    }


class KeyStore:
    """All key segments concatenated into one uint8 stream; windows never cross a segment boundary."""

    def __init__(self, Name, Segments):
        self.Name = Name
        self.Labels = [L for L, _ in Segments]
        Lens = np.array([len(S) for _, S in Segments], dtype=np.int64)
        self.SegStart = np.concatenate([[0], np.cumsum(Lens)[:-1]])
        self.SegLen = Lens
        self.Stream = np.concatenate([np.asarray(S, dtype=np.int64) % Alphabet for _, S in Segments]).astype(np.int16)
        self.StartCache = {}

    def Starts(self, Length):
        if Length not in self.StartCache:
            Ok = self.SegLen >= Length
            Counts = self.SegLen[Ok] - Length + 1
            Base = np.repeat(self.SegStart[Ok], Counts)
            Within = np.arange(Counts.sum(), dtype=np.int64) - np.repeat(np.cumsum(Counts) - Counts, Counts)
            if len(self.StartCache) >= 3:
                self.StartCache.clear()
            self.StartCache[Length] = (Base + Within).astype(np.int32)
        return self.StartCache[Length]

    def ValidMask(self, Length):
        Mask = np.zeros(len(self.Stream) - Length + 1, bool)
        Mask[self.Starts(Length)] = True
        return Mask

    def Locate(self, Pos):
        Seg = int(np.searchsorted(self.SegStart, Pos, side="right") - 1)
        return Seg, int(Pos - self.SegStart[Seg])


def BoundedStore():
    Segments = []
    for Fam, Arr in BoundedFamilies().items():
        Solved = Fam.startswith("solved")
        for D in (range(1, 18) if Solved else range(1, 17)):
            for R in range(D):
                for Dir in (1, -1):
                    Segments.append((f"{Fam}|s{D}|r{R}|d{Dir}", Arr[R::D][::Dir]))
    return KeyStore("bounded", Segments)


def OeisStore():
    Segments = []
    with gzip.open(OeisPath, "rt", encoding="ascii", errors="replace") as Handle:
        for Line in Handle:
            if not Line.startswith("A"):
                continue
            ANum, _, Rest = Line.partition(" ")
            Terms = [T for T in Rest.strip().strip(",").split(",") if T][:OeisTerms]
            Values = [int(T) % Alphabet for T in Terms]
            if len(Values) >= 9:
                Segments.append((f"{ANum}|d1", Values))
                Segments.append((f"{ANum}|d-1", Values[::-1]))
    return KeyStore("oeis", Segments)


Stores = {}


def GetStores():
    if not Stores:
        Stores["bounded"] = BoundedStore()
        if os.path.exists(OeisPath):
            Stores["oeis"] = OeisStore()
    return Stores


# ---------------------------------------------------------------- engine

def Variants(Cipher):
    """(skip set, form, chain mode) for every subset of the title's ciphertext Fs."""
    FPos = [J for J, C in enumerate(Cipher) if C == 0]
    for Mask in range(1 << len(FPos)):
        Skip = tuple(FPos[B] for B in range(len(FPos)) if Mask >> B & 1)
        for Form, (_, _, Chain) in Forms.items():
            for Mode in (("bridge", "through") if Chain and Skip else ("-",)):
                yield Skip, Form, Mode


def Plan(Cipher, Skip, Form, Mode):
    """Per position: ('fixed', value) | ('unknown',) | ('key', base, key column). Returns columns, key length.
    A skipped ciphertext F is plaintext F and consumes no key. Chain 'bridge': the chain state ignores a
    skipped F; 'through': the skipped F becomes the previous ciphertext rune."""
    Sc, _, Chain = Forms[Form]
    Cols, KeyIdx, Prev = [], 0, None
    for J, C in enumerate(Cipher):
        if J in Skip:
            Cols.append(("fixed", 0))
            if Mode == "through":
                Prev = C
            continue
        if Chain:
            Cols.append(("unknown",) if Prev is None else ("key", Sc * (C - Prev) % Alphabet, KeyIdx))
            Prev = C
        else:
            Cols.append(("key", Sc * C % Alphabet, KeyIdx))
        KeyIdx += 1
    return Cols, KeyIdx


def WordSpecs(Cols, WordLens):
    Specs, Pos = [], 0
    for WL in WordLens:
        Span = Cols[Pos:Pos + WL]
        Unknown = tuple(O for O, C in enumerate(Span) if C[0] == "unknown")
        Fixed = tuple((O, C[1]) for O, C in enumerate(Span) if C[0] == "fixed")
        Codes, Prob, Bitmap = Table(WL, Unknown, Fixed)
        KeyCols = [(C[1], C[2]) for C in Span if C[0] == "key"]
        Specs.append((Prob, Codes, KeyCols, Bitmap))
        Pos += WL
    return Specs


def ScanTitle(Cipher, WordLens, Store, OnlyVariant=None):
    """Return (hits, expected) where hits = [(skip, form, mode, start)] and expected = uniform-key chance count."""
    Hits, Expected = [], 0.0
    for Skip, Form, Mode in Variants(Cipher):
        if OnlyVariant and (Skip, Form, Mode) != OnlyVariant:
            continue
        _, Sk, _ = Forms[Form]
        Cols, KeyLen = Plan(Cipher, Skip, Form, Mode)
        Specs = sorted(WordSpecs(Cols, WordLens), key=lambda S: S[0])
        Starts = Store.Starts(KeyLen)
        Expected += len(Starts) * math.prod(S[0] for S in Specs)
        Idx = None
        for _, Codes, KeyCols, Bitmap in Specs:
            if not len(Codes):
                Idx = Starts[:0]
                break
            if not KeyCols:
                continue
            if Idx is None:
                # first filter over the whole stream with contiguous slices (no gather), then drop the
                # windows that cross a segment boundary
                Span = len(Store.Stream) - KeyLen + 1
                Code = np.zeros(Span, dtype=np.int32)
                for P, (Base, Col) in enumerate(KeyCols[:5]):
                    Lut = ((Base + Sk * np.arange(Alphabet)) % Alphabet * 29 ** P).astype(np.int32)
                    Code += Lut[Store.Stream[Col:Col + Span]]
                Keep = Bitmap[Code]
                Keep &= Store.ValidMask(KeyLen)
                Idx = np.nonzero(Keep)[0].astype(np.int64)
                Code = Code[Idx].astype(np.int64)
            else:
                Code = np.zeros(len(Idx), dtype=np.int64)
                for P, (Base, Col) in enumerate(KeyCols[:5]):
                    Code += ((Base + Sk * Store.Stream[Idx + Col]) % Alphabet).astype(np.int64) * Pow[P]
                Keep = Bitmap[Code]
                Idx, Code = Idx[Keep], Code[Keep]
            if len(KeyCols) > 5 and len(Idx):
                for P, (Base, Col) in enumerate(KeyCols[5:], 5):
                    Code += ((Base + Sk * Store.Stream[Idx + Col]) % Alphabet).astype(np.int64) * Pow[P]
                Idx = Idx[np.isin(Code, Codes)]
            if not len(Idx):
                break
        if Idx is None:
            Idx = Starts
        Hits += [(Skip, Form, Mode, int(S)) for S in Idx]
    return Hits, Expected


def Decrypt(Cipher, Skip, Form, Mode, Key):
    """Plaintext list (None = unknown) for one key window."""
    Sc, Sk, _ = Forms[Form]
    Cols, _ = Plan(Cipher, Skip, Form, Mode)
    return [C[1] if C[0] == "fixed" else None if C[0] == "unknown" else (C[1] + Sk * int(Key[C[2]])) % Alphabet
            for C in Cols]


def Render(Plain, WordLens):
    Out, Pos = [], 0
    for WL in WordLens:
        Out.append("".join("?" if V is None else ToLatin([V]) for V in Plain[Pos:Pos + WL]))
        Pos += WL
    return " ".join(Out)


def WordScore(Plain, WordLens):
    Score, Pos = 0.0, 0
    for WL in WordLens:
        W = Plain[Pos:Pos + WL]
        Pos += WL
        if None not in W:
            Score += math.log(1 + Freq.get(tuple(W), 0))
    return round(Score, 2)


def Continuation(Name, Cipher, Skip, Form, Mode, Store, Start):
    """Keep reading the key past the title over the section body; z of the unigram LLR vs a uniform plaintext.
    Two body variants: no F-skips, and every body F skipped. Returns (best z, runes used)."""
    Sc, Sk, Chain = Forms[Form]
    Seg, Off = Store.Locate(Start)
    KeyLen = len(Cipher) - len(Skip)
    Rest = Store.Stream[Start + KeyLen:Store.SegStart[Seg] + Store.SegLen[Seg]][:ContinueLen]
    Body = TitleBody(Name, ContinueLen)
    Ratio = UnigramLogRatio()
    Mu, Sd = Ratio.mean(), Ratio.std()
    Best, Used = -99.0, 0
    for SkipBodyF in (False, True):
        Prev = Cipher[-1] if not (Skip and Skip[-1] == len(Cipher) - 1 and Mode == "bridge") else \
            next(C for J, C in reversed(list(enumerate(Cipher))) if J not in Skip)
        Plain, K = [], 0
        for C in Body:
            if SkipBodyF and C == 0:
                Plain.append(0)
                if Mode == "through":
                    Prev = C
                continue
            if K >= len(Rest):
                break
            X = (C - Prev) if Chain else C
            Plain.append((Sc * X + Sk * int(Rest[K])) % Alphabet)
            Prev, K = C, K + 1
        if len(Plain) >= 10:
            Z = (np.mean(Ratio[Plain]) - Mu) / (Sd / math.sqrt(len(Plain)))
            if Z > Best:
                Best, Used = float(Z), len(Plain)
    return round(Best, 2), Used


def Describe(Name, Cipher, WordLens, Store, Hit):
    Skip, Form, Mode, Start = Hit
    Seg, Off = Store.Locate(Start)
    KeyLen = len(Cipher) - len(Skip)
    Plain = Decrypt(Cipher, Skip, Form, Mode, Store.Stream[Start:Start + KeyLen])
    FOrd = [J for J, C in enumerate(Cipher) if C == 0]
    return {"title": Name, "source": Store.Name, "segment": Store.Labels[Seg], "offset": Off,
            "skip": [FOrd.index(J) + 1 for J in Skip], "form": Form, "mode": Mode,
            "plain": Render(Plain, WordLens), "score": WordScore(Plain, WordLens)}


# ---------------------------------------------------------------- jobs

def RealTitles():
    return {N: TitleWords(N) for N in TitleNames}


def JobReal(Name):
    EnsureDictionary()
    Path = os.path.join(OutDir, f"real_{Name}.json")
    if os.path.exists(Path):
        return Name
    Words = RealTitles()[Name]
    Cipher, WordLens = sum(Words, []), [len(W) for W in Words]
    Out = {"title": Name, "cipher": ToLatin(Cipher), "wordlens": WordLens,
           "fpos": [J for J, C in enumerate(Cipher) if C == 0], "sources": {}}
    for SName, Store in GetStores().items():
        Hits, Expected = ScanTitle(Cipher, WordLens, Store)
        Rows = [Describe(Name, Cipher, WordLens, Store, H) for H in Hits]
        for H, R in zip(Hits, Rows):
            R["cont_z"], R["cont_n"] = Continuation(Name, Cipher, H[0], H[1], H[2], Store, H[3])
        Out["sources"][SName] = {"expected_uniform": Expected, "hits": Rows}
    with open(Path + ".tmp", "w") as Handle:
        json.dump(Out, Handle)
    os.replace(Path + ".tmp", Path)
    return Name


def Distinct(Rows):
    return len({(R["title"], R["plain"]) for R in Rows})


def RandomTitle(Words, Rng):
    """Same word lengths and F positions; every other rune uniform over the 28 non-F runes."""
    return [[0 if C == 0 else int(Rng.integers(1, Alphabet)) for C in W] for W in Words]


def JobNull(Args):
    Name, Rep = Args
    EnsureDictionary()
    Words = RealTitles()[Name]
    Rng = np.random.default_rng(1000 * TitleNames.index(Name) + Rep)
    Fake = RandomTitle(Words, Rng)
    Cipher, WordLens = sum(Fake, []), [len(W) for W in Fake]
    Out = {"title": Name, "rep": Rep}
    for SName, Store in GetStores().items():
        Hits, Expected = ScanTitle(Cipher, WordLens, Store)
        Plains = collections.defaultdict(set)
        for H in Hits:
            Plain = Decrypt(Cipher, H[0], H[1], H[2], Store.Stream[H[3]:H[3] + len(Cipher) - len(H[0])])
            Plains["skip" if H[0] else "noskip"].add(Render(Plain, WordLens))
        Out[SName] = {"rows": len(Hits), "distinct": len(Plains["skip"] | Plains["noskip"]),
                      "distinct_noskip": len(Plains["noskip"]), "distinct_skip": len(Plains["skip"]),
                      "expected_uniform": Expected}
    return Out


def SampleWord(Length, Rng, FixedF=()):
    Words = Dict[Length]
    Ok = np.ones(len(Words), bool)
    for O in FixedF:
        Ok &= Words[:, O] == 0
    Pool_ = Words[Ok]
    if not len(Pool_):
        return None
    Weights = np.array([math.log(2 + Freq.get(tuple(W), 0)) for W in Pool_])
    return [int(V) for V in Pool_[Rng.choice(len(Pool_), p=Weights / Weights.sum())]]


def Encrypt(Plain, Skip, Form, Mode, Key, Rng):
    """Inverse of Plan/Decrypt: skipped positions emit ciphertext F; chain starts from a random rune."""
    Sc, Sk, Chain = Forms[Form]
    Cipher, K, Prev = [], 0, None
    for J, P in enumerate(Plain):
        if J in Skip:
            Cipher.append(0)
            if Mode == "through":
                Prev = 0
            continue
        S = Sc * (P - Sk * int(Key[K])) % Alphabet
        if Chain:
            C = int(Rng.integers(0, Alphabet)) if Prev is None else (Prev + S) % Alphabet
            Prev = C
        else:
            C = S
        Cipher.append(C)
        K += 1
    return Cipher


def JobPlant(Index):
    EnsureDictionary()
    Rng = np.random.default_rng(29000 + Index)
    Real = RealTitles()
    Name = TitleNames[Index % len(TitleNames)]
    Words = Real[Name]
    WordLens = [len(W) for W in Words]
    FPos = [J for J, C in enumerate(sum(Words, [])) if C == 0]
    UseSkip = bool(FPos) and Index % 2 == 0
    Skip = tuple(J for J in FPos if Rng.random() < 0.7) if UseSkip else ()
    Skip = Skip or (tuple(FPos[:1]) if UseSkip else ())
    Form = list(Forms)[int(Rng.integers(0, 6))]
    Mode = ("bridge", "through")[int(Rng.integers(0, 2))] if Forms[Form][2] and Skip else "-"
    Plain, Pos = [], 0
    for WL in WordLens:
        W = SampleWord(WL, Rng, tuple(J - Pos for J in Skip if Pos <= J < Pos + WL))
        if W is None:
            return {"index": Index, "title": Name, "status": "no word fits"}
        Plain += W
        Pos += WL
    SName = ("bounded", "oeis")[Index % 4 // 2] if "oeis" in GetStores() else "bounded"
    Store = GetStores()[SName]
    KeyLen = len(Plain) - len(Skip)
    Starts = Store.Starts(KeyLen)
    Start = int(Starts[int(Rng.integers(0, len(Starts)))])
    Cipher = Encrypt(Plain, Skip, Form, Mode, Store.Stream[Start:Start + KeyLen], Rng)
    # a non-skipped position that encrypts to F is fine: the scan enumerates the plant's own Fs
    Hits, _ = ScanTitle(Cipher, WordLens, Store)
    Found = any(H == (Skip, Form, Mode, Start) for H in Hits)
    return {"index": Index, "title": Name, "source": SName, "segment": Store.Labels[Store.Locate(Start)[0]],
            "skip": len(Skip), "form": Form, "mode": Mode, "plain": Render(Plain, WordLens),
            "recovered": Found, "hits": len(Hits)}


def Control():
    """The outside 'A REMINDER' control (primes stride 3, offset 500, c-k) and a port check."""
    EnsureDictionary()
    Store = GetStores()["bounded"]
    Seg = Store.Labels.index("primes|s3|r0|d1")
    Start = int(Store.SegStart[Seg]) + 500
    Plain = LatinToRunes("A") + LatinToRunes("REMINDER")
    Cipher = [(P + int(K)) % Alphabet for P, K in zip(Plain, Store.Stream[Start:Start + 9])]
    Hits, _ = ScanTitle(Cipher, [1, 8], Store)
    Recovered = ((), "c-k", "-", Start) in Hits
    Lines = [f"named control 'A REMINDER' (primes s3 r0 d1 offset 500, c-k): recovered={Recovered}, "
             f"{len(Hits)} hits in total for that ciphertext (all variants, bounded families)"]
    # port check: outside/ReverseCrib2.py = no skips, outside solved strides, bounded families only
    for Name in TitleNames:
        Path = os.path.join(OutDir, f"real_{Name}.json")
        if not os.path.exists(Path):
            continue
        Rows = json.load(open(Path))["sources"]["bounded"]["hits"]
        Port = [R for R in Rows if not R["skip"] and (not R["segment"].startswith("solved")
                or int(R["segment"].split("|")[1][1:]) in OutsideSolvedStrides)]
        Lines.append(f"port check {Name}: {len(Port)} rows (outside run: {89 if Name == 'p15-22' else 0})")
    return Lines, Recovered


def RunPool(Fn, Jobs, Path, Workers):
    Done = set()
    if os.path.exists(Path):
        for Line in open(Path):
            R = json.loads(Line)
            Done.add(json.dumps(R["key"]))
    Todo = [J for J in Jobs if json.dumps(J) not in Done]
    print(f"{len(Done)} done, {len(Todo)} to do", flush=True)
    Started = time.time()
    with Pool(Workers, initializer=GetStores) as P, open(Path, "a") as Handle:
        for N, R in enumerate(P.imap_unordered(Fn, Todo), 1):
            Key = [R["title"], R["rep"]] if "rep" in R else R["index"]
            R["key"] = Key
            Handle.write(json.dumps(R) + "\n")
            Handle.flush()
            if N % max(1, len(Todo) // 50) == 0 or N == len(Todo):
                print(f"{N}/{len(Todo)} after {time.time() - Started:.0f}s", flush=True)


def NullKey(Job):
    return list(Job)


def Report():
    EnsureDictionary()
    Lines, Summary = [], {"titles": {}}
    Null = collections.defaultdict(list)
    NullPath = os.path.join(OutDir, "null.jsonl")
    if os.path.exists(NullPath):
        for Line in open(NullPath):
            R = json.loads(Line)
            Null[R["title"]].append(R)
    Lines.append("E0036 title cribs: distinct all-common-word plaintexts per title "
                 "(null = random titles with the same word lengths and F positions, identical scan)")
    Lines.append(f"{'title':7} {'source':7} {'rows':>6} {'dist':>5} {'noskip':>6} {'skip':>5} "
                 f"{'unif.exp':>9} {'null mean':>9} {'null max':>8} {'p':>6} {'maxcontz':>8}")
    AllRows = []
    for Name in TitleNames:
        Path = os.path.join(OutDir, f"real_{Name}.json")
        if not os.path.exists(Path):
            continue
        Real = json.load(open(Path))
        Summary["titles"][Name] = {"cipher": Real["cipher"], "wordlens": Real["wordlens"], "fpos": Real["fpos"]}
        for SName, S in Real["sources"].items():
            Rows = S["hits"]
            AllRows += Rows
            Dist = Distinct(Rows)
            NoSkip = len({R["plain"] for R in Rows if not R["skip"]})
            WithSkip = len({R["plain"] for R in Rows if R["skip"]})
            NullD = [R[SName]["distinct"] for R in Null[Name] if SName in R]
            Mean = float(np.mean(NullD)) if NullD else float("nan")
            Max = max(NullD) if NullD else -1
            P = (1 + sum(D >= Dist for D in NullD)) / (1 + len(NullD)) if NullD else float("nan")
            ContZ = max([R["cont_z"] for R in Rows], default=float("nan"))
            Lines.append(f"{Name:7} {SName:7} {len(Rows):6d} {Dist:5d} {NoSkip:6d} {WithSkip:5d} "
                         f"{S['expected_uniform']:9.2f} {Mean:9.2f} {Max:8d} {P:6.3f} {ContZ:8.2f}")
            Summary["titles"][Name][SName] = {"rows": len(Rows), "distinct": Dist, "distinct_noskip": NoSkip,
                                              "distinct_skip": WithSkip, "expected_uniform": S["expected_uniform"],
                                              "null_reps": len(NullD), "null_mean": Mean, "null_max": Max,
                                              "p": P, "max_cont_z": ContZ}
    Ctrl, _ = Control()
    Lines += [""] + Ctrl
    PowerPath = os.path.join(OutDir, "power.jsonl")
    if os.path.exists(PowerPath):
        Plants = [json.loads(L) for L in open(PowerPath)]
        Valid = [R for R in Plants if "recovered" in R]
        Rec = sum(R["recovered"] for R in Valid)
        By = collections.Counter((R["source"], "skip" if R["skip"] else "noskip", R["recovered"]) for R in Valid)
        Lines.append(f"power: {Rec}/{len(Valid)} planted keys recovered ({len(Plants) - len(Valid)} plants had no "
                     f"fitting word); by (source, skip, recovered): {dict(sorted(By.items()))}")
        Summary["power"] = {"recovered": Rec, "plants": len(Valid)}
    Top = sorted({(R["title"], R["plain"]): R for R in AllRows}.values(), key=lambda R: (-R["score"], R["title"]))
    Lines += ["", "top distinct hits by word score (title, source, segment, offset, skip, form, mode, plain, score, "
              "continuation z / runes):"]
    for R in Top[:25]:
        Lines.append(f"  {R['title']} {R['source']} {R['segment']} @{R['offset']} skip{R['skip']} {R['form']} "
                     f"{R['mode']} | {R['plain']} | {R['score']} | z {R['cont_z']}/{R['cont_n']}")
    BestZ = sorted(AllRows, key=lambda R: -R["cont_z"])[:5]
    Lines += ["", "highest continuation z (key read on into the section body):"]
    for R in BestZ:
        Lines.append(f"  {R['title']} {R['source']} {R['segment']} @{R['offset']} {R['form']} | {R['plain']} | "
                     f"z {R['cont_z']} over {R['cont_n']} runes")
    Lines.append(f"continuation trials: {len(AllRows)} hit rows x 2 body variants; Bonferroni z for p 0.01: "
                 f"{BonferroniZ(0.01, max(1, 2 * len(AllRows))):.2f}")
    with open(os.path.join(OutDir, "summary.txt"), "w") as Handle:
        Handle.write("\n".join(Lines) + "\n")
    with open(os.path.join(OutDir, "summary.json"), "w") as Handle:
        json.dump(Summary, Handle, indent=1)
    with open(os.path.join(OutDir, "hits.tsv"), "w") as Handle:
        Handle.write("title\tsource\tsegment\toffset\tskip\tform\tmode\tplain\tscore\tcont_z\tcont_n\n")
        for R in sorted(AllRows, key=lambda R: (R["title"], R["source"], -R["score"])):
            Handle.write("\t".join(str(R[K]) for K in ("title", "source", "segment", "offset", "skip", "form",
                                                        "mode", "plain", "score", "cont_z", "cont_n")) + "\n")
    print("\n".join(Lines[:14]))


def BonferroniZ(Alpha, Trials):
    from statistics import NormalDist
    return NormalDist().inv_cdf(1 - Alpha / Trials)


def Main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("job", choices=["real", "control", "power", "null", "report"])
    Parser.add_argument("--reps", type=int, default=50)
    Parser.add_argument("--plants", type=int, default=100)
    Parser.add_argument("--workers", type=int, default=4)
    Args = Parser.parse_args()
    os.makedirs(OutDir, exist_ok=True)
    EnsureDictionary()
    if Args.job == "real":
        with Pool(Args.workers, initializer=GetStores) as P:
            for Name in P.imap_unordered(JobReal, TitleNames):
                print("done", Name, flush=True)
    elif Args.job == "control":
        print("\n".join(Control()[0]))
    elif Args.job == "power":
        RunPool(JobPlant, list(range(Args.plants)), os.path.join(OutDir, "power.jsonl"), Args.workers)
    elif Args.job == "null":
        Jobs = [[N, R] for R in range(Args.reps) for N in TitleNames]
        RunPool(JobNull, Jobs, os.path.join(OutDir, "null.jsonl"), Args.workers)
    else:
        Report()


if __name__ == "__main__":
    Main()
