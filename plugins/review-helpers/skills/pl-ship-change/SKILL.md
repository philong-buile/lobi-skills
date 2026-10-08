---
name: pl-ship-change
description: >-
  Ship one feature or fix end to end in any repo:
  plan, branch, implement, verify (unit tests, a smoke test, an end-to-end run where the change
  lives), self-review, commit, push, open a short PR with a smoke-test guide, review the PR, and
  merge only when asked. It reads the repo's own rules (CLAUDE.md, AGENTS.md, CONTRIBUTING, the PR
  template, CI) for commands, branch names, PR format and merge method. Use when the user says
  "ship this feature", "ship this fix", "implement and open a PR", "take this from plan to PR",
  "full ship", or "fix #N and merge it".
---

# Ship a change: plan to merged PR

One change, one branch, one PR. This skill is the order of operations. The repo's own rules decide the details.

**Authorization.** Invoking this skill is the user's request to commit, push and open a **draft** PR for this one change. It does **not** authorize:
- merging, unless the user says so (§8);
- deploying to shared or production environments;
- posting review comments;
- touching other PRs or branches.

## 0. Read the house rules

Read these before anything else:

| Source | What to take from it |
|---|---|
| `CLAUDE.md` (user and project), `AGENTS.md`, `CONTRIBUTING.md` | build, test and format commands; files you must not touch; PR rules |
| `.github/pull_request_template.md` | the PR body structure. It replaces the default in §6. |
| `.github/workflows/*` | which checks gate a merge |
| `gh repo view --json defaultBranchRef` | the base branch, unless the house rules name another, such as `develop` |
| `gh pr list --state merged --limit 10 --json headRefName,title,body` | branch naming, title style, PR language, how long a body is |
| recent merge commits on the base | merge method: merge, squash or rebase |

If the rules disagree with this skill, the repo wins.

## 1. Plan

1. **Restate the goal** in one line, plus the observable result that proves it is done.
2. **Explore the code paths the change touches.**
   - If a code-intelligence tool is available (for example GitNexus), run impact analysis on every symbol you plan to change.
   - Check for an open PR or issue that already covers the change.
3. **Write the plan:**
   - files to change;
   - tests to add;
   - how to verify (§4);
   - what is out of scope;
   - the docs, config templates or env examples the change implies.
4. **Gate.** For a small, low-risk fix, state the plan and continue. Wait for the user's OK when any of these is true:
   - the change spans more than one component;
   - it touches auth, payments or billing, data deletion, writes to user files, or a protocol between processes;
   - it changes user-visible behavior nobody specified;
   - impact analysis reports high risk.

## 2. Branch

- **Start from a fresh base:** `git fetch origin <base>`, then `git switch -c <prefix>/<type>/<slug> origin/<base>`.
- **Worktrees:** if the repo works with one worktree per PR (`git worktree list` shows several), add a worktree instead.
- **Never work on the base branch.** Never switch a checkout that has uncommitted changes.
- **Stacked work:** use a stacked base only when the change depends on an open PR. The PR then targets that PR's branch.

## 3. Implement

- **Make the smallest change that meets the goal.** Match the surrounding code. No drive-by refactors; note them as follow-ups.
- **Write unit tests next to the change.** For a bug fix, write the test so it fails without the fix.
- **Update in the same change** whatever the repo keeps in sync with code:
  - the README of the component;
  - env templates and config examples;
  - instruction files that an agent reads at runtime.
- **Format** with the tool the repo uses for that path.
- **Never touch** lockfiles (unless dependencies change), CI workflows, secrets or `.env` files, unless the task is about them.

## 4. Verify

1. **Run the narrowest check that proves the change,** then the suite of the area you touched.
2. **If a suite cannot run locally** (missing toolchain or platform), say so and let CI be the proof. Never claim a run that did not happen.
3. **Then exercise the behavior where users meet it:**
   - **UI:** run the app (the `run` skill, or the repo's dev command) and drive the changed screen in a browser at desktop and mobile widths. Take the screenshots for the PR in the same pass.
   - **API or backend:** run it locally and call the changed endpoint with real input, including one failure case.
   - **CLI or library:** run the real command or a small script against a sample input.
   - **Integrations** (a host app, a device, a third-party service): use the repo's documented end-to-end recipe. Use a local or scratch environment, never shared or production data.
   - **Pure refactor:** the test suites are the proof. Say so.
4. **Record what ran, with numbers, and what did not.** The PR's Tests section comes from this record.

## 5. Self-review before commit

1. Read the full diff against the base as a reviewer would.
2. Run an independent review of the diff, either with the `code-review` skill or one reviewer subagent per touched component, and fix the real defects. Re-run the failing check after each fix.
3. Triage the remaining findings:

| Finding | Action |
|---|---|
| A caller not updated, a broken flow, a missing error path | Fix it in this PR. |
| A changed behavior with no test | Add the test. |
| The PR description claims less than the diff does | Fix the description. |
| A pre-existing issue the diff only touches | Leave it, and list it as a follow-up. |

Report what you fixed and what you dismissed, with reasons.

## 6. Commit, push, open the PR

1. **Commit** in the repo's message style (conventional commits if recent history uses them). The body says *why*. Stage paths explicitly.
2. **Push:** `git push -u origin <branch>`.
3. **Open the PR:** `gh pr create --draft --base <base> --title "<title>" --body-file <file>`.

The body is **short**: enough for a reviewer to understand and verify the change, nothing more. Write it in the language or languages the house rules ask for. Use the repo's template if it has one; otherwise:

```markdown
## Summary
<1-3 sentences: the problem and the fix.>

## Changes
- <file or area>: <what changed>

## Tests
- <suite>: <N passed>
- <smoke or e2e run: what was exercised and the result>
- <anything not run, and why>

## Smoke test guide
1. <how to run this branch>
2. <the one behavior this PR changes, and the decisive thing to see>
3. <one adjacent regression check, only if plausible>

<UI change: screenshots, each with a one-line caption>
```

Rules for the smoke test guide:
- Aim for 5 to 10 minutes of reviewer time, usually 2 or 3 cases.
- Every step asserts something this diff owns.
- Add no tool-attribution footer unless the repo wants one.

Afterwards:
- In the Claude desktop app, turn on Auto-fix (`pl-pr-autofix`) for the PR.
- Do not poll CI in a loop.

## 7. Review the PR

- Re-read the PR body against the final diff: test counts, smoke steps, screenshots. Update it with `gh pr edit --body-file`.
- Check `gh pr checks <N>` once. Fix the failures this branch caused. Report a failure caused by something outside the branch instead of working around it.
- Mark the PR ready with `gh pr ready` only when the user asks for ready or merge.

## 8. Merge (only when asked)

Merge only when all of these hold:
- the user asked to merge;
- the required checks are green;
- no blocker findings remain open;
- the PR is mergeable;
- the required approvals exist. You cannot approve your own PR; if a review from someone else is required, stop and say so.

```bash
gh pr merge <N> --<merge|squash|rebase> --match-head-commit <reviewed sha>
```

Use the repo's merge method. `--match-head-commit` refuses the merge if new commits arrived after your review. Then delete the branch and the worktree you created. Do not deploy unless asked.

## 9. Report

Reply in a few lines:
- the PR link and its state;
- what changed;
- what was verified, with numbers;
- what was not verified;
- follow-ups;
- anything left running, such as dev servers or local services. Stop those, or say why they are still running.

## Stop and ask when

- The plan gate in §1 applies.
- A check fails for a reason outside the change.
- Verifying needs shared or production environments, real user data, or credentials.
- The diff grows beyond the plan.
