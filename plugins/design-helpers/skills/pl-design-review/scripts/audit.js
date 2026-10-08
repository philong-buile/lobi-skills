// In-page design audit. Paste the whole file into the browser tool's javascript_exec on a fully
// loaded page (scroll reveals forced visible first). Returns measurable facts, not verdicts:
// interpret them with references/checklist.md. Run at 1280x800 and at 375x812.
(async () => {
  const vis = (el) => { const s = getComputedStyle(el); return s.display !== 'none' && s.visibility !== 'hidden' && el.getClientRects().length; };
  const text = (el) => el.textContent.replace(/\s+/g, ' ').trim();
  const all = [...document.querySelectorAll('body *')].filter(vis);

  // Hero: first h1, its line count, the subtext after it and where the first CTA lands.
  const h1 = document.querySelector('h1');
  let hero = null;
  if (h1) {
    const r = h1.getBoundingClientRect(), lh = parseFloat(getComputedStyle(h1).lineHeight) || r.height;
    const scope = h1.closest('section, header, main') || document.body;
    const sub = [...scope.querySelectorAll('p')].find((p) => vis(p) && p.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_PRECEDING);
    const cta = [...scope.querySelectorAll('a, button')].find((a) => vis(a) && /btn|button|cta/i.test(a.className) && a.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_PRECEDING);
    hero = {
      h1Lines: Math.round(r.height / lh), h1FontPx: parseFloat(getComputedStyle(h1).fontSize),
      subtextWords: sub ? text(sub).split(' ').length : null,
      ctaBottom: cta ? Math.round(cta.getBoundingClientRect().bottom + scrollY) : null, viewportH: innerHeight,
      hasImage: !!scope.querySelector('img, picture, video, canvas:not([aria-hidden])'),
    };
  }

  // Small uppercase labels sitting right above a heading ("eyebrows").
  const eyebrows = all.filter((el) => {
    const s = getComputedStyle(el), next = el.nextElementSibling;
    return s.textTransform === 'uppercase' && parseFloat(s.fontSize) <= 14 && parseFloat(s.letterSpacing) > 0.5
      && next && /^H[1-3]$/.test(next.tagName) && text(el).length < 60;
  }).map(text);
  const sections = document.querySelectorAll('main section, main > div[class], body > section').length;

  // CTA labels grouped so duplicate intents stand out.
  const ctas = {};
  all.filter((a) => (a.tagName === 'A' || a.tagName === 'BUTTON') && /btn|button|cta/i.test(a.className))
    .forEach((a) => { const t = text(a) || a.getAttribute('aria-label') || '?'; ctas[t] = (ctas[t] || 0) + 1; });
  const contactish = Object.keys(ctas).filter((t) => /contact|touch|talk|start|reach|project|let/i.test(t));

  // Shape and color signals.
  const radii = {};
  all.forEach((el) => { const v = getComputedStyle(el).borderTopLeftRadius; if (v !== '0px') radii[v] = (radii[v] || 0) + 1; });
  const glows = all.filter((el) => /rgba?\((?!0, 0, 0)[^)]*\) 0px 0px (1[0-9]|[2-9][0-9])px/.test(getComputedStyle(el).boxShadow)).length;
  const gradientText = all.filter((el) => getComputedStyle(el).backgroundClip === 'text' || getComputedStyle(el).webkitBackgroundClip === 'text').map(text).slice(0, 5);

  // Grids: rows that are not full (orphans).
  const orphans = [];
  all.filter((el) => getComputedStyle(el).display === 'grid').forEach((g) => {
    const cols = getComputedStyle(g).gridTemplateColumns.split(' ').length;
    const kids = [...g.children].filter(vis);
    if (cols < 2 || kids.length < 2) return;
    const colW = (g.clientWidth - (cols - 1) * (parseFloat(getComputedStyle(g).columnGap) || 0)) / cols;
    const rows = {};
    kids.forEach((k) => { const r = k.getBoundingClientRect(); const top = Math.round(r.top); rows[top] = (rows[top] || 0) + Math.max(1, Math.round(r.width / colW)); });
    const filled = Object.values(rows);
    if (filled.some((n) => n < cols)) orphans.push({ grid: g.className || g.tagName, cols, rowFill: filled });
  });

  // Copy and media hygiene.
  const body = document.body.innerText;
  const dashes = (body.match(/[—–]/g) || []).length + (document.title.match(/[—–]/g) || []).length;
  const imgs = [...document.images];
  const css = [...document.styleSheets].map((s) => { try { return [...s.cssRules].map((r) => r.cssText).join('\n'); } catch { return ''; } }).join('\n');

  return {
    url: location.href, viewport: `${innerWidth}x${innerHeight}`,
    horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
    hero,
    eyebrows: { count: eyebrows.length, sections, labels: eyebrows },
    ctas, contactLabels: contactish,
    radii, glowShadows: glows, gradientText,
    gridOrphans: orphans,
    emDashes: dashes,
    imagesMissingAlt: imgs.filter((i) => !i.hasAttribute('alt')).map((i) => i.src.split('/').pop()),
    imagesNoSize: imgs.filter((i) => !i.getAttribute('width') && !getComputedStyle(i).aspectRatio.includes('/')).length,
    reducedMotionCss: css.includes('prefers-reduced-motion'),
    viewTransitions: css.includes('view-transition'),
    infiniteAnimations: document.getAnimations().filter((a) => a.effect?.getTiming().iterations === Infinity).map((a) => a.animationName || 'anon'),
    fonts: [...new Set([...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family))],
  };
})()
