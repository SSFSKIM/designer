# W27c G1d native sitting — 2026-09-14

Machine: Mac14,12, macOS 26.5.2 (25F84). Automatic download and macOS update installation were both 0. The only display was BetterDisplay `가상 16:9`, persistent id `7709FD0F-F423-4277-B0C8-7CA94F85723A`: mode 68 at 2x, mode 69 at 1x, restored to mode 68 at 2026-09-14T02:16:35Z. Increase Contrast and Reduce Transparency each read 0 before both standard passes. The open-launched, ad-hoc-signed bundle at `/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app` reported ScreenCaptureKit OK at both backing scales and was not rebuilt. Its executable SHA-256 is `bd3092e8d6d1f50ba43124adf42bed8a29e96646adb97bb3a538582653fda212`.

Each pass was launched detached by `launch.sh` through `nohup` and `caffeinate`, with pid and log files in the raw sitting root. No browser suite or web capture ran beside it, no input was synthesised, and the harness did not report a lock or idle refusal. Raw runs remain at `/Users/new/vitrea-w27c-g1d-2026-09-14`.

## Pre-capture rehearsal

The first 2x dry run presented **8**, not the declared 4: both light-standard profiles still said `scenes: "all"`, so the additive scene ids entered the light profile as well as the explicit dark list. No pixel was captured. The pre-existing 164-member light profile set was frozen into an explicit list at `582a145`, excluding only the four new dark-only ids; the scene-matrix test then reproduced the harness selection and pinned four cells at each scale. The corrected 2x dry run and the 1x dry run each presented **4** and passed. `dry-2x-before-profile-scope.txt` preserves the refused rehearsal; `dry-1x.txt` preserves the second scale.

## inactive-2x

| run | cells | attested | first capture | last capture | min HID idle s | under 45 s | manifest SHA-256 |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| run-1 | 4 | 4 | 2026-09-14T02:05:51Z | 2026-09-14T02:06:19Z | 554.1 | 0 | `31ef5c3c2859e50890fedd808c13173e8746db75817e242b540d09e717f32835` |
| run-2 | 4 | 4 | 2026-09-14T02:06:30Z | 2026-09-14T02:06:58Z | 593.0 | 0 | `b387d185ab842316736f11216dcce34db51bf72be90e367344ef1e67a399800e` |
| run-3 | 4 | 4 | 2026-09-14T02:07:08Z | 2026-09-14T02:07:37Z | 631.9 | 0 | `5388ad70ea7a35d3e250f7252cdfbb8a75773ff8dc4a833852bbf09f25427a4f` |
| run-4 | 4 | 4 | 2026-09-14T02:07:47Z | 2026-09-14T02:08:17Z | 670.8 | 0 | `222218c5c7cad898eeb947856b17cb41e22ee4869145acdd3ada7e8cbe21ce7c` |
| run-5 | 4 | 4 | 2026-09-14T02:08:27Z | 2026-09-14T02:08:57Z | 711.0 | 0 | `3a949cc8daffa6a17ada04b9c92cef670678eb0b4ebd3c19c44babec689c4664` |
| run-6 | 4 | 4 | 2026-09-14T02:09:07Z | 2026-09-14T02:09:36Z | 750.9 | 0 | `f6a0d563bfc8c827d4b8c7700a01b50162b6cfca872195aa680a733b09cefd3f` |
| run-7 | 4 | 4 | 2026-09-14T02:09:46Z | 2026-09-14T02:10:15Z | 789.8 | 0 | `8ed776b5fe27e67779b894ab0af035b06005578125ff9b6948b79f111a0886a5` |

Plurality:
- `apple-macos-26.5-2x-dark-standard/mid-light-solid__capsule-button__inactive`: 7/7, published SHA-256 `8a3e36c08277b965e3f31718b27e0e657eda6fb7c04492cf0bd9ad1a9c8b3b59`.
- `apple-macos-26.5-2x-dark-standard/mid-light-solid__rrect-sm__inactive`: 7/7, published SHA-256 `2e51336b646c2a05a71345204ce604d8293b8cbe5e0f4586ca6415da75eaf8ce`.
- `apple-macos-26.5-2x-dark-standard/mid-light-solid__rrect-ml__inactive`: 7/7, published SHA-256 `78a793134aa79cc81de1cc0b2b961c0743a872c26be449306ba0d7b8f80913d6`.
- `apple-macos-26.5-2x-dark-standard/mid-light-solid__rrect-lg__inactive`: 7/7, published SHA-256 `451e640b6e2a215b580618912fe2acf92d8da6b1a6a32dbdc448fe6c5f3ff343`.

## inactive-1x

| run | cells | attested | first capture | last capture | min HID idle s | under 45 s | manifest SHA-256 |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| run-1 | 4 | 4 | 2026-09-14T02:11:45Z | 2026-09-14T02:12:14Z | 908.5 | 0 | `ae1795d39fba28b738f0e12333451ceb371359198ebfac9f7b5e99abba0a0809` |
| run-2 | 4 | 4 | 2026-09-14T02:12:24Z | 2026-09-14T02:12:53Z | 947.3 | 0 | `86e21f2f27acc1958e78e1246f15765ffb15658d54b066e275a104c86d04c992` |
| run-3 | 4 | 4 | 2026-09-14T02:13:03Z | 2026-09-14T02:13:33Z | 986.1 | 0 | `923ae8370507984c4e6070d7dc91bbd27110f9aace59266023d7f1d8ffd8cebc` |
| run-4 | 4 | 4 | 2026-09-14T02:13:43Z | 2026-09-14T02:14:11Z | 1026.1 | 0 | `06e3db23c1db1fcbb9de858a2a9e2193e0e0af4e4bce41926a46a4affc3286a0` |
| run-5 | 4 | 4 | 2026-09-14T02:14:21Z | 2026-09-14T02:14:50Z | 1064.9 | 0 | `f513ebb255fd94e8df16e53d9d57011bb0ba870807142ca858b93b9fe7f85b91` |
| run-6 | 4 | 4 | 2026-09-14T02:15:00Z | 2026-09-14T02:15:29Z | 1103.7 | 0 | `8cb31e2e8fa604e67ba392f2f40fac3779a627603080c09e28b74238cf18aac3` |
| run-7 | 4 | 4 | 2026-09-14T02:15:39Z | 2026-09-14T02:16:08Z | 1142.4 | 0 | `6eb55e4978f7d841197a475bec3883cd9c7c2eadc0dd4f89b8de1c6ce7a72095` |

Plurality:
- `apple-macos-26.5-1x-dark-standard/mid-light-solid__capsule-button__inactive`: 7/7, published SHA-256 `bf0d419efd662b1fe8ac230e6b0f498eca02f397a7dd0da10c99a0f2e5680e3a`.
- `apple-macos-26.5-1x-dark-standard/mid-light-solid__rrect-sm__inactive`: 7/7, published SHA-256 `243da66400529f1089578253b5c33ed3ce257a043e2f5fad615ad4806776dbee`.
- `apple-macos-26.5-1x-dark-standard/mid-light-solid__rrect-ml__inactive`: 6/7, published SHA-256 `90072530b8b4dbebcdf28f410d7fe2f3a7cd6fb148d7edbdf3d3dc7e7bcc5f17`.
- `apple-macos-26.5-1x-dark-standard/mid-light-solid__rrect-lg__inactive`: 6/7, published SHA-256 `3b65c53c2ba2859f2883b25625720fd4c3564ff44d215d0a55269362225af6fc`.

## Publication

`materialize --set probe --frequency-settle` first resolved both passes without writing, then published each pass separately beside the existing bundle. The 2x cells were 4/4 unanimous. At 1x the capsule and rrect-sm were unanimous; rrect-ml and rrect-lg were each 6/7, with the minority differing incidentally at no more than one 8-bit code. No cell was state-ambiguous or refused. `capture-record.json` proves every published PNG is the seven-run plurality.

The bundle moved from 611 to 619 manifest entries and gained `mid-light-solid@1x` and `mid-light-solid@2x`. `manifest-doctor` ran before and after. Against capture-input head `582a145`, `round-trip.json` reports 0 pre-existing entries changed, 0 pre-existing PNGs changed or lost, all 11 prior provenance blocks kept, and exactly the expected 8 entries added. The two new publication phases bring the provenance block count to 13. Raw run manifests and the exact per-run idle and attestation readings stay in `capture-record.json`; the raw PNGs stay on this machine.
