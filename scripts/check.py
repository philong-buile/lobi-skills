"""Repository checks for lobi-skills. Standard library only; runs in CI and locally.

    python scripts/check.py

Checks:
  1. marketplace.json and every plugin.json parse, names match, versions are semver,
     and every plugin source folder exists.
  2. Every skills/<name>/SKILL.md has front matter with a matching `name` and a
     non-empty `description` of at most 1024 characters.
  3. Every relative link and image in every Markdown file points at a file that exists.
  4. README files contain no em or en dashes.
  5. Bundled scripts pass their own self-tests.
Exit code 1 if anything fails.
"""

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
LINK = re.compile(r"\]\(([^)\s]+)\)|(?:src|srcset|href)=\"([^\"]+)\"")
failures, passed = [], 0


def check(ok, message):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(message)


def front_matter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.S)
    if not match:
        return {}
    fields, key = {}, None
    for line in match.group(1).splitlines():
        top = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            fields[key] = "" if value in (">-", ">", "|", "|-") else value.strip('"')
        elif key and line.startswith(" "):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def check_manifests():
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    for entry in market["plugins"]:
        folder = ROOT / entry["source"]
        check(folder.is_dir(), f"marketplace: source folder missing for {entry['name']}")
        manifest = folder / ".claude-plugin/plugin.json"
        check(manifest.is_file(), f"{entry['name']}: plugin.json missing")
        if manifest.is_file():
            plugin = json.loads(manifest.read_text(encoding="utf-8"))
            check(plugin.get("name") == entry["name"], f"{entry['name']}: plugin.json name mismatch")
            check(bool(SEMVER.match(plugin.get("version", ""))), f"{entry['name']}: version is not semver")


def check_skills():
    for skill in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        meta = front_matter(skill.read_text(encoding="utf-8"))
        where = skill.relative_to(ROOT).as_posix()
        check(meta.get("name") == skill.parent.name, f"{where}: front matter name != folder name")
        description = meta.get("description", "")
        check(0 < len(description) <= 1024, f"{where}: description empty or longer than 1024 chars")


def check_links():
    for md in sorted(ROOT.rglob("*.md")):
        if {".git", "results", "templates"} & set(md.parts):  # templates link into the target repo
            continue
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```|`[^`\n]*`", "", text, flags=re.S)  # links inside code are examples
        for match in LINK.finditer(text):
            target = (match.group(1) or match.group(2)).split("#")[0]
            if not target or re.match(r"^[a-z]+:", target) or "{{" in target or "<" in target:
                continue
            check((md.parent / target).exists(), f"{md.relative_to(ROOT).as_posix()}: broken link {target}")


def check_dashes():
    for md in sorted(ROOT.rglob("README.md")):
        if ".git" in md.parts:
            continue
        bad = [n for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1) if "—" in line or "–" in line]
        check(not bad, f"{md.relative_to(ROOT).as_posix()}: em/en dash on lines {bad}")


def check_self_tests():
    for script in sorted([*ROOT.glob("plugins/*/skills/*/scripts/*.py"), *ROOT.glob("evals/*.py")]):
        if "--self-test" not in script.read_text(encoding="utf-8"):
            continue
        run = subprocess.run([sys.executable, str(script), "--self-test"], capture_output=True, text=True)
        check(run.returncode == 0, f"{script.relative_to(ROOT).as_posix()}: self-test failed\n{run.stdout}{run.stderr}")


if __name__ == "__main__":
    for step in (check_manifests, check_skills, check_links, check_dashes, check_self_tests):
        step()
    for message in failures:
        print("FAIL", message)
    print(f"{passed} checks passed, {len(failures)} failed")
    sys.exit(1 if failures else 0)
