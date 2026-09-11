/**
 * The layer control: the one `GlassSegmentedControl`, bottom-right, in a
 * sampling group of its own over the field texture. A radiogroup by contract,
 * which is what a set of exclusive layers is.
 */

import { GlassGroup, GlassSegmentedControl } from "@vitreajs/vitrea-react";
import type { ReactNode } from "react";

import { FIELD_TEXTURE_ID } from "../field/Field";
import { LAYERS, type LayerId } from "../field/palettes";

export interface LayerControlProps {
  readonly value: LayerId;
  readonly onChange: (next: LayerId) => void;
}

const ITEMS = LAYERS.map((layer) => ({ value: layer.id, label: layer.label }));

export function LayerControl(props: LayerControlProps): ReactNode {
  return (
    <GlassGroup id="layers" backdrop={{ kind: "texture", id: FIELD_TEXTURE_ID }}>
      <GlassSegmentedControl<LayerId>
        aria-label="Field layer"
        className="layers"
        segmentClassName="segment"
        indicatorClassName="segment-indicator"
        items={ITEMS}
        value={props.value}
        onChange={props.onChange}
        thickness={8}
        radius={22}
      />
    </GlassGroup>
  );
}
