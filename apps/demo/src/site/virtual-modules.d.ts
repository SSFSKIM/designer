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
