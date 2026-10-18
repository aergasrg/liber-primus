"""tools/ask_other_model.py against a local mock of the Responses API (no network, no tokens).

Each test runs the real CLI in a subprocess with --root pointing at a temp dir, so the repo's own
budget ledger and docs/council are never touched.
"""
import datetime
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

RepoRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RepoRoot, "tools"))

import ask_other_model as Ask  # noqa: E402

Tool = os.path.join(RepoRoot, "tools", "ask_other_model.py")
MockModels = ["mock-completed", "mock-incomplete", "mock-failed", "mock-flagged", "mock-prohang", "mock-slow"]
FullUsage = {"input_tokens": 100, "output_tokens": 500, "total_tokens": 600,
             "output_tokens_details": {"reasoning_tokens": 300}}


def Message(Text):
    return [{"type": "message", "content": [{"type": "output_text", "text": Text}]}]


class MockState:
    def __init__(self):
        self.Responses = {}
        self.Bodies = []
        self.Cancelled = []
        self.Lock = threading.Lock()


def Advance(Record):
    """Status the mock reports on each GET for a given model and mode."""
    Model, Pro = Record["Body"]["model"], Record["Body"]["reasoning"].get("mode") == "pro"
    Record["Polls"] += 1
    Base = {"id": Record["Id"], "model": Model}
    if Model == "mock-prohang" and Pro:
        return dict(Base, status="in_progress")
    if Model == "mock-slow" and Record["Polls"] < 20:
        return dict(Base, status="in_progress")
    if Record["Polls"] < 2:
        return dict(Base, status="in_progress")
    if Model in ("mock-completed", "mock-prohang", "mock-slow"):
        return dict(Base, status="completed", usage=FullUsage, output=Message("ANSWER-TEXT"))
    if Model == "mock-incomplete":
        return dict(Base, status="incomplete", usage=FullUsage, output=Message("PARTIAL-TEXT"),
                    incomplete_details={"reason": "max_output_tokens"})
    if Model == "mock-flagged":
        return dict(Base, status="failed", usage=FullUsage,
                    error={"code": "invalid_prompt", "message": "flagged as potentially violating our usage policy"})
    return dict(Base, status="failed", error={"code": "server_error", "message": "boom"})


def MakeHandler(State):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *Args):
            pass

        def Reply(self, Payload, Code=200):
            Data = json.dumps(Payload).encode()
            self.send_response(Code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(Data)))
            self.end_headers()
            self.wfile.write(Data)

        def do_GET(self):
            if self.path == "/v1/models":
                return self.Reply({"data": [{"id": "mock-completed", "created": 1790000000}]})
            Id = self.path.rsplit("/", 1)[-1]
            with State.Lock:
                Record = State.Responses[Id]
                self.Reply(Advance(Record))

        def do_POST(self):
            Length = int(self.headers.get("Content-Length") or 0)
            Body = json.loads(self.rfile.read(Length) or b"{}")
            if self.path.endswith("/cancel"):
                Id = self.path.split("/")[-2]
                with State.Lock:
                    State.Cancelled.append(Id)
                return self.Reply({"id": Id, "status": "cancelled"})
            with State.Lock:
                Id = f"resp_{len(State.Responses) + 1}"
                State.Responses[Id] = {"Id": Id, "Body": Body, "Polls": 0}
                State.Bodies.append(Body)
            self.Reply({"id": Id, "status": "queued", "model": Body["model"]})
    return Handler


@pytest.fixture
def Mock():
    State = MockState()
    Server = ThreadingHTTPServer(("127.0.0.1", 0), MakeHandler(State))
    Thread = threading.Thread(target=Server.serve_forever, daemon=True)
    Thread.start()
    State.BaseUrl = f"http://127.0.0.1:{Server.server_address[1]}/v1"
    yield State
    Server.shutdown()


@pytest.fixture
def Root(tmp_path):
    Doc = tmp_path / "docs" / "models"
    Doc.mkdir(parents=True)
    (Doc / "openai.md").write_text(f"---\nupdated: {datetime.date.today()}\n---\n" + "\n".join(MockModels) + "\n")
    (tmp_path / "prompt.md").write_text("Q")
    return tmp_path


def Run(Mock, Root, *Extra, Cap="230000", Wait=True):
    Env = {Key: Value for Key, Value in os.environ.items() if Key != "OPENAI_API_KEY"}
    Env.update(OPENAI_BASE_URL=Mock.BaseUrl, OPENAI_TOKEN_CAP=Cap)
    Cmd = [sys.executable, Tool, "--root", str(Root), "--no-fetch", "--poll-seconds", "0.05",
           "--prompt-file", str(Root / "prompt.md"), "--purpose", "test", *Extra]
    Proc = subprocess.Popen(Cmd, env=Env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if not Wait:
        return Proc
    Out, Err = Proc.communicate(timeout=60)
    return Proc.returncode, Out, Err


def Ledger(Root):
    Path = Root / "budget" / "openai" / "ledger.jsonl"
    return [json.loads(Line) for Line in Path.read_text().splitlines()] if Path.exists() else []


def Finals(Root):
    return [Entry for Entry in Ledger(Root) if Entry["status"] != "reserved"]


def test_completed_call_logs_and_saves(Mock, Root):
    Code, Out, Err = Run(Mock, Root, "--model", "mock-completed", "--max-output", "8000")
    assert Code == 0, Err
    Lines = Out.strip().splitlines()
    assert len(Lines) == 2 and Lines[0].startswith("remaining:") and Lines[1].startswith("saved: docs/council/")
    assert Lines[1].endswith("/01-mock-completed-test.md")
    Entries = Ledger(Root)
    assert [Entry["status"] for Entry in Entries] == ["reserved", "completed"]
    assert Entries[0]["id"] == Entries[1]["id"]
    assert Entries[1]["total_tokens"] == 600 and Entries[1]["reasoning_tokens"] == 300
    for Key in ("time", "branch", "session", "model", "mode", "effort", "purpose", "input_tokens", "output_tokens"):
        assert Key in Entries[1]
    Body = Mock.Bodies[0]
    assert Body["background"] is True and Body["max_output_tokens"] == 8000
    assert Body["input"][0] == {"role": "developer", "content": Ask.DeveloperMessage}
    assert "ANSWER-TEXT" in (Root / Lines[1][len("saved: "):]).read_text()
    assert "remaining: 169400 general" in Lines[0]  # 220000 - 50000 - 600


def test_incomplete_keeps_partial_and_fails(Mock, Root):
    Code, Out, _ = Run(Mock, Root, "--model", "mock-incomplete", "--max-output", "8000")
    assert Code == 1
    assert Finals(Root)[0]["status"] == "incomplete"
    assert "PARTIAL-TEXT" in (Root / Out.splitlines()[1][len("saved: "):]).read_text()


def test_failed_without_usage_counts_whole_reservation(Mock, Root):
    Code, _, _ = Run(Mock, Root, "--model", "mock-failed", "--max-output", "8000")
    assert Code == 1
    Entries = Ledger(Root)
    assert Entries[1]["status"] == "failed"
    assert Entries[1]["total_tokens"] == Entries[0]["total_tokens"] > 8000


def test_flagged_is_logged_and_not_retried(Mock, Root):
    Code, _, Err = Run(Mock, Root, "--model", "mock-flagged", "--max-output", "8000")
    assert Code == 1 and "gpt-6.1-sol" in Err
    assert Finals(Root)[0]["status"] == "flagged"
    Code, _, Err = Run(Mock, Root, "--model", "mock-flagged", "--max-output", "8000")
    assert Code == 2 and "flagged" in Err
    assert len(Mock.Bodies) == 1


def test_pro_that_never_finishes_falls_back_once(Mock, Root):
    Code, Out, Err = Run(Mock, Root, "--model", "mock-prohang", "--mode", "pro", "--deadline-seconds", "0.5")
    assert Code == 0, Err
    Entries = Finals(Root)
    assert [(Entry["mode"], Entry["status"]) for Entry in Entries] == [("pro", "timeout"), ("standard", "completed")]
    assert Entries[0]["effort"] == Entries[1]["effort"] == "high"
    assert Entries[0]["max_output"] == 40000
    assert Entries[0]["total_tokens"] > 40000  # cancel returned no usage: whole reservation counted
    assert Mock.Cancelled == ["resp_1"]
    assert Mock.Bodies[0]["reasoning"] == {"effort": "high", "mode": "pro"}
    assert Mock.Bodies[1]["reasoning"] == {"effort": "high"}


def test_reserve_needs_verify_or_flag(Mock, Root):
    # Cap 60000, so 10000 is spendable without the reserve.
    Code, _, Err = Run(Mock, Root, "--model", "mock-completed", "--max-output", "16000", Cap="70000")
    assert Code == 2 and "reserve" in Err and not Ledger(Root)
    Code, _, _ = Run(Mock, Root, "--model", "mock-completed", "--max-output", "16000", "--use-reserve", Cap="70000")
    assert Code == 0
    Code, _, _ = Run(Mock, Root, "--model", "mock-completed", "--max-output", "16000", "--purpose", "verify",
                     Cap="70000")
    assert Code == 0


def test_cap_refusal(Mock, Root):
    Code, _, Err = Run(Mock, Root, "--model", "mock-completed", "--max-output", "25000", "--use-reserve", Cap="30000")
    assert Code == 2 and "refused" in Err
    assert not Mock.Bodies and not Ledger(Root)
    Code, _, Err = Run(Mock, Root, "--model", "mock-completed", "--max-output", "60000")
    assert Code == 2 and "48000" in Err


def test_two_parallel_calls_share_the_lock(Mock, Root):
    # 12000 general tokens: each call reserves ~8050, so exactly one of two simultaneous calls fits.
    Procs = [Run(Mock, Root, "--model", "mock-slow", "--max-output", "8000", Cap="72000", Wait=False)
             for _ in range(2)]
    Codes = sorted(Proc.wait(timeout=60) for Proc in Procs)
    for Proc in Procs:
        Proc.communicate()
    assert Codes == [0, 2]
    Entries = Ledger(Root)
    assert len(Entries) == 2 and len({Entry["id"] for Entry in Entries}) == 1


def test_dry_run_and_policy_refusals(Mock, Root):
    Code, Out, _ = Run(Mock, Root, "--model", "mock-completed", "--dry-run")
    assert Code == 0 and "would fit" in Out and not Ledger(Root) and not Mock.Bodies
    assert Run(Mock, Root, "--model", "mock-completed", "--effort", "max")[0] == 2
    assert Run(Mock, Root, "--model", "mock-completed", "--effort", "low")[0] == 2
    assert Run(Mock, Root, "--model", "gpt-6-astra", "--effort", "none", "--max-output", "200")[0] == 2
    assert Run(Mock, Root, "--model", "mock-undescribed", "--max-output", "200")[0] == 2


def test_merge_by_id_and_totals():
    Local = [{"id": "a", "status": "reserved", "total_tokens": 9000, "time": "1"},
             {"id": "a", "status": "completed", "total_tokens": 700, "time": "2"}]
    Origin = [{"id": "a", "status": "reserved", "total_tokens": 9000, "time": "1"},
              {"id": "b", "status": "reserved", "total_tokens": 5000, "time": "3"}]
    Merged = Ask.MergeLedgers(Local, Origin)
    assert len(Merged) == 3
    assert Ask.SpentTokens(Merged) == 700 + 5000
