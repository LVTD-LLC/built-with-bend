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

## Package-discovery guide links — verified 2026-10-21

JendHub and Bend Packages are discovery tools covered by the existing package-import
walkthrough. Link only their exact repository-bound listings to that guide; keep
original source/project actions primary. The ASCII example was checked October18
on Bend2.0.35 and2.0.37; that is not package-wide compatibility certification.
Primary discovery sources: https://jend.leeeet.dev/llms.txt and
https://777genius.github.io/bend-packages/ . Worked-example source:
`apps/pages/posts/bend-2-package-imports.md`. No new compiler test today.

Knot release/source review October21: README b914a71 remains unchanged and npm
still identifies0.0.1; type-checking and planned-runner caveats remain supported.
No installation/runtime/platform certification. Next source review October28.

## Official HTTP demo discovery — checked 2026-10-22

The original HTTP Server repository remains at 66a9258; its main check still fails
on Bend 2.0.35 and its separate computation-proof verdict still passes. Keep the
October 15 visible result, not a new compatibility claim. Next source check October 29.

A separate official Bend 2.0.35 demo at
https://github.com/bendlang/bend/tree/79df8d9c40722ee9507a1e253f283b51025f9d6c/demos/io_http_server
built natively without source edits and returned one local HTTP 200/Hello, world!
response on October 22. It binds 127.0.0.1:8080 and returns a fixed page; it is not
the listed server, a GPU example, a benchmark or a production recommendation.
The demo's check-only, ordinary proof and --verdict commands reject unsafe or
foreign-code dependencies on this compiler; never describe those checks as passing.
Reproducible public-source evidence: `.seo/evidence/2026-10-22-http-demo.md`.
Only the exact repository-bound listing receives the source-discovery section and
October 22 content date; original publication/actions/metadata remain unchanged.

## Browser listing exercise — checked 2026-10-23

Upstream remains at 84c04b02bbd3be2c5ee1b5622a1490e41e730391. The live
v4 Original / Refactor slip / Raise the limit to 1500 presets still return
pass / fail / pass. The source-bound listing adds a direct exercise link and a
reverse path to the existing introduction; original sources and publication remain
unchanged. Ordinary Bend2.0.25 checking is not --verdict, an IO runtime, a hub
package fetcher, or a benchmark. No AI provider or key was used. Next source
review October30; existing October16 introduction experiment dates remain intact.

## Editor server source versus release — verified 2026-10-25

The npm registry still publishes bend2-lsp 0.1.1 as latest. Repository revision
`ed06027cc5396050459776accf91214f0c433f79` declares 0.2.0; its October22
source change vendors Bend2.0.38 and adds completion/symbols/folding. Do not
represent that source version as a published npm release or an installed
kbrianps extension upgrade. Node>=26.9 remains declared. No source-build,
extension-install or host compatibility test was performed for this update.
Primary sources: https://registry.npmjs.org/bend2-lsp ;
https://github.com/don2e4/bend2-lsp/blob/ed06027cc5396050459776accf91214f0c433f79/package.json ;
https://github.com/don2e4/bend2-lsp/commit/af933fd975f50f6e37cbc0882cae7e3a6f643ee1 ;
https://github.com/don2e4/bend2-lsp/issues/4 .
Nuxyel06bcbaf and kbrianps81ba2c9 sources unchanged. Recheck November1 or on release.

## JendHub walkthrough source paths — verified 2026-10-25

Old search.txt?q returned400; /src/bend-kit-bytes@0.3.2.0/bytes.bend returned404.
Current /llms.txt documents search.txt?query= and read.txt?path= . Both
replacement links in the package guide return200. Search now returns bytes0.3.3.0;
retain the original tested0.3.2.0 import and explicitly avoid claiming a new
compiler/package test. The pinned read source still exposes to_hex at line631,
from_string, low-byte conversion, and hash-pinned int dependency. Source pages
are inspection evidence, not package-wide compatibility or a new execution test.
Recheck November1 or on upstream change.

## Native Neovim first use — source reviewed 2026-10-27

Bend2.nvim at a67312765430fc8dea4f291ca2ab071f311f1e32 provides native Lua editing
without Node.js or a separate language-server executable. Editing works without
Bend; compiler-backed checks, proof workflows, Bend Base completion, builds and runs
require Bend 2.0.28+ according to its maintainer. Neovim 0.11+ supports lazy.nvim
and native package layout; vim.pack needs 0.12+ and has an experimental API.
The published v1.0.0 GitHub release is available. The documented compiler test
matrix covers 2.0.28 and 2.0.32, not every later compiler. No local plugin install
or execution was performed. Preserve original listing metadata and sources.
Primary sources: https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/README.md
and https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/docs/INSTALLATION.md .
The dated first-use section and sitemap content date match the exact repository
and slug only. Recheck November 3 or on an upstream release/change.

## Knot published first use — checked 2026-10-28

README remains b914a71; npm latest remains0.0.1. Isolated prefix install with
--ignore-scripts succeeded, but --version and --help both failed in the native
loader on Linuxx64/glibc2.36/Node24.21.0: GLIBC_2.38 not found. Native binary
SHA256 matched the published wrapper. Knot did not start; no package-operation,
source-build, macOS,otherlibc,proof,benchmark or security certification.
Pinned README source-build prerequisites are Node24LTS/Bend2.0.24/nativeCcompiler;
not a tested workaround. Transpilation/typechecking and planned-runner limits stay.
Release/source instructions: https://registry.npmjs.org/@matheusbbarni/knot/0.0.1
and https://github.com/MatheusBBarni/knot-node-tooling/blob/b914a71bbca46b7e2fe447d19a7a182e2b9ff715/README.md .
Only exact repository-bound Knot listing gets newsection/date, originals retained.
Recheck November4 or relevant release; prior correction outcomesNov4/11 retained.


## ezmcp directory entry — checked 2026-10-29

Pinned source c8d39cebc58c7a967d4b22f0dd8fd97e60f23c45 is Bend 2, not
classic Bend/HVM. Unmodified examples/demo built natively on Linux x64 using
an isolated official Bend 2.0.38 release (verified release SHA-256). Stdio
and loopback HTTP initialized, listed tools and returned structured sum 42.
HTTP rejected an untrusted Origin (403), unsupported protocol version (400)
and GET (405). One local smoke check is not full conformance, proof, benchmark,
security or production certification. No global compiler change.

README/SPEC explicitly exclude authorization, resources, prompts, server SSE
and sessions; distinguish client SSE response reading from server SSE support.
Keep localhost or an authenticating proxy. Original source links and reviewed
public copy live in apps/directory/content/ezmcp.json. No popularity invented.
Next primary-source check November 5; acquisition/source-intent reads November
19/26 after final data. No clean growth attribution promised.


## Bend 2 pocket workshop — checked October 30, 2026

The publication payload at `apps/directory/content/bend-2-pocket-workshop.json` describes [np's browser workshop](https://np.github.io/bend-workshop/), not an official Bend product. Source pin `5c9ed4f4ae2303b042b18196df683e7e5d6ab90d`, compiler pin `d30d7dddae6c40785ef03001455599baa31a8e2d` (2.0.39). Independent live Chromium checks at 390/1440: value42, type-error rejection, open goal, bundled x+0 example checked; no page errors/overflow. This is not a full suite, physical-phone test, performance benchmark or Lean-kernel verification. No AI provider, hub import or Git operation exercised; no code/content copied from upstream. Repository has no detected license; link to sources, do not redistribute its code. Source review November6; discovery/source-intent outcomes November20/27, not a promised uplift.
