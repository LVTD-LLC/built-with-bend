# Editor guide: native and browser paths

Updated November 1, 2026. The existing slashless editor guide remains the intent
owner; its title, description and October 11 publication date are unchanged.
The new choice rows, section and navigation connect readers to two existing
profiles rather than creating another comparison page.

- [Native Neovim source](https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/README.md): Lua editing is separate from a Node-based LSP integration; compiler-backed commands require an installed compiler. The documented test matrix is not a guarantee for all later versions. No plugin installation was tested for this update.
- [Workshop source](https://github.com/np/bend-workshop/blob/f05af248febee43a589580550dba6ffe243e1fca/README.md) and [checking boundary](https://github.com/np/bend-workshop/blob/f05af248febee43a589580550dba6ffe243e1fca/AGENTS.md#checking-entryts): browser checker and single-core JavaScript execution, not the CLI Lean-kernel check. The profile's October 30 smoke observations retain their original date and are not claimed as a retest of the November 1 update. The compiler pin remains d30d7dd.
- [Published LSP metadata](https://registry.npmjs.org/bend2-lsp): November 1 read still reports 0.1.1; the original October 25 VS Code/server comparison is not silently recertified.

The added FAQ answer and FAQ schema agree. `updated_at`, rendered `dateModified`
and the guide's sitemap content date use November 1; publication date is retained.
No analytics, runtime dependency, project record, template or migration changes.

Verification: 474 tests plus 23 subtests; local quality/build checks; actual
Django rendering; four 390/1440 light/dark browser cases; 13 rendered truth rules.
Links are checked against actual rendered paths, not the pattern-only link audit.
QA browser requests block PostHog and Sentry. Existing primary source actions and
public analytics identity remain unchanged. Source review is not a compatibility,
proof, benchmark or physical-device certification.

[Screenshot: mobile](screenshots/2026-11-01-editor-mobile.png) ·
[Screenshot: desktop dark](screenshots/2026-11-01-editor-desktop-dark.png).
Private research and run/action history remain in the existing configured Rowset
history dataset; no raw analytics or research projections are committed.
ReviewGate is waived under standing project authority, not passed; CI and live
verification are still required.
