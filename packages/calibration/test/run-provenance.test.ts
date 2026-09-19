import { describe, expect, it } from "vitest";

import {
  osSeriesOf,
  parseAttestRead,
  runProvenanceProblems,
  type RunProvenance,
} from "../src/run-provenance";

/** An `attest.read` as `run-sitting-27.sh` writes it, reduced to the fields the rule reads. */
const ATTEST_27 = [
  "phase=open",
  "pass=standard-active-2x",
  "readAt=2026-09-18T12:00:00Z",
  "os=27.0 26A428",
  "osProductVersion=27.0",
  "osBuild=26A428",
  "glassTintAmount=0.5",
  "reduceTransparency=0",
  "increaseContrast=0",
  "a11yMode=standard",
  "showBorders=0",
  "bundleRecordedSdkNote=ld writes sdk == minos on this build path, so this is a record",
  "passSpecSha256=afcc59c5b0191b7ac6d24bdf99daff6e8bcc8a3460c38ef9a7bd6090c14287af",
].join("\n");

const run27 = (overrides: Partial<RunProvenance> = {}): RunProvenance => ({
  label: "A",
  hardware: { osVersion: "Version 27.0 (Build 26A428)", osBuild: "26A428" },
  attested: parseAttestRead(ATTEST_27),
  profileKeys: ["apple-macos-27.0-2x-light-standard-glass0.5"],
  ...overrides,
});

/** A 26.5 run: the bed that predates the attestation file entirely. */
const run265 = (overrides: Partial<RunProvenance> = {}): RunProvenance => ({
  label: "A",
  hardware: { osVersion: "Version 26.5.2 (Build 25F84)", osBuild: "25F84" },
  attested: null,
  profileKeys: ["apple-macos-26.5-2x-light-standard"],
  ...overrides,
});

describe("parsing what a run says about its machine", () => {
  it("splits an attest.read on its first '=' so a value may contain one", () => {
    const fields = parseAttestRead(ATTEST_27);
    expect(fields["osBuild"]).toBe("26A428");
    expect(fields["glassTintAmount"]).toBe("0.5");
    expect(fields["os"]).toBe("27.0 26A428");
    expect(fields["bundleRecordedSdkNote"]).toContain("sdk == minos");
  });

  it("parses the OS series out of both spellings of the same system", () => {
    // The manifest's field is `ProcessInfo.operatingSystemVersionString`; a
    // profile key's token is the bare series. A prefix match between the two is
    // either always false or accidentally true, so the rule parses.
    expect(osSeriesOf("Version 27.0 (Build 26A428)")).toBe("27.0");
    expect(osSeriesOf("Version 26.5.2 (Build 25F84)")).toBe("26.5");
    expect(osSeriesOf("27.0")).toBe("27.0");
    expect(osSeriesOf("macOS")).toBeNull();
  });
});

describe("the OS-and-build refusal (W29 Design; the check the harness never had)", () => {
  it("passes a 27 run under 27 keys and a 26.5 run under 26.5 keys", () => {
    expect(runProvenanceProblems([run27(), run27({ label: "B" })])).toEqual([]);
    expect(runProvenanceProblems([run265(), run265({ label: "B" })])).toEqual([]);
  });

  it("refuses a 27 run filing into a 26.5 key", () => {
    // The exact confusion W29 Grounding names: nothing in the harness would stop
    // it, and a 26.5 directory holding 27 pixels is the one mistake contract X1
    // cannot be checked against afterwards — the bytes carry no OS.
    const problems = runProvenanceProblems([
      run27({ profileKeys: ["apple-macos-26.5-2x-light-standard"] }),
    ]);
    expect(problems).toHaveLength(1);
    expect(problems[0]).toContain("records macOS 27.0");
    expect(problems[0]).toContain("claims 26.5");
  });

  it("refuses a 26.5 run filing into a 27 key", () => {
    const problems = runProvenanceProblems([
      run265({ profileKeys: ["apple-macos-27.0-2x-light-standard-glass0.5"] }),
    ]);
    expect(problems.some((p) => p.includes("records macOS 26.5") && p.includes("claims 27.0")))
      .toBe(true);
  });

  it("refuses a manifest whose osVersion states no version at all", () => {
    const problems = runProvenanceProblems([run27({ hardware: { osBuild: "26A428" } })]);
    expect(problems[0]).toContain("states no major.minor version");
  });

  it("refuses two runs taken on different builds of the same OS series", () => {
    // Each run agrees with its own key; only the pair is wrong. A point update is
    // a different material, so a plurality across one is a vote rather than a
    // majority.
    const problems = runProvenanceProblems([
      run27(),
      run27({
        label: "B",
        hardware: { osVersion: "Version 27.1 (Build 26B100)", osBuild: "26B100" },
        attested: parseAttestRead(
          ATTEST_27.replace("osProductVersion=27.0", "osProductVersion=27.1")
            .replace("osBuild=26A428", "osBuild=26B100"),
        ),
      }),
    ]);
    expect(problems.some((p) => p.includes("2 different OS builds"))).toBe(true);
  });

  it("refuses a key the grammar cannot parse rather than skipping it", () => {
    const problems = runProvenanceProblems([run27({ profileKeys: ["apple-macos-27-2x-light"] })]);
    expect(problems[0]).toContain("is not a profile key this grammar can parse");
  });
});

describe("the slider refusal (contract X6: the key names every axis that moved a pixel)", () => {
  it("refuses a 27 key when the run carries no attestation at all", () => {
    // No manifest field records `NSGlassTintAmount` — the harness does not read
    // it — so a run with no attest.read cannot say where the slider stood, and
    // the axis moves every cell of every arm (claims §5.149 §4).
    const problems = runProvenanceProblems([run27({ attested: null })]);
    expect(problems).toHaveLength(1);
    expect(problems[0]).toContain("carries no attest.read");
  });

  it("refuses an attested position that is not the one the key states", () => {
    // 0.5459057 is the machine's as-found value, which Decision Log 3 (a) records
    // as a reading and not a bed. It is 0.046 off the ruled centre and that is
    // above the noise bar on all ten probe cells, so it is a refusal rather than
    // a rounding.
    const problems = runProvenanceProblems([
      run27({
        attested: parseAttestRead(
          ATTEST_27.replace("glassTintAmount=0.5", "glassTintAmount=0.5459057"),
        ),
      }),
    ]);
    expect(problems).toHaveLength(1);
    expect(problems[0]).toContain("states appearance-slider position 0.5 and the run attested 0.5459057");
  });

  it("accepts a differently spelled but equal position, and refuses an unreadable one", () => {
    // The token parses as a number, so `0.50` and `0.5` name the same position;
    // `absent` — what the run script records when the key is missing — does not
    // name one at all, and a value nothing could read is not an attestation.
    expect(
      runProvenanceProblems([
        run27({
          attested: parseAttestRead(
            ATTEST_27.replace("glassTintAmount=0.5", "glassTintAmount=0.50"),
          ),
        }),
      ]),
    ).toEqual([]);
    const problems = runProvenanceProblems([
      run27({
        attested: parseAttestRead(
          ATTEST_27.replace("glassTintAmount=0.5", "glassTintAmount=absent"),
        ),
      }),
    ]);
    expect(problems[0]).toContain("not an attestation");
  });

  it("does not ask a 26.5 key for a slider that did not exist", () => {
    // The axis is absent before 27 rather than unspecified: `NSGlassTintAmount`
    // is in no 26.x preference store. Requiring an attestation of it from the
    // frozen bed would make X1's own evidence unpublishable.
    expect(runProvenanceProblems([run265()])).toEqual([]);
  });

  it("refuses when the manifest and the attestation disagree about the build", () => {
    // Two independent reads of one machine — the harness's, through Foundation,
    // and the run script's, through `sw_vers`. A bed is stronger for having both
    // agree; a disagreement leaves it unable to say which build drew its pixels.
    const problems = runProvenanceProblems([
      run27({
        attested: parseAttestRead(ATTEST_27.replace("osBuild=26A428", "osBuild=26B100")),
      }),
    ]);
    expect(problems.some((p) => p.includes("Two reads of one machine that disagree"))).toBe(true);
  });

  it("refuses runs of one pass that read different scene declarations", () => {
    // `sceneSpecVersion` would catch a version bump but not an edit inside one,
    // and the declaration decides which cells exist and where their geometry puts
    // them. Two runs taken across an edit are two beds.
    const problems = runProvenanceProblems([
      run27(),
      run27({
        label: "B",
        attested: parseAttestRead(ATTEST_27.replace(/passSpecSha256=\w+/, "passSpecSha256=deadbeef")),
      }),
    ]);
    expect(problems.some((p) => p.includes("2 different scene declarations"))).toBe(true);
  });

  it("does not ask a bed captured before the field existed for a declaration digest", () => {
    expect(runProvenanceProblems([run265(), run265({ label: "B" })])).toEqual([]);
  });

  it("reports every disagreement at once rather than the first", () => {
    // A sitting is hours of machine time; finding its second problem after fixing
    // its first costs another sitting.
    const problems = runProvenanceProblems([
      run27({
        profileKeys: [
          "apple-macos-26.5-2x-light-standard",
          "apple-macos-27.0-2x-dark-standard-glass0.9",
        ],
      }),
    ]);
    expect(problems.length).toBeGreaterThanOrEqual(2);
  });
});

describe("the accessibility refusal (W29 Decision Log 4 (b); claims §5.152)", () => {
  /** An increased-contrast run, in one of the two states macOS 27 can be in. */
  const contrast = (ic: string, rt: string, key: string): RunProvenance =>
    run27({
      attested: parseAttestRead(
        ATTEST_27.replace("increaseContrast=0", `increaseContrast=${ic}`)
          .replace("reduceTransparency=0", `reduceTransparency=${rt}`)
          .replace("a11yMode=standard", "a11yMode=increased-contrast"),
      ),
      profileKeys: [key],
    });

  const DECOUPLED = "apple-macos-27.0-1x-light-increased-contrast-glass0.5";
  const COUPLED = "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5";

  it("publishes each state under its own key", () => {
    expect(runProvenanceProblems([contrast("1", "0", DECOUPLED)])).toEqual([]);
    expect(runProvenanceProblems([contrast("1", "1", COUPLED)])).toEqual([]);
  });

  it("refuses the coupled state filed under the decoupled key, and the reverse", () => {
    // This is the confound §5.151 §9 records, caught before a pixel is opened.
    // The manifest cannot catch it: its `a11yMode` is
    // `SystemAccessibility.current`, which reads `increased-contrast` in BOTH
    // states, so the two toggles are separable only in the attestation.
    const filedDecoupled = runProvenanceProblems([contrast("1", "1", DECOUPLED)]);
    expect(filedDecoupled).toHaveLength(1);
    expect(filedDecoupled[0]).toContain("names increased contrast alone");
    expect(filedDecoupled[0]).toContain("belongs under the increased-contrast-coupled key");
    const filedCoupled = runProvenanceProblems([contrast("1", "0", COUPLED)]);
    expect(filedCoupled).toHaveLength(1);
    expect(filedCoupled[0]).toContain("claims the COUPLED state");
  });

  it("refuses either contrast key when the machine attested no contrast at all", () => {
    for (const key of [DECOUPLED, COUPLED]) {
      const problems = runProvenanceProblems([contrast("0", "1", key)]);
      expect(problems.some((p) => p.includes("the run attested increaseContrast=0")), key)
        .toBe(true);
    }
  });

  it("refuses a coupled key on a run that carries no attestation", () => {
    // The coupled token claims a state no manifest field carries, so a run that
    // cannot say both toggles stood on cannot be published under it (X2).
    const problems = runProvenanceProblems([run27({ attested: null, profileKeys: [COUPLED] })]);
    expect(problems.some((p) => p.includes("cannot say both stood on"))).toBe(true);
  });

  it("asks nothing of the 26.5 bed, whose coupled capture wears the plain token", () => {
    // On macOS 26.5 contrast force-enabled transparency reduction and the
    // checkbox could not be uncleared, so the coupled state was the only
    // increased-contrast state and the bed of that name is it (§5.150 Part B §3).
    // It predates the attestation file, and a rule that demanded one would make
    // the frozen bed unpublishable by its own machinery.
    expect(
      runProvenanceProblems([
        run265({ profileKeys: ["apple-macos-26.5-1x-light-increased-contrast"] }),
      ]),
    ).toEqual([]);
  });
});
