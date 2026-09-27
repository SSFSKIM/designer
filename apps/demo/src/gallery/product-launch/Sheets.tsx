/**
 * The content layer: printed sheets and the windows between them.
 *
 * A window is a transparent stretch of the scrolling column through which the plane (the fixed
 * canvas) shows whole; it carries the photograph's description for assistive technology and
 * nothing else. A sheet is opaque paper: type, hairlines and tabular figures, no shadow, no
 * glass. The comparison cards inside the sheets are content, so they are tonal fills, and the
 * radio inputs in them are ordinary form controls kept in step with the configure bar.
 */

import type { ReactNode, Ref } from "react";

import {
  BODY_PRICE,
  BODY_SPECS,
  CREDIT_ORDER,
  FINISHES,
  formatPrice,
  IN_THE_BOX,
  LENSES,
  PHOTOS,
  SENSOR_FIGURES,
  SENSOR_SPECS,
  finishById,
  lensById,
  type FinishId,
  type LensId,
  type PhotoId,
} from "./content";

export interface WindowRefs {
  readonly hero: Ref<HTMLDivElement>;
  readonly sensor: Ref<HTMLDivElement>;
  readonly lens: Ref<HTMLDivElement>;
  readonly finish: Ref<HTMLDivElement>;
}

interface SheetsProps {
  readonly windows: WindowRefs;
  readonly finish: FinishId;
  readonly lens: LensId;
  readonly onFinish: (finish: FinishId) => void;
  readonly onLens: (lens: LensId) => void;
  readonly priceHeadingRef: Ref<HTMLHeadingElement>;
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
}

function Caption(props: { readonly photo: PhotoId }): ReactNode {
  const photo = PHOTOS[props.photo];
  return (
    <p className="caption">
      <span className="caption__mark" aria-hidden="true">
        ↑
      </span>
      <span>{photo.caption}</span>
      <span className="caption__credit">
        Photograph: <a href={photo.credit.profile}>{photo.credit.name}</a>
      </span>
    </p>
  );
}

function Specs(props: { readonly rows: readonly (readonly [string, string])[] }): ReactNode {
  return (
    <dl className="specs">
      {props.rows.map(([term, value]) => (
        <div className="specs__row" key={term}>
          <dt>{term}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function Window(props: {
  readonly photo: PhotoId;
  readonly windowRef: Ref<HTMLDivElement>;
  readonly hero?: boolean;
}): ReactNode {
  return (
    <div
      ref={props.windowRef}
      className={props.hero === true ? "window window--hero" : "window"}
      role="img"
      aria-label={PHOTOS[props.photo].alt}
    />
  );
}

export function Sheets(props: SheetsProps): ReactNode {
  const lens = lensById(props.lens);
  const finish = finishById(props.finish);
  const total = BODY_PRICE + lens.price;
  const from = BODY_PRICE + Math.min(...LENSES.map((option) => option.price));

  return (
    <main className="page">
      <section id="top" aria-labelledby="top-title">
        <Window photo="hero" windowRef={props.windows.hero} hero />
        <div className="sheet sheet--intro">
          <Caption photo="hero" />
          <div className="intro">
            <p className="eyebrow">Alder Camera Co. · Portland, Oregon</p>
            <h1 id="top-title">Alder One</h1>
            <p className="lede">
              A full-frame camera designed, machined and assembled by fourteen people. One sensor,
              three lenses, two finishes, and nothing you have to dig through a menu to find.
            </p>
            <dl className="facts">
              <div>
                <dt>Orders</dt>
                <dd>Open today</dd>
              </div>
              <div>
                <dt>Ships</dt>
                <dd>From 4 November 2026</dd>
              </div>
              <div>
                <dt>From</dt>
                <dd>{formatPrice(from)} with a lens</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <section id="sensor" aria-labelledby="sensor-title">
        <Window photo="sensor" windowRef={props.windows.sensor} />
        <div className="sheet">
          <Caption photo="sensor" />
          <header className="head">
            <p className="kicker">The sensor</p>
            <h2 id="sensor-title">Full frame, and every photosite earns its place.</h2>
          </header>
          <div className="prose">
            <p>
              A back-illuminated 36 × 24 mm sensor with no optical low-pass filter in front of it.
              We stopped at 24.5 megapixels on purpose: each photosite is 5.9 µm across and
              gathers more light than the ones on a sixty-megapixel sensor, which is where the
              clean files at ISO 12,800 and the 14.8 stops at base come from.
            </p>
            <p>
              The sensor floats on a five-axis stabiliser that holds a 45 mm frame steady for a
              quarter of a second by hand, and reads out in 12.5 ms, fast enough that the silent
              shutter does not bend a passing car.
            </p>
          </div>
          <ul className="figures">
            {SENSOR_FIGURES.map(([figure, label]) => (
              <li key={figure}>
                <span className="figures__value">{figure}</span>
                <span className="figures__label">{label}</span>
              </li>
            ))}
          </ul>
          <Specs rows={SENSOR_SPECS} />
        </div>
      </section>

      <section id="lenses" aria-labelledby="lenses-title">
        <Window photo={lens.photo} windowRef={props.windows.lens} />
        <div className="sheet">
          <Caption photo={lens.photo} />
          <header className="head">
            <p className="kicker">The lenses</p>
            <h2 id="lenses-title">Three primes, one mount, no zooms.</h2>
          </header>
          <div className="prose">
            <p>
              Every Alder lens focuses on a helicoid you can feel and has an aperture ring marked
              in thirds. The AL mount has a 20 mm flange and eleven contacts, so the camera knows
              the focus distance and corrects the lens in the raw file, not in the glass.
            </p>
          </div>
          <fieldset className="choices choices--three">
            <legend className="visually-hidden">Your lens</legend>
            {LENSES.map((option) => (
              <label
                className="card"
                key={option.id}
                data-selected={option.id === props.lens ? "" : undefined}
              >
                <img className="card__image" src={PHOTOS[option.photo].src} alt="" loading="lazy" />
                <span className="card__head">
                  <input
                    type="radio"
                    name="lens"
                    value={option.id}
                    checked={option.id === props.lens}
                    onChange={() => props.onLens(option.id)}
                  />
                  <span className="card__name">{option.name}</span>
                </span>
                <span className="card__character">{option.character}</span>
                <span className="card__text">{option.description}</span>
                <Specs rows={option.specs} />
                <span className="card__price">{formatPrice(option.price)}</span>
              </label>
            ))}
          </fieldset>
        </div>
      </section>

      <section id="body" aria-labelledby="body-title">
        <Window photo={finish.photo} windowRef={props.windows.finish} />
        <div className="sheet">
          <Caption photo={finish.photo} />
          <header className="head">
            <p className="kicker">The body</p>
            <h2 id="body-title">Machined from one billet, finished twice.</h2>
          </header>
          <div className="prose">
            <p>
              The top and base plates are cut from a single billet of magnesium alloy, not cast,
              then finished by hand in one of two ways. The controls are where your fingers
              already are: shutter speed on the top plate, aperture on the lens, ISO on a dial
              under your thumb. The menu is four pages long.
            </p>
          </div>
          <fieldset className="choices choices--two">
            <legend className="visually-hidden">Your finish</legend>
            {FINISHES.map((option) => (
              <label
                className="card"
                key={option.id}
                data-selected={option.id === props.finish ? "" : undefined}
              >
                <img className="card__image" src={PHOTOS[option.card].src} alt="" loading="lazy" />
                <span className="card__head">
                  <input
                    type="radio"
                    name="finish"
                    value={option.id}
                    checked={option.id === props.finish}
                    onChange={() => props.onFinish(option.id)}
                  />
                  <span className="card__name">{option.name}</span>
                </span>
                <span className="card__character">{option.summary}</span>
                <span className="card__text">{option.description}</span>
                <span className="card__price">No extra cost</span>
              </label>
            ))}
          </fieldset>
          <Specs rows={BODY_SPECS} />
        </div>
      </section>

      <section id="price" aria-labelledby="price-title">
        <div className="sheet sheet--last">
          <header className="head">
            <p className="kicker">Price</p>
            <h2 id="price-title" ref={props.priceHeadingRef} tabIndex={-1}>
              Your Alder One: {formatPrice(total)}.
            </h2>
          </header>
          <div className="summary">
            <table className="summary__table">
              <caption className="visually-hidden">Your configuration</caption>
              <tbody>
                <tr>
                  <th scope="row">Alder One body, {finish.name}</th>
                  <td>{formatPrice(BODY_PRICE)}</td>
                </tr>
                <tr>
                  <th scope="row">{lens.name}</th>
                  <td>{formatPrice(lens.price)}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <th scope="row">Total</th>
                  <td>{formatPrice(total)}</td>
                </tr>
              </tfoot>
            </table>
            <p className="summary__note">
              US dollars, before sales tax. Shipping in the United States is free. Change the
              finish and lens here or in the bar below; the order button carries the total.
            </p>
          </div>
          <div className="terms">
            <div>
              <h3>Delivery</h3>
              <p>
                Orders placed today ship from 4 November 2026, in the order they were placed. We
                build about ninety a week.
              </p>
            </div>
            <div>
              <h3>In the box</h3>
              <ul>
                {IN_THE_BOX.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Warranty</h3>
              <p>
                Three years, parts and labour, repaired in Portland by the people who built it.
                Thirty days to change your mind.
              </p>
            </div>
          </div>

          <footer className="colophon">
            <div>
              <h3>Photographs</h3>
              <ul className="credits">
                {CREDIT_ORDER.map((id) => (
                  <li key={id}>
                    <a href={PHOTOS[id].credit.page}>{PHOTOS[id].caption}</a>{" "}
                    <span>
                      by <a href={PHOTOS[id].credit.profile}>{PHOTOS[id].credit.name}</a>,
                      Unsplash
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Display</h3>
              <p>
                The glass on this page follows your system's Reduce Transparency setting where the
                browser can report it. You can set it here for this page.
              </p>
              <label className="switch">
                <input
                  type="checkbox"
                  role="switch"
                  checked={props.reduceTransparency}
                  onChange={(event) => props.onReduceTransparency(event.target.checked)}
                />
                <span>Reduce transparency</span>
              </label>
              <p className="colophon__small">
                Alder is a fictional maker; the figures are realistic, the camera is not for sale.
                Built on vitrea 0.24.0. <a href="../">Back to the gallery</a>
              </p>
            </div>
          </footer>
        </div>
      </section>
    </main>
  );
}
