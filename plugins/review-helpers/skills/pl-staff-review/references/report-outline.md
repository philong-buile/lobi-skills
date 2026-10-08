# Report outline

The report is one HTML page with a fixed navigation. It has a hero, an optional red "Fix this first" banner, sections 00–14, and section A. Each section opens with its verdict, then gives the evidence. The section order follows the deliverable list that users usually ask for.

## Hero

- **Title:** 2–4 words, for example "<Product> Staff Review".
- **One-line purpose:** "A critical review of <system>, ranked by career impact per engineering hour, with a realistic plan to <deadline>".
- **Chips:**
  - **Scope:** the repos and areas covered.
  - **Method:** "N parallel deep reviews of a clean <branch> checkout; the claims that drive priorities were re-checked in the code".
  - **Not done:** for example no cloud API calls, no live exploit tests, no traffic data.
- **"Fix this first" banner.** Add it only when a Critical security finding exists. Give the attack chain in plain words, then the action: tell the lead today, ship the fix this week, keep the page internal.

## 00 Read this first

Write 4–6 bold one-line truths, each with 2–3 sentences of evidence. Lead with the hardest ones:
- the riskiest unguarded path;
- the fact that nothing is measured end to end;
- the biggest cost or latency sink;
- the outage blind spots;
- the user's narrative vs output volume, from the contribution profile.

## 01 Current architecture assessment

- **The real request path.** Draw it as a diagram or numbered steps, user → … → response. Show which process owns each step and each trust boundary. Use the code as the source, not the docs.
- **Verdict by area.** A table with columns area | verdict (good / mediocre / fragile) | one-line reason with evidence.
- **The critical read.** Answer each question with concrete items:
  - genuinely good;
  - mediocre;
  - fragile (incident scenarios);
  - over-engineered;
  - missing;
  - what a senior engineer notices immediately;
  - what a principal engineer challenges;
  - what an AI engineer considers outdated.

## 02 Top 10 improvements and full ranking

- **Top 10.** For each: title, one-line why, and score.
- **Full ranking table:**

| Tier | Improvement | Category | Impact | Effort | Risk | Visibility | Priority | Why it matters |
|---|---|---|--:|--:|--:|--:|--:|---|

- Under the table, put the formula: `Priority = Impact × Visibility ÷ (Effort + Risk ÷ 2)`.
- Add one sentence on each case where a tier overrides the score: strategic value, or "cannot finish before the deadline, so Tier C plus an ADR".

## 03 Killer projects (3–5)

Each card has a short name, a tagline (`propose → approve → apply …`), an effort in weeks, and a "signature" tag on the main project. Card fields:

- Problem
- Current limitation, with file:line and PR links
- Proposed solution
- Architecture
- Implementation steps: PoC → measure → productionize
- Estimated effort
- Dependencies
- Risks
- Metrics: a headline metric plus a guard metric that must not get worse
- Expected business impact
- Why management would care
- Why this demonstrates senior-level ability
- What a good PR or demo looks like: a 5-minute demo script

The usual shapes of a killer project:
- a safety/transaction model for AI writes to user data;
- an eval and telemetry lab, which makes every other claim measurable;
- a latency or cost cut with a before/after number;
- a UX change that people see first.

Make the measurement project come first in the schedule, so the other projects are measured against it.

## 04–09 Area sections

| Section | Content |
|---|---|
| 04 MCP / agent layer | Improvement list, plus "If designed today" with the 2–3 moves that give 80% of the value |
| 05 Backend | "Low effort, high impact" list, then "Larger changes" |
| 06 Frontend and UX | Improvements ranked by visibility; the 2–3 demo-changing items; analytics events |
| 07 Infrastructure | Reliability and cost items with $ estimates; alarms to add |
| 08 Security | Numbered fix list in severity order, with effort; mark what is confirmed and what is plausible |
| 09 Evaluation and observability | Eval sets (retrieval, agent, tool), golden datasets, CI gating, telemetry, feedback |

## 10 Open-source and industry patterns

A table with columns pattern | what it does | applies? | change needed | benefit | difficulty | risk. Add "adopt now", "later" and "do not adopt" lists. Each pattern links to its source and gives the date.

## 11 Roadmap to <deadline>

Use four phases with real dates computed from today to the deadline:

| Phase | Typical length | Content |
|---|---|---|
| 1 · Quick wins | first 3–4 weeks | security sprint, backfill baselines from existing logs, ship telemetry, known bugs, outage-proofing, triage open pitch PRs |
| 2 · High-impact engineering | next ~6 weeks | eval harness first, then the killer projects behind flags, cut into a release |
| 3 · Measurement and productionization | overlaps phase 2 | prod rollout, dashboards, SLOs, 2–3 weeks of after-data, runbooks, ADRs |
| 4 · Presentation | last 2–3 weeks | one-page before/after summary, recorded demo, eval report, "next year" slide |

Add a **"Secure in week 1"** list:
- a sponsor who agrees with the goals;
- the release dates;
- data or labelling approvals;
- an eval budget.

## 12 Metrics to start collecting now

A table with columns metric | definition | where to hook it in the code | baseline source (existing logs or "none, starts now"). Cover:
- latency (TTFT, p50, p95 per stage);
- cost per task, tokens;
- tool success rate, task completion rate;
- retrieval hit@k and MRR;
- feedback rate, error classes;
- availability.

## 13 What to show your manager

- **The story in four slides:**
  1. What I found: risk map.
  2. What I built to measure: eval suite and dashboard.
  3. What changed: before/after table, each headline paired with its guard metric.
  4. What's next: ADRs as the proposal for next year.
- **Statements to fill with measured numbers only.** Templates with `[X]`, for example "Cut <metric> from [X] to [Y] at unchanged <guard>".
- **Already delivered: package these now.** Merged PRs that already include measurements, from the contribution profile. Add "verify each number before quoting it".

## 14 What not to spend time on

- Fashionable infrastructure with no measured need.
- Big-bang rewrites or migrations that cannot finish before the deadline. Write ADRs instead.
- Cosmetic refactors and comment churn.
- Re-arguing decisions that are already measured.
- Polish beyond landing existing stacks.

End with "the honest read on focus": a few measured outcomes beat a high PR count.

## A Method and limits

- What was reviewed: SHAs, repos, and the PRs read.
- The lanes that ran, and the list of claims that were re-checked directly.
- **Not verified:** live cloud state, traffic, tenant settings, and items newer than the research date.
- Scores are judgement calls, adjusted for consistency. Dollar figures are estimates. Measured figures come from dated earlier measurements, so re-baseline them before quoting.
- Footer: "Prepared <date> for <name>." Add "Internal: contains unpatched security findings" if that applies.

## §F Follow-up: "Replace self-hosted X with managed Y?"

Save this as a separate `<topic>-assessment.md` in the review folder.

```markdown
# Replace <X> with <Y>? (assessment, <date>)

Proposal (user): <one paragraph, including any reference system they cite and the trade-off they accept>.
Supersedes: <earlier assessment, if any>.

## Verdict
<Yes / Partly / No> for <scope>, with corrections:
1. <What must stay, usually a thin proxy, and why>
2. <What must be proven before anything is deleted>

## What <vendor> actually offers (docs checked <date>)
| Option | What it is | Fit for us |

## Reference vs us            (when the user cites their own system)
| | Reference | Ours |      (size of data, tenancy, auth, stakes, hosting, prompt management)
Copy the cost model, not the trust model.

## Why the server cannot disappear
| Job the backend does today | Can <vendor> do it? | Where it must live |

## Cost (prices from <source>, <date>; verify)
Incremental cost per request; storage; current infra $/month (estimate, check the billing
console); break-even volume. Note when request volume is unmeasured.

## Target design
<diagram: client → proxy (auth, billing, caps, key, ownership binding) → vendor API>
What is removed, and what is kept.

## Risks
Quality in <language/domain>, vendor lock-in (mitigate: own the source data and the upload
script, keep the proxy interface narrow), data residency, outages, billing tables, security
(the proxy still enforces auth; current Critical fixes ship regardless).

## Plan
1. Spike (2–3 days): run the existing eval set against <Y>; compare hit@k and MRR. No infra change.
2. Behind a flag on one path; measure TTFT and $/request.
3. Move the remaining callers.
4. Decommission after one release cycle on the new path.
5. ADR with the numbers to <decision maker>.
```
