# Built with Bend design system

A warm, editorial project catalog inspired by shipwithjev.com, using original
branding and copy. Clean cards, source badges, compact filters, and a useful honest
empty state. No fabricated entries, audience counts, or sponsorship prices.

## Tokens

- Background #fbf8f4, ink #3d3935, muted #706860, terracotta accent #ba442b.
- Card #fffdf9, soft surface #f1ece4, border #e5ddd4.
- Dark equivalents are defined under html[data-theme=dark] in site.css.
- System sans-serif for UI, Georgia italic for the Bend wordmark/accent.
- Container 1200px; desktop side padding 32px, mobile 18px.
- Small 5–7px corners, simple borders, no shadows or decorative gradients.

Reusable styles live in frontend/src/styles/site.css. No external font or tracker
requests. JavaScript is optional; search, filters, pagination, and submission all
work through server-rendered forms. The theme toggle persists locally when storage
is available. Keep focus rings, skip link, visible labels, reduced-motion handling,
and equivalent light/dark readability. Test at 390px and 1440px and with long content.
