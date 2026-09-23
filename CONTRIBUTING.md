# Contributing to Built with Bend

Clear bug reports, documentation improvements, and focused pull requests are
welcome. Keep discussions respectful and specific to the work.

## Before you start

- Search existing issues and PRs in the [project repository](https://github.com/LVTD-LLC/built-with-bend)
  before starting duplicate work. Discuss substantial features or architectural
  changes with maintainers first.
- For bugs, include reproduction steps, expected and actual behavior, and relevant
  environment details. Redact credentials and personal data from logs and screenshots.
- Report security concerns privately to [the maintainer](mailto:rasul@lvtd.dev),
  not in a public issue containing exploitable details.

## Development and pull requests

1. Read [AGENTS.md](AGENTS.md) for project rules and
   [TECHNICAL.md](TECHNICAL.md#golden-path) for setup. Use local data and credentials.
2. Branch from the latest `main`, or work in a fork. Keep each PR focused; do not
   commit directly to the default branch.
3. Follow existing app boundaries and [DESIGN.md](DESIGN.md) for UI changes.
4. Add or update tests for changed behavior; prefer a regression test for bug fixes.
   Documentation-only changes need content/link checks, not artificial app tests.
5. Run the relevant checks from [docs/quality.md](docs/quality.md). The full local
   path is `make ci-local` once its prerequisites are configured. Explain any checks
   you could not run. Available CI must pass before merging.
6. Update affected documentation and add a concise entry under the current ISO
   date in [CHANGELOG.md](CHANGELOG.md), preserving previous entries.
7. Open a PR with the reason for the change, a summary, verification results,
   and linked issues. Include screenshots for visible UI changes and migration
   or rollout notes when needed. Use a draft PR for incomplete work.

AI-assisted contributions are welcome. Contributors remain responsible for
understanding their changes, checking generated claims, and verifying behavior.
Address material review feedback before merging.

## ReviewGate merge policy


ReviewGate is included, but activates only when `OPENROUTER_API_KEY` is available
as a GitHub Actions secret. A key in the application's `.env` is not sufficient.
See [the technical setup guide](TECHNICAL.md#reviewgate-ai-reviews).

**Once ReviewGate is configured, every PR needs a completed 5/5 review on its
exact current head commit before merging**, including documentation-only PRs.
Require the successful dedicated `ReviewGate` check as well as passing CI.
A green workflow alone, stale score, incomplete angle, timeout, or other reviewer
error is not approval. Any new commit requires a new current-head review.

Fix evidence-backed findings and push. When a finding is wrong, record code or
contract evidence through ReviewGate's [structured disposition process](https://reviewgate.lvtd.dev/docs/agent-workflows/).
The final current-head result must still be 5/5; resolving a thread alone is not enough.

After a run finishes, maintainers can comment exactly `@reviewgate review` on the
open PR to request another current-head review. Retry transient reviewer errors;
do not merge while a configured review is unavailable.

Without the key, a small configuration-check job records the reason and both
review and rereview jobs are skipped. No paid model call or ReviewGate check is
produced. Until the maintainer activates ReviewGate, use passing CI and human
review; do not describe this as a 5/5 pass. Removing a configured key must not be
used to bypass the review policy on a pending PR.

Fork and Dependabot PRs cannot use repository secrets. In a ReviewGate-enabled
repository, a maintainer must inspect the contribution and arrange a trusted
same-repository PR, then obtain passing CI and a current-head 5/5 before merging
that PR. Link and close the original PR without merging it. Never expose the key
to fork code or change the trigger to `pull_request_target`.

Branch protection is managed separately. Do not require a ReviewGate check before
it can run; once enabled, an available merge button does not waive this policy.
