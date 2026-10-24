# Deployment notification scope — October 24, 2026

The deployment path formerly captured a list of sitemap URLs and submitted the
union of that list and the post-deployment sitemap. That included unchanged pages
on every deployment. An IndexNow receipt is not evidence of indexing.

The existing workflow flags now capture a URL-to-lastmod map and compare it with
the verified deployment. Only added, changed or removed URLs are notified. The
Django management command and standalone CLI share the same validation and delta
logic as the existing daily checkpoint path. A code-only deployment with an
unchanged sitemap sends no notification. No schedules or provider settings change.

Malformed and legacy URL-only snapshots fail explicitly rather than silently
falling back to a full submission. The existing explicit manual command without a
snapshot still submits a full baseline. Sitemap dates retain their original
content meaning: same-date edits and edits without a lastmod change cannot be
detected by this comparison and may need an intentional manual notification.

Regression cases exercise snapshot-to-deployment flow, unchanged reruns, additions,
edits, removals, receipt statuses, malformed/null/legacy snapshots and public URL
validation. Existing retry, revision, checkpoint and batch-limit checks remain.
No page copy, metadata, sitemap content dates or analytics definitions change.
Private research and measurement history remain in the configured Rowset store.
