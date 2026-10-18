# 07 gpt-6-astra / midpoint-bughunt-columnllr

- id: 20261018T223716-67e21413
- time: 2026-10-18T22:42:54Z
- branch: claude/nifty-ride-hy6cds
- model: gpt-6-astra, mode standard, effort high, max-output 25000
- status: completed
- usage: input_tokens 3079, output_tokens 15394, reasoning_tokens 12948, total_tokens 18473

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

== ENGINE 2: column best-shift LLR scorer (E0030, page-local periodic keys L 2..20) ==
Ledger E0030 (negative): per page, views raw29 (Vigenere on raw runes, F removed and handled by masks),
unit28z1 (chain units, zero step consumes a key symbol), unit28z2 (zero step consumes nothing). Every
subset of <= 11 ciphertext-F skips (cap 4096 masks per page; Drift = cumulative skips before each
segment). Each column scored by English unigram LLR at its best of M shifts; page z pools columns through
a uniform-symbol Monte Carlo (Mu, Var) table; page best = max over views, L, masks. S1 = max over pages of
the page best standardised by that page's surrogate mean/sd. Null: 999 surrogate corpora (non-zero steps
permuted within each page, random start). Threshold 4.17 (0.99 quantile); real S1 3.14, p 0.153.
Power (>= 95/100 recovered): 273-rune page L 3-20; 217 runes L 3-13; 137 runes L 3-5; 76 runes raw L 3.
Plants: LP solved plaintext poured into a real page layout, doublets put at the layout's doublet
positions, skips none / random half of Fs (<= 11) / Welcome's F ordinals.

```python
# --- shared from E0027 ---
def BuildViews(Runes):
    """(Symbols, KeyIndex, Segment) per view; Segment = number of ciphertext Fs before the symbol."""
    C = np.asarray(Runes, dtype=np.int64)
    N = len(C)
    FPos = np.flatnonzero(C == 0)
    Index = np.arange(N)
    Views = {}
    Keep = C != 0
    Views["raw29"] = (C[Keep], Index[Keep], np.searchsorted(FPos, Index[Keep]))
    StepIndex = np.arange(1, N)
    S = (C[1:] - C[:-1]) % 29
    Clean = (C[1:] != 0) & (C[:-1] != 0)
    Segment = np.searchsorted(FPos, StepIndex)
    Views["step29"] = (S[Clean], StepIndex[Clean] - 1, Segment[Clean])
    NonZero = Clean & (S != 0)
    Views["unit28z1"] = ((S[NonZero] - 1) % 28, StepIndex[NonZero] - 1, Segment[NonZero])
    ZerosBefore = np.cumsum(S == 0) - (S == 0)
    Views["unit28z2"] = ((S[NonZero] - 1) % 28, (StepIndex - 1 - ZerosBefore)[NonZero], Segment[NonZero])
    return Views, len(FPos)

def SkipMasks(NumF):
    """(Masks bool [m, NumF], MaxK) with every subset of <= MaxK skips, MaxK <= 11, m <= 4096."""
    if NumF not in MaskCache:
        MaxK = min(MaxSkips, NumF)
        while sum(math.comb(NumF, K) for K in range(MaxK + 1)) > MaskCap:
            MaxK -= 1
        Rows = []
        for K in range(MaxK + 1):
            for Combo in itertools.combinations(range(NumF), K):
                Row = np.zeros(NumF, dtype=bool)
                Row[list(Combo)] = True
                Rows.append(Row)
        Masks = np.array(Rows).reshape(len(Rows), NumF)
        Drift = np.concatenate([np.zeros((len(Rows), 1), dtype=np.int64), np.cumsum(Masks, axis=1)], axis=1)
        MaskCache[NumF] = (Masks, Drift, MaxK)
    return MaskCache[NumF]

def SurrogateLayout(Layout, Seed):
    Rng = np.random.default_rng(Seed)
    Out = []
    for Name, PageList in Layout:
        NewPages = []
        for Number, PageRunes in PageList:
            C = np.asarray(PageRunes)
            Steps = (C[1:] - C[:-1]) % 29
            NonZero = np.flatnonzero(Steps)
            Steps[NonZero] = Rng.permutation(Steps[NonZero])
            Start = int(Rng.integers(29))
            NewPages.append((Number, np.r_[Start, (Start + np.cumsum(Steps)) % 29]))
        Out.append((Name, NewPages))
    return Out
def SkipSet(Plain, SkipType, Rng):
    """Indices of plaintext Fs that pass through without consuming key."""
    FIndex = [I for I, P in enumerate(Plain) if P == 0]
    if SkipType == "welcome":
        return {I for Ordinal, I in enumerate(FIndex, 1) if Ordinal in WelcomeOrdinals}
    if SkipType == "random":
        Chosen = [I for I in FIndex if Rng.random() < 0.5]
        return set(Chosen[:MaxSkips])
    return set()


def PlantPage(Model, LayoutRunes, L, SkipType, Rng, Plain=None):
    """Model: raw | chain-literal-z1 | chain-transparent-z2. Doublets at the layout's doublet positions."""
    N = len(LayoutRunes)
    Plain = PlantText(N, Rng) if Plain is None else Plain[:N]
    Skips = SkipSet(Plain, SkipType, Rng)
    Doublets = {I for I in range(1, N) if LayoutRunes[I] == LayoutRunes[I - 1]}
    Out, KeyPos = [], 0
    if Model == "raw":
        Key = Rng.integers(29, size=L)
        for I, P in enumerate(Plain):
            if I in Skips:
                Out.append(0)
            else:
                Out.append(int((P + Key[KeyPos % L]) % 29))
                KeyPos += 1
        return Out
    Key = Rng.integers(28, size=L)
    State = int(Rng.integers(29))
    for I, P in enumerate(Plain):
        if I in Doublets and Out:
            Out.append(Out[-1])
            State = Out[-1]
            if Model.endswith("z1"):
                KeyPos += 1
        elif I in Skips:
            Out.append(0)
            if "literal" in Model:
                State = 0
        else:
            State = int((State + 1 + (P % 28 + Key[KeyPos % L]) % 28) % 29)
            Out.append(State)
            KeyPos += 1
    return Out

# --- E0030 ---
def LogRatio(Modulus):
    """English log(P / uniform) per symbol, add-one smoothed; mod 28 merges F (0) and EA (28)."""
    Uni, _, Total = EnglishModel()
    Counts = np.array([Uni[R] + 1 for R in range(29)], dtype=float)
    if Modulus == 28:
        Counts = np.r_[Counts[0] + Counts[28], Counts[1:28]]
    return np.log(Counts / Counts.sum() * Modulus)


def ShiftMatrix(Modulus):
    """W[x, k] = LogRatio[(x - k) mod M]: Counts @ W scores every key shift k of a column."""
    Ratio = LogRatio(Modulus)
    X, K = np.meshgrid(np.arange(Modulus), np.arange(Modulus), indexing="ij")
    return Ratio[(X - K) % Modulus]


def NullTable(Modulus, MaxN=160):
    """(Mu, Var) of the best-shift column LLR for n uniform symbols, n = 0..MaxN (Monte Carlo, cached)."""
    if Modulus in Tables:
        return Tables[Modulus]
    Path = os.path.join(CheckpointDir, f"null_table_{Modulus}.json")
    if os.path.exists(Path):
        Data = json.load(open(Path))
        Tables[Modulus] = (np.array(Data["Mu"]), np.array(Data["Var"]))
        return Tables[Modulus]
    Rng = np.random.default_rng(28000 + Modulus)
    W = ShiftMatrix(Modulus)
    Mu, Var = np.zeros(MaxN + 1), np.ones(MaxN + 1)
    for N in range(1, MaxN + 1):
        Counts = Rng.multinomial(N, np.full(Modulus, 1.0 / Modulus), size=NullDraws)
        Best = (Counts @ W).max(axis=1)
        Mu[N], Var[N] = Best.mean(), Best.var(ddof=1)
    os.makedirs(CheckpointDir, exist_ok=True)
    with open(Path + ".part", "w") as Handle:
        json.dump({"Mu": Mu.tolist(), "Var": Var.tolist()}, Handle)
    os.replace(Path + ".part", Path)
    Tables[Modulus] = (Mu, Var)
    return Tables[Modulus]


def ScoreView(Symbols, KeyIndex, Segment, Modulus, L, Drift):
    """Best z over skip masks at period L. Returns (z, mask row, column shifts)."""
    W = ShiftMatrix(Modulus)
    Mu, Var = NullTable(Modulus)
    Groups = Drift.shape[1]
    Counts = np.zeros((Groups, L, Modulus))
    np.add.at(Counts, (Segment, KeyIndex % L, Symbols), 1)
    Offsets = (np.arange(L)[None, :] + np.arange(L)[:, None]) % L
    Rolled = Counts[:, Offsets]  # Rolled[g, d, c] = counts of segment g in key column (c + d) mod L
    RolledScore = (Rolled @ W).astype(np.float32)  # column scores are linear in counts: shift W first
    RolledSize = Rolled.sum(axis=3).astype(np.int64)
    Phase, Inverse = np.unique(Drift % L, axis=0, return_inverse=True)
    Inverse = Inverse.ravel()
    Score = np.zeros((len(Phase), L, Modulus), dtype=np.float32)
    Sizes = np.zeros((len(Phase), L), dtype=np.int64)
    for G in np.flatnonzero(Counts.sum(axis=(1, 2))):
        Score += RolledScore[G, Phase[:, G]]
        Sizes += RolledSize[G, Phase[:, G]]
    Best = Score.max(axis=2).astype(float)
    Z = (Best.sum(axis=1) - Mu[Sizes].sum(axis=1)) / np.sqrt(Var[Sizes].sum(axis=1))
    Index = int(np.argmax(Z))
    Shifts = Score[Index].argmax(axis=1)
    Row = int(np.flatnonzero(Inverse == Index)[0])
    return float(Z[Index]), Row, Shifts


def SearchPage(Runes, Detail=False):
    """Best z over views, L = 2..min(20, n // 3) and every skip mask. Detail adds the decryption."""
    Views, NumF = E27.BuildViews(Runes)
    Masks, Drift, MaxK = E27.SkipMasks(NumF)
    Result = {"Best": -np.inf, "BestAt": None, "MaxK": MaxK, "NumF": NumF}
    Top = min(MaxPeriod, len(Runes) // 3)
    for View in ViewNames:
        Symbols, KeyIndex, Segment = Views[View]
        for L in range(2, Top + 1):
            Z, Row, Shifts = ScoreView(Symbols, KeyIndex, Segment, ViewModulus[View], L, Drift)
            if Z > Result["Best"]:
                Result["Best"], Result["BestAt"] = Z, (View, L, int(Masks[Row].sum()))
                if Detail:
                    Column = (KeyIndex - Drift[Row][Segment]) % L
                    Plain = (Symbols - Shifts[Column]) % ViewModulus[View]
                    Result["Text"] = "".join(ToLatin(Plain[:80].tolist()))
    return Result
```

## Reply

**Assumptions:** the advertised constants are `MaxSkips=11`, `MaskCap=4096`, `MaxPeriod=20`. For plant examples, stub the RNG to return the stated key/start and `SkipSet` to return the stated indices. “Verdict-capable” does **not** mean the supplied evidence establishes that E0030’s result flips.

## Ranked defects

### 1. The advertised ≤11-skip search is not performed
**Location:** `SkipMasks`; coverage claim and plant/search contract.  
**Severity:** verdict-capable; also invalidates advertised power coverage.

- **Input:** `SkipMasks(13)`. A concrete page is `[1,0,2,0,...,13,0,14]`, with the first seven Fs skipped and period 2.
- **Does:** reduces `MaxK` to **6**, because \(\sum_{k=0}^{6}\binom{13}{k}=4096\). No seven-skip mask is tested.
- **Should:** test the claimed seven-skip hypothesis. Here every F separates retained raw symbols, so its phase effect is observable; no ≤6-skip mask has the same period-2 phase vector.
- **Minimal fix:** batch the full ≤11 search rather than cap its total size; otherwise explicitly restrict the claim and controls to each page’s returned `MaxK`. Capping `SkipSet` at 11 does not ensure detectability.

### 2. Float32 scoring against essentially zero null variance can manufacture enormous significance
**Location:** `NullTable`, `ScoreView`.  
**Severity:** verdict/control-number capable.

- **Input:** raw page `[1,2,0,0,0,0]`, `L=2`. Both columns contain one symbol. For a reproducible English-model fixture, use smoothed counts  
  `Counts = [4] + [2]*26 + [1]*2`, and clear caches.
- **Does:** every one-symbol column has exact best score `log(2)`, hence zero theoretical variance. But `RolledScore` rounds that score to float32, slightly **above** float64 `log(2)`. Dividing the resulting positive residual by zero or roundoff-sized `Var[1]` yields infinity or an enormous z.
- **Should:** singleton columns supply no best-shift evidence: their maximum is independent of the observed symbol.
- **Minimal fix:** retain float64 scores; set the exact singleton moments; explicitly give deterministic columns zero centered contribution and handle zero total variance without division.

### 3. Cached null moments can belong to a different scorer
**Location:** `NullTable`.  
**Severity:** conditionally verdict-capable; occurrence in E0030 is unproven.

- **Input:** cache a modulus-29 table with uniform English counts; change `EnglishModel` to the nonuniform fixture above; score `[1,1,1,1,1,1]`, `L=2`.
- **Does:** uses new nonuniform `W` with old `Mu=0`, `Var=0`; produces positive score divided by zero.
- **Should:** load moments for the **current** `W`.
- **Minimal fix:** fingerprint the English counts, smoothing/scoring version and table-generation settings in both memory and disk cache keys. Reject mismatches.

### 4. Cached masks ignore changes to search limits
**Location:** `SkipMasks`.  
**Severity:** conditionally verdict-capable.

- **Input:** clear cache; set `MaxSkips=0`; call `SkipMasks(1)`; set `MaxSkips=11`; call `SkipMasks(1)` again.
- **Does:** still returns only the no-skip mask.
- **Should:** return both masks under the current settings.
- **Minimal fix:** key the cache by `(NumF, MaxSkips, MaskCap)`, or clear it whenever those settings change.

### 5. Empty columns are assigned fictitious variance
**Location:** `NullTable`: `Var = np.ones(...)`.  
**Severity:** changes scores, ranking and power; does not independently invalidate an identically calibrated surrogate p-value.

- **Input:** raw `[1,0,2,0,3,0]`, `L=2`, no-skip mask: column sizes `[3,0]`.
- **Does:** divides by `sqrt(Var[3] + 1)`.
- **Should:** divide by `sqrt(Var[3])`; an empty column’s score is deterministically zero.
- **Minimal fix:** set `Mu[0]=Var[0]=0`, with the zero-total-variance handling from item 2. Rebuild cached tables.

### 6. Raw plants ignore the requested doublet layout
**Location:** `PlantPage`, `"raw"` branch.  
**Severity:** advertised power-model mismatch.

- **Input:** layout `[7,7,8,9,10,11]`, plaintext `[1,2,3,4,5,6]`, key `[0,0]`, no skips.
- **Does:** returns `[1,2,3,4,5,6]`; the layout doublet at index 1 disappears.
- **Should:** satisfy the stated layout-preserving control, or accurately describe the control as unconstrained raw Vigenère.
- **Minimal fix:** correct the power claim, or condition/resample genuine raw plants on the required layout. Blindly overwriting a ciphertext symbol would instead break the raw Vigenère equation.

The measured recovery rate may be correct **for the generated plants**, but it is not the stated layout-preserving raw power.

### 7. A doublet silently overrides an intended F-skip
**Location:** `PlantPage`, ordering of `Doublets` and `Skips`.  
**Severity:** power-model mismatch.

- **Input:** `chain-literal-z1`; layout `[7,7,8,9,10,11]`; plaintext `[1,0,2,3,4,5]`; key `[0,1]`; start 0; skips `{1}`.
- **Does:** returns `[2,2,5,10,15,22]`. Index 1 is not F and **consumes** a key symbol.
- **Should:** under the requested F-skip, return `[2,0,4,8,14,20]`. That conflicts with the requested physical doublet: both constraints cannot hold here.
- **Minimal fix:** reject/resample conflicting controls, or explicitly define and report the changed skip regime. Do not count the requested skip set as the emitted skip set.

### 8. A doublet after a transparent skip resets the hidden chain state
**Location:** `PlantPage`, `State = Out[-1]` in the doublet branch.  
**Severity:** power-model mismatch.

- **Input:** `chain-transparent-z2`; layout `[7,8,8,9,10,11]`; plaintext `[1,0,2,3,4,5]`; key `[0,1]`; start 0; skips `{1}`.
- **Does:** returns `[2,0,0,5,10,17]`. The duplicate F at index 2 resets hidden state from 2 to 0.
- **Should:** if transparent inserted Fs and key-free duplicates leave hidden state unchanged, return `[2,0,0,7,12,19]`.
- **Minimal fix:** remove that state assignment. It is redundant for literal chains but destructive after transparent skips. Alternatively, document that this control deliberately includes hidden-state resets; it is then a different model.

### 9. z2 subtracts the same non-consuming event twice under the actual skip mask
**Location:** `BuildViews`’s `ZerosBefore`, combined with `ScoreView`’s `Drift`.  
**Severity:** wrong skip attribution; **not by itself a demonstrated all-mask false negative**.

- **Input:** ciphertext `[1,2,0,0,3,4]`, transparent skipped positions `{2,3}`. This is generated with plaintext `[0,27,0,0,0,27]`, key `[0,1]`, start 0, and no imposed doublets.
- **Does:** retained transitions at indices 1 and 5 have base indices `[0,3]`; the actual two-skip mask changes these to `[0,1]`.
- **Should:** their effective indices, using the detector’s constant phase convention, are `[0,2]`. The F–F transition was already deducted as a zero step.
- **Important:** selecting **only one** of those Fs gives the correct phase vector. Thus the exhaustive search can recover the signal while reporting the wrong number/identity of skips.
- **Minimal fix:** for transparent z2, remove the candidate skipped Fs before counting genuine zero-step key consumption; derive indices from that effective stream. Each event must be charged once.

### 10. The null table has an unchecked finite size
**Location:** `NullTable`, `ScoreView` indexing `Mu[Sizes]`.  
**Severity:** control/run failure, not a silent explanation for a completed negative.

- **Input:** `[1]*322`, raw view, `L=2`, default fresh table.
- **Does:** requests `Mu[161]` from a table ending at 160: `IndexError`.
- **Should:** score the page or reject it explicitly.
- **Minimal fix:** extend tables to the maximum required column size; validate cached lengths too. Passing a larger `MaxN` currently does not extend an existing cached table.

## Plant–detector coverage mismatches

- **Skip-count mismatch:** plants can request up to 11 random skips, whereas the detector’s actual limit can be much smaller. Welcome skips are not capped by `SkipSet`.
- **Entire chain signals can be discarded around Fs.** For `[1,0,2,0,3,0]`, every transition fails `Clean`; both unit views are empty. Yet this is a valid no-skip, zero-key chain from start 0 with plaintext `[0,27,1,26,2,25]`. The detector neither scores these literal transitions nor reconstructs informative bridges across transparent skips.
- **Forced doublets erase planted plaintext symbols.** Chain controls do not encrypt the supplied `Plain[I]` at doublet positions; they simulate an English stream with imposed erasures/interruptions, not ordinary encryption of the complete supplied text.
- **Random capped skips are position-biased:** `Chosen[:MaxSkips]` retains the earliest successes, not a uniformly chosen capped subset. Power therefore does not describe arbitrary placement of that many skips.
- The detector covers additive periodic shifts with retained English-unigram evidence. It does not cover arbitrary nonrepeating “flat keys”; that is a scope boundary, not a polarity bug.

## Checks that do **not** reveal a bug

- `Rolled[g,d,c] = Counts[g,c+d]` correctly implements effective column `KeyIndex - Drift`.
- Plant `+Key` and detector `Symbols - Shifts` have matching polarity.
- The chain’s apparent one-symbol key offset is a constant cyclic key rotation, harmless when every column shift is free.
- `SurrogateLayout` preserves doublet positions and the nonzero-step multiset without mutating the source. Changing F positions is not inherently erroneous under its exchangeable-step null.
- The ledger’s outer maximum can account for views, periods, masks and pages **if repeated identically for every surrogate**. The aggregate calibration and power-recovery code is absent, so leakage, internal-versus-external standardization, and the reported p-value cannot be verified here.
