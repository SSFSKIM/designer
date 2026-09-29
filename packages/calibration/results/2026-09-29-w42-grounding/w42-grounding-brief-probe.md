# W42 grounding memo C: the probe series and the smallest capture that still identifies

Read `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-common.md` first, then memos A and B:
- `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-argument.txt`
- `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-kernel.txt`

Memo path: `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-probe.txt`. Scratch:
`~/vitrea-w42/grounding/probe/`.

## What A and B agree on
Apple's body is a heavy blur averaged in ENCODED space, plus a narrow detail term that passes
one side only. In the light scheme detail can rise above the heavy floor ("lighten"). In the dark
scheme it can fall below the heavy ceiling ("darken"). This holds in both poses. The receded pose
widens only the narrow component. Apple's widths hold in CSS px, while vitrea's deep blur is fixed
in device px. An uncommitted W29 layer dump points at a blur-fill layer composited with lighten
or darken: `/Users/new/vitrea-w29-g0-scratch/c/dump-sdk27/`.

## Your admitted evidence
It widens the common file's. The parent ruled that the user's chosen plan puts W42's structured
holdout in the NEW native capture. So you may now read the canonical PROBE cells' native pixels:
the checker pitch series, the low-contrast 128/229 checker, and the text cells, in every
endpoint and scale. You may also read the in-tree W34 archive's checkers, which are spent.
Canonical holdout and recorded cells stay closed.

## Questions
1. On the probe series, identify what A and B left open, for all four endpoints and both scales:
   - the narrow kernel's width and shape across pitch;
   - the form of the one-sided term: a hard max/min, a soft knee, or a lighten blend with an
     opacity;
   - the heavy component's width, and whether it is a group mean or a local blur limited to the
     footprint;
   - the averaging space on the non-binary checker.
   Prove every reader on vitrea's own captures first, as B did.
2. Read what the W29 dump shows of the filter chain: layer order, radii, blend modes and
   opacities by pose and span. State plainly what a dump across spans, poses and schemes would
   add. Treat dump numbers as pointers. They become evidence only when the pixels agree.
3. Given what the probes identify, shrink B's capture design to the smallest one that still
   identifies what remains and carries a structured holdout. List each cell family with the
   question it answers. Size it in cells, repeats and hours, and say what it drops against B's
   121-cell design and why.

Also note anything in the shipped material that is plainly a defect rather than a missing law,
such as the device-px blur that ignores the CSS scale. Give file:line and the evidence.
