# The 26.5 sitting — record (2026-09-12)

Machine: macOS 26.5.2 25F84 on Mac14,12. Sitting dir `/Users/new/vitrea-w27-26.5-run` (raw runs stay there; runbook §5). Driven by the parent session with the user's authorisation; the two accessibility toggles were the user's hand.

- Screen Recording: the runbook's `./capture.sh probe` reports the terminal's grant, not the bundle's; the open-launched probe printed OK at 2x and at 1x (runbook §1 corrected at 9a8d05b5).
- The 1x labelled probe: the runbook's recede recipe (policy variable only) produced KEY dumps on all 50 'inactive' arms — an .accessory application that activates still becomes active and key. Those dumps are committed under results/2026-09-12-w27e-probe-1x/policy-only/ as what they are: the ACTIVE pose. The recede was then taken through `dump-layers --inactive` (branch w27-dump-layers-inactive, built beside the granted bundle) under recede/: 50 dumps, all key=false active=false accessory. The active light arm through `open -W --require-key` lost key after its 9th scene (16 of 25 record key=false); the active dark arm is 25/25 key.
- Chrome (an automation instance) and Docker Desktop were running during the 2x inactive pass; neither is a capture process and the runs were clean. The Chrome instance had exited by the active 2x pass.
- The idle gate is enforced at a run's opening (45 s) and only RECORDED per cell; a touch mid-run files the cell with its idle beside it. The record lists every cell under 45 s of idle per run; the pose attestation held on all of them, and the seven-run plurality at materialize time is where a disturbed byte-state would show.
- The script, the runbook and the harness were corrected during the sitting on branch w27-dump-layers-inactive: `dump-layers --inactive` and per-dump pose facts; `VITREA_BUILD_OUT` for a side build; `VITREA_BED_FILE` and bed-inactive-a11y.txt; the runbook's probe launch and recede recipe. No fixture, profile, golden, scene, matrix row or declared bed file moved.
- Display restored to mode 68 (2x HiDPI) and the sitting's caffeinate ended after the last pass.

## inactive-2x

Display: 가상 16:9 (BetterDisplay virtual screen, the machine's only display) at 2560x1440 HiDPI, displayplacer mode 68, backingScaleFactor 2.0. Toggles: standard (both off). Launched 09:52Z by this session after the user's go; run 1 attempt 1 refused at the opening idle gate (the launch turn itself), attempt 2 captured. Runs 4 and 5 carry cells captured while the input was live (listed below); every one attested the pose.

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 76 | 76 | 2026-09-12T09:54:04Z | 2026-09-12T10:06:11Z | 117.0 | 0 | 6 | `e815162a9f093e18…` |
| run-2 | yes | 76 | 76 | 2026-09-12T10:06:21Z | 2026-09-12T10:18:27Z | 853.7 | 0 | 6 | `5c242a7cd88e2b4c…` |
| run-3 | yes | 76 | 76 | 2026-09-12T10:18:37Z | 2026-09-12T10:30:42Z | 1589.6 | 0 | 6 | `015426b6c7bc25a1…` |
| run-4 | yes | 76 | 76 | 2026-09-12T10:30:52Z | 2026-09-12T10:42:51Z | 0.1 | 13 | 6 | `cc66e53401c11d3d…` |
| run-5 | yes | 76 | 76 | 2026-09-12T10:43:02Z | 2026-09-12T10:55:00Z | 4.9 | 3 | 6 | `60d85e97b4188236…` |
| run-6 | yes | 76 | 76 | 2026-09-12T10:56:40Z | 2026-09-12T11:08:34Z | 124.4 | 0 | 6 | `062d53915e095f27…` |
| run-7 | yes | 76 | 76 | 2026-09-12T11:08:45Z | 2026-09-12T11:20:40Z | 848.7 | 0 | 6 | `bd65dfc0264cc701…` |

Cells captured under 45 s of input idle (the gate is enforced at a run's opening and only recorded per cell; the pose attestation still held on every one of these): run-4: `checkerboard-64__rrect-lg__inactive`, `checkerboard-8__rrect-md__inactive`, `checkerboard__glass-over-glass__inactive`, `dark-solid__rrect-48__inactive`, `dark-solid__rrect-sm__inactive`, `hc-text-7__rrect-md__inactive`, `hc-text-7__rrect-md__inactive`, `mid-chroma-solid__capsule-button__inactive-tint-orange`, `mid-dark-solid__capsule-button__inactive`, `mid-dark-solid__rrect-lg__inactive`, `mid-dark-solid__rrect-lg__inactive`, `mid-dark-solid__rrect-sm__inactive`, `photo__rrect-md__inactive`; run-5: `hc-text__rrect-sm__inactive`, `mid-chroma-solid__capsule-button__inactive`, `photo__glass-over-glass__inactive`

Refusals and retries (from the pass log):
- `run 1 attempt 1: refused for idle — leave the machine alone`
- `run 6 attempt 1: refused for idle — leave the machine alone`

Cells pixel-identical to their background raster in at least one run (the harness's own caveat; zero material pixels): `dark-solid__capsule-button__inactive`, `dark-solid__rrect-48__inactive`, `dark-solid__rrect-sm__inactive`

## active-2x

Display: same virtual screen, mode 68, backingScaleFactor 2.0. Toggles: standard (both off). 

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 4 | 4 | 2026-09-12T11:21:41Z | 2026-09-12T11:22:11Z | 1625.5 | 0 | 0 | `d840b586bf9b57cc…` |
| run-2 | yes | 4 | 4 | 2026-09-12T11:22:21Z | 2026-09-12T11:22:51Z | 1665.4 | 0 | 0 | `47f69d0743f3df7a…` |
| run-3 | yes | 4 | 4 | 2026-09-12T11:23:01Z | 2026-09-12T11:23:31Z | 1705.3 | 0 | 0 | `32ad0929b2f9d8ec…` |
| run-4 | yes | 4 | 4 | 2026-09-12T11:23:41Z | 2026-09-12T11:24:12Z | 1745.2 | 0 | 0 | `b4c8d15d0b7ce70c…` |
| run-5 | yes | 4 | 4 | 2026-09-12T11:24:22Z | 2026-09-12T11:24:51Z | 1786.0 | 0 | 0 | `aef512e119275ed5…` |
| run-6 | yes | 4 | 4 | 2026-09-12T11:25:02Z | 2026-09-12T11:25:30Z | 1825.7 | 0 | 0 | `ea49c5144c131d10…` |
| run-7 | yes | 4 | 4 | 2026-09-12T11:25:40Z | 2026-09-12T11:26:11Z | 1864.4 | 0 | 0 | `a4a5f1b8cc35479c…` |

## inactive-1x

Display: same virtual screen switched to displayplacer mode 69 (2560x1440, scaling off), backingScaleFactor 1.0 confirmed by the open-launched probe at 11:26Z. Toggles: standard (both off). Preceded by the 1x rehearsal (76 cells presented, PASS 11:50Z).

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 76 | 76 | 2026-09-12T11:51:20Z | 2026-09-12T12:03:13Z | 0.3 | 14 | 6 | `448c11735a08ea9a…` |
| run-2 | yes | 76 | 76 | 2026-09-12T12:03:23Z | 2026-09-12T12:15:16Z | 0.3 | 12 | 6 | `3e519c77798dbd13…` |
| run-3 | yes | 76 | 76 | 2026-09-12T12:15:26Z | 2026-09-12T12:27:17Z | 173.9 | 0 | 6 | `533f962fc87de673…` |
| run-4 | yes | 76 | 76 | 2026-09-12T12:27:27Z | 2026-09-12T12:39:20Z | 895.0 | 0 | 6 | `c442315b7edcf665…` |
| run-5 | yes | 76 | 76 | 2026-09-12T12:39:30Z | 2026-09-12T12:51:23Z | 6.7 | 5 | 6 | `02f2bd5032d4c51b…` |
| run-6 | yes | 76 | 76 | 2026-09-12T12:51:33Z | 2026-09-12T13:03:25Z | 150.7 | 0 | 6 | `b9c9f416fa955498…` |
| run-7 | yes | 76 | 76 | 2026-09-12T13:03:35Z | 2026-09-12T13:15:26Z | 872.5 | 0 | 6 | `83ea88dfe78dc28b…` |

Cells captured under 45 s of input idle (the gate is enforced at a run's opening and only recorded per cell; the pose attestation still held on every one of these): run-1: `checkerboard-4__rrect-md__inactive`, `checkerboard-lc16__capsule-button__inactive`, `dark-solid__capsule-button__inactive`, `dark-solid__rrect-48__inactive`, `dark-solid__rrect-80__inactive`, `hc-text-28__rrect-md__inactive`, `hc-text__rrect-lg__inactive`, `hc-text__rrect-sm__inactive`, `impulse__rrect-lg__inactive`, `impulse__rrect-lg__inactive`, `mid-chroma-solid__capsule-button__inactive-tint-orange`, `mid-dark-solid__rrect-md__inactive`, `mid-dark-solid__rrect-md__inactive`, `photo__glass-over-glass__inactive`; run-2: `checkerboard-64__rrect-md__inactive`, `checkerboard-64__rrect-md__inactive`, `checkerboard-8__rrect-lg__inactive`, `checkerboard-8__rrect-md__inactive`, `checkerboard-lc16__rrect-md__inactive`, `dark-solid__rrect-48__inactive`, `dark-solid__rrect-md-clear20__inactive`, `mid-chroma-solid__capsule-button__inactive`, `mid-chroma-solid__rrect-lg__inactive`, `mid-dark-solid__capsule-button__inactive`, `mid-dark-solid__rrect-lg__inactive`, `photo__glass-over-glass__inactive`; run-5: `checkerboard-8__rrect-md__inactive`, `dark-solid__rrect-48__inactive`, `hc-text__rrect-lg__inactive`, `impulse__rrect-lg__inactive`, `mid-dark-solid__rrect-lg__inactive`

Cells pixel-identical to their background raster in at least one run (the harness's own caveat; zero material pixels): `dark-solid__capsule-button__inactive`, `dark-solid__rrect-48__inactive`, `dark-solid__rrect-sm__inactive`

## active-1x

Display: same, mode 69, backingScaleFactor 1.0. Toggles: standard (both off). 

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 4 | 4 | 2026-09-12T13:23:06Z | 2026-09-12T13:23:36Z | 2044.0 | 0 | 0 | `78a8b8c44e1711b1…` |
| run-2 | yes | 4 | 4 | 2026-09-12T13:23:46Z | 2026-09-12T13:24:17Z | 2083.6 | 0 | 0 | `92b52008b4dc48c9…` |
| run-3 | yes | 4 | 4 | 2026-09-12T13:24:27Z | 2026-09-12T13:24:56Z | 2124.4 | 0 | 0 | `4205226beafd016f…` |
| run-4 | yes | 4 | 4 | 2026-09-12T13:25:06Z | 2026-09-12T13:25:35Z | 2163.9 | 0 | 0 | `27de8a5341e78564…` |
| run-5 | yes | 4 | 4 | 2026-09-12T13:25:46Z | 2026-09-12T13:26:15Z | 2203.4 | 0 | 0 | `cfda57ea5e1f9ea8…` |
| run-6 | yes | 4 | 4 | 2026-09-12T13:26:27Z | 2026-09-12T13:26:56Z | 2244.2 | 0 | 0 | `ab1914e20db024ef…` |
| run-7 | yes | 4 | 4 | 2026-09-12T13:27:06Z | 2026-09-12T13:27:36Z | 2283.8 | 0 | 0 | `2ae8e53a9e167ab4…` |

## inactive-1x-increase-contrast

Display: same, mode 69, backingScaleFactor 1.0. Toggles: Increase contrast ON (macOS force-couples Reduce transparency ON with it), set by the user's hand at 13:48:10Z. Own sitting root a11y-increase-contrast/ and VITREA_BED_FILE=bed-inactive-a11y.txt (14 ids: the bed's ids this profile declares) — the script names a pass by pose and scale only and feeds the whole 38-id bed, and the first rehearsal was refused for the 24 ids the profile does not declare. Second rehearsal presented 14 (13:52Z). Runs 1, 2 and 7 needed idle retries: the input was touched every few seconds between about 13:52Z and 13:59Z.

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 14 | 14 | 2026-09-12T13:57:10Z | 2026-09-12T13:59:16Z | 0.1 | 3 | 0 | `bbcc6e2d041254a9…` |
| run-2 | yes | 14 | 14 | 2026-09-12T14:00:56Z | 2026-09-12T14:03:01Z | 96.9 | 0 | 0 | `986b5fd75ed61767…` |
| run-3 | yes | 14 | 14 | 2026-09-12T14:03:11Z | 2026-09-12T14:05:15Z | 231.6 | 0 | 0 | `247a92d5cf147077…` |
| run-4 | yes | 14 | 14 | 2026-09-12T14:05:26Z | 2026-09-12T14:07:31Z | 367.1 | 0 | 0 | `f329af178eb36ee3…` |
| run-5 | yes | 14 | 14 | 2026-09-12T14:07:41Z | 2026-09-12T14:09:46Z | 501.8 | 0 | 0 | `6e863604d4745957…` |
| run-6 | yes | 14 | 14 | 2026-09-12T14:09:56Z | 2026-09-12T14:12:00Z | 7.0 | 1 | 0 | `2b2ff3371580074b…` |
| run-7 | yes | 14 | 14 | 2026-09-12T14:13:41Z | 2026-09-12T14:15:45Z | 4.9 | 5 | 0 | `72ac9a3546d9a217…` |

Cells captured under 45 s of input idle (the gate is enforced at a run's opening and only recorded per cell; the pose attestation still held on every one of these): run-1: `checkerboard-lc16__capsule-button__inactive`, `checkerboard__rrect-ml__inactive`, `hc-text__rrect-lg__inactive`; run-6: `checkerboard__rrect-ml__inactive`; run-7: `checkerboard-lc16__rrect-md__inactive`, `dark-solid__rrect-48__inactive`, `hc-text-28__rrect-md__inactive`, `hc-text__rrect-sm__inactive`, `photo__rrect-md__inactive`

Refusals and retries (from the pass log):
- `run 1 attempt 1: refused for idle — leave the machine alone`
- `run 1 attempt 2: refused for idle — leave the machine alone`
- `run 1 attempt 3: refused for idle — leave the machine alone`
- `run 2 attempt 1: refused for idle — leave the machine alone`
- `run 7 attempt 1: refused for idle — leave the machine alone`

## inactive-1x-reduce-transparency

Display: same, mode 69, backingScaleFactor 1.0. Toggles: Increase contrast OFF, Reduce transparency ON, set by the user's hand at 15:49:30Z. Same root pattern (a11y-reduce-transparency/) and the same 14-id list, which is identical for both accessibility profiles. Rehearsal presented 14 (15:51Z).

| run | banked | cells | attested | first capture | last capture | min HID idle s | cells under 45 s idle | identical-to-background | manifest sha256 |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- |
| run-1 | yes | 14 | 14 | 2026-09-12T15:52:03Z | 2026-09-12T15:54:07Z | 101.6 | 0 | 0 | `e997697fd97fa3ad…` |
| run-2 | yes | 14 | 14 | 2026-09-12T15:54:18Z | 2026-09-12T15:56:23Z | 237.3 | 0 | 0 | `4e76378b093d07d1…` |
| run-3 | yes | 14 | 14 | 2026-09-12T15:56:33Z | 2026-09-12T15:58:37Z | 371.8 | 0 | 0 | `caf24a38d1d2c7b2…` |
| run-4 | yes | 14 | 14 | 2026-09-12T15:58:47Z | 2026-09-12T16:00:52Z | 506.3 | 0 | 0 | `f2183d92968c01a8…` |
| run-5 | yes | 14 | 14 | 2026-09-12T16:01:02Z | 2026-09-12T16:03:07Z | 640.9 | 0 | 0 | `0baed952dc8dd574…` |
| run-6 | yes | 14 | 14 | 2026-09-12T16:03:17Z | 2026-09-12T16:05:21Z | 775.6 | 0 | 0 | `51d8dc7716048fd2…` |
| run-7 | yes | 14 | 14 | 2026-09-12T16:05:31Z | 2026-09-12T16:07:36Z | 910.2 | 0 | 0 | `78942c2373aa25ee…` |

## The 1x labelled probe, both poses

Committed under `results/2026-09-12-w27e-probe-1x/` (see its `index.md`). Each tally key reads `(isKeyWindow, appIsActive, activationPolicy, backingScaleFactor)`; `unrecorded` means the dump predates the fields `dump-layers --inactive` added.

- `active/dark`: 25 dumps; pose tally {"(True, 'unrecorded', 'unrecorded', 1)": 25}
- `active/light`: 25 dumps; pose tally {"(False, 'unrecorded', 'unrecorded', 1)": 16, "(True, 'unrecorded', 'unrecorded', 1)": 9}
- `policy-only/dark`: 25 dumps; pose tally {"(True, 'unrecorded', 'unrecorded', 1)": 25}
- `policy-only/light`: 25 dumps; pose tally {"(True, 'unrecorded', 'unrecorded', 1)": 25}
- `recede/dark`: 25 dumps; pose tally {"(False, False, 'accessory', 1)": 25}
- `recede/light`: 25 dumps; pose tally {"(False, False, 'accessory', 1)": 25}
