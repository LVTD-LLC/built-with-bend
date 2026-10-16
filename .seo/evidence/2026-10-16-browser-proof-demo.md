# Browser proof-demo discovery — 2026-10-16

The existing introductory guide now links to the existing Bend, Explained
listing and its versioned, editable demo. This is a contextual learning path,
not a new tutorial, title test, or benchmark. Original publication date and
all five project sections remain unchanged.

## Sources and observed behavior

- Primary README at revision `84c04b02bbd3be2c5ee1b5622a1490e41e730391`:
  https://github.com/raunak-11/bend-explainer/blob/84c04b02bbd3be2c5ee1b5622a1490e41e730391/README.md
- Browser exercise: https://raunak-11.github.io/bend-explainer/v4/#works-play
- With the optional LLM panel unused, select each preset and click
  **Run the checks**. Original and Raise the limit to 1500 returned pass;
  Refactor slip returned a failed law involving a missing police report.
- The demo bundles the ordinary Bend 2.0.25 checker. Its `runChecks` function
  invokes the embedded checker on PROOF.bend and main.bend. It does not run
  the separate `--verdict` kernel check. The README labels scheduler animations
  as simulations, not performance measurements.

## Scope

No API key, external LLM request, benchmark, compiler upgrade, or claim about
current-version native compilation. No user or private analytics data appears
in the public copy. Recheck the source and three presets on October 23 before
expanding the recommendation. Content modification date: October 16.
