---
title: "How Bendoom’s Random Table Works"
description: "Run a six-value Bend 2 probe against Bendoom’s random table. See why a valid lookup and an out-of-range lookup can both return zero."
published_at: 2026-11-25
author: Built with Bend
keywords: [Bendoom random table, Doom P_Random, Bend 2 examples]
topics: [Bend 2, Game development, Testing]
---

Bendoom’s random table is a fixed list of 256 numbers that its game simulation reads in order. A draw advances a cursor, wraps it from 255 to 0 if necessary, then reads the entry at the new position. Starting at cursor 0, the first draw returns **8**, not **0**.

That distinction makes [Bendoom](/projects/bendoom/) a useful Bend 2 project to read even if you never launch the game. You can test one piece of its simulation without a map, graphics window or game assets. Here’s the source, the small program we ran against it, and one result that looks right even when the lookup is wrong.

## The cursor is not the random number

In [id Software’s Doom source](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/m_random.c), one call to `P_Random` both updates the simulation index and returns a byte. In [Bendoom’s random module](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/src/random.bend), those operations have separate names. `Random.next` takes a cursor and returns the next **position**. `Random.at` takes a position and returns a **value**. Neither call updates the caller’s variable.

For example, the [table](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/src/tables.bend) starts with 0, 8 and 109. After the first draw, save position **1** for the next turn, not the value **8**. Passing 1 to the next draw takes you to position 2 and returns 109. Passing 8 instead skips straight to position 9. Doing neither and passing 0 again just gives you the first draw again. All three results look like plausible game data; only one continues the original sequence.

## Run a draw across the end of the table

We checked this on Linux x64 on November 25, 2026. Use Git and an extracted copy of the [Bend 2.0.26 release](https://github.com/bendlang/bend/releases/tag/v2.0.26). The [project’s native build](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/nix/bend.nix) uses a patched compiler of that version; the stock Linux release was sufficient for this module test. There’s no need to replace your system compiler. Set `BEND` to the absolute path to the extracted executable, keeping its accompanying directories in place.

```bash
# Replace this path with your extracted release.
BEND=/absolute/path/to/bend/bin/bend
git clone https://github.com/eliesgalvira/bendoom
cd bendoom
git checkout --detach 73935ed2fba1bbe932425bfe179536f98128c513
"$BEND" version
```

The version should read `bend 2.0.26`. Put the following in a new file named `wrap.bend` at the repository root so its relative import finds the real game module. Start at 254 rather than 0: three draws will reach the last entry, cross the boundary and leave it again.

```bend
import Base
import ./src/random.bend as R

def main() -> List<&2, U32>:
  +a = R.Random.next(254)
  +b = R.Random.next(a)
  +c = R.Random.next(b)
  [a, R.Random.at(a), b, R.Random.at(b), c, R.Random.at(c)]
```

Run `"$BEND" wrap.bend`. Our output was `[255, 249, 0, 0, 1, 8]`. Read it in pairs: position 255 contains 249; position 0 contains 0; position 1 contains 8. If you’re comparing a port to the original, keep both columns in your test output. Asserting only that the middle value is zero misses an important failure.

## Why two different lookups can both return zero

In the pinned module, a lookup that finds no entry falls back to zero. That is different from wrapping. The wrap happens in **next**, which adds one and masks the result with 255. **At** does not repair a bad cursor. We checked both direct lookups: `R.Random.at(0)` and `R.Random.at(256)` each returned 0. The former reads a real entry; the latter asks for a position beyond the table.

Try this negative control: change the middle pair in the returned list to `256, R.Random.at(256)`, leaving everything else alone. Our modified program printed `[255, 249, 256, 0, 1, 8]`. A check that compares only the three sampled values would accept the change. The expected six-number trace rejects it at the third number. This is why a boundary test should observe **which entry was read**, not just the byte it happened to contain.

## Diagnose a sequence that starts correctly, then drifts

Suppose two implementations agree on the first draw but disagree on the second. Before comparing the entire table, inspect the argument on the second call. In our check, starting from zero and asking for the next sample gave eight. Repeating the call with one gave 109. Passing eight instead gave 248. These are three different positions in the *same* table; swapping in a new table would be the wrong fix.

For a regression test, choose the input according to the mistake you want to catch:

- **Returning the old entry:** Start at zero. The old entry and the next entry differ, so one draw is enough to tell which was read.
- **Saving the sampled value:** Run two consecutive draws, passing the returned position forward. A single draw cannot tell you what the caller saved for its next turn.
- **Forgetting the wrap:** Start just before the end, as in the probe above. Include the position in the expected output. A test that starts at the beginning and stops after two turns never reaches the broken case.

These tests answer different questions. If the first two pass and the third fails, look at the position arithmetic before investigating how the caller stores state. If the boundary probe passes in isolation but a gameplay trace still diverges, count how many draws each caller actually made.

## Follow one draw into the game

In [Bendoom’s spawn logic](https://github.com/eliesgalvira/bendoom/blob/73935ed2fba1bbe932425bfe179536f98128c513/src/things.bend#L847-L853), look for the names `drawn` and `after`. The first is an advanced cursor. The second either keeps that cursor or advances it once more, according to whether the starting state has a positive tic count. The function passes `after` onward. A branch that consumes an extra draw changes the position the next caller receives, even if the two branches happen to produce the same visible outcome on this turn.

When tracing a replay discrepancy, write down the incoming cursor, the branch taken, the cursor handed back and the sampled value. Find the first **cursor** disagreement before comparing later values. The module exercise tells you what one draw does; matching those six numbers is not a test of a whole replay, still less a proof that every possible sequence of game inputs is handled correctly. For that distinction, see the [Bend 2 proof workflow](/blog/bend-2-proof-workflow).

**What if a newer Bend rejects the import?** With Bend 2.0.40, our check stopped while parsing the name `Tables.finesine.0` in the imported tables file. It never reached our draw. Recheck the two pins before debugging your arithmetic; changing the expected numbers cannot fix a parse error. This example uses Bend 2, not the older Bend/HVM toolchain described in the [Bend language and project guide](/blog/bend-programming-language).

If you want another project to inspect, browse the [Games category](/?category=games). For this exercise, use the Bendoom listing that links to **eliesgalvira/bendoom**: the import path and table names above refer to that repository and revision.
