---
name: pl-repo-reviewer
description: >-
  Build, refresh or run a repo-specific reviewer bot: a read-only Claude Code subagent at
  .claude/agents/<repo>-reviewer.md that checks a diff only against the rules this one repo has
  (its trust boundaries, data invariants, deliberate exceptions, guard tests, scripts that write
  shared data, docs rules), every rule backed by file:line evidence. It reviews its own prompt
  against the code, dry-runs it on a merged PR, and wires it into the repo's PR flow so every PR
  gets it. Use when the user says "create a reviewer bot for this repo", "make a review agent for
  this project", "a bot that checks our house rules on every PR", "refresh the reviewer agent",
  "tạo bot review cho repo này", or when another skill reaches PR review in a repo that already
  has a `.claude/agents/*-reviewer.md`.
---

# Repo reviewer bot: one per repo, run on every PR

Generic reviewers know the language. They do not know which endpoint is this repo's real trust boundary, that its audit log is append-only, or that one cleanup script deletes that log on purpose behind a flag. This skill writes those rules down once, as a subagent with evidence for each rule, and makes every PR run it.

**Authorization.** Creating the bot means writing one agent file plus a few routing lines, shipped through the repo's normal PR flow (`pl-ship-change` rules: draft PR, merge only when asked). Running the bot is read-only.

## Mode A: run the bot on a PR

1. **Find it:** `.claude/agents/*-reviewer.md` in the repo. None: go to Mode B, or say there is none.
2. **Spawn it by name** on the PR: agent type `<repo>-reviewer`, prompt `Review PR #<n>` (or the branch).
   - The agent type usually shows up once the file is in the session's own checkout. A file that exists only on a branch in another worktree is not visible, and a repo's first agent may need a new session. If the type is not listed, spawn a general-purpose agent with the prompt "Follow the instructions in `<path>` after the front matter. Read-only: do not edit files or run scripts. Review PR #<n>." The fallback does not get the agent's `tools:` limit, so the read-only line matters.
3. **Run it beside the generic review** (the `code-review` skill or the repo's own reviewer), never instead of it.
4. **Check each finding against the code before acting**, then triage like `pl-ship-change` §5: fix, skip with a reason, or a follow-up.

## Mode B: create or refresh the bot

### 1. Read the house rules and the incident history

- The same sources as `pl-ship-change` §0: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, the PR template, CI.
- What already went wrong: `git log --oneline --grep='fix\|revert\|incident\|outage' -i | head -40`, plus postmortems or status pages in `docs/`. A rule that once caused an outage is worth more than ten style rules.

### 2. Map the invariants, with evidence

Run read-only explore agents in parallel, one per component. Ask each one for rules with `path:line` evidence, with anything unconfirmed marked UNCONFIRMED:

| Ask for | Example |
|---|---|
| Every trust boundary, not only the obvious one | webhook signature checks, token-gated admin or data routes, session minting, tenant or household scoping |
| Data invariants | append-only logs, the one key or ID builder, TTLs, atomic operations, encryption at rest |
| **Deliberate exceptions** | the script that breaks a rule on purpose, and the flag that guards it |
| Guard tests, and how each one picks its files | scans every file, or reads a list? An allowlist that new files must join? |
| Scripts that write shared or production data | their names and their confirm flags (`--yes`, `--force`, dry-run by default) |
| Secrets and personal data | where secrets load, what fails closed when one is missing, how personal data is stored and deleted |
| Silent-success history | paths that reported success without doing the work |
| Docs and release rules | which page owns what, title codes, required PR sections |

Keep only what a generic reviewer for this language would not know. Drop style, formatting and anything a linter already enforces.

### 3. Write the agent

Copy [`templates/reviewer-agent.md`](templates/reviewer-agent.md) to `.claude/agents/<repo>-reviewer.md`. Fill in `<repo>`, `<base>`, the description nouns, the scripts sentence and the invariants. Leave `<n>`, `path:line` and `<fix>` as they are: the bot fills those in at run time. Rules for the invariants:

- **Every rule names the file** that enforces or embodies it.
- **Name the deliberate exceptions.** An absolute rule that the code already breaks on purpose gives a false BLOCKER on every PR that touches that file, and after that people stop reading the bot.
- **Forbid running things.** `Bash` lets the bot run anything. The template forbids project scripts, and you name the ones that write shared or production data.
- **Keep it short:** 8 to 12 invariants, under about 80 lines. A long prompt gets skimmed.

### 4. Review the prompt against the code

Run the `code-review` skill (or a reviewer subagent) on the new agent file, with this brief: for each rule, grep for code that already breaks it; for each mechanism claim, open the file it names. Fix what it finds. A first draft usually states several rules more absolutely than the code allows.

### 5. Dry-run it on merged code

Run the bot (Mode A) on the most recent merged PR that touched the riskiest component.

- **Spot-check at least the top 3 findings yourself.** Real findings on merged code prove that the bot catches things.
- **Real findings go to a follow-up task**, not into this PR.
- **Zero findings on a risky PR** means the rules are too vague. Tighten them and run it again.

### 6. Wire it into every PR

- **Routing line:** add one line to the review section of the repo's `CLAUDE.md` (or `AGENTS.md`). It names the agent and its path, and says it runs beside the generic review, not instead.
- **The repo's own ship or PR skill**, if it has one: add the agent to its review stage, marked as always run.
- **No repo-local PR skill:** nothing to add. `pl-ship-change` §5 runs any `.claude/agents/*-reviewer.md` it finds.

### 7. Ship it

Use the repo's flow (`pl-ship-change`). The PR body says what the bot checks, lists the dry-run findings with the spot-check result, and says "no runtime change".

## Refresh

Edit the bot, with evidence, through the same ship flow when:
- a PR adds a trust boundary, an invariant or a deliberate exception;
- the bot raises the same false positive twice;
- a rule's file moves.

## Report

- the agent path and the PR link with its state;
- the invariants, one line each;
- the prompt review: findings, and how many were fixed;
- the dry run: which PR, the findings, and how many you confirmed real;
- what was not verified.
