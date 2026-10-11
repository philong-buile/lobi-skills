# Lane prompt templates

Build each lane prompt from the common header, one lane block and the common footer. Replace every `<...>` placeholder. Remove the checklist items that do not apply to this system, and add the system's own hot spots. Each lane is named after its area (for example "Backend deep architecture review"). The extraction script uses that name for the report file name.

## Common header

```
You are a <role> doing a critical, evidence-based review of the <AREA> of <PRODUCT: one or two
sentences on what it is, who uses it, and what it can change for the user>. The review feeds an
improvement roadmap to <DEADLINE / AUDIENCE>. Focus on what is weak, fragile, missing or
measurable. Do not write praise.

STRICT RULES:
- READ-ONLY. Do not edit, create, commit or push anything.
- Do not call cloud APIs. Do not run exploits.
- Do not print secret values: give the file path, the key name, and whether the file is committed.
- <USER RESTRICTIONS, e.g. "Do not call mcp__<org>__* tools", "Do not read .env files">.
- Read-only shell commands are allowed: git log/show/diff, grep, gh pr view/list.

CODE: the clean <default-branch> checkout at `<checkout-path>` (SHA <sha>). Use this checkout, not
the main working copy. Scope: <folders>. PRs to read for context (`gh pr view N`): <list with
one-line notes>. Background notes in `<memory-dir>`, which may be stale, so verify them against
the code: <file names>.
```

## Common footer

```
THEN ASSESS CRITICALLY:
1. Genuinely good (brief).
2. Mediocre or outdated compared with current practice.
3. Fragile: give each likely production incident as a concrete scenario and the failure it causes.
4. Over-engineered: complexity that does not pay for itself, and dead code.
5. Missing: what a senior engineer in this area would expect.
6. <N> concrete improvement candidates. For each one:
   - title;
   - problem, with evidence as file:line;
   - proposal;
   - measurable benefit: which metric moves, and by roughly how much;
   - effort (1–10) and risk (1–10);
   - <frontend lane: visibility to management (1–10)>.
   Prefer candidates whose result can be measured and shown to management.
7. Metrics that could be collected immediately, and where in the code to hook them.

OUTPUT: a dense report of about <2000–3000> words, with file:line citations and no filler. Be
honest. Say when something is fine and should be left alone.
```

## Lane 1: Backend

Role: Principal Engineer.

```
RECONSTRUCT THE ACTUAL ARCHITECTURE (cite file:line):
- Entry points, routers and endpoints. Mark the ones with no authentication.
- LLM abstraction:
  - providers and models, and where the model is chosen;
  - routing and fallback, timeouts, retries;
  - streaming (SSE) and cancellation when the client disconnects;
  - token counting, prompt caching, cost tracking and billing calls.
- Agent proxy, if the backend fronts an agent loop: what it does per request (auth, billing,
  model choice, logging).
- RAG end to end:
  - ingestion: chunking, embedding model, metadata;
  - storage: schema, indexes, and whether ANN indexes are actually used;
  - query: rewriting, hybrid or BM25, top-k;
  - reranking: model, and where it runs;
  - citations;
  - latency breakdown;
  - the eval harness, if one exists.
- Concurrency:
  - workers, async vs sync code, and in-process ML inference;
  - thread pools, DB pool settings, memory per worker;
  - what this means for horizontal scaling.
- Data stores: migrations, connection handling, and per-user isolation of every store. Check
  whether keys include the user ID or only a session ID.
- Auth: JWT validation (algorithm, issuer, audience, JWKS caching), user identity, rate
  limiting, internal service tokens.
- Resilience: retries, circuit breakers, timeouts, errors in the middle of a stream, and raw
  error text exposed to users.
- Observability: logging, tracing, request IDs. What can be measured today, and what cannot.
- Tests: coverage, mock modes in CI, coverage gates, gaps.
- Config sprawl: the number of env vars and feature flags.
```

## Lane 2: Agent / tool layer (MCP)

Role: Staff AI/Agent Architect.

```
RECONSTRUCT (cite file:line):
- The full request flow from the user message to the response. Name the process that owns each
  step.
- Agent loop:
  - max iterations;
  - how tools are presented (count, descriptions, schemas, bytes per round);
  - how the system prompt and skills/instructions are built and selected;
  - history management: truncation, compaction, token budget;
  - parallel tool calls, streaming, cancellation;
  - retry after a tool error, and the termination conditions.
- Model selection and fallback in agent mode.
- Workflows that change user data:
  - how edits are generated and validated before the write;
  - dry-run or diff, and user approval before the write;
  - backup, revert, retention;
  - gates: what they enforce, and what was removed and why;
  - how read-only intent is told apart from modify intent.
- Tool server:
  - list every tool, with one line each;
  - metadata quality and schemas;
  - tool annotations (readOnlyHint, destructiveHint);
  - SDK version and protocol version;
  - lifecycle: spawn, restart, crash handling;
  - security boundaries: path handling, file access, and what the LLM can make it do.
- Agent memory: what is stored, where, its scope, and the risk of poisoning.
- Observability: logs, telemetry, tool latency and success, traces per turn.
- Tests: unit tests, golden tests, any agent-behaviour regression or eval tests.

ADD TO ASSESS:
- Score these patterns for fit:
  - plan → preview → approve → apply transaction model;
  - structural (not prompt-only) read/modify enforcement;
  - tool annotations and permission scopes;
  - per-turn tracing and an agent eval harness with recorded scenarios;
  - scoping tools to the task, and context budget management.
- "If designed today": sketch a better architecture, and name the 2–3 moves that give 80% of the
  value.
```

## Lane 3: Frontend + host integration

Role: senior AI product engineer. The question to answer: "What would make this feel like an excellent enterprise AI assistant rather than just a chat window?"

```
RECONSTRUCT (cite file:line):
- App structure, state management, and how the modes differ in the UI.
- Transport between the UI and the host or backend:
  - message types;
  - ordering, reconnect, partial failure;
  - request/reply timeouts: are they idle timeouts or absolute deadlines?
- Feature inventory, as a table of present vs absent:
  - streaming, stop, regenerate, edit-and-resend, copy;
  - citations and how they are shown;
  - tool-call progress, plan display;
  - change preview, approval, undo, and confirmation before destructive actions;
  - history, feedback (thumbs), usage meter;
  - error states (401, 402, 429, network), empty state;
  - keyboard, IME, a11y (aria-live), i18n leaks;
  - long-conversation performance (memoization, virtualization);
  - markdown, tables, code rendering.
- Host:
  - embedded browser security settings: navigation and new-window policy, message origin
    checks, CSP, DevTools and reload keys in release;
  - IPC design, process lifecycle, auth flow, config.
- Rendering of model output: raw HTML, URL sanitizer, auto-loading images. Can model output
  become an exfiltration channel or reach the host bridge?
- Tests: unit tests, coverage, end-to-end tests. Is lint enforced in CI?
  <Run the test suite ONLY if dependencies are already installed. Never run install.>

ADD TO ASSESS:
- Score visibility (1–10, how well it demos) for every candidate.
- Name the 2–3 changes that would most change how the product is perceived in a demo.
- List product analytics events to add now: event name, properties, and where to emit them. Send
  no message text, only buckets and IDs.
```

## Lane 4: Infra + CI/CD + operations

Role: Principal Cloud/Platform Engineer. Do not recommend fashionable tech (for example Kubernetes) without a clear technical or business justification.

```
RECONSTRUCT the deployed architecture for each environment, citing files:
- Network: VPC, subnets, NAT (how many, and in which AZs), load balancer, TLS, WAF.
- Compute:
  - task or instance sizes, desired/min/max counts, autoscaling;
  - health checks: what they call, and whether an upstream blip can kill every task at once;
  - deployment config and drift (ignore_changes).
- Data:
  - DB class, Multi-AZ, backups and PITR, parameter groups;
  - other stores: PITR, TTL;
  - object storage, the container registry.
- IAM: task roles and least privilege; deploy roles and OIDC trust (which refs can deploy to
  prod).
- Secrets, logs, metrics, alarms, dashboards, tracing. Look for alarms muted by design.
- Separation between dev and prod, the state backend, module reuse, leftover resources.
- CI/CD:
  - what each workflow does;
  - the deploy path to dev and to prod, pre-flight checks, rollback;
  - image size and build time;
  - test gates, security scans;
  - queue time, installer build and signing.

ADD TO ASSESS:
- Cost candidates with rough $/month. State the instance sizes and pricing you assumed, and
  label every figure "estimate".
- Name the alarms and dashboards to create now: concrete metric names and log metric filters.
```

## Lane 5: Security / threat model

Use the `agent-skills:security-auditor` agent type if it exists. Otherwise use `general-purpose`.

```
Perform a serious, evidence-based security review and threat model. Components: <list each
process, its language and its trust level>.

INVESTIGATE (cite file:line for every finding):
- LLM-specific risks:
  - direct and indirect prompt injection paths: retrieved documents, user files, tool outputs,
    persistent memory, instruction/skill files, replayed history;
  - can injected text cause a write, a delete, data exfiltration (for example through markdown
    images or links, or through tool arguments), or cross-user leakage?
  - poisoning of the ingestion inputs;
  - model output rendered as HTML, and the path from XSS to the host bridge.
- Tool security:
  - file paths each tool can touch (traversal, UNC paths, files outside the project);
  - destructive operations, and whether they need user confirmation;
  - argument validation, process privileges, DLL/library search order, update and installer
    integrity.
- Embedded browser: exposed host objects and message handlers, origin checks, navigation rules,
  CSP, DevTools.
- AuthN/AuthZ:
  - JWT validation: algorithm, issuer, audience, exp and nbf, JWKS caching;
  - client token storage, refresh tokens;
  - IDOR on every resource ID;
  - service-to-service tokens;
  - rate limits and cost DoS (unbounded LLM spend per user).
- Secrets:
  - anything committed now, or in git history (`git log -p -S<prefix>`);
  - keys held on client machines;
  - tokens or PII in logs and telemetry.
- Cloud: IAM breadth, public exposure, SSRF from URLs the user or the LLM controls, CORS.
- Supply chain: pinned dependencies, lockfiles, base images, CI permissions,
  pull_request_target, actions pinned by SHA.
- Audit logging: can you reconstruct who caused a data change, and why?

OUTPUT: a dense report of about 2000–3000 words:
(a) a text threat-model diagram showing the trust boundaries;
(b) a findings table sorted by severity (Critical, High, Medium, Low), with file:line, exploit
    scenario, fix direction and effort 1–10;
(c) the risks specific to <LLM + tools + domain> that generic reviews miss;
(d) the 3–5 fixes with the best risk reduction per hour;
(e) what is already done well, briefly.
Separate confirmed issues from plausible ones. Do not inflate severity. Check whether attack
steps chain together into one path.
```

## Lane 6: Ecosystem research (web)

Role: research analyst for a Staff AI engineer. Tell the lane to load WebSearch/WebFetch with `ToolSearch` (`select:WebSearch,WebFetch`) first.

```
Today is <date>. Research the current open-source and industry ecosystem for patterns worth
adopting in OUR system. Evaluate each pattern critically for fit. Do not recommend a thing
because it is popular. Prefer primary sources: spec pages, official docs, engineering blogs,
papers, READMEs. Cite URLs and the date of each source. Do not modify local files.

OUR SYSTEM (summary): <10–15 lines: modes, stack, retrieval, agent loop, tools, gates, billing,
team size, current eval and telemetry maturity>.

TOPICS (adapt them to the system; for each, give what the leading options do and the latest
developments):
1. Protocol and spec evolution relevant to us. Examples for MCP: latest spec revisions, tool
   annotations, structured output, elicitation, tasks, authorization, SDK status.
2. Tool-use optimization: deferred tool loading or tool search, code execution with tools,
   dynamic tool selection, reducing context bloat.
3. Agent safety for changing user data:
   - plan → preview → approve → apply → verify → rollback patterns;
   - human-in-the-loop design;
   - prompt-injection defences;
   - OWASP LLM / agentic guidance.
4. Agent and RAG evaluation frameworks: golden datasets, LLM-as-judge calibration, CI regression
   gating, bootstrapping eval sets from production traces.
5. LLM observability: OpenTelemetry GenAI conventions, tracing tools, cost per task.
6. RAG practice for <language/domain/DB>:
   - hybrid search;
   - contextual retrieval;
   - hosted vs in-process rerankers;
   - embedding models;
   - ANN index pitfalls;
   - managed retrieval offerings.
7. LLM routing and cost: routers, fallbacks, prompt caching, small-model intent classifiers.
8. Agent memory: when it is worth it, and when it is a liability.
9. AI UX patterns for <domain> assistants, and what domain competitors ship.

FOR EACH PATTERN: (1) what it does, (2) why it is interesting, (3) does it apply to us (yes,
partly or no, and why), (4) what we would need to change, (5) expected benefit, (6) difficulty
1–10, (7) risks.
THEN: a ranked shortlist of the 6–8 patterns most worth adopting for a small team aiming for
measurable results within ~3 months. Add a list of popular things NOT to adopt, with the reason
for each.

OUTPUT: a dense report of about 2500–3500 words with URLs. Mark anything you could not verify as
"unverified".
```
