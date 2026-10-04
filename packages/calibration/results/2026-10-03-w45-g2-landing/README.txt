W45 G2, the landing (claims §5.207; charter 2026-10-03-w45-span-selective-texture.md v1.4, G2 child and
Decision Log 8; branch w45-g2-landing off w45-g1-refit's head 8f836c80). What is here:

tree/     The capture tree's two acts. witness.py holds a tree to a generation file cell by cell (the row the
          compare launch wrote beside each capture equals the published row in full) and, with --copy, a copy to
          its source byte for byte. witness-g1-tree.json (G1's tree against ebc3d9105a4a),
          witness-c05-canonical-before.json (the canonical light 0.25 tree against 6d18c059eb42, before the
          move), witness-copy.json (3,280 files byte-identical), witness-canonical-after.json,
          witness-superseded-after.json; check-capture-tree before (exit 1, 656 superseded) and after (exit 0).
cuts/     landing.py regenerates the 0.25 cut from the published rows with W45's cuts (the referees spent at read
          7 counted as ordinary members) and compares it with G1's exposure cut (landing.json, EQUAL);
          cut-025-w45-landing.json/.txt is the cut the owner test pins; landing-run.txt the run's output.
t1/       derive.py (T1 on ebc3d9105a4a against c05 through both band fixtures, by W44 G1's t1.py and W45's
          rule.py): t1-derivation.json, missed-27-rows.ts.txt (the re-derived MISSED_27_ROWS T1 entries) and
          witness-iii.txt (part (iii): clause (b) on both forms against c05 with the list empty).
          witness-iii-owner.txt, owner-part-iv.txt, owner-part-v.txt: the owner test's runs at parts (iii),
          (iv) and (v).
demo/     reduction.ts: the virtual module the demo build embeds at the new union (reduction.txt).
sheets/   landing_sheets.py: W45 G0's sheets.py over the whole light bed from the trees the landing left;
          sent.txt records the zip sent to the MacBook.
close/    digests.ts (the ten shipped digests, digests.txt); chain.sh, the c9d chain at the head, with
          chain-status.txt, chain-invocations.txt and one chain-<step>.txt per step; close-checks.txt
          summarises them with exit codes.
