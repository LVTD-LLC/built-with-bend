# Bend 2 package-import example — October 18, 2026

Scope: the source-backed tutorial `/blog/bend-2-package-imports`; no adoption, speed, all-package compatibility or mathematical-validity claim.

## Sources and observed method

- Official [2.0.35 guide](https://github.com/bendlang/bend/blob/v2.0.35/guide/GUIDE.md#modules) and [2.0.37 guide](https://github.com/bendlang/bend/blob/v2.0.37/guide/GUIDE.md#modules): named/versioned imports, aliases and value-returning main normalization. Each release CLI `--help` lists `--check-only`; this flag is not attributed to the guide.
- [JendHub instructions](https://jend.leeeet.dev/llms.txt), [task search](https://jend.leeeet.dev/search.txt?q=hex%20encode%20bytes), [versioned source](https://jend.leeeet.dev/src/bend-kit-bytes@0.3.2.0/bytes.bend?def=to_hex): exact import, required Bytes type and `from_string`. Source includes bend-kit-int@0.2.0.0 dependency; conversion retains each character's low eight bits, so the example is deliberately ASCII.
- Executed ordinary check and run with Bend 2.0.35 and 2.0.37 on Linux x64: both exit 0; returned string is `"42656e64"`. Independent Python ASCII hex conversion agrees. A distinct verifier re-ran both cases and inspected return codes.
- Deliberate negative case `Bytes.to_hex("Bend")`: both compilers exit 1, expected Bytes.Bytes, observed String.
- The isolated 2.0.37 archive matches the upstream release digest `84c32465a39bc9ac315eade23f470cb8db03153dc860f89564fcfec153c3e445`. No global compiler or site infrastructure update.

## Reproduce

Use the complete `hex.bend` block in the tutorial with either exact compiler above. Run `bend version`, `bend hex.bend --check-only`, then `bend hex.bend`. Replace only the argument with a raw String to reproduce the input-type failure. Do not publish packages.

This test did not exercise --verdict, native compilation, IO, GPU execution, an empty cache, or every package/version/platform. Public search/source service state can change. Recheck the source and example October 25 before expanding compatibility claims.

## Publication contract

Existing Markdown route, metadata, sitemap and optional opt-in component reused. Existing editor-guide publication date/title remain unchanged; its modification date reflects the added link. Blog hub and editor guide provide two discovery pages. No analytics identities, private research or source responses in this change. ReviewGate waived under standing SEO authorization, not passed. CI and live verification remain required.
