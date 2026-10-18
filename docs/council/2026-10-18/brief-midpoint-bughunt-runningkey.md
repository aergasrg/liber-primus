Context: a lab testing hypotheses about the 9 unsolved Liber Primus sections (12,956 runes in 55 pages,
runes as numbers 0..28 in Gematria Primus order, F = 0, EA = 28). Fingerprint: IoC ~1.00, only 86 doublets
(c_i = c_(i-1)) where ~446 are expected; steps 1..28 flat. Working model: chain c_i = c_(i-1) + s_i, s_i in
1..28 from a flat key; unit u = s - 1 (0..27). Solved pages used Vigenere with keys from LP's own plain text
and "F-skips": some ciphertext F are plaintext F that consume no key symbol.
Python style: PascalCase variables (house rule).

TASK: hunt for concrete BUGS in the code below that could make the recorded NEGATIVE result wrong
(a real signal missed) or make the control/power numbers wrong: alignment, off-by-one, sign or polarity
mismatch between plant and detector, F-skip handling, doublet handling, null construction, leakage between
plants and null, multiple-testing errors. For EACH bug give: location (function), the failing input (small,
concrete: e.g. a 6-rune page and key), what the code does vs what it should do, severity (changes the
verdict / changes power numbers / cosmetic), and the minimal fix. Then list mismatches between what the
plants simulate and what the detector can find (a cipher the model claims to cover that it cannot score).
Do not suggest new experiments beyond what is needed to confirm each bug. Rank by severity. Be terse.

== ENGINE 1: lp/runningkey.py (E0029, skip-tolerant page-local running key) ==
Ledger E0029 (negative): exact DP over source position, any start per page, any F-skip set, English
source as a lattice (TH NG EO OE AE IA IO EA ING as one rune or letters), 4 views x 4 polarities x 2
directions = 32 forms. Score = English unigram log ratio along the path. Sources: LP solved plain
(2,979 runes), LP solved cipher, Self-Reliance, Mabinogion, 3 small byte files tiled. Controls: Koan 2
and Welcome keys hidden mid-Mabinogion found exactly (Gumbel z 49, 61). Power: >= 221 runes 100/100,
141-220 99-100/100, <= 140 50-86/100. Null: 20 word-shuffled sources per source, Gumbel per page with
scale pooled as kappa*sqrt(n); threshold standardised 11.01 (family-wise 0.01, 55 pages x 11 sources).
Real best page per source standardised 2.2-5.0. EnglishModel = unigram counts over a 2.37M-rune English
corpus; plants pour plaintext from that same corpus. Weights(): log((count+1)/Total*M).

```python
Views = ["raw29", "step29", "unit28z1", "unit28z2"]
ViewModulus = {"raw29": 29, "step29": 29, "unit28z1": 28, "unit28z2": 28}
Polarities = [(1, -1), (-1, 1), (1, 1), (-1, -1)]
Sentinel = 29
NegInf = np.float32(-np.inf)
SingleRune = {Name: Index for Index, Name in enumerate(LatinNames) if len(Name) == 1}
Digraphs = {"TH": 2, "NG": 21, "EO": 12, "OE": 22, "AE": 25, "IA": 27, "IO": 27, "EA": 28}


def Weights(Modulus):
    """English unigram log ratio vs uniform; mod 28 merges F and EA (p % 28)."""
    Uni, _, Total = EnglishModel()
    if Modulus == 29:
        return np.array([math.log((Uni[R] + 1) / Total * 29) for R in range(29)])
    Counts = [Uni[R] for R in range(28)]
    Counts[0] += Uni[28]
    return np.array([math.log((C + 1) / Total * 28) for C in Counts])


def NormaliseLatin(Text):
    """Upper-case letters only, with lp.gematria.LatinToRunes's substitutions (QU->CW, Q,K->C, V->U, Z->S)."""
    Text = Text.upper()
    Text = Text.replace("QU", "CW").replace("Q", "C").replace("K", "C").replace("V", "U").replace("Z", "S")
    return "".join(Ch for Ch in Text if Ch in SingleRune)
    def __init__(self, Name, Kind, Chunks, Reversed=False):
        self.Name, self.Kind, self.Chunks, self.Reversed = Name, Kind, Chunks, Reversed
        if Kind == "latin":
            Letters = "".join(Chunks)
            self.Letters = Letters[::-1] if Reversed else Letters
            self.Tok1 = np.array([SingleRune[Ch] for Ch in self.Letters], dtype=np.int8)
            self.Tok2 = np.full(len(self.Letters), Sentinel, dtype=np.int8)
            self.Tok3 = np.full(len(self.Letters), Sentinel, dtype=np.int8)
            Order = (lambda S: S[::-1]) if Reversed else (lambda S: S)
            for J in range(1, len(self.Letters)):
                Pair = Order(self.Letters[J - 1:J + 1])
                if Pair in Digraphs:
                    self.Tok2[J] = Digraphs[Pair]
                if J >= 2 and Order(self.Letters[J - 2:J + 1]) == "ING":
                    self.Tok3[J] = 21
            self.Lattice = True
        else:
            if Kind == "bytes":
                Values = np.asarray(Chunks, dtype=np.uint8).astype(np.int64) % Alphabet
            else:
                Values = np.array([V for Chunk in Chunks for V in Chunk], dtype=np.int64)
            self.Tok1 = (Values[::-1] if Reversed else Values).astype(np.int8)
            self.Tok2 = self.Tok3 = None
            self.Lattice = False
        self.Length = len(self.Tok1)

    def Reverse(self):
        return Source(self.Name, self.Kind, self.Chunks, not self.Reversed)

    def Shuffled(self, Seed):
        """Null source: chunks (words, or bytes) permuted; the lattice inside words is kept."""
        Rng = np.random.default_rng(Seed)
        if self.Kind == "bytes":
            return Source(self.Name + f"#shuf{Seed}", "bytes", Rng.permutation(np.asarray(self.Chunks)), self.Reversed)
        Order = Rng.permutation(len(self.Chunks))
        return Source(self.Name + f"#shuf{Seed}", self.Kind, [self.Chunks[I] for I in Order], self.Reversed)

def PageEvents(Runes, View):
    """Events for one page in one view: list of (CipherIndex, Options). An option is (Atoms, Const),
    Atoms a tuple of keyed symbols (>= 0) or -1 (consume one key symbol, unscored); Const != 0 marks
    an F-skip (option 1 = literal, option 2 = transparent in the step views)."""
    C = list(Runes)
    N = len(C)
    SkipScore = float(Weights(ViewModulus[View])[0])
    if View == "raw29":
        return [(I, [((0,), 0.0), ((), SkipScore)] if V == 0 else [((V,), 0.0)]) for I, V in enumerate(C)]

    def Atom(Step):
        Step %= 29
        if View == "step29":
            return (Step,)
        if Step:
            return ((Step - 1) % 28,)
        return (-1,) if View == "unit28z1" else ()

    Events = []
    I = 1
    while I < N:
        Isolated = C[I] == 0 and C[I - 1] != 0 and (I == N - 1 or C[I + 1] != 0)
        if not Isolated:
            Events.append((I, [(Atom(C[I] - C[I - 1]), 0.0)]))
            I += 1
        elif I == N - 1:
            Events.append((I, [(Atom(C[I] - C[I - 1]), 0.0), ((), SkipScore)]))
            I += 1
        else:
            Keyed = Atom(C[I] - C[I - 1]) + Atom(C[I + 1] - C[I])
            Events.append((I, [(Keyed, 0.0), (Atom(C[I + 1] - C[I]), SkipScore),
                               (Atom(C[I + 1] - C[I - 1]), SkipScore)]))
            I += 2
    return Events


class Tables:
    """Per-source score arrays G[L][x] = Tab[x, Tok_L] for one (modulus, b); polarity a re-indexes x."""

    def __init__(self, Src, Modulus, B):
        W = Weights(Modulus).astype(np.float32)
        Tab = np.full((Modulus + 1, 30), NegInf, dtype=np.float32)
        Tokens = np.arange(29) % Modulus
        for X in range(Modulus):
            Tab[X, :29] = W[(X + B * Tokens) % Modulus]
        Tab[Modulus, :29] = 0.0  # row Modulus = consume unscored
        self.Modulus = Modulus
        Levels = [Src.Tok1] + ([Src.Tok2, Src.Tok3] if Src.Lattice else [])
        self.G = [np.take(Tab, Tok.astype(np.int64), axis=1) for Tok in Levels]

    def Row(self, Level, Atom, A):
        X = self.Modulus if Atom < 0 else (A * Atom) % self.Modulus
        return self.G[Level][X]


def ApplyAtom(V, Tab, Atom, A, Out):
    """One keyed (or unscored) source token: Out[y] = max_L V[y-L] + G_L[y-1]."""
    Out[0] = NegInf
    np.add(V[:-1], Tab.Row(0, Atom, A), out=Out[1:])
    for Level in range(1, len(Tab.G)):
        Shift = Level + 1
        Cand = V[:-Shift] + Tab.Row(Level, Atom, A)[Level:]
        np.maximum(Out[Shift:], Cand, out=Out[Shift:])
    return Out


def RunEvents(Events, Tab, A, V=None):
    """Forward DP over a page; returns the final V (length source + 1)."""
    Length = len(Tab.G[0][0])
    V = np.zeros(Length + 1, dtype=np.float32) if V is None else V
    Spare = np.empty_like(V)
    for _, Options in Events:
        if len(Options) == 1 and len(Options[0][0]) == 1 and not Options[0][1]:
            Spare = ApplyAtom(V, Tab, Options[0][0][0], A, Spare)
            V, Spare = Spare, V
            continue
        Best = None
        for Atoms, Const in Options:
            Cur = V
            for Atom in Atoms:
                Cur = ApplyAtom(Cur, Tab, Atom, A, np.empty_like(V))
            if Const:
                Cur = Cur + np.float32(Const)
            Best = Cur if Best is None else np.maximum(Best, Cur)
        V = Best
    return V


def Combos(ViewList=Views, Directions=(False, True)):
    """Independent work units (Rev, Modulus, B): each builds its tables once."""
    Moduli = sorted({ViewModulus[V] for V in ViewList}, reverse=True)
    return [(Rev, M, B) for Rev in Directions for M in Moduli for B in (-1, 1)]


def SearchCombo(PageRunes, Src, Rev, Modulus, B, ViewList=Views):
    """Best score per (page, view, a, b, rev) for one combo: dict key -> (Score, EndY)."""
    S = Src.Reverse() if Rev != Src.Reversed else Src
    Tab = Tables(S, Modulus, B)
    Out = {}
    for View in [V for V in ViewList if ViewModulus[V] == Modulus]:
        for Page, Runes in enumerate(PageRunes):
            Events = PageEvents(Runes, View)
            for A in (1, -1):
                V = RunEvents(Events, Tab, A)
                End = int(np.argmax(V))
                Out[(Page, View, A, B, Rev)] = (float(V[End]), End)
    return Out


def RandomTokens(Src, Start, Count, Rng, MergeProb=0.5):
    """Key tokens read from Src (forward, as stored) at letter Start, merging each available digraph
    or ING with probability MergeProb. Returns (Tokens, LettersUsed)."""
    Out = []
    J = Start
    while len(Out) < Count:
        if J >= Src.Length:
            raise ValueError("source too short for plant")
        Took = 1
        if Src.Lattice:
            if J + 2 < Src.Length and Src.Tok3[J + 2] != Sentinel and Rng.random() < MergeProb:
                Took = 3
            elif J + 1 < Src.Length and Src.Tok2[J + 1] != Sentinel and Rng.random() < MergeProb:
                Took = 2
        Level = Took - 1
        Out.append(int([Src.Tok1, Src.Tok2, Src.Tok3][Level][J + Level]) if Src.Lattice else int(Src.Tok1[J]))
        J += Took
    return Out, J - Start


def PlantPage(Plain, KeyTokens, View, A, B, SkipAt, Doublets=(), Rng=None, Start=5):
    """Encrypt plaintext runes into a ciphertext page under the engine's model (inverse of the views).

    SkipAt: plaintext indices (plaintext F) emitted as a ciphertext F that consumes no key.
    Doublets (unit28 views): plaintext indices before which the last rune is repeated (z1 consumes a
    key symbol there, z2 does not). Step-view skips pick literal or transparent at random.
    Returns (CipherRunes, KeyUsed).
    """
    Rng = Rng or random.Random(0)
    Key = iter(KeyTokens)
    Used = 0
    if View == "raw29":
        Out = []
        for I, P in enumerate(Plain):
            if I in SkipAt:
                Out.append(0)
                continue
            Out.append((A * (P - B * next(Key))) % 29)  # p = a c + b k  =>  c = a (p - b k)
            Used += 1
        return Out, Used
    Out = [Start]
    State = Start
    for I, P in enumerate(Plain):
        if View != "step29" and I in Doublets:
            Out.append(Out[-1])
            State = Out[-1]
            if View == "unit28z1":
                next(Key)
                Used += 1
        if I in SkipAt:
            Out.append(0)
            if Rng.random() < 0.5:
                State = 0                 # literal: the chain state becomes F
            continue                      # transparent: the state stays at the previous rune
        K = next(Key)
        Used += 1
        if View == "step29":
            Step = (A * (P - B * K)) % 29
        else:
            Step = 1 + (A * (P % 28 - B * K)) % 28
        State = (State + Step) % 29
        Out.append(State)
    return Out, Used
# --- experiment script (E0029) ---
def Thresholds(Name, PageLengths, Alpha, Path=None):
    """Per-page Gumbel threshold at per-page level Alpha from the null replicates.

    Location per page from the replicate mean; scale pooled across pages as Kappa * sqrt(n) (the
    replicate sd of 20 values is too noisy to extrapolate on its own)."""
    Null = np.array(LoadJson(Path or os.path.join(OutDir, f"null_{Name}.json"))["best"])  # reps x pages
    Lengths = np.asarray(PageLengths, dtype=np.float64)
    Sd = Null.std(axis=0, ddof=1)
    Kappa = math.sqrt(np.mean(Sd ** 2 / Lengths))
    Scale = Kappa * np.sqrt(Lengths) * math.sqrt(6) / math.pi
    Location = Null.mean(axis=0) - 0.5772156649 * Scale
    Z = -math.log(-math.log(1 - Alpha))
    Standardised = (Null - Location) / Scale
    return Location + Z * Scale, Location, Scale, Standardised, Null.shape[0]

def MakePlant(Rng, Corpus, Page, View, Pattern, Src):
    """One plant in a real page layout. Returns (CipherRunes, Form, KeyStart, KeyLetters, Skips, KeyTokens)."""
    N = len(Page)
    Dbl = []
    if View.startswith("unit"):
        Dbl = [I for I in range(1, N) if Page[I] == Page[I - 1]]
    PlainLength = N if View == "raw29" else N - 1 - len(Dbl)
    DblPlain = {I - 1 - K for K, I in enumerate(Dbl)}
    for _ in range(200):
        Off = Rng.randrange(len(Corpus) - PlainLength)
        Plain = [int(V) for V in Corpus[Off:Off + PlainLength]]
        Fs = [I for I, P in enumerate(Plain) if P == 0]
        if Pattern == "none":
            Skips = set()
        elif Pattern == "early":
            First = [I for I in Fs if I < 50]
            if not First:
                continue
            Skips = {First[0]} | {I for I in Fs if I > First[0] and Rng.random() < 0.3}
        elif Pattern == "mid":
            First = [I for I in Fs if 80 <= I <= 130]
            if not First:
                continue
            Skips = {First[0]} | {I for I in Fs if I > First[0] and Rng.random() < 0.3}
        else:
            Late = [I for I in Fs if I >= PlainLength - 70]
            if not Late:
                continue
            Skips = {Late[0]} | {I for I in Late[1:] if Rng.random() < 0.5}
        break
    else:
        raise RuntimeError("no plaintext with the required F layout")
    A, B = Rng.choice(Rk.Polarities)
    Rev = Rng.random() < 0.5
    S = Src.Reverse() if Rev else Src
    Need = PlainLength + len(Dbl) + 5
    Start = Rng.randrange(0, S.Length - 3 * Need - 10)
    Key, Letters = Rk.RandomTokens(S, Start, Need, Rng)
    Cipher, _ = Rk.PlantPage(Plain, Key, View, A, B, Skips, DblPlain, Rng, Start=Page[0])
    return Cipher, (View, A, B, Rev), Start, Letters, Skips, Key


LengthEdges = [(0, 140), (141, 220), (221, 999)]
```
