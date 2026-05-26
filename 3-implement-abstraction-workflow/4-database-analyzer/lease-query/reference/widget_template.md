# Widget templates

How to render the visual / hybrid query answers via
`mcp__visualize__show_widget`. Call `mcp__visualize__read_me` with
`modules: ["interactive"]` before the first `show_widget` call of a session.

## Universal rules

- No emoji. Sentence case throughout.
- Two font weights only: 400 and 500. Never 600/700.
- Money: `Intl.NumberFormat('en-US', { style:'currency', currency:'USD',
  maximumFractionDigits:0 })`. Percent: one decimal.
- Use CSS variables (`var(--color-text-primary)`, `var(--color-background-primary)`,
  `var(--border-radius-lg)`) — never hard-coded hex outside the c-* palette.
- Cards: white bg, 0.5px border, radius-lg, padding 1rem 1.25rem.

## 1. Single-lease exhibit card

For a query about one lease's exhibit (signage, site plan, cage, etc.).

```
[Header row]
  <lease_n>  [asset-type badge]  [lease-type badge]

[Section: Summary]
  Two-column key/value list (Found on page-NN, exhibit label, etc.)

[Section: Content]
  Either a key-value table of specs (parking ratios, dimensions, cabinet
  counts) OR a verbatim blockquote of the exhibit text.

[Footer]
  Page reference line. Optional <a href="...png" /> link to open the page.
```

## 2. Multi-lease selector (hybrid)

For a hybrid query covering 2+ leases.

- Dropdown / segmented control at the top.
- All lease data embedded in a JS array on page load — no extra MCP calls.
- One card per lease following pattern 1.
- The selector's options should read like a real label, e.g.
  "1. Saltflats Tacos & Mezcal — RET — exp. 2036-11-30".

## 3. Portfolio summary (DB-only with metric flair)

Sometimes a DB-only query wants more than a table — e.g. a rent-roll snapshot.

- Top: metric cards row (Total ABR, Lease count, WALT in years,
  # expiring next 12 months). Use `--color-background-secondary` fill, no
  border, `--border-radius-md` corners.
- Below: the markdown table goes in the response text, not the widget.

(Default: keep DB-only as markdown only. Reach for metric cards only when
the user explicitly wants a dashboard view, or for the "rent roll snapshot"
query.)

## 4. Exhibit page inline — REQUIRED for visual answers

**The widget iframe cannot load local files.** A relative `<img src>` or a
`file://` URI to `_lease_pages/...png` will be blocked by the CSP. To
*actually show* an exhibit page, embed the PNG bytes inline as a base64 data
URI using `scripts/page_data_uri.py`.

### How to do it

For every visual answer, the skill should:

1. Pick the page(s) most worth showing (typically 1–2 per lease — the
   diagram-heavy page, not the prose page).
2. Call `python scripts/page_data_uri.py _lease_pages/<slug>/page-NN.png`
   to get a `data:image/jpeg;base64,...` string.
3. Drop that string straight into an `<img src="{uri}">` tag in the widget.

```python
# In the skill's bash step, just before show_widget:
import subprocess
def uri(p):
    return subprocess.check_output(
        ["python", "scripts/page_data_uri.py", p],
        text=True,
    ).strip()
page_uri = uri("_lease_pages/Saltgrass_Storage/page-22.png")
# Then pass page_uri into your widget_code template.
```

### Widget HTML pattern

```html
<figure style="margin:0 0 12px;">
  <img src="{PAGE_DATA_URI}"
       alt="Saltgrass site plan, page 22"
       style="display:block; width:100%; max-width:560px; height:auto;
              border:0.5px solid var(--color-border-tertiary);
              border-radius:var(--border-radius-md);" />
  <figcaption style="font-size:12px; color:var(--color-text-tertiary);
                     margin-top:6px;">
    Source: page 22 of the Saltgrass ground lease.
  </figcaption>
</figure>
```

### Sizing rules

- Default `--max-width 900 --quality 78` keeps a typical page under ~70 KB
  base64, which a widget carries comfortably.
- Diagram-heavy pages may run to ~150 KB — still fine for one inline page.
- For multi-page hybrid answers, embed **one page per lease** (the most
  visual one). If the user asks for more, render a second widget rather
  than ballooning a single widget code block.

### Fallback

If image inlining genuinely isn't workable (page is illegible, file
missing), fall back to the prose-summary card with the key facts in a table
and a one-line note: "Source: page NN of the <lease_name> lease."

## Selector skeleton

```html
<div style="display:flex; align-items:center; gap:12px; margin-bottom:1rem;">
  <label for="sel" style="font-size:13px; color:var(--color-text-secondary);">Lease</label>
  <select id="sel" style="flex:1; min-width:240px;"></select>
</div>
<div id="card"></div>
<script>
const D = [ /* one object per lease */ ];
const sel = document.getElementById('sel');
D.forEach((d,i) => {
  const o = document.createElement('option');
  o.value = i; o.textContent = (i+1)+'. '+d.label;
  sel.appendChild(o);
});
function render(i) { /* build card from D[i] */ }
sel.addEventListener('change', e => render(+e.target.value));
render(0);
</script>
```
