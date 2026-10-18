---
title: "Bend 2 Editors: VS Code and LSP"
description: "Choose Bend 2 editor tools by compiler setup: compare VS Code extensions, the standalone language server, version limits, and checks before you build."
published_at: 2026-10-11
updated_at: 2026-10-18
keywords: [Bend 2 editor, Bend VS Code, Bend language server]
topics: [Bend 2, Editor tools]
author: Built with Bend
---

Choose a **Bend 2 editor** by deciding which compiler should check your code. Nuxyel's VS Code extension connects to your installed Bend toolchain and adds proof-oriented workflows. Kbrianps's extension packages a language server with its own compiler snapshot. The standalone server offers another route for editors that speak LSP.

That distinction matters more than a screenshot of colored syntax. An editor can recognize a file without checking it with the compiler you use to build the project.

*Sources checked October 11, 2026: Nuxyel 1.0.1, kbrianps 0.1.3 and bend2-lsp 0.1.1. This is a source-and-documentation comparison, not a hands-on compatibility test or a ranking of every Bend extension.*

<nav aria-label="On this page">
<p><strong>In this guide:</strong> <a href="#choose">Choose a path</a> · <a href="#nuxyel">Nuxyel</a> · <a href="#kbrianps">Kbrianps</a> · <a href="#standalone">Standalone LSP</a> · <a href="#troubleshooting">Troubleshooting</a> · <a href="#questions">Questions</a> · <a href="#method">Method</a></p>
</nav>

<span id="choose"></span>

## Choose by the work you need to do

| Your task | Start by evaluating | Compiler boundary |
| --- | --- | --- |
| Check, build and inspect proofs in VS Code | Nuxyel | Separately installed Bend |
| Add packaged diagnostics and formatting to VS Code | Kbrianps | Compiler bundled with its language server |
| Connect another LSP-capable editor | Standalone bend2-lsp | Bundled compiler; separate Node runtime |

The table is a decision aid, not a promise that any particular host works. Check the exact extension ID and release, then the runtime and compiler requirements below. These projects have different settings despite sharing the `.bend` file extension.

If you are still deciding what to build, start with [five Bend 2 projects to explore](/blog/bend-programming-language). This guide addresses the next question: which editing setup fits the way you want to work?

<figure style="margin:2rem 0;">
<svg role="img" aria-labelledby="bend-2-editor-tools-title bend-2-editor-tools-desc" viewBox="0 0 360 306" style="display:block;width:100%;max-width:420px;height:auto;margin:auto;color:var(--ink);font-family:system-ui,sans-serif;">
<title id="bend-2-editor-tools-title">Two routes from an editor to a Bend compiler</title>
<desc id="bend-2-editor-tools-desc">Nuxyel sends compiler-backed work to the installed Bend executable. Kbrianps uses bend2-lsp and its bundled compiler for analysis. These can be different compiler versions.</desc>
<rect x="1" y="1" width="358" height="132" rx="6" style="fill:var(--soft);stroke:var(--line);"/>
<text x="18" y="30" font-size="17" font-weight="600" fill="currentColor">Nuxyel in VS Code</text>
<text x="18" y="59" font-size="14" fill="currentColor">Compiler commands</text>
<path d="M28 72 V92 M23 87 L28 92 L33 87" style="fill:none;stroke:var(--accent);stroke-width:2;"/>
<text x="48" y="98" font-size="15" fill="currentColor">Your installed Bend executable</text>
<rect x="1" y="149" width="358" height="132" rx="6" style="fill:var(--soft);stroke:var(--line);"/>
<text x="18" y="178" font-size="17" font-weight="600" fill="currentColor">Kbrianps in VS Code</text>
<text x="18" y="207" font-size="14" fill="currentColor">bend2-lsp analysis</text>
<path d="M28 220 V240 M23 235 L28 240 L33 235" style="fill:none;stroke:var(--accent);stroke-width:2;"/>
<text x="48" y="246" font-size="15" fill="currentColor">The server's bundled compiler</text>
<text x="18" y="301" font-size="12" style="fill:var(--muted);">Built with Bend · source review, October 11, 2026</text>
</svg>
<figcaption style="color:var(--muted);">The compiler behind editor feedback may differ from the one behind your build.</figcaption>
</figure>

<span id="nuxyel"></span>

## Nuxyel: use your installed toolchain

[Nuxyel's Bend 2 extension](https://github.com/nuxyel/bend2-vscode/releases/tag/v1.0.1) is the option to examine when you want compiler commands and proof navigation alongside editing. Its documented features include checking, building and running files, plus a Proof Explorer. The extension uses its own language-server implementation; it is not a different skin around don2e4's server.

Its extension ID is **`nuxyel.bend2-vscode`**. For compiler-backed operations, Bend must be available in the desktop or remote workspace environment. The [1.0.1 manifest](https://github.com/nuxyel/bend2-vscode/blob/06bcbaf32789a213172dbcc0379880a3fa4d8c6c/apps/vscode/package.json) defines the `bend2.executablePath` setting, which selects the executable or launcher; its default is `bend`. The separate `bend2.executableArgs` setting supplies launcher arguments. Those are Nuxyel settings, not configuration for kbrianps.

This makes the installed compiler an explicit part of the setup. It is useful when a repository specifies a toolchain and you want editor operations to call it. It also means that installing the extension alone is not enough to build that repository. Confirm the executable the extension found, especially when a remote workspace has a different environment from your local terminal.

The [1.0.1 support policy](https://github.com/nuxyel/bend2-vscode/blob/06bcbaf32789a213172dbcc0379880a3fa4d8c6c/docs/SUPPORT.md) declares Bend 2.0.28 or newer within the 2.x major line and VS Code 1.90 or newer. It covers Linux and macOS, with Windows compiler use through WSL or a remote workspace. The documented compiler test matrix names 2.0.28 and 2.0.32. That matrix is narrower than the support policy: it does not establish that every later release was tested.

Compiler diagnostics run on save by default. Parser-backed editing can work in VS Code Web, but compiler, build, execution and process-dependent proof commands require a desktop or remote host. A browser editor opening the file is not evidence that it can launch Bend.

For the project summary and original source, see [Bend 2 for VS Code by Nuxyel](/projects/bend-2-for-vs-code-nuxyel/).

<span id="kbrianps"></span>

## Kbrianps: a packaged editing path

The extension ID is **`kbrianps.bend2`**. Its [0.1.3 source manifest](https://github.com/kbrianps/bend-vscode/blob/81ba2c93f8fb879d53d9a3638eddc33683e48035/package.json) declares a dependency on don2e4's bend2-lsp, and its [README](https://github.com/kbrianps/bend-vscode/blob/81ba2c93f8fb879d53d9a3638eddc33683e48035/README.md) describes highlighting, diagnostics, hover and formatting through the bundled server. Published metadata is available on [Open VSX](https://open-vsx.org/extension/kbrianps/bend2).

Its appeal is the packaged editing path. You do not need a separate Bend source checkout for that server's diagnostic analysis. But the compiler bundled with the server is a particular source snapshot, not an alias for whichever `bend` executable your terminal finds. Upgrading your command-line compiler does not, by itself, update the compiler inside the language-server package.

The setting `bend.server.path` chooses a language-server executable or JavaScript entry point. Leaving it empty uses the extension's bundled server first, then a server on PATH. It does **not** select the Bend build compiler. Do not paste Nuxyel's executable settings into this extension and expect the same effect.

There is also a runtime boundary worth checking before relying on it. The extension manifest accepts VS Code from 1.82, while the [bend2-lsp 0.1.1 manifest](https://github.com/don2e4/bend2-lsp/blob/d85e556febcd3e787c48f4558b5f89a34729626d/package.json) declares Node.js 26.9 or newer. We have not tested that combination across editor releases. These declarations alone do not prove that every accepted editor can run the bundled checker, or that installing a newer system Node automatically changes the runtime used inside VS Code.

Evaluate this path for editing feedback, then check the project's build or run separately with the required Bend toolchain. The reviewed extension does not register a standalone application build/run command.

<span id="standalone"></span>

## Standalone bend2-lsp: bring your own editor integration

The [bend2-lsp project](/projects/bend2-lsp/) offers the same server outside the kbrianps extension. Its [0.1.1 README](https://github.com/don2e4/bend2-lsp/blob/d85e556febcd3e787c48f4558b5f89a34729626d/README.md) includes integration examples for Neovim, Helix and Emacs with Eglot. Those are maintainer examples, not integrations tested for this article.

The standalone package declares **Node.js 26.9 or newer**. It bundles a Bend compiler and Base library for analysis, so a separate compiler checkout is unnecessary for that purpose. If you already maintain an LSP configuration and want diagnostics, formatting, hover and import navigation without changing editors, this is the route to investigate.

Two limits affect what you should expect. Compiler analysis applies to saved `file:` documents; an untitled buffer still gets more limited features such as lexical diagnostics and syntax hover. Save the file before judging whether compiler checking is working. Also, the server deliberately does not provide inferred local-variable type hover. Silence over a local variable is not necessarily a broken connection.

Bundled analysis does not mean every project can be checked offline. Missing hash-package imports may be downloaded and cached using the compiler's package configuration. Check that behavior against your environment before opening a project with external package imports. For the package side of that check, follow [how to find and check a Bend 2 package import](/blog/bend-2-package-imports).

<span id="troubleshooting"></span>

## When the editor and terminal disagree

Before changing correct-looking code to satisfy an editor, identify where the message came from. The following is a troubleshooting checklist for your setup, not a claim that we reproduced a failure in these tools.

1. **Record the identities.** Note the extension publisher, extension version, host mode and project toolchain requirement. “Bend support” is not a precise enough name. Bend 1 and Bend 2 tools may both recognize a `.bend` filename; the [official Bend repository](https://github.com/bendlang/bend#limitations) distinguishes the language generations.
2. **Identify the checker.** With Nuxyel, inspect the selected Bend executable and reported version. With the bundled-server path, inspect the installed server package and its compiler provenance. Do not assume your terminal and editor use the same compiler because both display the word Bend.
3. **Use the same saved file.** Save your changes, check the project's expected working directory and imports, then compare feedback. An untitled document or unsaved buffer is a different input from the file your terminal reads.
4. **Separate editing from execution.** Successful formatting demonstrates a formatter response, not a successful build. A missing hover result says little about runtime behavior. Run the project's documented check and build steps separately.

For an initial smoke check, use a small, disposable copy of a file accepted by the project's required compiler. Introduce an obvious syntax error, confirm that diagnostics appear, then restore the file and confirm they clear. This checks that the feedback loop is active; it does not certify complete language compatibility or prove the application correct. Test one extension at a time so competing providers do not obscure the result.

<span id="questions"></span>

## Common questions

### Does a Bend 2 language server replace the compiler?

Not for building your application. Don2e4's server bundles a compiler for diagnostic analysis, while Nuxyel calls an installed Bend toolchain for compiler-backed work. Keep the project's own build instructions and compiler requirements as a separate check.

### Does a proof explorer guarantee a verified program?

No. A proof interface helps you inspect or invoke proof-related work. Its presence does not establish which checker ran, what properties were stated, or whether every required proof passed. Follow the project's proof procedure and inspect its actual result rather than treating an editor panel as the verdict.

### Are these the only Bend 2 editor options?

No. This comparison follows two VS Code paths and the standalone server that explains one of them. [Browse the developer-tool projects](/?category=tools) for other editors and integrations, then verify each project's current requirements. Built with Bend is an independent directory, not the vendor of these extensions.

<span id="method"></span>

## How this comparison was checked

We compared release or package metadata with repository documentation and configuration/source wiring. The useful distinction is the path from editor feedback to compiler: installed toolchain versus bundled analysis snapshot. We did not install these extensions, benchmark them, or test the listed host combinations. Links to versioned sources preserve what informed this comparison; upstream requirements can change.

Choose one path, verify it against a small project, then follow the original repository for setup details. If you build another useful Bend 2 tool, [submit your project](/submit/) so other developers can find its source.

<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Blog","item":"https://builtwithbend.com/blog/"},{"@type":"ListItem","position":2,"name":"Bend 2 Editors: VS Code and LSP","item":"https://builtwithbend.com/blog/bend-2-editor-tools"}]}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Does a Bend 2 language server replace the compiler?","acceptedAnswer":{"@type":"Answer","text":"Not for building your application. Don2e4's server bundles a compiler for diagnostic analysis, while Nuxyel calls an installed Bend toolchain for compiler-backed work. Keep the project's own build instructions and compiler requirements as a separate check."}},{"@type":"Question","name":"Does a proof explorer guarantee a verified program?","acceptedAnswer":{"@type":"Answer","text":"No. A proof interface helps you inspect or invoke proof-related work. Its presence does not establish which checker ran, what properties were stated, or whether every required proof passed. Follow the project's proof procedure and inspect its actual result rather than treating an editor panel as the verdict."}},{"@type":"Question","name":"Are these the only Bend 2 editor options?","acceptedAnswer":{"@type":"Answer","text":"No. This comparison follows two VS Code paths and the standalone server that explains one of them. Browse the developer-tool projects for other editors and integrations, then verify each project's current requirements. Built with Bend is an independent directory, not the vendor of these extensions."}}]}</script>
