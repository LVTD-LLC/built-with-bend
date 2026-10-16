# Public claim contract

Verified 2026-09-29. Private dated evidence is in the configured Rowset history.
- Directory: human-reviewed Bend 2 projects; public browsing/submission needs no account (README, directory views).
- Bend 2 differs from Bend 1/HVM; do not transfer old runtime/benchmark claims.
- Current Bend targets include C, Metal, CUDA and JavaScript; JavaScript is sequential.
- LAWS.bend describes laws; PROOF.bend supplies checked proofs. This does not guarantee unmodeled requirements.
Primary sources: https://bend-lang.com/ and https://github.com/bendlang/bend .
Published article: /blog/bend-programming-language (slashless).

## Knot release availability — verified 2026-10-14

Knot 0.0.1 is published on npm as `@matheusbbarni/knot`. This verifies package
availability, not install compatibility or production readiness. Upstream still
marks the test runner planned and distinguishes transpilation from type-checking.
Sources: https://github.com/MatheusBBarni/knot-node-tooling/blob/b914a71bbca46b7e2fe447d19a7a182e2b9ff715/README.md
and https://www.npmjs.com/package/@matheusbbarni/knot/v/0.0.1 .
The listing retains its original title, capabilities, source links and publication
date; the correction’s fixed content date drives sitemap lastmod. Reverify the
release caveat on 2026-10-21 before expanding installation guidance.

## Bend HTTP Server compatibility — checked 2026-10-15

The unmodified source at revision `66a9258100f1d55e5cabc37f8c30774e20061b69`
fails `bend main.bend --check-only` with Bend 2.0.35 at `TCP.listen(port())`
(expected String, observed U32). Its separate `bend PROOF.bend --verdict`
passes. Do not infer server-build, socket, HTTP or GPU correctness from those
computation laws, or describe the first failure as a complete migration recipe.
No runtime or benchmark was performed; other compiler versions are untested.
Sources and reproducible checks: `.seo/evidence/2026-10-15-http-server.md`.
The dated listing note is bound to its exact repository and slug. Recheck
October 22 or after a relevant upstream change.

## Browser proof demo — checked 2026-10-16

Bend, Explained v4 is a browser learning resource pinned to Bend 2.0.25's
ordinary checker. It is not the independent `--verdict` kernel check.
On October 16, its Original and Raise the limit to 1500 presets passed;
Refactor slip failed. The parallel-work animations are not benchmarks.
Source: https://github.com/raunak-11/bend-explainer/blob/84c04b02bbd3be2c5ee1b5622a1490e41e730391/README.md
Live interaction: https://raunak-11.github.io/bend-explainer/v4/#works-play
No external LLM call or key was used. Recheck October 23 before expanding claims.
