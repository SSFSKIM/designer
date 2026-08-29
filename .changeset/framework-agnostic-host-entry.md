---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

The browser host is published in its own right: `@vitreajs/vitrea-web`.

Until now `vitrea` alone could not mount a root. The runtime is DOM-free by
design and the host layer reached npm only inlined inside `vitrea-react`, so the
only way to render glass in a browser was through React — a narrower promise than
"framework-agnostic runtime" reads. The host is now its own package, and the
three layer the way React's own do: a pure runtime, a DOM host over it, framework
bindings over that.

- **New:** `npm install @vitreajs/vitrea-web` and call `createGlassRoot` from
  plain JavaScript, or from a Vue, Svelte, Angular or Web-Components adapter. It
  is the same entry the React bindings are built on; there is no privileged path.
  The package README carries the imperative quickstart, and
  `e2e/fixtures/vanilla.ts` is that quickstart executed on three engines.
- **New:** `GlassRoot.subscribe(listener)` — join the root's frame loop instead of
  running a second `requestAnimationFrame` beside it. Listeners run after the
  frame, on a settled scene; one that throws is reported as the new
  `frame-listener-failed` diagnostic and unsubscribed.
- **Changed:** `@vitreajs/vitrea-react` now *depends* on `@vitreajs/vitrea-web`
  rather than bundling a copy of it, so a page that mounts one root through the
  bindings and another through the host directly shares a single host. Both are
  installed for you; `npm install @vitreajs/vitrea-react` is now enough on its
  own. The React bindings' motion also runs on the root's loop now rather than on
  one of their own — one wake-up per frame, and a defined order between the scene
  resolving and the springs stepping.
- **Changed:** core's `DiagnosticsChannel`, `Diagnostic`, `DiagnosticSink` and
  `createDiagnosticsChannel` are generic over their code union, with core's own
  union as the default. Every existing use reads unchanged; the browser host's
  channel is now an instantiation of core's rather than a second copy of the
  machinery.
