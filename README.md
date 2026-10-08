# lobi-skills

Claude Code skills for code review, system review and frontend design review, packaged as a plugin marketplace.

## Plugins

| Plugin | Skills | What it does |
| --- | --- | --- |
| [`review-helpers`](./plugins/review-helpers) | `pl-pr-review-annotations`, `pl-pr-autofix`, `pl-staff-review` | `[FYI]` triage comments on large PRs, Auto-fix for new PRs, and a staff-level system review with a ranked roadmap |
| [`design-helpers`](./plugins/design-helpers) | `pl-design-review` | Frontend design and UX/UI review in a real browser, with a ranked P1/P2/P3 fix list and an optional fix-and-ship flow |

## Install

In Claude Code:

```
/plugin marketplace add philong-buile/lobi-skills
/plugin install review-helpers@lobi-skills
/plugin install design-helpers@lobi-skills
```

From a terminal:

```bash
claude plugin marketplace add philong-buile/lobi-skills
claude plugin install review-helpers@lobi-skills
```

To update later:

```bash
claude plugin marketplace update lobi-skills
claude plugin update review-helpers@lobi-skills
```

## Requirements

- `gh` (GitHub CLI), authenticated, for the PR skills and the staff review.
- The Claude desktop app (Code tab) for `pl-pr-autofix`, because it needs the `ccd_pr` tools, and for `pl-design-review`, because it needs the built-in browser.

## Layout

```
.
├── .claude-plugin/marketplace.json   lists the plugins below
└── plugins/
    └── <plugin>/
        ├── .claude-plugin/plugin.json
        ├── skills/<skill>/SKILL.md   plus references/ and scripts/ where needed
        └── README.md
```

## License

[MIT](./LICENSE)
