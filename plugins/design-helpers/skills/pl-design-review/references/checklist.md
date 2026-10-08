# Design review checklist

Each item is a question with a default answer. A "no" is a finding only if you can point at it.
Severity hints: **P1** breaks the first impression, accessibility or a hard rule; **P2** weakens
the page; **P3** is polish.

## Brief fit

- Does the aesthetic match the audience (trust-first vs. playful vs. technical)? The audience
  picks the style, not the reviewer.
- Are the LLM defaults absent: purple/blue AI gradients, centered hero over a dark mesh, three
  equal feature cards, glassmorphism everywhere, endless micro-animations?

## Layout

- **Hero fits the first viewport** at 1280x800: headline 2-3 lines max, subtext 20 words or
  fewer, CTAs visible without scrolling. (P1 when the CTA is below the fold.)
- **Hero holds four text elements max:** one label, headline, subtext, CTAs. Stats strips, logo
  walls and taglines under the CTAs go in their own section below. (P2)
- **Hero has a real visual** (product screenshot, photo) when the repo has one. Text over a
  gradient is a placeholder. (P1 when assets exist and go unused.)
- **No grid orphans:** N items fill complete rows, or some items span to fill them. (P1)
- **No layout repeated back to back:** the same card-row or boxed panel twice in a row reads as a
  template. A page of 6+ sections uses at least 4 layout families. (P2)
- **No three identical cards in a row** as the default feature layout. (P2)
- **Section labels are rationed:** at most one small uppercase label per three sections; no
  "01 / 02 / 03" numbering on section headers or steps. (P2)
- Single-line nav at desktop, 80px tall or less.
- Every multi-column layout has an explicit mobile fallback; no horizontal page scroll at 375px.

## Imagery

- Cards and heroes use real product images where they exist; icon-on-pattern tiles are the
  fallback, not the default. (P1)
- No div-built fake screenshots, no hand-drawn decorative SVG.
- No pills or captions printed over photos (move them under or beside the image).
- Images have `alt` (empty for decorative), `width`/`height` or an aspect-ratio to avoid layout
  shift, `loading="lazy"` below the fold and priority on the hero image.

## CTAs

- **One label per intent across the whole site** (nav, hero, bands, footer, detail pages). Pick
  one of "Get in touch" / "Contact" / "Start a project" and use it everywhere. (P1)
- One primary and at most one secondary CTA per block; labels fit on one line at desktop.
- Button text passes WCAG AA (4.5:1) against the button background; ghost buttons have a border.
- Buttons respond to press (`:active` scale or 1px shift).
- No emoji or text glyphs (▸ ✉) as icons; use an icon library or nothing.

## Shape and color

- **One radius scale,** written down as tokens (e.g. controls 10px, surfaces 16px, pills full).
  Count distinct `border-radius` values; more than ~4 is a finding. (P1)
- **One accent,** used the same way everywhere. Hover states don't switch to a second accent.
  Product or status colors are fine when they carry meaning. (P1 when mixed at random.)
- **No neon:** no glow `box-shadow`s, glowing logos or gradient text on headlines. Shadows are
  dark and tinted to the background. (P1)
- One theme for the whole page; sections don't flip light/dark.
- No pure `#000` or `#fff` surfaces.

## Typography and copy

- Display font is not a default reach (Inter, or Fraunces/Instrument Serif as "premium").
  Serif only with a real editorial or brand reason.
- Body text is 65ch or narrower, with relaxed line height.
- Zero em-dashes (and en-dashes as separators) in visible copy, titles and alt text.
- No internal notes leaked into copy ("the brand stays neutral; each product keeps its color").
- No filler verbs (elevate, seamless, unleash), no invented precise numbers, no generic names.
- The `·` separator appears at most once per line.
- Casing is consistent between header nav and footer nav.

## Motion

- Every animation answers "what does this communicate?" (hierarchy, sequence, feedback, state
  change). Infinite background animations with no purpose go. (P2; P1 when they repaint the whole
  viewport every frame, e.g. animating `background-position`.)
- Only `transform` and `opacity` animate.
- **Scroll reveals stagger** items that enter together, and the reveal does not override hover
  transitions. A `transition` on `[data-reveal]` with higher specificity than `.card` silently
  replaces the card's hover timing; a keyframe animation with `fill-mode: backwards` does not. (P1
  if hover is broken.)
- Page changes don't hard-cut when a crossfade is cheap: `@view-transition { navigation: auto; }`
  with a named, fixed nav.
- Galleries and tabs crossfade instead of swapping instantly.
- Menus and overlays fade/slide in, close on Escape and return focus to the trigger.
- **`prefers-reduced-motion` disables** reveals, page transitions, smooth scroll and loops. (P1)
- No `window.addEventListener('scroll')` driving animation; use IntersectionObserver or CSS
  scroll-driven animations.

## Accessibility

- Visible `:focus-visible` style on every interactive element.
- Hidden menus are out of the tab order (`visibility: hidden`, not just `opacity: 0`).
- `aria-current` on the active nav link; `aria-expanded` on the menu button.
- Text contrast AA at body sizes, including small mono labels and placeholder text.
- Labels above inputs; no placeholder-as-label.

## Mobile

- Check at 375px: no overflow, hero CTA visible in the first screen, cards not taller than about
  half a screen each, wrapped labels don't strand one word on a line.
- Viewport units use `svh`/`dvh` with a `vh` fallback, never plain `100vh` heroes.

## Performance

- Fonts self-hosted or at least preconnected with `display=swap`.
- No full-viewport repaint loops; canvas backgrounds pause when the tab is hidden and respect
  reduced motion.
- Hero image is eager with `fetchpriority="high"`; everything below the fold is lazy.
- No console errors or 404s on the live site.
