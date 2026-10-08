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

The unfiltered first directory page introduces the existing Bend 2 project guide
with an underlined, theme-aware link below the hero description. Keep the official
language link and leave filtered/search/paginated views focused on the catalog.

Expose Blog in the main navigation on desktop and mobile. Guides are not linked
from the public footer; existing documentation URLs remain available.

Keep long-form posts in a centered reading column. Blog prose, metadata and
listing hover states use the directory color variables in both themes. The
article template supplies the H1; Markdown bodies start below it.

## Project thumbnails

Optional image previews sit above card content and between detail metadata and
the description. Use a 16:9 soft-background frame with `object-fit: contain` so
code examples and screenshots are not cropped. Missing images add no placeholder;
broken images are hidden by progressive enhancement. Keep existing owner avatars.

## Header utilities

Keep project search in the shared header, with an accessible label, submit button
and Cmd/Ctrl-K focus shortcut. On small screens the traffic label and search wrap
below the brand/navigation without horizontal overflow. Traffic is a real cached
24-hour pageview aggregate, hidden when unavailable; no simulated live audience.

## Related project browsing

Detail pages offer up to three published builds of the same type below the sources.
Use a compact text list with a title and short description, shared theme tokens,
and visible keyboard focus. Do not imply a quality ranking or add nested cards.

## Newsletter

The first, unfiltered directory page has a compact weekly Bend newsletter signup
between the hero and catalog. Keep it secondary to browsing, with a visible email
label, native form, consent copy and privacy link. Stack input/button on phones;
use the same light/dark tokens. Hide it until the double-opt-in list is configured.

Project detail pages reuse the newsletter signup below related builds. Stack the
copy above the form in the narrower reading column, preserving the same configured
list gate, consent copy, and native submission flow as the homepage.

Blog posts reuse the same optional signup after the complete article, outside the
prose block. Keep reading and project links primary; never gate the guide.
