# review-helpers

Claude Code skills for shipping changes and reviewing code and whole systems.

## Skills

### `pl-ship-change`

Takes one feature or fix from plan to merged PR, in any repo. It first reads the repo's own rules: CLAUDE.md, AGENTS.md, CONTRIBUTING, the PR template, CI and recent merged PRs. Those set the commands, branch names, PR format and merge method. Then it works through these steps:

1. Plans, and waits for your OK on risky or multi-component changes.
2. Branches from a fresh base and makes the smallest change, with tests.
3. Verifies with unit tests, a smoke test and an end-to-end run where the change lives.
4. Self-reviews the diff, plus the repo's reviewer bot when there is one (`pl-repo-reviewer`), then opens a short draft PR with a 5 to 10 minute smoke-test guide.
5. Reviews its own PR.
6. Merges only when you ask and the checks and approvals allow it.

**Trigger phrases**

- "Ship this fix"
- "Implement this and open a PR"
- "Fix #123 and merge it"

**Requires** `gh` (GitHub CLI), authenticated in the current shell.

### `pl-repo-reviewer`

Builds a reviewer bot for one repo and makes every PR run it. The bot is a read-only Claude Code subagent at `.claude/agents/<repo>-reviewer.md`. It checks a diff only against the rules a generic reviewer cannot know: the repo's trust boundaries, data invariants, guard tests, scripts that write shared data, and docs rules. The steps:

1. Reads the house rules and the fix and revert history.
2. Maps the invariants with parallel read-only agents. Every rule needs `file:line` evidence, and the deliberate exceptions are named.
3. Writes the agent from [a template](./skills/pl-repo-reviewer/templates/reviewer-agent.md): 8 to 12 rules, a ban on running project scripts, and one line per finding.
4. Reviews the prompt against the code, so no rule is stated more absolutely than the code allows.
5. Dry-runs the bot on a merged PR and spot-checks its top findings.
6. Adds a routing line to `CLAUDE.md` and to the repo's own ship skill, if it has one. `pl-ship-change` runs the bot automatically.
7. Ships it through the repo's PR flow.

On later PRs, it spawns the bot beside the generic review and checks each finding before acting.

**Trigger phrases**

- "Create a reviewer bot for this repo"
- "A bot that checks our house rules on every PR"
- "Refresh the reviewer agent"

**Requires** `gh` (GitHub CLI), authenticated in the current shell.

### `pl-pr-review-annotations`

Adds simple `[FYI]` triage comments to a PR, so reviewers can quickly tell which hunks matter. It uses three priority bands:

- `[FYI] Important Changes`: core logic, architecture, behavior, security or performance, changes across many modules.
- `[FYI] Medium Changes`: refactors, validation, error handling, API tweaks, more tests.
- `[FYI] Minor Changes`: logging, docs, naming, small fixes.

It does not modify source code. It posts the comments as one PR review through `gh api`.

**Trigger phrases**

- "Add FYI comments on this PR"
- "Annotate PR #42 for reviewers"
- "Mark the important parts of this PR"

**Requires** `gh` (GitHub CLI), authenticated in the current shell.

### `pl-pr-review-request`

Drafts the Slack message that asks a reviewer to look at a set of PRs. It works like this:

- fetches each PR's real title, URL, draft state and CI status from `gh`;
- orders stacked PRs base to head;
- writes a short plain-English summary per PR from its description.

The tone is a coworker asking a senior colleague: simple English, no "Sir", no exclamation marks. Two optional CLAUDE.md lines configure it:

```
Review-request reviewer: https://<workspace>.slack.com/team/<member-id>
Review-request greeting: お疲れ様です。
```

It only drafts the message in a code block for you to paste. It never sends anything and never changes PR state.

**Trigger phrases**

- "Draft a review request for these PRs"
- "Message my lead the PRs are ready"
- "/review-helpers:pl-pr-review-request 118 119 121"

**Requires** `gh` (GitHub CLI), authenticated in the current shell.

### `pl-pr-autofix`

Turns on Auto-fix in the Claude desktop app for a PR right after it is opened. Auto-fix wakes the session on CI failures, merge conflicts and review comments.

You choose the covered repos with one line in your CLAUDE.md:

```
Auto-fix repos: owner/repo-a, owner/repo-b
```

- **Covered repos:** Auto-fix turns on without asking, and CI failures and conflicts are fixed and pushed.
- **Other repos:** it only offers Auto-fix.
- **Review comments:** they are triaged, and nothing is posted on GitHub without asking.

Desktop app only, because it needs the `ccd_pr` tools. It never turns on auto-merge.

**Trigger phrases**

- Runs automatically after `gh pr create`
- "Turn on auto-fix"
- "Watch this PR's CI"

### `pl-staff-review`

A critical staff/principal-level review of a whole system. It ranks improvements by impact per engineering hour, for a deadline such as a salary or promotion review. It covers code, related infra repos, open PRs and PoCs, CI/CD, security, UX and the open-source ecosystem. The steps:

1. Makes a clean worktree of the default branch.
2. Runs six read-only review lanes in parallel: backend, agent/MCP layer, frontend and host, infra and CI/CD, security, and ecosystem web research.
3. Re-checks in the code every claim that drives a priority.
4. Scores each candidate with `Impact × Visibility ÷ (Effort + Risk/2)` and sorts it into Tier S, A, B or C.
5. Writes 3 to 5 killer projects, a dated 4-phase roadmap, the metrics to start collecting, and what to show your manager.

The report and the raw lane reports are saved to a folder outside git. The skill also handles follow-up questions such as "should we replace our self-hosted X with managed Y?".

It is read-only for the reviewed repos. It never edits, commits or pushes there, never calls cloud APIs, and never prints secret values. If a subagent's `.output` file is empty, `scripts/extract_agent_reports.py` recovers the lane report from the session transcript.

**Trigger phrases**

- "Do a staff-level review of this project"
- "What should I build before my performance review?"
- "Should we drop our self-hosted RAG and use a managed service?"

**Requires** `gh` (GitHub CLI), authenticated in the current shell. The ecosystem lane needs web search.

## Agents

Subagents that ship with the plugin, available in every repo as `review-helpers:<name>`. Skills run inside your conversation; an agent runs separately with its own context and tool limits and returns only its result.

### `docs-drift-checker`

Read-only. Takes each factual claim in the READMEs, docs pages, user-facing policy pages and agent instruction files, checks it against the code at the current base, and reports `doc:line | code:line | severity | what is wrong`. A broken promise to users, such as a deletion page that says more than the code deletes, is HIGH. `pl-ship-change` runs it when a diff changes documented behaviour.

### `finding-to-test`

Turns one confirmed finding into one regression test that fails on the current code, in the repo's own runner and style. It writes test files only, never the fix, so the person fixing the bug cannot bend the test to the fix. If the test passes, it reports that the finding is wrong or already fixed, and deletes the test.

## Install

```
/plugin marketplace add philong-buile/lobi-skills
/plugin install review-helpers@lobi-skills
```

Invoke as `/review-helpers:pl-ship-change`, `/review-helpers:pl-repo-reviewer`, `/review-helpers:pl-pr-review-annotations`, `/review-helpers:pl-pr-review-request`, `/review-helpers:pl-pr-autofix` or `/review-helpers:pl-staff-review` from any repo.
