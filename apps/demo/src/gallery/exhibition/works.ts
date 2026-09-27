/**
 * The exhibition's eight works and its introduction.
 *
 * Every tombstone field is the holding museum's own record (The Met's Open Access API, the Art
 * Institute of Chicago's API and the Rijksmuseum's Linked Art data, read 2026-09-27); the essays
 * are this exhibition's, written from those records and the museums' published descriptions, and
 * `images/CREDITS.md` names each photograph's source and licence. The order is chronological,
 * which is the exhibition's argument: the sky moving from backdrop to subject, from a Dutch winter
 * in the Little Ice Age to a London fog that was largely coal smoke.
 */

import avercamp from "./images/avercamp.jpg";
import caillebotte from "./images/caillebotte.jpg";
import cole from "./images/cole.jpg";
import heade from "./images/heade.jpg";
import homer from "./images/homer.jpg";
import monet from "./images/monet.jpg";
import ruisdael from "./images/ruisdael.jpg";
import vangogh from "./images/vangogh.jpg";

export interface Work {
  /** The phase id: the room's weather, lower case. */
  readonly id: string;
  /** The room's weather, as the exhibition names it. */
  readonly weather: string;
  /** What the sky is doing, for the data list. */
  readonly conditions: string;
  readonly title: string;
  readonly artist: string;
  /** Nationality and life dates, as the museum gives them. */
  readonly artistBio: string;
  readonly date: string;
  readonly medium: string;
  readonly dimensions: string;
  readonly collection: string;
  readonly creditLine: string;
  readonly accession: string;
  readonly image: string;
  /** Pixel size of the file in `images/`, so layout never waits on a decode. */
  readonly imageSize: readonly [number, number];
  /**
   * Where the environment's crop sits vertically, 0 (top) to 1 (bottom), as a fraction of the
   * slack the cover fit leaves. Every work is landscape, so the crop is only ever vertical.
   */
  readonly focusY: number;
  /** A short description of the painting for the canvas's accessible name. */
  readonly alt: string;
  readonly essay: readonly string[];
}

export const EXHIBITION = {
  title: "Weather in Painting",
  subtitle: "Eight skies, 1608–1900",
  introduction: [
    "For most of the history of European painting the sky was the back wall of the picture. " +
      "This exhibition follows it becoming the subject: eight rooms, each holding one work, " +
      "from a Dutch winter in the Little Ice Age to a London fog that was largely coal smoke.",
    "Each work fills the room. Its label sits beside it, and the audio guide reads the label " +
      "aloud in your browser’s own voice.",
  ],
} as const;

export const WORKS: readonly Work[] = [
  {
    id: "frost",
    weather: "Frost",
    conditions: "Hard frost, haze over the ice",
    title: "Winter Landscape with Ice Skaters",
    artist: "Hendrick Avercamp",
    artistBio: "Dutch, 1585–1634",
    date: "c. 1608",
    medium: "Oil on panel",
    dimensions: "77.3 × 131.9 cm",
    collection: "Rijksmuseum, Amsterdam",
    creditLine: "Purchased with the support of the Vereniging Rembrandt",
    accession: "SK-A-1718",
    image: avercamp,
    imageSize: [2400, 1385],
    focusY: 0.55,
    alt:
      "A frozen river crowded with skaters, walkers and a horse-drawn sledge, a church and " +
      "brick houses on the left, bare trees against a pale winter sky.",
    essay: [
      "Avercamp made his name painting winter, in the years when the Little Ice Age brought " +
        "hard frosts to the Low Countries. Here a whole village has moved onto the ice: skaters, " +
        "walkers, players of kolf, a horse-drawn sledge on the right, a church on the left.",
      "Look at how the air is built. The figures in front are sharp and full of colour; a few " +
        "hundred metres back they thin into grey-white haze, and the far bank all but " +
        "dissolves. That haze is the weather: cold, damp air thick enough to carry the light.",
      "Avercamp signed the picture on the wall of a wooden shed on the right, among the " +
        "scratched graffiti, where it is easy to miss.",
    ],
  },
  {
    id: "cloud",
    weather: "Cloud",
    conditions: "Heaped cumulus, sun breaking through",
    title: "The Windmill at Wijk bij Duurstede",
    artist: "Jacob van Ruisdael",
    artistBio: "Dutch, 1628/29–1682",
    date: "c. 1668–70",
    medium: "Oil on canvas",
    dimensions: "83 × 101 cm",
    collection: "Rijksmuseum, Amsterdam",
    creditLine: "On loan from the City of Amsterdam (A. van der Hoop Bequest)",
    accession: "SK-C-211",
    image: ruisdael,
    imageSize: [2400, 1976],
    focusY: 0.42,
    alt:
      "A tall windmill on a riverbank under a sky of towering grey and white clouds, a " +
      "sailing boat on the river to the left.",
    essay: [
      "Ruisdael sets the horizon very low, so the sky takes more than half the canvas, and he " +
        "paints it as a structure: banks of cumulus heaped over one another, grey underneath, " +
        "lit at their edges by a sun we cannot see.",
      "Below, the mill stands near the bank of the river Lek. A sailing boat is out on the " +
        "water, the towers of Duurstede castle and the church rise in the distance, and a few " +
        "women walk along the bank, very small against the mill.",
      "Dutch painters of the seventeenth century made the sky a subject in its own right. Few " +
        "made it carry as much of a picture as this.",
    ],
  },
  {
    id: "clearing",
    weather: "Clearing",
    conditions: "Thunderstorm passing, sun on the valley",
    title: "View from Mount Holyoke, Northampton, Massachusetts, after a Thunderstorm—The Oxbow",
    artist: "Thomas Cole",
    artistBio: "American, born England, 1801–1848",
    date: "1836",
    medium: "Oil on canvas",
    dimensions: "130.8 × 193 cm",
    collection: "The Metropolitan Museum of Art, New York",
    creditLine: "Gift of Mrs. Russell Sage, 1908",
    accession: "08.228",
    image: cole,
    imageSize: [2400, 1630],
    focusY: 0.5,
    alt:
      "A panorama from a wooded mountaintop: a dark storm with falling rain on the left, and " +
      "on the right a sunlit valley where a river makes a great loop through fields.",
    essay: [
      "A thunderstorm is leaving the Connecticut River valley. On the left it still hangs over " +
        "wild, broken trees, and rain falls in grey veils across the hills. On the right the " +
        "air has cleared over cleared land: fields, farms and the river’s great loop.",
      "Cole divided the picture along a diagonal, and the weather does the dividing. He " +
        "painted it for the 1836 annual exhibition of the National Academy of Design, calling " +
        "the view from Mount Holyoke “about the finest scene I have in my sketchbook.”",
      "Look for the painter himself near the bottom of the canvas: a small figure at an easel " +
        "among the rocks, turning back toward us.",
    ],
  },
  {
    id: "thunder",
    weather: "Thunder",
    conditions: "Thunderstorm approaching over still water",
    title: "Approaching Thunder Storm",
    artist: "Martin Johnson Heade",
    artistBio: "American, 1819–1904",
    date: "1859",
    medium: "Oil on canvas",
    dimensions: "71.1 × 111.8 cm",
    collection: "The Metropolitan Museum of Art, New York",
    creditLine:
      "Gift of Erving Wolf Foundation and Mr. and Mrs. Erving Wolf, " +
      "in memory of Diane R. Wolf, 1975",
    accession: "1975.160",
    image: heade,
    imageSize: [2400, 1527],
    focusY: 0.62,
    alt:
      "A man and a small white dog sit on a sunlit shore facing a bay of black water under a " +
      "black sky; a white sail and a rowing boat are out on the water.",
    essay: [
      "A man and his dog sit on the shore of Narragansett Bay, Rhode Island, with sunlight " +
        "still at their backs. Ahead of them the sky has gone almost black, and a thin red bolt " +
        "of lightning cuts down on the left. A rower pulls for shore; a white sail stands out " +
        "against the dark.",
      "A critic of Heade’s day spoke of the “ominous hush” before such a storm, and that is " +
        "what the picture holds: not the storm itself but the minute before it.",
      "Painted two years before the Civil War, it has often been read as a picture of a " +
        "country waiting for something to break. Heade based it on a storm he had watched from " +
        "Prudence Island, in the bay, around 1858.",
    ],
  },
  {
    id: "rain",
    weather: "Rain",
    conditions: "Light rain, overcast",
    title: "Paris Street; Rainy Day",
    artist: "Gustave Caillebotte",
    artistBio: "French, 1848–1894",
    date: "1877",
    medium: "Oil on canvas",
    dimensions: "212.2 × 276.2 cm",
    collection: "The Art Institute of Chicago",
    creditLine: "Charles H. and Mary F. S. Worcester Collection",
    accession: "1964.336",
    image: caillebotte,
    imageSize: [2400, 1863],
    focusY: 0.55,
    alt:
      "A Paris intersection on a rainy day: a couple under an umbrella walk toward the viewer" +
      " on the right, a green lamppost in the middle, wet paving stones and other walkers " +
      "with umbrellas behind.",
    essay: [
      "There are no raindrops in this picture. Caillebotte paints the rain through what it " +
        "does: the paving stones shine, the light is flat and pearly, and almost everyone " +
        "carries an umbrella, the newly invented retractable kind.",
      "The place is a busy intersection a short walk from the painter’s home, in a Paris " +
        "rebuilt with wide streets and uniform stone façades. A green lamppost splits the " +
        "canvas in two; the couple on the right walk straight toward us, looking at something " +
        "beyond the frame.",
      "Nearly life-size, it is Caillebotte’s largest painting. He showed it at the third " +
        "Impressionist exhibition in 1877, the year he made it.",
    ],
  },
  {
    id: "wind",
    weather: "Wind",
    conditions: "Summer wind, fast cloud",
    title: "Wheat Field with Cypresses",
    artist: "Vincent van Gogh",
    artistBio: "Dutch, 1853–1890",
    date: "1889",
    medium: "Oil on canvas",
    dimensions: "73.2 × 93.4 cm",
    collection: "The Metropolitan Museum of Art, New York",
    creditLine: "Purchase, The Annenberg Foundation Gift, 1993",
    accession: "1993.132",
    image: vangogh,
    imageSize: [1800, 1411],
    focusY: 0.45,
    alt:
      "A golden wheat field bending in the wind, a dark green cypress on the right, olive " +
      "trees and blue hills beneath a sky of swirling white clouds.",
    essay: [
      "Everything in this field is moving the same way. The wheat bends, the olive trees toss, " +
        "the cypresses flicker like dark flames, and the clouds curl across the sky in thick " +
        "ridges of white and blue. Van Gogh laid the paint on so heavily that the brushstrokes " +
        "themselves take the shape of the wind.",
      "He painted it in late June or early July 1889 at Saint-Rémy in Provence, where he was a " +
        "patient at the asylum of Saint-Paul-de-Mausole, working outdoors in front of the " +
        "motif.",
      "He counted it among his best summer canvases, and that September made two studio " +
        "versions of it: one now in the National Gallery, London, the other a smaller copy for " +
        "his mother and sister.",
    ],
  },
  {
    id: "gale",
    weather: "Gale",
    conditions: "Winter northeaster off the Atlantic",
    title: "Northeaster",
    artist: "Winslow Homer",
    artistBio: "American, 1836–1910",
    date: "1895; reworked by 1901",
    medium: "Oil on canvas",
    dimensions: "87.6 × 127 cm",
    collection: "The Metropolitan Museum of Art, New York",
    creditLine: "Gift of George A. Hearn, 1910",
    accession: "10.64.5",
    image: homer,
    imageSize: [2400, 1639],
    focusY: 0.5,
    alt:
      "A huge white burst of spray over a dark rocky ledge, green-blue waves breaking under a" +
      " grey sky.",
    essay: [
      "A northeaster is a winter storm that drives in off the Atlantic on a northeast wind. " +
        "Homer watched them from Prouts Neck, on the coast of Maine, where he lived and painted " +
        "for the last decades of his life.",
      "When he first exhibited this canvas in 1895, two men in foul-weather gear crouched on the " +
        "rocks at the lower left. By 1900 he had painted them out and raised a much larger " +
        "column of spray. What is left is rock, water and air: the dark ledge, the green body of " +
        "the wave and the white burst where they meet.",
      "A critic in 1901 praised it for “great natural spaces unmarked by the presence of puny " +
        "man.”",
    ],
  },
  {
    id: "fog",
    weather: "Fog",
    conditions: "Winter fog and coal smoke",
    title: "Waterloo Bridge, Gray Weather",
    artist: "Claude Monet",
    artistBio: "French, 1840–1926",
    date: "1900",
    medium: "Oil on canvas",
    dimensions: "65.4 × 92.6 cm",
    collection: "The Art Institute of Chicago",
    creditLine: "Gift of Mrs. Mortimer B. Harris",
    accession: "1984.1173",
    image: monet,
    imageSize: [2400, 1697],
    focusY: 0.5,
    alt:
      "The arches of a bridge across a river, dissolved in grey-green haze, with factory " +
      "chimneys and towers faint behind.",
    essay: [
      "Without the fog, Monet once remarked, London “wouldn’t be a beautiful city. It’s the " +
        "fog that gives it its magnificent breadth.” Much of that fog was the smoke of coal " +
        "fires, thickest in winter, which is when he came to paint it.",
      "He painted Waterloo Bridge in the mornings from his fifth-floor window at the Savoy " +
        "Hotel, moving on to Charing Cross Bridge later in the day. Here the bridge is a dark " +
        "band of arches, and the city behind it is only chimneys and towers in the haze.",
      "He finished the London pictures in his studio at Giverny, and would not release any of " +
        "them until he was satisfied with the series as a whole.",
    ],
  },
];

export const WORK_IDS: readonly string[] = WORKS.map((work) => work.id);

export function workById(id: string): Work | undefined {
  return WORKS.find((work) => work.id === id);
}
