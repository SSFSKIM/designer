/**
 * The label: the window's reading view of one work.
 *
 * Hierarchy is carried by type and order, not by the material, so the CSS tier, Reduce
 * Transparency and forced colours keep all of it: the room and its weather, the title and maker,
 * the whole work in an opaque frame, the essay, then the work's data on a darker separating fill.
 * The essay is rendered sentence by sentence from the audio guide's own split, so the sentence
 * being read can be underlined (a decoration, which survives forced colours where a fill would
 * not, and which is not light-on-light on a bright body).
 */

import { Fragment, type CSSProperties, type ReactNode } from "react";

import { visibleDetail } from "./painter";
import type { GuideStop } from "./guide";
import { EXHIBITION, WORKS, type Work } from "./works";

export interface LabelViewProps {
  readonly work: Work;
  readonly stop: GuideStop;
  /** The sentence the guide is reading, or undefined when it is silent. */
  readonly spoken: number | undefined;
  readonly viewport: { readonly width: number; readonly height: number };
}

export function LabelView({ work, stop, spoken, viewport }: LabelViewProps): ReactNode {
  const index = WORKS.indexOf(work);
  const detail = visibleDetail(work, viewport);
  const clamp = (value: number): number => Math.max(0, Math.min(1, value));
  const left = clamp(detail.x);
  const top = clamp(detail.y);
  const right = clamp(detail.x + detail.width);
  const bottom = clamp(detail.y + detail.height);
  const [iw, ih] = work.imageSize;

  return (
    <article className="exh-label" aria-labelledby="exh-work-title">
      <header className="exh-head">
        <div className="exh-kicker">
          <h1 className="exh-exhibition">{EXHIBITION.title}</h1>
          <p className="exh-room">
            Room {index + 1} of {WORKS.length}
          </p>
        </div>
        <p className="exh-weather">{work.weather}</p>
        <h2 className="exh-title" id="exh-work-title">
          {work.title}
        </h2>
        <p className="exh-maker">
          <span className="exh-artist">{work.artist}</span>
          <span className="exh-bio">
            {work.artistBio} · {work.date}
          </span>
        </p>
      </header>

      <figure className="exh-whole">
        <div
          className="exh-whole__frame"
          style={{ aspectRatio: `${iw} / ${ih}`, "--aspect": iw / ih } as CSSProperties}
        >
          <img className="exh-whole__image" src={work.image} alt="" width={iw} height={ih} />
          <span
            className="exh-whole__detail"
            aria-hidden="true"
            style={{
              left: `${left * 100}%`,
              top: `${top * 100}%`,
              width: `${(right - left) * 100}%`,
              height: `${(bottom - top) * 100}%`,
            }}
          />
        </div>
        <figcaption className="exh-caption">
          The whole work. The outline marks the part around you.
        </figcaption>
      </figure>

      <div className="exh-essay">
        {stop.paragraphs.map((indices, p) => (
          <p key={p}>
            {indices.map((i, n) => (
              <Fragment key={i}>
                <span className={spoken === i ? "exh-sentence is-spoken" : "exh-sentence"}>
                  {stop.sentences[i]}
                </span>
                {n < indices.length - 1 ? " " : null}
              </Fragment>
            ))}
          </p>
        ))}
      </div>

      <section className="exh-data" aria-label="About the work">
        <dl>
          <div>
            <dt>Weather</dt>
            <dd>{work.conditions}</dd>
          </div>
          <div>
            <dt>Artist</dt>
            <dd>
              {work.artist} ({work.artistBio})
            </dd>
          </div>
          <div>
            <dt>Date</dt>
            <dd>{work.date}</dd>
          </div>
          <div>
            <dt>Medium</dt>
            <dd>{work.medium}</dd>
          </div>
          <div>
            <dt>Size</dt>
            <dd>{work.dimensions}</dd>
          </div>
          <div>
            <dt>Collection</dt>
            <dd>{work.collection}</dd>
          </div>
          <div>
            <dt>Credit</dt>
            <dd>{work.creditLine}</dd>
          </div>
          <div>
            <dt>Number</dt>
            <dd>{work.accession}</dd>
          </div>
        </dl>
      </section>
      <p className="exh-image-credit">
        Photograph: {work.collection}, open access, public domain.
      </p>
    </article>
  );
}
