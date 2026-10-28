# Knot 0.0.1: installation is not executable startup

Checked October 28, 2026. This is a bounded first-use observation, not a
recommendation or compatibility/security certification.

## Sources

- [Published wrapper metadata](https://registry.npmjs.org/@matheusbbarni/knot/0.0.1)
- [Pinned README](https://github.com/MatheusBBarni/knot-node-tooling/blob/b914a71bbca46b7e2fe447d19a7a182e2b9ff715/README.md)

The wrapper's published README says the command also needs curl, gzip and zlib;
its manifest declares Node>=18 and darwin-arm64/linux-x64 optional binaries.
Source-build prerequisites are distinct from published-wrapper requirements.
The older npm-distribution design document still calls itself a plan; it is not
used as evidence of current publication.

## Attempt and scope

Installed `@matheusbbarni/knot@0.0.1` in a fresh disposable prefix, with lifecycle
scripts disabled (`--ignore-scripts`), no global install, an empty test home,
and no provider credentials passed to the process. npm returned success.
The wrapper tarball matched its registry SHA-512 integrity. The native Linux
binary's SHA-256 matched the wrapper manifest:
`d3ac2fc9752acede50a840e419f7bc5e769affc95743aa21b38aaf21c41f3ace`.

Host: Linux x64, glibc 2.36, Node.js 24.21.0. Both `knot --version` and
`knot --help` returned exit 1 with `GLIBC_2.38 not found`. The native loader
failed before Knot started. Do not describe npm's success as a working CLI.

No global runtime/compiler/system-library update was attempted. Other hosts,
macOS, source builds, package operations, proofs and performance are untested.
A newer glibc is not established as sufficient. No workaround was certified.

## Public intervention

Add a compact source-discovery section after original sources on the exact
Knot repository-bound listing. Preserve its description, publication/sort date,
metadata, original project actions and public analytics identity. Only this
section's content date updates. No database migration or source-row rewrite.
Purpose: help developers reach original versioned release/build information
with an honest failed-first-use boundary, not expand to a generic Knot article.

Source recheck November 4; acquisition/source-intent outcome reads November 18
and 25 after final GSC data is available. Existing October 14 correction outcome
windows remain November 4/11. Overlapping changes prevent clean causal attribution.
