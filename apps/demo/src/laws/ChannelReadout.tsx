/**
 * What one surface's host actually carries, in the runtime's own properties.
 *
 * The CSS tier writes `--vitrea-tint`, `--vitrea-occlusion`, `--vitrea-blur`,
 * `--vitrea-border-color` and `--vitrea-foreground` on the host every frame; the
 * WebGPU tier publishes only the foreground pair, because its body is the
 * canvas's and not the host's. Both facts are worth seeing, so the rows are read
 * off the host on the runtime's own tick and a property the tier does not write
 * shows as absent rather than being filled in from the other tier's answer.
 */

import { useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useState, type ReactNode } from "react";

const CHANNELS = [
  ["--vitrea-tint", "Tint"],
  ["--vitrea-occlusion", "Occlusion"],
  ["--vitrea-blur", "Blur"],
  ["--vitrea-border-color", "Border"],
  ["--vitrea-foreground", "Foreground"],
] as const;

type Channels = Readonly<Record<(typeof CHANNELS)[number][0], string>>;

const EMPTY: Channels = {
  "--vitrea-tint": "",
  "--vitrea-occlusion": "",
  "--vitrea-blur": "",
  "--vitrea-border-color": "",
  "--vitrea-foreground": "",
};

export function ChannelReadout(props: { readonly label: string; readonly testId: string }): ReactNode {
  const ticker = useGlassTicker();
  const [values, setValues] = useState<Channels>(EMPTY);

  useEffect(
    () =>
      ticker.subscribe(() => {
        const host = document.querySelector<HTMLElement>(`[data-testid="${props.testId}"]`);
        if (host === null) return;
        const next = {
          "--vitrea-tint": host.style.getPropertyValue("--vitrea-tint"),
          "--vitrea-occlusion": host.style.getPropertyValue("--vitrea-occlusion"),
          "--vitrea-blur": host.style.getPropertyValue("--vitrea-blur"),
          "--vitrea-border-color": host.style.getPropertyValue("--vitrea-border-color"),
          "--vitrea-foreground": host.style.getPropertyValue("--vitrea-foreground"),
        } satisfies Channels;
        setValues((previous) =>
          CHANNELS.every(([property]) => previous[property] === next[property]) ? previous : next,
        );
      }),
    [props.testId, ticker],
  );

  return (
    <dl className="readout" data-testid={`${props.testId}-channels`}>
      <div className="readout__head">
        <dt>Surface</dt>
        <dd>{props.label}</dd>
      </div>
      {CHANNELS.map(([property, label]) => {
        const value = values[property].trim();
        return (
          <div className="readout__row" key={property}>
            <dt>{label}</dt>
            <dd data-channel={property} data-empty={value === "" ? "" : undefined}>
              {value === "" ? "not published on this tier" : value}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
