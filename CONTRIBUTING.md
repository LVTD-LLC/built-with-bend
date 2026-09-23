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


The ReviewGate workflow was omitted when this project was generated. Use passing
CI and maintainer review (including authorized maintainer agents) before merging. If maintainers later install ReviewGate and
configure `OPENROUTER_API_KEY` as an Actions secret, require its completed **5/5**
review and successful dedicated check on the exact current PR head before merge.
Skipped, stale, incomplete, or errored reviews are never a 5/5 approval. See the
[ReviewGate setup guide](https://reviewgate.lvtd.dev/docs/github-actions/).
