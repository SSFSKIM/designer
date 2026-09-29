# W42 grounding memo A — the argument E3 is evaluated at

Read `/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-common.md` first. Memo path:
`/Users/new/.claude/jobs/17c7ce02/tmp/w42-grounding-argument.txt`; scratch
`~/vitrea-w42/grounding/argument/`.

Question: hold E3's identified F and g fixed. What argument, for luma L and for chroma v,
reproduces Apple's light-inactive body on the canonical structured calibration/validation cells
(checkerboard, hc-text, impulse, photo, gradients, both scales)? The argument must also leave the
uniform closure intact. Candidates to size, at least:
- per pixel at vitrea's current blur, the known failure, as a control;
- the group mean in encoded space;
- the group mean in linear light;
- an encoded-space blur at width s;
- a linear-space blur at width s;
- a blend m·local + (1 − m)·group.
Luma and chroma may take different arguments; test that. For each candidate report:
- the body residual per cell and stratum against native;
- the L1/M2/M1 values its predictions would give on those cells, next to the adopted bounds;
- whether uniform backdrops are unchanged by construction.
Explain hc-text's miss under the encoded-mean pointer. Say which candidates the existing cells
cannot tell apart, and which cell or capture would separate them.
Also check whether the same question applies to the shipped body in the active pose and the dark
scheme, where E3 does not apply: does vitrea's shipped body keep backdrop structure there that
Apple's smooths away? Size it on the same cells.
