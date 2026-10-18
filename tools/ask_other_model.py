"""OpenAI second-opinion helper (v3). Standard library only. All OpenAI calls go through this file.

Read docs/models/openai.md first: the models it uses are newer than Claude's training data.

    python3 tools/ask_other_model.py --list-models
    python3 tools/ask_other_model.py --model gpt-6-astra --effort high --purpose bughunt --prompt-file brief.md

Every call is a background Responses API request (POST /v1/responses, poll GET every 15 s, cancel at the
deadline), budgeted against a shared token ledger in budget/openai/ledger.jsonl under an fcntl lock.
Prompt, reply and usage are saved to docs/council/<date>/<NN>-<model>-<purpose>.md. Stdout is only the
remaining budget and that path. Keys are never read aloud: an Authorization header is sent only when
OPENAI_API_KEY is set; otherwise the environment's credential proxy adds it.

Exit codes: 0 completed, 1 call ended without a full answer (incomplete, failed, flagged, timeout),
2 refused before calling (budget, policy, refresh rule), 3 HTTP or usage error.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

RepoRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DeveloperMessage = ("One-shot request from an automated research lab. You cannot ask questions. "
                    "State any assumption and answer fully, concretely, testably.")
DefaultCap = 230000
CapMargin = 10000
ReserveTokens = 50000
HardMaxOutput = 48000
PolicyMaxOutput = {"medium": 16000, "high": 25000, "xhigh": 40000, "pro": 40000}
DeadlineMinutes = {"none": 8, "low": 8, "medium": 8, "high": 12, "xhigh": 20, "pro": 30}
# Efforts each model accepts, from docs/models/openai.md. Unlisted models are not checked here.
ModelEfforts = {
    "gpt-6-astra": {"low", "medium", "high", "xhigh", "max"},
    "gpt-6.1-sol": {"low", "medium", "high", "xhigh", "max"},
    "gpt-6-luna": {"none", "low", "medium", "high", "xhigh", "max"},
}
FlagTerms = ("safety", "content_filter", "flagged", "usage policy", "invalid_prompt", "moderation", "cyber")
# --list-models only flags text/reasoning ids from the current generations (API created stamp).
ListHorizon = datetime.date(2026, 6, 1)
NonTextIdTerms = ("image", "realtime", "transcribe", "live", "tts", "audio", "search", "embedding", "moderation")
DocMaxAgeDays = 30


class Refused(Exception):
    """A call refused before any request was sent."""


# ---------------------------------------------------------------- paths, git, small helpers

def Paths(Root):
    Budget = os.path.join(Root, "budget", "openai")
    return {"Ledger": os.path.join(Budget, "ledger.jsonl"), "Lock": os.path.join(Budget, "ledger.lock"),
            "Council": os.path.join(Root, "docs", "council"), "ModelDoc": os.path.join(Root, "docs", "models", "openai.md")}


def Git(Root, *Args, Timeout=60):
    try:
        Done = subprocess.run(["git", "-C", Root, *Args], capture_output=True, text=True, timeout=Timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return Done.stdout if Done.returncode == 0 else None


def CurrentBranch(Root):
    return (Git(Root, "rev-parse", "--abbrev-ref", "HEAD") or "unknown").strip()


def Warn(Text):
    print(Text, file=sys.stderr)


def NowIso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def Slug(Text):
    return re.sub(r"[^A-Za-z0-9.]+", "-", Text).strip("-").lower() or "general"


# ---------------------------------------------------------------- ledger and budget

def ParseLedger(Text):
    Entries = []
    for Line in Text.splitlines():
        Line = Line.strip()
        if not Line:
            continue
        try:
            Entries.append(json.loads(Line))
        except json.JSONDecodeError:
            Warn("ledger: skipped an unreadable line")
    return Entries


def EntryKey(Entry):
    return (Entry.get("id"), "reserved" if Entry.get("status") == "reserved" else "final")


def MergeLedgers(*EntryLists):
    """Union by (id, reserved|final), first copy wins, ordered by time. Never drops an entry."""
    Merged = {}
    for Entries in EntryLists:
        for Entry in Entries:
            Merged.setdefault(EntryKey(Entry), Entry)
    return sorted(Merged.values(), key=lambda Entry: (Entry.get("time", ""), EntryKey(Entry)[1] != "reserved"))


def SpentTokens(Entries):
    """A final entry replaces its reservation; a reservation with no final (crash, running call) counts whole."""
    Finals, Reserved = {}, {}
    for Entry in Entries:
        Id, Kind = EntryKey(Entry)
        (Finals if Kind == "final" else Reserved)[Id] = int(Entry.get("total_tokens") or 0)
    return sum(Finals.values()) + sum(Total for Id, Total in Reserved.items() if Id not in Finals)


def CapTokens():
    try:
        Requested = int(os.environ.get("OPENAI_TOKEN_CAP") or DefaultCap)
    except ValueError:
        Requested = DefaultCap
    return min(Requested, DefaultCap) - CapMargin


def Remaining(Spent):
    Cap = CapTokens()
    return {"Cap": Cap, "General": max(0, Cap - ReserveTokens - Spent), "Total": max(0, Cap - Spent)}


def RemainingLine(Spent):
    Left = Remaining(Spent)
    return (f"remaining: {Left['General']} general, {Left['Total']} incl. reserve "
            f"(cap {Left['Cap']}, spent {Spent})")


def OriginLedger(Root, Fetch):
    if Fetch and Git(Root, "fetch", "-q", "origin", "main") is None:
        Warn("warning: git fetch origin main failed; merging the last fetched origin/main ledger")
    Text = Git(Root, "show", "origin/main:budget/openai/ledger.jsonl", Timeout=20)
    return ParseLedger(Text or "")


class LedgerLock:
    def __init__(self, Root):
        self.Path = Paths(Root)["Lock"]

    def __enter__(self):
        os.makedirs(os.path.dirname(self.Path), exist_ok=True)
        self.Handle = open(self.Path, "a")
        fcntl.flock(self.Handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, *Exc):
        fcntl.flock(self.Handle, fcntl.LOCK_UN)
        self.Handle.close()


def ReadLocalLedger(Root):
    Path = Paths(Root)["Ledger"]
    if not os.path.exists(Path):
        return []
    with open(Path, encoding="utf-8") as Handle:
        return ParseLedger(Handle.read())


def WriteLedger(Root, Entries):
    Path = Paths(Root)["Ledger"]
    os.makedirs(os.path.dirname(Path), exist_ok=True)
    Temp = Path + ".tmp"
    with open(Temp, "w", encoding="utf-8") as Handle:
        for Entry in Entries:
            Handle.write(json.dumps(Entry, sort_keys=True) + "\n")
    os.replace(Temp, Path)


def AppendEntry(Root, Entry):
    with LedgerLock(Root):
        with open(Paths(Root)["Ledger"], "a", encoding="utf-8") as Handle:
            Handle.write(json.dumps(Entry, sort_keys=True) + "\n")


def Reserve(Root, Call, Origin, DryRun=False):
    """Under the lock: merge origin/main, total, check cap and reserve, append the reservation."""
    with LedgerLock(Root):
        Entries = MergeLedgers(ReadLocalLedger(Root), Origin)
        Spent = SpentTokens(Entries)
        for Entry in Entries:
            if (Entry.get("status") == "flagged" and Entry.get("model") == Call["model"]
                    and Entry.get("prompt_sha256") == Call["prompt_sha256"]):
                raise Refused(f"refused: this prompt was flagged on {Call['model']} ({Entry.get('id')}); "
                              "do not retry that model, ask gpt-6.1-sol instead")
        Cap = CapTokens()
        Limit = Cap if Call["UsesReserve"] else Cap - ReserveTokens
        if Spent + Call["Reservation"] > Limit:
            Which = "cap" if Call["UsesReserve"] else "cap minus the 50k reserve (needs --purpose verify or --use-reserve)"
            raise Refused(f"refused: reservation {Call['Reservation']} + spent {Spent} passes the {Which} ({Limit}). "
                          + RemainingLine(Spent))
        if DryRun:
            return Spent
        Entry = {Key: Call[Key] for Key in ("id", "branch", "session", "model", "mode", "effort", "purpose",
                                             "max_output", "prompt_sha256")}
        Entry.update(time=NowIso(), status="reserved", input_tokens=0, output_tokens=0, reasoning_tokens=0,
                     total_tokens=Call["Reservation"])
        Entries.append(Entry)
        WriteLedger(Root, Entries)
        return Spent


def FinalSpent(Root):
    with LedgerLock(Root):
        return SpentTokens(ReadLocalLedger(Root))


# ---------------------------------------------------------------- HTTP

def BaseUrl():
    return (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")


def Request(Method, Path, Body=None, Timeout=60):
    Url = BaseUrl() + Path
    Headers = {"Content-Type": "application/json"}
    if os.environ.get("OPENAI_API_KEY"):
        Headers["Authorization"] = "Bearer " + os.environ["OPENAI_API_KEY"]
    Data = json.dumps(Body).encode() if Body is not None else None
    Req = urllib.request.Request(Url, data=Data, headers=Headers, method=Method)
    Host = urllib.parse.urlparse(Url).hostname or ""
    Handlers = [urllib.request.ProxyHandler({})] if Host in ("127.0.0.1", "localhost", "::1") else []
    with urllib.request.build_opener(*Handlers).open(Req, timeout=Timeout) as Resp:
        return json.loads(Resp.read().decode() or "{}")


def HttpErrorBody(Error):
    try:
        return json.loads(Error.read().decode() or "{}")
    except (ValueError, OSError):
        return {}


# ---------------------------------------------------------------- model doc, refresh rule

def ReadModelDoc(Root):
    Path = Paths(Root)["ModelDoc"]
    if not os.path.exists(Path):
        return None, None
    with open(Path, encoding="utf-8") as Handle:
        Text = Handle.read()
    Match = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", Text, re.M)
    return Text, (datetime.date.fromisoformat(Match.group(1)) if Match else None)


def DocDescribes(Text, ModelId):
    return re.search(r"(?<![\w.-])" + re.escape(ModelId) + r"(?![\w.-])", Text) is not None


def CheckRefreshRule(Root, ModelId):
    Text, Updated = ReadModelDoc(Root)
    if Text is None:
        raise Refused("refused: docs/models/openai.md is missing; write it before calling a model")
    if Updated is None or (datetime.date.today() - Updated).days > DocMaxAgeDays:
        raise Refused("refused: docs/models/openai.md is over 30 days old; refresh it (web search, "
                      "developers.openai.com/api/docs/models) and bump 'updated:' first")
    if not DocDescribes(Text, ModelId):
        raise Refused(f"refused: {ModelId} is not described in docs/models/openai.md; look it up and add it first")


def ListModels(Root):
    try:
        Data = Request("GET", "/models")
    except (urllib.error.URLError, OSError) as Error:
        Warn(f"list-models failed: {getattr(Error, 'code', '')} {getattr(Error, 'reason', Error)}")
        return 3
    Models = Data.get("data", [])
    Text, Updated = ReadModelDoc(Root)
    Text = Text or ""
    Recent = []
    for Model in Models:
        Created = datetime.datetime.fromtimestamp(Model.get("created", 0), datetime.timezone.utc).date()
        Id = Model.get("id", "")
        if Created >= ListHorizon and Id.startswith("gpt-") and not any(T in Id for T in NonTextIdTerms):
            Recent.append(Id)
    Undescribed = sorted(Id for Id in Recent if not DocDescribes(Text, Id))
    print(f"{len(Models)} models live; recent text models: {' '.join(sorted(Recent))}")
    Age = (datetime.date.today() - Updated).days if Updated else None
    print(f"docs/models/openai.md updated {Updated} ({Age} days ago)"
          + (" -> STALE, refresh it" if Age is None or Age > DocMaxAgeDays else ""))
    print("not in docs/models/openai.md: " + (" ".join(Undescribed) if Undescribed else "none"))
    return 0


# ---------------------------------------------------------------- one call

def IsFlagged(Response):
    Error = Response.get("error") or {}
    Text = f"{Error.get('code', '')} {Error.get('type', '')} {Error.get('message', '')}".lower()
    Reason = str((Response.get("incomplete_details") or {}).get("reason") or "").lower()
    return any(Term in Text or Term in Reason for Term in FlagTerms)


def OutputText(Response):
    if isinstance(Response.get("output_text"), str):
        return Response["output_text"]
    Parts = []
    for Item in Response.get("output") or []:
        if Item.get("type") == "message":
            for Content in Item.get("content") or []:
                if Content.get("type") in ("output_text", "text"):
                    Parts.append(Content.get("text", ""))
    return "".join(Parts)


def Usage(Response):
    Raw = Response.get("usage") or {}
    if not Raw:
        return None
    Details = Raw.get("output_tokens_details") or {}
    Input, Output = int(Raw.get("input_tokens") or 0), int(Raw.get("output_tokens") or 0)
    return {"input_tokens": Input, "output_tokens": Output,
            "reasoning_tokens": int(Details.get("reasoning_tokens") or 0),
            "total_tokens": int(Raw.get("total_tokens") or Input + Output)}


def RunCall(Call, PollSeconds, DeadlineSeconds):
    """Returns (Status, Response or {}, Usage or None, Note). Never raises for API outcomes."""
    Body = {"model": Call["model"], "background": True, "store": True,
            "max_output_tokens": Call["max_output"],
            "input": [{"role": "developer", "content": DeveloperMessage},
                      {"role": "user", "content": Call["PromptText"]}],
            "reasoning": {"effort": Call["effort"]}}
    if Call["mode"] == "pro":
        Body["reasoning"]["mode"] = "pro"
    if Call["SystemText"]:
        Body["instructions"] = Call["SystemText"]
    try:
        Response = Request("POST", "/responses", Body)
    except urllib.error.HTTPError as Error:
        Err = HttpErrorBody(Error)
        Status = "flagged" if IsFlagged(Err) else "error"
        Message = str((Err.get("error") or {}).get("message", ""))[:200]
        return Status, Err, {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0}, \
            f"HTTP {Error.code} on create: {Message}"
    except (urllib.error.URLError, OSError) as Error:
        return "error", {}, None, f"create failed: {Error}"
    ResponseId = Response.get("id", "")
    Deadline = time.monotonic() + DeadlineSeconds
    while Response.get("status") in ("queued", "in_progress"):
        if time.monotonic() >= Deadline:
            try:
                Response = Request("POST", f"/responses/{ResponseId}/cancel", {})
            except (urllib.error.URLError, OSError):
                pass
            return "timeout", Response, Usage(Response), f"deadline {DeadlineSeconds:.0f} s reached; cancelled"
        time.sleep(PollSeconds)
        try:
            Response = Request("GET", f"/responses/{ResponseId}")
        except urllib.error.HTTPError as Error:
            if Error.code < 500:
                return "error", Response, Usage(Response), f"HTTP {Error.code} while polling"
        except (urllib.error.URLError, OSError):
            pass  # transient; keep polling until the deadline
    Status = Response.get("status", "unknown")
    if IsFlagged(Response):
        return "flagged", Response, Usage(Response), "stopped by a safety check"
    if Status == "incomplete":
        Reason = (Response.get("incomplete_details") or {}).get("reason", "")
        return "incomplete", Response, Usage(Response), f"incomplete: {Reason}"
    if Status == "completed":
        return "completed", Response, Usage(Response), ""
    return Status if Status in ("failed", "cancelled") else "error", Response, Usage(Response), \
        str((Response.get("error") or {}).get("message", ""))[:200]


def SaveCouncilFile(Root, Call, Status, Reply, UsageData, Note):
    Folder = os.path.join(Paths(Root)["Council"], datetime.date.today().isoformat())
    os.makedirs(Folder, exist_ok=True)
    while True:
        Taken = [int(Name[:2]) for Name in os.listdir(Folder) if re.match(r"\d\d-", Name)]
        Number = max(Taken, default=0) + 1
        Path = os.path.join(Folder, f"{Number:02d}-{Slug(Call['model'])}-{Slug(Call['purpose'])}.md")
        try:
            Handle = open(Path, "x", encoding="utf-8")
            break
        except FileExistsError:
            continue
    UsageLine = ", ".join(f"{Key} {Value}" for Key, Value in (UsageData or {}).items()) or "none reported"
    with Handle:
        Handle.write(f"# {Number:02d} {Call['model']} / {Call['purpose']}\n\n"
                     f"- id: {Call['id']}\n- time: {NowIso()}\n- branch: {Call['branch']}\n"
                     f"- model: {Call['model']}, mode {Call['mode']}, effort {Call['effort']}, "
                     f"max-output {Call['max_output']}\n- status: {Status}" + (f" ({Note})" if Note else "") +
                     f"\n- usage: {UsageLine}\n\n")
        if Call["SystemText"]:
            Handle.write("## System\n\n" + Call["SystemText"].rstrip() + "\n\n")
        Handle.write("## Prompt\n\n" + Call["PromptText"].rstrip() + "\n\n## Reply\n\n"
                     + (Reply.rstrip() if Reply else "(no reply text)") + "\n")
    return os.path.relpath(Path, Root)


def Attempt(Root, Call, Origin, PollSeconds, DeadlineSeconds):
    """Reserve, call, record the final entry, save the council file. Returns (Status, Path, Spent)."""
    Reserve(Root, Call, Origin)
    Status, Response, UsageData, Note = RunCall(Call, PollSeconds, DeadlineSeconds)
    if UsageData is None:
        UsageData = {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "total_tokens": Call["Reservation"]}
        Note = (Note + "; " if Note else "") + "no usage reported, whole reservation counted"
    Entry = {Key: Call[Key] for Key in ("id", "branch", "session", "model", "mode", "effort", "purpose",
                                         "max_output", "prompt_sha256")}
    Entry.update(UsageData, time=NowIso(), status=Status, response_id=Response.get("id", ""), note=Note)
    AppendEntry(Root, Entry)
    Path = SaveCouncilFile(Root, Call, Status, OutputText(Response), UsageData, Note)
    return Status, Path, Note


def BuildCall(Args, Root, Mode, Effort, MaxOutput, PromptText, SystemText):
    Chars = len(DeveloperMessage) + len(PromptText) + len(SystemText)
    return {"id": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8],
            "branch": CurrentBranch(Root), "session": os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID", ""),
            "model": Args.model, "mode": Mode, "effort": Effort, "purpose": Slug(Args.purpose),
            "max_output": MaxOutput, "Reservation": math.ceil(Chars / 3) + MaxOutput,
            "prompt_sha256": hashlib.sha256((SystemText + "\0" + PromptText).encode()).hexdigest(),
            "UsesReserve": Args.use_reserve or Slug(Args.purpose) == "verify",
            "PromptText": PromptText, "SystemText": SystemText}


def ResolvePolicy(Args):
    Effort = Args.effort or ("high" if Args.mode == "pro" else "medium")
    if Effort == "max":
        raise Refused("refused: max effort is off-policy (public runs waited 7+ minutes for a first token)")
    Allowed = ModelEfforts.get(Args.model)
    if Allowed is not None and Effort not in Allowed:
        raise Refused(f"refused: {Args.model} does not accept effort {Effort} (HTTP 400); allowed: "
                      + ", ".join(sorted(Allowed)))
    PolicyKey = "pro" if Args.mode == "pro" else Effort
    MaxOutput = Args.max_output or PolicyMaxOutput.get(PolicyKey)
    if MaxOutput is None:
        raise Refused(f"refused: effort {Effort} is off-policy (do small jobs yourself); pass --max-output to force it")
    if not 1 <= MaxOutput <= HardMaxOutput:
        raise Refused(f"refused: --max-output must be 1..{HardMaxOutput}")
    return Effort, MaxOutput


def ReadText(Path):
    if not Path:
        return ""
    with open(Path, encoding="utf-8") as Handle:
        return Handle.read()


def Main(Argv=None):
    Parser = argparse.ArgumentParser(description="OpenAI second opinion, budgeted. Read docs/models/openai.md first.")
    Parser.add_argument("--list-models", action="store_true", help="GET /v1/models (no tokens) and flag undescribed ids")
    Parser.add_argument("--model")
    Parser.add_argument("--prompt-file")
    Parser.add_argument("--system-file")
    Parser.add_argument("--purpose", default="general", help="short slug; 'verify' may spend the 50k reserve")
    Parser.add_argument("--effort", choices=["none", "low", "medium", "high", "xhigh", "max"])
    Parser.add_argument("--mode", choices=["standard", "pro"], default="standard")
    Parser.add_argument("--max-output", type=int, help=f"default from the effort policy; hard max {HardMaxOutput}")
    Parser.add_argument("--dry-run", action="store_true", help="budget check only; nothing sent or written")
    Parser.add_argument("--use-reserve", action="store_true")
    # Test hooks (tests/test_ask_other_model.py); not for normal use.
    Parser.add_argument("--root", default=RepoRoot, help=argparse.SUPPRESS)
    Parser.add_argument("--poll-seconds", type=float, default=15.0, help=argparse.SUPPRESS)
    Parser.add_argument("--deadline-seconds", type=float, help=argparse.SUPPRESS)
    Parser.add_argument("--no-fetch", action="store_true", help=argparse.SUPPRESS)
    Args = Parser.parse_args(Argv)
    Root = os.path.abspath(Args.root)

    if Args.list_models:
        return ListModels(Root)
    if not Args.model or not Args.prompt_file:
        Parser.error("--model and --prompt-file are required (or use --list-models)")
    try:
        Effort, MaxOutput = ResolvePolicy(Args)
        CheckRefreshRule(Root, Args.model)
        PromptText, SystemText = ReadText(Args.prompt_file), ReadText(Args.system_file)
        Origin = OriginLedger(Root, Fetch=not Args.no_fetch)
        Modes = [Args.mode] + (["standard"] if Args.mode == "pro" else [])
        for Index, Mode in enumerate(Modes):
            Call = BuildCall(Args, Root, Mode, Effort, MaxOutput, PromptText, SystemText)
            if Args.dry_run:
                Spent = Reserve(Root, Call, Origin, DryRun=True)
                print(f"dry run: {Call['model']} {Mode} effort {Effort} max-output {MaxOutput} "
                      f"reservation {Call['Reservation']} would fit")
                print(RemainingLine(Spent))
                return 0
            Deadline = Args.deadline_seconds or 60 * DeadlineMinutes["pro" if Mode == "pro" else Effort]
            if Index:
                Origin = OriginLedger(Root, Fetch=not Args.no_fetch)  # fresh budget check for the fallback
                Warn("pro call did not finish; falling back once to standard mode")
            Status, Path, Note = Attempt(Root, Call, Origin, Args.poll_seconds, Deadline)
            if Mode == "pro" and Status in ("timeout", "failed", "error"):
                Warn(f"pro attempt: {Status} ({Note}); saved {Path}")
                continue
            break
    except Refused as Problem:
        Warn(str(Problem))
        return 2
    except OSError as Problem:
        Warn(f"error: {Problem}")
        return 3
    print(RemainingLine(FinalSpent(Root)))
    print(f"saved: {Path}")
    if Status == "flagged":
        Warn(f"stopped by a safety check: do not retry {Args.model}; ask gpt-6.1-sol instead")
    elif Status != "completed":
        Warn(f"status {Status}: {Note}" + ("; partial text kept in the saved file" if Status == "incomplete" else ""))
    return 0 if Status == "completed" else (3 if Status == "error" else 1)


if __name__ == "__main__":
    sys.exit(Main())
