# The 1x labelled probe, both window poses (2026-09-12, taken in the 26.5 sitting)

The run §5.136 §5 scheduled: `scenes-w27e-probe.json`'s 25 scenes per scheme, at **1x**
(BetterDisplay virtual screen "가상 16:9", displayplacer mode 69, `backingScaleFactor 1.0`), through
`dump-layers`, so the 2x/non-key corpus of `2026-09-11-w27e-probe/` and the 1x/key corpus of
§5.133 can be separated on the pose axis. Nothing here is a fixture; a dump captures no pixels.
Each dump records `isKeyWindow`; the `recede/` dumps also record `appIsActive` and
`activationPolicy`, added to the harness during the sitting (branch `w27-dump-layers-inactive`).

| arm | launch | light | dark | what it is |
| --- | --- | ---: | ---: | --- |
| `active/` | `open -W … --require-key` (regular policy, bundle launch) | 25 dumps: **9 key, 16 not key** | 25 dumps: 25 key | The active pose, asserted key at the gate. The light arm lost key after its 9th scene and did not regain it; the 16 non-key dumps are the *regular-policy* recede (the application stayed active), which is not the mechanism the capture uses. The dark arm held key throughout. |
| `policy-only/` | `VITREA_ACTIVATION_POLICY=accessory ./capture.sh dump-layers` (the runbook's first recipe) | 25 dumps: 25 key | 25 dumps: 25 key | **The active pose, not the recede.** An `.accessory` application that calls `activate` becomes active and its key-capable window becomes key. Kept under the name of what it is; on the machine this arm's raw directory is called `inactive/`. |
| `recede/` | `dump-layers --inactive` (build beside the granted bundle) | 25 dumps: key false, active false, accessory | 25 dumps: key false, active false, accessory | The recede by mechanism: `Capture.presentInactive` — `.accessory` before the run loop, a non-key-capable window, ordered front and never activated. |

So the 1x corpus separates as: **active pose** = `active/dark` (25) + `active/light`'s 9 key dumps +
`policy-only/*` (50); **recede** = `recede/*` (50). `active/light`'s 16 non-key dumps are a third
state (regular policy, application active, window not key) and are read on their own.

Order taken: `active/light` 11:26:49Z, `policy-only/light` 11:30:21Z, `active/dark` 11:33:53Z,
`policy-only/dark` 11:37:23Z (all before the inactive 1x pass), `recede/light` and `recede/dark`
13:15–13:22Z (after it). `--settle 8` throughout. Logs under `logs/`.

The reading (which operators sit on which layers under which pose, against §5.133 §8 and
§5.136 §5's four-outcome table) is W27e G2's, per Decision Log 15; nothing here is read yet.
