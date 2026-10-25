# Bend 2 editor server: source is not a release

The existing editor guide owns compiler-path selection. Its pinned 0.1.1
comparison remains useful, but current repository documentation now describes a
different compiler snapshot. This update makes that boundary explicit before
readers interpret an editor diagnostic or assume an extension was upgraded.

Verified October25, 2026:

- npm registry dist-tags.latest and package metadata still identify0.1.1:
  https://registry.npmjs.org/bend2-lsp .
- Current source manifest declares0.2.0 and Node>=26.9:
  https://github.com/don2e4/bend2-lsp/blob/ed06027cc5396050459776accf91214f0c433f79/package.json .
- October22 source commit vendors Bend2.0.38 and adds completion, symbols and folding:
  https://github.com/don2e4/bend2-lsp/commit/af933fd975f50f6e37cbc0882cae7e3a6f643ee1 .
- Source README documents named imports and revised diagnostics:
  https://github.com/don2e4/bend2-lsp/blob/ed06027cc5396050459776accf91214f0c433f79/README.md .
- Maintainer-reported diagnostic mismatch (not independently reproduced here):
  https://github.com/don2e4/bend2-lsp/issues/4 .
- Nuxyel06bcbaf and kbrianps81ba2c9 remain the compared source revisions.

No source build or extension install was tested; no claim that the newer server
is in kbrianps0.1.3. Existing title/description/publication, comparison diagram,
FAQ and inbound blog/listing/package-guide paths retained. Updated content date
drives Article dateModified and sitemap lastmod; no new URL or manual resubmission.
ReviewGate is waived, not passed. Research/analytics/experiment ledger stays private.

## Package walkthrough: broken source-discovery paths repaired

A due source review reproduced HTTP400 for search.txt?q=hex%20encode%20bytes and
HTTP404 for /src/bend-kit-bytes@0.3.2.0/bytes.bend?def=to_hex. Current
https://jend.leeeet.dev/llms.txt documents query= and read.txt?path=.
The replacement search and pinned read links return200. Search now finds
0.3.3.0; the guide deliberately retains its tested0.3.2.0, with the difference
visible to readers. The read endpoint opens historical releases, unlike
definition search’s latest-release index. Original tested code/results stay
unchanged; no new compiler execution or 0.3.3.0 compatibility claim.
This material reachability defect was discovered during the same due guide
source review and included before shipping. Package dateModified/lastmod bumped.
