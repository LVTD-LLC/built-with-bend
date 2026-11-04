---
title: "Bend 2 HTTP Server: Tested First Use"
description: "Run a Bend 2 HTTP server locally, compare the official demo with Bendo, and test response contracts before choosing a project."
published_at: 2026-11-04
author: Built with Bend
keywords: [Bend 2 HTTP server, Bendo, Bend web framework]
topics: [Bend 2, HTTP, Developer tools]
---

Start a **Bend 2 HTTP server** with the official socket demo if you want to understand request handling. Try Bendo if you want a framework with routes and middleware. In either case, check the response body and an unwanted request before calling the example a working API: a successful connection does not establish the route you intended.

**Checked November 4, 2026:** Built with Bend compiled and ran the official **Bend 2.0.39** HTTP demo and Bendo's hello example with its pinned **Bend 2.0.38**, on Linux x86-64 with clang 14. We sent four requests to each native server. The results below are local smoke checks, not throughput measurements, proof-kernel checks or production recommendations. The separate community compute server is source-reviewed only.

## Choose a starting point

- **Learn socket effects:** use the [official HTTP demo](https://github.com/bendlang/bend/blob/v2.0.39/demos/io_http_server/main.bend). It is a small accept/read/reply example, not a routed application.
- **Explore application routing:** use [Bendo](/projects/bendo/). The framework has route and middleware APIs; the hello program deliberately uses a wildcard GET route. Bendo is pre-alpha.
- **Study computation behind HTTP:** read [Bend HTTP Server](/projects/bend-http-server/). Its source separates request handling from a fork-join workload. Its compatibility caveats matter before trying to build it.

These are different learning tasks, not a ranking. A minimal socket example wins on how little code you need to read. A framework gives you more application machinery to inspect. The compute experiment is useful when your question concerns that workload, rather than a general-purpose web stack.

Follow the checked workflow:

1. [Select the compiler and source](#versions).
2. [Run the official local demo](#official).
3. [Run Bendo's wildcard hello](#bendo).
4. [Compare response contracts](#responses), including unwanted requests.
5. [Read the limits before expanding](#limits).

<span id="versions"></span>

## 1. Keep the compiler and project versions together

Use a terminal, a text editor, curl, git and a native C compiler. The official [v2.0.39 guide](https://github.com/bendlang/bend/blob/v2.0.39/guide/GUIDE.md#tooling) documents native builds with clang 14 or newer; programs using GPU-marked calls need additional tooling. Neither checked hello program here uses a GPU workload.

Start with:

```bash
bend version
bend guide
```

For the official example below, our version was `bend 2.0.39`. Obtain the matching archive for your system from the [2.0.39 release](https://github.com/bendlang/bend/releases/tag/v2.0.39), verify its published checksum, and follow the distribution's setup instructions. We checked Linux x64, not every available platform.

Bendo's [pinned quick start](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/README.md#quick-start) instead selects **2.0.38**. Keep that compiler in a separate extracted directory and use its executable explicitly. Do not silently run a newer `bend` from your PATH and describe that as the pinned result. Our two compiler archives matched their release checksums.

These are Bend 2 instructions. The older Bend/HVM toolchain is a different generation; commands from its tutorials are not interchangeable. The [Bend language and project guide](/blog/bend-programming-language) explains the distinction. If your editor reports a different error from the terminal, identify its checker using the [editor guide](/blog/bend-2-editor-tools) before changing the example.

<span id="official"></span>

## 2. Run the official HTTP demo on loopback

Create an empty working folder. Download the versioned program and read it before compiling:

```bash
mkdir bend-http-demo
cd bend-http-demo
curl -fsSL https://raw.githubusercontent.com/bendlang/bend/v2.0.39/demos/io_http_server/main.bend -o main.bend
bend main.bend -o http-server
./http-server +RTS --threads 2 --gpu off
```

These build and runtime options were exercised in our check. If clang is installed under a versioned name rather than selected by default, choose it with your environment's `CC` setting; our build used `CC=clang-14`. Leave the server running in this terminal. It binds **127.0.0.1:8080**, so the example is local to this machine. If another process already occupies that port, resolve the conflict before interpreting a response as this program's output.

In a second terminal:

```bash
curl --max-time 5 -i http://127.0.0.1:8080/
curl --max-time 5 -i http://127.0.0.1:8080/todos/42
curl --max-time 5 -i http://127.0.0.1:8080/missing-bend-probe
curl --max-time 5 -i -X POST http://127.0.0.1:8080/todos/42
```

All four requests returned HTTP **200**, `Content-Type: text/html`, and the same body in our check:

```html
<h1>Hello, world!</h1>
```

The POST above has no request body. It is a method probe, not a test of form uploads or JSON handling.

Read the [demo source](https://github.com/bendlang/bend/blob/v2.0.39/demos/io_http_server/main.bend) alongside the output: it accepts a connection, reads from the socket, sends a fixed response and closes. It does not dispatch on the request path or method. A 200 response for a nonexistent path is therefore consistent with this example's purpose. It is not evidence of a working todo endpoint.

The code also gives each accepted socket to `IO.spawn`. That demonstrates concurrent connection handling; this small exercise does not measure how many requests run simultaneously or how well the server scales. Stop it with Ctrl+C when finished.

<span id="bendo"></span>

## 3. Run Bendo's wildcard hello with its pinned compiler

Bendo's [README](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/README.md) describes a pre-alpha framework with routing, middleware and a TypeScript toolkit for application clients. At the inspected commit, the toolkit is not published to npm. Start from the checkout rather than treating a prospective `bun create bendo` command as an available package.

In a new terminal, clone and select the exact source we checked:

```bash
git clone https://github.com/opencoredev/bendo.git
cd bendo
git checkout a42deb987571aeb6bb35790f787f5f7defb1d5e0
```

After following the pinned quick start's compiler setup, replace the path below with your extracted **2.0.38** executable:

```bash
BEND38=/absolute/path/to/bend-2.0.38/bin/bend
"$BEND38" version
"$BEND38" examples/hello/main.bend -o hello
./hello +RTS --threads 2 --gpu off
```

The checked hello program binds **127.0.0.1:8787** by default. Keep it running and use a second terminal:

```bash
curl --max-time 5 -i http://127.0.0.1:8787/
curl --max-time 5 -i http://127.0.0.1:8787/todos/42
curl --max-time 5 -i http://127.0.0.1:8787/missing-bend-probe
curl --max-time 5 -i -X POST http://127.0.0.1:8787/todos/42
```

The todo-path GET returned HTTP 200, `Content-Type: text/plain; charset=utf-8`, and `Hello from Bendo! You asked for /todos/42`. The root and missing-path GETs also succeeded, with their own paths in the text. The bodyless POST returned HTTP 405 with an empty body and `Allow: GET, HEAD`. Stop the server with Ctrl+C after the checks.

The [hello source](https://github.com/opencoredev/bendo/blob/a42deb987571aeb6bb35790f787f5f7defb1d5e0/examples/hello/main.bend) registers `B.get(Tag, "/*", Hello{})`. That is an intentional wildcard GET handler. **It does not implement a todo lookup**, even though the response repeats a todo-shaped URL. A missing-path 200 is expected for that route; a body containing the path does not establish that a record was loaded.

For application structure, inspect the repository's API/fullstack templates and store example next. We did not scaffold those templates or test their frontend clients in this run. The native hello test does not establish that every advertised feature works in your environment.

<span id="responses"></span>

## 4. Compare what the responses establish

Here is the complete eight-request matrix. Each entry is one request to a locally running native binary, without automatic redirect following. All POST requests had no body.

<div role="region" aria-label="Checked local HTTP responses" tabindex="0" style="max-width:100%;overflow-x:auto;">
<table>
<thead><tr><th scope="col">Request</th><th scope="col">Official 2.0.39 demo</th><th scope="col">Bendo hello, compiler 2.0.38</th></tr></thead>
<tbody>
<tr><th scope="row">GET /</th><td>200; fixed HTML</td><td>200; greeting with /</td></tr>
<tr><th scope="row">GET /todos/42</th><td>200; fixed HTML</td><td>200; greeting with /todos/42</td></tr>
<tr><th scope="row">GET /missing-bend-probe</th><td>200; fixed HTML</td><td>200; greeting with /missing-bend-probe</td></tr>
<tr><th scope="row">POST /todos/42, no body</th><td>200; fixed HTML</td><td>405; method rejected</td></tr>
</tbody>
</table>
</div>

A **response contract** is the set of properties your caller actually requires. For these demos, the expected greeting is a useful smoke-test contract. For a todo API, you would need a different contract: perhaps JSON with the requested identifier, a deliberately defined missing-record response, and rejection of an unsupported method. Those are proposed application requirements, not features demonstrated by these hello programs.

Keep a small worksheet beside your experiment:

```text
Source commit and compiler:
Native binary or another backend:
Request method and path:
Expected status and Content-Type:
Expected body or selected fields:
Unwanted path and expected result:
Unwanted method and expected result:
Observed result and first error:
```

For example, capture a Bendo response to separate status, headers and body rather than trusting a terminal full of text:

```bash
curl --max-time 5 -sS -D hello.headers -o hello.body \
  -w '%{http_code}\n' http://127.0.0.1:8787/todos/42
cat hello.headers
cat hello.body
```

The expected status here is 200 and the expected body is the literal greeting above, not a todo object. Inspect the content type too. Do not add curl's `-L` while investigating a route response: following redirects would make the final page answer a different question from the immediate status.

If you want executable header and payload assertions after this first check, [Hurl HTTP tests: catch a false green](https://builtwithrust.com/guides/hurl-http-tests) provides a worked local fixture that deliberately keeps status 200 while changing a required JSON value. It is a follow-up on testing a response contract, not documentation for Bend or Bendo. You do not need Hurl to run this article's curl probes.

<span id="limits"></span>

## 5. Read the limits before choosing the next project

The [community compute server's pinned source](https://github.com/iamsahilsonawane/bend2-http-server/tree/66a9258100f1d55e5cabc37f8c30774e20061b69) is useful for studying socket effects, routing and a computation module separately. Its README describes health/runtime-information endpoints and CPU/GPU-oriented compute paths. That makes it a more focused architecture example than a general framework recommendation.

However, its socket calls differ from the official 2.0.39 example, including the listener and receive interfaces. **We did not build or run that community server for this article.** Do not substitute its command into the working official-demo instructions and assume compatibility. The [catalog entry](/projects/bend-http-server/) keeps the project and the separate official-demo path distinct.

Its source reads a request with a single receive operation. TCP is a byte stream, not a sequence of complete HTTP messages: [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html#name-key-tcp-concepts) explains that application writes and reads do not preserve message boundaries. A small request can still arrive in pieces. Passing our ordinary local probes does not test split headers, large bodies, timeouts, persistent connections or malformed requests.

Also separate connection concurrency from parallel computation. The [versioned Bend guide](https://github.com/bendlang/bend/blob/v2.0.39/guide/GUIDE.md#parallelism) says the JavaScript target runs sequentially. Native worker settings and GPU-capable syntax do not, by themselves, prove a faster HTTP service. We ran native binaries with two CPU workers and GPU disabled; we did not measure speedup or test a GPU path.

Finally, distinguish a proof claim from an HTTP result. Bendo documents proofs for pure framework components while keeping socket effects outside that scope. The compute server's laws concern its arithmetic computation and range predicate, not every parser or socket behavior. This article ran no `--verdict` checks. The [proof-workflow guide](/blog/bend-2-proof-workflow) shows why an ordinary checker pass and additional kernel validation are separate results.

Neither tested hello example establishes TLS termination, authentication, durable storage, safe public deployment or complete HTTP handling. Keep them local while learning. If your immediate task is a production web application, require evidence for those needs rather than adopting a project because its first greeting worked.

## Troubleshoot the first failed response

If curl reports a connection refusal, first check the server terminal. A successful compile does not mean the binary is still running. Confirm its announced address and port, and keep the first startup error. Do not start several copies and then guess which one answered. A timeout is also a failed observation; the five-second limit above bounds waiting rather than defining a performance target.

If compilation fails, record the compiler version, selected source commit and first diagnostic together. Reconfirm that the Bendo command uses the pinned executable, not the compiler selected for the official demo. Changing the compiler and the source at the same time makes it harder to identify which change mattered. A dependency-fetch failure is different from a type error; preserve the distinction instead of replacing both with “does not work.”

If headers arrive but reading the body fails, keep both observations. During an initial probe, sending a body-bearing POST to the official demo produced a connection-reset error while our Python client read the response. We did not turn that partial read into a successful body result. The completed matrix deliberately uses bodyless POST requests; it says nothing about upload support. That failure is another reason to specify the request body in a reproduction rather than reporting only a URL and a status code.

## Keep one working result before adding features

Choose the smallest program that answers your question. Save its source commit, compiler version and observed response. Then replace one broad hello handler with the route your caller needs and keep the unwanted-path and unwanted-method probes beside it.

For libraries to explore after that first response, browse the [Bend library catalog](/?category=libraries) and follow each project's original sources. The [package-import walkthrough](/blog/bend-2-package-imports) helps you inspect a versioned dependency before using it. A catalog visit should lead to a small result you can explain, not an assumption that every listed project is production-ready.

<script type="application/ld+json">{"@context":"https://schema.org","@type":"HowTo","name":"Bend 2 HTTP Server: Tested First Use","description":"Run pinned official and Bendo hello servers locally, then inspect status, headers, bodies and unwanted requests.","step":[{"@type":"HowToStep","name":"Keep the compiler and project versions together","text":"Record the compiler version and select the official 2.0.39 demo or Bendo's pinned 2.0.38 compiler.","url":"https://builtwithbend.com/blog/bend-2-http-server#versions"},{"@type":"HowToStep","name":"Run the official HTTP demo on loopback","text":"Compile the versioned official demo, run it on loopback port 8080, and inspect its fixed HTML responses.","url":"https://builtwithbend.com/blog/bend-2-http-server#official"},{"@type":"HowToStep","name":"Run Bendo's wildcard hello","text":"Select the pinned Bendo checkout, compile its hello with Bend 2.0.38, and probe port 8787.","url":"https://builtwithbend.com/blog/bend-2-http-server#bendo"},{"@type":"HowToStep","name":"Compare response contracts","text":"Compare the immediate status, content type and body; test an unwanted path and a bodyless unsupported method.","url":"https://builtwithbend.com/blog/bend-2-http-server#responses"},{"@type":"HowToStep","name":"Read the limits before expanding","text":"Separate source-only community-server observations, concurrency, proofs and production requirements from the checked local hello results.","url":"https://builtwithbend.com/blog/bend-2-http-server#limits"}]}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Built with Bend","item":"https://builtwithbend.com/"},{"@type":"ListItem","position":2,"name":"Blog","item":"https://builtwithbend.com/blog/"},{"@type":"ListItem","position":3,"name":"Bend 2 HTTP Server: Tested First Use","item":"https://builtwithbend.com/blog/bend-2-http-server"}]}</script>
