# Image and data credits

The two sky maps Tonight samples through its projection, and the star catalogue it draws.

| file | what | source | credit and terms |
|---|---|---|---|
| `milky-way-2020-celestial-4k.webp` | The Milky Way without its bright stars: the `milkyway_2020_4k.exr` layer of *Deep Star Maps 2020*, a plate carrée map in celestial (ICRF/J2000) coordinates, 0h right ascension at the centre and RA increasing leftward. Converted from linear OpenEXR to sRGB (ffmpeg, IEC 61966-2-1 transfer), smoothed by a Gaussian of radius 1.1 px so the faint-star grain does not alias under the lens (the page draws its own stars from the catalogue), and re-encoded as WebP at 4096 × 2048; no other change. | [NASA SVS 4851](https://svs.gsfc.nasa.gov/4851) | NASA/Goddard Space Flight Center Scientific Visualization Studio. Gaia DR2: ESA/Gaia/DPAC. NASA imagery is not copyrighted; used under NASA's reproduction guidelines with the credit line the page carries. |
| `constellation-figures-2020-celestial-8k.webp` | The constellation stick figures of the same release (`constellation_figures_8k.tif`), a grayscale plate carrée layer in the same coordinates, re-encoded losslessly. | [NASA SVS 4851](https://svs.gsfc.nasa.gov/4851) | As above; the figures are based on work by Alan MacRobert of *Sky & Telescope* for the IAU (with Roger Sinnott and Rick Fienberg). |
| `../data/stars.bin`, `../data/names.json` | 9,096 stars to visual magnitude 7.96 with J2000 positions, V magnitude and B−V colour, built by `apps/demo/scripts/build-planetarium-stars.mjs` from the *Bright Star Catalogue, 5th Revised Edition*; the 88 proper names are the page's, each checked against the catalogue's Bayer designation at build time. | [CDS V/50](https://cdsarc.cds.unistra.fr/viz-bin/cat/V/50), Hoffleit D., Warren Jr W.H. (1991) | Public domain (Astronomical Data Center, NSSDC/ADC). |

Positions of the Sun, Moon and planets, rise and set times, twilight and constellation membership
are computed in the browser by [astronomy-engine](https://github.com/cosinekitty/astronomy)
(Don Cross, MIT licence). The page names NASA, ESA/Gaia/DPAC and the catalogue in its Place
platter, so the credit is on screen and not only in this file.
