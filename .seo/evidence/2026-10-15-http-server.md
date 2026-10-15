# Bend HTTP Server compatibility check

Checked October 15, 2026. This is public, reproducible source evidence, not
traffic research or a benchmark.

- Source: `iamsahilsonawane/bend2-http-server`, revision
  `66a9258100f1d55e5cabc37f8c30774e20061b69` (unmodified checkout).
- Compiler: `bend version` returned `bend 2.0.35`.
- `bend main.bend --check-only` exited 1 at `src/server.bend:199`,
  `TCP.listen(port())`: expected `String`, observed `U32`.
- `bend PROOF.bend --verdict` exited 0, `ALL PROOFS CHECK`.
- The versioned compiler guide documents `TCP.listen(host, port)`:
  https://github.com/bendlang/bend/blob/v2.0.35/guide/GUIDE.md
- Source and laws:
  https://github.com/iamsahilsonawane/bend2-http-server/tree/66a9258100f1d55e5cabc37f8c30774e20061b69

The first failed check does not establish that one edit fixes the server. The
proof file checks the stated computation laws, not the IO server. No server was
started, no compiler was upgraded, and no hardware-performance or compatibility
claim is made about other versions. This does not label the project unusable
with every compiler.

The new listing section gives developers the precise check boundary and a
source-reading path through HTTP parsing, routing and laws. The existing
description, title, source records, publication order and project actions stay
intact. Only the matching slug **and repository URL** receive the note and the
fixed October 15 sitemap content date. This change is template-backed; no
production database fields are edited.

Recheck the upstream source on October 22, or earlier if a relevant source
change is observed. Retain the dated result until a new check supersedes it.
