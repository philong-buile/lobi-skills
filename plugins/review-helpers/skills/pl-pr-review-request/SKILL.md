---
name: pl-pr-review-request
description: >-
  Draft the Slack message that tells a reviewer (for example your lead) that a set of
  GitHub PRs are ready for review. The message uses real titles and URLs from `gh`,
  lists stacked PRs base to head, and adds a short plain-English summary per PR. Use
  when the user says "message my lead the PRs are ready", "draft a review request",
  "PRs ready for review message", "tell the reviewer to look at these", or invokes
  /review-helpers:pl-pr-review-request. Produces the message text for the user to copy
  into Slack. It does NOT send anything.
---

# PR review-request message

Draft a Slack message telling the reviewer that one or more GitHub PRs are ready for review.

**Only draft it. Never send it.** The user copies the output into Slack themselves. Sending a message on the user's behalf needs their explicit approval for each message.

## Configuration (from CLAUDE.md)

Read these optional lines from the user's CLAUDE.md (user-level or project-level):

```
Review-request reviewer: https://<workspace>.slack.com/team/<member-id>
Review-request greeting: お疲れ様です。
Review-request emotes: :blob_bowing: :ojigi: :bow:
```

- **Reviewer:** paste the bare member URL. Do **not** use a markdown link or the display name. Slack expands a bare member URL into a real mention by itself. Do **not** wrap it as `[@Name](...)`, because that renders as literal link text and pings nobody.
- **No reviewer line, or the user names someone else** whose member URL you don't have: use a plain `@Name`, and tell the user to replace it with the member URL.
- **Greeting and emotes:** these default to the Japanese-workplace style shown above. Use the user's values when they are given.

## Steps

1. **Figure out which PRs.**
   - Prefer explicit input: PR numbers or URLs in the user's message or in the skill args.
   - Otherwise use the PRs created or updated earlier in this session.
   - If it is still ambiguous, ask which PRs. Don't guess.

2. **Fetch each PR's real title and URL.** Never hand-type them:

   ```bash
   gh pr view <number> --json number,title,url,isDraft,baseRefName,headRefName
   ```

   Check CI before calling a PR "ready":

   ```bash
   gh pr checks <number>
   ```

   If a required check is failing or still pending, don't list that PR as ready. Flag it to the user instead.

3. **Order the list by review order.**
   - **Stacked PRs** (each PR's `baseRefName` is another PR's `headRefName`): sort base → head, so the PR to review **first** comes first. Number them `1.`, `2.`, `3.`.
   - **Independent PRs:** keep the user's order.

4. **Write a short summary for each PR.** The title alone does not tell the reviewer *what the change is for*. Add one to three short sentences per PR: what it is about and, when it matters, why. Base the summary on the PR body, not on the title:

   ```bash
   gh pr view <number> --json title,body,files
   ```

   The PR description already has the technical detail, so the summary is **context, not a spec**. It gives the reviewer enough to know what the PR is about before opening it.
   - Use simple English that non-native readers read easily: short sentences, common words.
   - Be concrete: "the export ran twice when the user clicked fast", not "improves export handling".
   - Keep the important technical points: a flag that is off by default, the issue number, a decision the reviewer has to make. Drop everything else: endpoint names, internal component names, test counts, step-by-step behavior.
   - If the PR needs the reviewer's opinion, say so as a plain question: "I'd like your opinion on one point: …".
   - Never invent a reason that the PR body does not support. If the body is thin, describe the diff factually instead.

5. **Group related PRs.** Put PRs from the same piece of work (same program, same subsystem, or overlapping files) under a short heading, and say how they relate:
   - **Stacked:** give the review order, base → head.
   - **Related but independent** (same area, shared files, both based on the default branch): say so, and name the merge-order constraint. Example: "They share files, so whichever merges second needs a rebase."

   Unrelated PRs stay in separate groups. Never imply a dependency that does not exist.

6. **Write it like a coworker asking a senior colleague for a review**, not like an AI report or release note.
   - Respectful toward a senior colleague, slightly humble, but not overly formal.
   - Friendly and professional, in simple English. Keep names, titles and terms in other languages as they are.
   - Short enough for Slack.
   - Closing line: "Please help me take a look at it whenever you have the time". Use "them" for several PRs.
   - **Never** use phrases like these: "Sir", "these following PRs have been ready for review", "When you have a chance, I'd appreciate it if you could take a look". They read as stiff and AI-written.
   - Avoid AI tells: em-dashes, bold labels inside sentences, "Key changes:", headings in a two-PR message.
   - **No exclamation marks** anywhere ("Thank you very much", not "Thank you!").

   Shape of a stacked example. Adapt the wording; don't copy it word for word every time:

   ```
   <reviewer member URL> さん
   お疲れ様です。:blob_bowing:

   The PRs for <the piece of work> are ready for review.
   They're related, so it would be helpful if you could look at them in this order:

   1. [<title>](<url>)
       - <one to three short sentences: what it is about>

   2. [<title>](<url>)
       - <one to three short sentences>

   Screenshots and test steps are in each PR.
   Please help me take a look at them whenever you have the time :blob_bowing:
   Thank you very much :ojigi:
   ```

   Formatting rules:
   - **Opening:** the mention URL on its own line, then the greeting on its own line.
   - **Emotes:** put one right after the greeting, and one or two at the end of the closing lines. Vary them between messages. Use at most one per line, and never put one inside the PR list.
   - **Purpose line:** say in one line what the PRs are for. If they are stacked or related, also say why the order matters.
   - **Independent PRs:** plain `*` bullets instead of numbers, and drop the "in this order" line. Give each unrelated group a short `*<group name>*` heading. For related-but-independent PRs that share files, say which one merges first, or that the second one will need a rebase.
   - **Single PR:** write "This PR is ready for review", with no numbering.
   - **"Screenshots and test steps are in each PR":** include this line only when the descriptions actually have them.
   - **Draft PRs:** mark them inline with `(draft)`, and also tell the user outside the message. Never present a draft as ready.

7. **Output the message in a fenced code block** so the user can copy it cleanly, then stop.
   - Do not run any send or post command.
   - Do not convert draft PRs to "Ready for review" (`gh pr ready`) unless the user explicitly asks, because that changes PR state.

## Notes

- **Titles** come straight from `gh`, so they always match the live PR. If a title should change, rename the PR first, then run this skill.
- **Markdown flavor:** the message body uses Slack-flavored markdown (`[text](url)` links, `*` bullets) on purpose. It is pasted into Slack, not GitHub.
- **Reviewer mention:** the one exception to the link syntax. It stays a **bare URL**, because Slack only expands member URLs into mentions when they aren't wrapped in link syntax. PR titles still use `[title](url)`.
- **Emotes:** write them as Slack shortcodes (`:blob_bowing:`), not Unicode emoji. Slack renders the workspace's custom emotes from the shortcode. Use only shortcodes that exist in the user's workspace.
