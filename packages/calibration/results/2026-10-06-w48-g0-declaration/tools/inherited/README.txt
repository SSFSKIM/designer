W48 G0 (b): W47's tool tests under W48's bindings (charter clause 2). Each transcript here is one W47 test
module run UNCHANGED by `tools/run_inherited.py <path under W47's root>` (W48's bindings installed as
`bindings` by `inherit.py`; any write into W47's directory refused by an audit hook):

  cuts__test_rule.txt           cuts/test_rule.py            W45's 19 synthetic cases of the landing rule
  cuts__test_cuts_refusals.txt  cuts/test_cuts_refusals.py   the cuts' refusals (W44-W47's places refused)
  referees__test_referees.txt   referees/test_referees.py    X69: w46-referees-1 by hash, membership, disjointness
  sheets__test_sheets.txt       sheets/test_sheets.py        the eye sheets' populations per phase
  stage__test_x60.txt           stage/test_x60.py            X60 by render and by evidence, red cases

W47 test modules NOT run as such, because some of their cases assert a W47 binding, a W47 count or write
beside themselves into W47's directory. Each is loaded by path inside a W48 test module of the same name
(`tools/inherited_suite.py`), which runs every OTHER case of it unchanged and replaces the named ones:

  test_bindings.py              -> W48 test_bindings.py (a port: the charter pin, the refusal naming four
                                   waves; adds W47's places, part hashes and charter, INHERITED, inherit.py)
  fit/test_fit.py               -> W48 fit/test_fit.py: replaces Part2.test_other_waves_part_hashes_refuse
                                   (W47's hashes and the four-wave message), Part2.test_stage_2_admits_the_
                                   receded_start_a_stage_1_point_leaves and CrossedFactorial.test_the_tap_is_
                                   crossed_into_the_span_law (W48's stage 1 has no second tap; ladder (ii) met
                                   no rung), CrossedFactorial.test_points_and_renders_per_scale (counted in full
                                   by fit/test_stage_sizes.py)
  fit/test_build_candidate.py   -> W48 fit/test_build_candidate.py: replaces Admits.test_every_x64_key_together_
                                   is_digest_neutral (the candidate's name carries w48); drives W48's builder copy
  seal/test_seal.py             -> W48 seal/test_seal.py: drives W48's seal copy (module SEAL re-pointed); its four
                                   digest pins run on a subclass whose expected recordedBy is "W48 G1"
  stage/test_stage.py           -> W48 stage/test_stage.py: stage.py through inherit.tool (SEALED_BY re-bound,
                                   inherit.REBIND); replaces Stage.test_the_stages_are_w47s_and_dark and
                                   Stage.test_g1_refuses_the_shipped_documents_and_unhashed_parts; adds the
                                   shipped stage re-proven without a render
  level/test_level.py           -> W48 level/test_level.py: module SCRATCH re-pointed out of W47's directory
                                   (W47's cases write `.test-scratch` beside themselves); every case W47's
  ladders/test_ladder.py        -> class X70 only, in W48 referees/test_x69_x70.py (W47's protocol bound while it
                                   imports; W48's protocol has W48's shape, not a runner's)
  ladders/test_read.py          not run: it waits on W47's level control render (WAITING skip); W48 renders none

Known label residue (cosmetic, decides nothing): inherited tools still print "w47-stage" / "w47-fit" as census
labels (stage/stage.py, fit/fit.py) and write "W47 G1: ..." in the `what` strings of fit/joint.py, finding.py and
recover.py records. W48 G1's records from those tools will carry them; they name the tool's origin, not the wave.
