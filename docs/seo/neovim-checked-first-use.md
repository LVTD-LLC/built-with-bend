# Neovim checked native first use

The existing Neovim listing now records a dated local first-use smoke, not
another general editor guide or a cross-version compatibility certification.
Original metadata, database publication, source actions and analytics identity
remain intact. The source-matched content date is November 3, 2026.

Reproduction uses the maintainer’s native package layout from
[the pinned installation instructions](https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/docs/INSTALLATION.md#native-package-layout),
with an isolated Neovim data/config directory, plugin source at
a67312765430fc8dea4f291ca2ab071f311f1e32, official Neovim 0.11.7 Linux x86-64 and
Bend 2.0.39 Linux x64. The Bend archive SHA-256 matched the GitHub release asset
digest: `6cf462fd8f70b094a4950ebb709a9c4ffd8f1d1189d9cedf1fd63cd5d041c7ab`.
Configure `cmd` to the intended compiler executable using the pinned README
configuration reference, then follow the
[proof-workflow example](https://github.com/nuxyel/bend2-nvim/blob/a67312765430fc8dea4f291ca2ab071f311f1e32/examples/proof-workflow/README.md).

Observed: automatic native-package load and Bend filetype;
`:Bend2CheckWorkspace` returned PASS for the example proof suite;
`:Bend2Proofs` displayed `adding_zero_preserves_value` as proved. Compiler version
detection used the plugin’s documented-source fallback to `bend version`.
No compiler or plugin result was mocked. This did not run the full test suite,
the proven kernel via `--verdict`, other operating systems, Neovim 0.12,
performance or security verification. It does not establish application correctness.

Verification includes the existing identity/repurposing regression, date checks,
rendered source/truth checks and mobile/desktop light/dark layout checks.
Release and live verification remain separate from this source record.
ReviewGate is waived by standing project authorization, never passed.
Raw analytics, shortlist, run history and execution logs remain private in Rowset.
