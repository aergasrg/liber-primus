"""Skip-tolerant, tokenisation-tolerant running-key search (B01).

Model: one LP page is enciphered with a running key read from a source, starting anywhere in it.
Every ciphertext F may be a pass-through F-skip: it is the plaintext F and consumes no key symbol.
English sources are a lattice: each TH, NG, EO, OE, AE, IA, IO, EA (and ING) may be one rune or its
letters, chosen per occurrence. The search is an exact dynamic program over the source position,
vectorised over every start offset at once:

    V[y] = best score of a path whose next unread source letter is y.
    keyed symbol x: V'[y] = max over token lengths L in {1,2,3} of V[y-L] + Tab[x, Tok_L[y-1]]
    ciphertext F:  V' = max(keyed-F update, V + W[F])          (the skip consumes nothing)

The page score is max_y V at the end of the page (any start, any skip set, any tokenisation).
Cost is (events x source letters) per form; there is no skip-count dimension.

Views (the symbol stream the key is applied to; page-local, first rune of a page dropped for steps):
  raw29     p = a c + b k (mod 29), scored with the English unigram log ratio
  step29    p = a s + b k (mod 29), s_i = c_i - c_(i-1); zero steps are ordinary symbols
  unit28z1  p%28 = a u + b k (mod 28), u = s - 1 over non-zero steps; a zero step consumes one key
            symbol and is unscored
  unit28z2  the same; a zero step consumes nothing
  In the step views a skipped F at c_i has two conventions, both allowed: literal (step i unkeyed,
  the chain state becomes F, step i+1 keyed as observed) and transparent (the state is kept, so the
  next keyed step is taken from the previous state). Fs in a run (FF...) are handled jointly: each F
  of the run is keyed, literal or transparent independently (B24). A skip scores W[F] in every view.
Polarity: (a, b) in {+1,-1}^2; Vigenere decrypt p = c - k is (1, -1), Beaufort p = k - c is (-1, 1).
Direction: the source read forwards or as a reversed token sequence.
"""
import math
import random

import numpy as np

from .detectors import EnglishModel
from .gematria import Alphabet, LatinNames

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


class Source:
    """A key source: Chunks (words or bytes) of letters or rune tokens, plus its lattice arrays.

    Kind 'latin': Chunks are Latin words (lattice on); 'runes': rune-index lists (no lattice);
    'bytes': one byte array (value % 29, no lattice). Tok1/Tok2/Tok3[j] = rune of the 1/2/3-letter token
    ending at letter j (Sentinel = no such token). Reverse() reads the token lattice backwards.
    """

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

    def Slice(self, Start, Stop):
        """Token arrays restricted to letters [Start, Stop) (used for windowed plant scoring)."""
        Out = object.__new__(Source)
        Out.__dict__.update(self.__dict__)
        Out.Tok1 = self.Tok1[Start:Stop]
        Out.Tok2 = None if self.Tok2 is None else self.Tok2[Start:Stop].copy()
        Out.Tok3 = None if self.Tok3 is None else self.Tok3[Start:Stop].copy()
        if Out.Tok2 is not None:
            Out.Tok2[:1] = Sentinel
            Out.Tok3[:2] = Sentinel
        Out.Length = len(Out.Tok1)
        return Out


def LatinSource(Name, Text):
    return Source(Name, "latin", [W for W in (NormaliseLatin(Part) for Part in Text.split()) if W])


def RuneSource(Name, Words):
    return Source(Name, "runes", [list(W) for W in Words if len(W)])


def ByteSource(Name, Data):
    return Source(Name, "bytes", np.frombuffer(bytes(Data), dtype=np.uint8))


def PageEvents(Runes, View, Labels=False):
    """Events for one page in one view: list of (CipherIndex, Options). An option is (Atoms, Const),
    Atoms a tuple of keyed symbols (>= 0) or -1 (consume one key symbol, unscored); Const != 0 marks
    F-skips (Const = number of skips x W[F]). With Labels=True each event is (CipherIndex, Options, Info),
    Info[k] = (Skips, Layout) for option k: Skips [(cipher index, 'S'/'L'/'T')], Layout the option's
    plaintext order ('S' a skip, 'A' one atom)."""
    C = list(Runes)
    N = len(C)
    SkipScore = float(Weights(ViewModulus[View])[0])
    if View == "raw29":
        Events = []
        for I, V in enumerate(C):
            if V == 0:
                Events.append((I, [((0,), 0.0), ((), SkipScore)], [([], "A"), ([(I, "S")], "S")]))
            else:
                Events.append((I, [((V,), 0.0)], [([], "A")]))
        return Events if Labels else [(I, Options) for I, Options, _ in Events]

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
        if C[I] != 0:
            Events.append((I, [(Atom(C[I] - C[I - 1]), 0.0)], [([], "A")]))
            I += 1
            continue
        # An F-run I..J-1: each F is keyed (state F), a literal skip (state F) or a transparent skip
        # (state kept); the first non-F rune after the run is keyed from the state the run leaves.
        J = I
        while J < N and C[J] == 0:
            J += 1
        Paths = {(C[I - 1], (), 0): ([], "")}  # (State, Atoms, Skips) -> (labels, layout)
        for K in range(I, J):
            Next = {}
            for (State, Atoms, Skips), (Lab, Lay) in Paths.items():
                Keyed = Atom(0 - State)
                for Item in [((0, Atoms + Keyed, Skips), (Lab, Lay + "A" * len(Keyed))),
                             ((0, Atoms, Skips + 1), (Lab + [(K, "L")], Lay + "S")),
                             ((State, Atoms, Skips + 1), (Lab + [(K, "T")], Lay + "S"))]:
                    Next.setdefault(*Item)
            Paths = Next
        Options, Info = {}, {}
        for (State, Atoms, Skips), (Lab, Lay) in Paths.items():
            if J < N:
                Out = Atom(C[J] - State)
                Atoms, Lay = Atoms + Out, Lay + "A" * len(Out)
            if (Atoms, Skips) not in Options:
                Options[(Atoms, Skips)] = (Atoms, Skips * SkipScore)
                Info[(Atoms, Skips)] = (Lab, Lay)
        Keys = sorted(Options, key=lambda Key: (Key[1], len(Key[0])))
        Events.append((I, [Options[Key] for Key in Keys], [Info[Key] for Key in Keys]))
        I = J + 1
    return Events if Labels else [(I, Options) for I, Options, _ in Events]


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


def SearchPages(PageRunes, Src, ViewList=Views, Directions=(False, True)):
    """All forms (views x 4 polarities x directions), serially. See SearchCombo for the parallel unit."""
    Out = {}
    for Rev, Modulus, B in Combos(ViewList, Directions):
        Out.update(SearchCombo(PageRunes, Src, Rev, Modulus, B, ViewList))
    return Out


def Trace(Runes, Src, View, A, B, EndY, Margin=None):
    """Exact traceback of the best path ending at source pointer EndY (float64, windowed).

    Returns dict: Score, StartY, EndY, Skips [(cipher index, 'S' raw / 'L' literal / 'T' transparent)],
    Plain (plaintext symbols in the view's modulus, a skip as 0) and TokenLengths (1, 2 or 3 letters).
    """
    Events = PageEvents(Runes, View, Labels=True)
    Modulus = ViewModulus[View]
    W = Weights(Modulus)
    Margin = Margin or 3 * len(Runes) + 10
    Lo = max(0, EndY - Margin)
    Tok = [Src.Tok1[Lo:EndY]] + ([Src.Tok2[Lo:EndY], Src.Tok3[Lo:EndY]] if Src.Lattice else [])
    Size = EndY - Lo

    def TokScore(Atom, Level, J):  # (score, plaintext) of the token of Level+1 letters ending at J
        if J < Level or J >= Size:
            return -math.inf, None
        T = int(Tok[Level][J])
        if T == Sentinel:
            return -math.inf, None
        if Atom < 0:
            return 0.0, None
        P = (A * Atom + B * T) % Modulus
        return W[P], P

    def Apply(Cur, Atom):
        New = np.full(Size + 1, -math.inf)
        for Level in range(len(Tok)):
            for Y in range(Level + 1, Size + 1):
                Sc, _ = TokScore(Atom, Level, Y - 1)
                if Cur[Y - Level - 1] + Sc > New[Y]:
                    New[Y] = Cur[Y - Level - 1] + Sc
        return New

    History = [np.zeros(Size + 1)]
    for _, Options, _ in Events:
        Best = np.full(Size + 1, -math.inf)
        for Atoms, Const in Options:
            Cur = History[-1]
            for Atom in Atoms:
                Cur = Apply(Cur, Atom)
            Best = np.maximum(Best, Cur + Const)
        History.append(Best)
    Y = Size
    Skips, Plain, Lengths = [], [], []
    for E in range(len(Events) - 1, -1, -1):
        Index, Options, Info = Events[E]
        Target = History[E + 1][Y]
        Found = False
        for OptionIndex, (Atoms, Const) in enumerate(Options):
            Combos = [()]
            for _ in Atoms:
                Combos = [Co + (L,) for Co in Combos for L in range(len(Tok))]
            for Combo in Combos:
                Yc, Total, Got = Y, Const, []
                for Atom, Level in zip(reversed(Atoms), reversed(Combo)):
                    Sc, P = TokScore(Atom, Level, Yc - 1)
                    Total += Sc
                    Got.append((P, Level + 1))
                    Yc -= Level + 1
                if Total > -math.inf and Yc >= 0 and abs(History[E][Yc] + Total - Target) < 1e-6:
                    Found = True
                    break
            if Found:
                break
        if not Found:
            raise RuntimeError("traceback failed")
        Got.reverse()
        Labels, Layout = Info[OptionIndex]
        Skips.extend(Labels)
        Atoms = iter(Got)
        Part = [0 if Item == "S" else next(Atoms)[0] for Item in Layout]
        Plain[:0] = [P for P in Part if P is not None]
        Lengths[:0] = [L for _, L in Got]
        Y = Yc
    return {"Score": float(History[-1][Size]), "StartY": Lo + Y, "EndY": EndY, "Skips": sorted(Skips),
            "Plain": Plain, "TokenLengths": Lengths}


def GumbelFromMoments(Values):
    """(Location, Scale) of a Gumbel max distribution by moments."""
    Values = np.asarray(Values, dtype=np.float64)
    Scale = Values.std(ddof=1) * math.sqrt(6) / math.pi
    return Values.mean() - 0.5772156649 * Scale, Scale


def GumbelQuantile(Location, Scale, Q):
    return Location - Scale * math.log(-math.log(Q))


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
