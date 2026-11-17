# Bendo: from hello to a real typed-client task

Source: https://github.com/opencoredev/bendo/tree/a42deb987571aeb6bb35790f787f5f7defb1d5e0

The existing listing gains a try-next path to the pinned todo example, its
client configuration, result contract and route-regeneration instructions.
It distinguishes the wildcard hello response from stateful CRUD. No new
overlapping article, title change, database edit or release claim.

November 17 verification used isolated checksum-verified Bend 2.0.38 and
Bun 1.4.4 downloads, with clang 14 on Linux x64; managed tools were unchanged.
The unmodified upstream `tests/todo-example.test.ts` passed all 20 tests
(103 assertions): native CRUD, rejected writes, generated-file freshness,
shared validation, CORS, frontend build and typechecking. The first attempt
stopped before testing because `clang` was not on PATH; adding the existing
LLVM 14 bin directory resolved that environment issue. No source patch.

This is not an interactive React browser test, scaffolder-template test,
proof-kernel check, benchmark or production-readiness assessment. The
November 2 hello test keeps its original dated scope. Source/analytics links,
publication and ordering are preserved; the exact listing receives a fixed
November 17 content date, never a build-time lastmod.

Required verification: catalog identity isolation, rendered canonical/body/
source order and analytics identity, sitemap date, responsive/theme checks,
CI, exact deployed web/worker revision, and live source links. Raw analytics,
research, selection and outcomes stay in the existing private Rowset history.
