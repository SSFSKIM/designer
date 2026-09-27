/**
 * Stations: the moorings reporting into the field, as a table, with one action
 * per row that carries the probe to the mooring. The table is content and takes
 * no glass; the cross-link is what stops the sheet and the field being two
 * unrelated widgets sharing a screen.
 */

import type { ReactNode } from "react";

import { formatBearing, formatLat, formatLon, STATIONS, stationToField, type Station } from "../data";
import { Sheet } from "./Sheet";

export interface StationsSheetProps {
  readonly onClose: () => void;
  readonly onLocate: (station: Station, u: number, v: number) => void;
}

export function StationsSheet(props: StationsSheetProps): ReactNode {
  const latest = STATIONS.reduce((best, station) => (station.updated > best ? station.updated : best), "");
  return (
    <Sheet id="stations" title="Stations" onClose={props.onClose}>
      <p className="sheet__lead">
        Six moorings report surface velocity into the field every ten minutes. The reading
        beside each is the mooring's own; the probe reads the assimilated field around it.
      </p>
      <div className="table-scroll">
        <table className="table">
          <caption className="table__caption">
            {STATIONS.length} moorings reporting, latest at {latest} UTC
          </caption>
          <thead>
            <tr>
              <th scope="col">Station</th>
              <th scope="col">Position</th>
              <th scope="col" className="table__num">
                Speed
              </th>
              <th scope="col" className="table__num">
                Bearing
              </th>
              <th scope="col">
                <span className="visually-hidden">Locate</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {STATIONS.map((station) => {
              const { u, v } = stationToField(station);
              return (
                <tr key={station.id}>
                  <th scope="row">
                    <span className="table__id">{station.id}</span>
                    <span className="table__name">{station.name}</span>
                  </th>
                  <td className="table__data">
                    {formatLat(station.lat)} {formatLon(station.lon)}
                  </td>
                  <td className="table__data table__num">{station.speed.toFixed(2)} m/s</td>
                  <td className="table__data table__num">{formatBearing(station.bearing)}</td>
                  <td className="table__action">
                    <button
                      type="button"
                      className="link-button"
                      onClick={() => props.onLocate(station, u, v)}
                    >
                      Locate
                      <span className="visually-hidden"> {station.name}</span>
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Sheet>
  );
}
