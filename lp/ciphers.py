"""Cipher primitives on rune indices (mod 29) and on chain units (mod 28).

Conventions (keep them; every ledger entry assumes them):
  * Vigenere decrypt  p = c - k (mod 29); encrypt c = p + k.
  * Beaufort          p = k - c (mod 29) (self-inverse).
  * Atbash            p = 28 - c.
  * F-skip            a ciphertext F (index 0) at a chosen position passes through unchanged and does
                      NOT consume a key symbol. Welcome skips the 4,5,6,7,10,11,14,18,20,21,25th F.
  * Chain form        c_i = c_(i-1) + s_i, s_i in 1..28. Chain unit u_i = s_i - 1 (0..27) for every
                      non-doublet step; doublets (s_i = 0) are dropped. A keyed chain is
                      u_i = (p_i % 28 + k_i) % 28, so decrypt is (u_i - k_i) % 28.
"""
from .gematria import Alphabet, FirstPrimes, LatinToRunes


def FSkipPositions(Values, FOrdinals):
    """Indices of the ciphertext F runes whose 1-based ordinal is in FOrdinals."""
    Wanted = set(FOrdinals)
    Out = set()
    Seen = 0
    for Index, Value in enumerate(Values):
        if Value == 0:
            Seen += 1
            if Seen in Wanted:
                Out.add(Index)
    return Out


def ApplyKeyStream(Values, KeyStream, Sign=-1, Modulus=Alphabet, PassThrough=(), Beaufort=False):
    """Combine Values with KeyStream symbol by symbol.

    Sign -1 decrypts a Vigenere (c - k), +1 encrypts. Beaufort gives k - c. Positions in
    PassThrough are copied unchanged and do not consume key. KeyStream may be any indexable; it is
    cycled if shorter than needed.
    """
    PassThrough = set(PassThrough)
    Out = []
    KeyPos = 0
    KeyLength = len(KeyStream)
    for Index, Value in enumerate(Values):
        if Index in PassThrough:
            Out.append(Value)
            continue
        Key = KeyStream[KeyPos % KeyLength]
        KeyPos += 1
        if Beaufort:
            Out.append((Key - Value) % Modulus)
        else:
            Out.append((Value + Sign * Key) % Modulus)
    return Out


def Vigenere(Values, Key, Decrypt=True, FSkips=()):
    """Key: Latin string or list of indices. FSkips: 1-based ordinals of ciphertext Fs to pass through."""
    KeyValues = LatinToRunes(Key) if isinstance(Key, str) else list(Key)
    PassThrough = FSkipPositions(Values, FSkips) if Decrypt else ()
    return ApplyKeyStream(Values, KeyValues, -1 if Decrypt else 1, PassThrough=PassThrough)


def Beaufort(Values, Key, FSkips=()):
    KeyValues = LatinToRunes(Key) if isinstance(Key, str) else list(Key)
    return ApplyKeyStream(Values, KeyValues, PassThrough=FSkipPositions(Values, FSkips), Beaufort=True)


def Atbash(Values):
    return [(Alphabet - 1 - V) for V in Values]


def Shift(Values, Amount):
    return [(V + Amount) % Alphabet for V in Values]


def TotientStream(Length, Offset=0):
    """phi(p_n) = p_n - 1 for the n-th prime (An End uses c - (p_n - 1))."""
    return [P - 1 for P in FirstPrimes(Length + Offset)][Offset:]


def CiphertextAutokey(Values, Lag, Sign=-1, Modulus=Alphabet):
    """p_i = c_i + Sign * c_(i-Lag); the first Lag symbols pass unchanged."""
    return [V if I < Lag else (V + Sign * Values[I - Lag]) % Modulus for I, V in enumerate(Values)]


def PlaintextAutokey(Values, Primer, Sign=-1, Modulus=Alphabet):
    """p_i = c_i + Sign * k_i with k = Primer followed by the recovered plaintext."""
    Key = list(Primer)
    Out = []
    for I, V in enumerate(Values):
        P = (V + Sign * Key[I]) % Modulus
        Out.append(P)
        Key.append(P)
    return Out


def ChainUnits(Values):
    """Return (Units, Positions): u = step - 1 for non-zero steps, and the index i of c_i for each."""
    Units, Positions = [], []
    for Index in range(1, len(Values)):
        Step = (Values[Index] - Values[Index - 1]) % Alphabet
        if Step:
            Units.append(Step - 1)
            Positions.append(Index)
    return Units, Positions


def ChainDecrypt(Values, Key28, Sign=-1):
    """Chain-form decrypt: (u_i + Sign * k_i) % 28 over the chain units of Values."""
    Units, _ = ChainUnits(Values)
    return ApplyKeyStream(Units, Key28, Sign, Modulus=28)


def ChainEncrypt(Plain, Key28, Start=5):
    """Planting helper: c_0 = Start, c_i = c_(i-1) + 1 + (p_i % 28 + k_i) % 28 (mod 29).

    Produces no doublets. Output has len(Plain) + 1 runes.
    """
    Chain = [Start]
    for Index, P in enumerate(Plain):
        Chain.append((Chain[-1] + 1 + (P % 28 + Key28[Index % len(Key28)]) % 28) % Alphabet)
    return Chain
