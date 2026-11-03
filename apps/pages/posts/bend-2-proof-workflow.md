---
title: "Bend 2 Proofs: Check a Law and Test the Boundary"
description: "Try a tested Bend 2 proof workflow with separate laws, failure controls, and an honest comparison of --check-only and --verdict."
published_at: 2026-11-03
author: Built with Bend
keywords: [Bend 2 proofs, Bend 2 laws, Bend check-only, Bend verdict]
topics: [Bend 2, Proofs, Developer tools]
canonical_url: https://builtwithbend.com/blog/bend-2-proof-workflow
---

To check **Bend 2 proofs**, state the property in `LAWS.bend`, implement its witness in `PROOF.bend`, and check the proof file rather than the law file alone. Then deliberately break the example. A useful first workflow distinguishes an open goal, a rejected proof, an ordinary checker pass, and a second-kernel result instead of treating every green message as the same guarantee.

**Checked November 3, 2026:** Built with Bend ran the files below with **Bend 2.0.39 on Linux x86-64**. The ordinary checker accepted the completed proof and rejected three negative controls. The stronger `--verdict` command failed with a translation/kernel mismatch diagnostic. We therefore report an ordinary-checker result, **not a kernel-validated proof**. No native binary, GPU workload or performance benchmark was tested.

This guide is for developers reading Bend projects or trying their first law. It uses the [official versioned guide](https://github.com/bendlang/bend/blob/v2.0.39/guide/GUIDE.md#laws-and-proofs), with a small file-layout adaptation and additional failure checks. The arithmetic theorem is the guide's example, not a new mathematical result. The contribution here is the reproducible boundary test and the decision checklist for interpreting project claims.

## Workflow at a glance

1. [Identify the compiler](#version) and read its matching guide.
2. [Write a law](#law) whose meaning you can explain.
3. [Add a separate proof](#proof) and check its complete import graph.
4. [Run negative controls](#controls) without weakening the original law.
5. [Record the verdict boundary](#verdict), including failures.
6. [Apply the checklist to a real project](#projects).

<span id="version"></span>

## 1. Start with Bend 2, not the older HVM toolchain

You need a terminal, a text editor and an installed Bend 2 compiler. This walkthrough uses the [v2.0.39 release](https://github.com/bendlang/bend/releases/tag/v2.0.39). If you need to install it, choose the release archive matching your operating system and architecture and follow the official distribution instructions. We exercised the Linux x64 distribution; we did not repeat these checks on macOS or Linux ARM.

Select that release explicitly and make sure the `bend` executable on your PATH is the one you intend to use. Record the compiler before copying code:

```bash
bend version
bend --help
bend guide
```

Our version output was `bend 2.0.39`. Its help describes `--check-only` as checking the file and its imports without running anything. Do not assume a command from an older Bend tutorial has the same meaning. The [language and project guide](/blog/bend-programming-language) separates Bend 2 from the earlier Bend/HVM ecosystem.

An editor is optional for this exercise. If editor diagnostics disagree with the terminal, identify the compiler or bundled checker producing each result; the [Bend 2 editor comparison](/blog/bend-2-editor-tools) explains that distinction. Keep the terminal command and version in your record even when the editor offers a proof panel.

<span id="law"></span>

## 2. State a law you can read without its proof

Create a new directory for the exercise. Save this first file as **`LAWS.bend`**:

```text
import Base

law add_zero:
  for x: Nat
  {Nat.add(x, 0n) == x : Nat}
```

In words: for every natural number `x`, adding zero on the right returns `x`. `Nat` is the natural-number type; the `n` suffix identifies natural-number literals. The statement names its input domain and the equality to establish. It does not yet provide the witness that establishes it.

Check the law file by itself:

```bash
bend LAWS.bend --check-only
```

In our run this exited with status **1** and reported `1 TODO found` followed by “The code is incomplete, and not a valid proof yet.” That is the expected state of this open claim. A well-formed law is not the same as a completed proof.

The official convention separates human-owned specifications from implementations and proofs. For an application, `LAWS.bend` imports the code whose behavior it specifies; this small arithmetic example only needs `Base`. `PROOF.bend` imports the laws and fills them. Preserve that boundary when working with an agent: changing the specification to match broken code is a different action from proving the original requirement.

Before continuing, ask whether the law says what you actually want. A sorting law that checks order but never checks that elements are preserved leaves a different gap from an incorrect proof. A checker can only check the statement you supplied, not the unstated intention behind it.

<span id="proof"></span>

## 3. Add the witness in PROOF.bend

Save the following as **`PROOF.bend`** beside the law file:

```text
import Base
import ./LAWS.bend as Laws

def Laws.add_zero(x):
  match x:
    case 0n:
      {==}
    case 1n+p:
      %Laws.add_zero(p) : {1n+Nat.add(p, 0n) == 1n+_ : Nat}
      {==}
```

The `Laws` alias names the imported module. The definition `Laws.add_zero` fills the law declared there; it is not an unrelated function with a similar name. Local-file imports and separately filled laws are documented in the official [Modules reference](https://github.com/bendlang/bend/blob/v2.0.39/guide/GUIDE.md#modules).

The proof follows the natural number's structure. For zero, the two sides compute to the same term and `{==}` supplies reflexivity. For a successor `1n+p`, the recursive call supplies the statement for `p`; the `%` line uses that equality to rewrite the goal. The final reflexivity closes the resulting equality. This is the guide's case-analysis and induction pattern, not a test loop over a chosen range of integers.

Now check the proof file:

```bash
bend PROOF.bend --check-only
```

Our completed file exited with status **0** and printed:

```text
ALL PROOFS CHECK
Use --verdict for mathematical validity.
```

Retain both lines. Reporting only the first loses the compiler's explicit distinction between this check and its additional validation mode. There is no `main` in this file, and `--check-only` does not run an application. A passing check is not evidence that a native executable, browser interface or network service works.

<span id="controls"></span>

## 4. Make the check fail on purpose

Keep a copy of the two working files. Apply each change separately, run `bend PROOF.bend --check-only`, and restore the originals before trying the next case. Do not stack the mutations: otherwise an early error can hide the failure you meant to investigate.

| Case | Change | Observed result on 2.0.39 |
|---|---|---|
| Open law | Check `LAWS.bend` alone | Exit 1; one TODO |
| Completed witness | Use both complete files above | Exit 0; ordinary checker pass |
| Open witness | Replace the proof body with `?TODO` | Exit 1; one TODO |
| False statement | Change the law's right side from `x` to `0n`, keeping the original proof | Exit 1; expected/observed equality mismatch |
| Missing law import | Replace `PROOF.bend` with a program that only imports Base and returns 42 | Exit 1; requires `./LAWS.bend` |

For the open-witness case, the whole replacement file is:

```text
import Base
import ./LAWS.bend as Laws

def Laws.add_zero(x):
  ?TODO
```

The false statement would claim that adding zero to **every** natural number returns zero. Keeping the original witness makes the inconsistency visible in its successor case. Our diagnostic identified `Laws.add_zero` and displayed an expected equality ending in `0n`, versus an observed equality ending in `1n`. Preserve that diagnostic rather than summarizing it as “the compiler broke.”

For the missing-import control, use:

```text
import Base

def main() -> U32:
  42
```

With the original `LAWS.bend` still beside it, the file named `PROOF.bend` was rejected with `PROOF.bend must import ./LAWS.bend`. This checks a specific convention in this compiler release. It is not evidence that arbitrary filenames, repositories or CI configurations cannot accidentally omit their specifications.

These controls answer a practical review question: did the command actually include the law, and does the gate distinguish incomplete or incompatible evidence from the completed example? They do not audit the checker itself.

<span id="verdict"></span>

## 5. Keep --check-only and --verdict results separate

After restoring both complete files, run:

```bash
bend PROOF.bend --verdict
```

The official guide describes this mode as checking again with a small kernel with a proof in Lean. It also explicitly says that the translation read by that kernel is **not itself proved**. The [v2.0.39 checker entry point](https://github.com/bendlang/bend/blob/v2.0.39/bend2/main.ts#L887-L943) is the source reference for how this gate is invoked.

Neither mode turns unsafe or foreign-code dependencies into proved behavior. In this release, ordinary checking also rejects those dependencies in the proof's import graph; `--verdict` adds the independent kernel check. Keep a proof module's dependencies focused on the pure definitions it needs.

In our Linux run, the command exited **1**, reported `SOME PROOFS FAIL`, and included:

```text
parse error: expected '1'
```

It then described a mismatch between the TypeScript implementation and the formalized BendTT kernel, saying it could not validate the proofs. A separate minimal reflexivity example, `{0n == 0n : Nat}`, also failed through this mode with the same diagnostic prefix. That second observation narrows the investigation; it does not establish a root cause or prove that the induction step is responsible.

We also exercised the documented export command:

```bash
bend PROOF.bend -o PROOF.bendtt
```

It exited **0** and wrote a nonempty translation file. Export success did not make the failed `--verdict` check pass. Keep those outcomes separate too.

If you reproduce the mismatch, preserve your exact files, compiler version, platform, command and diagnostic. Investigate against upstream sources or a newer release as a new case. Do not silently remove `--verdict` from a gate that promises kernel validation, or describe this result as either a validated proof or a discovered false theorem. This walkthrough establishes neither.

<span id="projects"></span>

## 6. Read real Bend projects with a proof-boundary checklist

Now move from the arithmetic exercise to an application. These source-reading examples were reviewed on November 3; we did not build or recheck either project's proofs in this run.

**[Bendoom](/projects/bendoom/): trace one input rule.** Its [pinned `last_press` law](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/LAWS.bend#L43-L52) states that applying two updates to the same key is equivalent to applying only the second update, for the specified key-state arguments. Find `Laws.last_press` in the [corresponding witness file](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/PROOF.bend#L354). That is a concrete behavior to inspect; it does not establish every gameplay, audio or rendering property.

**[MyLSM](/projects/mylsm/): separate fixtures from quantified laws.** Its [key laws](https://github.com/FabianVegaA/mylsm/blob/eefd74145aedbd331acca297ca781888a3f6d56c/laws/Keys.bend) place concrete comparison fixtures beside a general `key_cmp_refl` claim. Ask whether a statement covers a particular value or arbitrary inputs, then inspect its [matching witnesses](https://github.com/FabianVegaA/mylsm/blob/eefd74145aedbd331acca297ca781888a3f6d56c/proofs/KeysProof.bend). The project's [formal-verification notes](https://github.com/FabianVegaA/mylsm/blob/eefd74145aedbd331acca297ca781888a3f6d56c/docs/standards/formal-verification.md) distinguish those evidence categories and exclude the filesystem and C/JavaScript effects from its laws' guarantees.

Follow the original repositories' current toolchain requirements rather than assuming this exercise's compiler is right for every project.

Use this reusable review card:

- **Statement:** Which exact law represents the behavior you care about? Read it before its witness.
- **Coverage:** Does it specify the whole requirement, or one invariant? What remains unstated?
- **Connection:** Does the checked file import the intended law and implementation?
- **Completeness:** Are there open goals, assumptions, unsafe definitions or foreign-code boundaries?
- **Checker:** Which compiler and command produced the result? Was the extra kernel mode exercised successfully?
- **Execution:** Which tests cover compiled behavior, external effects and integration? Keep those results separate from proof checking.
- **Reproduction:** Can another developer repeat the check from the recorded source revision and toolchain?

The two project suggestions are reading routes, not fresh certifications of their proofs or production readiness. A law about a pure state transition does not by itself establish that a socket, filesystem, graphics driver or deployment behaves correctly. The official guide treats host effects separately; inspect those boundaries in the actual project.

For a library import, combine this card with the [tested Bend 2 package workflow](/blog/bend-2-package-imports): preserve the package version and input representation as well as the compiler. For a larger application, start with one behavior and trace its law, witness and execution test before attempting a repository-wide conclusion.

The useful result is a precise statement you can defend: **these files passed this ordinary checker; these negative controls failed; this additional validation attempt did not succeed**. That is a better foundation for choosing a project to study than an unqualified “all proven” label.

<script type="application/ld+json">{"@context": "https://schema.org", "@type": "HowTo", "name": "Bend 2 Proofs: Check a Law and Test the Boundary", "step": [{"@type": "HowToStep", "name": "Identify Bend 2", "text": "Run bend version and read its matching guide.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#version"}, {"@type": "HowToStep", "name": "State the law", "text": "Save LAWS.bend and observe the incomplete claim.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#law"}, {"@type": "HowToStep", "name": "Check the witness", "text": "Save PROOF.bend and run --check-only.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#proof"}, {"@type": "HowToStep", "name": "Exercise failure controls", "text": "Test an open witness, false statement and missing law import separately.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#controls"}, {"@type": "HowToStep", "name": "Record additional validation", "text": "Attempt --verdict and report its actual result; this checked environment returned a mismatch.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#verdict"}, {"@type": "HowToStep", "name": "Review an application", "text": "Use the statement, coverage, connection, completeness, checker, execution and reproduction checklist.", "url": "https://builtwithbend.com/blog/bend-2-proof-workflow#projects"}]}</script>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Built with Bend", "item": "https://builtwithbend.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://builtwithbend.com/blog/"}, {"@type": "ListItem", "position": 3, "name": "Bend 2 Proofs: Check a Law and Test the Boundary", "item": "https://builtwithbend.com/blog/bend-2-proof-workflow"}]}</script>
