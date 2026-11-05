# Checked ezmcp stdio first use

The existing ezmcp listing now offers a copyable pinned demo build and JSON-RPC
input, with expected success and two distinct failure results. It owns this
bounded first-use intent; no new generic MCP article or inferred client setup.
Original listing copy, actions, metadata and publication date stay unchanged.
Only the reviewed slug plus repository identity receives this section/content date.

## Source and verification

- Upstream: Emerging-Patterns/ezmcp, commit
  `222124b0814a3e5c1193e78eba0392e709b99174`; pinned README,
  `examples/demo/main.bend` and `docs/SPEC.md` linked beside the commands.
- Linux x64, Bend 2.0.38, Clang 14.0.6: unmodified native demo builds.
- Exact displayed build and stdio input: initialization selects 2025-11-25,
  tool listing returns echo/add, and add(2,40) returns structured sum 42.
- Separate negative controls: a noninteger add argument returns a tool error;
  an unknown tool returns JSON-RPC -32602. No notification reply.
- Five pinned source destinations return HTTP 200.
- Screenshots cover 390/1440px, light/dark. Source actions precede setup,
  command block scrolls by keyboard on mobile, focus is visible, page does not
  overflow, and public-content identity/source-link annotations are preserved.
  Browser checks block analytics requests; local fixtures are synthetic.
- Regression coverage checks the public rendered section and content date only
  for the reviewed identity, retaining the original publication and description.
- Existing library pagination and Chromi/Dithra listing links reach ezmcp.

This is a local stdio smoke check, not HTTP revalidation, agent-client integration,
other-platform support, full conformance, proof verification or security/production
certification. The earlier October smoke check remains separately dated.
Raw research, analytics and outcome history stay in the existing private Rowset
history dataset referenced by `.seo/config.json`. Search/activation uplift is
not established. ReviewGate is waived by standing owner authorization, not passed;
CI, deployment and live verification remain required.
