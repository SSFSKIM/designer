---
"@vitreajs/vitrea": patch
"@vitreajs/vitrea-react": patch
---

Fix: the published `.d.ts` files typecheck for a consumer with `skipLibCheck: false`.

Both artifacts named WebGPU globals — `GPUDevice`, `GPUTextureView`,
`GPUPowerPreference` and eleven more — that nothing in the tarball declared. This
workspace resolved them out of `lib.dom.d.ts`, which only ships the WebGPU
interfaces from TypeScript 6.0 onward, so a consumer on TypeScript 5 read 29
`TS2304`s out of `node_modules`.

Each artifact now declares those names itself: the interfaces empty and global, so
they merge with the consumer's real WebGPU types wherever they have them, and the
two string-union aliases module-local, because a type alias cannot merge. Nothing
was added to either package's dependencies, and the emitted JavaScript is
unchanged. Verified with `skipLibCheck: false` on TypeScript 5.8, 5.9, 6.0 and
7.0, with the DOM lib, with `@types/web` in place of it, and alongside a
consumer's own `@webgpu/types`.
