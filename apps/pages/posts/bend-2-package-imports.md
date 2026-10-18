---
title: "Bend 2 Packages: Find and Import"
description: "Find a Bend 2 package with JendHub, inspect its input type, and check a versioned import with a worked example tested on two compilers."
published_at: 2026-10-18
updated_at: 2026-10-18
keywords: [Bend 2 packages, Bend 2 import, Bend libraries]
topics: [Bend 2, Packages]
author: Built with Bend
---

To use a **Bend 2 package**, find the function you need, inspect its source and input type, then copy its versioned import into a small program. Check that file before running it. This walkthrough follows a JendHub search to a byte-to-hex function and a known result, rather than stopping at an import line.

**Built with Bend checked this example on October 18, 2026, with Bend 2.0.35 and 2.0.37 on Linux.** Both returned `"42656e64"` for the ASCII text `Bend`. This is a worked example of one package, not a compatibility survey, performance benchmark or independent proof of its implementation.

The workflow is:

1. [Search for an operation](#find), not just a package name.
2. [Read the definition and its input type](#inspect).
3. [Copy the exact package version and file path](#import).
4. [Check the program and compare its result](#check) with an expected value.

<span id="generation"></span>

## Confirm you are using Bend 2

You need an installed Bend 2 compiler, a terminal and a text editor. Start with `bend version` and `bend guide`; they identify the compiler and show its matching reference. The commands below follow the official [2.0.35 guide](https://github.com/bendlang/bend/blob/v2.0.35/guide/GUIDE.md#modules) and [2.0.37 guide](https://github.com/bendlang/bend/blob/v2.0.37/guide/GUIDE.md#modules). They are not instructions for the older Bend 1/HVM toolchain.

<figure style="margin:2rem 0;">
<svg role="img" aria-labelledby="bend-package-flow-title bend-package-flow-desc" viewBox="0 0 360 310" style="display:block;width:100%;max-width:420px;height:auto;margin:auto;color:var(--ink);font-family:system-ui,sans-serif;">
<title id="bend-package-flow-title">From a package search to a checked example</title>
<desc id="bend-package-flow-desc">Search finds candidate definitions. Source inspection identifies the type and import. The local compiler checks the program. Comparing its output checks the example's result. Each stage answers a different question.</desc>
<g style="fill:var(--soft);stroke:var(--line);"><rect x="1" y="1" width="358" height="55" rx="6"/><rect x="1" y="77" width="358" height="55" rx="6"/><rect x="1" y="153" width="358" height="55" rx="6"/><rect x="1" y="229" width="358" height="55" rx="6"/></g>
<g fill="currentColor" font-size="15"><text x="18" y="34">Search: which definition might fit?</text><text x="18" y="110">Source: which type, version and file?</text><text x="18" y="186">Compiler: does this program check?</text><text x="18" y="262">Result: does this example agree?</text></g>
<path d="M180 58v14m-4-4 4 4 4-4M180 134v14m-4-4 4 4 4-4M180 210v14m-4-4 4 4 4-4" style="fill:none;stroke:var(--accent);stroke-width:2;"/>
<text x="18" y="305" font-size="12" style="fill:var(--muted);">Built with Bend · checked October 18, 2026</text>
</svg>
<figcaption style="color:var(--muted);">A search result is a candidate. A checked, observed example answers a narrower question than package-wide compatibility.</figcaption>
</figure>

<span id="find"></span>

## 1. Find a definition for your task

Suppose you want to display bytes as hexadecimal text. A package name alone does not tell you whether its function accepts a string, a linked list, an array or a custom byte buffer. Search for the operation first: [hex encode bytes in JendHub](https://jend.leeeet.dev/search.txt?q=hex%20encode%20bytes).

[JendHub](/projects/jendhub/) searches definitions from Base and packages on BendHub. Its [agent instructions](https://jend.leeeet.dev/llms.txt) describe searching in plain language and opening a result's source before choosing it. The text endpoint is useful for a terminal or agent; the [website](https://jend.leeeet.dev/) also provides a browser interface.

In the checked response, `Bytes.to_hex` appeared in more than one package. We selected the definition in **bend-kit-bytes 0.3.2.0**, rather than assuming that every result called `to_hex` was interchangeable. The result supplied a source link, a function signature and an import line. Search order can change, so use that identity to follow the example, not “click the second result.”

For broader browsing, [Bend Packages](/projects/bend-packages/) is another discovery surface. It is a community catalog, not the compiler or official hub. Use a catalog to find a library, definition search to locate an operation, and the original sources to decide what to call. None of those steps replaces checking your own program.

<span id="inspect"></span>

## 2. Inspect the type before copying the call

Open the [versioned Bytes source](https://jend.leeeet.dev/src/bend-kit-bytes@0.3.2.0/bytes.bend?def=to_hex). Its `to_hex` definition takes the package's `Bytes` type and returns a `String`. The same file provides `from_string`, which constructs that byte buffer from a string. It also imports `bend-kit-int@0.2.0.0/int.bend`: this is not a dependency-free snippet.

Those details explain the complete expression used below. `Bytes.from_string("Bend")` produces the input expected by `Bytes.to_hex`. Passing `"Bend"` directly is a different program, even though the task sounds like “turn this text into hex.”

**Keep this example ASCII.** The reviewed `from_string` implementation keeps the low eight bits of each character. Do not treat it as a general UTF-8 encoder or substitute arbitrary Unicode text and expect this recipe to preserve the intended bytes. For non-ASCII data, identify the encoding you need and inspect the appropriate conversion before using the result.

Hex encoding is neither encryption nor hashing.

Also separate this exact package release from its wider source repository. A successful import of `bend-kit-bytes@0.3.2.0` does not establish that every current bend-kit module works with the same compiler. The package version, compiler version and imported file are separate pieces of the reproduction.

<span id="import"></span>

## 3. Copy the version and file into a small program

Save the following as **`hex.bend`**. The import syntax comes from the official guides linked above; the package path and calls come from the versioned Bytes source. Built with Bend checked this complete example with both named compiler versions.

```python
import Base
import bend-kit-bytes@0.3.2.0/bytes.bend as Bytes

def main() -> String:
  Bytes.to_hex(Bytes.from_string("Bend"))
```

`import Base` supplies the standard library used by this example. Keep it alongside the separate third-party package import.

The package import names four things worth keeping together: package `bend-kit-bytes`, version `0.3.2.0`, file `bytes.bend`, and the local alias `Bytes`. The alias is the name this file uses for imported definitions. It is not the compiler version and does not mean that a module with the same alias from another package has the same interface.

The official Modules reference also documents imports by content hash. A named, versioned import identifies a package through the hub; a hash import identifies its content directly. For this walkthrough, keep the returned named import intact. Do not guess a hash, shorten the version or replace the file path with the package name alone.

Bend fetches hub imports as part of loading them. The source shown by a search service is useful for inspection, but this example still uses the compiler's normal package import; it does not download code from JendHub into your project. An available source page is therefore not proof that your machine can reach every required package dependency.

<span id="check"></span>

## 4. Check first, then compare the result

The `--help` output from both tested compilers lists `--check-only` for checking without running a program. This command was exercised with the [2.0.35](https://github.com/bendlang/bend/releases/tag/v2.0.35) and [2.0.37](https://github.com/bendlang/bend/releases/tag/v2.0.37) releases. From the directory containing `hex.bend`, use:

```bash
bend hex.bend --check-only
```

For this file, the ordinary compiler check printed `ALL PROOFS CHECK`, followed by its reminder about `--verdict`. That message is not a report that we ran the independent kernel check. We did not use `--verdict` for this walkthrough, and a passing example does not prove all behavior of the package.

Next, run the file using the same compiler, following the guide's ordinary file invocation:

```bash
bend hex.bend
```

The observed result on both tested versions was `"42656e64"`, including the displayed string quotes. The expected value was also checked independently with a standard hexadecimal conversion of the ASCII bytes for `Bend`. Keep a known input and expected output when trying another function; “it printed something” is a weak check.

Here `main` returns a value, so Bend normalizes that value and prints it, as described in the official guide. This is **not a native-binary build, GPU run or speed test**. It is enough to check that this small import-and-call example produces the expected result in the tested environments. Larger programs, IO, other package releases and other platforms need their own checks.

<span id="troubleshoot"></span>

## Troubleshooting questions

### Why does the checker reject a string?

Read the failure before changing dependencies. During this walkthrough we deliberately replaced the inner conversion with a raw string. On both tested compilers, the check failed with **expected `Bytes.Bytes`, observed `String`**. Restoring `Bytes.from_string("Bend")` supplied the required type. A visible function name is not enough to determine its calling convention.

### What should I check after an import error?

For an import or fetch error, compare the exact package name, version and path with the source you inspected. Then distinguish a failed network request from a compiler diagnostic. Do not silently substitute a different library and call the original example fixed. Record the compiler version and first error so you can reproduce the problem.

### Why can my editor disagree with the terminal?

If the terminal succeeds but your editor complains, check which compiler or language server is producing the message. The [Bend 2 editor and LSP guide](/blog/bend-2-editor-tools) explains why an installed compiler and an editor's bundled checker can differ. Reinstalling unrelated tools before identifying that boundary makes the result harder to explain.

<span id="method"></span>

## Keep the reproduction small

When sharing a result, include the complete file, the output of `bend version`, the exact command and the first diagnostic or returned value. Separate the compiler's output from your interpretation. If you change the package version, input or imported file, mark that as a new case instead of overwriting the record of the working one.

Our check used the public search response and versioned source, then the ordinary local compiler. It did not test a deliberately empty package cache or measure network downloads. Repeated runs are therefore not evidence of cold-start behavior. Preserve that distinction if you use the example to investigate a fetch failure on another machine.

## What to try next

Repeat the same process with an operation your project actually needs: search, inspect the signature and source, keep the exact import, and test a small known case. Inspect dependencies and data representation before expanding the example. A useful search result saves discovery work; it does not remove the need to understand the function.

For examples of larger applications and experiments, return to [what people build with Bend 2](/blog/bend-programming-language). For this task, success is smaller and concrete: you found an existing definition, understood the input it expects, and checked a program that calls it. Keep that working file and its compiler version as your starting point.


<script type="application/ld+json">{"@context": "https://schema.org", "@type": "HowTo", "name": "Bend 2 Packages: Find and Import", "description": "Find a Bend 2 package with JendHub, inspect its input type, and check a versioned import with a worked example tested on two compilers.", "step": [{"@type": "HowToStep", "name": "Confirm you are using Bend 2", "text": "Run bend version and read bend guide for the installed compiler.", "url": "https://builtwithbend.com/blog/bend-2-package-imports#generation"}, {"@type": "HowToStep", "name": "1. Find a definition for your task", "text": "Search JendHub for hex encode bytes and identify the bend-kit-bytes 0.3.2.0 result.", "url": "https://builtwithbend.com/blog/bend-2-package-imports#find"}, {"@type": "HowToStep", "name": "2. Inspect the type before copying the call", "text": "Inspect to_hex and from_string in the versioned bytes.bend source; keep this example ASCII.", "url": "https://builtwithbend.com/blog/bend-2-package-imports#inspect"}, {"@type": "HowToStep", "name": "3. Copy the version and file into a small program", "text": "Save the complete hex.bend example with the exact named package import and Bytes alias.", "url": "https://builtwithbend.com/blog/bend-2-package-imports#import"}, {"@type": "HowToStep", "name": "4. Check first, then compare the result", "text": "Check hex.bend with --check-only, then run it and compare the result with 42656e64.", "url": "https://builtwithbend.com/blog/bend-2-package-imports#check"}]}</script>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Built with Bend", "item": "https://builtwithbend.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://builtwithbend.com/blog/"}, {"@type": "ListItem", "position": 3, "name": "Bend 2 Packages: Find and Import", "item": "https://builtwithbend.com/blog/bend-2-package-imports"}]}</script>

<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "Why does the checker reject a string?", "acceptedAnswer": {"@type": "Answer", "text": "The reviewed to_hex function expects the package Bytes type, not a String. For the ASCII example, Bytes.from_string(\"Bend\") supplies that type. Passing the raw string failed with expected Bytes.Bytes, observed String on both tested compilers."}}, {"@type": "Question", "name": "Why can my editor disagree with the terminal?", "acceptedAnswer": {"@type": "Answer", "text": "Identify the compiler or language server producing the diagnostic. An editor using a bundled checker can differ from the separately installed compiler used by your terminal. Check that boundary before reinstalling tools."}}]}</script>
