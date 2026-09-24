---
title: "Bend Programming Language: What You Can Build with Bend 2"
description: "Explore the Bend programming language through five Bend 2 projects: a Doom recreation, an SVG editor, a database, a fractal explorer, and an HTTP server."
published_at: 2026-09-24
keywords: [Bend programming language, Bend 2, Bend 2 projects]
topics: [Bend 2, Project examples]
author: Built with Bend
image: /static/social/bend-2-projects.png
image_alt: "What can you build with Bend 2? Five projects worth exploring."
---

A programming language gets more interesting when someone builds something you can inspect. With Bend 2, that includes a recreation of Doom's first level, an SVG editor, a storage engine, and a Mandelbrot explorer.

If you've been reading about the **Bend programming language** and wondering what lies beyond the parallel-computing demos, these projects are a useful starting point. Each has public source code, and each uses Bend for a different kind of work.

First, one distinction matters: this article covers **Bend 2**. The current [official Bend repository](https://github.com/bendlang/bend#limitations) explicitly says that Bend 1 programs and HVM do not carry over. An older tutorial may describe a different language and toolchain from the one these projects use.

*Sources checked on September 24, 2026. Project descriptions are based on their repositories and documentation, not independent runtime benchmarks.*

## What is the Bend programming language?

Bend 2 combines a programming language with a proof-checking workflow. Its Python-like surface syntax sits over a system with dependent types: types that can express properties of values, rather than just broad categories such as strings or numbers.

The practical idea is to state a rule your program should obey, then supply a proof that the implementation satisfies it. Bend's official workflow uses `LAWS.bend` for those rules and `PROOF.bend` for their proofs. The [Bend website](https://bend-lang.com/) demonstrates this with a game rule that must remain true after the code changes.

For a developer, the important question becomes: **which behavior have we actually specified and checked?** A proof of one property is not a promise that every part of an application is correct. An incomplete specification can leave important behavior uncovered.

Bend also targets parallel computation. Its current compiler supports C, Metal, CUDA, and JavaScript, although the JavaScript target runs sequentially. The [official limitations](https://github.com/bendlang/bend#limitations) describe a young toolchain, including restrictions on parallelism and unresolved compiler and proof-system concerns. That makes concrete projects especially valuable: they show the implementation choices behind the headline capabilities.

## Five Bend 2 projects worth exploring

These aren't ranked from best to worst. Pick the one closest to the kind of software you want to understand.

### 1. Bendoom: a game with simulation rules to inspect

[Bendoom](https://builtwithbend.com/projects/bendoom/) recreates Doom's E1M1 level in Bend 2. Its repository documents combat, doors, pickups, sound, music, and gameplay recording with video export. It offers releases for Linux and Apple Silicon macOS, while noting that macOS gameplay and audio still need hardware testing.

The useful learning material isn't just the familiar game. The repository separates out Bend source and includes `LAWS.bend` and `PROOF.bend` for simulation invariants. That gives you somewhere concrete to look when asking how a game describes rules that should survive later changes.

Start with the simulation laws, then find the corresponding game behavior. Which properties are formalized? Which behaviors are checked by tests or comparison with a reference implementation? Those are more revealing questions than simply asking whether the whole game is “proven.”

**Explore it for:** game logic, simulation invariants, and a substantial Bend application. [Read the Bendoom source and README](https://github.com/eliesgalvira/bendoom).

### 2. Bend SVG Studio: an editor that does its own rendering

[Bend SVG Studio](https://builtwithbend.com/projects/bend-svg-studio/) is an SVG viewer and editor with native and browser interfaces. The project implements SVG parsing, geometry, painting, rasterization, hit testing, and editing in Bend.

Its browser interface has an unusual boundary: the browser displays PNG frames generated from Bend-rendered pixels. It isn't handing the SVG document to the browser's own SVG renderer. Both interfaces use a shared document reducer, which handles changes to the editor's state.

This makes it a useful project for studying how an application separates its document model from presentation. Follow an edit from the interface through the shared state and into the resulting image.

The README documents incomplete SVG conformance, CPU rendering, and a macOS requirement for the native window. Treat it as an implementation to study, not a drop-in replacement for every SVG engine.

**Explore it for:** parsing, rendering, editor state, and shared application logic. [Read the SVG Studio source and README](https://github.com/nicolas-abril/bend2-svg-demo).

### 3. MyLSM: an experimental storage engine

[MyLSM](https://builtwithbend.com/projects/mylsm/) is a log-structured merge-tree key-value store implemented in Bend 2. The project includes durable-storage machinery such as a write-ahead log, SSTables, compaction, and recovery.

It's an interesting change of pace from graphics demos. Storage forces you to think about what happens after a write, a deletion, a restart, or a failure—not just whether a computation returns the expected answer once.

MyLSM also distinguishes its pure, in-memory library interface from the repository's durable-storage implementation. Its documentation keeps storage I/O on the CPU; GPU execution applies only to suitable pure computation.

The project's correctness notes are worth reading alongside the code. They distinguish existing proof witnesses and executable checks from general properties and host I/O behavior that still need stronger validation. The README also identifies remaining work before making production or competitive claims.

**Explore it for:** storage architecture and the boundary between checked computation and external effects. [Read the MyLSM source and README](https://github.com/FabianVegaA/mylsm).

### 4. Bend 2 Mandelbrot: GPU computation inside a native application

[Bend 2 Mandelbrot](https://builtwithbend.com/projects/bend-2-mandelbrot/) is an interactive fractal explorer for Apple Silicon Macs. It supports zooming, panning, coloring, and deep-zoom experiments.

The implementation matters as much as the image. Bend GPU code handles ordinary-depth rendering, while dedicated Metal kernels handle the multiprecision rendering path. It is a mixed-language application, not evidence that every part of a native interface or deep-zoom algorithm comes from Bend alone.

That boundary is useful to study. Where does Bend express the computation, where does the project use platform-specific code, and what happens when a user changes the view before rendering finishes?

The repository documents its Apple toolchain requirements and distinguishes rendering modes. Check those before trying it on your own machine.

**Explore it for:** GPU workloads and integration with a platform-specific application. [Read the Mandelbrot source and README](https://github.com/tomc98/bend-2-mandelbrot).

### 5. Bend HTTP Server: separating requests from computation

[Bend HTTP Server](https://builtwithbend.com/projects/bend-http-server/) is a focused HTTP/1.1 server experiment. Its layout separates socket operations from request parsing, response formatting, routing, and computation.

It includes routes that perform a fork-join computation on the CPU or dispatch it to the GPU. The accompanying laws and proofs address agreement between the computation paths. This is a useful example of choosing a specific property to check, rather than making a blanket claim about server correctness.

The project also makes an important development distinction: running through the JavaScript backend is single-threaded. Native compilation is needed for the demonstrated multicore and GPU execution paths.

Read this as a small server implementation, not a complete web framework. Its value is that the boundaries are visible: parsing and routing on one side, socket effects on another, and an isolated workload to experiment with.

**Explore it for:** server structure and CPU/GPU computation behind an HTTP interface. [Read the HTTP server source and README](https://github.com/iamsahilsonawane/bend2-http-server).

## How to choose your first Bend 2 example

Choose one question before choosing a repository:

- **How do I express a rule about changing application state?** Start with Bendoom's simulation laws.
- **How can two interfaces share an application core?** Follow SVG Studio's document reducer.
- **What sits outside a proof about pure code?** Compare MyLSM's computation and storage-I/O boundaries.
- **How does Bend fit alongside native GPU code?** Trace the Mandelbrot rendering paths.
- **How do requests reach parallel computation?** Follow the HTTP server's routing and compute modules.

Then narrow the reading to one behavior. Trace its input, implementation, and output. If there is a law, inspect what it says before reading the proof. If there is a performance claim, look for the workload, execution mode, hardware, and measurement method.

You don't need to understand the entire repository to learn something useful from it.

## Where to go next

For language syntax and installation, start with the [official Bend site](https://bend-lang.com/) and its linked guide. For project setup, follow the chosen repository's own requirements: examples may depend on a particular toolchain version or operating system.

For more applications to read, [browse the Built with Bend directory](https://builtwithbend.com/). It links builds to their sources so you can move from “someone made this” to “here is how it works.”

Already building something with Bend 2? [Submit your build](https://builtwithbend.com/submit/) so other developers can learn from it.
