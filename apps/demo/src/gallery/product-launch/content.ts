/**
 * The product, as data: one body, two finishes, three lenses, and the photographs the page stands
 * on. Everything a sheet prints and everything the configure bar sells comes from here, so the
 * price in the order button and the price in the summary table cannot disagree.
 *
 * The maker is fictional. The figures are chosen to sit where a real small maker's full-frame
 * camera would: a 24-megapixel sensor with large photosites rather than a resolution race, manual
 * primes, a machined body, a price between the volume makers' enthusiast bodies and Leica's.
 */

import finishGraphite from "./images/finish-graphite.jpg";
import finishNickel from "./images/finish-nickel.jpg";
import heroBody from "./images/hero-body.jpg";
import lens28 from "./images/lens-28.jpg";
import lens45 from "./images/lens-45.jpg";
import lens90 from "./images/lens-90.jpg";
import sensor from "./images/sensor.jpg";

export type FinishId = "nickel" | "graphite";
export type LensId = "28" | "45" | "90";
export type PhotoId =
  | "hero"
  | "sensor"
  | "lens-28"
  | "lens-45"
  | "lens-90"
  | "finish-nickel"
  | "finish-graphite"
  | "nickel-ring";

export interface Photo {
  readonly id: PhotoId;
  readonly src: string;
  /** The window's accessible description. */
  readonly alt: string;
  /** The caption printed at the head of the sheet that follows the window. */
  readonly caption: string;
  /**
   * Where the cover-fit crop is anchored, as CSS `object-position` fractions. Chosen per photograph
   * so the two bands the floating bars stand on carry structure (seams, rings, blades, grain)
   * rather than an empty corner; checked on the rendered page, not assumed.
   */
  readonly focus: readonly [number, number];
  /**
   * How many times closer than the cover fit the plane frames it; absent is the cover fit. The
   * focus then anchors the crop inside the larger overflow, exactly as `object-position` would.
   */
  readonly zoom?: number;
  readonly credit: { readonly name: string; readonly profile: string; readonly page: string };
}

export const PHOTOS: Readonly<Record<PhotoId, Photo>> = {
  hero: {
    id: "hero",
    src: heroBody,
    alt: "An Alder One in Nickel lying on weathered red-brown deck boards, photographed from above, its strap looped beside it.",
    caption: "The Alder One in Nickel, on the bench.",
    focus: [0.5, 0.3],
    credit: {
      name: "Wesley Hilario",
      profile: "https://unsplash.com/@wesley_squared",
      page: "https://unsplash.com/photos/black-and-silver-dslr-camera-on-brown-wooden-surface-VZMoJL9C53k",
    },
  },
  sensor: {
    id: "sensor",
    src: sensor,
    alt: "The camera's mount with the lens removed: a bright steel bayonet ring around the exposed sensor, which glows pale green and cream.",
    caption: "The AL mount with the lens off, and the sensor behind it.",
    focus: [0.5, 0.5],
    credit: {
      name: "kuaileqie RE",
      profile: "https://unsplash.com/@kuaileqie",
      page: "https://unsplash.com/photos/a-close-up-of-a-camera-lens-EdlPw15eHpE",
    },
  },
  "lens-28": {
    id: "lens-28",
    src: lens28,
    alt: "Looking into the 28 mm lens: eleven dark rounded aperture blades closed to a small bright opening.",
    caption: "The 28 mm's eleven rounded blades, stopped down.",
    focus: [0.5, 0.5],
    credit: {
      name: "Kool C",
      profile: "https://unsplash.com/@koolcreation",
      page: "https://unsplash.com/photos/black-camera-lens-in-close-up-photography-7jabkilL0qI",
    },
  },
  "lens-45": {
    id: "lens-45",
    src: lens45,
    alt: "The 45 mm lens wide open, its front elements reflecting bands of magenta, teal and sky blue.",
    caption: "The 45 mm wide open, the coating blooming across the front element.",
    focus: [0.5, 0.5],
    credit: {
      name: "Agence Olloweb",
      profile: "https://unsplash.com/@olloweb",
      page: "https://unsplash.com/photos/a-close-up-of-a-lens-with-a-blurry-background-9wYdW55NbnY",
    },
  },
  "lens-90": {
    id: "lens-90",
    src: lens90,
    alt: "The rear of the 90 mm macro lens, its gold electrical contacts curving around the mount.",
    caption: "The gold contacts on the rear of the 90 mm Macro.",
    focus: [0.5, 0.5],
    credit: {
      name: "Tatiana Conde",
      profile: "https://unsplash.com/@condetatiana",
      page: "https://unsplash.com/photos/black-camera-lens-on-brown-wooden-table-ml4he3xUYFg",
    },
  },
  /*
   * The Nickel phase is the hero's photograph at one and a half times the cover fit, not the
   * knurled-ring macro. The macro is one diagonal band of knurling across a defocused field, and
   * the page's two bars are horizontal and centred 808 px apart: at the cover fit the band passes
   * under neither (a crop anchor has 60 px of vertical travel at 1440 × 900), and bringing it under
   * both needs the band steep enough to cross both bars, which it only is over a stretch about
   * 330 px tall, a zoom of about 2.4. This frame puts board seams, wood grain, the strap and the
   * camera's own plates under every surface; the macro stays on the page as the Nickel card's
   * photograph (`nickel-ring`), and this frame is credited by the hero's line.
   */
  "finish-nickel": {
    id: "finish-nickel",
    src: heroBody,
    alt: "Closer on the Alder One in Nickel on the deck boards: the satin top plate, the knurled shutter-speed dial and the knurled focus ring of the lens.",
    caption: "Closer on a Nickel body: satin plates and knurled dials.",
    focus: [0.12, 0.27],
    zoom: 1.5,
    credit: {
      name: "Wesley Hilario",
      profile: "https://unsplash.com/@wesley_squared",
      page: "https://unsplash.com/photos/black-and-silver-dslr-camera-on-brown-wooden-surface-VZMoJL9C53k",
    },
  },
  "finish-graphite": {
    id: "finish-graphite",
    src: finishGraphite,
    alt: "The octagonal viewfinder window of a Graphite body, set into black pebbled leatherette.",
    caption: "The viewfinder window of a Graphite body, set into leatherette.",
    focus: [0.5, 0.5],
    credit: {
      name: "Jonathan Cosens Photography",
      profile: "https://unsplash.com/@jcosens",
      page: "https://unsplash.com/photos/close-up-of-a-vintage-camera-lens-with-textured-background-FojZAX9TOQA",
    },
  },
  "nickel-ring": {
    id: "nickel-ring",
    src: finishNickel,
    alt: "A close-up of the knurled control ring on a Nickel body, in soft black and white.",
    caption: "The knurled control ring of a Nickel body, bead-blasted satin.",
    focus: [0.5, 0.5],
    credit: {
      name: "Jonathan Cosens Photography",
      profile: "https://unsplash.com/@jcosens",
      page: "https://unsplash.com/photos/close-up-of-a-textured-metal-surface-im5lgiYl4Ro",
    },
  },
};

/**
 * Credit order on the page: one line per photograph file, in the order they appear. The Nickel
 * phase is the hero's photograph and is credited by the hero's line.
 */
export const CREDIT_ORDER: readonly PhotoId[] = [
  "hero",
  "sensor",
  "lens-28",
  "lens-45",
  "lens-90",
  "nickel-ring",
  "finish-graphite",
];

export const BODY_PRICE = 2390;

export interface Finish {
  readonly id: FinishId;
  readonly name: string;
  readonly summary: string;
  readonly description: string;
  /** The swatch drawn beside the name: the finish's own colour, a fill, never a tint. */
  readonly swatch: string;
  /** The plane's photograph while this finish is chosen. */
  readonly photo: PhotoId;
  /** The photograph printed on this finish's comparison card. */
  readonly card: PhotoId;
}

export const FINISHES: readonly Finish[] = [
  {
    id: "nickel",
    name: "Nickel",
    summary: "Bead-blasted satin",
    description:
      "Top and base plates in bead-blasted satin nickel, with knurled control rings. It wears to a soft polish where your hands go, which is the point.",
    swatch: "#b9b6b0",
    photo: "finish-nickel",
    card: "nickel-ring",
  },
  {
    id: "graphite",
    name: "Graphite",
    summary: "Black anodised, leatherette",
    description:
      "Hard-anodised black plates and a pebbled leatherette wrap. Nothing on it catches the light, which is what street photographers ask us for.",
    swatch: "#2b2a29",
    photo: "finish-graphite",
    card: "finish-graphite",
  },
];

export interface Lens {
  readonly id: LensId;
  /** The short name the configure bar and the platter print. */
  readonly short: string;
  readonly name: string;
  readonly character: string;
  readonly description: string;
  readonly price: number;
  readonly photo: PhotoId;
  readonly specs: readonly (readonly [string, string])[];
}

export const LENSES: readonly Lens[] = [
  {
    id: "28",
    short: "28 mm f/2",
    name: "Alder 28 mm f/2",
    character: "The everyday wide",
    description:
      "Small enough to leave on. Eleven rounded blades keep points of light round two stops down, where you will use it most.",
    price: 690,
    photo: "lens-28",
    specs: [
      ["Construction", "9 elements in 7 groups, 2 aspherical"],
      ["Aperture", "f/2 to f/16, 11 rounded blades"],
      ["Closest focus", "0.25 m, 0.15×"],
      ["Filter", "43 mm"],
      ["Weight", "212 g"],
    ],
  },
  {
    id: "45",
    short: "45 mm f/1.4",
    name: "Alder 45 mm f/1.4",
    character: "The fast normal",
    description:
      "A touch wider than fifty, the way the eye sees a room. Wide open it is soft at the edges on purpose; by f/2.8 it is sharp to the corners.",
    price: 1090,
    photo: "lens-45",
    specs: [
      ["Construction", "10 elements in 8 groups, 1 aspherical, 2 ED"],
      ["Aperture", "f/1.4 to f/16, 9 rounded blades"],
      ["Closest focus", "0.40 m, 0.14×"],
      ["Filter", "52 mm"],
      ["Weight", "318 g"],
    ],
  },
  {
    id: "90",
    short: "90 mm f/2.8 Macro",
    name: "Alder 90 mm f/2.8 Macro",
    character: "Portraits, and life size",
    description:
      "A floating group keeps it sharp from infinity down to one-to-one. Long enough for a face, close enough for a watch movement.",
    price: 940,
    photo: "lens-90",
    specs: [
      ["Construction", "12 elements in 10 groups, floating focus"],
      ["Aperture", "f/2.8 to f/22, 9 rounded blades"],
      ["Closest focus", "0.28 m, 1.0×"],
      ["Filter", "55 mm"],
      ["Weight", "460 g"],
    ],
  },
];

export const SENSOR_FIGURES: readonly (readonly [string, string])[] = [
  ["24.5 MP", "Back-illuminated, no low-pass filter"],
  ["14.8 stops", "Dynamic range at ISO 64, measured on raw"],
  ["5.9 µm", "Photosites, for a clean ISO 12,800"],
  ["6.5 stops", "Sensor-shift stabilisation, five axes"],
];

export const SENSOR_SPECS: readonly (readonly [string, string])[] = [
  ["Sensor", "35.9 × 23.9 mm BSI CMOS, 6064 × 4040"],
  ["Sensitivity", "ISO 64 to 25,600; 32 to 102,400 extended"],
  ["Raw", "14-bit DNG, lossless compressed"],
  ["Shutter", "Mechanical 1/8000 s to 60 min; electronic to 1/32000 s"],
  ["Readout", "12.5 ms full sensor, for an electronic shutter you can pan with"],
  ["Autofocus", "Phase detection, 693 points, to −5 EV"],
  ["Stabilisation", "5-axis sensor shift, 6.5 stops (CIPA, with the 45 mm)"],
  ["Video", "4K 30p, 10-bit 4:2:2, oversampled from 6K"],
];

export const BODY_SPECS: readonly (readonly [string, string])[] = [
  ["Dimensions", "131 × 79 × 42 mm"],
  ["Weight", "612 g with battery and card"],
  ["Viewfinder", "5.76M-dot OLED, 0.78×, 23 mm eyepoint"],
  ["Rear screen", "3.0 in, 2.1M dots, tilting"],
  ["Sealing", "38 gaskets; rated for rain, not for rivers"],
  ["Storage", "Two UHS-II SD slots"],
  ["Battery", "AB-1, about 430 frames (CIPA); charges over USB-C"],
  ["Connections", "USB-C 10 Gb/s, Wi-Fi 6, Bluetooth 5.3"],
];

export const IN_THE_BOX: readonly string[] = [
  "Alder One body, in the finish you chose",
  "Your lens, with front and rear caps and a metal hood",
  "AB-1 battery and a USB-C cable",
  "Waxed-cotton strap",
  "Body cap and hot-shoe cover",
];

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export const formatPrice = (value: number): string => money.format(value);

export const lensById = (id: LensId): Lens => LENSES.find((lens) => lens.id === id) ?? LENSES[1]!;
export const finishById = (id: FinishId): Finish =>
  FINISHES.find((finish) => finish.id === id) ?? FINISHES[0]!;
