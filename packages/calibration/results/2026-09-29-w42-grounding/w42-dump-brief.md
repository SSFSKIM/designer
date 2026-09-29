# W42: dump Apple's glass layer tree across spans, poses and schemes (no pixels)

vitrea is a TypeScript runtime replicating Apple's Liquid Glass. W42 grounding found that Apple's
body is a heavy blur averaged in encoded space, plus a narrow detail term composited one-sidedly:
lighten in light, darken in dark. It also found that the unfocused window widens the narrow term.
An old uncommitted W29 dump, `/Users/new/vitrea-w29-g0-scratch/c/dump-sdk27/`, shows a glassBackground
filter with inputBlurRadius 5, a blur opacity graded by span and pose, and a radius-8 blur fill at
0.9 lighten or darken plus 0.546 normal. It covers only a few scenes and one receded cell. Read the
grounding memos for context:
- `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-kernel.txt` §4 and §7
- `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-argument.txt`

Task: use the EXISTING reference harness's `dump-layers` mode to read Apple's filter parameters.
Read `apps/reference-apple/README.md` and `Sources/main.swift` (`runDumpLayers`, `--inactive`,
`--scheme`, `--scenes`, `--settle`, `--out`), and `/Users/new/vitrea-w29-g0-scratch/c/dump-sdk27/*.out`
for how W29 ran it. Cover every canonical glass component and span in `scenes.json` on one
representative backdrop, plus photo and checkerboard on rrect-md, in:
- both schemes;
- both poses, using `--inactive` for receded;
- at the display's native 2x, and at 1x if the harness supports it without rebuilding.
Use `--settle 8`. Write output under `~/vitrea-w42/grounding/dumps/`, never under the repository or
`fixtures/`.

## Hard rules
- **The user asked to be told first, and wants this run only while away from the Mac.** Before
  launching anything, message the parent (to: "main") with the command, the scene count and the
  expected duration. Then wait until the Mac has been idle for at least 5 minutes: HID idle from
  `ioreg -c IOHIDSystem`, polling every 60 s, at most 3 hours of waiting. Launch only then. Stop
  between runs if idle drops below 60 s, and resume when it is idle again.
- Use only the existing built binaries. Never rebuild anything: no `build.sh`, no Xcode, no new
  bundle and no new bundle identifier. Never touch `apps/reference-apple/build` contents,
  `fixtures/` or `scenes.json`.
- Capture no pixels, and need no Screen Recording grant. If any system permission prompt appears
  (check with `osascript -e 'tell application "System Events" to get name of every window of
  every process'`), stop, click nothing, and report to the parent.
- Launch through `open --env VAR=value …` if env vars are needed. `launchctl setenv` does not reach
  the GUI session.

## Report
Write a memo to `/Users/new/.claude/jobs/17c7ce02/tmp/w42-dumps.txt`: tables of the filter chain per
scheme × pose × component/span × scale. Cover layer order, blur radii, blend modes and opacities,
SDF grading, the face colour matrix and saturation, and anything that differs by pose or span. Say
which W29 pointers hold, which fail, and what the numbers imply for the native capture design. These
are pointers to Apple's declared configuration; pixels remain the evidence. Hand back the memo
path and a ten-line summary. No commits.
