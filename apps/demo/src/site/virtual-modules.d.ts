/**
 * The build-time modules this app resolves through a Vite plugin rather than from a
 * file. `../../shipped-documents.ts` is the plugin that produces this one.
 */
declare module "virtual:vitrea-shipped-documents" {
  /**
   * `packages/calibration/profiles/<file>` → twelve hex characters of SHA-256 over the
   * document's bytes, as the documents stand at the moment the bundle was built.
   */
  export const SHIPPED_DOCUMENT_HASHES: Readonly<Record<string, string>>;
}

/**
 * The calibration matrix, reduced to the rows this page can show and the fields it
 * prints. `../../matrix-reduction.ts` is the plugin that produces this one, and the
 * reason it exists is there: the current matrix spans a frozen file and indexed
 * generation files, while the page needs only a few hundred projected rows.
 */
declare module "virtual:vitrea-matrix-reduction" {
  interface Metric {
    readonly value: number;
    readonly units: string;
  }
  /** The projected cells, in the matrix's own order. */
  export const CELLS: readonly {
    readonly key: {
      readonly profileKey: string;
      readonly sceneId: string;
      readonly web: {
        readonly engine: string;
        readonly engineVersion: string;
        readonly renderer: string;
        readonly samplingBackend: string;
        readonly gpuAdapter: string;
        readonly capturePath: string;
      };
    };
    readonly tier: string;
    readonly fixtureSet: string;
    readonly capturedAt: string;
    readonly shape?: Readonly<Record<string, Metric>>;
    readonly perceptual?: Readonly<Record<string, Metric>>;
    readonly material?: Readonly<Record<string, Metric>>;
  }[];
  /** The current union's row count, before filtering to displayable cells. */
  export const MATRIX_CELL_COUNT: number;
}
