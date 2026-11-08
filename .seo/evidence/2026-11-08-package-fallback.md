# Package-walkthrough source fallback — November 8, 2026

The exact formerly linked search endpoint repeatedly returned HTTP503 and
The search index is not ready. No evidence of a whole-site JendHub outage:
llms.txt and read.txt were200. This is a source-access repair on our guide,
not a repair to JendHub or a new compiler compatibility claim.

Primary documentation: https://jend.leeeet.dev/llms.txt
Former search: https://jend.leeeet.dev/search.txt?query=hex%20encode%20bytes&limit=10
Working exact-name fallback:
https://jend.leeeet.dev/grep.txt?pattern=to_hex&path=bend-kit-bytes%400.3.2.0%2Fbytes.bend&limit=10
Returned200 and bend-kit-bytes@0.3.2.0/bytes.bend:631:def to_hex(b: Bytes) -> String:
Working source:
https://jend.leeeet.dev/read.txt?path=bend-kit-bytes%400.3.2.0%2Fbytes.bend&start_line=1&end_line=700
Returned200 and the original Bytes definition/dependency boundary.
The grep endpoint requires path; an exploratory call without path returned400
and is not used in the guide. Exact-name search cannot replace semantic
package discovery. The original October18 compiler tests, package0.3.2.0,
publication/title/description, and historical0.3.3.0search observation remain.
No new compiler run. Recheck search November9; retain fallback if stillneeded.
