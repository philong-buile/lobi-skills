---
name: pl-staff-review
description: "Critical staff/principal-level review of a whole software system (code, related infra repos, open PRs and PoCs, CI/CD, security, UX, open-source ecosystem). Produces a ranked, measurable roadmap to a deadline such as a salary or promotion review. Runs parallel read-only review lanes on a clean checkout, re-checks the claims that drive priorities, scores each improvement with Impact × Visibility ÷ (Effort + Risk/2), picks 3–5 killer projects, and saves the report outside git. Use when the user asks for a \"staff-level review\", a \"principal engineer review of the project\", \"what should I build before my performance review\", a \"promotion roadmap\", or \"career impact per engineering hour\". Also use for follow-ups such as \"should we replace our self-hosted X with managed service Y\"."
---

# Staff-level system review and ranked roadmap

## What this produces

The review finds the 3–5 improvements with the most business and career impact per engineering hour. It proves each one with file:line evidence and plans them to a dated deadline. Be critical, not polite. Prefer measurable work over cosmetic work.

## Hard rules

- **Read-only.** Never edit, commit or push in the reviewed repos.
- **No live systems.** Never call cloud APIs (AWS, GCP, Azure), run `terraform plan` or `apply`, or run exploits against a live system.
- **No secret values.** Report a secret as file path + key name + "committed or not". Never print the value.
- Pass the user's standing restrictions into every lane prompt. Look for these in CLAUDE.md and memory:
  - tools that need per-repo consent;
  - secret files that must not be read;
  - "never commit" rules.

## 0. Inputs

Find each input from the request, the repo, CLAUDE.md and memory. Ask only for what blocks the review.

| Input | How to find it |
|---|---|
| Repos in scope | Main repo, plus related repos (infra, sibling services). Use `git remote -v`, sibling folders, and `gh repo list <owner>`. |
| Baseline branch | The default branch: `gh repo view --json defaultBranchRef`. Review that branch, not the user's current feature branch. |
| Deadline and audience | For example "performance review in 3 months, audience: manager". If missing, ask once. Default: 3 months from today, audience "manager". |
| Open work | Open PRs and PoCs: `gh pr list --state open --limit 50`. Recent merged PRs: `gh pr list --state merged --limit 60`. |
| Background notes | Memory notes about this repo. Give each lane the file names that apply to it. Tell lanes to verify the notes, because notes go stale. |

If the user pasted a long brief with its own sections and deliverables, keep their list. It overrides `references/report-outline.md`.

## 1. Make a clean checkout

```bash
git -C <repo> fetch origin
git -C <repo> -c core.longpaths=true worktree add --detach <short-path> origin/<default-branch>
git -C <short-path> rev-parse --short HEAD
```

- The last command gives the SHA. Record it for the report.
- On Windows, keep `<short-path>` short, for example a sibling folder of the repo. A path under a temp or scratchpad folder can fail with `Filename too long`.
- For a related repo (for example infra) that is checked out on a feature branch, treat `origin/main` as the deployed baseline. Read the branch difference with `git diff origin/main --stat`.

## 2. Plan the lanes

Use one lane for each area that a separate expert would review. The default is six lanes. Prompt templates are in `references/lane-prompts.md`.

1. **Backend:** API, data, LLM, RAG, concurrency.
2. **Agent / tool layer:** MCP, the agent loop, and workflows that change user data.
3. **Frontend + host integration:** UI, desktop or web host, IPC.
4. **Infra + CI/CD + operations.**
5. **Security / threat model.** Use the `agent-skills:security-auditor` agent type if it exists.
6. **Ecosystem research** on the web.

Change the default lane set to fit the system:
- Drop a lane that has nothing to review.
- Split a lane when its area is larger than about 30k LOC.
- Use at most about 7 lanes.

Fill each lane prompt with:
- product context in 2–3 sentences;
- the goal and the deadline;
- the hard rules;
- the checkout path and the folders in scope;
- the PRs to read;
- the memory notes to skim.

## 3. Run the lanes in parallel

Launch all lanes in ONE message, as background `Agent` calls.

While the lanes run, do this work yourself:
- **Contribution profile.** Run `gh pr list --author @me --state merged --search "merged:>=<start-date>" --limit 1000 --json number,title,mergedAt`.
  - Count the PRs by conventional prefix (feat, fix, refactor, perf, test, docs, chore).
  - List the merged PRs that already include measured numbers. They go into "already delivered" in section 13.
- **Real request path.** Read the top-level README, the architecture docs and the CI workflows. Draft the actual request path (user → … → response) to compare against the lane reports.

Lane `.output` files are sometimes empty when the lane finishes. If that happens, recover the reports from the session transcript:

```bash
python <skill-dir>/scripts/extract_agent_reports.py ~/.claude/projects/<project-slug>/ <review-dir>/agent-reports
```

When you pass a project folder, the script reads the newest `*.jsonl` in it, which is the current session.

## 4. Verify before ranking

Lanes are sometimes wrong. Before a claim becomes Critical, High, Tier S or Tier A, check it yourself in the clean checkout: Read or Grep the cited file:line. Then answer these questions:

- Is it already fixed on the default branch? Or is it fixed only on a feature branch that never merged?
- Does an open PR already address it?
- Is the cited number from a dated measurement? If yes, mark it "re-baseline before quoting".

Drop or downgrade each claim that fails the check. Write down what you verified and what you could not verify (for example live cloud state, traffic volume, tenant settings). This list goes into "Method and limits".

## 5. Score and tier

Score every candidate from 1 to 10 for Impact, Effort, Risk and Visibility (how well the result demos to management):

```
Priority = Impact × Visibility ÷ (Effort + Risk / 2)
```

The score ranks return per hour. Assign each candidate to a tier:

| Tier | Meaning |
|---|---|
| S | Must do |
| A | Strong candidate |
| B | Nice to have |
| C | Avoid |

Tier rules:
- A tier can override the score for strategic value, but say why. Example: a project that changes how the product is judged.
- A candidate that cannot finish before the deadline goes to Tier C. Recommend an ADR for it instead.
- Critical and High security fixes are not ranked. Label them "fix first".

## 6. Write the report

Follow `references/report-outline.md`: "Read this first", 14 sections, then "Method and limits".

- Start with the uncomfortable truths.
- Say briefly what is good, and say when something should be left alone.
- Give a file:line or a PR link for every claim.
- Give a source and a date for every number, or label it "estimate".
- Write 3–5 killer projects. Each one follows the path PoC → measure → productionize → present.
- Split the roadmap into 4 dated phases from today to the deadline. Add a "Secure in week 1" list:
  - the security fix;
  - capturing the baseline numbers, because a "before" number cannot be recreated later;
  - sponsor agreement.
- Write the manager statements as templates with blanks such as `[X]%`. Never fill a blank with a guess.

## 7. Deliver and store

1. **HTML report.** If the `Artifact` tool exists, load `artifact-design` first, then publish the report as a private artifact. Otherwise write the HTML file to the review folder only.
2. **Local folder outside any git repo:** `<parent-of-repo>/reviews/<YYYY-MM-DD>-staff-review/`. Check that the folder is outside git: `git -C <dir> rev-parse` must fail. The folder contains:
   - `README.md`: index, reviewed SHAs, artifact URL, headline, and a warning if one applies;
   - `staff-review.html`;
   - `agent-reports/NN-<lane>.md`: the raw lane reports, each starting with a comment that gives the SHA and the date.
3. **Unpatched security findings.** If the report contains any, put a warning at the top of the README and in your reply. Keep the folder internal. Do not commit, push or share it until the findings are fixed.
4. **Memory.** If file memory exists, write one project memory: the key findings, the plan, the folder path, and links to related notes.
5. **Clean up.** Remove the worktree: `git -C <repo> worktree remove <short-path>`.

**Reply to the user** with:
- the verdict in about 5 bullets, Critical items first;
- the killer projects;
- the link or the folder path;
- one next step to offer, for example the fix PR or a spike.

Do not start the next step until the user says yes.

## Follow-up: "Should we replace self-hosted X with managed Y?"

This question often comes after the review. Example: "drop our self-hosted RAG and use the vendor's managed retrieval". Use the template in `references/report-outline.md` §F.

- **Check what the vendor actually offers.** Use current docs and web search, and record the date. Do not assume a product exists because a similar vendor has one.
- **List the jobs the current server does:** key custody, auth, billing, rate limits, ownership checks. Usually a thin proxy has to stay.
- **Compare with the user's reference system** if they cite one. Copy its cost model, not its trust model.
- **Cost:** use dated prices. Give the incremental cost per request and the break-even point against current infra. Label infra cost as an estimate, and tell the user to check the billing console.
- **Quality risk:** run a spike on the existing eval set before anything is decommissioned.
- **Save** the result as `<topic>-assessment.md` in the review folder. Update the README table and the memory note.
