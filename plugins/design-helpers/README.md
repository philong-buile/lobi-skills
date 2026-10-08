# design-helpers

Frontend design review for websites and product UI, and README redesigns for public repos.

## Skills

- **pl-design-review**: reviews a site the way a senior frontend lead would. It opens every page
  in the built-in browser at 1280x800 and 375x812, freezes motion for screenshots, runs an in-page
  audit script (hero fit, grid orphans, CTA labels per intent, radius scale, glows, em-dashes,
  image hygiene, reduced-motion and view-transition support), reads the source behind each
  finding, and returns a design read, current vs target dials, and a ranked P1/P2/P3 list with
  file:line references. When asked, it fixes a tier and ships it: branch, PR, independent review,
  merge, deploy, live check.

- **pl-readme-polish**: redesigns a README so it reads like a popular open-source project:
  a light/dark SVG banner through `<picture>`, at most three factual badges, install commands
  first, one table of what you get, a Mermaid diagram when there is a real mechanism, then
  configuration, requirements, layout, contributing and license. It checks the banner geometry
  in a browser, scrubs private details from public repos, asks before a public push, and checks
  the rendered page on GitHub afterwards.

Files:

- `skills/pl-design-review/SKILL.md`: the workflow.
- `skills/pl-design-review/references/checklist.md`: the rules the review checks against.
- `skills/pl-design-review/scripts/audit.js`: paste into the browser tool to get measurable facts.
- `skills/pl-readme-polish/SKILL.md`: the README workflow.
- `skills/pl-readme-polish/templates/`: banner SVG and README skeleton to fill in.

Works best with the `design-taste-frontend` skill installed, but does not require it.
