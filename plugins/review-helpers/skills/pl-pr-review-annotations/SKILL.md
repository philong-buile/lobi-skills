---
name: pl-pr-review-annotations
description: "Use when the user asks you to annotate a pull request with reviewer-facing FYI comments to help prioritize a large diff. Examples: \"Add FYI comments on this PR\", \"Annotate PR #42 for reviewers\", \"Mark the important parts of this PR\""
---

# PR Review Annotations

## Goal

Help reviewers quickly understand large PRs by adding simple, short, review-friendly comments directly on the Git PR review side (NOT modifying source code).

## Workflow

1. Resolve the PR. Run `gh pr view --json number,headRefOid,baseRefName,baseRefOid,files` and capture `headRefOid` (commit SHA) + the changed file list.
2. Get the diff. Run `gh pr diff <number>` and read every hunk. Group hunks into Important / Medium / Minor per the Priority Labels below. Skip hunks that don't warrant an FYI.
3. Post all FYI comments in one atomic review. Build a JSON file `comments.json` shaped like:

   `[{ "path": "src/foo.ts", "line": 42, "side": "RIGHT", "body": "[FYI] Important Changes: ..." }, ...]`

   Then:

   `gh api -X POST repos/{owner}/{repo}/pulls/<number>/reviews -f commit_id=<headRefOid> -f event=COMMENT -F comments=@comments.json`

4. For a single overall PR comment instead of inline ones, use `gh pr comment <number> --body "..."`.

> `path` is repo-relative. `line` is the line number in the new file (or in the old file when `side` is `LEFT`). `side: "RIGHT"` for added/modified lines, `side: "LEFT"` for deleted ones.

## Instructions

Please review the PR changes again and identify important areas based on impact level.

For each important area, create short review comments directly in Git PR comments (not code comments).

### Comment Rules

- Use very simple, plain English — words a beginner can understand
- Pick short, common words over long or technical ones
  - "checks" not "validation"
  - "makes sure" not "ensures"
  - "uses" not "leverages/utilizes"
  - "old" not "legacy/deprecated"
  - "stops" not "prevents"
  - "talks to" not "communicates with"
  - "many places" not "multiple modules"
  - "works" not "functions/operates"
- Avoid jargon when a plain word works. If a tech term is needed (e.g. "API", "cache"), keep it but explain the *effect* in plain words.
- Keep comments short (1–3 short sentences max)
- Focus on helping reviewers prioritize review effort
- Explain *why the change matters*, not how it works inside
- Do NOT rewrite code or suggest code changes unless requested
- Add comments only to meaningful locations

### Priority Labels

**[FYI] Important Changes**

Use for:

- Core logic changes
- Architecture changes
- Behavior changes
- Security/performance-related updates
- Changes affecting multiple modules
- High-risk modifications

Format example:

> [FYI] Important Changes: This changes how users pick things by hand. Look here first — it changes how the tool runs and how pages get picked.

**[FYI] Medium Changes**

Use for:

- Refactoring
- Validation improvements
- Error handling updates
- API adjustments
- Test expansion

Format example:

> [FYI] Medium Changes: Added more checks here to catch bad input and make the code less likely to break.

**[FYI] Minor Changes**

Use for:

- Logging
- Comments/docstrings
- Naming cleanup
- Small fixes
- Non-functional updates

Format example:

> [FYI] Minor Changes: Added logs here so it's easier to see what went wrong when things fail.

## Main Intention

The goal is NOT to explain every change.

The goal is to:

1. Help reviewers focus on high-impact areas first
2. Reduce reviewer fatigue in large PRs
3. Make critical changes easier to notice
4. Speed up review without hiding important risks

When uncertain, prefer fewer comments but higher quality comments.
