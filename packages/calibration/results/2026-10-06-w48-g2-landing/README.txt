W48 G2, the landing (claims §5.214; charter 2026-10-06-w48-dark-operators-fit.md, clause 10, the G2 child and
Decision Logs 9 and 10; branch w48-g2-landing off w48-g1-fit's head 7788e596d). What is here:

tree/     W45 G2's witness.py (copied) holds a tree to a generation file cell by cell and a copy to its source byte
          for byte: witness-g1-tree.json (G1's stage tree against b2d074d2df24), witness-d0219-canonical-before.json,
          witness-copy.json (2,340 files), witness-canonical-after.json, witness-superseded-after.json;
          check-capture-tree before (exit 1, 468 superseded) and after (exit 0).
cuts/     landing.py regenerates the dark 0.25 cut from the published rows with W47's cuts under W48's bindings
          (the dark referees spent at read 8 counted as ordinary members) and compares it with G1's exposure cut
          (landing.json, EQUAL); cut-025-dark-w48-landing.json/.txt is the cut the owner test pins.
t1/       bands.py (the b2d074d2df24 T-band fixture, equal to both cuts' bands), derive.py (T1 on b2d074d2df24
          against d0219cd684bf: t1-derivation.json, missed-27-rows.ts.txt, witness-iii.txt), the owner test's
          runs at parts (iii), (iv), (v), without the tree, and after the review closure.
demo/     reduction.ts and reduction.txt: the virtual module the demo build embeds at the new union.
sheets/   landing_sheets.py: W47's sheets tool over the whole dark bed from the trees the landing left; sent.txt.
close/    digests.ts / digests.txt (the ten shipped digests); chain.sh with chain-status.txt, chain-invocations.txt
          and one chain-<step>.txt per step (chain-run-1/ the first run, kept whole; chain-react-e2e.red-*.txt the
          three reds; react-firefox-probe/ the readings that put them in the tracker's intermittent class);
          declaration-witness.sh and its outputs; summarise.py writes close-checks.txt.
