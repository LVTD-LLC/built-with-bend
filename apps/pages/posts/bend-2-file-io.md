---
title: "Bend 2 File I/O: Create, Read, Close"
description: "Try Bend 2 file I/O with checked native examples, exclusive creation, read-back assertions and failure controls before exploring storage projects."
published_at: 2026-11-18
updated_at: 2026-11-27
author: Built with Bend
keywords: [Bend 2 file I/O, Bend File.open, Bend read file, Bend write file]
topics: [Bend 2, File I/O, Developer tools]
---

For **Bend 2 file I/O**, open a file through `IO`, pass its handle to the operation, and close the returned handle before acting on the result. Start with exclusive creation (`"x"`) in a fresh directory: a second run should fail rather than overwrite your first file. Check the bytes on disk as well as the program's exit status.

**Checked November 18, 2026:** Built with Bend used the official **Bend 2.0.40 Linux x64** release and clang 14 for the native examples below. The exercise checks a small ASCII file and deliberate failure cases. It does not test crash recovery, storage performance, other platforms, GPU execution or the `--verdict` proof kernel. The storage projects linked at the end are separate next steps, not implementations we certified through this exercise.

Follow the workflow:

1. [Select the compiler and a fresh directory](#setup).
2. [Create and close a file](#create).
3. [Read it and inspect the actual bytes](#read).
4. [Run the failure controls](#controls).
5. [Choose the next storage task](#next).

<span id="setup"></span>

## 1. Set up a Bend 2 file I/O experiment

You need a terminal, a text editor, a native C compiler and Python 3 for the independent filesystem assertions. Identify the Bend executable you will use:

```bash
bend version
bend guide
clang-14 --version
```

Our executable reported `bend 2.0.40`. To reproduce that release, choose your platform's archive from the [official 2.0.40 release](https://github.com/bendlang/bend/releases/tag/v2.0.40), check its published SHA-256, and follow the distribution's setup instructions. Our Linux x64 archive matched `c9ff8d67bd903fb6ad9a26b43d8a62c01021de82a44d55ce4a3dcd4732113d6b`. We extracted it separately rather than replacing the machine's existing compiler. Use that executable's explicit path wherever this guide says `bend` if it is not the one on your PATH.

These are Bend 2 examples, not older Bend/HVM examples. The [language and project introduction](/blog/bend-programming-language) explains that distinction. If your editor and terminal disagree, identify the checker each uses with the [Bend 2 editor guide](/blog/bend-2-editor-tools).

Create a disposable workspace:

```bash
workdir=$(mktemp -d)
cd "$workdir"
```

Keep the same terminal directory for the remaining steps. `note.txt` is a relative path, so the process's working directory determines where it is created. A fresh directory makes the expected first run reproducible without deleting a file you may care about.

The [versioned Base file API](https://github.com/bendlang/bend/blob/v2.0.40/bend2/base.bend) documents these modes:

- `"r"`: read an existing file.
- `"r+"`: read and write without creating or truncating it.
- `"w"`: create a file or truncate an existing one.
- `"a"`: append or create.
- `"x"`: create exclusively, failing if the path already exists.

Use `"x"` here because refusing an accidental second creation is part of the exercise. It is not a general replacement for append, update or atomic-replacement workflows. Avoid switching to `"w"` merely to silence an existing-file error: that changes the contract you are checking.

<span id="create"></span>

## 2. Create a file and close the returned handle

Save this as `create.bend`:

```text
import Base

def finish(result: File & Result<&1, &1, U32 & String, Unit>) -> IO(Unit):
  match result:
    case (file, status):
      do IO<Unit>:
        File.close(file)
        IO.pass(Unit, status)

def main() -> IO(Unit):
  do IO<Unit>:
    file : File <- IO.try(File, File.open("note.txt", "x"))
    result : File & Result<&1, &1, U32 & String, Unit> <- File.write(file, "Bend\n")
    finish(result)
```

The long type is worth reading. `File.write` returns a **pair**: the file handle and a `Result`. Its success value is `Unit`; its failure contains an error code and message. `finish` separates that pair, closes the handle, then passes the status to `IO.pass`. That last operation returns the successful value or terminates with the reported error.

Closing before unwrapping the status makes the cleanup explicit on both the successful-write and failed-write paths. `IO.try(File, File.open(...))` is different: when opening fails, no file handle was acquired for this program to close. The [official IO guide](https://github.com/bendlang/bend/blob/v2.0.40/guide/GUIDE.md#io-and-concurrency) describes handles as affine: they cannot be freely reused, and operations hand them back alongside their results.

Check, build and run:

```bash
bend create.bend --check-only
CC=clang-14 bend create.bend -o create
BENDRTS='' ./create +RTS --threads 1 --gpu off
```

In our native check, the final command exited successfully without printing a success banner. That is expected: the program writes a file, not a status message. A checker message is also not a disk-content assertion. Inspect the side effect independently:

```bash
python3 - <<'PY'
from pathlib import Path
assert Path("note.txt").read_bytes() == b"Bend\n"
print("file bytes match")
PY
```

That assertion is the acceptance criterion for this fixture. It compares the exact bytes, including the newline, rather than looking for a word somewhere in the output. It does not prove that arbitrary input or a different filesystem behaves correctly.

<span id="read"></span>

## 3. Read a file in Bend 2 with an explicit bound

Save this as `read.bend`:

```text
import Base

def finish(result: File & Result<&1, &1, U32 & String, String>) -> IO(Unit):
  match result:
    case (file, status):
      do IO<Unit>:
        File.close(file)
        text : String <- IO.pass(String, status)
        IO.print(text)

def main() -> IO(Unit):
  do IO<Unit>:
    file : File <- IO.try(File, File.open("note.txt", "r"))
    result : File & Result<&1, &1, U32 & String, String> <- File.read(file, 64)
    finish(result)
```

Build and run it from the directory holding `note.txt`:

```bash
bend read.bend --check-only
CC=clang-14 bend read.bend -o read
BENDRTS='' ./read +RTS --threads 1 --gpu off
```

The program should print `Bend`. The file already contains a newline; `IO.print` can affect the display separately, so use the Python byte assertion above as the file-content oracle rather than inferring bytes from terminal spacing.

The `64` is a **byte bound**, not a request for the entire contents of any file. The Base documentation says `File.read` reads up to that bound, ending earlier at end-of-file. It is enough for this five-byte fixture. A larger file needs an intentional continuation or rejection strategy; copying this reader into an importer does not make it a complete-file reader.

For larger inputs, decide what a complete result means before adding a loop. A byte cap prevents this call from requesting an unbounded buffer, but it does not validate a file format or report that the whole document fit. A prefix can look plausible while omitting the record you needed. Compare the expected length or structure in your own application, and test a file that is deliberately too large. That larger-file case is a recommended extension, not one of our executed controls.

Text and binary data also need different handling. Base exposes `File.read_bytes` and `File.write_bytes` for byte lists. Do not assume a package-specific `Bytes` type is interchangeable with that list or that every string conversion is a UTF-8 encoder. The [package-import walkthrough](/blog/bend-2-package-imports) shows why reading a function's exact input type matters. This exercise stays ASCII; it is not a Unicode-boundary test. The [native reader](https://github.com/bendlang/bend/blob/v2.0.40/bend2/effs/file_read.c) converts each read buffer separately. A byte-sized chunk can split a multibyte character, so do not present repeated text reads as a lossless streaming decoder. Preserve bytes first when you need to control decoding across chunk boundaries.

### Tell a blank line from end-of-file

Use a **positive byte limit** with `File.read_line` if your loop treats an empty string as end-of-file. With a limit of zero, the native reader can return an empty string without consuming anything. In our Bend 2.0.40 check, a zero-byte read returned `""`; the next read on the returned handle, with a limit of 64, still returned the entire first line.

A successful read is not necessarily a whole line, either. The [release’s runnable line-reader example](https://github.com/bendlang/bend/blob/v2.0.40/tests/io/file_read_line.bend) writes `ab\n\nlonger\nend`. Predict the next chunk before each read:

- A limit of 64 returns `"ab\n"`, then `"\n"` for the blank line. The reader keeps the newline.
- A limit of 3 returns `"lon"`. Reading again with 64 returns `"ger\n"`: two reads, one line.
- The next read returns `"end"` without a trailing newline. Process it. Only the following read returns `""`.

If your input uses Windows-style line endings, do not assume the reader strips the carriage return. On Linux with a CRLF fixture, our blank line came back as `"\r\n"`. Decide whether to normalize line endings **after** assembling the line; a chunk boundary is not a record boundary.

<span id="controls"></span>

## 4. Check the failures, not only the happy path

We checked these native cases against the same compiler release. The observations concern this fixture on Linux, not an exhaustive error-code portability guarantee.

- **Fresh directory:** `create` exits zero and produces exactly `b"Bend\n"`.
- **Read-back:** `read` exits zero and prints the text from that file.
- **Second exclusive creation:** `create` exits nonzero; the existing file's bytes remain unchanged.
- **Missing file:** running `read` in a different empty directory exits nonzero and does not create `note.txt`.
- **Write through a read-only handle:** the writer variant described below exits nonzero; the fixture's bytes remain unchanged.

Test the second creation without hiding the exit status:

```bash
if BENDRTS='' ./create +RTS --threads 1 --gpu off; then
  echo "unexpected second-create success"
  exit 1
else
  echo "second creation rejected"
fi
```

Run the Python byte assertion again. A nonzero exit alone would not tell you whether the old content survived. The [native open implementation](https://github.com/bendlang/bend/blob/v2.0.40/bend2/effs/file_open.c) maps exclusive mode to an exclusive filesystem create; the observed rejection and byte comparison check the result from the user's side.

For the missing-file control, run the compiled reader by absolute path from another fresh directory:

```bash
reader="$PWD/read"
missing_dir=$(mktemp -d)
(cd "$missing_dir" && BENDRTS='' "$reader" +RTS --threads 1 --gpu off)
```

The subshell command is expected to fail. Confirm that `note.txt` remains absent there. If you automate the exercise, capture the return code explicitly; do not configure your harness to treat the expected failure as a successful read.

For the write-error control, copy `create.bend` to `write-readonly.bend` and change **only** its open mode from `"x"` to `"r"`. Compile it with the same command pattern and run it beside the existing fixture. Opening now succeeds, but writing through a read-only handle fails. The same `finish` helper closes the acquired handle before propagating the failure. We tested this variant and checked the file's bytes afterward; we did not instrument operating-system descriptors or inject a close failure.

If a result differs, first record the compiler path, working directory and file bytes before editing the program. An existing fixture explains an exclusive-open failure; a different directory explains a missing-file failure. Recompiling a changed source is necessary before claiming that the new binary exercised your change. Keep diagnostics alongside the command that produced them, rather than treating a later successful run as evidence about an earlier failure.

These controls catch different mistakes. The duplicate-create case tests the open policy; the read-only case reaches the write-result path. Neither substitutes for the other.

<span id="next"></span>

## 5. Decide what to explore after basic file I/O

**A successful write/read-back is not a crash-durability guarantee.** The [versioned native write and close implementations](https://github.com/bendlang/bend/tree/v2.0.40/bend2/effs) do not turn this exercise into a transaction, recovery protocol or power-loss test. We made no durability measurement. A failed write is not a promise of rollback either: earlier writes may already have changed part of a file before a later operation fails. Our read-only control leaves this fixture unchanged because that handle cannot perform the write; it does not establish that every failed write preserves old content.

There is another reporting limit in the [native close operation](https://github.com/bendlang/bend/blob/v2.0.40/bend2/effs/file_close.c): it does not return a fallible result to the Bend caller. Our programs explicitly call close, but they do not receive an independently checkable close-success verdict. If your next project requires stronger storage guarantees, inspect its synchronization, replacement and recovery design rather than treating the cleanup helper as that design. Likewise, a checked program with foreign file effects is not a proof of filesystem behavior; see the [proof workflow's checker boundaries](/blog/bend-2-proof-workflow).

Choose a next step by the problem you actually have:

- **One small file:** keep learning the Base operations. Decide whether creation, append or update matches your intended behavior, then add controls for that choice.
- **Binary representation or encoding:** inspect the exact byte type and conversion in a library before importing it. [JendHub](/projects/jendhub/) and the [community package catalog](/projects/bend-packages/) can help you find definitions; their presence is not compatibility certification.
- **Persistent key/value data and snapshots:** inspect [MyLSM](/projects/mylsm/). Its listing provides a release-aware reading path through text, binary and snapshot examples. That is a different storage task from writing this file; this guide does not claim we ran MyLSM or verified its recovery guarantees.

When evaluating a project, carry a small acceptance checklist with you: record the compiler and source revision; identify the effect's return type; follow the handle through success and failure; compare the external result independently; and name the behavior still untested. Start with the two programs above, then browse the [Bend library category](/?category=libraries) for a project that needs the next check you want to learn.
