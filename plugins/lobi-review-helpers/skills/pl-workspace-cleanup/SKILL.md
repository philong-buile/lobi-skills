---
name: pl-workspace-cleanup
description: "Clean up a whole work folder full of repos: leftover git worktrees, local branches whose PR is merged or closed, stale folders, and Claude desktop sessions whose work is done. It takes an inventory first, proves each item is safe (clean, pushed, PR merged, or every local commit already in the base branch), asks once, then removes. Use when the user says \"clean up worktrees\", \"dọn worktree\", \"delete merged branches\", \"remove stale sessions\", \"clean up my work folder\" or \"xoá session đã merge\"."
---

# Workspace cleanup

Clean a folder that holds many repos, such as `C:\work` or `~/code`. The job has four phases. Do not remove anything before phase 3.

1. Inventory: worktrees, PR state, uncommitted work, local-only commits, sessions.
2. Plan: sort each item into **remove** or **keep**, with a reason.
3. Ask once, then remove worktrees and branches, then sessions.
4. Report what was removed, what was kept and why.

Removal is permanent. When an item is unclear, keep it and list it. Never guess.

## Evidence hook (before deleting sessions)

A session transcript can be the only record of work: research, reports and decisions that never became a PR. Before you delete sessions, check the user's CLAUDE.md for a line like this:

```
Cleanup evidence step: <agent or skill name>
```

If the line exists, run that agent or skill first and wait for it to finish. Delete sessions only after it reports success. If the line does not exist and the sessions belong to work the user may need later, ask whether to export anything before deleting.

## Phase 1: inventory

### Repos and worktrees

Find every repo, then list worktrees from each main repo. Worktrees under `.claude/worktrees/` sit deeper than a plain `find` reaches, so `git worktree list` is the reliable source.

```bash
find . -maxdepth 4 -type d -name .git -not -path '*/node_modules/*' | sed 's#/\.git$##'
git -C "$repo" worktree list --porcelain
```

For each non-main worktree, record:

- branch, or `(detached)`
- `git status --porcelain` line count
- upstream: `git rev-parse --abbrev-ref '@{u}'`
- commits that exist on no remote: `git rev-list --count HEAD --not --remotes`
- last commit date: `git log -1 --format=%cs`
- origin slug, from `git remote get-url origin`

Run `git fetch --prune origin` once per repo first.

### PR state

Get the PR state from GitHub, per repo:

```bash
gh pr list -R owner/repo --state all --limit 500 --json headRefName,state,number
```

- One `gh` account often cannot see every org. If you get `Could not resolve to a Repository`, run `gh auth status` to see the accounts, then retry with `GH_TOKEN=$(gh auth token -u <other-account>)`.
- Do not trust the PR state cached in the session list. It can say OPEN after the PR was merged. Use `gh`.
- `jq` may not be installed. Use `gh --template` or `--jq`, or Python.

### Uncommitted work

A dirty worktree is not always real work. Look at the files:

- **Junk:** untracked build output, screenshots and tool caches, for example `node_modules/`, `.pr-shots/`, `.impeccable/`, `public/<vendor>/` copies. These are safe to lose.
- **Real work:** modified tracked files, new source files, docs, reports. Keep the worktree unless the user says otherwise.

### Local-only commits

A squash-merged PR leaves the branch with commits that no remote has. Check whether their content is already in the base branch:

```bash
git cherry origin/<base> HEAD   # every line starts with "-": all patches are already in base
```

If every line is `-`, the commits are safe to drop. If any line is `+`, keep the branch.

### Sessions (Claude desktop app)

Use `mcp__ccd_session_mgmt__list_sessions` with `include_archived: true` and a high `limit`. The result is often too large for one read, so save it and summarize it with a script: id, archived, running, last activity, PR state and number, cwd, title.

On Windows, run Python as `python -X utf8 -I`. Without `-X utf8`, printing Vietnamese or Japanese titles fails with `UnicodeEncodeError: 'cp932'`.

## Phase 2: plan

**Remove a worktree** only when it has no real uncommitted work and one of these is true:

- Its PR is MERGED or CLOSED, and `git cherry` shows nothing new.
- It has no PR, and the branch has no commits outside the base branch (`git rev-list --count HEAD --not origin/<base>` is 0).

**Keep a worktree** when:

- its PR is OPEN
- it has real uncommitted changes
- it has commits that exist only locally and are not in the base branch

**Remove a session** when it is not running and:

- its PR is MERGED or CLOSED (checked with `gh`), or
- it is archived and has no PR.

**Keep a session** when it is running, its PR is open, or it is active with no PR. Never delete the current session.

Show the plan as short grouped lists with PR numbers. Name every kept item that has real uncommitted work, so the user can decide. Then ask one question with `AskUserQuestion`. Offer three options: the plan as proposed, worktrees only, and the plan plus the old dirty worktrees.

## Phase 3: remove

### Worktrees and branches

```bash
b=$(git -C "$wt" symbolic-ref --short HEAD 2>/dev/null)
git -C "$repo" worktree remove --force "$wt" && [ -n "$b" ] && git -C "$repo" branch -D "$b"
git -C "$repo" worktree prune
```

- Use `branch -D`, not `-d`. Squash merges make `-d` refuse. Phase 1 already proved the branch is safe.
- Worktrees that contain `node_modules` are slow to remove. Run the loop in the background and do other work.
- On Windows, `worktree remove` can fail with `Directory not empty` after git has already unregistered the worktree. Delete the leftover folder with `Remove-Item -LiteralPath <path> -Recurse -Force`. This can also take minutes.
- After the worktrees, delete local branches whose PR is MERGED or CLOSED, are not checked out anywhere, and have no commits outside the remotes. Skip and list the rest.
- Do not delete remote branches unless the user asks.

When an executor agent such as `lobi-agent-cleanup` is installed, you can give it the exact approved list instead of running the loop yourself.

### Sessions

`mcp__ccd_session_mgmt__delete_session` takes at most 25 ids per call and shows the user an approval card for each call. Send batches of 25.

Read the skip reasons in each result:

- **Kept for the user (pinned or in use):** leave it.
- **Worktree could not be checked:** this usually means you already removed the worktree. Run `git worktree list` and check the folder. If the PR is merged and nothing real is left, tell the user which sessions are affected, then retry with `force_worktree_cleanup: true`.

## Phase 4: report

Give counts and names:

- worktrees removed, branches deleted, sessions deleted
- skipped items and why
- kept items with real uncommitted work, with paths, so the user can decide later

Keep the report short. Do not paste raw git output.
