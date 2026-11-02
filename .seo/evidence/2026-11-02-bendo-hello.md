# Bendo hello: reproducible public-source check

Checked November 2, 2026. Source: [opencoredev/bendo at a42deb9](https://github.com/opencoredev/bendo/tree/a42deb987571aeb6bb35790f787f5f7defb1d5e0).
The `.bend-version` pin is 2.0.38. The [README quick start](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/README.md#quick-start)
supplies the commands and expected response. The [scaffolder instructions](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/packages/create-bendo/README.md#before-the-first-npm-release)
require a checkout before the first npm release.

An isolated official Linux x64 Bend 2.0.38 release archive matched SHA-256
`f19d088b079c9e1a8834ecd153b7d58c11a5f8f9ab1bdb78dbc96a6bf49aaa81`.
The managed compiler was not replaced. With the unmodified checkout on Linux
x64/glibc 2.36, run the README's native hello commands using that compiler:

```sh
bend examples/hello/main.bend -o hello
./hello
```

From a second terminal, the README request:

```sh
curl http://127.0.0.1:8787/todos/42
```

returned HTTP 200 and exactly `Hello from Bendo! You asked for /todos/42`.
The local process was stopped after the request. No dependency install, application
scaffolding, full test suite, proof-kernel verification, GPU test, benchmark,
security certification or production-readiness assessment was performed.
The [law documentation](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/docs/laws/README.md)
describes the scope of pure-code proofs separately from IO.

Only the exact repository-bound Bendo listing receives the section and content
date. Retain its title, description, original actions and publication date.
