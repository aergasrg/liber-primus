"""Quick port check (bootstrap session): the seed PrngSweep control, rebuilt on the lp package.

Plants a Perl drand48 keystream (seed 777777) into solved plaintext in raw and chain form, then
recovers it by sweeping seeds 777000..777999 through the same scorer used on real sections.
Seed session reported control IoC 1.88 (raw) and 1.81 (chain). Also scores 4,096 real seeds on the
first 300 runes of every unsolved section to show the noise level. Runtime ~10 s.
Output: results/port_check.txt
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lp.ciphers import ChainEncrypt, ChainUnits  # noqa: E402
from lp.controls import ControlPlaintext  # noqa: E402
from lp.data import LoadAllUnsolved, RepoRoot  # noqa: E402
from lp.detectors import BatchIoc  # noqa: E402
from lp.keysources import Drand48Ints  # noqa: E402

Window = 300


def BestOverForms(Raw, Units, Seeds):
    Key29 = Drand48Ints(Seeds, Window, 29)
    Key28 = Drand48Ints(Seeds, Window, 28)
    Scores = [BatchIoc((Raw[None, :] - Key29) % 29, 29), BatchIoc((Raw[None, :] + Key29) % 29, 29),
              BatchIoc((Units[None, :] - Key28) % 28, 28), BatchIoc((Units[None, :] + Key28) % 28, 28)]
    return np.max(np.stack(Scores), axis=0), Scores


Started = time.time()
Plain = np.array(ControlPlaintext(Window + 1))
Noise = np.random.default_rng(29).integers(0, 29, Window)
NoiseUnits = np.random.default_rng(31).integers(0, 28, Window)
PlantedRaw = (Plain[:Window] + Drand48Ints([777777], Window, 29)[0]) % 29
PlantedChain = ChainEncrypt(list(Plain[:Window + 1]), list(Drand48Ints([777777], Window + 1, 28)[0]))
PlantedUnits = np.array(ChainUnits(PlantedChain)[0][:Window])
Seeds = np.arange(777000, 778000)
_, RawScores = BestOverForms(PlantedRaw, NoiseUnits, Seeds)
_, ChainScores = BestOverForms(Noise, PlantedUnits, Seeds)
RawHit = int(Seeds[np.argmax(RawScores[0])])
ChainHit = int(Seeds[np.argmax(ChainScores[2])])
Lines = [f"control raw: best seed {RawHit} IoC {RawScores[0].max():.3f} (seed session 1.88)",
         f"control chain: best seed {ChainHit} IoC {ChainScores[2].max():.3f} (seed session 1.81)"]
RealSeeds = np.arange(4096)
for Section in LoadAllUnsolved():
    Raw = np.array(Section["Runes"][:Window])
    Units = np.array(ChainUnits(Section["Runes"])[0][:Window])
    Best, _ = BestOverForms(Raw, Units, RealSeeds)
    Lines.append(f"{Section['Name']:7} seeds 0..4095 best IoC {Best.max():.3f}")
Lines.append(f"runtime {time.time() - Started:.1f}s")
OutPath = os.path.join(RepoRoot, "results", "port_check.txt")
os.makedirs(os.path.dirname(OutPath), exist_ok=True)
with open(OutPath, "w") as Handle:
    Handle.write("\n".join(Lines) + "\n")
print("\n".join(Lines[:2]), f"\nreal best {max(float(L.split()[-1]) for L in Lines[2:-1]):.3f}; full output in {OutPath}")
assert RawHit == 777777 and ChainHit == 777777
