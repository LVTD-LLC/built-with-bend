# JendHub destination check — October 17, 2026

The existing JendHub listing had no live-site action, and its implementation
source at `src/jend/build.py` returned HTTP 404. This was a curated-record issue,
not a route or template failure across the directory.

The project's [pinned README](https://github.com/LeeeeT/JendHub/blob/73c4451810ee63a48f8c4c5321fdeea36cebe082/README.md)
names `https://jend.leeeet.dev` as its public service. The homepage and its
[agent guide](https://jend.leeeet.dev/llms.txt) responded successfully. The current
[site implementation](https://github.com/LeeeeT/JendHub/blob/73c4451810ee63a48f8c4c5321fdeea36cebe082/src/jendhub/services/site/app.py)
is the replacement for the dead source link.

A reversible, guarded data migration adds the live destination and replaces only
the dead source URL. It preserves the description, repository, source identity,
publication date, moderation state and other metadata. Later destination edits
cause the migration to stop rather than overwrite them. Fresh installs without
the curated project are unchanged. No lookup runs inside the migration.

The existing outbound-action analytics contract is reused. This is a route to a
working tool, not certification of its search relevance, compiler compatibility,
package safety or performance. Private research and measurement remain in the
existing configured Rowset store. Source review: October 24.
