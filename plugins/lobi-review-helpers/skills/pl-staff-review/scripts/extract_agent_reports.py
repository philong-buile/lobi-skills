"""Recover subagent reports from a Claude Code session transcript.

Use when an Agent task's .output file is empty after it finished. Reads every
<task-notification> in the session JSONL and writes each finished agent's
<result> to <outdir>/NN-<slug>.md, numbered in order of first completion.
If an agent notified more than once (resumed), the last result wins.

Usage:
  python extract_agent_reports.py <session.jsonl | project-dir> <outdir> [--match TEXT]
  python extract_agent_reports.py --self-test

A project dir (~/.claude/projects/<slug>/) uses its newest *.jsonl, which is
normally the current session. --match keeps only agents whose name contains TEXT.
"""

import html
import json
import pathlib
import re
import sys

SUMMARY = re.compile(r'<summary>Agent "(.+?)" finished</summary>')
RESULT = re.compile(r"<result>(.*)</result>", re.S)


def texts(obj):
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                for key in ("text", "content"):
                    if isinstance(block.get(key), str):
                        yield block[key]


def extract(jsonl, match=None):
    found = {}  # dict keeps first-seen order; later results overwrite the value
    for line in jsonl.open(encoding="utf-8"):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        for text in texts(obj):
            for note in text.split("<task-notification>")[1:]:
                s, r = SUMMARY.search(note), RESULT.search(note)
                if s and r and (match is None or match in s.group(1)):
                    found[s.group(1)] = html.unescape(r.group(1).strip())
    return found


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "agent"


def write(found, outdir, source):
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, (name, body) in enumerate(found.items(), 1):
        path = outdir / f"{i:02d}-{slug(name)}.md"
        header = f"<!-- Raw subagent report: {name}. Source: {source.name}. -->\n\n"
        path.write_text(header + body + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def resolve(src):
    if src.is_dir():
        files = sorted(src.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        if not files:
            sys.exit(f"no *.jsonl in {src}")
        return files[-1]
    return src


def self_test():
    import tempfile

    def note(name, body):
        return (f'<task-notification><summary>Agent "{name}" finished</summary>'
                f"<result>{body}</result></task-notification>")

    lines = [
        {"message": {"content": note("Backend review", "old &amp; stale")}},
        {"message": {"content": [{"type": "text", "text": note("Security review", "a &lt;b&gt;")}]}},
        {"message": {"content": note("Backend review", "new")}},
        {"message": {"content": "no notification here"}},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "s.jsonl"
        src.write_text("\n".join(json.dumps(x) for x in lines) + "\nnot json\n", encoding="utf-8")
        found = extract(src)
        assert list(found) == ["Backend review", "Security review"], found
        assert found["Backend review"] == "new"
        assert found["Security review"] == "a <b>"
        assert list(extract(src, "Security")) == ["Security review"]
        paths = write(found, pathlib.Path(tmp) / "out", src)
        assert [p.name for p in paths] == ["01-backend-review.md", "02-security-review.md"]
        assert resolve(pathlib.Path(tmp)) == src
    print("self-test ok")


def main(argv):
    if argv[1:] == ["--self-test"]:
        return self_test()
    if len(argv) not in (3, 5) or (len(argv) == 5 and argv[3] != "--match"):
        sys.exit(__doc__)
    src = resolve(pathlib.Path(argv[1]).expanduser())
    found = extract(src, argv[4] if len(argv) == 5 else None)
    if not found:
        sys.exit(f"no finished agent reports in {src}")
    for path in write(found, pathlib.Path(argv[2]).expanduser(), src):
        print(path)


if __name__ == "__main__":
    main(sys.argv)
