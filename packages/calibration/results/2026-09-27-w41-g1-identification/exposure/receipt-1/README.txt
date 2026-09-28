W41 receipt-1 — the one exposure of the W39 holdout (c9a §5.192.25; charter X26)
==============================================================================

What ran (2026-09-28/29 UTC)
- 23:22:53Z state check, then the just-in-time browser check
  (final-configuration/browser-jit-1.json: executable, framework, Info.plist hashes,
  version 151.0.7922.34 and all 655 recursive chromium-1234 entries MATCH; nothing launched)
  and the external preflight (final-configuration/preflight-20260928T232300Z.json,
  SUCCESS in 181 s, runner.verify against manifest-1 77f93ba2…).
- attempt-1, 23:26:09Z: X6 pre-begin gate REFUSED at 23:30:31Z on foreignProcessCountZero,
  receipt NOT begun (attempt-1/x6-prebegin.json). The one foreign process was the
  exposure owner's own progress watcher, whose zsh wrapper command line carried the
  text "Google Chrome for Testing" that the FOREIGN regex matches. Idle, RT, IC and
  NSGlassTintAmount passed. Under the coordinator's ruling (a pre-begin refusal is not a
  begun attempt; rerun into a new directory, at most three), a watcher whose script and
  command line carry no FOREIGN token replaced it (drivers/monitor-attempt.sh.txt), a
  fresh X6 reading passed at 23:31:08Z, and attempt-2 started.
- attempt-2, 23:31:16Z: pre-begin PASS 23:35:34Z; Receipt begin 23:35:33.849Z (log);
  four profile gates PASS (cumulative X6 wait 133.6 / 268.2 / 403.3 / 538.0 s of 3,600,
  in-guard manifest re-verification included); 4 × 16 captures, each byte-identical over
  two loads, 0 CSS fallbacks, 0 carry problems; browser work ended about 23:45:46Z;
  every recapture equal to its frozen PNG and projection; scored; Receipt complete
  23:53:22.306Z; exit 0. One begun attempt, no retry.

Files
- ../../../2026-09-26-w39-g0-colour-edge-bed/wave-identification-receipt.jsonl: the
  receipt log, committed at its fixed path as the runner wrote it (begin, complete).
- wave-identification-receipt-scores.json.gz: gzip (mtime 0) of the runner's
  authoritative receipt-adjacent scores file, which stays untracked at its W39 path
  (111,640,287 bytes; storage.json has both hashes and the round-trip check).
- result.json.gz: gzip of attempt-2/result.json (222,690,690 bytes, kept outside git at
  /Users/new/vitrea-w41/g1-exposure/attempt-2/). No committed file exceeds 50 MB.
- attempt-1/, attempt-2/: the runner's output trees (x6 records, the 64 captures with
  their cell/report sidecars), byte-identical copies; result.json is the gzip above.
- run-production-{1,2}.{log,times}: stdout/stderr and start/exit times.
- drivers/: the exact stdin driver texts and the watcher, stored as text.
- summarize.py.txt -> summary.json (closure computation) and storage.json.

Result (summary.json)
body-e3, light-inactive E3, uniform-backdrop claim: numerical 18/18 claimed held-out
cells measured and passing (0 censored; worst 0.666 codes, held-y0.08-h150 G); rendered
16/16 measured and passing (0 censored; worst 1.0 code at the bound, G 170 against 171 on
held-y0.08-h150 and -h270 at both scales); per-bin veto passes on all 64 rendered cells
(29,584 bins pass, 5,040 UNMEASURED below four pixels, max worsening 0.0). The 48
unclaimed rendered cells are byte-identical to the identity baseline. Measured coverage:
all claimed held-out cells; 18/72 and 16/64 of the whole held-out set, the rest being
the three unclaimed endpoints (identity diagnostics, not claims).
