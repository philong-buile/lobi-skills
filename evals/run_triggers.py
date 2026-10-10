"""Trigger eval: does a plain-language prompt fire the right lobi-skills skill?

For each case in triggers.json, runs a headless Claude Code session with ONLY this repo's
plugins loaded (no user settings, plugins or skills) inside a small fixture web app
(evals/fixture/), lets the model take up to --max-turns turns with every writing tool disabled,
and records the first skill it invokes. A miss also records the model's first action.

    python evals/run_triggers.py [--runs N] [--max-turns 6] [--model sonnet] [--workers 4]

Needs the `claude` CLI, logged in (`claude auth login`). Each run is one short session on your
account. Results are printed and written to evals/results/triggers-<date>.md.
"""

import argparse
import concurrent.futures
import datetime
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
BLOCKED = "Bash Edit Write NotebookEdit WebFetch WebSearch"
CLAUDE = shutil.which("claude") or "claude"  # on Windows the CLI is a .cmd shim


def run_case(prompt, workdir, model, max_turns):
    cmd = [CLAUDE, "-p", prompt, "--setting-sources", "project", "--output-format", "stream-json",
           "--verbose", "--max-turns", str(max_turns), "--no-session-persistence", "--disallowedTools", BLOCKED]
    for plugin in sorted((ROOT / "plugins").iterdir()):
        cmd += ["--plugin-dir", str(plugin)]
    if model:
        cmd += ["--model", model]
    timed_out = False
    try:
        # ponytail: on Windows `claude` is a .cmd shim, and killing the shim leaves the real
        # CLI running, so communicate() waits for it and 300 s is not a hard cap. Kill the
        # process tree (taskkill /T /F) if a run ever needs a strict limit.
        out = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, encoding="utf-8",
                             stdin=subprocess.DEVNULL, timeout=300).stdout
    except subprocess.TimeoutExpired as e:
        # A session that keeps working after its skill fired is still a valid case: the
        # first skill is already in the partial transcript, so score that instead of
        # losing every result to one slow run.
        out, timed_out = as_text(e.stdout), True
    action = first_action(out)
    return first_skill(out), f"timeout after {action}" if timed_out else action, session_model(out)


def as_text(out):
    """TimeoutExpired.stdout may be bytes, str or None depending on the platform."""
    if isinstance(out, bytes):
        return out.decode("utf-8", "replace")
    return out or ""


def first_skill(stream):
    """Return the first skill invoked in a stream-json transcript, None if none, or raise on auth errors."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and "Failed to authenticate" in block.get("text", ""):
                raise RuntimeError("claude CLI is not logged in: run `claude auth login`")
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                return str(block["input"].get("skill", "")).split(":")[-1].lstrip("/")
    return None


def session_model(stream):
    """Model and CLI version from the init event, so the report states what actually ran."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("subtype") == "init":
            return f"{event.get('model')}, Claude Code {event.get('claude_code_version')}"
    return "unknown"


def first_action(stream):
    """Name of the first tool the model used, for explaining misses."""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                return block["name"]
    return "answered"


def self_test():
    stream = "\n".join(json.dumps(e) for e in [
        {"type": "system"},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "review-helpers:pl-ship-change"}}]}},
    ])
    assert first_skill(stream) == "pl-ship-change"
    assert first_action(stream) == "Read" and first_action("") == "answered"
    init = json.dumps({"subtype": "init", "model": "m", "claude_code_version": "1.0"})
    assert session_model(init) == "m, Claude Code 1.0" and session_model("") == "unknown"
    assert first_skill('{"type": "result"}\nnot json') is None
    assert as_text(None) == "" and as_text(b"ok") == "ok" and as_text("ok") == "ok"
    try:
        first_skill(json.dumps({"message": {"content": [{"type": "text", "text": "Failed to authenticate: x"}]}}))
        raise AssertionError("auth failure not detected")
    except RuntimeError:
        pass
    print("self-test ok")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--model")
    parser.add_argument("--max-turns", type=int, default=6)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    cases = json.loads((HERE / "triggers.json").read_text(encoding="utf-8"))
    jobs = [(c, r) for c in cases for r in range(args.runs)]
    with tempfile.TemporaryDirectory() as tmp:
        workdir = shutil.copytree(HERE / "fixture", pathlib.Path(tmp) / "notes-web")
        subprocess.run(["git", "init", "-q"], cwd=workdir, check=True)
        with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
            results = list(pool.map(lambda job: run_case(job[0]["prompt"], workdir, args.model, args.max_turns), jobs))
    fired = [skill for skill, _, _ in results]
    models = sorted({model for _, _, model in results})

    rows, hits = [], 0
    for (case, _), (skill, action, _) in zip(jobs, results):
        ok = skill == case["expect"]
        hits += ok
        result = "pass" if ok else f"FAIL (first action: {action})"
        rows.append(f"| {case['prompt'][:70]} | {case['expect'] or 'none'} | {skill or 'none'} | {result} |")
    positives = [ok for (c, _), s in zip(jobs, fired) for ok in [s == c["expect"]] if c["expect"]]
    negatives = [ok for (c, _), s in zip(jobs, fired) for ok in [s == c["expect"]] if not c["expect"]]
    summary = (f"{hits}/{len(jobs)} correct. Right skill fired: {sum(positives)}/{len(positives)}. "
               f"No skill on unrelated prompts: {sum(negatives)}/{len(negatives)}.")
    report = "\n".join([f"# Trigger eval, {datetime.date.today()}", "", summary,
                        f"Model: {' / '.join(models)}. Runs per case: {args.runs}. Max turns: {args.max_turns}.", "",
                        "| Prompt | Expected | Fired | Result |", "| --- | --- | --- | --- |", *rows, ""])
    out = HERE / "results" / f"triggers-{datetime.date.today()}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"written to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
