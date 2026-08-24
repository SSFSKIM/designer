/**
 * Pass-by-pass timing, for the benchmark §Performance envelope pins the ~2 ms
 * hypothesis to.
 *
 * The spec asks for the budget to be "measured per pass (backdrop import, blur,
 * analysis, body, highlight, composite) alongside browser end-to-end frame time",
 * which needs GPU-side timestamps: wall-clock around `submit()` measures the
 * queue, not the work. WebGPU's only timestamp mechanism is `timestampWrites` on
 * a pass descriptor — `encoder.writeTimestamp` was removed from the spec — so the
 * timeline hands out begin/end query indices by label and each pass spreads them
 * into its descriptor.
 *
 * Where `timestamp-query` is unavailable the timeline is simply absent and the
 * benchmark falls back to wall-clock totals, reported as such. A number labelled
 * as a GPU pass time that was actually a CPU submit time would be worse than no
 * number, and §Risks already names timestamp-query availability as an engine
 * variance to record rather than to assume.
 *
 * One caveat worth stating because it changes how the results read: Chrome
 * quantises timestamp results to 100 µs by default, so a single short pass reads
 * as 0. The benchmark works around it the way S2's harness did — by launching with
 * `--disable-dawn-features=timestamp_quantization`, and by measuring many
 * repetitions when it cannot.
 */

export interface PassTimeline {
  /** Query indices for a render pass, or undefined when timing is off. */
  renderSlot(label: string): GPURenderPassTimestampWrites | undefined;
  computeSlot(label: string): GPUComputePassTimestampWrites | undefined;
}

export interface TimingCollector extends PassTimeline {
  readonly capacity: number;
  readonly used: number;
  /** Queue the resolve + copy. Call once, after the last pass of the frame. */
  resolve(encoder: GPUCommandEncoder): void;
  /** Read the resolved timings. Labels map to elapsed nanoseconds. */
  read(): Promise<ReadonlyMap<string, number>>;
  /**
   * Slots whose resolved pair was not a positive duration, since the collector
   * was created. A non-zero count means some number reported here is missing a
   * pass, and saying so is better than quietly averaging it in.
   */
  readonly anomalies: number;
  reset(): void;
  destroy(): void;
}

export function supportsTimestamps(device: GPUDevice): boolean {
  return device.features.has("timestamp-query");
}

export function createTimingCollector(device: GPUDevice, capacity = 64): TimingCollector {
  const querySet = device.createQuerySet({
    label: "vitrea:timing",
    type: "timestamp",
    count: capacity * 2,
  });
  const byteLength = capacity * 2 * 8;
  const resolveBuffer = device.createBuffer({
    label: "vitrea:timing:resolve",
    size: byteLength,
    usage: GPUBufferUsage.QUERY_RESOLVE | GPUBufferUsage.COPY_SRC,
  });
  const staging = device.createBuffer({
    label: "vitrea:timing:staging",
    size: byteLength,
    usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST,
  });

  let used = 0;
  let anomalies = 0;
  const labels: string[] = [];

  const take = (label: string): { begin: number; end: number } | undefined => {
    if (used >= capacity) return undefined;
    const index = used;
    used += 1;
    labels[index] = label;
    return { begin: index * 2, end: index * 2 + 1 };
  };

  return {
    capacity,
    get used() {
      return used;
    },

    get anomalies() {
      return anomalies;
    },

    renderSlot(label) {
      const slot = take(label);
      if (slot === undefined) return undefined;
      return {
        querySet,
        beginningOfPassWriteIndex: slot.begin,
        endOfPassWriteIndex: slot.end,
      };
    },

    computeSlot(label) {
      const slot = take(label);
      if (slot === undefined) return undefined;
      return {
        querySet,
        beginningOfPassWriteIndex: slot.begin,
        endOfPassWriteIndex: slot.end,
      };
    },

    resolve(encoder) {
      if (used === 0) return;
      encoder.resolveQuerySet(querySet, 0, used * 2, resolveBuffer, 0);
      encoder.copyBufferToBuffer(resolveBuffer, 0, staging, 0, used * 2 * 8);
    },

    async read() {
      const out = new Map<string, number>();
      if (used === 0) return out;
      await staging.mapAsync(GPUMapMode.READ, 0, used * 2 * 8);
      const view = new BigInt64Array(staging.getMappedRange(0, used * 2 * 8).slice(0));
      staging.unmap();
      for (let i = 0; i < used; i += 1) {
        const begin = view[i * 2] ?? 0n;
        const end = view[i * 2 + 1] ?? 0n;
        const label = labels[i] ?? `pass-${i}`;
        const elapsed = Number(end - begin);
        // Zero IS a legitimate duration — a clear-only pass with no draw really
        // does take no measurable time. What is not legitimate is a *negative*
        // one, or a pair where both endpoints are zero: WebGPU leaves a slot
        // unspecified when its pass did not run, and averaging that in would
        // corrupt every number in the report. Those are dropped and counted.
        if (!Number.isFinite(elapsed) || elapsed < 0 || (begin === 0n && end === 0n)) {
          anomalies += 1;
          continue;
        }
        // Several passes share a label (one per group, one per pyramid level), and
        // the interesting number is the total the budget is spent on, so labels
        // accumulate rather than overwrite.
        out.set(label, (out.get(label) ?? 0) + elapsed);
      }
      return out;
    },

    reset() {
      used = 0;
      labels.length = 0;
    },

    destroy() {
      querySet.destroy();
      resolveBuffer.destroy();
      staging.destroy();
    },
  };
}

/** Pass labels, so the benchmark's report and the passes agree on the names. */
export const PASS_LABEL = {
  import: "backdrop-import",
  chain: "blur-chain",
  bodyBlur: "body-blur",
  analysis: "analysis",
  field: "group-field",
  optics: "optics",
  highlight: "highlight",
} as const;
