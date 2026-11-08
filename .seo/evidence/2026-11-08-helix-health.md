# Helix first-use resource check — November 8, 2026

## Purpose and sources

The existing editor guide owns editor-choice intent. Its Helix section helps
readers distinguish loaded syntax resources from separately configured compiler
feedback; it is not another generic editor article or a compatibility ranking.

- Packaging: https://github.com/davidawad/helix-bend/tree/093e204a8a9b87cd16d3f0801252eb3e97321901
- Installer grammar: https://github.com/davidawad/tree-sitter-bend2/tree/8ad225d157f7409b59c995a11a86908123b9b20c
- Config grammar: https://github.com/davidawad/tree-sitter-bend2/tree/e25608da7574a221827766847ed9366f8957fe18
- Helix release: https://github.com/helix-editor/helix/releases/tag/25.07.1
- Language configuration: https://docs.helix-editor.com/languages.html

## Bounded method and observations

Linux x86-64/glibc2.36; official Helix25.07.1 reports a05c151b;
Tree-sitter0.27.1. The latter emitted a weak GLIBC2.39 warning but its version
and installer build completed; this is not portable-binary certification.
An explicit temporary XDG_CONFIG_HOME kept personal editor configuration intact.
Run the unmodified pinned installer with hx and tree-sitter available on PATH.
For this fresh test directory only, copy the supplied languages.toml into
its Helix config, then run hx --health bend. Parser and highlight queries present;
textobject and indent queries absent; no configured LSP/formatter/debugger.

For a second, bounded grammar build, add the documented top-level
`use-grammars = { only = ["bend2"] }` selector to this temporary config,
then run hx --grammar fetch and hx --grammar build. Git confirms e25608d,
and a second hx --health bend has the same availability results. An initial
unfiltered fetch was stopped because Helix merges built-in grammar entries;
it is not represented as a completed all-grammar check. No global editor files
were changed. The installer and later configured build do not select one uniform
revision. Do not infer identical parse/color behavior from matching health output.

No interactive-color correctness, full grammar suite, compiler, LSP, formatter,
debugger, proof, security, performance, other-platform or production certification.
The public section describes health checks only. Previous dated editor reviews
and publication/title/metadata remain intact. Recheck sources November15 or
following a relevant upstream change.
