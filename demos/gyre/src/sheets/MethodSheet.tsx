/**
 * Method: how the field is made, in three short paragraphs and one readout.
 */

import type { ReactNode } from "react";

import { METHOD } from "../data";
import { Readout, Sheet } from "./Sheet";

export function MethodSheet(props: { readonly onClose: () => void }): ReactNode {
  return (
    <Sheet id="method" title="Method" onClose={props.onClose}>
      <p className="sheet__display">One field, three sources, ten minutes old.</p>
      <p>
        Gyre assimilates {METHOD.drifters} drifting buoys, {METHOD.altimetry} satellite altimetry
        tracks and {METHOD.radar} coastal radar sites into a single surface-velocity field on a{" "}
        {METHOD.grid} grid. Each source is weighted by its own error estimate, so a buoy inside a
        ring does not drag the whole ring with it.
      </p>
      <p>
        The field is re-solved every {METHOD.cadence} and carried {METHOD.horizon} ahead with a
        reduced-gravity model. Observation latency, from a buoy fix to its effect on this screen,
        is {METHOD.latency} at the median.
      </p>
      <p>
        The probe reads the assimilated field, not the nearest instrument. Where the two disagree
        by more than the field's own uncertainty, the station table says so.
      </p>
      <Readout
        rows={[
          { label: "Grid", value: METHOD.grid },
          { label: "Horizon", value: METHOD.horizon },
          { label: "Cadence", value: METHOD.cadence },
          { label: "Latency, median", value: METHOD.latency },
          { label: "Drifters", value: METHOD.drifters },
          { label: "Altimetry tracks", value: METHOD.altimetry },
          { label: "Radar sites", value: METHOD.radar },
        ]}
      />
    </Sheet>
  );
}
