# 06 gpt-6-astra / midpoint-bughunt-runningkey

- id: 20261018T223711-976733d6
- time: 2026-10-18T22:41:32Z
- branch: claude/nifty-ride-hy6cds
- model: gpt-6-astra, mode standard, effort high, max-output 25000
- status: completed
- usage: input_tokens 4472, output_tokens 12506, reasoning_tokens 10358, total_tokens 16978

## Prompt

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

## Reply

**Assumptions:** the missing `class Source:` is a transcription omission; “doublets” are zero-step insertions, not instructions to reset a transparently preserved chain state. The null-generation and power-scoring loops are not shown, so their aggregation/leakage cannot be verified.

## Concrete bugs, ranked

### 1. F-skips are supported only for isolated F — **verdict coverage**
**Location:** `PageEvents`.

**Failing input:**
```python
PlantPage(
    Plain=[0, 0, 1, 1, 1], KeyTokens=[0, 0, 0],
    View="step29", A=1, B=-1, SkipAt={0, 1},
    Rng=random.Random(0), Start=5
)
```
Produces `[5, 0, 0, 6, 7, 8]`, consuming three keys: both skips are transparent.

**Actual:** neither F is `Isolated`. The detector requires five keyed atoms, `[24, 0, 6, 1, 1]`. With a three-token source, the generating form scores `-inf`; indeed, none of the other views can fit that source either.

**Expected:** two skipped-F scores plus keyed steps `[1, 1, 1]`.

This also breaks **a single skipped F adjacent to a keyed ciphertext F**, not just consecutive plaintext skips.

**Minimal fix:** handle whole F-runs, preserving literal/transparent chain state and allowing each F to be keyed or skipped. Removing the `Isolated` condition alone is insufficient because the current two-rune grouping would overlap.

---

### 2. Doublet runs collapse, and terminal doublets disappear — **power numbers**
**Location:** `MakePlant`, `PlantPage`.

Two independent failing layouts:

| Real page | Derived data | Actual |
|---|---|---|
| `[5,5,5,6,7,8]` | `Dbl=[1,2]`, `DblPlain={0}`, `PlainLength=3` | Two insertions collapse to one; plant has **5**, not 6 runes. |
| `[5,6,7,8,9,9]` | `Dbl=[5]`, `DblPlain={4}`, `PlainLength=4` | Index 4 is never visited; plant has **5**, not 6 runes. |

**Expected:** preserve multiplicity and permit insertions after the final plaintext rune.

**Minimal fix:** replace the set with insertion counts, e.g. a `Counter`; emit that many repeats at each gap, including gap `len(Plain)`. Merely replacing the set with a list does not fix the membership-based emitter.

---

### 3. An inserted doublet cancels a transparent skip — **power numbers**
**Location:** `PlantPage`, doublet branch: `State = Out[-1]`.

**Failing input:**
```python
Plain=[0, 1]
KeyTokens=[0]
View="unit28z2"
A=1; B=-1
SkipAt={0}; Doublets={1}
Start=5; Rng=random.Random(0)
```

**Actual:** `[5,0,0,2]`. The transparent skip preserves state 5, but the duplicate resets it to 0.

**Expected:** `[5,0,0,7]`: repeating an emitted symbol must not undo the transparent skip’s preserved state.

**Minimal fix:** remove `State = Out[-1]` from the doublet-insertion branch. This does **not** fix the detector’s F-run limitation in bug 1.

---

### 4. Valid plaintext windows are excluded — **power/harness**
**Location:** `MakePlant`, corpus offset selection.

**Failing input:** raw six-rune page; `Corpus=[1]*6`; `Pattern="none"`.

**Actual:** `randrange(0)` raises, although the complete corpus is a valid plaintext window. With seven corpus runes, the final valid offset, 1, is never sampled.

**Expected:** offsets `0 .. len(Corpus)-PlainLength`, inclusive.

**Minimal fix:**
```python
Off = Rng.randrange(len(Corpus) - PlainLength + 1)
```
Reject genuinely shorter corpora explicitly.

---

### 5. Key-start sampling rejects valid sources and strongly truncates positions — **power/harness**
**Location:** `MakePlant`, `Start` selection.

**Failing input:** six-rune raw page, non-lattice source of length 20, sufficiently long corpus.

`Need=11`, hence:
```python
Rng.randrange(0, 20 - 3*11 - 10)
```
raises, although eleven tokens fit at starts 0 through 9, and encryption itself needs at most six.

**Actual:** the three-letters-per-token reserve is imposed even on rune/byte sources; an unexplained ten-symbol margin and exclusive endpoint remove further valid starts.

**Expected:** sample starts supporting the required key tokens.

**Minimal fix:** for non-lattices use `Rng.randrange(S.Length - Need + 1)`. For lattices, validate token availability rather than treating a worst-case reserve as a necessary condition.

For long sources this is a **sampling restriction**, not a detector failure; reported power does not cover all valid start positions.

---

### 6. Reversal metadata disagrees with the detector for already-reversed sources — **form-specific controls/power**
**Location:** `MakePlant` versus `SearchCombo`.

**Failing input:** `Src.Reversed=True`, underlying rune chunks `[1,2,3]*20`, sampled `Rev=False`, `Start=0`.

**Actual:** `MakePlant` plants `[3,2,1,...]` and labels it `Rev=False`; `SearchCombo(..., Rev=False)` searches `[1,2,3,...]`.

**Expected:** the reported form selects the source actually planted.

**Minimal fix:**
```python
S = Src.Reverse() if Rev != Src.Reversed else Src
```
Unchanged for ordinary forward sources. Searching both directions still covers the plant; checking only the reported generating form does not.

---

### 7. Degenerate shuffled nulls produce invalid standardised scores — **calibration**
**Location:** `Thresholds`.

**Failing input:** twenty null replicates, one page, all scores equal to 1; page length 6. This occurs, for example, when every shuffle leaves the source unchanged.

**Actual:** `Kappa=Scale=0`; standardised null scores are `0/0 = NaN`. The function nevertheless returns a purported threshold.

**Expected:** explicitly report that this null cannot provide a fitted Gumbel scale.

**Minimal fix:** reject nonpositive/nonfinite pooled scale and nonfinite null scores. Do not manufacture a positive scale merely to continue.

---

### 8. Add-one probabilities are not normalised — **cosmetic at the stated corpus size**
**Location:** `Weights`.

**Failing input:** 29 rune counts all equal to 1, `Total=29`.

**Actual:** every mod-29 weight is `log(2)`, although this is a uniform model.

**Expected:** every weight is zero.

**Minimal fix:** denominator `Total + Modulus`, assuming `Total == sum(Uni)`.

At 2.37M runes the error is only about \(1.2\times10^{-5}\) per scored rune. Variable scoring lengths mean it is not universally an irrelevant constant, but it cannot plausibly explain the reported large z-gap.

## Null-construction issue: conditional, not an established implementation error

**Location:** `Source.Shuffled`, bytes branch.

Shuffling **after tiling** destroys the tiled source’s repetition and changes its effective search multiplicity.

**Concrete example:** source `[0,1,0,1,0,1]`; a shuffle can yield `[0,0,0,1,1,1]`. For raw ciphertext `[18,18,18]`, `A=1, B=-1`, and \(W[18]>W[17]\):

- original source best: `2*W[18] + W[17]`;
- that shuffled source best: `3*W[18]`.

Thus the shuffle changes the search baseline, not merely the ordering of an otherwise equivalent tiled key.

**Severity:** potentially calibration/verdict; it can make the null harder than the real fixed-source search. **Fix if the intended null preserves tiled-file structure:** shuffle the base file, then tile it identically. If arbitrary byte permutations are intentionally the null, the code implements that null—but its claimed fixed-source FWER needs separate justification.

## Coverage and accounting mismatches

- **Actual advertised-model gap:** plants can generate F-runs that the purported “any F-skip set” detector cannot score.
- **Plant-layout gap:** repeated/terminal doublets are not faithfully planted; transparent-skip/doublet interactions change the cipher itself.
- **Mixed doublet policies are unsupported:** one page cannot mix key-consuming and non-consuming doublets. Example: `[5,6,6,7,7,8]`, with the first duplicate consuming a key and the second not. Neither uniform z1 nor uniform z2 implements that schedule. This is an additional limitation, **not** a contradiction if the claim is strictly the listed 32 forms.
- `MakePlant` returns `Letters` for **all reserved tokens**, not tokens actually consumed. For a six-rune raw plant without skips it generates eleven tokens but uses six. This is not wrong as reservation metadata; using it as the true endpoint would corrupt “exact recovery” accounting. Return the consumed-prefix letter span if that is what controls compare.

**Not demonstrated as bugs:** polarity inversion is consistent; reversed lattices are consistent. If null `"best"` already maximises over the same 32 forms, the 605-comparison correction and threshold ≈11.01 need **no additional factor of 32**. Twenty replicates plus an assumed Gumbel tail do not themselves establish FWER 0.01. Shared English training/plant corpus makes power in-corpus; the shown code does not establish plant-to-null leakage.
