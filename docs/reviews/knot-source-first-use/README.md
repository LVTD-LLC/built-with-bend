# Knot source-built first use

Checked November 4, 2026. This extends the existing Knot listing, not the project’s
capabilities or production-readiness claims. Original catalog metadata, source
actions, public analytics identity and publication order stay unchanged.

## Reproduction and scope

- Source: [b914a71](https://github.com/MatheusBBarni/knot-node-tooling/tree/b914a71bbca46b7e2fe447d19a7a182e2b9ff715), unmodified.
- Compiler: Bend 2.0.24 Linux x64 archive, verified against the upstream
  [toolchain pin](https://github.com/MatheusBBarni/knot-node-tooling/blob/b914a71bbca46b7e2fe447d19a7a182e2b9ff715/toolchain.json).
- Host: Linux x64, glibc 2.36, Node.js 24.22.1, Clang 14.0.6 exposed as `clang`.
- Follow the linked README’s build instructions and compiler examples. The
  source build completed; version/help started; generated greet JavaScript
  printed `hello knot`; graph analysis listed two modules without missing imports.
- Installing npm 0.0.1 with lifecycle scripts disabled succeeded, but startup
  still failed for missing `GLIBC_2.38`. The October 28 observation is retained.
- Not the full upstream acceptance suite, Knot package operations, a proof/kernel
  check, other-platform/newer-compiler certification, benchmark or security audit.

The repository/slug guard remains unchanged. Content date advances only for
this exact listing. Preview screenshots cover mobile/desktop and both themes;
analytics requests were blocked during browser QA. Raw observations remain in
the existing private research store.

ReviewGate is waived by standing project authorization, not passed. CI and live
web/worker revision verification are still required before marking this shipped.
