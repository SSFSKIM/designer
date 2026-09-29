# W42 grounding memo B — Apple's body blur: kernel, space, pose, and the capture that identifies it

Read `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-common.md` first. Memo path:
`/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-kernel.txt`; scratch
`~/vitrea-w42/grounding/kernel/`.

Question: measure the effective spatial transfer of Apple's body on structured canonical
calibration/validation cells, in all four endpoints (light and dark scheme, active and inactive
pose). Is the receded body blurred more than the active one? In linear or encoded space? What kernel
width and shape, and does it depend on the surface's size or span? Compare with vitrea's shipped
blur and scatter laws, as `material.ts` and the WGSL implement them and as vitrea's own captures
show them. Prove your reader on vitrea's captures first, where the kernel is known.

Then design the native capture that would identify the receded body's argument and kernel. The
backdrops must vary group mean and spatial frequency independently, at several pitches. Include
uniform inputs above encoded 150, since E3's F is identified only on 40–150. Cover both schemes,
both poses and both scales, and state what is held out: structured backdrops must be in the
holdout this time. Size it: cells and repeats, and hours at the Mac, estimated from W39's recorded
sitting (6,360 captures in about 17 hours). Name what it identifies that memo A cannot, and what it
still cannot identify.
