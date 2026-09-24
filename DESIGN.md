# Built with Bend design system

A warm, editorial project catalog inspired by shipwithjev.com, using original
branding and copy. Clean cards, source badges, compact filters, and a useful honest
empty state. No fabricated entries, audience counts, or sponsorship prices.

## Tokens

- Background #fbf8f4, ink #3d3935, muted #706860, terracotta accent #ba442b.
- Card #fffdf9, soft surface #f1ece4, border #e5ddd4.
- Dark equivalents are defined under html[data-theme=dark] in site.css.
- System sans-serif for UI, Georgia italic for the Bend wordmark/accent.
- Container 1440px; desktop side padding 40px, mobile 16px.
- Small 5–7px corners, simple borders, no shadows or decorative gradients.

Reusable styles live in frontend/src/styles/site.css. No external font or tracker
requests. JavaScript is optional; search, filters, pagination, and submission all
work through server-rendered forms. The theme toggle persists locally when storage
is available. Keep focus rings, skip link, visible labels, reduced-motion handling,
and equivalent light/dark readability. Test at 390px and 1440px and with long content.


## Catalog layout

Source pills sit above the results, with project-type links in the left sidebar
and the team sponsor block directly underneath. Keep source/type/search/count
filters combinable and URL-addressable. Use compact bordered cards, subdued
source footers, and restrained category colors. No decorative eyebrows. On narrow
screens the type and sponsor sections share a compact two-column area above the
source tabs. Counts come from published records; unknown popularity stays blank.

## Blog

Expose Blog in the main navigation on desktop and mobile. Guides are not linked
from the public footer; existing documentation URLs remain available.

Keep long-form posts in a centered reading column. Blog prose, metadata and
listing hover states use the directory color variables in both themes. The
article template supplies the H1; Markdown bodies start below it.
