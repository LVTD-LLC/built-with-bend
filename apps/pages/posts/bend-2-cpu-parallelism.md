---
title: "Bend 2 CPU Parallelism: First Checks"
description: "Try Bend 2 CPU parallelism with a checked range-sum example, two deliberately wrong partitions, and a checklist for evaluating real projects."
published_at: 2026-11-16
author: Built with Bend
keywords: [Bend 2 CPU parallelism, Bend native compilation, Bend parallel calls]
topics: [Bend 2, Parallel computing, Developer tools]
---

To try **Bend 2 CPU parallelism**, write independent calls with the parallel-call notation, compile a native binary, and compare its result at different thread counts. Check against an answer obtained independently, too. Two implementations can agree because they contain the same mistake.

**Checked November 16, 2026:** Built with Bend ran the example and both deliberate mistakes below with the official **Bend 2.0.40 Linux x64** release and clang 14. Each program was checked, evaluated through the CLI, compiled, and run natively at one, two and four requested CPU threads with GPU execution disabled. These are result checks, not timing measurements or evidence of actual multicore utilization. No GPU or `--verdict` validation was performed.

This walkthrough answers a narrower question than “is Bend fast?”: can you identify the work being split and catch a bad split before measuring it? It is useful preparation for reading a compute-oriented project in the [Bend directory](/), especially one that has several execution targets.

Follow the exercise:

1. [Record the compiler and target](#versions).
2. [Write a range sum with two call styles](#partition).
3. [Run the native CPU checks](#native).
4. [Make two wrong partitions](#controls).
5. [Use the result when choosing a project](#projects).

<span id="versions"></span>

## 1. Keep Bend 2 CPU parallelism separate from older Bend

Use a terminal, a text editor, Python 3 for the optional assertion below, and a native C compiler. Start by identifying your executable:

```bash
bend version
bend guide
```

Our compiler reported `bend 2.0.40`. To reproduce that version, choose your platform's archive from the [official 2.0.40 release](https://github.com/bendlang/bend/releases/tag/v2.0.40), verify its published SHA-256, and follow its setup instructions. We extracted a separate copy rather than replacing the machine's existing compiler. Our Linux x64 archive matched `c9ff8d67bd903fb6ad9a26b43d8a62c01021de82a44d55ce4a3dcd4732113d6b`. We did not test the other platform archives.

The [versioned compiler's native-build code](https://github.com/bendlang/bend/blob/v2.0.40/bend2/main.ts#L414-L490) supports a CPU build with clang 14 or newer. We selected `CC=clang-14`. A GPU build has additional requirements; this program does not use a GPU-marked call.

Older Bend tutorials can describe a different language and runtime. The [BendRT design document](https://github.com/bendlang/bend/blob/v2.0.40/bend2/docs/BendRT/main.typ) distinguishes Bend 2's runtime from the interaction-net approach. Do not mix HVM-era installation commands with this exercise. The [language and project introduction](/blog/bend-programming-language) gives that version distinction more context.

Also distinguish checking from native execution. The [2.0.40 CLI implementation](https://github.com/bendlang/bend/blob/v2.0.40/bend2/main.ts#L1099-L1109) normalizes a value-returning `main` in the checker; an `IO` entry point takes a compiled execution path. Our example returns a pair of values. Its plain CLI result is a convenient reference, not a native-thread measurement.

<span id="partition"></span>

## 2. Split a range, not the meaning of the calculation

Save this as `reduction.bend` in a new working folder:

```python
import Base

def sum_seq(+depth: Nat, +start: U32) -> U32:
  match depth:
    case 0n:
      start
    case 1n+p:
      half = U32.shln(1, p)
      left = sum_seq(p, start)
      right = sum_seq(p, (start + half : U32))
      (left + right : U32)

def sum_par(+depth: Nat, +start: U32) -> U32:
  match depth:
    case 0n:
      start
    case 1n+p:
      half = U32.shln(1, p)
      left right = sum_par(p, start) sum_par(p, (start + half : U32))
      (left + right : U32)

def main() -> U32 & U32:
  (sum_seq(6n, 0), sum_par(6n, 0))
```

This is a small range-partition exercise, not an efficient way to calculate an arithmetic series. At depth zero, a leaf returns its starting number. At each larger depth, the left call covers the first half and the right call starts after it. With depth six and start zero, the leaves cover 0 through 63. Their sum is **2016**, independently calculated as `63 × 64 ÷ 2`.

The functions deliberately keep the same partitioning algorithm. In `sum_seq`, the recursive calls use separate bindings. In `sum_par`, this line uses Bend's parallel-call notation:

```python
left right = sum_par(p, start) sum_par(p, (start + half : U32))
```

The `&` in the return type describes a pair; it is not the parallel-call operator. The `+` annotations permit repeated use of the inputs. These forms are documented in the [2.0.40 language guide](https://github.com/bendlang/bend/blob/v2.0.40/guide/GUIDE.md#parallelism).

Our two branches have equal shapes and leaf counts. That makes the example easy to inspect, but does not establish that arbitrary application branches take equal time. Two subtrees containing different amounts of expensive work need another balance check. The runtime design describes fixed fork-join scheduling without work stealing: choosing balanced work remains the programmer's responsibility.

Keep the inputs small here. The example uses `U32`, not unbounded integers. Increasing the depth or starting value changes the arithmetic range as well as the amount of work; do not scale it into a benchmark without checking overflow and the new expected answer.

<span id="native"></span>

## 3. Run Bend 2 CPU parallelism checks on a native binary

With the selected 2.0.40 compiler on your PATH:

```bash
bend reduction.bend --check-only
bend reduction.bend
CC=clang-14 bend reduction.bend -o reduction
BENDRTS='' ./reduction +RTS --threads 1 --gpu off
BENDRTS='' ./reduction +RTS --threads 2 --gpu off
BENDRTS='' ./reduction +RTS --threads 4 --gpu off
```

Use your explicit compiler path instead of `bend` if you installed the archive separately. Each evaluation and native run in our check printed:

```text
(2016, 2016)
```

The [runtime option parser](https://github.com/bendlang/bend/blob/v2.0.40/bend2/comp.ts#L5887-L5950) reads runtime flags inside the `+RTS` block. Clearing `BENDRTS` keeps inherited runtime settings out of this reproduction. If a program also takes application arguments, close the runtime block with `-RTS` before those arguments. Do not copy an older command with bare `--threads` and assume it controls this release's worker pool.

For an executable acceptance check, save this as `check-result.py` beside the binary:

```python
import os
import subprocess

for threads in (1, 2, 4):
    result = subprocess.run(
        ["./reduction", "+RTS", "--threads", str(threads), "--gpu", "off"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "BENDRTS": ""},
    )
    assert result.stdout.strip() == "(2016, 2016)", result.stdout
print("All requested thread settings returned the expected pair.")
```

Run `python3 check-result.py`. We exercised this assertion against the good program and the deliberate errors below. Checking the full pair catches disagreement between the implementations **and** agreement on an answer other than 2016. A successful process exit alone checks neither.

Requesting four threads does not prove four cores were busy, and equal output does not prove a speedup. This tiny input is intended to make the partition inspectable. We did not time it. Keep performance claims out of your notes until you have a representative workload and measurements from the actual native target.

<span id="controls"></span>

## 4. Make a wrong partition and watch the right check fail

First, change only the parallel function's fork to reuse `start` on both sides:

```python
left right = sum_par(p, start) sum_par(p, start)
```

Recheck, rebuild the binary, and rerun the commands. Our CLI and all three native thread settings returned **`(2016, 0)`**. Every leaf in the changed parallel function now receives zero. The ordinary checker still accepted the program: its types do not state that the leaves must cover the intended range. The Python assertion rejected the result.

Next, make the same offset mistake in the sequential function:

```python
right = sum_seq(p, start)
```

Leave the parallel mistake in place. Recheck and rebuild again. Our CLI and all three native settings now returned **`(0, 0)`**. A test that only compares the two results would pass. The assertion against the independently calculated answer still failed.

<div role="region" aria-label="Observed range-partition checks" tabindex="0" style="overflow-x:auto">
<table>
<thead><tr><th scope="col">Program</th><th scope="col">Ordinary check</th><th scope="col">CLI and native 1 / 2 / 4 result</th><th scope="col">Expected-answer assertion</th></tr></thead>
<tbody>
<tr><th scope="row">Original partition</th><td>Accepted</td><td>(2016, 2016)</td><td>Passed</td></tr>
<tr><th scope="row">Wrong parallel offset</th><td>Accepted</td><td>(2016, 0)</td><td>Rejected</td></tr>
<tr><th scope="row">Both offsets wrong</th><td>Accepted</td><td>(0, 0)</td><td>Rejected</td></tr>
</tbody>
</table>
</div>

Restore both original offsets and rebuild before continuing. During our checks, all three versions received the ordinary checker's `ALL PROOFS CHECK` message. **None declares a law specifying the range sum.** That message therefore does not certify this intended arithmetic property. The [proof-workflow guide](/blog/bend-2-proof-workflow) explains how explicit laws and the additional kernel check differ from this example's result assertions.

This failure exercise is the useful artifact to keep: a reference answer, a wrong single implementation, and a shared mistake. When you adapt a real computation, ask which of those failures your current tests would notice.

## Troubleshoot the stage that actually failed

If checking fails, stop before trying another thread count. The thread setting belongs to execution, so it cannot diagnose a rejected source program. Keep the first diagnostic and compare your file with the example, especially the shift function name and the single-line parallel binding. Record the compiler version alongside the error. Changing syntax and upgrading the compiler together would turn one reproduction into two different experiments.

If checking succeeds but compilation fails, preserve the build error separately. Confirm that the selected C compiler exists and that the command uses the intended Bend executable. An old binary may remain after an unsuccessful build; running it would test yesterday's program rather than the edit in front of you. Use a new output filename when investigating a build failure, and run that file only after the build command succeeds.

If the binary exits successfully but the assertion fails, keep its complete output before editing anything else. Identify whether one value is wrong or both are wrong. The two controls above give you concrete examples of each situation. Rebuild after restoring the source, then rerun the same acceptance script. Do not replace the expected pair with whatever the latest run printed.

Run the Python check normally, without optimization flags that disable assertions. If you need this check in a larger automated harness, preserve both the subprocess failure and the explicit expected-result comparison. A timeout, a crash and a wrong answer should remain distinguishable failures. This small exercise has no network dependency or long-running server to account for; investigate those additional failure modes separately when you move to an application.

<span id="projects"></span>

## 5. Carry the checklist into a real Bend project

The [Bend HTTP Server listing](/projects/bend-http-server/) is a useful source-reading follow-up because it separates request handling from computation. Read its compatibility notes before attempting the project. This article did not build that server or establish that its workload scales. For a separately checked local HTTP starting point, use the [HTTP-server walkthrough](/blog/bend-2-http-server).

When reviewing a compute path, record:

```text
Project source commit and compiler version:
Actual execution target: checker / JavaScript / native CPU / GPU:
Function being parallelized:
Meaning of each partition and its input range:
Why the branches should contain comparable work:
Independent expected answer for one small input:
Single-implementation mistake caught:
Shared-implementation mistake caught:
Native outputs at each requested thread count:
Timing evidence, or explicitly not measured:
```

Use this before interpreting a project's “parallel” description. The JavaScript target is sequential; an editable browser demo can still be useful for learning syntax or checking a result, but is not a substitute for a native CPU experiment. Likewise, concurrent socket handling and a parallel pure calculation answer different questions. A working network greeting tells you nothing about the range partition inside a compute endpoint.

If you later measure a representative workload, keep the source, compiler, target, input and output checks fixed while changing the thread setting. Record repeat measurements and the hardware limits rather than copying another machine's speedup. [Hyperfine's catalog entry](https://builtwithrust.com/projects/hyperfine) describes a tool for repeated command measurements and exportable results; its [upstream usage guide](https://github.com/sharkdp/hyperfine#usage) documents the controls. It is optional follow-up tooling, not a Bend runtime or a benchmark performed here.

Finally, treat the compiler as experimental. Its [own source warning](https://github.com/bendlang/bend/blob/v2.0.40/bend2/comp.ts#L1-L3) explicitly anticipates bugs. Keep a small reproduction of the first unexpected result, including whether it came from checking, building or executing. If an editor disagrees with your terminal, identify the checker it invokes using the [editor-tools guide](/blog/bend-2-editor-tools). Do not “fix” the expected answer to match a surprising output.

Start with one partition you can explain. Keep the failing controls. Then choose a project whose actual execution target matches the question you want to investigate.

<script type="application/ld+json">{"@context":"https://schema.org","@type":"HowTo","name":"Bend 2 CPU Parallelism: First Checks","description":"Check a small range reduction under native CPU thread settings, then use two deliberate partition errors to test the result assertions.","step":[{"@type":"HowToStep","name":"Record the compiler and target","text":"Select Bend 2.0.40 and identify the compiler, archive and native build toolchain.","url":"https://builtwithbend.com/blog/bend-2-cpu-parallelism#versions"},{"@type":"HowToStep","name":"Write a range sum with two call styles","text":"Save the sequential and parallel range partition example; independently calculate the expected answer 2016.","url":"https://builtwithbend.com/blog/bend-2-cpu-parallelism#partition"},{"@type":"HowToStep","name":"Run the native CPU checks","text":"Compile and compare the expected pair at one, two and four requested CPU threads with GPU disabled.","url":"https://builtwithbend.com/blog/bend-2-cpu-parallelism#native"},{"@type":"HowToStep","name":"Make two wrong partitions","text":"Remove the parallel offset, then both offsets; confirm that expected-answer assertions reject both mistakes even when the ordinary checker accepts them.","url":"https://builtwithbend.com/blog/bend-2-cpu-parallelism#controls"},{"@type":"HowToStep","name":"Use the checklist with a real project","text":"Record the source, execution target, partition boundaries, expected answer and unmeasured performance before evaluating a project's parallel path.","url":"https://builtwithbend.com/blog/bend-2-cpu-parallelism#projects"}]}</script>

<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://builtwithbend.com/"},{"@type":"ListItem","position":2,"name":"Blog","item":"https://builtwithbend.com/blog/"},{"@type":"ListItem","position":3,"name":"Bend 2 CPU Parallelism: First Checks","item":"https://builtwithbend.com/blog/bend-2-cpu-parallelism"}]}</script>
