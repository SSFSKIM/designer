The landing's first chain run, kept whole (claims §5.207 §10). It ran at bed6f4a4f and HALTED at
`units` (exit 1): matrix-store.test.ts still pinned W43's glass 0.25 generations
({ 6d18c059eb42: 656, d0219cd684bf: 468 }), and W45 G1 had published ebc3d9105a4a and retired
c05. Every step before it was green (freeze 1,818, X41 911, check-capture-tree exit 0, build,
the ten digests, lint, root eslint). The case was fixed at the next commit, and the whole chain
re-ran from its first step at the new head (../chain-*.txt).
