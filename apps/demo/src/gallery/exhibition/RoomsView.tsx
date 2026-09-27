/**
 * The rooms: the window's second view, the exhibition as a whole.
 *
 * The list of rooms is a collection read in place, so it lives in the window as content rather
 * than on a platter. Rows are plain buttons; the current room is marked by a darker fill, a
 * border that survives forced colours, heavier type and `aria-current`, never by colour alone.
 * The viewing room's one setting, Reduce Transparency, lives here because the engine may not be
 * able to report it, and the page then honours it only by offering it.
 */

import type { ReactNode } from "react";

import { EXHIBITION, WORKS, type Work } from "./works";

export interface RoomsViewProps {
  readonly current: Work;
  readonly onChoose: (work: Work) => void;
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (value: boolean) => void;
}

export function RoomsView(props: RoomsViewProps): ReactNode {
  const { current, onChoose, reducedTransparency, onReducedTransparency } = props;
  return (
    <div className="exh-rooms">
      <header className="exh-head">
        <div className="exh-kicker">
          <h1 className="exh-exhibition">{EXHIBITION.title}</h1>
          <p className="exh-room">{WORKS.length} rooms</p>
        </div>
        <p className="exh-weather">{EXHIBITION.subtitle}</p>
      </header>
      <div className="exh-essay">
        {EXHIBITION.introduction.map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </div>

      <h2 className="exh-section-title">Rooms</h2>
      <ol className="exh-room-list">
        {WORKS.map((work, index) => {
          const isCurrent = work.id === current.id;
          return (
            <li key={work.id}>
              <button
                type="button"
                className="exh-room-row"
                aria-current={isCurrent ? "true" : undefined}
                onClick={() => onChoose(work)}
              >
                <img
                  className="exh-room-row__thumb"
                  src={work.image}
                  alt=""
                  width={work.imageSize[0]}
                  height={work.imageSize[1]}
                />
                <span className="exh-room-row__text">
                  <span className="exh-room-row__weather">
                    {String(index + 1).padStart(2, "0")} · {work.weather}
                    {isCurrent ? (
                      <span className="exh-room-row__here"> · you are here</span>
                    ) : null}
                  </span>
                  <span className="exh-room-row__title">{work.title}</span>
                  <span className="exh-room-row__maker">
                    {work.artist}, {work.date}
                  </span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      <section className="exh-data exh-settings" aria-labelledby="exh-settings-title">
        <h2 className="exh-section-title" id="exh-settings-title">
          Viewing
        </h2>
        <div className="exh-setting">
          <span className="exh-setting__text">
            <span className="exh-setting__name" id="exh-rt-label">
              Reduce transparency
            </span>
            <span className="exh-setting__note" id="exh-rt-note">
              Frosts the label and the controls so the painting shows through less.
            </span>
          </span>
          <button
            type="button"
            role="switch"
            className="exh-switch"
            aria-checked={reducedTransparency}
            aria-labelledby="exh-rt-label"
            aria-describedby="exh-rt-note"
            onClick={() => onReducedTransparency(!reducedTransparency)}
          >
            <span className="exh-switch__knob" aria-hidden="true" />
          </button>
        </div>
      </section>

      <h2 className="exh-section-title">Photographs</h2>
      <ul className="exh-credits">
        {WORKS.map((work) => (
          <li key={work.id}>
            {work.artist}, <cite>{work.title}</cite>: {work.collection}, open access, public
            domain.
          </li>
        ))}
      </ul>
    </div>
  );
}
