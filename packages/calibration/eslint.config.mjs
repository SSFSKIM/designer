import { node } from "../../eslint.config.mjs";

export default [
  /*
   * `results/` is committed EVIDENCE, not code that ships: the scripts, probe
   * pages and JSON a wave's findings were produced with, kept beside the numbers
   * so a reading can be reproduced. Several of them are browser-context by
   * necessity (a probe page's own module, a script evaluated inside a page), so
   * linting them against this package's Node-flavoured rules reports globals
   * rather than defects — which is the same reason, and the same wording, as the
   * root config's ignore of `spikes/`.
   */
  { ignores: ["results/**"] },
  ...node,
];
