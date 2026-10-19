"""E0035 (B03): the public-domain texts Cicada used, as page-local skip-tolerant running keys.

Hypothesis: each LP page is enciphered with a running key read from Liber AL vel Legis (Cicada's 2013 book
code text), the 1911 Britannica "Cicada" article (2012) or Blake's Marriage of Heaven and Hell (2012),
starting anywhere, with any ciphertext F possibly a non-consuming F-skip.
Method: exactly E0029's engine, forms, null, planted controls and power study (lp.runningkey, 32 forms),
imported from experiments/E0029_skip_tolerant_running_key.py with three new sources and its own output
directory. Only the family-wise threshold changes (55 pages x 3 sources).
Sources (fetched by scripts/fetch_keysources.sh into data/texts/, never committed):
  liber_al       Wikisource wikitext, markup stripped; verses and the Comment (Crowley, PD in the US)
  britannica     1911 Britannica "Cicada" article via the Wikisource parse API, tags stripped (~2,000 letters)
  blake          Gutenberg 45315 body, Marriage of Heaven and Hell
Stages: real, null, power, report (as E0029; controls = the power stage's plants on each source).
Usage: python3 experiments/E0035_cicada_public_domain_texts.py STAGE [--source NAME] [--reps R] [--plants P]
Outputs: results/E0035/ (small JSON/text); checkpoints in results/E0035/checkpoint/ (gitignored).
"""
import html
import importlib.util
import json
import multiprocessing
import os
import re
import sys

Here = os.path.dirname(os.path.abspath(__file__))
Spec = importlib.util.spec_from_file_location("E0029", os.path.join(Here, "E0029_skip_tolerant_running_key.py"))
E29 = importlib.util.module_from_spec(Spec)
sys.modules["E0029"] = E29
Spec.loader.exec_module(E29)

TextDir = os.path.join(E29.DataDir, "texts")
Sources = ["liber_al", "britannica", "blake"]
OrigRawSource = E29.RawSource


def Read(Name):
    with open(os.path.join(TextDir, Name), encoding="utf-8") as Handle:
        return Handle.read()


def LiberAl():
    Text = Read("liber_al.txt")
    Text = Text[:Text.index("{{PD/US")]
    Text = re.sub(r"\{\{[^}]*\}\}", " ", Text)      # templates (header, c|...)
    Text = re.sub(r"<[^>]+>", " ", Text)            # html
    Text = re.sub(r"\[\[[^\]|]*\|?([^\]]*)\]\]", r"\1", Text)
    return Text.replace("'''", "").replace("''", "")


def Britannica():
    Text = json.loads(Read("britannica_cicada.json"))["parse"]["text"]
    Text = re.sub(r"<style.*?</style>", "", Text, flags=re.S)
    Text = html.unescape(re.sub(r"<[^>]+>", " ", Text))
    Start = Text.index("CICADA")
    return Text[Start:Text.index("See also", Start)] if "See also" in Text[Start:] else Text[Start:]


def RawSource(Name):
    if Name == "liber_al":
        return "latin", LiberAl()
    if Name == "britannica":
        return "latin", Britannica()
    if Name == "blake":
        return "latin", E29.GutenbergBody(os.path.join(TextDir, "blake_marriage.txt"))
    return OrigRawSource(Name)


E29.RawSource = RawSource
TraceFailures = []
OrigTrace = E29.Rk.Trace


def SafeTrace(*Args, **Kwargs):
    """E0029's power stage uses Trace only to count exact start recovery (3 plants per row). Trace raises
    StopIteration on a few unit28 plants (layout/atom mismatch, to be fixed in lp.runningkey); count it as
    an inexact start and log it instead of aborting the run."""
    try:
        return OrigTrace(*Args, **Kwargs)
    except StopIteration:
        TraceFailures.append(Args[2])
        return {"StartY": -10 ** 9}


E29.Rk.Trace = SafeTrace
E29.OutDir = os.path.join(E29.RepoRoot, "results", "E0035")
E29.CheckDir = os.path.join(E29.OutDir, "checkpoint")
E29.CpuSources = Sources
E29.GpuSources = []


def Main():
    import argparse
    Parser = argparse.ArgumentParser()
    Parser.add_argument("stage", choices=["real", "null", "power", "report", "sizes"])
    Parser.add_argument("--source", default=None)
    Parser.add_argument("--reps", type=int, default=20)
    Parser.add_argument("--plants", type=int, default=100)
    Args = Parser.parse_args()
    os.makedirs(E29.CheckDir, exist_ok=True)
    Names = [Args.source] if Args.source else Sources
    if Args.stage == "sizes":
        for Name in Names:
            Src = E29.BuildSource(Name)
            print(Name, "letters", Src.Length, "head", Src.Letters[:60])
        return
    if Args.stage == "report":
        E29.StageReport()
        return
    with multiprocessing.get_context("fork").Pool(E29.Workers) as Pool:
        for Name in Names:
            if Args.stage == "real":
                E29.StageReal(Name, Pool)
            elif Args.stage == "null":
                E29.StageNull(Name, Args.reps, Pool)
            elif Args.stage == "power":
                E29.StagePower(Name, Args.plants, Pool)
                E29.Log(f"trace failures so far (views): {TraceFailures}")


if __name__ == "__main__":
    Main()
