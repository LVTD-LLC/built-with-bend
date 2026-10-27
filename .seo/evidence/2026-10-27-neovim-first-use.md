# Neovim first-use source path

The existing Bend 2 for Neovim listing now distinguishes editing-only setup from
compiler-backed checks and points to the maintainer’s installation choices and
proof-workflow example. It is not another general editor article or a tested
installation walkthrough. Original database description, source links, project
actions, publication timestamp and sort order remain unchanged.

Primary sources checked October 27, 2026:

- README: https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/README.md
- Installation: https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/docs/INSTALLATION.md
- Example: https://github.com/nuxyel/bend2-nvim/tree/a67312765430fc8dea4f291ca2ab071f311f1e32/examples/proof-workflow
- Published release: https://github.com/nuxyel/bend2-nvim/releases/tag/v1.0.0

Current upstream HEAD remains a673127. Native Lua editing requires neither Node
nor a separate language-server executable; compiler-backed features require Bend
2.0.28+ according to the maintainer. Neovim 0.11+ installation paths differ from
0.12+ experimental vim.pack. Documented compiler tests cover 2.0.28 and 2.0.32,
not every later version. The page explicitly says Built with Bend has not installed
or run this plugin. No performance, proof-soundness or production-readiness claim.

Implementation uses the existing curated-section pattern. Exact slug AND
repository matching controls the section and October 27 sitemap content date.
No production database mutation, new URL, global editor link or analytic event
schema. Existing source-intent events measure visits to sources, not external
installation success. Future source review: November 3 or a relevant release.

Verification includes a public-view identity/repurposing regression test, rendered
mobile/desktop light/dark inspection, source-link checks, and repository CI before
merge. Live deployment verification remains separate. ReviewGate is waived by
standing project authorization, never recorded as passed. Private observations,
action history and experiment outcomes remain in the established Rowset dataset.
