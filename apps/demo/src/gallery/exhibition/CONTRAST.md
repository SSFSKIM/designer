# Rendered-pixel contrast, every line

The per-line readings behind `DESIGN.md` part two. Each text line's ink is its element's computed
colour (painted through a canvas and read back: the runtime's token as it resolved that frame);
its surface is the same frame captured with every glyph and icon on the glass made transparent.
Per pixel of the line's box the ink is composited over that surface pixel in encoded sRGB and
the WCAG ratio taken. Each cell is `median / p10` for the line, p10 being its adverse tail (10th
percentile) and the number that gates; `surface` is the drawn body's encoded luma under the line
(median, active pose). Lines inside the window's scroll-edge fades are not read at that scroll
position; the scroller is stepped so every line is read clear of them (`scroll` is the scroll
offset in CSS px at which it was read). Floors: 4.5 for text, 3 for large text (24 px, or 18.66 px
bold) and for icons (marked `icon:`). A reading under its floor would be marked **FAIL**; none is.
Instrument: a Playwright script in Chromium (`channel: "chromium"`, real adapter), Reduce Motion
emulated so each phase is a cut, `__glassDemo.setPhase` then 700 ms to settle, the pose set with
`root.setWindowActivation`. Measured 2026-09-27 at the page as committed with this record.

## GPU tier

WebGPU, texture sampling, DPR 1, 1440 × 900, active and receded. 3756 line readings, 0 under floor. Worst p10 4.93: dark, active, wind, rooms view, window, “· you are here”.

### GPU tier · light · frost · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 12.67 / 12.42 | 11.51 / 11.24 | 0.906 |
| window | 0 | Room 1 of 8 | 13.79 / 13.62 | 12.86 / 12.69 | 0.953 |
| window | 0 | Frost (large) | 12.45 / 12.18 | 11.32 / 11.01 | 0.897 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 12.95 / 12.01 | 11.88 / 10.76 | 0.918 |
| window | 0 | Hendrick Avercamp | 12.47 / 12.09 | 11.3 / 10.91 | 0.897 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 12.49 / 12.27 | 11.4 / 11.1 | 0.898 |
| window | 0 | The whole work. The outline marks the part around you. | 11.2 / 10.33 | 9.8 / 8.74 | 0.842 |
| window | 0 | Avercamp made his name painting winter, in the years | 11.27 / 10.53 | 9.88 / 9.01 | 0.845 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 11.49 / 11.04 | 10.16 / 9.61 | 0.855 |
| window | 0 | Countries. Here a whole village has moved onto the | 11.5 / 11.14 | 10.18 / 9.74 | 0.855 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 11.03 / 10.62 | 9.6 / 9.11 | 0.835 |
| window | 0 | sledge on the right, a church on the left. | 10.97 / 10.38 | 9.52 / 8.83 | 0.832 |
| window | 0 | Look at how the air is built. The figures in front are | 10.7 / 10.34 | 9.21 / 8.78 | 0.821 |
| window | 0 | sharp and full of colour; a few hundred metres back | 10.59 / 10.26 | 9.06 / 8.69 | 0.815 |
| window | 0 | they thin into grey-white haze, and the far bank all but | 10.56 / 10.33 | 9.04 / 8.75 | 0.814 |
| Rooms | 0 | 1 | 12.55 / 11.96 | 11.47 / 10.81 | 0.901 |
| Rooms | 0 | / 8 | 12.9 / 12.73 | 11.89 / 11.64 | 0.916 |
| Audio guide | 0 | Audio guide | 13.16 / 12.86 | 12.13 / 11.81 | 0.927 |
| Audio guide | 0 | About 0:51 | 13.26 / 13 | 12.24 / 12.01 | 0.931 |
| Rooms | 0 | icon: Next room: Cloud | 13.08 / 12.99 | 12.15 / 12.06 | 0.923 |
| Audio guide | 0 | icon: Play the audio guide | 11.97 / 11.24 | 10.78 / 10.1 | 0.876 |
| window | 552 | Look at how the air is built. The figures in front are | 13.2 / 12.5 | 12.25 / 11.34 | 0.928 |
| window | 552 | sharp and full of colour; a few hundred metres back | 13.1 / 12.51 | 12.09 / 11.36 | 0.924 |
| window | 552 | they thin into grey-white haze, and the far bank all but | 13 / 12.26 | 11.93 / 11.09 | 0.92 |
| window | 552 | dissolves. That haze is the weather: cold, damp air | 12.94 / 11.99 | 11.87 / 10.74 | 0.917 |
| window | 552 | thick enough to carry the light. | 12.48 / 12 | 11.39 / 10.82 | 0.898 |
| window | 552 | Avercamp signed the picture on the wall of a wooden | 12.87 / 12.35 | 11.79 / 11.19 | 0.914 |
| window | 552 | shed on the right, among the scratched graffiti, where | 12.75 / 12.34 | 11.66 / 11.17 | 0.909 |
| window | 552 | it is easy to miss. | 12.11 / 11.85 | 10.89 / 10.53 | 0.882 |
| window | 552 | Weather | 9.91 / 9.67 | 8.61 / 8.32 | 0.784 |
| window | 552 | Hard frost, haze over the ice | 11.21 / 9.57 | 10.16 / 8.21 | 0.843 |
| window | 552 | Artist | 9.75 / 9.68 | 8.46 / 8.33 | 0.777 |
| window | 552 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 11.08 / 9.87 | 9.94 / 8.55 | 0.838 |
| window | 552 | Date | 9.48 / 9.45 | 8.1 / 8.04 | 0.764 |
| window | 552 | c. 1608 | 9.88 / 9.7 | 8.55 / 8.35 | 0.783 |
| window | 552 | Medium | 9.43 / 9.4 | 7.97 / 7.95 | 0.762 |
| window | 552 | Oil on panel | 10.31 / 9.87 | 9.07 / 8.55 | 0.803 |
| window | 552 | Size | 9.64 / 9.6 | 8.3 / 8.21 | 0.772 |
| window | 552 | 77.3 × 131.9 cm | 9.88 / 9.54 | 8.55 / 8.14 | 0.783 |
| window | 552 | Collection | 10.57 / 10.03 | 9.39 / 8.75 | 0.815 |
| window | 552 | Rijksmuseum, Amsterdam | 10.47 / 10.27 | 9.26 / 9.03 | 0.809 |
| window | 552 | Credit | 9.71 / 9.64 | 8.35 / 8.26 | 0.775 |
| window | 552 | Purchased with the support of the Vereniging | 9.99 / 9.6 | 8.68 / 8.25 | 0.788 |
| window | 552 | Rembrandt | 10.09 / 9.96 | 8.84 / 8.65 | 0.792 |
| window | 552 | Number | 9.43 / 9.24 | 8.02 / 7.77 | 0.762 |
| window | 552 | SK-A-1718 | 10.14 / 9.98 | 8.89 / 8.67 | 0.794 |
| window | 552 | Photograph: Rijksmuseum, Amsterdam , open access, public | 10.57 / 10.28 | 9.06 / 8.69 | 0.814 |
| window | 552 | domain. | 10.4 / 10.36 | 8.85 / 8.81 | 0.807 |

### GPU tier · light · cloud · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.95 / 9.93 | 8.62 / 8.55 | 0.787 |
| window | 0 | Room 2 of 8 | 10.11 / 10.03 | 8.78 / 8.7 | 0.794 |
| window | 0 | Cloud (large) | 9.95 / 9.86 | 8.55 / 8.53 | 0.787 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 10.2 / 9.97 | 8.86 / 8.62 | 0.798 |
| window | 0 | Jacob van Ruisdael | 10.11 / 10.03 | 8.78 / 8.7 | 0.794 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 10.2 / 10.11 | 8.87 / 8.78 | 0.798 |
| window | 0 | The whole work. The outline marks the part around you. | 10.7 / 10.28 | 9.48 / 8.94 | 0.821 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 10.96 / 10.53 | 9.74 / 9.25 | 0.832 |
| window | 0 | more than half the canvas, and he paints it as a | 10.86 / 10.59 | 9.58 / 9.32 | 0.828 |
| window | 0 | structure: banks of cumulus heaped over one another, | 10.86 / 10.51 | 9.58 / 9.23 | 0.828 |
| window | 0 | grey underneath, lit at their edges by a sun we | 10.94 / 10.76 | 9.72 / 9.48 | 0.832 |
| window | 0 | cannot see. | 10.94 / 10.94 | 9.71 / 9.65 | 0.831 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 11.73 / 11.54 | 10.58 / 10.37 | 0.866 |
| window | 0 | A sailing boat is out on the water, the towers of | 11.73 / 11.62 | 10.58 / 10.45 | 0.866 |
| window | 0 | Duurstede castle and the church rise in the distance, | 11.54 / 11.38 | 10.33 / 10.21 | 0.858 |
| Rooms | 0 | 2 | 9.97 / 9.88 | 9.04 / 8.95 | 0.788 |
| Rooms | 0 | / 8 | 10.21 / 10.11 | 9.25 / 9.13 | 0.799 |
| Audio guide | 0 | Audio guide | 10.22 / 10.13 | 9.28 / 9.21 | 0.799 |
| Audio guide | 0 | About 0:49 | 10.06 / 10.02 | 9.12 / 9.03 | 0.792 |
| Rooms | 0 | icon: Previous room: Frost | 10 / 9.89 | 9.07 / 8.95 | 0.789 |
| Rooms | 0 | icon: Next room: Clearing | 9.95 / 9.87 | 9.01 / 8.94 | 0.787 |
| Audio guide | 0 | icon: Play the audio guide | 10.14 / 10.04 | 9.21 / 9.05 | 0.795 |
| window | 552 | Below, the mill stands near the bank of the river Lek. | 10.12 / 9.93 | 8.86 / 8.55 | 0.794 |
| window | 552 | A sailing boat is out on the water, the towers of | 10.04 / 9.87 | 8.7 / 8.53 | 0.791 |
| window | 552 | Duurstede castle and the church rise in the distance, | 10.14 / 9.87 | 8.84 / 8.54 | 0.795 |
| window | 552 | and a few women walk along the bank, very small | 10.2 / 9.95 | 8.86 / 8.62 | 0.798 |
| window | 552 | against the mill. | 10.03 / 9.97 | 8.7 / 8.62 | 0.79 |
| window | 552 | Dutch painters of the seventeenth century made the | 10.29 / 10.12 | 9.01 / 8.78 | 0.802 |
| window | 552 | sky a subject in its own right. Few made it carry as | 10.69 / 10.18 | 9.41 / 8.86 | 0.82 |
| window | 552 | much of a picture as this. | 10.27 / 10.12 | 8.94 / 8.78 | 0.801 |
| window | 552 | Weather | 9.69 / 9.59 | 8.6 / 8.38 | 0.775 |
| window | 552 | Heaped cumulus, sun breaking through | 9.44 / 9.19 | 8.29 / 7.99 | 0.763 |
| window | 552 | Artist | 10.03 / 9.92 | 8.93 / 8.83 | 0.79 |
| window | 552 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 9.59 / 9.27 | 8.38 / 8.07 | 0.77 |
| window | 552 | Date | 9.93 / 9.92 | 8.84 / 8.82 | 0.786 |
| window | 552 | c. 1668–70 | 9.53 / 9.36 | 8.32 / 8.22 | 0.767 |
| window | 552 | Medium | 10.09 / 10.01 | 8.99 / 8.84 | 0.793 |
| window | 552 | Oil on canvas | 9.78 / 9.7 | 8.66 / 8.58 | 0.779 |
| window | 552 | Size | 10.03 / 10.03 | 8.93 / 8.93 | 0.79 |
| window | 552 | 83 × 101 cm | 10.01 / 9.85 | 8.9 / 8.75 | 0.789 |
| window | 552 | Collection | 10.02 / 9.92 | 8.93 / 8.77 | 0.79 |
| window | 552 | Rijksmuseum, Amsterdam | 9.68 / 9.57 | 8.57 / 8.37 | 0.774 |
| window | 552 | Credit | 10.01 / 9.93 | 8.9 / 8.84 | 0.789 |
| window | 552 | On loan from the City of Amsterdam (A. van | 9.91 / 9.77 | 8.76 / 8.6 | 0.785 |
| window | 552 | der Hoop Bequest) | 10.08 / 9.98 | 8.99 / 8.9 | 0.792 |
| window | 552 | Number | 10.3 / 10.14 | 9.28 / 9.04 | 0.803 |
| window | 552 | SK-C-211 | 10.67 / 10.58 | 9.63 / 9.54 | 0.819 |
| window | 552 | Photograph: Rijksmuseum, Amsterdam , open access, public | 11.56 / 11.48 | 10.4 / 10.32 | 0.859 |
| window | 552 | domain. | 11.47 / 11.38 | 10.3 / 10.21 | 0.855 |

### GPU tier · light · clearing · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 10.16 / 10.08 | 8.93 / 8.85 | 0.796 |
| window | 0 | Room 3 of 8 | 10.6 / 10.45 | 9.41 / 9.26 | 0.816 |
| window | 0 | Clearing (large) | 10.14 / 10.05 | 8.95 / 8.84 | 0.795 |
| window | 0 | View from Mount Holyoke, (large) | 10.19 / 10.04 | 8.99 / 8.8 | 0.798 |
| window | 0 | Northampton, Massachusetts, (large) | 10.19 / 10.02 | 8.99 / 8.77 | 0.798 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 10.32 / 10.04 | 9.08 / 8.8 | 0.804 |
| window | 0 | Thomas Cole | 10.15 / 9.91 | 8.91 / 8.67 | 0.796 |
| window | 0 | American, born England, 1801–1848 · 1836 | 10.27 / 9.98 | 9.04 / 8.75 | 0.801 |
| window | 0 | The whole work. The outline marks the part around you. | 10.17 / 10 | 8.94 / 8.76 | 0.797 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 9.96 / 9.9 | 8.74 / 8.66 | 0.787 |
| window | 0 | valley. On the left it still hangs over wild, broken trees, | 9.92 / 9.88 | 8.68 / 8.64 | 0.785 |
| window | 0 | and rain falls in grey veils across the hills. On the right | 9.98 / 9.81 | 8.74 / 8.56 | 0.788 |
| window | 0 | the air has cleared over cleared land: fields, farms | 9.96 / 9.8 | 8.73 / 8.56 | 0.787 |
| window | 0 | and the river’s great loop. | 9.94 / 9.82 | 8.69 / 8.59 | 0.786 |
| Rooms | 0 | 3 | 9.71 / 9.65 | 8.86 / 8.79 | 0.775 |
| Rooms | 0 | / 8 | 10.05 / 9.8 | 9.06 / 8.96 | 0.791 |
| Audio guide | 0 | Audio guide | 9.67 / 9.3 | 8.69 / 8.42 | 0.774 |
| Audio guide | 0 | About 0:50 | 9.58 / 9.47 | 8.64 / 8.56 | 0.769 |
| Rooms | 0 | icon: Previous room: Cloud | 9.51 / 9.48 | 8.6 / 8.52 | 0.766 |
| Rooms | 0 | icon: Next room: Thunder | 9.54 / 9.49 | 8.6 / 8.52 | 0.768 |
| Audio guide | 0 | icon: Play the audio guide | 9.71 / 9.55 | 8.74 / 8.65 | 0.776 |
| window | 608 | Cole divided the picture along a diagonal, and the | 10.25 / 10.11 | 9.07 / 8.9 | 0.801 |
| window | 608 | weather does the dividing. He painted it for the 1836 | 10.25 / 10.1 | 9.01 / 8.9 | 0.801 |
| window | 608 | annual exhibition of the National Academy of Design, | 10.25 / 10.05 | 9.01 / 8.87 | 0.801 |
| window | 608 | calling the view from Mount Holyoke “about the finest | 10.25 / 10.05 | 9.01 / 8.81 | 0.801 |
| window | 608 | scene I have in my sketchbook.” | 10.17 / 10.02 | 8.95 / 8.76 | 0.797 |
| window | 608 | Look for the painter himself near the bottom of the | 10.32 / 10.04 | 9.08 / 8.8 | 0.804 |
| window | 608 | canvas: a small figure at an easel among the rocks, | 10.31 / 10.06 | 9.13 / 8.89 | 0.803 |
| window | 608 | turning back toward us. | 10.2 / 9.95 | 9 / 8.72 | 0.798 |
| window | 608 | Weather | 9.25 / 9.18 | 8.13 / 8.05 | 0.754 |
| window | 608 | Thunderstorm passing, sun on the valley | 9.48 / 9.3 | 8.36 / 8.22 | 0.765 |
| window | 608 | Artist | 9.47 / 9.36 | 8.34 / 8.28 | 0.764 |
| window | 608 | Thomas Cole ( American, born England, | 9.47 / 9.24 | 8.33 / 8.16 | 0.764 |
| window | 608 | 1801–1848 ) | 9.38 / 9.18 | 8.26 / 8.04 | 0.76 |
| window | 608 | Date | 9.58 / 9.56 | 8.46 / 8.43 | 0.769 |
| window | 608 | 1836 | 9.2 / 9.18 | 8.12 / 8.05 | 0.751 |
| window | 608 | Medium | 9.33 / 9.32 | 8.25 / 8.19 | 0.758 |
| window | 608 | Oil on canvas | 9.17 / 9.08 | 8.05 / 7.98 | 0.75 |
| window | 608 | Size | 9.11 / 9.06 | 7.99 / 7.93 | 0.747 |
| window | 608 | 130.8 × 193 cm | 9.09 / 9.07 | 8.02 / 7.95 | 0.746 |
| window | 608 | Collection | 9.08 / 9.02 | 7.97 / 7.91 | 0.746 |
| window | 608 | The Metropolitan Museum of Art, New York | 9.01 / 8.98 | 7.9 / 7.86 | 0.742 |
| window | 608 | Credit | 9.14 / 9.11 | 8.06 / 7.99 | 0.749 |
| window | 608 | Gift of Mrs. Russell Sage, 1908 | 8.99 / 8.93 | 7.87 / 7.8 | 0.741 |
| window | 608 | Number | 9.12 / 9.04 | 8.01 / 7.93 | 0.748 |
| window | 608 | 08.228 | 8.9 / 8.86 | 7.77 / 7.75 | 0.737 |
| window | 608 | Photograph: The Metropolitan Museum of Art, New York , open | 9.96 / 9.86 | 8.73 / 8.63 | 0.787 |
| window | 608 | access, public domain. | 9.85 / 9.81 | 8.62 / 8.56 | 0.782 |

### GPU tier · light · thunder · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.94 / 9.87 | 8.72 / 8.64 | 0.786 |
| window | 0 | Room 4 of 8 | 9.94 / 9.86 | 8.72 / 8.64 | 0.786 |
| window | 0 | Thunder (large) | 10.03 / 10.02 | 8.8 / 8.79 | 0.79 |
| window | 0 | Approaching Thunder Storm (large) | 10.03 / 10.03 | 8.85 / 8.8 | 0.79 |
| window | 0 | Martin Johnson Heade | 10.12 / 10.03 | 8.87 / 8.8 | 0.794 |
| window | 0 | American, 1819–1904 · 1859 | 10.38 / 10.04 | 9.21 / 8.87 | 0.806 |
| window | 0 | The whole work. The outline marks the part around you. | 10.19 / 10.11 | 8.96 / 8.87 | 0.798 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 10.51 / 10.23 | 9.33 / 9 | 0.812 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 10.53 / 10.25 | 9.35 / 9.01 | 0.813 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 9.88 / 9.81 | 8.65 / 8.57 | 0.783 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 9.8 / 9.77 | 8.56 / 8.54 | 0.78 |
| window | 0 | rower pulls for shore; a white sail stands out against | 9.8 / 9.77 | 8.56 / 8.54 | 0.78 |
| window | 0 | the dark. | 9.77 / 9.69 | 8.56 / 8.48 | 0.778 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 9.81 / 9.79 | 8.59 / 8.56 | 0.78 |
| window | 0 | before such a storm, and that is what the picture | 10.08 / 9.8 | 8.86 / 8.57 | 0.792 |
| Rooms | 0 | 4 | 10.23 / 10.04 | 9.3 / 9.16 | 0.798 |
| Rooms | 0 | / 8 | 10.67 / 10.31 | 9.69 / 9.39 | 0.817 |
| Audio guide | 0 | Audio guide | 11.72 / 11.3 | 10.66 / 10.3 | 0.864 |
| Audio guide | 0 | About 0:53 | 11.6 / 10.84 | 10.56 / 9.76 | 0.858 |
| Rooms | 0 | icon: Previous room: Clearing | 10.33 / 10.02 | 9.42 / 9.21 | 0.803 |
| Rooms | 0 | icon: Next room: Rain | 11.77 / 11.33 | 10.77 / 10.41 | 0.865 |
| Audio guide | 0 | icon: Play the audio guide | 10.69 / 10.24 | 9.71 / 9.32 | 0.819 |
| window | 618 | holds: not the storm itself but the minute before it. | 10.03 / 10.03 | 8.8 / 8.79 | 0.79 |
| window | 618 | Painted two years before the Civil War, it has often | 10.03 / 10.03 | 8.8 / 8.8 | 0.79 |
| window | 618 | been read as a picture of a country waiting for | 10.03 / 10.03 | 8.85 / 8.8 | 0.79 |
| window | 618 | something to break. Heade based it on a storm | 10.11 / 10.03 | 8.87 / 8.8 | 0.794 |
| window | 618 | he had watched from Prudence Island, in the bay, | 10.3 / 10.11 | 9.11 / 8.87 | 0.802 |
| window | 618 | around 1858. | 10.2 / 10.04 | 8.96 / 8.87 | 0.798 |
| window | 618 | Weather | 9.66 / 9.59 | 8.55 / 8.47 | 0.773 |
| window | 618 | Thunderstorm approaching over still water | 9.75 / 9.68 | 8.64 / 8.56 | 0.778 |
| window | 618 | Artist | 9.66 / 9.51 | 8.55 / 8.41 | 0.773 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 9.68 / 9.68 | 8.62 / 8.56 | 0.774 |
| window | 618 | 1819–1904 ) | 9.68 / 9.67 | 8.56 / 8.56 | 0.774 |
| window | 618 | Date | 9.66 / 9.51 | 8.55 / 8.4 | 0.773 |
| window | 618 | 1859 | 9.67 / 9.61 | 8.56 / 8.56 | 0.774 |
| window | 618 | Medium | 9.43 / 9.35 | 8.37 / 8.23 | 0.762 |
| window | 618 | Oil on canvas | 9.29 / 9.19 | 8.22 / 8.13 | 0.756 |
| window | 618 | Size | 9.29 / 9.21 | 8.23 / 8.14 | 0.755 |
| window | 618 | 71.1 × 111.8 cm | 9.34 / 9.27 | 8.22 / 8.15 | 0.758 |
| window | 618 | Collection | 9.85 / 9.77 | 8.78 / 8.65 | 0.781 |
| window | 618 | The Metropolitan Museum of Art, New York | 9.58 / 9.32 | 8.46 / 8.27 | 0.769 |
| window | 618 | Credit | 8.96 / 8.88 | 7.86 / 7.78 | 0.74 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 8.9 / 8.88 | 7.8 / 7.78 | 0.737 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 8.88 / 8.86 | 7.78 / 7.78 | 0.736 |
| window | 618 | 1975 | 8.86 / 8.86 | 7.78 / 7.76 | 0.735 |
| window | 618 | Number | 8.86 / 8.78 | 7.77 / 7.68 | 0.735 |
| window | 618 | 1975.160 | 8.88 / 8.88 | 7.77 / 7.77 | 0.736 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 9.93 / 9.8 | 8.72 / 8.57 | 0.786 |
| window | 618 | access, public domain. | 10.11 / 9.72 | 8.93 / 8.49 | 0.794 |

### GPU tier · light · rain · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 13.04 / 11.48 | 12.04 / 10.18 | 0.922 |
| window | 0 | Room 5 of 8 | 11.5 / 11.43 | 10.19 / 10.11 | 0.856 |
| window | 0 | Rain (large) | 12 / 11.54 | 10.85 / 10.24 | 0.878 |
| window | 0 | Paris Street; Rainy Day (large) | 11.83 / 11.36 | 10.59 / 10.03 | 0.871 |
| window | 0 | Gustave Caillebotte | 11.74 / 11.06 | 10.43 / 9.67 | 0.866 |
| window | 0 | French, 1848–1894 · 1877 | 11.47 / 11.11 | 10.15 / 9.72 | 0.855 |
| window | 0 | The whole work. The outline marks the part around you. | 11.72 / 10.23 | 10.48 / 8.71 | 0.866 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 12.18 / 10.74 | 11 / 9.29 | 0.885 |
| window | 0 | paints the rain through what it does: the paving | 12.2 / 10.76 | 10.96 / 9.31 | 0.887 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 12.12 / 11.03 | 10.94 / 9.64 | 0.883 |
| window | 0 | everyone carries an umbrella, the newly invented | 12.1 / 10.94 | 10.86 / 9.54 | 0.882 |
| window | 0 | retractable kind. | 11.54 / 10.48 | 10.23 / 8.96 | 0.858 |
| window | 0 | The place is a busy intersection a short walk from the | 11.9 / 10.72 | 10.66 / 9.27 | 0.874 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 11.83 / 10.8 | 10.58 / 9.34 | 0.871 |
| window | 0 | and uniform stone façades. A green lamppost splits | 11.83 / 10.96 | 10.58 / 9.52 | 0.87 |
| Rooms | 0 | 5 | 10.4 / 10.28 | 9.39 / 9.33 | 0.807 |
| Rooms | 0 | / 8 | 10.69 / 10.48 | 9.66 / 9.48 | 0.82 |
| Audio guide | 0 | Audio guide | 11.83 / 11.59 | 10.78 / 10.58 | 0.871 |
| Audio guide | 0 | About 0:46 | 11.7 / 11.28 | 10.62 / 10.31 | 0.865 |
| Rooms | 0 | icon: Previous room: Thunder | 10.23 / 10.14 | 9.16 / 9.07 | 0.8 |
| Rooms | 0 | icon: Next room: Wind | 11.64 / 11.03 | 10.59 / 10.16 | 0.862 |
| Audio guide | 0 | icon: Play the audio guide | 11.5 / 11.32 | 10.36 / 10.26 | 0.856 |
| window | 578 | painter’s home, in a Paris rebuilt with wide streets | 12.04 / 11.38 | 10.81 / 10.04 | 0.88 |
| window | 578 | and uniform stone façades. A green lamppost splits | 11.84 / 11.44 | 10.61 / 10.12 | 0.871 |
| window | 578 | the canvas in two; the couple on the right walk | 11.92 / 11.46 | 10.68 / 10.14 | 0.874 |
| window | 578 | straight toward us, looking at something beyond | 11.82 / 11.38 | 10.57 / 10.06 | 0.87 |
| window | 578 | the frame. | 11.45 / 11.24 | 10.13 / 9.84 | 0.854 |
| window | 578 | Nearly life-size, it is Caillebotte’s largest painting. He | 11.59 / 11.26 | 10.28 / 9.9 | 0.86 |
| window | 578 | showed it at the third Impressionist exhibition in 1877, | 11.56 / 11.46 | 10.25 / 10.13 | 0.859 |
| window | 578 | the year he made it. | 11.72 / 11.48 | 10.47 / 10.2 | 0.866 |
| window | 578 | Weather | 10.43 / 10.25 | 9.28 / 8.99 | 0.808 |
| window | 578 | Light rain, overcast | 9.95 / 9.84 | 8.68 / 8.57 | 0.786 |
| window | 578 | Artist | 9.43 / 9.33 | 8.03 / 7.93 | 0.762 |
| window | 578 | Gustave Caillebotte ( French, 1848–1894 ) | 10.12 / 9.38 | 8.86 / 7.99 | 0.794 |
| window | 578 | Date | 9.1 / 9.01 | 7.65 / 7.55 | 0.747 |
| window | 578 | 1877 | 10.39 / 10.1 | 9.2 / 8.85 | 0.807 |
| window | 578 | Medium | 9.27 / 8.99 | 7.84 / 7.52 | 0.755 |
| window | 578 | Oil on canvas | 10.89 / 10.46 | 9.77 / 9.29 | 0.829 |
| window | 578 | Size | 9.17 / 9 | 7.73 / 7.59 | 0.75 |
| window | 578 | 212.2 × 276.2 cm | 11.1 / 10.79 | 9.99 / 9.65 | 0.839 |
| window | 578 | Collection | 10.92 / 10.91 | 9.8 / 9.71 | 0.831 |
| window | 578 | The Art Institute of Chicago | 11.04 / 10.95 | 9.92 / 9.76 | 0.836 |
| window | 578 | Credit | 9.6 / 9.18 | 8.22 / 7.74 | 0.771 |
| window | 578 | Charles H. and Mary F. S. Worcester | 11.03 / 10.94 | 9.9 / 9.75 | 0.835 |
| window | 578 | Number | 9.64 / 9.46 | 8.3 / 8.09 | 0.772 |
| window | 578 | 1964.336 | 10.81 / 10.72 | 9.69 / 9.6 | 0.826 |
| window | 578 | Photograph: The Art Institute of Chicago , open access, public | 11.83 / 10.88 | 10.59 / 9.42 | 0.871 |
| window | 578 | domain. | 10.88 / 10.63 | 9.42 / 9.18 | 0.829 |

### GPU tier · light · wind · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.98 / 11.23 | 10.81 / 9.97 | 0.877 |
| window | 0 | Room 6 of 8 | 12.22 / 11.98 | 11.12 / 10.81 | 0.887 |
| window | 0 | Wind (large) | 11.47 / 11.09 | 10.23 / 9.78 | 0.855 |
| window | 0 | Wheat Field with Cypresses (large) | 11.97 / 11.85 | 10.81 / 10.61 | 0.876 |
| window | 0 | Vincent van Gogh | 11.86 / 11.67 | 10.69 / 10.48 | 0.872 |
| window | 0 | Dutch, 1853–1890 · 1889 | 11.64 / 11.56 | 10.41 / 10.35 | 0.862 |
| window | 0 | The whole work. The outline marks the part around you. | 11.33 / 11.21 | 10.04 / 9.9 | 0.849 |
| window | 0 | Everything in this field is moving the same way. The | 11.44 / 11.28 | 10.19 / 10 | 0.854 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 11.4 / 10.8 | 10.14 / 9.47 | 0.852 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 10.98 / 10.36 | 9.65 / 8.94 | 0.833 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 10.59 / 10.32 | 9.19 / 8.89 | 0.815 |
| window | 0 | the paint on so heavily that the brushstrokes | 10.68 / 10.44 | 9.28 / 9.02 | 0.819 |
| window | 0 | themselves take the shape of the wind. | 10.77 / 10.52 | 9.41 / 9.11 | 0.824 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 10.73 / 10.3 | 9.35 / 8.89 | 0.822 |
| window | 0 | Saint-Rémy in Provence, where he was a patient at the | 10.58 / 10.25 | 9.19 / 8.83 | 0.815 |
| Rooms | 0 | 6 | 11.06 / 10.86 | 10.09 / 9.92 | 0.835 |
| Rooms | 0 | / 8 | 11.12 / 10.85 | 10.1 / 9.91 | 0.838 |
| Audio guide | 0 | Audio guide | 10.74 / 10.49 | 9.76 / 9.51 | 0.821 |
| Audio guide | 0 | About 0:51 | 10.64 / 10.29 | 9.65 / 9.41 | 0.817 |
| Rooms | 0 | icon: Previous room: Rain | 10.83 / 10.5 | 9.81 / 9.57 | 0.825 |
| Rooms | 0 | icon: Next room: Gale | 11.21 / 10.8 | 10.14 / 9.86 | 0.842 |
| Audio guide | 0 | icon: Play the audio guide | 10.62 / 10.37 | 9.61 / 9.45 | 0.816 |
| window | 578 | He painted it in late June or early July 1889 at Saint-Rémy | 12.15 / 11.12 | 11.03 / 9.8 | 0.884 |
| window | 578 | Saint-Rémy in Provence, where he was a patient at the | 12.2 / 11.12 | 11.04 / 9.8 | 0.887 |
| window | 578 | asylum of Saint-Paul-de-Mausole, working outdoors | 12.04 / 11.65 | 10.9 / 10.41 | 0.88 |
| window | 578 | in front of the motif. | 12.09 / 11.99 | 10.93 / 10.82 | 0.882 |
| window | 578 | He counted it among his best summer canvases, and | 11.77 / 11.66 | 10.59 / 10.46 | 0.868 |
| window | 578 | that September made two studio versions of it: one | 11.6 / 11.51 | 10.37 / 10.27 | 0.86 |
| window | 578 | now in the National Gallery, London, the other a | 11.54 / 11.33 | 10.3 / 10.06 | 0.858 |
| window | 578 | smaller copy for his mother and sister. | 11.44 / 11.18 | 10.17 / 9.91 | 0.853 |
| window | 578 | Weather | 10.4 / 10.37 | 9.26 / 9.23 | 0.807 |
| window | 578 | Summer wind, fast cloud | 10.27 / 10.19 | 9.12 / 9.01 | 0.801 |
| window | 578 | Artist | 10.43 / 10.38 | 9.32 / 9.2 | 0.808 |
| window | 578 | Vincent van Gogh ( Dutch, 1853–1890 ) | 10.27 / 10.16 | 9.08 / 8.97 | 0.801 |
| window | 578 | Date | 10.13 / 10.09 | 8.99 / 8.91 | 0.795 |
| window | 578 | 1889 | 10.16 / 10.15 | 9.02 / 8.96 | 0.796 |
| window | 578 | Medium | 10.3 / 10.28 | 9.17 / 9.1 | 0.803 |
| window | 578 | Oil on canvas | 10.25 / 10.18 | 9.11 / 9.01 | 0.8 |
| window | 578 | Size | 10.44 / 10.39 | 9.3 / 9.27 | 0.809 |
| window | 578 | 73.2 × 93.4 cm | 10.43 / 10.36 | 9.29 / 9.21 | 0.808 |
| window | 578 | Collection | 10.4 / 10.38 | 9.26 / 9.24 | 0.807 |
| window | 578 | The Metropolitan Museum of Art, New York | 9.73 / 9.47 | 8.51 / 8.19 | 0.776 |
| window | 578 | Credit | 10.38 / 10.34 | 9.26 / 9.21 | 0.806 |
| window | 578 | Purchase, The Annenberg Foundation Gift, | 9.49 / 9.38 | 8.21 / 8.05 | 0.765 |
| window | 578 | 1993 | 9.6 / 9.45 | 8.34 / 8.19 | 0.77 |
| window | 578 | Number | 10.36 / 10.19 | 9.21 / 9.03 | 0.805 |
| window | 578 | 1993.132 | 9.48 / 9.39 | 8.22 / 8.1 | 0.765 |
| window | 578 | Photograph: The Metropolitan Museum of Art, New York , open | 10.65 / 10.25 | 9.26 / 8.82 | 0.818 |
| window | 578 | access, public domain. | 10.72 / 10.22 | 9.34 / 8.76 | 0.821 |

### GPU tier · light · gale · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.88 / 11.55 | 10.64 / 10.31 | 0.873 |
| window | 0 | Room 7 of 8 | 12.81 / 11.54 | 11.78 / 10.29 | 0.912 |
| window | 0 | Gale (large) | 11.9 / 11.36 | 10.69 / 10.03 | 0.873 |
| window | 0 | Northeaster (large) | 12.22 / 11.52 | 11.05 / 10.19 | 0.887 |
| window | 0 | Winslow Homer | 12.32 / 11.82 | 11.15 / 10.57 | 0.892 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 12.61 / 12.25 | 11.46 / 11.08 | 0.904 |
| window | 0 | The whole work. The outline marks the part around you. | 11.68 / 11.33 | 10.4 / 10 | 0.864 |
| window | 0 | A northeaster is a winter storm that drives in off the | 11.73 / 11.4 | 10.47 / 10.07 | 0.866 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 11.58 / 11.33 | 10.28 / 10.01 | 0.86 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 11.58 / 11.14 | 10.27 / 9.76 | 0.859 |
| window | 0 | lived and painted for the last decades of his life. | 10.81 / 10.24 | 9.37 / 8.67 | 0.826 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 9.9 / 9.77 | 8.25 / 8.12 | 0.784 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 9.88 / 9.75 | 8.24 / 8.11 | 0.783 |
| window | 0 | lower left. By 1900 he had painted them out and | 9.85 / 9.76 | 8.2 / 8.1 | 0.782 |
| window | 0 | raised a much larger column of spray. What is left is | 9.88 / 9.82 | 8.24 / 8.17 | 0.783 |
| Rooms | 0 | 7 | 9.83 / 9.69 | 8.87 / 8.78 | 0.781 |
| Rooms | 0 | / 8 | 9.88 / 9.8 | 8.95 / 8.89 | 0.783 |
| Audio guide | 0 | Audio guide | 9.64 / 9.54 | 8.73 / 8.58 | 0.773 |
| Audio guide | 0 | About 0:50 | 9.78 / 9.64 | 8.81 / 8.73 | 0.779 |
| Rooms | 0 | icon: Previous room: Wind | 9.58 / 9.47 | 8.64 / 8.49 | 0.769 |
| Rooms | 0 | icon: Next room: Fog | 9.89 / 9.75 | 8.9 / 8.8 | 0.784 |
| Audio guide | 0 | icon: Play the audio guide | 10.19 / 10.08 | 9.2 / 9.1 | 0.798 |
| window | 506 | When he first exhibited this canvas in 1895, two men | 13.36 / 11.88 | 12.41 / 10.62 | 0.935 |
| window | 506 | in foul-weather gear crouched on the rocks at the | 13.24 / 11.63 | 12.23 / 10.37 | 0.93 |
| window | 506 | lower left. By 1900 he had painted them out and | 13.05 / 11.64 | 12.04 / 10.38 | 0.922 |
| window | 506 | raised a much larger column of spray. What is left is | 13 / 11.98 | 11.96 / 10.74 | 0.92 |
| window | 506 | rock, water and air: the dark ledge, the green body of | 12.74 / 12.19 | 11.71 / 10.96 | 0.909 |
| window | 506 | the wave and the white burst where they meet. | 12.64 / 12.34 | 11.55 / 11.17 | 0.905 |
| window | 506 | A critic in 1901 praised it for “great natural spaces | 12.81 / 12.26 | 11.71 / 11.09 | 0.912 |
| window | 506 | unmarked by the presence of puny man.” | 12.81 / 12.06 | 11.71 / 10.81 | 0.912 |
| window | 506 | Weather | 10.95 / 10.83 | 9.82 / 9.64 | 0.832 |
| window | 506 | Winter northeaster off the Atlantic | 11.25 / 11.08 | 10.23 / 9.95 | 0.845 |
| window | 506 | Artist | 11.05 / 10.86 | 9.87 / 9.67 | 0.836 |
| window | 506 | Winslow Homer ( American, 1836–1910 ) | 10.82 / 10.45 | 9.69 / 9.27 | 0.826 |
| window | 506 | Date | 10.92 / 10.78 | 9.74 / 9.65 | 0.83 |
| window | 506 | 1895; reworked by 1901 | 10.59 / 10.27 | 9.4 / 9.03 | 0.815 |
| window | 506 | Medium | 10.83 / 10.69 | 9.67 / 9.55 | 0.826 |
| window | 506 | Oil on canvas | 10.42 / 10.39 | 9.24 / 9.19 | 0.808 |
| window | 506 | Size | 10.19 / 10.09 | 8.93 / 8.85 | 0.798 |
| window | 506 | 87.6 × 127 cm | 10.35 / 10.34 | 9.16 / 9.1 | 0.805 |
| window | 506 | Collection | 10.03 / 9.77 | 8.77 / 8.45 | 0.79 |
| window | 506 | The Metropolitan Museum of Art, New York | 10.53 / 9.87 | 9.35 / 8.59 | 0.813 |
| window | 506 | Credit | 8.96 / 8.88 | 7.51 / 7.4 | 0.74 |
| window | 506 | Gift of George A. Hearn, 1910 | 9.07 / 8.94 | 7.6 / 7.46 | 0.745 |
| window | 506 | Number | 8.87 / 8.86 | 7.37 / 7.36 | 0.735 |
| window | 506 | 10.64.5 | 8.94 / 8.88 | 7.44 / 7.37 | 0.739 |
| window | 506 | Photograph: The Metropolitan Museum of Art, New York , open | 9.88 / 9.82 | 8.24 / 8.17 | 0.783 |
| window | 506 | access, public domain. | 9.84 / 9.78 | 8.24 / 8.13 | 0.781 |

### GPU tier · light · fog · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.09 / 11.02 | 9.87 / 9.86 | 0.838 |
| window | 0 | Room 8 of 8 | 11.27 / 11.21 | 10.06 / 9.99 | 0.846 |
| window | 0 | Fog (large) | 11.11 / 11.02 | 9.89 / 9.8 | 0.839 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 11.15 / 11.02 | 9.95 / 9.8 | 0.841 |
| window | 0 | Claude Monet | 10.91 / 10.81 | 9.64 / 9.54 | 0.83 |
| window | 0 | French, 1840–1926 · 1900 | 10.95 / 10.72 | 9.74 / 9.48 | 0.832 |
| window | 0 | The whole work. The outline marks the part around you. | 10.22 / 10.16 | 8.93 / 8.87 | 0.799 |
| window | 0 | Without the fog, Monet once remarked, London | 10.19 / 10.14 | 8.89 / 8.82 | 0.797 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 10.18 / 10.12 | 8.88 / 8.81 | 0.797 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 10.19 / 10.07 | 8.88 / 8.72 | 0.797 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 10.22 / 10.02 | 8.94 / 8.67 | 0.799 |
| window | 0 | he came to paint it. | 10.86 / 10.76 | 9.65 / 9.54 | 0.828 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 10.21 / 10.04 | 8.9 / 8.7 | 0.798 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 10.19 / 10.04 | 8.89 / 8.73 | 0.797 |
| window | 0 | Charing Cross Bridge later in the day. Here the bridge | 10.2 / 10.09 | 8.91 / 8.8 | 0.798 |
| Rooms | 0 | 8 | 10.3 / 10.1 | 9.32 / 9.16 | 0.803 |
| Rooms | 0 | / 8 | 10.4 / 10.32 | 9.4 / 9.3 | 0.807 |
| Audio guide | 0 | Audio guide | 10.03 / 9.93 | 9.09 / 9 | 0.79 |
| Audio guide | 0 | About 0:50 | 10.08 / 10 | 9.13 / 9.05 | 0.792 |
| Rooms | 0 | icon: Previous room: Gale | 10.5 / 10.4 | 9.52 / 9.44 | 0.812 |
| Audio guide | 0 | icon: Play the audio guide | 10.02 / 9.97 | 9.05 / 9.02 | 0.789 |
| window | 532 | He painted Waterloo Bridge in the mornings from his | 11.12 / 11.1 | 9.91 / 9.89 | 0.839 |
| window | 532 | fifth-floor window at the Savoy Hotel, moving on to | 11.12 / 11.03 | 9.91 / 9.88 | 0.839 |
| window | 532 | Charing Cross Bridge later in the day. Here the bridge | 11.13 / 11.02 | 9.93 / 9.8 | 0.84 |
| window | 532 | is a dark band of arches, and the city behind it is only | 11.17 / 11.01 | 10.01 / 9.78 | 0.842 |
| window | 532 | chimneys and towers in the haze. | 11.13 / 10.82 | 9.91 / 9.6 | 0.84 |
| window | 532 | He finished the London pictures in his studio at | 11.06 / 10.71 | 9.85 / 9.49 | 0.837 |
| window | 532 | Giverny, and would not release any of them until he | 10.93 / 10.76 | 9.71 / 9.49 | 0.831 |
| window | 532 | was satisfied with the series as a whole. | 10.82 / 10.73 | 9.58 / 9.49 | 0.826 |
| window | 532 | Weather | 9.86 / 9.8 | 8.75 / 8.68 | 0.783 |
| window | 532 | Winter fog and coal smoke | 9.82 / 9.75 | 8.7 / 8.63 | 0.781 |
| window | 532 | Artist | 9.61 / 9.54 | 8.5 / 8.32 | 0.771 |
| window | 532 | Claude Monet ( French, 1840–1926 ) | 9.49 / 9.37 | 8.32 / 8.16 | 0.765 |
| window | 532 | Date | 9.31 / 9.24 | 8.07 / 8.06 | 0.756 |
| window | 532 | 1900 | 9.38 / 9.31 | 8.16 / 8.14 | 0.76 |
| window | 532 | Medium | 9.23 / 9.21 | 8.07 / 8.04 | 0.752 |
| window | 532 | Oil on canvas | 9.34 / 9.32 | 8.13 / 8.11 | 0.758 |
| window | 532 | Size | 9.26 / 9.24 | 8.08 / 8.08 | 0.754 |
| window | 532 | 65.4 × 92.6 cm | 9.27 / 9.19 | 8.11 / 8.03 | 0.755 |
| window | 532 | Collection | 9.49 / 9.27 | 8.28 / 8.12 | 0.765 |
| window | 532 | The Art Institute of Chicago | 9.18 / 9.13 | 8.01 / 7.92 | 0.75 |
| window | 532 | Credit | 9.83 / 9.67 | 8.72 / 8.52 | 0.781 |
| window | 532 | Gift of Mrs. Mortimer B. Harris | 9.28 / 9.11 | 8.12 / 7.9 | 0.755 |
| window | 532 | Number | 9.78 / 9.62 | 8.61 / 8.53 | 0.779 |
| window | 532 | 1984.1173 | 9.73 / 9.67 | 8.62 / 8.55 | 0.776 |
| window | 532 | Photograph: The Art Institute of Chicago , open access, public | 10.23 / 10.07 | 8.94 / 8.79 | 0.799 |
| window | 532 | domain. | 10.8 / 10.71 | 9.53 / 9.43 | 0.825 |

### GPU tier · light · rooms view · active (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 12.42 | 9.93 | 10.08 | 9.87 | 11.48 | 11.23 | 11.55 | 11.02 |
| 8 rooms | 13.72 | 10.03 | 10.53 | 9.86 | 11.43 | 11.97 | 11.45 | 11.21 |
| Eight skies, 1608–1900 | 12.44 | 9.89 | 10.1 | 10.03 | 11.41 | 11.11 | 11.79 | 11.1 |
| For most of the history of European painting the sky | 11.99 | 9.95 | 10.05 | 10.03 | 11.45 | 11.87 | 11.72 | 11.02 |
| was the back wall of the picture. This exhibition | 12.08 | 10.03 | 10.02 | 10.03 | 11.34 | 11.74 | 11.98 | 10.95 |
| follows it becoming the subject: eight rooms, each | 12.25 | 10.03 | 10.02 | 10.04 | 11.08 | 11.61 | 12.15 | 10.83 |
| holding one work, from a Dutch winter in the Little Ice | 12.43 | 10.12 | 10.06 | 10.12 | 11.38 | 11.43 | 12.36 | 10.72 |
| Age to a London fog that was largely coal smoke. | 12.3 | 10.2 | 10.06 | 10.3 | 11.48 | 11.26 | 12.36 | 10.71 |
| Each work fills the room. Its label sits beside it, and | 11.46 | 10.12 | 10 | 10.62 | 10.93 | 11.17 | 12.07 | 10.73 |
| the audio guide reads the label aloud in your | 10.88 | 10.12 | 10.08 | 10.62 | 11.04 | 11.18 | 11.99 | 10.74 |
| browser’s own voice. | 10.54 | 10.12 | 10.1 | 10.56 | 10.94 | 11.32 | 11.87 | 10.77 |
| Rooms | 10.7 | 11.05 | 10.31 | 10.53 | 10.01 | 11.19 | 11.94 | 10.48 |
| 01 · Frost | 9.1 | 10.61 | 10.11 | 10.2 | 11.23 | 11.19 | 11.65 | 10.21 |
| · you are here | 9.58 | 9.23 | 8.59 | 8.7 | 9.91 | 9.7 | 10.92 | 8.88 |
| Winter Landscape with Ice Skaters | 9.44 | 10.28 | 10.11 | 10.04 | 11.45 | 11.23 | 11.33 | 10.16 |
| Hendrick Avercamp , c. 1608 | 9.23 | 10.44 | 10.01 | 10.21 | 11.45 | 11.34 | 11.33 | 10.16 |
| 02 · Cloud | 11.39 | 9.36 | 9.98 | 10.26 | 11.95 | 11.34 | 11.4 | 10.17 |
| The Windmill at Wijk bij Duurstede | 11.34 | 9.15 | 9.91 | 9.81 | 11.94 | 10.3 | 11.22 | 10.06 |
| Jacob van Ruisdael , c. 1668–70 | 11.01 | 9.32 | 9.9 | 9.77 | 12.01 | 10.36 | 10.45 | 10.02 |
| 03 · Clearing | 11 | 11.13 | 8.46 | 9.79 | 11.72 | 10.49 | 9.77 | 10.73 |
| View from Mount Holyoke, Northampton, | 10.52 | 11.47 | 8.49 | 9.79 | 11.79 | 10.48 | 9.77 | 10.02 |
| Massachusetts, after a Thunderstorm—The | 10.45 | 11.72 | 8.52 | 9.79 | 11.79 | 10.36 | 9.82 | 10.03 |
| Oxbow | 10.3 | 11.61 | 8.55 | 9.81 | 11.68 | 10.19 | 9.81 | 10.73 |
| Thomas Cole , 1836 | 10.35 | 11.41 | 8.55 | 10.04 | 11.68 | 10.19 | 9.79 | 10.28 |
| 04 · Thunder | 12.54 | 9.95 | 10.14 | 8.7 | 12.95 | 11.96 | 11.98 | 11.1 |
| Approaching Thunder Storm | 12.45 | 10.03 | 10.11 | 8.7 | 11.37 | 11.91 | 12.13 | 11.11 |
| Martin Johnson Heade , 1859 | 12.31 | 10.1 | 10.13 | 8.7 | 11.34 | 11.87 | 12.27 | 11.11 |
| 05 · Rain | 12.47 | 10.12 | 10.1 | 10.04 | 10.56 | 11.75 | 12.4 | 11.04 |
| Paris Street; Rainy Day | 12.49 | 10.19 | 10.19 | 10.2 | 9.92 | 11.59 | 12.34 | 11.03 |
| Gustave Caillebotte , 1877 | 12.47 | 10.14 | 10.22 | 10.46 | 9.92 | 11.43 | 12.45 | 10.95 |
| 06 · Wind | 11.75 | 10.12 | 10.25 | 10.47 | 11.46 | 10.03 | 12.47 | 10.9 |
| Wheat Field with Cypresses | 11.3 | 10.12 | 10.19 | 10.64 | 11.47 | 9.68 | 12.56 | 10.78 |
| Vincent van Gogh , 1889 | 10.72 | 10.12 | 10.23 | 10.64 | 11.25 | 9.66 | 12.53 | 10.74 |
| 07 · Gale | 10.5 | 10.2 | 10.15 | 10.64 | 10.92 | 11.35 | 10.53 | 10.8 |
| Northeaster | 10.72 | 10.2 | 10.07 | 10.63 | 10.43 | 11.19 | 10.54 | 10.74 |
| Winslow Homer , 1895; reworked by 1901 | 10.92 | 10.2 | 10.09 | 10.55 | 10.41 | 11.18 | 10.04 | 10.33 |
| 08 · Fog | 10.47 | 10.7 | 10.11 | 10.13 | 11.34 | 11.19 | 11.65 | 8.89 |
| Waterloo Bridge, Gray Weather | 10.79 | 9.95 | 10.09 | 10.03 | 11.34 | 11.28 | 11.33 | 8.84 |
| Claude Monet , 1900 | 10.51 | 9.95 | 10 | 10.03 | 11.57 | 11.4 | 11.4 | 8.87 |
| Viewing | 9.68 | 9.03 | 9.03 | 8.8 | 9.11 | 10.32 | 9.5 | 9.37 |
| Reduce transparency | 9.42 | 9.11 | 8.92 | 8.86 | 9.54 | 9.43 | 8.92 | 9.75 |
| Frosts the label and the controls so the painting shows | 9.51 | 9.19 | 8.88 | 8.86 | 9.73 | 9.52 | 8.87 | 9.12 |
| through less. | 9.25 | 9.19 | 8.97 | 8.8 | 9.54 | 9.81 | 8.86 | 9.62 |
| Photographs | 11.05 | 10.12 | 9.97 | 10.55 | 11.01 | 11.2 | 11.8 | 10.7 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 10.82 | 10.11 | 10.1 | 10.62 | 11.04 | 11.22 | 11.99 | 10.74 |
| Rijksmuseum, Amsterdam , open access, public domain. | 10.59 | 10.12 | 10.09 | 10.62 | 10.18 | 11.19 | 11.8 | 10.49 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 10.68 | 10.12 | 10.15 | 10.62 | 10.49 | 11.2 | 12.03 | 10.72 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 10.61 | 10.29 | 10.16 | 10.47 | 10.03 | 11.18 | 11.44 | 10.25 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 10.34 | 10.28 | 10.19 | 10.22 | 10.1 | 11.18 | 11.35 | 10.21 |
| Metropolitan Museum of Art, New York , open access, public | 10.35 | 10.28 | 9.99 | 10.04 | 10.33 | 10.95 | 11.33 | 10.14 |
| domain. | 10.38 | 10.89 | 9.95 | 10.11 | 9.91 | 11.33 | 11.14 | 10.12 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 10.54 | 10.53 | 10.01 | 10.34 | 10.66 | 11.27 | 11.4 | 10.14 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 10.89 | 10.59 | 9.89 | 9.79 | 11.03 | 10.27 | 10.88 | 10.05 |
| Chicago , open access, public domain. | 10.34 | 10.86 | 9.81 | 9.73 | 10.46 | 10.25 | 9.77 | 10.07 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 10.43 | 10.94 | 9.83 | 9.77 | 11.01 | 10.46 | 9.82 | 10.02 |
| Museum of Art, New York , open access, public domain. | 10.44 | 11.1 | 9.77 | 9.77 | 10.73 | 10.54 | 9.77 | 10.02 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 10.33 | 11.55 | 9.82 | 9.79 | 10.72 | 10.43 | 9.75 | 10.04 |
| New York , open access, public domain. | 10.11 | 11.62 | 9.84 | 9.79 | 10.55 | 10.28 | 9.76 | 10.04 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 10.28 | 11.47 | 9.86 | 9.79 | 10.89 | 10.27 | 9.82 | 10.07 |

### GPU tier · light · rooms view · inactive (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 11.24 | 8.55 | 8.85 | 8.64 | 10.18 | 9.97 | 10.31 | 9.86 |
| 8 rooms | 12.85 | 8.7 | 9.34 | 8.62 | 10.11 | 10.8 | 10.14 | 9.99 |
| Eight skies, 1608–1900 | 11.28 | 8.54 | 8.87 | 8.79 | 10.04 | 9.79 | 10.53 | 9.88 |
| For most of the history of European painting the sky | 10.76 | 8.62 | 8.81 | 8.8 | 10.09 | 10.69 | 10.46 | 9.8 |
| was the back wall of the picture. This exhibition | 10.91 | 8.64 | 8.82 | 8.8 | 10.01 | 10.56 | 10.74 | 9.72 |
| follows it becoming the subject: eight rooms, each | 11.03 | 8.7 | 8.78 | 8.87 | 9.69 | 10.37 | 10.96 | 9.6 |
| holding one work, from a Dutch winter in the Little Ice | 11.26 | 8.84 | 8.86 | 8.94 | 10.04 | 10.19 | 11.25 | 9.5 |
| Age to a London fog that was largely coal smoke. | 11.08 | 8.86 | 8.83 | 9.12 | 10.16 | 9.99 | 11.18 | 9.49 |
| Each work fills the room. Its label sits beside it, and | 10.11 | 8.78 | 8.77 | 9.44 | 9.52 | 9.89 | 10.89 | 9.5 |
| the audio guide reads the label aloud in your | 9.42 | 8.78 | 8.84 | 9.44 | 9.64 | 9.89 | 10.76 | 9.52 |
| browser’s own voice. | 9.01 | 8.78 | 8.92 | 9.44 | 9.54 | 10.05 | 10.66 | 9.55 |
| Rooms | 9.21 | 9.83 | 9.07 | 9.35 | 8.39 | 9.87 | 10.68 | 9.19 |
| 01 · Frost | 7.75 | 9.34 | 8.88 | 8.96 | 9.86 | 9.87 | 10.4 | 8.92 |
| · you are here | 8.35 | 8.11 | 7.5 | 7.63 | 8.74 | 8.59 | 9.95 | 7.76 |
| Winter Landscape with Ice Skaters | 8.2 | 8.94 | 8.88 | 8.87 | 10.12 | 9.97 | 9.94 | 8.85 |
| Hendrick Avercamp , c. 1608 | 7.89 | 9.17 | 8.82 | 8.97 | 10.13 | 10.07 | 10 | 8.88 |
| 02 · Cloud | 10.03 | 8.35 | 8.75 | 9.08 | 10.7 | 10.05 | 10.02 | 8.89 |
| The Windmill at Wijk bij Duurstede | 9.97 | 8.03 | 8.66 | 8.57 | 10.71 | 8.86 | 9.85 | 8.71 |
| Jacob van Ruisdael , c. 1668–70 | 9.59 | 8.19 | 8.66 | 8.56 | 10.77 | 8.92 | 8.95 | 8.67 |
| 03 · Clearing | 9.55 | 9.95 | 7.43 | 8.56 | 10.41 | 9.09 | 8.12 | 9.51 |
| View from Mount Holyoke, Northampton, | 8.97 | 10.31 | 7.43 | 8.56 | 10.54 | 9.07 | 8.12 | 8.68 |
| Massachusetts, after a Thunderstorm—The | 8.9 | 10.57 | 7.47 | 8.56 | 10.55 | 8.89 | 8.17 | 8.7 |
| Oxbow | 8.72 | 10.46 | 7.47 | 8.57 | 10.38 | 8.73 | 8.11 | 9.52 |
| Thomas Cole , 1836 | 8.78 | 10.19 | 7.48 | 8.86 | 10.37 | 8.73 | 8.14 | 8.94 |
| 04 · Thunder | 11.38 | 8.62 | 8.96 | 7.63 | 11.9 | 10.73 | 10.71 | 9.89 |
| Approaching Thunder Storm | 11.3 | 8.7 | 8.93 | 7.63 | 10.04 | 10.74 | 10.94 | 9.89 |
| Martin Johnson Heade , 1859 | 11.15 | 8.78 | 8.9 | 7.63 | 9.97 | 10.69 | 11.13 | 9.89 |
| 05 · Rain | 11.32 | 8.8 | 8.9 | 8.87 | 9.53 | 10.51 | 11.23 | 9.82 |
| Paris Street; Rainy Day | 11.38 | 8.85 | 8.95 | 8.96 | 8.76 | 10.36 | 11.24 | 9.81 |
| Gustave Caillebotte , 1877 | 11.38 | 8.86 | 8.98 | 9.29 | 8.75 | 10.17 | 11.35 | 9.74 |
| 06 · Wind | 10.43 | 8.78 | 9.01 | 9.3 | 10.2 | 8.95 | 11.38 | 9.63 |
| Wheat Field with Cypresses | 9.89 | 8.78 | 8.98 | 9.44 | 10.15 | 8.52 | 11.47 | 9.55 |
| Vincent van Gogh , 1889 | 9.24 | 8.78 | 9.03 | 9.44 | 9.86 | 8.52 | 11.36 | 9.52 |
| 07 · Gale | 8.98 | 8.86 | 8.92 | 9.44 | 9.52 | 10.08 | 9.43 | 9.58 |
| Northeaster | 9.22 | 8.86 | 8.83 | 9.44 | 8.93 | 9.87 | 9.5 | 9.5 |
| Winslow Homer , 1895; reworked by 1901 | 9.45 | 8.94 | 8.85 | 9.38 | 8.86 | 9.92 | 8.92 | 9.05 |
| 08 · Fog | 8.91 | 9.48 | 8.87 | 8.94 | 10.03 | 9.88 | 10.32 | 7.75 |
| Waterloo Bridge, Gray Weather | 9.31 | 8.57 | 8.86 | 8.78 | 10.03 | 9.98 | 9.94 | 7.69 |
| Claude Monet , 1900 | 8.97 | 8.62 | 8.77 | 8.8 | 10.27 | 10.13 | 10.07 | 7.73 |
| Viewing | 8.31 | 7.83 | 7.93 | 7.7 | 7.67 | 9.17 | 8.11 | 8.16 |
| Reduce transparency | 7.99 | 7.91 | 7.79 | 7.76 | 8.16 | 8.11 | 7.43 | 8.6 |
| Frosts the label and the controls so the painting shows | 8.08 | 7.99 | 7.77 | 7.77 | 8.41 | 8.26 | 7.37 | 7.92 |
| through less. | 7.79 | 7.99 | 7.85 | 7.7 | 8.16 | 8.61 | 7.36 | 8.52 |
| Photographs | 9.64 | 8.77 | 8.74 | 9.38 | 9.61 | 9.91 | 10.55 | 9.47 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 9.34 | 8.78 | 8.89 | 9.44 | 9.63 | 9.93 | 10.75 | 9.52 |
| Rijksmuseum, Amsterdam , open access, public domain. | 9.09 | 8.78 | 8.89 | 9.44 | 8.6 | 9.91 | 10.56 | 9.22 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 9.18 | 8.84 | 8.91 | 9.44 | 8.97 | 9.88 | 10.83 | 9.48 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 9.11 | 8.95 | 8.95 | 9.29 | 8.44 | 9.91 | 10.11 | 8.96 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 8.78 | 8.94 | 8.99 | 9.04 | 8.51 | 9.86 | 10.01 | 8.91 |
| Metropolitan Museum of Art, New York , open access, public | 8.74 | 8.95 | 8.75 | 8.87 | 8.8 | 9.61 | 10 | 8.82 |
| domain. | 8.78 | 9.68 | 8.71 | 8.88 | 8.27 | 10.06 | 9.76 | 8.81 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 9.01 | 9.25 | 8.82 | 9.15 | 9.13 | 9.99 | 10.01 | 8.81 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 9.43 | 9.31 | 8.64 | 8.56 | 9.64 | 8.81 | 9.45 | 8.7 |
| Chicago , open access, public domain. | 8.78 | 9.65 | 8.56 | 8.5 | 8.95 | 8.82 | 8.12 | 8.78 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 8.87 | 9.71 | 8.56 | 8.54 | 9.56 | 9.03 | 8.17 | 8.72 |
| Museum of Art, New York , open access, public domain. | 8.87 | 9.88 | 8.55 | 8.56 | 9.22 | 9.13 | 8.12 | 8.69 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 8.77 | 10.38 | 8.58 | 8.56 | 9.2 | 9.01 | 8.11 | 8.7 |
| New York , open access, public domain. | 8.48 | 10.45 | 8.59 | 8.56 | 9.09 | 8.85 | 8.1 | 8.76 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 8.7 | 10.3 | 8.63 | 8.57 | 9.5 | 8.83 | 8.17 | 8.79 |

### GPU tier · dark · frost · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.61 / 6.51 | 7.07 / 6.91 | 0.283 |
| window | 0 | Room 1 of 8 | 6.45 / 6.34 | 6.9 / 6.72 | 0.29 |
| window | 0 | Frost (large) | 6.7 / 6.61 | 7.17 / 7.08 | 0.279 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 6.63 / 6.61 | 7.1 / 7.09 | 0.282 |
| window | 0 | Hendrick Avercamp | 6.69 / 6.69 | 7.18 / 7.17 | 0.279 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 6.69 / 6.68 | 7.18 / 7.1 | 0.279 |
| window | 0 | The whole work. The outline marks the part around you. | 6.76 / 6.73 | 7.29 / 7.21 | 0.276 |
| window | 0 | Avercamp made his name painting winter, in the years | 6.76 / 6.71 | 7.28 / 7.2 | 0.276 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 6.75 / 6.71 | 7.26 / 7.2 | 0.276 |
| window | 0 | Countries. Here a whole village has moved onto the | 6.76 / 6.73 | 7.26 / 7.21 | 0.276 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 6.77 / 6.76 | 7.27 / 7.26 | 0.276 |
| window | 0 | sledge on the right, a church on the left. | 6.78 / 6.76 | 7.28 / 7.27 | 0.275 |
| window | 0 | Look at how the air is built. The figures in front are | 6.79 / 6.76 | 7.29 / 7.27 | 0.275 |
| window | 0 | sharp and full of colour; a few hundred metres back | 6.78 / 6.76 | 7.3 / 7.28 | 0.275 |
| window | 0 | they thin into grey-white haze, and the far bank all but | 6.79 / 6.76 | 7.29 / 7.28 | 0.275 |
| Rooms | 0 | 1 | 5.61 / 5.58 | 6 / 5.93 | 0.329 |
| Rooms | 0 | / 8 | 5.6 / 5.53 | 5.99 / 5.93 | 0.329 |
| Audio guide | 0 | Audio guide | 5.54 / 5.46 | 5.92 / 5.85 | 0.332 |
| Audio guide | 0 | About 0:51 | 5.51 / 5.44 | 5.85 / 5.83 | 0.334 |
| Rooms | 0 | icon: Next room: Cloud | 5.53 / 5.44 | 5.91 / 5.85 | 0.333 |
| Audio guide | 0 | icon: Play the audio guide | 5.53 / 5.46 | 5.91 / 5.85 | 0.333 |
| window | 552 | Look at how the air is built. The figures in front are | 6.63 / 6.61 | 7.09 / 7.08 | 0.282 |
| window | 552 | sharp and full of colour; a few hundred metres back | 6.63 / 6.61 | 7.09 / 7.09 | 0.282 |
| window | 552 | they thin into grey-white haze, and the far bank all but | 6.63 / 6.61 | 7.1 / 7.08 | 0.282 |
| window | 552 | dissolves. That haze is the weather: cold, damp air | 6.63 / 6.61 | 7.1 / 7.09 | 0.282 |
| window | 552 | thick enough to carry the light. | 6.69 / 6.68 | 7.17 / 7.09 | 0.279 |
| window | 552 | Avercamp signed the picture on the wall of a wooden | 6.68 / 6.61 | 7.1 / 7.09 | 0.28 |
| window | 552 | shed on the right, among the scratched graffiti, where | 6.68 / 6.62 | 7.1 / 7.09 | 0.28 |
| window | 552 | it is easy to miss. | 6.71 / 6.71 | 7.19 / 7.17 | 0.278 |
| window | 552 | Weather | 8.39 / 8.37 | 8.8 / 8.72 | 0.214 |
| window | 552 | Hard frost, haze over the ice | 8.34 / 8.26 | 8.67 / 8.67 | 0.215 |
| window | 552 | Artist | 8.4 / 8.32 | 8.74 / 8.74 | 0.213 |
| window | 552 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 8.33 / 8.33 | 8.67 / 8.67 | 0.216 |
| window | 552 | Date | 8.4 / 8.32 | 8.83 / 8.74 | 0.213 |
| window | 552 | c. 1608 | 8.39 / 8.37 | 8.81 / 8.79 | 0.214 |
| window | 552 | Medium | 8.41 / 8.41 | 8.83 / 8.81 | 0.213 |
| window | 552 | Oil on panel | 8.34 / 8.34 | 8.78 / 8.7 | 0.215 |
| window | 552 | Size | 8.37 / 8.35 | 8.81 / 8.71 | 0.214 |
| window | 552 | 77.3 × 131.9 cm | 8.33 / 8.29 | 8.77 / 8.77 | 0.216 |
| window | 552 | Collection | 8.36 / 8.33 | 8.7 / 8.68 | 0.215 |
| window | 552 | Rijksmuseum, Amsterdam | 8.31 / 8.31 | 8.76 / 8.76 | 0.217 |
| window | 552 | Credit | 8.34 / 8.29 | 8.79 / 8.76 | 0.215 |
| window | 552 | Purchased with the support of the Vereniging | 8.33 / 8.31 | 8.77 / 8.76 | 0.216 |
| window | 552 | Rembrandt | 8.31 / 8.31 | 8.77 / 8.76 | 0.217 |
| window | 552 | Number | 8.36 / 8.35 | 8.85 / 8.79 | 0.215 |
| window | 552 | SK-A-1718 | 8.31 / 8.31 | 8.76 / 8.76 | 0.217 |
| window | 552 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.79 / 6.76 | 7.3 / 7.28 | 0.275 |
| window | 552 | domain. | 6.8 / 6.76 | 7.29 / 7.28 | 0.274 |

### GPU tier · dark · cloud · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 7 / 6.93 | 7.58 / 7.51 | 0.266 |
| window | 0 | Room 2 of 8 | 6.94 / 6.92 | 7.51 / 7.51 | 0.269 |
| window | 0 | Cloud (large) | 7.02 / 7 | 7.6 / 7.58 | 0.265 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 7 / 6.91 | 7.58 / 7.41 | 0.266 |
| window | 0 | Jacob van Ruisdael | 7 / 7 | 7.58 / 7.58 | 0.266 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 7 / 6.93 | 7.58 / 7.51 | 0.266 |
| window | 0 | The whole work. The outline marks the part around you. | 6.93 / 6.91 | 7.51 / 7.49 | 0.269 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 6.91 / 6.91 | 7.49 / 7.41 | 0.27 |
| window | 0 | more than half the canvas, and he paints it as a | 6.93 / 6.91 | 7.51 / 7.41 | 0.269 |
| window | 0 | structure: banks of cumulus heaped over one another, | 6.93 / 6.91 | 7.51 / 7.41 | 0.269 |
| window | 0 | grey underneath, lit at their edges by a sun we | 6.93 / 6.91 | 7.5 / 7.49 | 0.269 |
| window | 0 | cannot see. | 6.91 / 6.84 | 7.49 / 7.41 | 0.27 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 6.84 / 6.82 | 7.41 / 7.38 | 0.273 |
| window | 0 | A sailing boat is out on the water, the towers of | 6.84 / 6.82 | 7.41 / 7.38 | 0.273 |
| window | 0 | Duurstede castle and the church rise in the distance, | 6.84 / 6.83 | 7.41 / 7.38 | 0.273 |
| Rooms | 0 | 2 | 6.82 / 6.82 | 7.62 / 7.6 | 0.274 |
| Rooms | 0 | / 8 | 6.81 / 6.81 | 7.6 / 7.6 | 0.274 |
| Audio guide | 0 | Audio guide | 7.01 / 6.94 | 7.92 / 7.91 | 0.266 |
| Audio guide | 0 | About 0:49 | 7.03 / 7.02 | 8.02 / 8.02 | 0.265 |
| Rooms | 0 | icon: Previous room: Frost | 6.81 / 6.79 | 7.6 / 7.6 | 0.274 |
| Rooms | 0 | icon: Next room: Clearing | 6.82 / 6.8 | 7.6 / 7.6 | 0.274 |
| Audio guide | 0 | icon: Play the audio guide | 7.01 / 6.99 | 7.94 / 7.92 | 0.266 |
| window | 552 | Below, the mill stands near the bank of the river Lek. | 7 / 6.91 | 7.58 / 7.51 | 0.266 |
| window | 552 | A sailing boat is out on the water, the towers of | 7 / 6.93 | 7.6 / 7.51 | 0.266 |
| window | 552 | Duurstede castle and the church rise in the distance, | 7 / 6.93 | 7.58 / 7.51 | 0.266 |
| window | 552 | and a few women walk along the bank, very small | 7 / 6.91 | 7.58 / 7.49 | 0.266 |
| window | 552 | against the mill. | 7 / 7 | 7.59 / 7.58 | 0.266 |
| window | 552 | Dutch painters of the seventeenth century made the | 6.93 / 6.84 | 7.51 / 7.41 | 0.269 |
| window | 552 | sky a subject in its own right. Few made it carry as | 6.93 / 6.83 | 7.51 / 7.38 | 0.269 |
| window | 552 | much of a picture as this. | 7 / 6.91 | 7.58 / 7.51 | 0.266 |
| window | 552 | Weather | 8.49 / 8.39 | 9.03 / 8.91 | 0.21 |
| window | 552 | Heaped cumulus, sun breaking through | 8.49 / 8.37 | 9.03 / 8.9 | 0.21 |
| window | 552 | Artist | 8.47 / 8.36 | 8.92 / 8.81 | 0.211 |
| window | 552 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 8.49 / 8.39 | 9.03 / 8.91 | 0.21 |
| window | 552 | Date | 8.47 / 8.36 | 8.91 / 8.81 | 0.211 |
| window | 552 | c. 1668–70 | 8.49 / 8.49 | 9.03 / 9.03 | 0.21 |
| window | 552 | Medium | 8.47 / 8.36 | 8.92 / 8.81 | 0.211 |
| window | 552 | Oil on canvas | 8.49 / 8.46 | 9.03 / 9.02 | 0.21 |
| window | 552 | Size | 8.47 / 8.37 | 8.91 / 8.81 | 0.211 |
| window | 552 | 83 × 101 cm | 8.47 / 8.46 | 9 / 9 | 0.211 |
| window | 552 | Collection | 8.47 / 8.39 | 8.92 / 8.91 | 0.211 |
| window | 552 | Rijksmuseum, Amsterdam | 8.49 / 8.47 | 9.03 / 9 | 0.21 |
| window | 552 | Credit | 8.47 / 8.36 | 9 / 8.89 | 0.211 |
| window | 552 | On loan from the City of Amsterdam (A. van | 8.48 / 8.47 | 9.02 / 9 | 0.21 |
| window | 552 | der Hoop Bequest) | 8.47 / 8.46 | 8.91 / 8.91 | 0.211 |
| window | 552 | Number | 8.38 / 8.38 | 8.91 / 8.8 | 0.214 |
| window | 552 | SK-C-211 | 8.38 / 8.38 | 8.91 / 8.91 | 0.214 |
| window | 552 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.84 / 6.83 | 7.41 / 7.38 | 0.273 |
| window | 552 | domain. | 6.85 / 6.75 | 7.41 / 7.21 | 0.273 |

### GPU tier · dark · clearing · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.49 / 7.47 | 8.35 / 8.33 | 0.247 |
| window | 0 | Room 3 of 8 | 7.29 / 7.24 | 8.11 / 7.98 | 0.255 |
| window | 0 | Clearing (large) | 7.52 / 7.49 | 8.44 / 8.35 | 0.246 |
| window | 0 | View from Mount Holyoke, (large) | 7.49 / 7.46 | 8.39 / 8.24 | 0.247 |
| window | 0 | Northampton, Massachusetts, (large) | 7.49 / 7.39 | 8.36 / 8.22 | 0.247 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 7.49 / 7.34 | 8.33 / 8.09 | 0.247 |
| window | 0 | Thomas Cole | 7.57 / 7.5 | 8.44 / 8.43 | 0.244 |
| window | 0 | American, born England, 1801–1848 · 1836 | 7.49 / 7.37 | 8.33 / 8.22 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.54 / 7.48 | 8.41 / 8.33 | 0.245 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 7.58 / 7.52 | 8.45 / 8.42 | 0.243 |
| window | 0 | valley. On the left it still hangs over wild, broken trees, | 7.58 / 7.55 | 8.48 / 8.42 | 0.243 |
| window | 0 | and rain falls in grey veils across the hills. On the right | 7.58 / 7.52 | 8.48 / 8.37 | 0.243 |
| window | 0 | the air has cleared over cleared land: fields, farms | 7.58 / 7.52 | 8.48 / 8.36 | 0.243 |
| window | 0 | and the river’s great loop. | 7.6 / 7.51 | 8.47 / 8.37 | 0.243 |
| Rooms | 0 | 3 | 8.01 / 7.92 | 10.09 / 9.98 | 0.227 |
| Rooms | 0 | / 8 | 7.82 / 7.7 | 9.74 / 9.51 | 0.234 |
| Audio guide | 0 | Audio guide | 7.61 / 7.27 | 8.99 / 8.48 | 0.242 |
| Audio guide | 0 | About 0:50 | 7.6 / 7.49 | 9.04 / 8.83 | 0.242 |
| Rooms | 0 | icon: Previous room: Cloud | 8.01 / 7.98 | 10.14 / 10.06 | 0.227 |
| Rooms | 0 | icon: Next room: Thunder | 8.02 / 8 | 10.14 / 10.12 | 0.227 |
| Audio guide | 0 | icon: Play the audio guide | 7.62 / 7.52 | 9.06 / 8.84 | 0.242 |
| window | 608 | Cole divided the picture along a diagonal, and the | 7.49 / 7.37 | 8.33 / 8.22 | 0.247 |
| window | 608 | weather does the dividing. He painted it for the 1836 | 7.49 / 7.29 | 8.35 / 8.11 | 0.247 |
| window | 608 | annual exhibition of the National Academy of Design, | 7.49 / 7.27 | 8.35 / 8.09 | 0.247 |
| window | 608 | calling the view from Mount Holyoke “about the finest | 7.49 / 7.25 | 8.35 / 8.01 | 0.247 |
| window | 608 | scene I have in my sketchbook.” | 7.53 / 7.49 | 8.43 / 8.33 | 0.245 |
| window | 608 | Look for the painter himself near the bottom of the | 7.49 / 7.36 | 8.33 / 8.11 | 0.247 |
| window | 608 | canvas: a small figure at an easel among the rocks, | 7.49 / 7.36 | 8.33 / 8.11 | 0.247 |
| window | 608 | turning back toward us. | 7.54 / 7.47 | 8.36 / 8.33 | 0.245 |
| window | 608 | Weather | 8.99 / 8.97 | 9.69 / 9.68 | 0.192 |
| window | 608 | Thunderstorm passing, sun on the valley | 8.9 / 8.86 | 9.6 / 9.57 | 0.196 |
| window | 608 | Artist | 8.91 / 8.91 | 9.6 / 9.6 | 0.195 |
| window | 608 | Thomas Cole ( American, born England, | 8.91 / 8.86 | 9.6 / 9.59 | 0.195 |
| window | 608 | 1801–1848 ) | 8.99 / 8.97 | 9.68 / 9.68 | 0.193 |
| window | 608 | Date | 8.87 / 8.87 | 9.57 / 9.57 | 0.197 |
| window | 608 | 1836 | 9.05 / 9.05 | 9.77 / 9.69 | 0.19 |
| window | 608 | Medium | 8.99 / 8.98 | 9.68 / 9.68 | 0.193 |
| window | 608 | Oil on canvas | 9.06 / 8.97 | 9.78 / 9.68 | 0.19 |
| window | 608 | Size | 9.05 / 9.05 | 9.77 / 9.76 | 0.19 |
| window | 608 | 130.8 × 193 cm | 9.1 / 8.97 | 9.79 / 9.69 | 0.189 |
| window | 608 | Collection | 9.07 / 9.05 | 9.79 / 9.77 | 0.19 |
| window | 608 | The Metropolitan Museum of Art, New York | 9.09 / 9.01 | 9.83 / 9.69 | 0.189 |
| window | 608 | Credit | 9.03 / 9.02 | 9.79 / 9.79 | 0.191 |
| window | 608 | Gift of Mrs. Russell Sage, 1908 | 9.09 / 9.01 | 9.86 / 9.69 | 0.189 |
| window | 608 | Number | 9.05 / 9.04 | 9.82 / 9.79 | 0.19 |
| window | 608 | 08.228 | 9.12 / 9.09 | 9.91 / 9.83 | 0.188 |
| window | 608 | Photograph: The Metropolitan Museum of Art, New York , open | 7.58 / 7.44 | 8.48 / 8.3 | 0.243 |
| window | 608 | access, public domain. | 7.6 / 7.58 | 8.5 / 8.48 | 0.242 |

### GPU tier · dark · thunder · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.63 / 7.62 | 8.54 / 8.54 | 0.241 |
| window | 0 | Room 4 of 8 | 7.65 / 7.65 | 8.54 / 8.53 | 0.241 |
| window | 0 | Thunder (large) | 7.65 / 7.62 | 8.62 / 8.54 | 0.241 |
| window | 0 | Approaching Thunder Storm (large) | 7.63 / 7.62 | 8.54 / 8.54 | 0.241 |
| window | 0 | Martin Johnson Heade | 7.63 / 7.54 | 8.54 / 8.41 | 0.241 |
| window | 0 | American, 1819–1904 · 1859 | 7.52 / 7.4 | 8.38 / 8.28 | 0.246 |
| window | 0 | The whole work. The outline marks the part around you. | 7.54 / 7.52 | 8.52 / 8.41 | 0.245 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 7.37 / 7.25 | 8.18 / 8.03 | 0.251 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 7.34 / 7.16 | 8.13 / 7.9 | 0.252 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 7.69 / 7.57 | 8.62 / 8.48 | 0.239 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 7.73 / 7.71 | 8.71 / 8.66 | 0.238 |
| window | 0 | rower pulls for shore; a white sail stands out against | 7.73 / 7.71 | 8.71 / 8.66 | 0.238 |
| window | 0 | the dark. | 7.73 / 7.73 | 8.74 / 8.66 | 0.238 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 7.69 / 7.41 | 8.64 / 8.25 | 0.239 |
| window | 0 | before such a storm, and that is what the picture | 7.55 / 6.61 | 8.45 / 7.17 | 0.244 |
| Rooms | 0 | 4 | 6.28 / 6.26 | 6.86 / 6.86 | 0.297 |
| Rooms | 0 | / 8 | 6.28 / 6.2 | 6.86 / 6.77 | 0.297 |
| Audio guide | 0 | Audio guide | 6.37 / 6.29 | 6.97 / 6.95 | 0.293 |
| Audio guide | 0 | About 0:53 | 6.4 / 6.37 | 7.04 / 6.96 | 0.291 |
| Rooms | 0 | icon: Previous room: Clearing | 6.2 / 6.18 | 6.77 / 6.75 | 0.3 |
| Rooms | 0 | icon: Next room: Rain | 6.18 / 6.1 | 6.75 / 6.66 | 0.301 |
| Audio guide | 0 | icon: Play the audio guide | 6.39 / 6.35 | 7.05 / 6.96 | 0.292 |
| window | 618 | holds: not the storm itself but the minute before it. | 7.65 / 7.62 | 8.54 / 8.53 | 0.241 |
| window | 618 | Painted two years before the Civil War, it has often | 7.65 / 7.62 | 8.54 / 8.53 | 0.241 |
| window | 618 | been read as a picture of a country waiting for | 7.63 / 7.62 | 8.54 / 8.53 | 0.241 |
| window | 618 | something to break. Heade based it on a storm | 7.63 / 7.62 | 8.54 / 8.52 | 0.241 |
| window | 618 | he had watched from Prudence Island, in the bay, | 7.52 / 7.38 | 8.41 / 8.26 | 0.246 |
| window | 618 | around 1858. | 7.54 / 7.42 | 8.52 / 8.28 | 0.245 |
| window | 618 | Weather | 8.95 / 8.95 | 9.57 / 9.57 | 0.194 |
| window | 618 | Thunderstorm approaching over still water | 8.84 / 8.81 | 9.54 / 9.51 | 0.198 |
| window | 618 | Artist | 8.95 / 8.94 | 9.57 / 9.57 | 0.194 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 8.84 / 8.84 | 9.54 / 9.54 | 0.198 |
| window | 618 | 1819–1904 ) | 8.95 / 8.95 | 9.57 / 9.57 | 0.194 |
| window | 618 | Date | 8.95 / 8.87 | 9.57 / 9.57 | 0.194 |
| window | 618 | 1859 | 8.92 / 8.92 | 9.57 / 9.57 | 0.195 |
| window | 618 | Medium | 8.95 / 8.95 | 9.68 / 9.68 | 0.194 |
| window | 618 | Oil on canvas | 9.06 / 9.03 | 9.76 / 9.76 | 0.19 |
| window | 618 | Size | 9.04 / 9.01 | 9.76 / 9.65 | 0.191 |
| window | 618 | 71.1 × 111.8 cm | 9.05 / 8.94 | 9.78 / 9.65 | 0.19 |
| window | 618 | Collection | 8.65 / 8.64 | 9.36 / 9.33 | 0.204 |
| window | 618 | The Metropolitan Museum of Art, New York | 8.88 / 8.75 | 9.52 / 9.46 | 0.196 |
| window | 618 | Credit | 9.13 / 9.12 | 9.87 / 9.87 | 0.188 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 9.17 / 9.15 | 9.92 / 9.92 | 0.187 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9.17 / 9.15 | 10 / 9.89 | 0.187 |
| window | 618 | 1975 | 9.19 / 9.18 | 9.92 / 9.92 | 0.186 |
| window | 618 | Number | 9.19 / 9.19 | 10 / 9.92 | 0.186 |
| window | 618 | 1975.160 | 9.17 / 9.17 | 10 / 9.92 | 0.187 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 7.64 / 6.85 | 8.58 / 7.47 | 0.241 |
| window | 618 | access, public domain. | 7.55 / 7.12 | 8.43 / 7.89 | 0.244 |

### GPU tier · dark · rain · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.67 / 6.51 | 7.09 / 6.98 | 0.28 |
| window | 0 | Room 5 of 8 | 6.73 / 6.65 | 7.21 / 7.18 | 0.278 |
| window | 0 | Rain (large) | 6.71 / 6.69 | 7.26 / 7.16 | 0.278 |
| window | 0 | Paris Street; Rainy Day (large) | 6.79 / 6.69 | 7.28 / 7.17 | 0.275 |
| window | 0 | Gustave Caillebotte | 6.79 / 6.71 | 7.28 / 7.19 | 0.275 |
| window | 0 | French, 1848–1894 · 1877 | 6.81 / 6.73 | 7.3 / 7.28 | 0.274 |
| window | 0 | The whole work. The outline marks the part around you. | 6.79 / 6.72 | 7.28 / 7.28 | 0.275 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 6.74 / 6.73 | 7.28 / 7.28 | 0.277 |
| window | 0 | paints the rain through what it does: the paving | 6.79 / 6.73 | 7.28 / 7.21 | 0.275 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 6.79 / 6.72 | 7.28 / 7.21 | 0.275 |
| window | 0 | everyone carries an umbrella, the newly invented | 6.79 / 6.73 | 7.28 / 7.28 | 0.275 |
| window | 0 | retractable kind. | 6.81 / 6.81 | 7.31 / 7.28 | 0.274 |
| window | 0 | The place is a busy intersection a short walk from the | 6.81 / 6.73 | 7.28 / 7.28 | 0.274 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 6.81 / 6.73 | 7.3 / 7.28 | 0.274 |
| window | 0 | and uniform stone façades. A green lamppost splits | 6.81 / 6.73 | 7.28 / 7.28 | 0.274 |
| Rooms | 0 | 5 | 6.45 / 6.43 | 7.09 / 7.09 | 0.289 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 7.09 / 7.01 | 0.29 |
| Audio guide | 0 | Audio guide | 6.02 / 6 | 6.52 / 6.52 | 0.309 |
| Audio guide | 0 | About 0:46 | 6.09 / 6 | 6.54 / 6.52 | 0.306 |
| Rooms | 0 | icon: Previous room: Thunder | 6.44 / 6.44 | 7.08 / 7.08 | 0.29 |
| Rooms | 0 | icon: Next room: Wind | 6.34 / 6.26 | 6.99 / 6.9 | 0.294 |
| Audio guide | 0 | icon: Play the audio guide | 6.09 / 6 | 6.52 / 6.52 | 0.306 |
| window | 578 | painter’s home, in a Paris rebuilt with wide streets | 6.73 / 6.69 | 7.28 / 7.16 | 0.278 |
| window | 578 | and uniform stone façades. A green lamppost splits | 6.79 / 6.69 | 7.28 / 7.17 | 0.275 |
| window | 578 | the canvas in two; the couple on the right walk | 6.79 / 6.69 | 7.28 / 7.17 | 0.275 |
| window | 578 | straight toward us, looking at something beyond | 6.79 / 6.69 | 7.28 / 7.17 | 0.275 |
| window | 578 | the frame. | 6.81 / 6.71 | 7.3 / 7.26 | 0.274 |
| window | 578 | Nearly life-size, it is Caillebotte’s largest painting. He | 6.81 / 6.79 | 7.3 / 7.28 | 0.274 |
| window | 578 | showed it at the third Impressionist exhibition in 1877, | 6.81 / 6.79 | 7.3 / 7.28 | 0.274 |
| window | 578 | the year he made it. | 6.81 / 6.73 | 7.3 / 7.28 | 0.274 |
| window | 578 | Weather | 8.38 / 8.37 | 8.82 / 8.82 | 0.214 |
| window | 578 | Light rain, overcast | 8.38 / 8.38 | 8.9 / 8.82 | 0.214 |
| window | 578 | Artist | 8.45 / 8.39 | 8.91 / 8.9 | 0.211 |
| window | 578 | Gustave Caillebotte ( French, 1848–1894 ) | 8.39 / 8.36 | 8.82 / 8.82 | 0.214 |
| window | 578 | Date | 8.47 / 8.46 | 9.01 / 8.99 | 0.211 |
| window | 578 | 1877 | 8.36 / 8.33 | 8.8 / 8.78 | 0.215 |
| window | 578 | Medium | 8.46 / 8.36 | 8.91 / 8.88 | 0.211 |
| window | 578 | Oil on canvas | 8.33 / 8.33 | 8.77 / 8.77 | 0.216 |
| window | 578 | Size | 8.47 / 8.46 | 8.92 / 8.91 | 0.211 |
| window | 578 | 212.2 × 276.2 cm | 8.33 / 8.33 | 8.78 / 8.77 | 0.216 |
| window | 578 | Collection | 8.36 / 8.33 | 8.77 / 8.77 | 0.215 |
| window | 578 | The Art Institute of Chicago | 8.33 / 8.33 | 8.78 / 8.77 | 0.216 |
| window | 578 | Credit | 8.46 / 8.36 | 8.91 / 8.88 | 0.211 |
| window | 578 | Charles H. and Mary F. S. Worcester | 8.33 / 8.33 | 8.78 / 8.77 | 0.216 |
| window | 578 | Number | 8.44 / 8.38 | 8.91 / 8.88 | 0.212 |
| window | 578 | 1964.336 | 8.36 / 8.36 | 8.79 / 8.79 | 0.215 |
| window | 578 | Photograph: The Art Institute of Chicago , open access, public | 6.81 / 6.73 | 7.3 / 7.28 | 0.274 |
| window | 578 | domain. | 6.83 / 6.81 | 7.31 / 7.31 | 0.273 |

### GPU tier · dark · wind · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.62 / 6.54 | 7.09 / 7 | 0.282 |
| window | 0 | Room 6 of 8 | 6.61 / 6.53 | 7.02 / 6.99 | 0.282 |
| window | 0 | Wind (large) | 6.72 / 6.64 | 7.2 / 7.11 | 0.278 |
| window | 0 | Wheat Field with Cypresses (large) | 6.72 / 6.64 | 7.18 / 7.11 | 0.278 |
| window | 0 | Vincent van Gogh | 6.71 / 6.63 | 7.2 / 7.11 | 0.278 |
| window | 0 | Dutch, 1853–1890 · 1889 | 6.73 / 6.7 | 7.2 / 7.18 | 0.277 |
| window | 0 | The whole work. The outline marks the part around you. | 6.74 / 6.69 | 7.22 / 7.2 | 0.277 |
| window | 0 | Everything in this field is moving the same way. The | 6.74 / 6.69 | 7.23 / 7.21 | 0.277 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 6.74 / 6.71 | 7.23 / 7.21 | 0.277 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 6.77 / 6.69 | 7.23 / 7.21 | 0.276 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 6.79 / 6.76 | 7.31 / 7.22 | 0.275 |
| window | 0 | the paint on so heavily that the brushstrokes | 6.8 / 6.76 | 7.31 / 7.23 | 0.275 |
| window | 0 | themselves take the shape of the wind. | 6.78 / 6.75 | 7.24 / 7.2 | 0.275 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 6.78 / 6.76 | 7.24 / 7.22 | 0.275 |
| window | 0 | Saint-Rémy in Provence, where he was a patient at the | 6.8 / 6.78 | 7.31 / 7.23 | 0.275 |
| Rooms | 0 | 6 | 6.35 / 6.33 | 6.99 / 6.97 | 0.294 |
| Rooms | 0 | / 8 | 6.34 / 6.34 | 6.99 / 6.97 | 0.294 |
| Audio guide | 0 | Audio guide | 6.44 / 6.42 | 7.09 / 7.06 | 0.29 |
| Audio guide | 0 | About 0:51 | 6.49 / 6.41 | 7.09 / 7.07 | 0.287 |
| Rooms | 0 | icon: Previous room: Rain | 6.34 / 6.32 | 6.97 / 6.9 | 0.294 |
| Rooms | 0 | icon: Next room: Gale | 6.33 / 6.25 | 6.9 / 6.88 | 0.294 |
| Audio guide | 0 | icon: Play the audio guide | 6.45 / 6.42 | 7.09 / 7.09 | 0.289 |
| window | 578 | He painted it in late June or early July 1889 at Saint-Rémy | 6.64 / 6.62 | 7.11 / 7.09 | 0.281 |
| window | 578 | Saint-Rémy in Provence, where he was a patient at the | 6.64 / 6.63 | 7.11 / 7.09 | 0.281 |
| window | 578 | asylum of Saint-Paul-de-Mausole, working outdoors | 6.71 / 6.64 | 7.18 / 7.11 | 0.278 |
| window | 578 | in front of the motif. | 6.64 / 6.63 | 7.18 / 7.11 | 0.281 |
| window | 578 | He counted it among his best summer canvases, and | 6.72 / 6.64 | 7.2 / 7.11 | 0.278 |
| window | 578 | that September made two studio versions of it: one | 6.73 / 6.72 | 7.2 / 7.19 | 0.277 |
| window | 578 | now in the National Gallery, London, the other a | 6.73 / 6.72 | 7.2 / 7.2 | 0.277 |
| window | 578 | smaller copy for his mother and sister. | 6.73 / 6.69 | 7.21 / 7.2 | 0.277 |
| window | 578 | Weather | 8.31 / 8.21 | 8.71 / 8.69 | 0.216 |
| window | 578 | Summer wind, fast cloud | 8.36 / 8.3 | 8.71 / 8.71 | 0.215 |
| window | 578 | Artist | 8.3 / 8.26 | 8.71 / 8.69 | 0.217 |
| window | 578 | Vincent van Gogh ( Dutch, 1853–1890 ) | 8.37 / 8.32 | 8.7 / 8.69 | 0.214 |
| window | 578 | Date | 8.36 / 8.26 | 8.71 / 8.68 | 0.215 |
| window | 578 | 1889 | 8.38 / 8.38 | 8.71 / 8.71 | 0.214 |
| window | 578 | Medium | 8.35 / 8.25 | 8.69 / 8.69 | 0.215 |
| window | 578 | Oil on canvas | 8.36 / 8.31 | 8.71 / 8.71 | 0.215 |
| window | 578 | Size | 8.29 / 8.19 | 8.71 / 8.67 | 0.217 |
| window | 578 | 73.2 × 93.4 cm | 8.31 / 8.3 | 8.71 / 8.71 | 0.216 |
| window | 578 | Collection | 8.29 / 8.29 | 8.71 / 8.69 | 0.217 |
| window | 578 | The Metropolitan Museum of Art, New York | 8.39 / 8.35 | 8.8 / 8.69 | 0.214 |
| window | 578 | Credit | 8.35 / 8.24 | 8.69 / 8.66 | 0.215 |
| window | 578 | Purchase, The Annenberg Foundation Gift, | 8.41 / 8.4 | 8.83 / 8.73 | 0.213 |
| window | 578 | 1993 | 8.41 / 8.38 | 8.83 / 8.72 | 0.213 |
| window | 578 | Number | 8.34 / 8.24 | 8.69 / 8.66 | 0.215 |
| window | 578 | 1993.132 | 8.41 / 8.39 | 8.83 / 8.81 | 0.213 |
| window | 578 | Photograph: The Metropolitan Museum of Art, New York , open | 6.8 / 6.78 | 7.31 / 7.24 | 0.275 |
| window | 578 | access, public domain. | 6.78 / 6.76 | 7.23 / 7.22 | 0.275 |

### GPU tier · dark · gale · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.75 / 6.74 | 7.29 / 7.21 | 0.276 |
| window | 0 | Room 7 of 8 | 6.72 / 6.71 | 7.21 / 7.2 | 0.278 |
| window | 0 | Gale (large) | 6.84 / 6.84 | 7.39 / 7.32 | 0.273 |
| window | 0 | Northeaster (large) | 6.84 / 6.82 | 7.32 / 7.32 | 0.273 |
| window | 0 | Winslow Homer | 6.82 / 6.82 | 7.32 / 7.3 | 0.274 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 6.8 / 6.73 | 7.3 / 7.3 | 0.275 |
| window | 0 | The whole work. The outline marks the part around you. | 6.84 / 6.82 | 7.4 / 7.39 | 0.273 |
| window | 0 | A northeaster is a winter storm that drives in off the | 6.84 / 6.81 | 7.4 / 7.3 | 0.273 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 6.82 / 6.73 | 7.4 / 7.3 | 0.273 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 6.83 / 6.81 | 7.4 / 7.3 | 0.273 |
| window | 0 | lived and painted for the last decades of his life. | 6.92 / 6.74 | 7.5 / 7.3 | 0.269 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 6.96 / 6.81 | 7.54 / 7.31 | 0.268 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 7.01 / 6.94 | 7.6 / 7.5 | 0.266 |
| window | 0 | lower left. By 1900 he had painted them out and | 7.01 / 6.96 | 7.6 / 7.6 | 0.266 |
| window | 0 | raised a much larger column of spray. What is left is | 7.01 / 6.96 | 7.6 / 7.57 | 0.266 |
| Rooms | 0 | 7 | 7.76 / 7.67 | 9.34 / 9.23 | 0.237 |
| Rooms | 0 | / 8 | 7.74 / 7.66 | 9.31 / 9.23 | 0.238 |
| Audio guide | 0 | Audio guide | 8.17 / 8.12 | 10.71 / 10.59 | 0.222 |
| Audio guide | 0 | About 0:50 | 8.13 / 8.03 | 10.6 / 10.46 | 0.223 |
| Rooms | 0 | icon: Previous room: Wind | 7.8 / 7.69 | 9.45 / 9.32 | 0.235 |
| Rooms | 0 | icon: Next room: Fog | 7.71 / 7.67 | 9.29 / 9.26 | 0.238 |
| Audio guide | 0 | icon: Play the audio guide | 7.9 / 7.85 | 10.19 / 10.02 | 0.231 |
| window | 506 | When he first exhibited this canvas in 1895, two men | 6.73 / 6.71 | 7.2 / 7.2 | 0.277 |
| window | 506 | in foul-weather gear crouched on the rocks at the | 6.73 / 6.73 | 7.29 / 7.2 | 0.277 |
| window | 506 | lower left. By 1900 he had painted them out and | 6.73 / 6.73 | 7.29 / 7.2 | 0.277 |
| window | 506 | raised a much larger column of spray. What is left is | 6.73 / 6.73 | 7.29 / 7.2 | 0.277 |
| window | 506 | rock, water and air: the dark ledge, the green body of | 6.8 / 6.73 | 7.3 / 7.22 | 0.275 |
| window | 506 | the wave and the white burst where they meet. | 6.8 / 6.74 | 7.3 / 7.3 | 0.275 |
| window | 506 | A critic in 1901 praised it for “great natural spaces | 6.8 / 6.73 | 7.3 / 7.29 | 0.275 |
| window | 506 | unmarked by the presence of puny man.” | 6.8 / 6.73 | 7.3 / 7.22 | 0.275 |
| window | 506 | Weather | 8.39 / 8.36 | 8.82 / 8.82 | 0.214 |
| window | 506 | Winter northeaster off the Atlantic | 8.37 / 8.36 | 8.82 / 8.79 | 0.214 |
| window | 506 | Artist | 8.39 / 8.36 | 8.82 / 8.71 | 0.214 |
| window | 506 | Winslow Homer ( American, 1836–1910 ) | 8.39 / 8.37 | 8.91 / 8.82 | 0.214 |
| window | 506 | Date | 8.36 / 8.34 | 8.82 / 8.71 | 0.215 |
| window | 506 | 1895; reworked by 1901 | 8.39 / 8.39 | 8.91 / 8.9 | 0.213 |
| window | 506 | Medium | 8.39 / 8.36 | 8.9 / 8.79 | 0.214 |
| window | 506 | Oil on canvas | 8.39 / 8.39 | 8.91 / 8.91 | 0.213 |
| window | 506 | Size | 8.47 / 8.37 | 8.91 / 8.9 | 0.211 |
| window | 506 | 87.6 × 127 cm | 8.47 / 8.37 | 8.91 / 8.91 | 0.211 |
| window | 506 | Collection | 8.48 / 8.37 | 8.91 / 8.91 | 0.21 |
| window | 506 | The Metropolitan Museum of Art, New York | 8.37 / 8.35 | 8.91 / 8.79 | 0.214 |
| window | 506 | Credit | 8.58 / 8.49 | 9.1 / 9.02 | 0.207 |
| window | 506 | Gift of George A. Hearn, 1910 | 8.5 / 8.38 | 9.02 / 8.91 | 0.21 |
| window | 506 | Number | 8.58 / 8.51 | 9.1 / 9.1 | 0.207 |
| window | 506 | 10.64.5 | 8.51 / 8.51 | 9.1 / 9.1 | 0.209 |
| window | 506 | Photograph: The Metropolitan Museum of Art, New York , open | 7.01 / 6.97 | 7.6 / 7.57 | 0.266 |
| window | 506 | access, public domain. | 7.02 / 6.96 | 7.6 / 7.6 | 0.265 |

### GPU tier · dark · fog · label view

| where | scroll | line | active | inactive | surface |
|---|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.75 / 6.73 | 7.31 / 7.21 | 0.276 |
| window | 0 | Room 8 of 8 | 6.74 / 6.72 | 7.23 / 7.21 | 0.277 |
| window | 0 | Fog (large) | 6.83 / 6.75 | 7.31 / 7.28 | 0.273 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 6.82 / 6.82 | 7.31 / 7.31 | 0.274 |
| window | 0 | Claude Monet | 6.84 / 6.82 | 7.41 / 7.31 | 0.273 |
| window | 0 | French, 1840–1926 · 1900 | 6.83 / 6.82 | 7.38 / 7.31 | 0.273 |
| window | 0 | The whole work. The outline marks the part around you. | 6.88 / 6.88 | 7.44 / 7.42 | 0.271 |
| window | 0 | Without the fog, Monet once remarked, London | 6.9 / 6.88 | 7.44 / 7.42 | 0.27 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 6.89 / 6.88 | 7.44 / 7.42 | 0.271 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 6.88 / 6.86 | 7.44 / 7.41 | 0.271 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 6.88 / 6.83 | 7.44 / 7.38 | 0.271 |
| window | 0 | he came to paint it. | 6.85 / 6.82 | 7.38 / 7.38 | 0.273 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 6.9 / 6.85 | 7.44 / 7.41 | 0.27 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 6.89 / 6.85 | 7.44 / 7.41 | 0.271 |
| window | 0 | Charing Cross Bridge later in the day. Here the bridge | 6.89 / 6.85 | 7.44 / 7.41 | 0.271 |
| Rooms | 0 | 8 | 6.57 / 6.54 | 7.21 / 7.21 | 0.284 |
| Rooms | 0 | / 8 | 6.57 / 6.5 | 7.21 / 7.21 | 0.284 |
| Audio guide | 0 | Audio guide | 6.8 / 6.79 | 7.63 / 7.56 | 0.274 |
| Audio guide | 0 | About 0:50 | 6.81 / 6.77 | 7.63 / 7.56 | 0.274 |
| Rooms | 0 | icon: Previous room: Gale | 6.48 / 6.47 | 7.13 / 7.11 | 0.288 |
| Audio guide | 0 | icon: Play the audio guide | 6.82 / 6.75 | 7.62 / 7.55 | 0.273 |
| window | 532 | He painted Waterloo Bridge in the mornings from his | 6.82 / 6.81 | 7.31 / 7.31 | 0.274 |
| window | 532 | fifth-floor window at the Savoy Hotel, moving on to | 6.82 / 6.81 | 7.31 / 7.31 | 0.274 |
| window | 532 | Charing Cross Bridge later in the day. Here the bridge | 6.82 / 6.81 | 7.31 / 7.31 | 0.274 |
| window | 532 | is a dark band of arches, and the city behind it is only | 6.82 / 6.81 | 7.31 / 7.31 | 0.274 |
| window | 532 | chimneys and towers in the haze. | 6.82 / 6.81 | 7.31 / 7.31 | 0.274 |
| window | 532 | He finished the London pictures in his studio at | 6.82 / 6.82 | 7.33 / 7.31 | 0.273 |
| window | 532 | Giverny, and would not release any of them until he | 6.84 / 6.83 | 7.4 / 7.38 | 0.273 |
| window | 532 | was satisfied with the series as a whole. | 6.84 / 6.83 | 7.4 / 7.4 | 0.273 |
| window | 532 | Weather | 8.39 / 8.38 | 8.91 / 8.8 | 0.214 |
| window | 532 | Winter fog and coal smoke | 8.38 / 8.38 | 8.91 / 8.91 | 0.214 |
| window | 532 | Artist | 8.4 / 8.38 | 8.91 / 8.8 | 0.213 |
| window | 532 | Claude Monet ( French, 1840–1926 ) | 8.4 / 8.4 | 8.94 / 8.91 | 0.213 |
| window | 532 | Date | 8.44 / 8.44 | 8.93 / 8.93 | 0.212 |
| window | 532 | 1900 | 8.42 / 8.39 | 8.93 / 8.93 | 0.213 |
| window | 532 | Medium | 8.44 / 8.44 | 8.93 / 8.93 | 0.212 |
| window | 532 | Oil on canvas | 8.43 / 8.41 | 8.93 / 8.93 | 0.212 |
| window | 532 | Size | 8.43 / 8.43 | 8.93 / 8.92 | 0.212 |
| window | 532 | 65.4 × 92.6 cm | 8.42 / 8.42 | 8.93 / 8.93 | 0.212 |
| window | 532 | Collection | 8.4 / 8.38 | 8.93 / 8.91 | 0.213 |
| window | 532 | The Art Institute of Chicago | 8.44 / 8.39 | 8.94 / 8.91 | 0.212 |
| window | 532 | Credit | 8.39 / 8.37 | 8.91 / 8.81 | 0.214 |
| window | 532 | Gift of Mrs. Mortimer B. Harris | 8.42 / 8.36 | 8.93 / 8.89 | 0.212 |
| window | 532 | Number | 8.39 / 8.37 | 8.91 / 8.81 | 0.214 |
| window | 532 | 1984.1173 | 8.39 / 8.38 | 8.91 / 8.91 | 0.214 |
| window | 532 | Photograph: The Art Institute of Chicago , open access, public | 6.89 / 6.85 | 7.43 / 7.41 | 0.271 |
| window | 532 | domain. | 6.85 / 6.76 | 7.31 / 7.21 | 0.273 |

### GPU tier · dark · rooms view · active (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 6.51 | 6.93 | 7.47 | 7.62 | 6.51 | 6.54 | 6.74 | 6.73 |
| 8 rooms | 6.27 | 6.91 | 7.17 | 7.65 | 6.65 | 6.54 | 6.72 | 6.65 |
| Eight skies, 1608–1900 | 6.61 | 6.93 | 7.46 | 7.62 | 6.69 | 6.63 | 6.71 | 6.81 |
| For most of the history of European painting the sky | 6.61 | 6.91 | 7.34 | 7.62 | 6.69 | 6.64 | 6.73 | 6.82 |
| was the back wall of the picture. This exhibition | 6.61 | 6.84 | 7.39 | 7.62 | 6.69 | 6.64 | 6.73 | 6.81 |
| follows it becoming the subject: eight rooms, each | 6.61 | 6.84 | 7.36 | 7.41 | 6.72 | 6.7 | 6.73 | 6.81 |
| holding one work, from a Dutch winter in the Little Ice | 6.62 | 6.83 | 7.34 | 7.29 | 6.79 | 6.72 | 6.73 | 6.82 |
| Age to a London fog that was largely coal smoke. | 6.62 | 6.81 | 7.36 | 7.3 | 6.79 | 6.69 | 6.73 | 6.81 |
| Each work fills the room. Its label sits beside it, and | 6.63 | 6.79 | 7.35 | 7.3 | 6.82 | 6.69 | 6.73 | 6.83 |
| the audio guide reads the label aloud in your | 6.65 | 6.81 | 7.37 | 7.31 | 6.82 | 6.71 | 6.73 | 6.84 |
| browser’s own voice. | 6.74 | 6.91 | 7.46 | 7.41 | 6.76 | 6.69 | 6.75 | 6.85 |
| Rooms | 6.73 | 6.82 | 7.41 | 7.35 | 6.87 | 6.68 | 6.74 | 6.77 |
| 01 · Frost | 4.97 | 6.93 | 7.44 | 7.45 | 6.79 | 6.74 | 6.82 | 6.86 |
| · you are here | 4.96 | 5.05 | 5.44 | 5.51 | 5.01 | 4.93 | 4.97 | 5.07 |
| Winter Landscape with Ice Skaters | 4.96 | 6.91 | 7.36 | 7.55 | 6.72 | 6.69 | 6.82 | 6.87 |
| Hendrick Avercamp , c. 1608 | 4.96 | 6.91 | 7.45 | 7.39 | 6.73 | 6.69 | 6.84 | 6.88 |
| 02 · Cloud | 6.73 | 5.03 | 7.55 | 7.25 | 6.79 | 6.7 | 6.82 | 6.88 |
| The Windmill at Wijk bij Duurstede | 6.71 | 5.03 | 7.5 | 7.57 | 6.73 | 6.74 | 6.81 | 6.86 |
| Jacob van Ruisdael , c. 1668–70 | 6.76 | 5.03 | 7.48 | 7.71 | 6.79 | 6.76 | 6.82 | 6.83 |
| 03 · Clearing | 6.76 | 6.84 | 5.51 | 7.73 | 6.81 | 6.76 | 6.96 | 6.83 |
| View from Mount Holyoke, Northampton, | 6.76 | 6.83 | 5.46 | 7.71 | 6.73 | 6.78 | 6.93 | 6.85 |
| Massachusetts, after a Thunderstorm—The | 6.76 | 6.82 | 5.44 | 7.64 | 6.73 | 6.78 | 6.96 | 6.85 |
| Oxbow | 6.78 | 6.82 | 5.51 | 7.61 | 6.81 | 6.81 | 6.96 | 6.85 |
| Thomas Cole , 1836 | 6.78 | 6.83 | 5.44 | 6.71 | 6.74 | 6.78 | 7 | 6.85 |
| 04 · Thunder | 6.68 | 7 | 7.49 | 5.51 | 6.69 | 6.62 | 6.75 | 6.82 |
| Approaching Thunder Storm | 6.61 | 6.93 | 7.46 | 5.49 | 6.69 | 6.64 | 6.73 | 6.82 |
| Martin Johnson Heade , 1859 | 6.61 | 7 | 7.47 | 5.49 | 6.69 | 6.64 | 6.73 | 6.82 |
| 05 · Rain | 6.69 | 7 | 7.52 | 7.62 | 4.94 | 6.71 | 6.82 | 6.82 |
| Paris Street; Rainy Day | 6.68 | 6.93 | 7.46 | 7.42 | 4.96 | 6.72 | 6.8 | 6.82 |
| Gustave Caillebotte , 1877 | 6.68 | 6.93 | 7.46 | 7.4 | 5.01 | 6.73 | 6.8 | 6.82 |
| 06 · Wind | 6.71 | 7 | 7.47 | 7.32 | 6.76 | 4.95 | 6.81 | 6.83 |
| Wheat Field with Cypresses | 6.63 | 6.79 | 7.39 | 7.32 | 6.81 | 4.93 | 6.73 | 6.83 |
| Vincent van Gogh , 1889 | 6.7 | 6.92 | 7.4 | 7.32 | 6.82 | 4.94 | 6.73 | 6.85 |
| 07 · Gale | 6.78 | 6.93 | 7.49 | 7.42 | 6.85 | 6.69 | 5.02 | 6.84 |
| Northeaster | 6.74 | 6.93 | 7.48 | 7.42 | 6.84 | 6.69 | 5.02 | 6.84 |
| Winslow Homer , 1895; reworked by 1901 | 6.72 | 6.91 | 7.36 | 7.39 | 6.74 | 6.74 | 5.02 | 6.85 |
| 08 · Fog | 6.76 | 6.93 | 7.48 | 7.52 | 6.79 | 6.74 | 6.84 | 5.07 |
| Waterloo Bridge, Gray Weather | 6.61 | 6.91 | 7.37 | 7.52 | 6.69 | 6.62 | 6.71 | 5.02 |
| Claude Monet , 1900 | 6.61 | 6.91 | 7.49 | 7.28 | 6.69 | 6.62 | 6.73 | 5.02 |
| Viewing | 8.3 | 8.38 | 9.04 | 9.08 | 8.33 | 8.23 | 8.36 | 8.36 |
| Reduce transparency | 8.3 | 8.47 | 9.03 | 9.06 | 8.33 | 8.25 | 8.36 | 8.36 |
| Frosts the label and the controls so the painting shows | 8.22 | 8.38 | 8.86 | 8.9 | 8.33 | 8.33 | 8.34 | 8.36 |
| through less. | 8.22 | 8.37 | 9 | 9.03 | 8.33 | 8.25 | 8.34 | 8.37 |
| Photographs | 6.71 | 6.91 | 7.47 | 7.42 | 6.82 | 6.71 | 6.81 | 6.83 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 6.65 | 6.81 | 7.37 | 7.31 | 6.83 | 6.71 | 6.73 | 6.84 |
| Rijksmuseum, Amsterdam , open access, public domain. | 6.65 | 6.83 | 7.36 | 7.32 | 6.82 | 6.69 | 6.75 | 6.84 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 6.67 | 6.83 | 7.36 | 7.32 | 6.84 | 6.69 | 6.75 | 6.84 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 6.73 | 6.91 | 7.36 | 7.42 | 6.74 | 6.73 | 6.82 | 6.87 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 6.74 | 6.91 | 7.36 | 7.42 | 6.74 | 6.73 | 6.82 | 6.86 |
| Metropolitan Museum of Art, New York , open access, public | 6.71 | 6.91 | 7.36 | 7.14 | 6.72 | 6.69 | 6.73 | 6.86 |
| domain. | 6.73 | 6.75 | 7.38 | 7.32 | 6.81 | 6.62 | 6.75 | 6.89 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 6.71 | 6.91 | 7.4 | 7.21 | 6.73 | 6.69 | 6.81 | 6.88 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 6.75 | 6.91 | 7.52 | 7.69 | 6.73 | 6.75 | 6.74 | 6.85 |
| Chicago , open access, public domain. | 6.76 | 6.83 | 7.39 | 6.21 | 6.73 | 6.73 | 6.92 | 6.82 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 6.76 | 6.86 | 7.52 | 7.71 | 6.73 | 6.76 | 6.74 | 6.83 |
| Museum of Art, New York , open access, public domain. | 6.76 | 6.84 | 7.52 | 7.71 | 6.79 | 6.75 | 6.92 | 6.83 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 6.76 | 6.82 | 7.52 | 7.71 | 6.73 | 6.75 | 6.94 | 6.85 |
| New York , open access, public domain. | 6.76 | 6.82 | 7.49 | 7.5 | 6.81 | 6.75 | 6.96 | 6.84 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 6.76 | 6.83 | 7.44 | 6.89 | 6.73 | 6.78 | 6.96 | 6.85 |

### GPU tier · dark · rooms view · inactive (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 6.91 | 7.51 | 8.33 | 8.54 | 6.98 | 7 | 7.21 | 7.21 |
| 8 rooms | 6.69 | 7.51 | 7.98 | 8.53 | 7.11 | 6.99 | 7.2 | 7.21 |
| Eight skies, 1608–1900 | 7.09 | 7.51 | 8.22 | 8.53 | 7.16 | 7.09 | 7.2 | 7.31 |
| For most of the history of European painting the sky | 7.09 | 7.48 | 8.11 | 8.53 | 7.17 | 7.18 | 7.2 | 7.31 |
| was the back wall of the picture. This exhibition | 7.09 | 7.41 | 8.22 | 8.52 | 7.19 | 7.11 | 7.2 | 7.31 |
| follows it becoming the subject: eight rooms, each | 7.09 | 7.41 | 8.11 | 8.28 | 7.28 | 7.18 | 7.27 | 7.31 |
| holding one work, from a Dutch winter in the Little Ice | 7.09 | 7.41 | 8.09 | 8.13 | 7.28 | 7.2 | 7.3 | 7.3 |
| Age to a London fog that was largely coal smoke. | 7.09 | 7.38 | 8.12 | 8.08 | 7.28 | 7.2 | 7.3 | 7.31 |
| Each work fills the room. Its label sits beside it, and | 7.09 | 7.37 | 8.12 | 8.07 | 7.3 | 7.21 | 7.29 | 7.4 |
| the audio guide reads the label aloud in your | 7.11 | 7.39 | 8.19 | 8.17 | 7.31 | 7.21 | 7.3 | 7.4 |
| browser’s own voice. | 7.21 | 7.49 | 8.33 | 8.19 | 7.31 | 7.23 | 7.3 | 7.33 |
| Rooms | 7.25 | 7.31 | 8.23 | 8.19 | 7.4 | 7.12 | 7.22 | 7.31 |
| 01 · Frost | 5.31 | 7.51 | 8.32 | 8.3 | 7.28 | 7.22 | 7.39 | 7.42 |
| · you are here | 5.25 | 5.46 | 6.01 | 6.09 | 5.31 | 5.25 | 5.31 | 5.4 |
| Winter Landscape with Ice Skaters | 5.25 | 7.51 | 8.2 | 8.52 | 7.28 | 7.22 | 7.39 | 7.42 |
| Hendrick Avercamp , c. 1608 | 5.29 | 7.48 | 8.3 | 8.18 | 7.28 | 7.22 | 7.39 | 7.44 |
| 02 · Cloud | 7.26 | 5.45 | 8.42 | 8.03 | 7.28 | 7.23 | 7.4 | 7.43 |
| The Windmill at Wijk bij Duurstede | 7.25 | 5.45 | 8.34 | 8.51 | 7.28 | 7.21 | 7.3 | 7.41 |
| Jacob van Ruisdael , c. 1668–70 | 7.26 | 5.45 | 8.35 | 8.63 | 7.28 | 7.23 | 7.4 | 7.38 |
| 03 · Clearing | 7.27 | 7.41 | 6.08 | 8.74 | 7.28 | 7.23 | 7.54 | 7.38 |
| View from Mount Holyoke, Northampton, | 7.27 | 7.38 | 6.01 | 8.63 | 7.28 | 7.24 | 7.5 | 7.41 |
| Massachusetts, after a Thunderstorm—The | 7.28 | 7.38 | 6.01 | 8.58 | 7.28 | 7.24 | 7.52 | 7.41 |
| Oxbow | 7.28 | 7.38 | 6.11 | 8.56 | 7.3 | 7.33 | 7.6 | 7.41 |
| Thomas Cole , 1836 | 7.29 | 7.38 | 5.95 | 7.32 | 7.28 | 7.31 | 7.6 | 7.41 |
| 04 · Thunder | 7.1 | 7.6 | 8.35 | 6.09 | 7.16 | 7.09 | 7.29 | 7.31 |
| Approaching Thunder Storm | 7.09 | 7.51 | 8.33 | 6.09 | 7.17 | 7.11 | 7.2 | 7.31 |
| Martin Johnson Heade , 1859 | 7.1 | 7.58 | 8.33 | 6.09 | 7.17 | 7.18 | 7.2 | 7.31 |
| 05 · Rain | 7.17 | 7.58 | 8.36 | 8.52 | 5.23 | 7.2 | 7.3 | 7.31 |
| Paris Street; Rainy Day | 7.1 | 7.51 | 8.33 | 8.3 | 5.29 | 7.19 | 7.3 | 7.31 |
| Gustave Caillebotte , 1877 | 7.1 | 7.51 | 8.24 | 8.18 | 5.3 | 7.2 | 7.3 | 7.31 |
| 06 · Wind | 7.19 | 7.58 | 8.33 | 8.17 | 7.3 | 5.24 | 7.3 | 7.4 |
| Wheat Field with Cypresses | 7.09 | 7.37 | 8.22 | 8.17 | 7.3 | 5.25 | 7.22 | 7.4 |
| Vincent van Gogh , 1889 | 7.19 | 7.51 | 8.25 | 8.17 | 7.3 | 5.24 | 7.29 | 7.4 |
| 07 · Gale | 7.31 | 7.51 | 8.34 | 8.19 | 7.32 | 7.23 | 5.31 | 7.41 |
| Northeaster | 7.21 | 7.51 | 8.33 | 8.19 | 7.32 | 7.22 | 5.33 | 7.41 |
| Winslow Homer , 1895; reworked by 1901 | 7.19 | 7.49 | 8.22 | 8.19 | 7.3 | 7.21 | 5.33 | 7.41 |
| 08 · Fog | 7.21 | 7.51 | 8.33 | 8.41 | 7.28 | 7.22 | 7.39 | 5.4 |
| Waterloo Bridge, Gray Weather | 7.09 | 7.49 | 8.22 | 8.42 | 7.16 | 7.09 | 7.2 | 5.32 |
| Claude Monet , 1900 | 7.09 | 7.48 | 8.32 | 8.05 | 7.16 | 7.09 | 7.2 | 5.32 |
| Viewing | 8.66 | 8.91 | 9.77 | 9.89 | 8.75 | 8.56 | 8.82 | 8.8 |
| Reduce transparency | 8.67 | 8.91 | 9.7 | 9.76 | 8.67 | 8.67 | 8.79 | 8.8 |
| Frosts the label and the controls so the painting shows | 8.67 | 8.91 | 9.59 | 9.52 | 8.78 | 8.68 | 8.79 | 8.8 |
| through less. | 8.65 | 8.89 | 9.79 | 9.68 | 8.77 | 8.68 | 8.79 | 8.81 |
| Photographs | 7.18 | 7.41 | 8.33 | 8.19 | 7.3 | 7.22 | 7.3 | 7.35 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 7.11 | 7.39 | 8.19 | 8.17 | 7.31 | 7.21 | 7.3 | 7.4 |
| Rijksmuseum, Amsterdam , open access, public domain. | 7.18 | 7.39 | 8.22 | 8.17 | 7.3 | 7.2 | 7.3 | 7.4 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 7.18 | 7.41 | 8.22 | 8.19 | 7.32 | 7.2 | 7.31 | 7.38 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 7.21 | 7.49 | 8.22 | 8.19 | 7.3 | 7.2 | 7.32 | 7.42 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 7.21 | 7.49 | 8.19 | 8.28 | 7.28 | 7.2 | 7.32 | 7.42 |
| Metropolitan Museum of Art, New York , open access, public | 7.21 | 7.41 | 8.12 | 7.9 | 7.28 | 7.2 | 7.3 | 7.42 |
| domain. | 7.2 | 7.31 | 8.22 | 8.1 | 7.38 | 7.13 | 7.3 | 7.43 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 7.22 | 7.41 | 8.22 | 8.03 | 7.28 | 7.21 | 7.3 | 7.42 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 7.25 | 7.49 | 8.42 | 8.62 | 7.21 | 7.21 | 7.3 | 7.41 |
| Chicago , open access, public domain. | 7.26 | 7.31 | 8.2 | 6.66 | 7.21 | 7.2 | 7.5 | 7.31 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 7.27 | 7.41 | 8.37 | 8.66 | 7.28 | 7.23 | 7.3 | 7.38 |
| Museum of Art, New York , open access, public domain. | 7.27 | 7.41 | 8.37 | 8.71 | 7.28 | 7.2 | 7.5 | 7.38 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 7.27 | 7.38 | 8.37 | 8.63 | 7.28 | 7.2 | 7.5 | 7.41 |
| New York , open access, public domain. | 7.28 | 7.38 | 8.32 | 8.37 | 7.3 | 7.22 | 7.6 | 7.38 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 7.28 | 7.38 | 8.3 | 7.55 | 7.28 | 7.24 | 7.57 | 7.41 |

## CSS tier

`?tier=css`, DPR 1, 1440 × 900, active pose. 1916 line readings, 0 under floor. Worst p10 4.95: dark, active, rain, rooms view, window, “05 · Rain”.

### CSS tier · light · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 12.6 / 12.24 | 0.903 |
| window | 0 | Room 1 of 8 | 13.76 / 13.62 | 0.952 |
| window | 0 | Frost (large) | 12.38 / 12.24 | 0.894 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 12.88 / 12.16 | 0.914 |
| window | 0 | Hendrick Avercamp | 12.37 / 12.09 | 0.893 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 12.46 / 12.18 | 0.897 |
| window | 0 | The whole work. The outline marks the part around you. | 11.15 / 10.47 | 0.841 |
| window | 0 | Avercamp made his name painting winter, in the years | 11.25 / 10.84 | 0.845 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 11.27 / 11.05 | 0.846 |
| window | 0 | Countries. Here a whole village has moved onto the | 11.26 / 11.01 | 0.845 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 11.09 / 10.79 | 0.838 |
| window | 0 | sledge on the right, a church on the left. | 10.99 / 10.54 | 0.833 |
| window | 0 | Look at how the air is built. The figures in front are | 10.66 / 10.36 | 0.818 |
| window | 0 | sharp and full of colour; a few hundred metres back | 10.63 / 10.28 | 0.817 |
| Rooms | 0 | 1 | 12.47 / 12.01 | 0.897 |
| Rooms | 0 | / 8 | 12.82 / 12.65 | 0.912 |
| Audio guide | 0 | Audio guide | 13.01 / 12.75 | 0.92 |
| Audio guide | 0 | About 0:51 | 13.11 / 13 | 0.924 |
| Rooms | 0 | icon: Next room: Cloud | 12.98 / 12.94 | 0.919 |
| Audio guide | 0 | icon: Play the audio guide | 12 / 11.29 | 0.877 |
| window | 554 | Look at how the air is built. The figures in front are | 13.13 / 12.5 | 0.925 |
| window | 554 | sharp and full of colour; a few hundred metres back | 13.03 / 12.42 | 0.921 |
| window | 554 | they thin into grey-white haze, and the far bank all | 12.93 / 12.26 | 0.917 |
| window | 554 | but dissolves. That haze is the weather: cold, damp | 12.88 / 12.16 | 0.915 |
| window | 554 | air thick enough to carry the light. | 12.56 / 12.09 | 0.901 |
| window | 554 | Avercamp signed the picture on the wall of a wooden | 12.78 / 12.26 | 0.911 |
| window | 554 | shed on the right, among the scratched graffiti, | 12.64 / 12.23 | 0.905 |
| window | 554 | where it is easy to miss. | 12.07 / 11.93 | 0.88 |
| window | 554 | Weather | 10.07 / 9.94 | 0.792 |
| window | 554 | Hard frost, haze over the ice | 11.16 / 10.03 | 0.841 |
| window | 554 | Artist | 9.73 / 9.71 | 0.776 |
| window | 554 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 11.03 / 10.01 | 0.835 |
| window | 554 | Date | 9.56 / 9.55 | 0.768 |
| window | 554 | c. 1608 | 10.02 / 9.85 | 0.79 |
| window | 554 | Medium | 9.53 / 9.52 | 0.767 |
| window | 554 | Oil on panel | 10.08 / 10 | 0.792 |
| window | 554 | Size | 9.69 / 9.66 | 0.774 |
| window | 554 | 77.3 × 131.9 cm | 10.03 / 9.95 | 0.79 |
| window | 554 | Collection | 10.17 / 9.89 | 0.797 |
| window | 554 | Rijksmuseum, Amsterdam | 10.25 / 10.11 | 0.8 |
| window | 554 | Credit | 9.75 / 9.66 | 0.778 |
| window | 554 | Purchased with the support of the | 10.09 / 10.03 | 0.793 |
| window | 554 | Vereniging Rembrandt | 10.07 / 9.97 | 0.792 |
| window | 554 | Number | 9.43 / 9.28 | 0.762 |
| window | 554 | SK-A-1718 | 9.97 / 9.87 | 0.787 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 10.6 / 10.28 | 0.816 |
| window | 554 | domain. | 10.25 / 10.19 | 0.801 |

### CSS tier · light · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.95 / 9.87 | 0.787 |
| window | 0 | Room 2 of 8 | 10.04 / 9.97 | 0.791 |
| window | 0 | Cloud (large) | 9.95 / 9.87 | 0.787 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 10.21 / 9.97 | 0.799 |
| window | 0 | Jacob van Ruisdael | 10.12 / 10.04 | 0.795 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 10.22 / 10.12 | 0.799 |
| window | 0 | The whole work. The outline marks the part around you. | 10.71 / 10.44 | 0.821 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 10.87 / 10.55 | 0.828 |
| window | 0 | more than half the canvas, and he paints it as a | 10.87 / 10.62 | 0.828 |
| window | 0 | structure: banks of cumulus heaped over one | 10.87 / 10.69 | 0.828 |
| window | 0 | another, grey underneath, lit at their edges by a sun | 10.96 / 10.87 | 0.832 |
| window | 0 | we cannot see. | 11.12 / 11.03 | 0.839 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 11.56 / 11.4 | 0.859 |
| window | 0 | A sailing boat is out on the water, the towers of | 11.58 / 11.47 | 0.859 |
| Rooms | 0 | 2 | 9.97 / 9.95 | 0.788 |
| Rooms | 0 | / 8 | 10.2 / 10.11 | 0.798 |
| Audio guide | 0 | Audio guide | 10.2 / 10.13 | 0.798 |
| Audio guide | 0 | About 0:49 | 10.13 / 10.05 | 0.795 |
| Rooms | 0 | icon: Previous room: Frost | 9.97 / 9.87 | 0.788 |
| Rooms | 0 | icon: Next room: Clearing | 9.87 / 9.81 | 0.783 |
| Audio guide | 0 | icon: Play the audio guide | 10.06 / 9.98 | 0.792 |
| window | 554 | Below, the mill stands near the bank of the river Lek. | 10.2 / 9.94 | 0.798 |
| window | 554 | A sailing boat is out on the water, the towers of | 10.2 / 9.87 | 0.798 |
| window | 554 | Duurstede castle and the church rise in the distance, | 10.2 / 9.95 | 0.798 |
| window | 554 | and a few women walk along the bank, very small | 10.2 / 9.97 | 0.798 |
| window | 554 | against the mill. | 10.04 / 9.97 | 0.791 |
| window | 554 | Dutch painters of the seventeenth century made the | 10.46 / 10.14 | 0.81 |
| window | 554 | sky a subject in its own right. Few made it carry as | 10.62 / 10.2 | 0.817 |
| window | 554 | much of a picture as this. | 10.29 / 10.2 | 0.802 |
| window | 554 | Weather | 9.72 / 9.61 | 0.776 |
| window | 554 | Heaped cumulus, sun breaking through | 9.72 / 9.28 | 0.776 |
| window | 554 | Artist | 9.86 / 9.84 | 0.783 |
| window | 554 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 9.68 / 9.3 | 0.774 |
| window | 554 | Date | 10.01 / 9.95 | 0.789 |
| window | 554 | c. 1668–70 | 9.54 / 9.45 | 0.768 |
| window | 554 | Medium | 10.01 / 9.93 | 0.789 |
| window | 554 | Oil on canvas | 9.72 / 9.68 | 0.776 |
| window | 554 | Size | 10.03 / 10.01 | 0.79 |
| window | 554 | 83 × 101 cm | 9.85 / 9.78 | 0.782 |
| window | 554 | Collection | 9.95 / 9.94 | 0.787 |
| window | 554 | Rijksmuseum, Amsterdam | 9.77 / 9.68 | 0.778 |
| window | 554 | Credit | 9.95 / 9.87 | 0.787 |
| window | 554 | On loan from the City of Amsterdam (A. van | 9.91 / 9.84 | 0.785 |
| window | 554 | der Hoop Bequest) | 10.08 / 10.01 | 0.793 |
| window | 554 | Number | 10.29 / 10.14 | 0.802 |
| window | 554 | SK-C-211 | 10.5 / 10.42 | 0.812 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 11.47 / 11.37 | 0.855 |
| window | 554 | domain. | 11.33 / 11.18 | 0.849 |

### CSS tier · light · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 10.07 / 9.87 | 0.792 |
| window | 0 | Room 3 of 8 | 10.45 / 10.37 | 0.809 |
| window | 0 | Clearing (large) | 10.13 / 9.95 | 0.795 |
| window | 0 | View from Mount Holyoke, (large) | 10.22 / 9.95 | 0.799 |
| window | 0 | Northampton, Massachusetts, (large) | 10.25 / 9.95 | 0.8 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 10.27 / 10.04 | 0.801 |
| window | 0 | Thomas Cole | 10.07 / 9.89 | 0.792 |
| window | 0 | American, born England, 1801–1848 · 1836 | 10.26 / 10 | 0.801 |
| window | 0 | The whole work. The outline marks the part around you. | 10.12 / 10.02 | 0.794 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 9.99 / 9.93 | 0.788 |
| window | 0 | valley. On the left it still hangs over wild, broken | 9.93 / 9.91 | 0.786 |
| window | 0 | trees, and rain falls in grey veils across the hills. On | 9.94 / 9.87 | 0.786 |
| window | 0 | the right the air has cleared over cleared land: fields, | 9.95 / 9.81 | 0.787 |
| window | 0 | farms and the river’s great loop. | 9.87 / 9.87 | 0.783 |
| Rooms | 0 | 3 | 9.75 / 9.62 | 0.778 |
| Rooms | 0 | / 8 | 9.96 / 9.85 | 0.787 |
| Audio guide | 0 | Audio guide | 9.57 / 9.3 | 0.769 |
| Audio guide | 0 | About 0:50 | 9.56 / 9.47 | 0.769 |
| Rooms | 0 | icon: Previous room: Cloud | 9.48 / 9.4 | 0.765 |
| Rooms | 0 | icon: Next room: Thunder | 9.49 / 9.41 | 0.765 |
| Audio guide | 0 | icon: Play the audio guide | 9.54 / 9.38 | 0.767 |
| window | 610 | Cole divided the picture along a diagonal, and the | 10.27 / 10.04 | 0.801 |
| window | 610 | weather does the dividing. He painted it for the 1836 | 10.27 / 10.06 | 0.801 |
| window | 610 | annual exhibition of the National Academy of Design, | 10.27 / 10.04 | 0.801 |
| window | 610 | calling the view from Mount Holyoke “about the finest | 10.27 / 10.04 | 0.801 |
| window | 610 | scene I have in my sketchbook.” | 10.19 / 9.95 | 0.798 |
| window | 610 | Look for the painter himself near the bottom of the | 10.27 / 9.98 | 0.801 |
| window | 610 | canvas: a small figure at an easel among the rocks, | 10.33 / 10 | 0.804 |
| window | 610 | turning back toward us. | 10.23 / 9.98 | 0.8 |
| window | 610 | Weather | 9.24 / 9.13 | 0.753 |
| window | 610 | Thunderstorm passing, sun on the valley | 9.55 / 9.31 | 0.768 |
| window | 610 | Artist | 9.32 / 9.29 | 0.757 |
| window | 610 | Thomas Cole ( American, born England, | 9.48 / 9.31 | 0.765 |
| window | 610 | 1801–1848 ) | 9.32 / 9.31 | 0.757 |
| window | 610 | Date | 9.4 / 9.35 | 0.761 |
| window | 610 | 1836 | 9.31 / 9.25 | 0.757 |
| window | 610 | Medium | 9.32 / 9.26 | 0.757 |
| window | 610 | Oil on canvas | 9.25 / 9.18 | 0.754 |
| window | 610 | Size | 9.09 / 9.07 | 0.746 |
| window | 610 | 130.8 × 193 cm | 9.15 / 9.08 | 0.749 |
| window | 610 | Collection | 9.07 / 9.01 | 0.745 |
| window | 610 | The Metropolitan Museum of Art, New York | 9.05 / 9.01 | 0.745 |
| window | 610 | Credit | 9.05 / 8.98 | 0.745 |
| window | 610 | Gift of Mrs. Russell Sage, 1908 | 9.03 / 8.98 | 0.743 |
| window | 610 | Number | 9.04 / 8.96 | 0.744 |
| window | 610 | 08.228 | 8.9 / 8.9 | 0.737 |
| window | 610 | Photograph: The Metropolitan Museum of Art, New York , open | 9.94 / 9.79 | 0.786 |
| window | 610 | access, public domain. | 9.77 / 9.68 | 0.778 |

### CSS tier · light · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.84 / 9.67 | 0.782 |
| window | 0 | Room 4 of 8 | 9.84 / 9.67 | 0.781 |
| window | 0 | Thunder (large) | 10.03 / 9.84 | 0.79 |
| window | 0 | Approaching Thunder Storm (large) | 10.03 / 10.01 | 0.79 |
| window | 0 | Martin Johnson Heade | 10.19 / 9.95 | 0.798 |
| window | 0 | American, 1819–1904 · 1859 | 10.31 / 10.03 | 0.803 |
| window | 0 | The whole work. The outline marks the part around you. | 10.3 / 10.2 | 0.802 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 10.38 / 10.13 | 0.806 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 10.3 / 10.07 | 0.802 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 10.03 / 9.89 | 0.79 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 9.85 / 9.84 | 0.782 |
| window | 0 | rower pulls for shore; a white sail stands out against | 9.79 / 9.77 | 0.779 |
| window | 0 | the dark. | 9.75 / 9.6 | 0.778 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 9.91 / 9.69 | 0.785 |
| Rooms | 0 | 4 | 10.31 / 10.22 | 0.802 |
| Rooms | 0 | / 8 | 10.7 / 10.37 | 0.819 |
| Audio guide | 0 | Audio guide | 11.58 / 11.18 | 0.857 |
| Audio guide | 0 | About 0:53 | 11.6 / 10.93 | 0.858 |
| Rooms | 0 | icon: Previous room: Clearing | 10.38 / 10.12 | 0.805 |
| Rooms | 0 | icon: Next room: Rain | 11.58 / 11.22 | 0.856 |
| Audio guide | 0 | icon: Play the audio guide | 10.73 / 10.37 | 0.821 |
| window | 618 | holds: not the storm itself but the minute before it. | 10.01 / 9.93 | 0.789 |
| window | 618 | Painted two years before the Civil War, it has often | 10.03 / 10.01 | 0.79 |
| window | 618 | been read as a picture of a country waiting for | 10.03 / 10.01 | 0.79 |
| window | 618 | something to break. Heade based it on a storm he | 10.13 / 10.03 | 0.795 |
| window | 618 | had watched from Prudence Island, in the bay, | 10.29 / 10.03 | 0.802 |
| window | 618 | around 1858. | 10.2 / 10.02 | 0.798 |
| window | 618 | Weather | 9.58 / 9.43 | 0.769 |
| window | 618 | Thunderstorm approaching over still water | 9.69 / 9.61 | 0.775 |
| window | 618 | Artist | 9.58 / 9.43 | 0.769 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 9.68 / 9.62 | 0.774 |
| window | 618 | 1819–1904 ) | 9.6 / 9.6 | 0.77 |
| window | 618 | Date | 9.49 / 9.43 | 0.765 |
| window | 618 | 1859 | 9.57 / 9.57 | 0.769 |
| window | 618 | Medium | 9.37 / 9.34 | 0.76 |
| window | 618 | Oil on canvas | 9.37 / 9.37 | 0.76 |
| window | 618 | Size | 9.35 / 9.28 | 0.758 |
| window | 618 | 71.1 × 111.8 cm | 9.43 / 9.35 | 0.762 |
| window | 618 | Collection | 9.48 / 9.41 | 0.765 |
| window | 618 | The Metropolitan Museum of Art, New York | 9.34 / 9.15 | 0.758 |
| window | 618 | Credit | 9.09 / 8.97 | 0.746 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 8.99 / 8.95 | 0.741 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 8.94 / 8.93 | 0.739 |
| window | 618 | 1975 | 8.92 / 8.92 | 0.738 |
| window | 618 | Number | 8.78 / 8.69 | 0.732 |
| window | 618 | 1975.160 | 8.95 / 8.94 | 0.739 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 10.12 / 9.7 | 0.794 |
| window | 620 | holds: not the storm itself but the minute before it. | 10.01 / 9.93 | 0.789 |
| window | 620 | Painted two years before the Civil War, it has often | 10.03 / 10.01 | 0.79 |
| window | 620 | been read as a picture of a country waiting for | 10.03 / 10.01 | 0.79 |
| window | 620 | something to break. Heade based it on a storm he | 10.11 / 10.03 | 0.794 |
| window | 620 | had watched from Prudence Island, in the bay, | 10.29 / 10.03 | 0.802 |
| window | 620 | around 1858. | 10.2 / 10.02 | 0.798 |
| window | 620 | Weather | 9.58 / 9.43 | 0.769 |
| window | 620 | Thunderstorm approaching over still water | 9.69 / 9.61 | 0.775 |
| window | 620 | Artist | 9.58 / 9.43 | 0.769 |
| window | 620 | Martin Johnson Heade ( American, 1819–1904 | 9.68 / 9.66 | 0.774 |
| window | 620 | 1819–1904 ) | 9.6 / 9.6 | 0.77 |
| window | 620 | Date | 9.5 / 9.43 | 0.766 |
| window | 620 | 1859 | 9.59 / 9.57 | 0.77 |
| window | 620 | Medium | 9.43 / 9.34 | 0.762 |
| window | 620 | Oil on canvas | 9.37 / 9.37 | 0.76 |
| window | 620 | Size | 9.34 / 9.28 | 0.758 |
| window | 620 | 71.1 × 111.8 cm | 9.43 / 9.35 | 0.762 |
| window | 620 | Collection | 9.52 / 9.42 | 0.767 |
| window | 620 | The Metropolitan Museum of Art, New York | 9.35 / 9.15 | 0.758 |
| window | 620 | Credit | 9.11 / 8.97 | 0.747 |
| window | 620 | Gift of Erving Wolf Foundation and Mr. and | 9.04 / 8.96 | 0.744 |
| window | 620 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 8.94 / 8.94 | 0.739 |
| window | 620 | 1975 | 8.92 / 8.92 | 0.738 |
| window | 620 | Number | 8.84 / 8.69 | 0.734 |
| window | 620 | 1975.160 | 8.95 / 8.94 | 0.739 |
| window | 620 | Photograph: The Metropolitan Museum of Art, New York , open | 10.11 / 9.7 | 0.794 |
| window | 620 | access, public domain. | 10.06 / 9.51 | 0.792 |

### CSS tier · light · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 12.87 / 11.53 | 0.914 |
| window | 0 | Room 5 of 8 | 11.52 / 11.43 | 0.857 |
| window | 0 | Rain (large) | 12.2 / 11.7 | 0.886 |
| window | 0 | Paris Street; Rainy Day (large) | 11.94 / 11.55 | 0.875 |
| window | 0 | Gustave Caillebotte | 11.95 / 11.31 | 0.876 |
| window | 0 | French, 1848–1894 · 1877 | 11.68 / 11.39 | 0.864 |
| window | 0 | The whole work. The outline marks the part around you. | 11.72 / 10.4 | 0.866 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 12.12 / 10.76 | 0.883 |
| window | 0 | paints the rain through what it does: the paving | 12.12 / 10.84 | 0.883 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 12.11 / 10.93 | 0.883 |
| window | 0 | everyone carries an umbrella, the newly invented | 12.02 / 10.92 | 0.879 |
| window | 0 | retractable kind. | 11.39 / 10.5 | 0.851 |
| window | 0 | The place is a busy intersection a short walk from the | 11.9 / 10.93 | 0.873 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 11.83 / 10.91 | 0.87 |
| Rooms | 0 | 5 | 10.47 / 10.4 | 0.811 |
| Rooms | 0 | / 8 | 10.71 / 10.58 | 0.821 |
| Audio guide | 0 | Audio guide | 11.75 / 11.61 | 0.867 |
| Audio guide | 0 | About 0:46 | 11.71 / 11.44 | 0.865 |
| Rooms | 0 | icon: Previous room: Thunder | 10.23 / 10.06 | 0.799 |
| Rooms | 0 | icon: Next room: Wind | 11.46 / 11.03 | 0.854 |
| Audio guide | 0 | icon: Play the audio guide | 11.43 / 11.3 | 0.853 |
| window | 580 | painter’s home, in a Paris rebuilt with wide streets | 12.14 / 11.55 | 0.884 |
| window | 580 | and uniform stone façades. A green lamppost splits | 11.96 / 11.63 | 0.876 |
| window | 580 | the canvas in two; the couple on the right walk | 11.96 / 11.63 | 0.876 |
| window | 580 | straight toward us, looking at something beyond | 11.81 / 11.57 | 0.87 |
| window | 580 | the frame. | 11.66 / 11.37 | 0.863 |
| window | 580 | Nearly life-size, it is Caillebotte’s largest painting. He | 11.62 / 11.5 | 0.861 |
| window | 580 | showed it at the third Impressionist exhibition in 1877, | 11.54 / 11.45 | 0.858 |
| window | 580 | the year he made it. | 11.65 / 11.5 | 0.862 |
| window | 580 | Weather | 10.07 / 10.06 | 0.792 |
| window | 580 | Light rain, overcast | 10.08 / 10.06 | 0.792 |
| window | 580 | Artist | 9.59 / 9.51 | 0.77 |
| window | 580 | Gustave Caillebotte ( French, 1848–1894 ) | 10.16 / 9.7 | 0.796 |
| window | 580 | Date | 9.21 / 9.09 | 0.752 |
| window | 580 | 1877 | 10.24 / 10.07 | 0.8 |
| window | 580 | Medium | 9.39 / 9.12 | 0.761 |
| window | 580 | Oil on canvas | 10.86 / 10.46 | 0.828 |
| window | 580 | Size | 9.31 / 9.21 | 0.757 |
| window | 580 | 212.2 × 276.2 cm | 11.02 / 10.71 | 0.835 |
| window | 580 | Collection | 10.85 / 10.82 | 0.827 |
| window | 580 | The Art Institute of Chicago | 11.04 / 10.86 | 0.836 |
| window | 580 | Credit | 9.71 / 9.32 | 0.776 |
| window | 580 | Charles H. and Mary F. S. Worcester | 10.96 / 10.92 | 0.832 |
| window | 580 | Number | 9.73 / 9.56 | 0.776 |
| window | 580 | 1964.336 | 10.81 / 10.72 | 0.826 |
| window | 580 | Photograph: The Art Institute of Chicago , open access, public | 11.81 / 10.91 | 0.87 |
| window | 580 | domain. | 10.74 / 10.5 | 0.823 |

### CSS tier · light · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.89 / 11.3 | 0.873 |
| window | 0 | Room 6 of 8 | 12.08 / 11.83 | 0.881 |
| window | 0 | Wind (large) | 11.67 / 11.28 | 0.863 |
| window | 0 | Wheat Field with Cypresses (large) | 11.88 / 11.83 | 0.873 |
| window | 0 | Vincent van Gogh | 11.87 / 11.75 | 0.872 |
| window | 0 | Dutch, 1853–1890 · 1889 | 11.67 / 11.64 | 0.863 |
| window | 0 | The whole work. The outline marks the part around you. | 11.33 / 11.27 | 0.848 |
| window | 0 | Everything in this field is moving the same way. The | 11.33 / 11.18 | 0.848 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 11.23 / 10.84 | 0.844 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 10.98 / 10.58 | 0.833 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 10.73 / 10.55 | 0.822 |
| window | 0 | the paint on so heavily that the brushstrokes | 10.65 / 10.57 | 0.818 |
| window | 0 | themselves take the shape of the wind. | 10.72 / 10.56 | 0.821 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 10.65 / 10.48 | 0.819 |
| Rooms | 0 | 6 | 11.03 / 10.92 | 0.834 |
| Rooms | 0 | / 8 | 11.04 / 10.91 | 0.835 |
| Audio guide | 0 | Audio guide | 10.83 / 10.55 | 0.826 |
| Audio guide | 0 | About 0:51 | 10.68 / 10.41 | 0.819 |
| Rooms | 0 | icon: Previous room: Rain | 10.81 / 10.66 | 0.825 |
| Rooms | 0 | icon: Next room: Gale | 11.05 / 10.87 | 0.835 |
| Audio guide | 0 | icon: Play the audio guide | 10.58 / 10.47 | 0.814 |
| window | 580 | He painted it in late June or early July 1889 at Saint-Rémy | 12.19 / 11.33 | 0.886 |
| window | 580 | Saint-Rémy in Provence, where he was a patient at the | 12.1 / 11.35 | 0.882 |
| window | 580 | asylum of Saint-Paul-de-Mausole, working outdoors | 12 / 11.67 | 0.878 |
| window | 580 | in front of the motif. | 11.97 / 11.86 | 0.876 |
| window | 580 | He counted it among his best summer canvases, and | 11.76 / 11.65 | 0.867 |
| window | 580 | that September made two studio versions of it: one | 11.64 / 11.59 | 0.862 |
| window | 580 | now in the National Gallery, London, the other a | 11.49 / 11.41 | 0.856 |
| window | 580 | smaller copy for his mother and sister. | 11.41 / 11.32 | 0.852 |
| window | 580 | Weather | 10.34 / 10.34 | 0.804 |
| window | 580 | Summer wind, fast cloud | 10.27 / 10.22 | 0.801 |
| window | 580 | Artist | 10.31 / 10.25 | 0.803 |
| window | 580 | Vincent van Gogh ( Dutch, 1853–1890 ) | 10.28 / 10.19 | 0.802 |
| window | 580 | Date | 10.26 / 10.19 | 0.801 |
| window | 580 | 1889 | 10.24 / 10.24 | 0.8 |
| window | 580 | Medium | 10.27 / 10.26 | 0.801 |
| window | 580 | Oil on canvas | 10.24 / 10.23 | 0.8 |
| window | 580 | Size | 10.31 / 10.31 | 0.803 |
| window | 580 | 73.2 × 93.4 cm | 10.34 / 10.29 | 0.804 |
| window | 580 | Collection | 10.38 / 10.31 | 0.806 |
| window | 580 | The Metropolitan Museum of Art, New York | 9.86 / 9.65 | 0.782 |
| window | 580 | Credit | 10.34 / 10.31 | 0.804 |
| window | 580 | Purchase, The Annenberg Foundation Gift, | 9.6 / 9.55 | 0.77 |
| window | 580 | 1993 | 9.73 / 9.64 | 0.776 |
| window | 580 | Number | 10.19 / 10.03 | 0.798 |
| window | 580 | 1993.132 | 9.56 / 9.54 | 0.768 |
| window | 580 | Photograph: The Metropolitan Museum of Art, New York , open | 10.58 / 10.4 | 0.815 |
| window | 580 | access, public domain. | 10.61 / 10.34 | 0.817 |

### CSS tier · light · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.81 / 11.39 | 0.87 |
| window | 0 | Room 7 of 8 | 12.54 / 11.73 | 0.901 |
| window | 0 | Gale (large) | 11.81 / 11.46 | 0.869 |
| window | 0 | Northeaster (large) | 12.1 / 11.62 | 0.882 |
| window | 0 | Winslow Homer | 12.22 / 11.84 | 0.887 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 12.71 / 12.14 | 0.908 |
| window | 0 | The whole work. The outline marks the part around you. | 11.73 / 11.44 | 0.866 |
| window | 0 | A northeaster is a winter storm that drives in off the | 11.66 / 11.42 | 0.863 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 11.51 / 11.3 | 0.856 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 11.23 / 10.98 | 0.844 |
| window | 0 | lived and painted for the last decades of his life. | 10.72 / 10.46 | 0.822 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 10.03 / 9.93 | 0.79 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 9.95 / 9.78 | 0.787 |
| window | 0 | lower left. By 1900 he had painted them out and | 9.89 / 9.78 | 0.784 |
| Rooms | 0 | 7 | 9.77 / 9.75 | 0.778 |
| Rooms | 0 | / 8 | 9.85 / 9.78 | 0.782 |
| Audio guide | 0 | Audio guide | 9.62 / 9.48 | 0.771 |
| Audio guide | 0 | About 0:50 | 9.73 / 9.64 | 0.777 |
| Rooms | 0 | icon: Previous room: Wind | 9.49 / 9.39 | 0.765 |
| Rooms | 0 | icon: Next room: Fog | 9.78 / 9.69 | 0.779 |
| Audio guide | 0 | icon: Play the audio guide | 10 / 9.96 | 0.789 |
| window | 508 | When he first exhibited this canvas in 1895, two men | 13.15 / 11.78 | 0.927 |
| window | 508 | in foul-weather gear crouched on the rocks at the | 13.15 / 11.72 | 0.927 |
| window | 508 | lower left. By 1900 he had painted them out and | 12.97 / 11.8 | 0.919 |
| window | 508 | raised a much larger column of spray. What is left is | 12.97 / 11.93 | 0.919 |
| window | 508 | rock, water and air: the dark ledge, the green body of | 12.89 / 12.12 | 0.915 |
| window | 508 | the wave and the white burst where they meet. | 12.72 / 12.16 | 0.908 |
| window | 508 | A critic in 1901 praised it for “great natural spaces | 12.81 / 12.16 | 0.912 |
| window | 508 | unmarked by the presence of puny man.” | 12.79 / 12.04 | 0.911 |
| window | 508 | Weather | 10.98 / 10.79 | 0.833 |
| window | 508 | Winter northeaster off the Atlantic | 11.22 / 11.07 | 0.844 |
| window | 508 | Artist | 10.98 / 10.88 | 0.833 |
| window | 508 | Winslow Homer ( American, 1836–1910 ) | 10.9 / 10.7 | 0.83 |
| window | 508 | Date | 10.85 / 10.77 | 0.827 |
| window | 508 | 1895; reworked by 1901 | 10.6 / 10.38 | 0.816 |
| window | 508 | Medium | 10.68 / 10.58 | 0.82 |
| window | 508 | Oil on canvas | 10.5 / 10.43 | 0.812 |
| window | 508 | Size | 10.24 / 10.18 | 0.8 |
| window | 508 | 87.6 × 127 cm | 10.34 / 10.26 | 0.805 |
| window | 508 | Collection | 9.88 / 9.79 | 0.783 |
| window | 508 | The Metropolitan Museum of Art, New York | 10.46 / 9.85 | 0.81 |
| window | 508 | Credit | 9.26 / 9.18 | 0.755 |
| window | 508 | Gift of George A. Hearn, 1910 | 9.41 / 9.19 | 0.762 |
| window | 508 | Number | 8.88 / 8.87 | 0.736 |
| window | 508 | 10.64.5 | 8.95 / 8.94 | 0.74 |
| window | 508 | Photograph: The Metropolitan Museum of Art, New York , open | 9.83 / 9.78 | 0.781 |
| window | 508 | access, public domain. | 9.78 / 9.7 | 0.779 |

### CSS tier · light · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.03 / 11.01 | 0.835 |
| window | 0 | Room 8 of 8 | 11.13 / 11.05 | 0.84 |
| window | 0 | Fog (large) | 11.1 / 11.03 | 0.838 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 11.15 / 10.95 | 0.841 |
| window | 0 | Claude Monet | 10.87 / 10.83 | 0.828 |
| window | 0 | French, 1840–1926 · 1900 | 10.96 / 10.75 | 0.832 |
| window | 0 | The whole work. The outline marks the part around you. | 10.26 / 10.2 | 0.801 |
| window | 0 | Without the fog, Monet once remarked, London | 10.19 / 10.15 | 0.798 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 10.19 / 10.11 | 0.798 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 10.2 / 10.1 | 0.798 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 10.21 / 10.08 | 0.799 |
| window | 0 | he came to paint it. | 10.74 / 10.67 | 0.822 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 10.27 / 10.07 | 0.801 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 10.27 / 10.07 | 0.801 |
| Rooms | 0 | 8 | 10.3 / 10.16 | 0.803 |
| Rooms | 0 | / 8 | 10.4 / 10.33 | 0.807 |
| Audio guide | 0 | Audio guide | 10.06 / 9.97 | 0.791 |
| Audio guide | 0 | About 0:50 | 10.1 / 10.02 | 0.793 |
| Rooms | 0 | icon: Previous room: Gale | 10.41 / 10.35 | 0.808 |
| Audio guide | 0 | icon: Play the audio guide | 9.96 / 9.93 | 0.787 |
| window | 534 | He painted Waterloo Bridge in the mornings from his | 11.11 / 11.1 | 0.839 |
| window | 534 | fifth-floor window at the Savoy Hotel, moving on to | 11.11 / 11.04 | 0.839 |
| window | 534 | Charing Cross Bridge later in the day. Here the bridge | 11.13 / 11.02 | 0.84 |
| window | 534 | is a dark band of arches, and the city behind it is only | 11.15 / 10.93 | 0.841 |
| window | 534 | chimneys and towers in the haze. | 11.13 / 10.84 | 0.84 |
| window | 534 | He finished the London pictures in his studio at | 11.05 / 10.8 | 0.836 |
| window | 534 | Giverny, and would not release any of them until he | 10.93 / 10.79 | 0.831 |
| window | 534 | was satisfied with the series as a whole. | 10.83 / 10.78 | 0.827 |
| window | 534 | Weather | 9.77 / 9.72 | 0.778 |
| window | 534 | Winter fog and coal smoke | 9.72 / 9.65 | 0.776 |
| window | 534 | Artist | 9.61 / 9.59 | 0.771 |
| window | 534 | Claude Monet ( French, 1840–1926 ) | 9.53 / 9.46 | 0.767 |
| window | 534 | Date | 9.37 / 9.31 | 0.759 |
| window | 534 | 1900 | 9.42 / 9.42 | 0.762 |
| window | 534 | Medium | 9.23 / 9.22 | 0.753 |
| window | 534 | Oil on canvas | 9.33 / 9.27 | 0.758 |
| window | 534 | Size | 9.25 / 9.18 | 0.754 |
| window | 534 | 65.4 × 92.6 cm | 9.34 / 9.25 | 0.758 |
| window | 534 | Collection | 9.47 / 9.36 | 0.764 |
| window | 534 | The Art Institute of Chicago | 9.27 / 9.16 | 0.755 |
| window | 534 | Credit | 9.67 / 9.65 | 0.774 |
| window | 534 | Gift of Mrs. Mortimer B. Harris | 9.28 / 9.14 | 0.755 |
| window | 534 | Number | 9.73 / 9.7 | 0.776 |
| window | 534 | 1984.1173 | 9.68 / 9.63 | 0.774 |
| window | 534 | Photograph: The Art Institute of Chicago , open access, public | 10.27 / 10.1 | 0.801 |
| window | 534 | domain. | 10.67 / 10.66 | 0.819 |

### CSS tier · light · rooms view · active (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 12.24 | 9.87 | 9.87 | 9.67 | 11.53 | 11.3 | 11.39 | 11.01 |
| 8 rooms | 13.7 | 9.97 | 10.44 | 9.59 | 11.43 | 11.81 | 11.68 | 11.05 |
| Eight skies, 1608–1900 | 12.36 | 9.87 | 10.04 | 9.95 | 11.61 | 11.34 | 11.64 | 11.1 |
| For most of the history of European painting the sky | 12.16 | 9.97 | 10.04 | 10.01 | 11.57 | 11.87 | 11.81 | 11.01 |
| was the back wall of the picture. This exhibition | 12.16 | 10.04 | 9.98 | 10.03 | 11.54 | 11.75 | 11.93 | 10.93 |
| follows it becoming the subject: eight rooms, each | 12.26 | 10.12 | 9.98 | 10.03 | 11.47 | 11.63 | 12.12 | 10.84 |
| holding one work, from a Dutch winter in the Little Ice | 12.26 | 10.2 | 10.06 | 10.19 | 11.47 | 11.51 | 12.23 | 10.82 |
| Age to a London fog that was largely coal smoke. | 12.16 | 10.2 | 10 | 10.29 | 11.46 | 11.36 | 12.16 | 10.79 |
| Each work fills the room. Its label sits beside it, and | 11.67 | 10.2 | 10.06 | 10.54 | 11.13 | 11.29 | 12.07 | 10.78 |
| the audio guide reads the label aloud in your | 11.26 | 10.2 | 10.08 | 10.54 | 11.11 | 11.26 | 11.94 | 10.78 |
| browser’s own voice. | 10.9 | 10.2 | 10.11 | 10.45 | 10.99 | 11.27 | 11.82 | 10.77 |
| Rooms | 10.63 | 10.88 | 10.25 | 10.38 | 10.22 | 11.29 | 11.96 | 10.52 |
| 01 · Frost | 9.36 | 10.62 | 10.18 | 10.3 | 11.04 | 11.27 | 11.73 | 10.29 |
| · you are here | 9.7 | 9.26 | 8.62 | 8.69 | 10.04 | 9.88 | 10.78 | 8.93 |
| Winter Landscape with Ice Skaters | 9.53 | 10.44 | 10.18 | 10.2 | 11.49 | 11.27 | 11.43 | 10.19 |
| Hendrick Avercamp , c. 1608 | 9.53 | 10.47 | 10.1 | 10.3 | 11.52 | 11.27 | 11.42 | 10.18 |
| 02 · Cloud | 11.27 | 9.45 | 10 | 10.29 | 11.75 | 11.22 | 11.31 | 10.29 |
| The Windmill at Wijk bij Duurstede | 11.15 | 9.32 | 9.95 | 9.96 | 11.92 | 10.57 | 10.98 | 10.1 |
| Jacob van Ruisdael , c. 1668–70 | 11.13 | 9.36 | 9.91 | 9.85 | 11.9 | 10.55 | 10.61 | 10.08 |
| 03 · Clearing | 10.83 | 11.28 | 8.5 | 9.83 | 11.72 | 10.56 | 9.94 | 10.59 |
| View from Mount Holyoke, Northampton, | 10.66 | 11.39 | 8.5 | 9.77 | 11.79 | 10.56 | 9.85 | 10.06 |
| Massachusetts, after a Thunderstorm—The | 10.62 | 11.54 | 8.56 | 9.77 | 11.72 | 10.48 | 9.79 | 10.07 |
| Oxbow | 10.53 | 11.58 | 8.54 | 9.89 | 11.52 | 10.39 | 9.78 | 10.67 |
| Thomas Cole , 1836 | 10.44 | 11.36 | 8.46 | 10.11 | 11.59 | 10.32 | 9.78 | 10.27 |
| 04 · Thunder | 12.54 | 9.97 | 10.19 | 8.7 | 12.78 | 11.9 | 12.06 | 11.1 |
| Approaching Thunder Storm | 12.47 | 10.04 | 10.19 | 8.7 | 11.57 | 11.91 | 12.24 | 11.1 |
| Martin Johnson Heade , 1859 | 12.39 | 10.06 | 10.19 | 8.7 | 11.55 | 11.87 | 12.27 | 11.11 |
| 05 · Rain | 12.37 | 10.12 | 10.12 | 10.11 | 10.46 | 11.75 | 12.38 | 11.03 |
| Paris Street; Rainy Day | 12.46 | 10.2 | 10.19 | 10.27 | 10.03 | 11.61 | 12.42 | 10.96 |
| Gustave Caillebotte , 1877 | 12.35 | 10.2 | 10.22 | 10.39 | 10 | 11.5 | 12.43 | 10.94 |
| 06 · Wind | 11.88 | 10.2 | 10.19 | 10.54 | 11.48 | 9.95 | 12.45 | 10.83 |
| Wheat Field with Cypresses | 11.59 | 10.2 | 10.25 | 10.56 | 11.37 | 9.85 | 12.45 | 10.83 |
| Vincent van Gogh , 1889 | 11.26 | 10.2 | 10.25 | 10.56 | 11.21 | 9.81 | 12.43 | 10.8 |
| 07 · Gale | 10.88 | 10.23 | 10.24 | 10.56 | 10.85 | 11.31 | 10.6 | 10.73 |
| Northeaster | 10.8 | 10.23 | 10.24 | 10.56 | 10.77 | 11.26 | 10.54 | 10.63 |
| Winslow Homer , 1895; reworked by 1901 | 10.85 | 10.29 | 10.24 | 10.45 | 10.89 | 11.22 | 10.2 | 10.39 |
| 08 · Fog | 10.81 | 10.71 | 10.18 | 10.3 | 11.13 | 11.27 | 11.73 | 8.93 |
| Waterloo Bridge, Gray Weather | 10.98 | 9.96 | 10.15 | 9.93 | 11.52 | 11.27 | 11.42 | 8.86 |
| Claude Monet , 1900 | 10.97 | 9.95 | 10.08 | 10.01 | 11.58 | 11.33 | 11.42 | 8.86 |
| Viewing | 9.7 | 9.05 | 8.99 | 8.88 | 9.33 | 10.25 | 9.54 | 9.44 |
| Reduce transparency | 9.58 | 9.12 | 8.96 | 8.77 | 9.56 | 9.64 | 9.12 | 9.66 |
| Frosts the label and the controls so the painting | 9.52 | 9.2 | 8.9 | 8.84 | 9.73 | 9.56 | 8.95 | 9.14 |
| shows through less. | 9.3 | 9.28 | 8.9 | 8.72 | 9.64 | 9.55 | 8.87 | 9.71 |
| Photographs | 11.48 | 10.2 | 9.98 | 10.38 | 11.24 | 11.21 | 11.86 | 10.74 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 11.2 | 10.2 | 10.08 | 10.56 | 11.1 | 11.26 | 11.94 | 10.78 |
| Rijksmuseum, Amsterdam , open access, public domain. | 10.72 | 10.2 | 10.16 | 10.54 | 10.46 | 11.22 | 11.9 | 10.55 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 10.83 | 10.22 | 10.24 | 10.56 | 10.69 | 11.23 | 12.06 | 10.65 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 10.63 | 10.3 | 10.24 | 10.45 | 10.24 | 11.24 | 11.69 | 10.37 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 10.55 | 10.38 | 10.24 | 10.29 | 10.24 | 11.27 | 11.51 | 10.28 |
| Metropolitan Museum of Art, New York , open access, public | 10.47 | 10.44 | 10.01 | 10.15 | 10.46 | 10.97 | 11.38 | 10.13 |
| domain. | 10.47 | 10.98 | 9.93 | 10.1 | 10.04 | 11.3 | 11.14 | 10.15 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 10.78 | 10.55 | 10.08 | 10.22 | 10.74 | 11.19 | 11.42 | 10.15 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 10.94 | 10.71 | 9.93 | 9.87 | 10.93 | 10.55 | 10.88 | 10.1 |
| Chicago , open access, public domain. | 10.25 | 10.89 | 9.69 | 9.61 | 10.57 | 10.34 | 9.76 | 10.18 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 10.59 | 11.05 | 9.89 | 9.77 | 10.93 | 10.58 | 10.04 | 10.06 |
| Museum of Art, New York , open access, public domain. | 10.51 | 11.19 | 9.81 | 9.75 | 10.82 | 10.57 | 9.87 | 10.06 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 10.36 | 11.39 | 9.81 | 9.71 | 10.91 | 10.55 | 9.78 | 10.06 |
| New York , open access, public domain. | 10.26 | 11.46 | 9.87 | 9.69 | 10.74 | 10.47 | 9.77 | 10.16 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 10.28 | 11.24 | 9.79 | 9.62 | 10.91 | 10.4 | 9.78 | 10.1 |

### CSS tier · dark · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.54 / 6.51 | 0.286 |
| window | 0 | Room 1 of 8 | 6.44 / 6.33 | 0.29 |
| window | 0 | Frost (large) | 6.69 / 6.6 | 0.279 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 6.69 / 6.62 | 0.279 |
| window | 0 | Hendrick Avercamp | 6.71 / 6.61 | 0.278 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 6.71 / 6.63 | 0.278 |
| window | 0 | The whole work. The outline marks the part around you. | 6.81 / 6.8 | 0.274 |
| window | 0 | Avercamp made his name painting winter, in the years | 6.81 / 6.79 | 0.274 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 6.79 / 6.79 | 0.275 |
| window | 0 | Countries. Here a whole village has moved onto the | 6.79 / 6.79 | 0.275 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 6.81 / 6.79 | 0.274 |
| window | 0 | sledge on the right, a church on the left. | 6.87 / 6.81 | 0.271 |
| window | 0 | Look at how the air is built. The figures in front are | 6.88 / 6.87 | 0.271 |
| window | 0 | sharp and full of colour; a few hundred metres back | 6.88 / 6.88 | 0.271 |
| Rooms | 0 | 1 | 5.53 / 5.53 | 0.333 |
| Rooms | 0 | / 8 | 5.52 / 5.52 | 0.333 |
| Audio guide | 0 | Audio guide | 5.52 / 5.45 | 0.333 |
| Audio guide | 0 | About 0:51 | 5.52 / 5.45 | 0.333 |
| Rooms | 0 | icon: Next room: Cloud | 5.22 / 5.17 | 0.349 |
| Audio guide | 0 | icon: Play the audio guide | 5.32 / 5.31 | 0.344 |
| window | 554 | Look at how the air is built. The figures in front are | 6.6 / 6.53 | 0.283 |
| window | 554 | sharp and full of colour; a few hundred metres back | 6.62 / 6.61 | 0.282 |
| window | 554 | they thin into grey-white haze, and the far bank all | 6.69 / 6.62 | 0.279 |
| window | 554 | but dissolves. That haze is the weather: cold, damp | 6.69 / 6.62 | 0.279 |
| window | 554 | air thick enough to carry the light. | 6.69 / 6.69 | 0.279 |
| window | 554 | Avercamp signed the picture on the wall of a wooden | 6.69 / 6.62 | 0.279 |
| window | 554 | shed on the right, among the scratched graffiti, | 6.71 / 6.69 | 0.278 |
| window | 554 | where it is easy to miss. | 6.71 / 6.63 | 0.278 |
| window | 554 | Weather | 8.36 / 8.33 | 0.215 |
| window | 554 | Hard frost, haze over the ice | 8.33 / 8.33 | 0.216 |
| window | 554 | Artist | 8.38 / 8.36 | 0.214 |
| window | 554 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 8.33 / 8.33 | 0.216 |
| window | 554 | Date | 8.38 / 8.36 | 0.214 |
| window | 554 | c. 1608 | 8.37 / 8.37 | 0.215 |
| window | 554 | Medium | 8.39 / 8.37 | 0.214 |
| window | 554 | Oil on panel | 8.34 / 8.34 | 0.215 |
| window | 554 | Size | 8.34 / 8.34 | 0.215 |
| window | 554 | 77.3 × 131.9 cm | 8.35 / 8.34 | 0.215 |
| window | 554 | Collection | 8.34 / 8.33 | 0.215 |
| window | 554 | Rijksmuseum, Amsterdam | 8.34 / 8.34 | 0.215 |
| window | 554 | Credit | 8.34 / 8.34 | 0.215 |
| window | 554 | Purchased with the support of the | 8.34 / 8.34 | 0.215 |
| window | 554 | Vereniging Rembrandt | 8.34 / 8.34 | 0.215 |
| window | 554 | Number | 8.45 / 8.43 | 0.211 |
| window | 554 | SK-A-1718 | 8.42 / 8.42 | 0.213 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.88 / 6.81 | 0.271 |
| window | 554 | domain. | 6.81 / 6.79 | 0.274 |

### CSS tier · dark · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.99 / 6.91 | 0.267 |
| window | 0 | Room 2 of 8 | 6.99 / 6.91 | 0.267 |
| window | 0 | Cloud (large) | 7.09 / 7.01 | 0.263 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 7.08 / 6.91 | 0.263 |
| window | 0 | Jacob van Ruisdael | 7.08 / 6.99 | 0.263 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 7.01 / 6.99 | 0.266 |
| window | 0 | The whole work. The outline marks the part around you. | 6.99 / 6.89 | 0.267 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 6.91 / 6.89 | 0.27 |
| window | 0 | more than half the canvas, and he paints it as a | 6.98 / 6.89 | 0.267 |
| window | 0 | structure: banks of cumulus heaped over one | 6.98 / 6.89 | 0.267 |
| window | 0 | another, grey underneath, lit at their edges by a sun | 6.91 / 6.89 | 0.27 |
| window | 0 | we cannot see. | 6.91 / 6.82 | 0.27 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 6.89 / 6.82 | 0.271 |
| window | 0 | A sailing boat is out on the water, the towers of | 6.89 / 6.82 | 0.271 |
| Rooms | 0 | 2 | 6.81 / 6.81 | 0.274 |
| Rooms | 0 | / 8 | 6.8 / 6.8 | 0.275 |
| Audio guide | 0 | Audio guide | 7.09 / 6.9 | 0.262 |
| Audio guide | 0 | About 0:49 | 7.09 / 7.09 | 0.262 |
| Rooms | 0 | icon: Previous room: Frost | 6.81 / 6.81 | 0.274 |
| Rooms | 0 | icon: Next room: Clearing | 6.8 / 6.8 | 0.275 |
| Audio guide | 0 | icon: Play the audio guide | 7 / 6.98 | 0.266 |
| window | 554 | Below, the mill stands near the bank of the river Lek. | 7.01 / 6.99 | 0.266 |
| window | 554 | A sailing boat is out on the water, the towers of | 7.01 / 6.99 | 0.266 |
| window | 554 | Duurstede castle and the church rise in the distance, | 7.01 / 6.98 | 0.266 |
| window | 554 | and a few women walk along the bank, very small | 7.08 / 6.91 | 0.263 |
| window | 554 | against the mill. | 7.08 / 7.01 | 0.263 |
| window | 554 | Dutch painters of the seventeenth century made the | 6.99 / 6.89 | 0.267 |
| window | 554 | sky a subject in its own right. Few made it carry as | 6.98 / 6.89 | 0.267 |
| window | 554 | much of a picture as this. | 7.01 / 6.91 | 0.266 |
| window | 554 | Weather | 8.47 / 8.36 | 0.211 |
| window | 554 | Heaped cumulus, sun breaking through | 8.56 / 8.44 | 0.208 |
| window | 554 | Artist | 8.44 / 8.36 | 0.212 |
| window | 554 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 8.56 / 8.44 | 0.208 |
| window | 554 | Date | 8.37 / 8.36 | 0.212 |
| window | 554 | c. 1668–70 | 8.56 / 8.56 | 0.208 |
| window | 554 | Medium | 8.44 / 8.33 | 0.212 |
| window | 554 | Oil on canvas | 8.55 / 8.55 | 0.208 |
| window | 554 | Size | 8.37 / 8.33 | 0.215 |
| window | 554 | 83 × 101 cm | 8.47 / 8.47 | 0.211 |
| window | 554 | Collection | 8.47 / 8.36 | 0.211 |
| window | 554 | Rijksmuseum, Amsterdam | 8.55 / 8.47 | 0.208 |
| window | 554 | Credit | 8.44 / 8.36 | 0.212 |
| window | 554 | On loan from the City of Amsterdam (A. van | 8.47 / 8.47 | 0.211 |
| window | 554 | der Hoop Bequest) | 8.47 / 8.47 | 0.211 |
| window | 554 | Number | 8.36 / 8.36 | 0.215 |
| window | 554 | SK-C-211 | 8.44 / 8.44 | 0.212 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.89 / 6.82 | 0.271 |
| window | 554 | domain. | 6.8 / 6.73 | 0.275 |

### CSS tier · dark · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.5 / 7.47 | 0.246 |
| window | 0 | Room 3 of 8 | 7.28 / 7.2 | 0.255 |
| window | 0 | Clearing (large) | 7.5 / 7.49 | 0.246 |
| window | 0 | View from Mount Holyoke, (large) | 7.5 / 7.4 | 0.246 |
| window | 0 | Northampton, Massachusetts, (large) | 7.49 / 7.37 | 0.247 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 7.47 / 7.28 | 0.248 |
| window | 0 | Thomas Cole | 7.5 / 7.5 | 0.246 |
| window | 0 | American, born England, 1801–1848 · 1836 | 7.5 / 7.37 | 0.246 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.48 | 0.247 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 7.59 / 7.51 | 0.243 |
| window | 0 | valley. On the left it still hangs over wild, broken | 7.59 / 7.51 | 0.243 |
| window | 0 | trees, and rain falls in grey veils across the hills. On | 7.59 / 7.51 | 0.243 |
| window | 0 | the right the air has cleared over cleared land: fields, | 7.59 / 7.51 | 0.243 |
| window | 0 | farms and the river’s great loop. | 7.6 / 7.49 | 0.243 |
| Rooms | 0 | 3 | 7.88 / 7.86 | 0.232 |
| Rooms | 0 | / 8 | 7.75 / 7.75 | 0.237 |
| Audio guide | 0 | Audio guide | 7.53 / 7.25 | 0.245 |
| Audio guide | 0 | About 0:50 | 7.59 / 7.37 | 0.243 |
| Rooms | 0 | icon: Previous room: Cloud | 7.93 / 7.93 | 0.231 |
| Rooms | 0 | icon: Next room: Thunder | 7.93 / 7.93 | 0.231 |
| Audio guide | 0 | icon: Play the audio guide | 7.6 / 7.58 | 0.243 |
| window | 610 | Cole divided the picture along a diagonal, and the | 7.47 / 7.37 | 0.248 |
| window | 610 | weather does the dividing. He painted it for the 1836 | 7.47 / 7.28 | 0.248 |
| window | 610 | annual exhibition of the National Academy of Design, | 7.49 / 7.28 | 0.247 |
| window | 610 | calling the view from Mount Holyoke “about the finest | 7.49 / 7.27 | 0.247 |
| window | 610 | scene I have in my sketchbook.” | 7.5 / 7.47 | 0.246 |
| window | 610 | Look for the painter himself near the bottom of the | 7.47 / 7.37 | 0.248 |
| window | 610 | canvas: a small figure at an easel among the rocks, | 7.47 / 7.37 | 0.248 |
| window | 610 | turning back toward us. | 7.5 / 7.5 | 0.246 |
| window | 610 | Weather | 9 / 8.99 | 0.192 |
| window | 610 | Thunderstorm passing, sun on the valley | 8.91 / 8.87 | 0.196 |
| window | 610 | Artist | 8.91 / 8.91 | 0.195 |
| window | 610 | Thomas Cole ( American, born England, | 8.91 / 8.87 | 0.196 |
| window | 610 | 1801–1848 ) | 9 / 8.99 | 0.192 |
| window | 610 | Date | 8.88 / 8.88 | 0.196 |
| window | 610 | 1836 | 9 / 8.99 | 0.192 |
| window | 610 | Medium | 8.99 / 8.91 | 0.193 |
| window | 610 | Oil on canvas | 9 / 8.99 | 0.192 |
| window | 610 | Size | 9 / 8.99 | 0.192 |
| window | 610 | 130.8 × 193 cm | 9.1 / 9 | 0.189 |
| window | 610 | Collection | 9.1 / 9.1 | 0.189 |
| window | 610 | The Metropolitan Museum of Art, New York | 9.11 / 9.03 | 0.189 |
| window | 610 | Credit | 9.11 / 9.03 | 0.189 |
| window | 610 | Gift of Mrs. Russell Sage, 1908 | 9.13 / 9.03 | 0.188 |
| window | 610 | Number | 9.11 / 9.03 | 0.189 |
| window | 610 | 08.228 | 9.13 / 9.13 | 0.188 |
| window | 610 | Photograph: The Metropolitan Museum of Art, New York , open | 7.59 / 7.49 | 0.243 |
| window | 610 | access, public domain. | 7.61 / 7.61 | 0.242 |

### CSS tier · dark · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.67 / 7.67 | 0.24 |
| window | 0 | Room 4 of 8 | 7.67 / 7.67 | 0.24 |
| window | 0 | Thunder (large) | 7.67 / 7.67 | 0.24 |
| window | 0 | Approaching Thunder Storm (large) | 7.67 / 7.57 | 0.24 |
| window | 0 | Martin Johnson Heade | 7.57 / 7.57 | 0.244 |
| window | 0 | American, 1819–1904 · 1859 | 7.48 / 7.48 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.55 / 7.48 | 0.245 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 7.46 / 7.44 | 0.248 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 7.46 / 7.45 | 0.248 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 7.58 / 7.56 | 0.243 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 7.7 / 7.68 | 0.239 |
| window | 0 | rower pulls for shore; a white sail stands out against | 7.77 / 7.77 | 0.236 |
| window | 0 | the dark. | 7.8 / 7.8 | 0.235 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 7.63 / 7.35 | 0.241 |
| Rooms | 0 | 4 | 6.19 / 6.19 | 0.301 |
| Rooms | 0 | / 8 | 6.19 / 6.19 | 0.301 |
| Audio guide | 0 | Audio guide | 6.43 / 6.39 | 0.29 |
| Audio guide | 0 | About 0:53 | 6.43 / 6.34 | 0.29 |
| Rooms | 0 | icon: Previous room: Clearing | 5.92 / 5.9 | 0.313 |
| Rooms | 0 | icon: Next room: Rain | 5.97 / 5.87 | 0.311 |
| Audio guide | 0 | icon: Play the audio guide | 6.22 / 6.16 | 0.3 |
| window | 618 | holds: not the storm itself but the minute before it. | 7.67 / 7.67 | 0.24 |
| window | 618 | Painted two years before the Civil War, it has often | 7.67 / 7.67 | 0.24 |
| window | 618 | been read as a picture of a country waiting for | 7.67 / 7.6 | 0.24 |
| window | 618 | something to break. Heade based it on a storm he | 7.57 / 7.57 | 0.244 |
| window | 618 | had watched from Prudence Island, in the bay, | 7.55 / 7.46 | 0.245 |
| window | 618 | around 1858. | 7.57 / 7.48 | 0.244 |
| window | 618 | Weather | 8.96 / 8.96 | 0.194 |
| window | 618 | Thunderstorm approaching over still water | 8.88 / 8.88 | 0.196 |
| window | 618 | Artist | 8.96 / 8.96 | 0.194 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 8.88 / 8.88 | 0.196 |
| window | 618 | 1819–1904 ) | 8.96 / 8.96 | 0.194 |
| window | 618 | Date | 8.96 / 8.96 | 0.194 |
| window | 618 | 1859 | 8.96 / 8.96 | 0.194 |
| window | 618 | Medium | 8.99 / 8.99 | 0.193 |
| window | 618 | Oil on canvas | 8.99 / 8.99 | 0.193 |
| window | 618 | Size | 8.97 / 8.97 | 0.193 |
| window | 618 | 71.1 × 111.8 cm | 8.97 / 8.97 | 0.193 |
| window | 618 | Collection | 8.95 / 8.95 | 0.194 |
| window | 618 | The Metropolitan Museum of Art, New York | 8.97 / 8.97 | 0.193 |
| window | 618 | Credit | 9.08 / 9.08 | 0.19 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 9.13 / 9.1 | 0.188 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9.13 / 9.13 | 0.188 |
| window | 618 | 1975 | 9.21 / 9.21 | 0.185 |
| window | 618 | Number | 9.23 / 9.21 | 0.184 |
| window | 618 | 1975.160 | 9.13 / 9.1 | 0.188 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 7.51 / 7.16 | 0.246 |
| window | 620 | holds: not the storm itself but the minute before it. | 7.67 / 7.67 | 0.24 |
| window | 620 | Painted two years before the Civil War, it has often | 7.67 / 7.67 | 0.24 |
| window | 620 | been read as a picture of a country waiting for | 7.67 / 7.6 | 0.24 |
| window | 620 | something to break. Heade based it on a storm he | 7.57 / 7.57 | 0.244 |
| window | 620 | had watched from Prudence Island, in the bay, | 7.55 / 7.48 | 0.245 |
| window | 620 | around 1858. | 7.57 / 7.48 | 0.244 |
| window | 620 | Weather | 8.96 / 8.96 | 0.194 |
| window | 620 | Thunderstorm approaching over still water | 8.88 / 8.86 | 0.196 |
| window | 620 | Artist | 8.96 / 8.96 | 0.194 |
| window | 620 | Martin Johnson Heade ( American, 1819–1904 | 8.88 / 8.88 | 0.196 |
| window | 620 | 1819–1904 ) | 8.96 / 8.96 | 0.194 |
| window | 620 | Date | 8.96 / 8.96 | 0.194 |
| window | 620 | 1859 | 8.96 / 8.96 | 0.194 |
| window | 620 | Medium | 8.99 / 8.99 | 0.193 |
| window | 620 | Oil on canvas | 8.99 / 8.99 | 0.193 |
| window | 620 | Size | 8.97 / 8.97 | 0.193 |
| window | 620 | 71.1 × 111.8 cm | 8.97 / 8.97 | 0.193 |
| window | 620 | Collection | 8.95 / 8.95 | 0.194 |
| window | 620 | The Metropolitan Museum of Art, New York | 8.97 / 8.95 | 0.193 |
| window | 620 | Credit | 9.08 / 9.08 | 0.19 |
| window | 620 | Gift of Erving Wolf Foundation and Mr. and | 9.1 / 9.1 | 0.189 |
| window | 620 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9.13 / 9.13 | 0.188 |
| window | 620 | 1975 | 9.21 / 9.21 | 0.185 |
| window | 620 | Number | 9.23 / 9.23 | 0.184 |
| window | 620 | 1975.160 | 9.21 / 9.1 | 0.185 |
| window | 620 | Photograph: The Metropolitan Museum of Art, New York , open | 7.51 / 7.17 | 0.246 |
| window | 620 | access, public domain. | 7.54 / 7.31 | 0.245 |

### CSS tier · dark · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.53 / 6.5 | 0.286 |
| window | 0 | Room 5 of 8 | 6.63 / 6.54 | 0.282 |
| window | 0 | Rain (large) | 6.69 / 6.61 | 0.279 |
| window | 0 | Paris Street; Rainy Day (large) | 6.71 / 6.69 | 0.278 |
| window | 0 | Gustave Caillebotte | 6.71 / 6.71 | 0.278 |
| window | 0 | French, 1848–1894 · 1877 | 6.73 / 6.71 | 0.278 |
| window | 0 | The whole work. The outline marks the part around you. | 6.79 / 6.73 | 0.275 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 6.73 / 6.71 | 0.278 |
| window | 0 | paints the rain through what it does: the paving | 6.73 / 6.71 | 0.278 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 6.71 / 6.71 | 0.278 |
| window | 0 | everyone carries an umbrella, the newly invented | 6.73 / 6.71 | 0.278 |
| window | 0 | retractable kind. | 6.8 / 6.73 | 0.275 |
| window | 0 | The place is a busy intersection a short walk from the | 6.73 / 6.71 | 0.278 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 6.73 / 6.71 | 0.278 |
| Rooms | 0 | 5 | 6.43 / 6.43 | 0.29 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 0.29 |
| Audio guide | 0 | Audio guide | 6.09 / 6 | 0.306 |
| Audio guide | 0 | About 0:46 | 6.09 / 6 | 0.306 |
| Rooms | 0 | icon: Previous room: Thunder | 6.34 / 6.34 | 0.294 |
| Rooms | 0 | icon: Next room: Wind | 6.18 / 6.18 | 0.302 |
| Audio guide | 0 | icon: Play the audio guide | 5.84 / 5.84 | 0.317 |
| window | 580 | painter’s home, in a Paris rebuilt with wide streets | 6.62 / 6.59 | 0.282 |
| window | 580 | and uniform stone façades. A green lamppost splits | 6.71 / 6.69 | 0.278 |
| window | 580 | the canvas in two; the couple on the right walk | 6.71 / 6.69 | 0.278 |
| window | 580 | straight toward us, looking at something beyond | 6.71 / 6.69 | 0.278 |
| window | 580 | the frame. | 6.71 / 6.7 | 0.278 |
| window | 580 | Nearly life-size, it is Caillebotte’s largest painting. He | 6.79 / 6.71 | 0.275 |
| window | 580 | showed it at the third Impressionist exhibition in 1877, | 6.79 / 6.71 | 0.275 |
| window | 580 | the year he made it. | 6.73 / 6.7 | 0.278 |
| window | 580 | Weather | 8.36 / 8.33 | 0.215 |
| window | 580 | Light rain, overcast | 8.36 / 8.36 | 0.215 |
| window | 580 | Artist | 8.36 / 8.36 | 0.215 |
| window | 580 | Gustave Caillebotte ( French, 1848–1894 ) | 8.36 / 8.36 | 0.215 |
| window | 580 | Date | 8.46 / 8.46 | 0.211 |
| window | 580 | 1877 | 8.33 / 8.33 | 0.216 |
| window | 580 | Medium | 8.46 / 8.44 | 0.211 |
| window | 580 | Oil on canvas | 8.33 / 8.33 | 0.216 |
| window | 580 | Size | 8.46 / 8.44 | 0.211 |
| window | 580 | 212.2 × 276.2 cm | 8.33 / 8.33 | 0.216 |
| window | 580 | Collection | 8.33 / 8.33 | 0.216 |
| window | 580 | The Art Institute of Chicago | 8.33 / 8.33 | 0.216 |
| window | 580 | Credit | 8.44 / 8.36 | 0.212 |
| window | 580 | Charles H. and Mary F. S. Worcester | 8.33 / 8.33 | 0.216 |
| window | 580 | Number | 8.36 / 8.36 | 0.215 |
| window | 580 | 1964.336 | 8.33 / 8.33 | 0.216 |
| window | 580 | Photograph: The Art Institute of Chicago , open access, public | 6.71 / 6.71 | 0.278 |
| window | 580 | domain. | 6.73 / 6.73 | 0.278 |

### CSS tier · dark · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.61 / 6.53 | 0.282 |
| window | 0 | Room 6 of 8 | 6.54 / 6.53 | 0.285 |
| window | 0 | Wind (large) | 6.71 / 6.65 | 0.278 |
| window | 0 | Wheat Field with Cypresses (large) | 6.71 / 6.7 | 0.278 |
| window | 0 | Vincent van Gogh | 6.73 / 6.61 | 0.278 |
| window | 0 | Dutch, 1853–1890 · 1889 | 6.73 / 6.63 | 0.278 |
| window | 0 | The whole work. The outline marks the part around you. | 6.74 / 6.73 | 0.277 |
| window | 0 | Everything in this field is moving the same way. The | 6.74 / 6.73 | 0.277 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 6.82 / 6.73 | 0.274 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 6.82 / 6.73 | 0.274 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 6.83 / 6.73 | 0.273 |
| window | 0 | the paint on so heavily that the brushstrokes | 6.83 / 6.73 | 0.273 |
| window | 0 | themselves take the shape of the wind. | 6.83 / 6.73 | 0.273 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 6.83 / 6.74 | 0.273 |
| Rooms | 0 | 6 | 6.43 / 6.43 | 0.29 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 0.29 |
| Audio guide | 0 | Audio guide | 6.44 / 6.4 | 0.29 |
| Audio guide | 0 | About 0:51 | 6.45 / 6.42 | 0.289 |
| Rooms | 0 | icon: Previous room: Rain | 6.43 / 6.35 | 0.29 |
| Rooms | 0 | icon: Next room: Gale | 6.35 / 6.34 | 0.294 |
| Audio guide | 0 | icon: Play the audio guide | 6.29 / 6.27 | 0.297 |
| window | 580 | He painted it in late June or early July 1889 at Saint-Rémy | 6.62 / 6.61 | 0.282 |
| window | 580 | Saint-Rémy in Provence, where he was a patient at the | 6.71 / 6.71 | 0.278 |
| window | 580 | asylum of Saint-Paul-de-Mausole, working outdoors | 6.71 / 6.7 | 0.278 |
| window | 580 | in front of the motif. | 6.71 / 6.63 | 0.278 |
| window | 580 | He counted it among his best summer canvases, and | 6.73 / 6.63 | 0.278 |
| window | 580 | that September made two studio versions of it: one | 6.73 / 6.71 | 0.278 |
| window | 580 | now in the National Gallery, London, the other a | 6.73 / 6.73 | 0.278 |
| window | 580 | smaller copy for his mother and sister. | 6.74 / 6.73 | 0.277 |
| window | 580 | Weather | 8.36 / 8.25 | 0.215 |
| window | 580 | Summer wind, fast cloud | 8.36 / 8.36 | 0.215 |
| window | 580 | Artist | 8.33 / 8.25 | 0.216 |
| window | 580 | Vincent van Gogh ( Dutch, 1853–1890 ) | 8.36 / 8.33 | 0.215 |
| window | 580 | Date | 8.33 / 8.25 | 0.216 |
| window | 580 | 1889 | 8.36 / 8.36 | 0.215 |
| window | 580 | Medium | 8.33 / 8.25 | 0.216 |
| window | 580 | Oil on canvas | 8.36 / 8.36 | 0.215 |
| window | 580 | Size | 8.25 / 8.25 | 0.219 |
| window | 580 | 73.2 × 93.4 cm | 8.36 / 8.36 | 0.215 |
| window | 580 | Collection | 8.36 / 8.25 | 0.215 |
| window | 580 | The Metropolitan Museum of Art, New York | 8.36 / 8.36 | 0.215 |
| window | 580 | Credit | 8.33 / 8.25 | 0.216 |
| window | 580 | Purchase, The Annenberg Foundation Gift, | 8.37 / 8.36 | 0.215 |
| window | 580 | 1993 | 8.37 / 8.36 | 0.215 |
| window | 580 | Number | 8.33 / 8.25 | 0.216 |
| window | 580 | 1993.132 | 8.39 / 8.37 | 0.214 |
| window | 580 | Photograph: The Metropolitan Museum of Art, New York , open | 6.83 / 6.75 | 0.273 |
| window | 580 | access, public domain. | 6.75 / 6.73 | 0.276 |

### CSS tier · dark · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.72 / 6.63 | 0.278 |
| window | 0 | Room 7 of 8 | 6.7 / 6.7 | 0.279 |
| window | 0 | Gale (large) | 6.81 / 6.81 | 0.274 |
| window | 0 | Northeaster (large) | 6.81 / 6.81 | 0.274 |
| window | 0 | Winslow Homer | 6.81 / 6.72 | 0.274 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 6.79 / 6.79 | 0.275 |
| window | 0 | The whole work. The outline marks the part around you. | 6.82 / 6.81 | 0.274 |
| window | 0 | A northeaster is a winter storm that drives in off the | 6.82 / 6.79 | 0.274 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 6.89 / 6.79 | 0.271 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 6.91 / 6.79 | 0.27 |
| window | 0 | lived and painted for the last decades of his life. | 6.93 / 6.79 | 0.269 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 7.03 / 6.82 | 0.265 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 7.1 / 6.98 | 0.262 |
| window | 0 | lower left. By 1900 he had painted them out and | 7.08 / 7.08 | 0.263 |
| Rooms | 0 | 7 | 7.59 / 7.59 | 0.243 |
| Rooms | 0 | / 8 | 7.59 / 7.59 | 0.243 |
| Audio guide | 0 | Audio guide | 8.12 / 7.93 | 0.224 |
| Audio guide | 0 | About 0:50 | 7.93 / 7.9 | 0.231 |
| Rooms | 0 | icon: Previous room: Wind | 7.61 / 7.61 | 0.242 |
| Rooms | 0 | icon: Next room: Fog | 7.59 / 7.54 | 0.243 |
| Audio guide | 0 | icon: Play the audio guide | 7.86 / 7.72 | 0.233 |
| window | 508 | When he first exhibited this canvas in 1895, two men | 6.73 / 6.7 | 0.278 |
| window | 508 | in foul-weather gear crouched on the rocks at the | 6.73 / 6.72 | 0.278 |
| window | 508 | lower left. By 1900 he had painted them out and | 6.79 / 6.73 | 0.275 |
| window | 508 | raised a much larger column of spray. What is left is | 6.79 / 6.72 | 0.275 |
| window | 508 | rock, water and air: the dark ledge, the green body of | 6.79 / 6.72 | 0.275 |
| window | 508 | the wave and the white burst where they meet. | 6.79 / 6.73 | 0.275 |
| window | 508 | A critic in 1901 praised it for “great natural spaces | 6.79 / 6.79 | 0.275 |
| window | 508 | unmarked by the presence of puny man.” | 6.79 / 6.79 | 0.275 |
| window | 508 | Weather | 8.36 / 8.33 | 0.215 |
| window | 508 | Winter northeaster off the Atlantic | 8.36 / 8.36 | 0.215 |
| window | 508 | Artist | 8.36 / 8.33 | 0.215 |
| window | 508 | Winslow Homer ( American, 1836–1910 ) | 8.36 / 8.36 | 0.215 |
| window | 508 | Date | 8.33 / 8.33 | 0.216 |
| window | 508 | 1895; reworked by 1901 | 8.44 / 8.36 | 0.212 |
| window | 508 | Medium | 8.36 / 8.33 | 0.215 |
| window | 508 | Oil on canvas | 8.46 / 8.38 | 0.211 |
| window | 508 | Size | 8.36 / 8.36 | 0.215 |
| window | 508 | 87.6 × 127 cm | 8.46 / 8.46 | 0.211 |
| window | 508 | Collection | 8.47 / 8.36 | 0.211 |
| window | 508 | The Metropolitan Museum of Art, New York | 8.44 / 8.33 | 0.212 |
| window | 508 | Credit | 8.57 / 8.57 | 0.207 |
| window | 508 | Gift of George A. Hearn, 1910 | 8.57 / 8.44 | 0.207 |
| window | 508 | Number | 8.68 / 8.66 | 0.203 |
| window | 508 | 10.64.5 | 8.66 / 8.66 | 0.204 |
| window | 508 | Photograph: The Metropolitan Museum of Art, New York , open | 7.08 / 7.08 | 0.263 |
| window | 508 | access, public domain. | 7.1 / 7.1 | 0.262 |

### CSS tier · dark · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.73 / 6.64 | 0.278 |
| window | 0 | Room 8 of 8 | 6.71 / 6.63 | 0.278 |
| window | 0 | Fog (large) | 6.8 / 6.73 | 0.275 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 6.82 / 6.8 | 0.274 |
| window | 0 | Claude Monet | 6.82 / 6.73 | 0.274 |
| window | 0 | French, 1840–1926 · 1900 | 6.82 / 6.8 | 0.274 |
| window | 0 | The whole work. The outline marks the part around you. | 6.93 / 6.91 | 0.269 |
| window | 0 | Without the fog, Monet once remarked, London | 6.93 / 6.93 | 0.269 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 6.93 / 6.91 | 0.269 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 6.93 / 6.91 | 0.269 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 6.91 / 6.84 | 0.27 |
| window | 0 | he came to paint it. | 6.83 / 6.82 | 0.273 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 6.91 / 6.83 | 0.27 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 6.91 / 6.82 | 0.27 |
| Rooms | 0 | 8 | 6.49 / 6.49 | 0.288 |
| Rooms | 0 | / 8 | 6.49 / 6.49 | 0.288 |
| Audio guide | 0 | Audio guide | 6.82 / 6.75 | 0.274 |
| Audio guide | 0 | About 0:50 | 6.82 / 6.75 | 0.274 |
| Rooms | 0 | icon: Previous room: Gale | 6.31 / 6.27 | 0.296 |
| Audio guide | 0 | icon: Play the audio guide | 6.82 / 6.81 | 0.274 |
| window | 534 | He painted Waterloo Bridge in the mornings from his | 6.8 / 6.73 | 0.275 |
| window | 534 | fifth-floor window at the Savoy Hotel, moving on to | 6.82 / 6.8 | 0.274 |
| window | 534 | Charing Cross Bridge later in the day. Here the bridge | 6.82 / 6.79 | 0.274 |
| window | 534 | is a dark band of arches, and the city behind it is only | 6.8 / 6.79 | 0.275 |
| window | 534 | chimneys and towers in the haze. | 6.82 / 6.8 | 0.274 |
| window | 534 | He finished the London pictures in his studio at | 6.82 / 6.82 | 0.274 |
| window | 534 | Giverny, and would not release any of them until he | 6.82 / 6.82 | 0.274 |
| window | 534 | was satisfied with the series as a whole. | 6.82 / 6.82 | 0.274 |
| window | 534 | Weather | 8.36 / 8.33 | 0.215 |
| window | 534 | Winter fog and coal smoke | 8.38 / 8.36 | 0.214 |
| window | 534 | Artist | 8.36 / 8.36 | 0.215 |
| window | 534 | Claude Monet ( French, 1840–1926 ) | 8.47 / 8.46 | 0.211 |
| window | 534 | Date | 8.4 / 8.38 | 0.213 |
| window | 534 | 1900 | 8.46 / 8.46 | 0.211 |
| window | 534 | Medium | 8.48 / 8.4 | 0.21 |
| window | 534 | Oil on canvas | 8.48 / 8.48 | 0.21 |
| window | 534 | Size | 8.48 / 8.4 | 0.21 |
| window | 534 | 65.4 × 92.6 cm | 8.49 / 8.47 | 0.21 |
| window | 534 | Collection | 8.46 / 8.38 | 0.211 |
| window | 534 | The Art Institute of Chicago | 8.49 / 8.47 | 0.21 |
| window | 534 | Credit | 8.36 / 8.36 | 0.215 |
| window | 534 | Gift of Mrs. Mortimer B. Harris | 8.49 / 8.37 | 0.21 |
| window | 534 | Number | 8.36 / 8.33 | 0.215 |
| window | 534 | 1984.1173 | 8.44 / 8.37 | 0.212 |
| window | 534 | Photograph: The Art Institute of Chicago , open access, public | 6.91 / 6.8 | 0.27 |
| window | 534 | domain. | 6.73 / 6.71 | 0.277 |

### CSS tier · dark · rooms view · active (cells are p10; the current room's row is lifted)

| line | frost | cloud | clearing | thunder | rain | wind | gale | fog |
|---|---|---|---|---|---|---|---|---|
| Weather in Painting | 6.51 | 6.91 | 7.47 | 7.67 | 6.5 | 6.53 | 6.63 | 6.64 |
| 8 rooms | 6.27 | 6.89 | 7.18 | 7.67 | 6.54 | 6.54 | 6.7 | 6.63 |
| Eight skies, 1608–1900 | 6.61 | 6.99 | 7.4 | 7.67 | 6.61 | 6.65 | 6.7 | 6.8 |
| For most of the history of European painting the sky | 6.62 | 6.91 | 7.28 | 7.6 | 6.69 | 6.63 | 6.72 | 6.8 |
| was the back wall of the picture. This exhibition | 6.69 | 6.91 | 7.37 | 7.57 | 6.71 | 6.71 | 6.73 | 6.8 |
| follows it becoming the subject: eight rooms, each | 6.62 | 6.89 | 7.3 | 7.46 | 6.71 | 6.71 | 6.73 | 6.8 |
| holding one work, from a Dutch winter in the Little Ice | 6.61 | 6.89 | 7.28 | 7.38 | 6.71 | 6.7 | 6.72 | 6.8 |
| Age to a London fog that was largely coal smoke. | 6.69 | 6.89 | 7.37 | 7.36 | 6.73 | 6.72 | 6.79 | 6.82 |
| Each work fills the room. Its label sits beside it, and | 6.69 | 6.89 | 7.37 | 7.36 | 6.73 | 6.73 | 6.79 | 6.82 |
| the audio guide reads the label aloud in your | 6.71 | 6.89 | 7.37 | 7.38 | 6.81 | 6.74 | 6.79 | 6.82 |
| browser’s own voice. | 6.75 | 6.89 | 7.48 | 7.45 | 6.74 | 6.65 | 6.74 | 6.82 |
| Rooms | 6.75 | 6.82 | 7.41 | 7.45 | 6.89 | 6.65 | 6.72 | 6.82 |
| 01 · Frost | 5.02 | 6.98 | 7.48 | 7.48 | 6.73 | 6.81 | 6.82 | 6.91 |
| · you are here | 5.02 | 5.08 | 5.46 | 5.52 | 4.97 | 4.97 | 5.01 | 5.05 |
| Winter Landscape with Ice Skaters | 5.02 | 6.98 | 7.38 | 7.48 | 6.73 | 6.74 | 6.82 | 6.93 |
| Hendrick Avercamp , c. 1608 | 5.02 | 6.91 | 7.48 | 7.46 | 6.71 | 6.74 | 6.82 | 6.93 |
| 02 · Cloud | 6.79 | 5.03 | 7.58 | 7.44 | 6.73 | 6.74 | 6.91 | 6.91 |
| The Windmill at Wijk bij Duurstede | 6.79 | 5.03 | 7.51 | 7.56 | 6.71 | 6.82 | 6.79 | 6.91 |
| Jacob van Ruisdael , c. 1668–70 | 6.79 | 5.03 | 7.51 | 7.68 | 6.71 | 6.82 | 6.89 | 6.89 |
| 03 · Clearing | 6.81 | 6.89 | 5.52 | 7.77 | 6.73 | 6.82 | 7.1 | 6.83 |
| View from Mount Holyoke, Northampton, | 6.87 | 6.89 | 5.46 | 7.65 | 6.73 | 6.83 | 6.91 | 6.83 |
| Massachusetts, after a Thunderstorm—The | 6.87 | 6.89 | 5.45 | 7.46 | 6.71 | 6.83 | 6.98 | 6.83 |
| Oxbow | 6.88 | 6.89 | 5.53 | 7.51 | 6.73 | 6.83 | 7.1 | 6.83 |
| Thomas Cole , 1836 | 6.81 | 6.83 | 5.45 | 7.14 | 6.63 | 6.83 | 7.08 | 6.82 |
| 04 · Thunder | 6.69 | 7.08 | 7.49 | 5.52 | 6.69 | 6.71 | 6.79 | 6.82 |
| Approaching Thunder Storm | 6.69 | 7.01 | 7.47 | 5.52 | 6.69 | 6.71 | 6.72 | 6.82 |
| Martin Johnson Heade , 1859 | 6.69 | 7.01 | 7.47 | 5.52 | 6.69 | 6.71 | 6.73 | 6.82 |
| 05 · Rain | 6.71 | 7.08 | 7.5 | 7.57 | 4.95 | 6.73 | 6.81 | 6.82 |
| Paris Street; Rainy Day | 6.69 | 6.99 | 7.4 | 7.48 | 4.95 | 6.73 | 6.79 | 6.8 |
| Gustave Caillebotte , 1877 | 6.69 | 6.99 | 7.4 | 7.45 | 4.97 | 6.73 | 6.79 | 6.82 |
| 06 · Wind | 6.71 | 7.08 | 7.48 | 7.45 | 6.73 | 4.97 | 6.79 | 6.82 |
| Wheat Field with Cypresses | 6.71 | 6.89 | 7.37 | 7.38 | 6.79 | 4.97 | 6.79 | 6.82 |
| Vincent van Gogh , 1889 | 6.71 | 6.99 | 7.41 | 7.38 | 6.81 | 4.97 | 6.79 | 6.82 |
| 07 · Gale | 6.83 | 6.99 | 7.49 | 7.45 | 6.81 | 6.74 | 5.01 | 6.82 |
| Northeaster | 6.81 | 6.99 | 7.49 | 7.45 | 6.81 | 6.74 | 5.01 | 6.82 |
| Winslow Homer , 1895; reworked by 1901 | 6.73 | 6.91 | 7.37 | 7.45 | 6.73 | 6.74 | 5.01 | 6.91 |
| 08 · Fog | 6.83 | 6.98 | 7.48 | 7.48 | 6.79 | 6.81 | 6.82 | 5.03 |
| Waterloo Bridge, Gray Weather | 6.53 | 6.91 | 7.4 | 7.46 | 6.59 | 6.62 | 6.63 | 4.97 |
| Claude Monet , 1900 | 6.62 | 6.91 | 7.48 | 7.44 | 6.62 | 6.71 | 6.72 | 5.02 |
| Viewing | 8.21 | 8.36 | 9.02 | 9.1 | 8.33 | 8.23 | 8.35 | 8.33 |
| Reduce transparency | 8.23 | 8.37 | 9.01 | 9.09 | 8.33 | 8.23 | 8.33 | 8.33 |
| Frosts the label and the controls so the painting | 8.31 | 8.44 | 8.87 | 8.96 | 8.33 | 8.33 | 8.33 | 8.33 |
| shows through less. | 8.21 | 8.36 | 9.01 | 8.99 | 8.33 | 8.25 | 8.33 | 8.33 |
| Photographs | 6.63 | 6.89 | 7.48 | 7.45 | 6.72 | 6.67 | 6.79 | 6.81 |
| Hendrick Avercamp , Winter Landscape with Ice Skaters : | 6.71 | 6.89 | 7.37 | 7.38 | 6.81 | 6.74 | 6.79 | 6.82 |
| Rijksmuseum, Amsterdam , open access, public domain. | 6.71 | 6.89 | 7.37 | 7.38 | 6.81 | 6.73 | 6.81 | 6.82 |
| Jacob van Ruisdael , The Windmill at Wijk bij Duurstede : | 6.71 | 6.89 | 7.37 | 7.38 | 6.81 | 6.73 | 6.81 | 6.82 |
| Thomas Cole , View from Mount Holyoke, Northampton, | 6.73 | 6.89 | 7.37 | 7.45 | 6.73 | 6.73 | 6.81 | 6.84 |
| Massachusetts, after a Thunderstorm—The Oxbow : The | 6.8 | 6.89 | 7.37 | 7.48 | 6.73 | 6.73 | 6.81 | 6.91 |
| Metropolitan Museum of Art, New York , open access, public | 6.79 | 6.89 | 7.37 | 7.44 | 6.71 | 6.73 | 6.79 | 6.93 |
| domain. | 6.79 | 6.8 | 7.38 | 7.45 | 6.82 | 6.63 | 6.73 | 6.86 |
| Martin Johnson Heade , Approaching Thunder Storm : The | 6.79 | 6.89 | 7.4 | 7.44 | 6.71 | 6.73 | 6.81 | 6.93 |
| Gustave Caillebotte , Paris Street; Rainy Day : The Art Institute of | 6.79 | 6.89 | 7.51 | 7.56 | 6.71 | 6.73 | 6.79 | 6.89 |
| Chicago , open access, public domain. | 6.79 | 6.8 | 7.47 | 6.98 | 6.61 | 6.72 | 6.91 | 6.73 |
| Vincent van Gogh , Wheat Field with Cypresses : The Metropolitan | 6.81 | 6.89 | 7.51 | 7.77 | 6.71 | 6.73 | 6.79 | 6.82 |
| Museum of Art, New York , open access, public domain. | 6.81 | 6.89 | 7.51 | 7.77 | 6.73 | 6.73 | 6.91 | 6.82 |
| Winslow Homer , Northeaster : The Metropolitan Museum of Art, | 6.87 | 6.83 | 7.51 | 7.58 | 6.73 | 6.73 | 6.98 | 6.83 |
| New York , open access, public domain. | 6.88 | 6.82 | 7.49 | 7.37 | 6.73 | 6.73 | 7.08 | 6.8 |
| Claude Monet , Waterloo Bridge, Gray Weather : The Art Institute of | 6.81 | 6.82 | 7.49 | 7.18 | 6.71 | 6.74 | 7.08 | 6.82 |

## CSS tier at DPR 2, collapsed body

`?tier=css`, DPR 2 (`cssBody: collapsed`), 1440 × 900, active pose, label view. 812 line readings, 0 under floor. Worst p10 5.32: dark, active, frost, label view, Audio guide, “About 0:51”.

### CSS tier at DPR 2, collapsed body · light · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 12.6 / 12.32 | 0.903 |
| window | 0 | Room 1 of 8 | 13.76 / 13.62 | 0.952 |
| window | 0 | Frost (large) | 12.45 / 12.23 | 0.897 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 12.9 / 12.08 | 0.915 |
| window | 0 | Hendrick Avercamp | 12.39 / 12.06 | 0.894 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 12.54 / 12.24 | 0.9 |
| window | 0 | The whole work. The outline marks the part around you. | 11.17 / 10.35 | 0.842 |
| window | 0 | Avercamp made his name painting winter, in the years | 11.26 / 10.76 | 0.845 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 11.4 / 11.03 | 0.851 |
| window | 0 | Countries. Here a whole village has moved onto the | 11.39 / 11.02 | 0.851 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 11.08 / 10.72 | 0.837 |
| window | 0 | sledge on the right, a church on the left. | 10.97 / 10.5 | 0.832 |
| window | 0 | Look at how the air is built. The figures in front are | 10.68 / 10.32 | 0.82 |
| window | 0 | sharp and full of colour; a few hundred metres back | 10.61 / 10.27 | 0.816 |
| Rooms | 0 | 1 | 12.49 / 12.01 | 0.898 |
| Rooms | 0 | / 8 | 12.84 / 12.56 | 0.913 |
| Audio guide | 0 | Audio guide | 13.07 / 12.71 | 0.923 |
| Audio guide | 0 | About 0:51 | 13.24 / 13.09 | 0.93 |
| Rooms | 0 | icon: Next room: Cloud | 13.01 / 12.97 | 0.92 |
| Audio guide | 0 | icon: Play the audio guide | 12 / 11.49 | 0.877 |
| window | 554 | Look at how the air is built. The figures in front are | 13.2 / 12.53 | 0.928 |
| window | 554 | sharp and full of colour; a few hundred metres back | 13.11 / 12.52 | 0.924 |
| window | 554 | they thin into grey-white haze, and the far bank all | 12.94 / 12.26 | 0.917 |
| window | 554 | but dissolves. That haze is the weather: cold, damp | 12.95 / 12.08 | 0.918 |
| window | 554 | air thick enough to carry the light. | 12.56 / 12.01 | 0.901 |
| window | 554 | Avercamp signed the picture on the wall of a wooden | 12.85 / 12.29 | 0.913 |
| window | 554 | shed on the right, among the scratched graffiti, | 12.68 / 12.25 | 0.906 |
| window | 554 | where it is easy to miss. | 12.12 / 11.91 | 0.883 |
| window | 554 | Weather | 10.06 / 9.88 | 0.792 |
| window | 554 | Hard frost, haze over the ice | 11.18 / 9.77 | 0.842 |
| window | 554 | Artist | 9.71 / 9.69 | 0.775 |
| window | 554 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 11.05 / 9.91 | 0.836 |
| window | 554 | Date | 9.56 / 9.55 | 0.768 |
| window | 554 | c. 1608 | 9.94 / 9.78 | 0.786 |
| window | 554 | Medium | 9.44 / 9.42 | 0.763 |
| window | 554 | Oil on panel | 10.13 / 9.89 | 0.795 |
| window | 554 | Size | 9.74 / 9.66 | 0.777 |
| window | 554 | 77.3 × 131.9 cm | 9.91 / 9.81 | 0.784 |
| window | 554 | Collection | 10.41 / 10.01 | 0.808 |
| window | 554 | Rijksmuseum, Amsterdam | 10.34 / 10.16 | 0.804 |
| window | 554 | Credit | 9.77 / 9.65 | 0.778 |
| window | 554 | Purchased with the support of the | 10.09 / 9.95 | 0.793 |
| window | 554 | Vereniging Rembrandt | 10.07 / 9.99 | 0.791 |
| window | 554 | Number | 9.41 / 9.35 | 0.761 |
| window | 554 | SK-A-1718 | 10.07 / 9.93 | 0.792 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 10.59 / 10.27 | 0.816 |
| window | 554 | domain. | 10.3 / 10.27 | 0.803 |

### CSS tier at DPR 2, collapsed body · light · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.97 / 9.89 | 0.788 |
| window | 0 | Room 2 of 8 | 10.06 / 10.04 | 0.792 |
| window | 0 | Cloud (large) | 9.95 / 9.89 | 0.787 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 10.2 / 9.97 | 0.798 |
| window | 0 | Jacob van Ruisdael | 10.12 / 9.97 | 0.794 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 10.22 / 10.12 | 0.799 |
| window | 0 | The whole work. The outline marks the part around you. | 10.72 / 10.35 | 0.822 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 10.89 / 10.54 | 0.829 |
| window | 0 | more than half the canvas, and he paints it as a | 10.87 / 10.56 | 0.828 |
| window | 0 | structure: banks of cumulus heaped over one | 10.81 / 10.59 | 0.825 |
| window | 0 | another, grey underneath, lit at their edges by a sun | 10.95 / 10.79 | 0.832 |
| window | 0 | we cannot see. | 11.05 / 10.96 | 0.836 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 11.65 / 11.47 | 0.863 |
| window | 0 | A sailing boat is out on the water, the towers of | 11.65 / 11.62 | 0.862 |
| Rooms | 0 | 2 | 9.97 / 9.95 | 0.788 |
| Rooms | 0 | / 8 | 10.21 / 10.12 | 0.799 |
| Audio guide | 0 | Audio guide | 10.21 / 10.2 | 0.799 |
| Audio guide | 0 | About 0:49 | 10.07 / 9.96 | 0.792 |
| Rooms | 0 | icon: Previous room: Frost | 10.01 / 9.97 | 0.789 |
| Rooms | 0 | icon: Next room: Clearing | 9.98 / 9.94 | 0.788 |
| Audio guide | 0 | icon: Play the audio guide | 10.15 / 10.07 | 0.796 |
| window | 554 | Below, the mill stands near the bank of the river Lek. | 10.2 / 9.94 | 0.798 |
| window | 554 | A sailing boat is out on the water, the towers of | 10.06 / 9.94 | 0.792 |
| window | 554 | Duurstede castle and the church rise in the distance, | 10.2 / 9.94 | 0.798 |
| window | 554 | and a few women walk along the bank, very small | 10.2 / 9.97 | 0.798 |
| window | 554 | against the mill. | 10.04 / 9.97 | 0.791 |
| window | 554 | Dutch painters of the seventeenth century made the | 10.38 / 10.12 | 0.806 |
| window | 554 | sky a subject in its own right. Few made it carry as | 10.61 / 10.2 | 0.817 |
| window | 554 | much of a picture as this. | 10.28 / 10.14 | 0.802 |
| window | 554 | Weather | 9.72 / 9.6 | 0.776 |
| window | 554 | Heaped cumulus, sun breaking through | 9.62 / 9.19 | 0.771 |
| window | 554 | Artist | 9.95 / 9.84 | 0.787 |
| window | 554 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 9.61 / 9.28 | 0.771 |
| window | 554 | Date | 9.95 / 9.95 | 0.787 |
| window | 554 | c. 1668–70 | 9.53 / 9.43 | 0.767 |
| window | 554 | Medium | 10.01 / 9.95 | 0.789 |
| window | 554 | Oil on canvas | 9.78 / 9.68 | 0.779 |
| window | 554 | Size | 10.09 / 10.09 | 0.793 |
| window | 554 | 83 × 101 cm | 9.95 / 9.85 | 0.787 |
| window | 554 | Collection | 10.01 / 9.94 | 0.789 |
| window | 554 | Rijksmuseum, Amsterdam | 9.7 / 9.61 | 0.775 |
| window | 554 | Credit | 9.95 / 9.93 | 0.787 |
| window | 554 | On loan from the City of Amsterdam (A. van | 9.85 / 9.78 | 0.782 |
| window | 554 | der Hoop Bequest) | 10.08 / 10.01 | 0.793 |
| window | 554 | Number | 10.3 / 10.14 | 0.803 |
| window | 554 | SK-C-211 | 10.59 / 10.51 | 0.816 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 11.59 / 11.47 | 0.86 |
| window | 554 | domain. | 11.38 / 11.3 | 0.851 |

### CSS tier at DPR 2, collapsed body · light · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 10.07 / 9.98 | 0.792 |
| window | 0 | Room 3 of 8 | 10.52 / 10.43 | 0.813 |
| window | 0 | Clearing (large) | 10.18 / 10.03 | 0.797 |
| window | 0 | View from Mount Holyoke, (large) | 10.19 / 10.03 | 0.798 |
| window | 0 | Northampton, Massachusetts, (large) | 10.22 / 10.01 | 0.799 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 10.27 / 10.04 | 0.801 |
| window | 0 | Thomas Cole | 10.09 / 9.89 | 0.793 |
| window | 0 | American, born England, 1801–1848 · 1836 | 10.27 / 10 | 0.801 |
| window | 0 | The whole work. The outline marks the part around you. | 10.15 / 10 | 0.796 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 9.99 / 9.93 | 0.788 |
| window | 0 | valley. On the left it still hangs over wild, broken | 9.93 / 9.91 | 0.786 |
| window | 0 | trees, and rain falls in grey veils across the hills. On | 9.94 / 9.81 | 0.786 |
| window | 0 | the right the air has cleared over cleared land: fields, | 9.96 / 9.81 | 0.787 |
| window | 0 | farms and the river’s great loop. | 9.94 / 9.81 | 0.786 |
| Rooms | 0 | 3 | 9.8 / 9.69 | 0.779 |
| Rooms | 0 | / 8 | 9.98 / 9.89 | 0.788 |
| Audio guide | 0 | Audio guide | 9.54 / 9.25 | 0.767 |
| Audio guide | 0 | About 0:50 | 9.52 / 9.42 | 0.767 |
| Rooms | 0 | icon: Previous room: Cloud | 9.56 / 9.5 | 0.769 |
| Rooms | 0 | icon: Next room: Thunder | 9.56 / 9.47 | 0.768 |
| Audio guide | 0 | icon: Play the audio guide | 9.78 / 9.55 | 0.779 |
| window | 610 | Cole divided the picture along a diagonal, and the | 10.27 / 10.06 | 0.801 |
| window | 610 | weather does the dividing. He painted it for the 1836 | 10.27 / 10.06 | 0.801 |
| window | 610 | annual exhibition of the National Academy of Design, | 10.27 / 10.06 | 0.801 |
| window | 610 | calling the view from Mount Holyoke “about the finest | 10.27 / 10.03 | 0.801 |
| window | 610 | scene I have in my sketchbook.” | 10.18 / 9.97 | 0.797 |
| window | 610 | Look for the painter himself near the bottom of the | 10.27 / 10.06 | 0.801 |
| window | 610 | canvas: a small figure at an easel among the rocks, | 10.33 / 10.06 | 0.804 |
| window | 610 | turning back toward us. | 10.24 / 9.91 | 0.8 |
| window | 610 | Weather | 9.26 / 9.16 | 0.754 |
| window | 610 | Thunderstorm passing, sun on the valley | 9.55 / 9.31 | 0.768 |
| window | 610 | Artist | 9.38 / 9.3 | 0.76 |
| window | 610 | Thomas Cole ( American, born England, | 9.46 / 9.25 | 0.764 |
| window | 610 | 1801–1848 ) | 9.33 / 9.24 | 0.758 |
| window | 610 | Date | 9.48 / 9.48 | 0.765 |
| window | 610 | 1836 | 9.25 / 9.25 | 0.754 |
| window | 610 | Medium | 9.32 / 9.26 | 0.757 |
| window | 610 | Oil on canvas | 9.18 / 9.08 | 0.751 |
| window | 610 | Size | 9.09 / 9.01 | 0.746 |
| window | 610 | 130.8 × 193 cm | 9.08 / 9.06 | 0.746 |
| window | 610 | Collection | 9.08 / 9.01 | 0.746 |
| window | 610 | The Metropolitan Museum of Art, New York | 9.03 / 9.01 | 0.743 |
| window | 610 | Credit | 9.08 / 9.01 | 0.746 |
| window | 610 | Gift of Mrs. Russell Sage, 1908 | 9.01 / 8.9 | 0.743 |
| window | 610 | Number | 9.06 / 9.02 | 0.745 |
| window | 610 | 08.228 | 8.9 / 8.9 | 0.737 |
| window | 610 | Photograph: The Metropolitan Museum of Art, New York , open | 9.94 / 9.83 | 0.786 |
| window | 610 | access, public domain. | 9.77 / 9.76 | 0.778 |

### CSS tier at DPR 2, collapsed body · light · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 9.87 / 9.78 | 0.783 |
| window | 0 | Room 4 of 8 | 9.86 / 9.76 | 0.782 |
| window | 0 | Thunder (large) | 10.01 / 9.93 | 0.789 |
| window | 0 | Approaching Thunder Storm (large) | 10.03 / 10.01 | 0.79 |
| window | 0 | Martin Johnson Heade | 10.12 / 10.03 | 0.795 |
| window | 0 | American, 1819–1904 · 1859 | 10.38 / 10.03 | 0.806 |
| window | 0 | The whole work. The outline marks the part around you. | 10.27 / 10.14 | 0.801 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 10.47 / 10.19 | 0.81 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 10.39 / 10.16 | 0.807 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 9.97 / 9.86 | 0.787 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 9.79 / 9.77 | 0.779 |
| window | 0 | rower pulls for shore; a white sail stands out against | 9.77 / 9.75 | 0.778 |
| window | 0 | the dark. | 9.75 / 9.61 | 0.778 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 9.85 / 9.77 | 0.782 |
| Rooms | 0 | 4 | 10.31 / 10.14 | 0.802 |
| Rooms | 0 | / 8 | 10.7 / 10.39 | 0.819 |
| Audio guide | 0 | Audio guide | 11.51 / 11.17 | 0.854 |
| Audio guide | 0 | About 0:53 | 11.59 / 10.85 | 0.858 |
| Rooms | 0 | icon: Previous room: Clearing | 10.39 / 10.32 | 0.805 |
| Rooms | 0 | icon: Next room: Rain | 11.67 / 11.38 | 0.86 |
| Audio guide | 0 | icon: Play the audio guide | 10.86 / 10.62 | 0.827 |
| window | 618 | holds: not the storm itself but the minute before it. | 10.01 / 10.01 | 0.79 |
| window | 618 | Painted two years before the Civil War, it has often | 10.03 / 10.01 | 0.79 |
| window | 618 | been read as a picture of a country waiting for | 10.03 / 10.01 | 0.79 |
| window | 618 | something to break. Heade based it on a storm he | 10.11 / 10.03 | 0.794 |
| window | 618 | had watched from Prudence Island, in the bay, | 10.29 / 10.03 | 0.802 |
| window | 618 | around 1858. | 10.2 / 10.03 | 0.798 |
| window | 618 | Weather | 9.6 / 9.5 | 0.77 |
| window | 618 | Thunderstorm approaching over still water | 9.69 / 9.68 | 0.775 |
| window | 618 | Artist | 9.6 / 9.5 | 0.77 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 9.68 / 9.66 | 0.774 |
| window | 618 | 1819–1904 ) | 9.66 / 9.66 | 0.773 |
| window | 618 | Date | 9.58 / 9.49 | 0.769 |
| window | 618 | 1859 | 9.6 / 9.59 | 0.77 |
| window | 618 | Medium | 9.37 / 9.27 | 0.76 |
| window | 618 | Oil on canvas | 9.35 / 9.28 | 0.759 |
| window | 618 | Size | 9.35 / 9.22 | 0.758 |
| window | 618 | 71.1 × 111.8 cm | 9.37 / 9.35 | 0.76 |
| window | 618 | Collection | 9.65 / 9.55 | 0.772 |
| window | 618 | The Metropolitan Museum of Art, New York | 9.39 / 9.22 | 0.76 |
| window | 618 | Credit | 8.97 / 8.94 | 0.741 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 8.94 / 8.94 | 0.739 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 8.88 / 8.86 | 0.736 |
| window | 618 | 1975 | 8.86 / 8.86 | 0.735 |
| window | 618 | Number | 8.84 / 8.7 | 0.734 |
| window | 618 | 1975.160 | 8.88 / 8.86 | 0.736 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 10.07 / 9.77 | 0.792 |
| window | 620 | holds: not the storm itself but the minute before it. | 10.01 / 10.01 | 0.79 |
| window | 620 | Painted two years before the Civil War, it has often | 10.03 / 10.01 | 0.79 |
| window | 620 | been read as a picture of a country waiting for | 10.03 / 10.01 | 0.79 |
| window | 620 | something to break. Heade based it on a storm he | 10.11 / 10.03 | 0.794 |
| window | 620 | had watched from Prudence Island, in the bay, | 10.28 / 10.03 | 0.802 |
| window | 620 | around 1858. | 10.2 / 10.03 | 0.798 |
| window | 620 | Weather | 9.6 / 9.5 | 0.77 |
| window | 620 | Thunderstorm approaching over still water | 9.69 / 9.68 | 0.775 |
| window | 620 | Artist | 9.6 / 9.5 | 0.77 |
| window | 620 | Martin Johnson Heade ( American, 1819–1904 | 9.68 / 9.66 | 0.774 |
| window | 620 | 1819–1904 ) | 9.66 / 9.66 | 0.773 |
| window | 620 | Date | 9.58 / 9.49 | 0.769 |
| window | 620 | 1859 | 9.6 / 9.59 | 0.77 |
| window | 620 | Medium | 9.44 / 9.33 | 0.763 |
| window | 620 | Oil on canvas | 9.35 / 9.33 | 0.759 |
| window | 620 | Size | 9.34 / 9.22 | 0.758 |
| window | 620 | 71.1 × 111.8 cm | 9.35 / 9.34 | 0.759 |
| window | 620 | Collection | 9.65 / 9.56 | 0.772 |
| window | 620 | The Metropolitan Museum of Art, New York | 9.45 / 9.24 | 0.763 |
| window | 620 | Credit | 9.03 / 8.95 | 0.743 |
| window | 620 | Gift of Erving Wolf Foundation and Mr. and | 8.95 / 8.94 | 0.74 |
| window | 620 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 8.88 / 8.86 | 0.736 |
| window | 620 | 1975 | 8.86 / 8.86 | 0.735 |
| window | 620 | Number | 8.84 / 8.7 | 0.734 |
| window | 620 | 1975.160 | 8.88 / 8.86 | 0.736 |
| window | 620 | Photograph: The Metropolitan Museum of Art, New York , open | 10.04 / 9.78 | 0.791 |
| window | 620 | access, public domain. | 10.08 / 9.62 | 0.792 |

### CSS tier at DPR 2, collapsed body · light · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 12.98 / 11.51 | 0.919 |
| window | 0 | Room 5 of 8 | 11.52 / 11.45 | 0.857 |
| window | 0 | Rain (large) | 12.13 / 11.61 | 0.883 |
| window | 0 | Paris Street; Rainy Day (large) | 11.86 / 11.47 | 0.872 |
| window | 0 | Gustave Caillebotte | 11.85 / 11.2 | 0.871 |
| window | 0 | French, 1848–1894 · 1877 | 11.5 / 11.29 | 0.856 |
| window | 0 | The whole work. The outline marks the part around you. | 11.7 / 10.32 | 0.865 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 12.16 / 10.76 | 0.885 |
| window | 0 | paints the rain through what it does: the paving | 12.18 / 10.84 | 0.886 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 12.12 / 10.95 | 0.883 |
| window | 0 | everyone carries an umbrella, the newly invented | 12.08 / 10.93 | 0.881 |
| window | 0 | retractable kind. | 11.45 / 10.46 | 0.854 |
| window | 0 | The place is a busy intersection a short walk from the | 11.9 / 10.91 | 0.874 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 11.83 / 10.89 | 0.871 |
| Rooms | 0 | 5 | 10.47 / 10.41 | 0.81 |
| Rooms | 0 | / 8 | 10.66 / 10.51 | 0.819 |
| Audio guide | 0 | Audio guide | 11.85 / 11.64 | 0.871 |
| Audio guide | 0 | About 0:46 | 11.73 / 11.45 | 0.866 |
| Rooms | 0 | icon: Previous room: Thunder | 10.28 / 10.2 | 0.802 |
| Rooms | 0 | icon: Next room: Wind | 11.48 / 11.23 | 0.855 |
| Audio guide | 0 | icon: Play the audio guide | 11.5 / 11.39 | 0.856 |
| window | 580 | painter’s home, in a Paris rebuilt with wide streets | 12.09 / 11.47 | 0.882 |
| window | 580 | and uniform stone façades. A green lamppost splits | 11.83 / 11.47 | 0.87 |
| window | 580 | the canvas in two; the couple on the right walk | 11.84 / 11.47 | 0.871 |
| window | 580 | straight toward us, looking at something beyond | 11.81 / 11.47 | 0.87 |
| window | 580 | the frame. | 11.56 / 11.27 | 0.859 |
| window | 580 | Nearly life-size, it is Caillebotte’s largest painting. He | 11.61 / 11.39 | 0.861 |
| window | 580 | showed it at the third Impressionist exhibition in 1877, | 11.6 / 11.47 | 0.861 |
| window | 580 | the year he made it. | 11.7 / 11.48 | 0.865 |
| window | 580 | Weather | 10.22 / 10.13 | 0.799 |
| window | 580 | Light rain, overcast | 10.05 / 9.96 | 0.791 |
| window | 580 | Artist | 9.59 / 9.5 | 0.77 |
| window | 580 | Gustave Caillebotte ( French, 1848–1894 ) | 10.15 / 9.58 | 0.796 |
| window | 580 | Date | 9.14 / 9.08 | 0.749 |
| window | 580 | 1877 | 10.33 / 10.08 | 0.804 |
| window | 580 | Medium | 9.38 / 9.05 | 0.76 |
| window | 580 | Oil on canvas | 10.89 / 10.46 | 0.829 |
| window | 580 | Size | 9.29 / 9.05 | 0.756 |
| window | 580 | 212.2 × 276.2 cm | 11.04 / 10.77 | 0.836 |
| window | 580 | Collection | 10.92 / 10.84 | 0.831 |
| window | 580 | The Art Institute of Chicago | 11.04 / 10.95 | 0.836 |
| window | 580 | Credit | 9.7 / 9.29 | 0.775 |
| window | 580 | Charles H. and Mary F. S. Worcester | 11.02 / 10.94 | 0.835 |
| window | 580 | Number | 9.73 / 9.51 | 0.776 |
| window | 580 | 1964.336 | 10.81 / 10.72 | 0.826 |
| window | 580 | Photograph: The Art Institute of Chicago , open access, public | 11.83 / 10.89 | 0.87 |
| window | 580 | domain. | 10.76 / 10.63 | 0.824 |

### CSS tier at DPR 2, collapsed body · light · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.88 / 11.31 | 0.873 |
| window | 0 | Room 6 of 8 | 12.18 / 11.87 | 0.886 |
| window | 0 | Wind (large) | 11.64 / 11.12 | 0.862 |
| window | 0 | Wheat Field with Cypresses (large) | 11.9 / 11.85 | 0.873 |
| window | 0 | Vincent van Gogh | 11.87 / 11.67 | 0.872 |
| window | 0 | Dutch, 1853–1890 · 1889 | 11.65 / 11.62 | 0.862 |
| window | 0 | The whole work. The outline marks the part around you. | 11.34 / 11.22 | 0.849 |
| window | 0 | Everything in this field is moving the same way. The | 11.4 / 11.26 | 0.852 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 11.31 / 10.79 | 0.848 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 10.99 / 10.46 | 0.833 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 10.62 / 10.43 | 0.817 |
| window | 0 | the paint on so heavily that the brushstrokes | 10.63 / 10.54 | 0.817 |
| window | 0 | themselves take the shape of the wind. | 10.74 / 10.55 | 0.822 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 10.71 / 10.38 | 0.821 |
| Rooms | 0 | 6 | 11.02 / 11 | 0.834 |
| Rooms | 0 | / 8 | 11.04 / 11 | 0.835 |
| Audio guide | 0 | Audio guide | 10.89 / 10.55 | 0.828 |
| Audio guide | 0 | About 0:51 | 10.67 / 10.54 | 0.819 |
| Rooms | 0 | icon: Previous room: Rain | 10.9 / 10.84 | 0.828 |
| Rooms | 0 | icon: Next room: Gale | 11.1 / 10.99 | 0.837 |
| Audio guide | 0 | icon: Play the audio guide | 10.64 / 10.58 | 0.818 |
| window | 580 | He painted it in late June or early July 1889 at Saint-Rémy | 12.19 / 11.18 | 0.886 |
| window | 580 | Saint-Rémy in Provence, where he was a patient at the | 12.12 / 11.24 | 0.883 |
| window | 580 | asylum of Saint-Paul-de-Mausole, working outdoors | 12.01 / 11.65 | 0.878 |
| window | 580 | in front of the motif. | 12.01 / 11.89 | 0.878 |
| window | 580 | He counted it among his best summer canvases, and | 11.76 / 11.65 | 0.867 |
| window | 580 | that September made two studio versions of it: one | 11.64 / 11.52 | 0.862 |
| window | 580 | now in the National Gallery, London, the other a | 11.52 / 11.36 | 0.857 |
| window | 580 | smaller copy for his mother and sister. | 11.42 / 11.31 | 0.852 |
| window | 580 | Weather | 10.4 / 10.34 | 0.807 |
| window | 580 | Summer wind, fast cloud | 10.27 / 10.22 | 0.801 |
| window | 580 | Artist | 10.38 / 10.31 | 0.806 |
| window | 580 | Vincent van Gogh ( Dutch, 1853–1890 ) | 10.27 / 10.18 | 0.801 |
| window | 580 | Date | 10.22 / 10.2 | 0.799 |
| window | 580 | 1889 | 10.19 / 10.19 | 0.798 |
| window | 580 | Medium | 10.29 / 10.27 | 0.802 |
| window | 580 | Oil on canvas | 10.26 / 10.23 | 0.801 |
| window | 580 | Size | 10.38 / 10.38 | 0.806 |
| window | 580 | 73.2 × 93.4 cm | 10.4 / 10.36 | 0.807 |
| window | 580 | Collection | 10.38 / 10.37 | 0.806 |
| window | 580 | The Metropolitan Museum of Art, New York | 9.78 / 9.56 | 0.779 |
| window | 580 | Credit | 10.34 / 10.32 | 0.805 |
| window | 580 | Purchase, The Annenberg Foundation Gift, | 9.57 / 9.45 | 0.769 |
| window | 580 | 1993 | 9.62 / 9.52 | 0.771 |
| window | 580 | Number | 10.29 / 10.11 | 0.802 |
| window | 580 | 1993.132 | 9.54 / 9.52 | 0.768 |
| window | 580 | Photograph: The Metropolitan Museum of Art, New York , open | 10.58 / 10.32 | 0.815 |
| window | 580 | access, public domain. | 10.68 / 10.3 | 0.82 |

### CSS tier at DPR 2, collapsed body · light · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.81 / 11.55 | 0.87 |
| window | 0 | Room 7 of 8 | 12.63 / 11.81 | 0.904 |
| window | 0 | Gale (large) | 11.82 / 11.39 | 0.87 |
| window | 0 | Northeaster (large) | 12.17 / 11.6 | 0.885 |
| window | 0 | Winslow Homer | 12.31 / 11.84 | 0.891 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 12.71 / 12.16 | 0.908 |
| window | 0 | The whole work. The outline marks the part around you. | 11.71 / 11.42 | 0.865 |
| window | 0 | A northeaster is a winter storm that drives in off the | 11.71 / 11.42 | 0.865 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 11.6 / 11.33 | 0.86 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 11.42 / 11.06 | 0.852 |
| window | 0 | lived and painted for the last decades of his life. | 10.72 / 10.38 | 0.822 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 9.95 / 9.79 | 0.787 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 9.95 / 9.77 | 0.787 |
| window | 0 | lower left. By 1900 he had painted them out and | 9.89 / 9.79 | 0.784 |
| Rooms | 0 | 7 | 9.83 / 9.77 | 0.781 |
| Rooms | 0 | / 8 | 9.92 / 9.84 | 0.785 |
| Audio guide | 0 | Audio guide | 9.57 / 9.38 | 0.769 |
| Audio guide | 0 | About 0:50 | 9.73 / 9.55 | 0.776 |
| Rooms | 0 | icon: Previous room: Wind | 9.64 / 9.49 | 0.772 |
| Rooms | 0 | icon: Next room: Fog | 9.88 / 9.7 | 0.783 |
| Audio guide | 0 | icon: Play the audio guide | 10.16 / 10.02 | 0.796 |
| window | 508 | When he first exhibited this canvas in 1895, two men | 13.25 / 11.81 | 0.931 |
| window | 508 | in foul-weather gear crouched on the rocks at the | 13.23 / 11.71 | 0.93 |
| window | 508 | lower left. By 1900 he had painted them out and | 13.05 / 11.72 | 0.922 |
| window | 508 | raised a much larger column of spray. What is left is | 12.93 / 11.93 | 0.917 |
| window | 508 | rock, water and air: the dark ledge, the green body of | 12.81 / 12.13 | 0.912 |
| window | 508 | the wave and the white burst where they meet. | 12.72 / 12.23 | 0.908 |
| window | 508 | A critic in 1901 praised it for “great natural spaces | 12.81 / 12.2 | 0.912 |
| window | 508 | unmarked by the presence of puny man.” | 12.79 / 12 | 0.912 |
| window | 508 | Weather | 10.96 / 10.78 | 0.832 |
| window | 508 | Winter northeaster off the Atlantic | 11.23 / 11.07 | 0.844 |
| window | 508 | Artist | 10.99 / 10.88 | 0.833 |
| window | 508 | Winslow Homer ( American, 1836–1910 ) | 10.83 / 10.61 | 0.827 |
| window | 508 | Date | 10.92 / 10.78 | 0.83 |
| window | 508 | 1895; reworked by 1901 | 10.6 / 10.34 | 0.816 |
| window | 508 | Medium | 10.75 / 10.51 | 0.823 |
| window | 508 | Oil on canvas | 10.43 / 10.42 | 0.809 |
| window | 508 | Size | 10.25 / 10.12 | 0.8 |
| window | 508 | 87.6 × 127 cm | 10.36 / 10.32 | 0.805 |
| window | 508 | Collection | 9.94 / 9.8 | 0.786 |
| window | 508 | The Metropolitan Museum of Art, New York | 10.51 / 9.86 | 0.812 |
| window | 508 | Credit | 9.1 / 9.04 | 0.747 |
| window | 508 | Gift of George A. Hearn, 1910 | 9.25 / 9.04 | 0.754 |
| window | 508 | Number | 8.86 / 8.86 | 0.735 |
| window | 508 | 10.64.5 | 8.88 / 8.88 | 0.736 |
| window | 508 | Photograph: The Metropolitan Museum of Art, New York , open | 9.86 / 9.79 | 0.782 |
| window | 508 | access, public domain. | 9.79 / 9.78 | 0.779 |

### CSS tier at DPR 2, collapsed body · light · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 11.08 / 11.03 | 0.838 |
| window | 0 | Room 8 of 8 | 11.19 / 11.14 | 0.843 |
| window | 0 | Fog (large) | 11.1 / 11.04 | 0.839 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 11.15 / 11.02 | 0.841 |
| window | 0 | Claude Monet | 10.88 / 10.82 | 0.829 |
| window | 0 | French, 1840–1926 · 1900 | 10.98 / 10.74 | 0.833 |
| window | 0 | The whole work. The outline marks the part around you. | 10.24 / 10.19 | 0.8 |
| window | 0 | Without the fog, Monet once remarked, London | 10.19 / 10.11 | 0.798 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 10.19 / 10.12 | 0.798 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 10.21 / 10.09 | 0.798 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 10.24 / 10.05 | 0.8 |
| window | 0 | he came to paint it. | 10.81 / 10.69 | 0.826 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 10.21 / 10.04 | 0.799 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 10.26 / 10.06 | 0.801 |
| Rooms | 0 | 8 | 10.3 / 10.21 | 0.803 |
| Rooms | 0 | / 8 | 10.38 / 10.34 | 0.806 |
| Audio guide | 0 | Audio guide | 10.06 / 9.98 | 0.791 |
| Audio guide | 0 | About 0:50 | 10.1 / 10.06 | 0.793 |
| Rooms | 0 | icon: Previous room: Gale | 10.55 / 10.46 | 0.814 |
| Audio guide | 0 | icon: Play the audio guide | 10.03 / 9.99 | 0.79 |
| window | 534 | He painted Waterloo Bridge in the mornings from his | 11.11 / 11.1 | 0.839 |
| window | 534 | fifth-floor window at the Savoy Hotel, moving on to | 11.12 / 11.1 | 0.839 |
| window | 534 | Charing Cross Bridge later in the day. Here the bridge | 11.13 / 11.04 | 0.84 |
| window | 534 | is a dark band of arches, and the city behind it is only | 11.17 / 10.98 | 0.842 |
| window | 534 | chimneys and towers in the haze. | 11.13 / 10.84 | 0.84 |
| window | 534 | He finished the London pictures in his studio at | 11.09 / 10.74 | 0.838 |
| window | 534 | Giverny, and would not release any of them until he | 10.92 / 10.78 | 0.83 |
| window | 534 | was satisfied with the series as a whole. | 10.83 / 10.75 | 0.826 |
| window | 534 | Weather | 9.79 / 9.79 | 0.779 |
| window | 534 | Winter fog and coal smoke | 9.8 / 9.72 | 0.78 |
| window | 534 | Artist | 9.61 / 9.59 | 0.771 |
| window | 534 | Claude Monet ( French, 1840–1926 ) | 9.53 / 9.43 | 0.767 |
| window | 534 | Date | 9.31 / 9.31 | 0.756 |
| window | 534 | 1900 | 9.42 / 9.36 | 0.762 |
| window | 534 | Medium | 9.22 / 9.15 | 0.752 |
| window | 534 | Oil on canvas | 9.33 / 9.32 | 0.758 |
| window | 534 | Size | 9.19 / 9.18 | 0.751 |
| window | 534 | 65.4 × 92.6 cm | 9.3 / 9.19 | 0.756 |
| window | 534 | Collection | 9.47 / 9.32 | 0.764 |
| window | 534 | The Art Institute of Chicago | 9.19 / 9.14 | 0.751 |
| window | 534 | Credit | 9.73 / 9.65 | 0.776 |
| window | 534 | Gift of Mrs. Mortimer B. Harris | 9.26 / 9.12 | 0.754 |
| window | 534 | Number | 9.76 / 9.66 | 0.778 |
| window | 534 | 1984.1173 | 9.75 / 9.65 | 0.778 |
| window | 534 | Photograph: The Art Institute of Chicago , open access, public | 10.27 / 10.09 | 0.801 |
| window | 534 | domain. | 10.81 / 10.73 | 0.826 |

### CSS tier at DPR 2, collapsed body · dark · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.54 / 6.51 | 0.286 |
| window | 0 | Room 1 of 8 | 6.44 / 6.35 | 0.29 |
| window | 0 | Frost (large) | 6.71 / 6.61 | 0.278 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 6.69 / 6.62 | 0.279 |
| window | 0 | Hendrick Avercamp | 6.71 / 6.69 | 0.278 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 6.7 / 6.69 | 0.279 |
| window | 0 | The whole work. The outline marks the part around you. | 6.81 / 6.8 | 0.274 |
| window | 0 | Avercamp made his name painting winter, in the years | 6.81 / 6.78 | 0.274 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 6.79 / 6.78 | 0.275 |
| window | 0 | Countries. Here a whole village has moved onto the | 6.79 / 6.79 | 0.275 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 6.81 / 6.79 | 0.274 |
| window | 0 | sledge on the right, a church on the left. | 6.87 / 6.81 | 0.271 |
| window | 0 | Look at how the air is built. The figures in front are | 6.88 / 6.81 | 0.271 |
| window | 0 | sharp and full of colour; a few hundred metres back | 6.88 / 6.87 | 0.271 |
| Rooms | 0 | 1 | 5.6 / 5.57 | 0.329 |
| Rooms | 0 | / 8 | 5.6 / 5.53 | 0.329 |
| Audio guide | 0 | Audio guide | 5.52 / 5.39 | 0.333 |
| Audio guide | 0 | About 0:51 | 5.52 / 5.32 | 0.333 |
| Rooms | 0 | icon: Next room: Cloud | 5.52 / 5.39 | 0.333 |
| Audio guide | 0 | icon: Play the audio guide | 5.53 / 5.52 | 0.333 |
| window | 554 | Look at how the air is built. The figures in front are | 6.62 / 6.61 | 0.282 |
| window | 554 | sharp and full of colour; a few hundred metres back | 6.69 / 6.61 | 0.279 |
| window | 554 | they thin into grey-white haze, and the far bank all | 6.69 / 6.62 | 0.279 |
| window | 554 | but dissolves. That haze is the weather: cold, damp | 6.69 / 6.62 | 0.279 |
| window | 554 | air thick enough to carry the light. | 6.69 / 6.69 | 0.279 |
| window | 554 | Avercamp signed the picture on the wall of a wooden | 6.69 / 6.69 | 0.279 |
| window | 554 | shed on the right, among the scratched graffiti, | 6.71 / 6.69 | 0.278 |
| window | 554 | where it is easy to miss. | 6.71 / 6.69 | 0.278 |
| window | 554 | Weather | 8.36 / 8.33 | 0.215 |
| window | 554 | Hard frost, haze over the ice | 8.33 / 8.33 | 0.216 |
| window | 554 | Artist | 8.38 / 8.36 | 0.214 |
| window | 554 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 8.33 / 8.33 | 0.216 |
| window | 554 | Date | 8.38 / 8.36 | 0.214 |
| window | 554 | c. 1608 | 8.37 / 8.34 | 0.215 |
| window | 554 | Medium | 8.44 / 8.37 | 0.212 |
| window | 554 | Oil on panel | 8.34 / 8.33 | 0.215 |
| window | 554 | Size | 8.34 / 8.34 | 0.215 |
| window | 554 | 77.3 × 131.9 cm | 8.42 / 8.34 | 0.213 |
| window | 554 | Collection | 8.33 / 8.33 | 0.216 |
| window | 554 | Rijksmuseum, Amsterdam | 8.35 / 8.34 | 0.215 |
| window | 554 | Credit | 8.37 / 8.34 | 0.215 |
| window | 554 | Purchased with the support of the | 8.35 / 8.34 | 0.215 |
| window | 554 | Vereniging Rembrandt | 8.35 / 8.34 | 0.215 |
| window | 554 | Number | 8.44 / 8.43 | 0.212 |
| window | 554 | SK-A-1718 | 8.35 / 8.34 | 0.215 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.88 / 6.81 | 0.271 |
| window | 554 | domain. | 6.88 / 6.81 | 0.271 |

### CSS tier at DPR 2, collapsed body · dark · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.99 / 6.92 | 0.267 |
| window | 0 | Room 2 of 8 | 6.99 / 6.91 | 0.267 |
| window | 0 | Cloud (large) | 7.11 / 7.01 | 0.262 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 7.01 / 6.91 | 0.266 |
| window | 0 | Jacob van Ruisdael | 7.02 / 6.99 | 0.266 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 7.01 / 6.99 | 0.266 |
| window | 0 | The whole work. The outline marks the part around you. | 6.99 / 6.91 | 0.267 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 6.91 / 6.91 | 0.27 |
| window | 0 | more than half the canvas, and he paints it as a | 6.91 / 6.91 | 0.27 |
| window | 0 | structure: banks of cumulus heaped over one | 6.92 / 6.91 | 0.269 |
| window | 0 | another, grey underneath, lit at their edges by a sun | 6.91 / 6.91 | 0.27 |
| window | 0 | we cannot see. | 6.91 / 6.83 | 0.27 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 6.89 / 6.82 | 0.271 |
| window | 0 | A sailing boat is out on the water, the towers of | 6.89 / 6.82 | 0.271 |
| Rooms | 0 | 2 | 6.81 / 6.81 | 0.274 |
| Rooms | 0 | / 8 | 6.8 / 6.8 | 0.275 |
| Audio guide | 0 | Audio guide | 6.92 / 6.89 | 0.269 |
| Audio guide | 0 | About 0:49 | 6.97 / 6.92 | 0.267 |
| Rooms | 0 | icon: Previous room: Frost | 6.81 / 6.71 | 0.274 |
| Rooms | 0 | icon: Next room: Clearing | 6.81 / 6.71 | 0.274 |
| Audio guide | 0 | icon: Play the audio guide | 6.92 / 6.89 | 0.269 |
| window | 554 | Below, the mill stands near the bank of the river Lek. | 7.01 / 6.99 | 0.266 |
| window | 554 | A sailing boat is out on the water, the towers of | 7.01 / 6.99 | 0.266 |
| window | 554 | Duurstede castle and the church rise in the distance, | 7.01 / 6.98 | 0.266 |
| window | 554 | and a few women walk along the bank, very small | 7.08 / 6.91 | 0.263 |
| window | 554 | against the mill. | 7.08 / 7.01 | 0.263 |
| window | 554 | Dutch painters of the seventeenth century made the | 6.99 / 6.89 | 0.267 |
| window | 554 | sky a subject in its own right. Few made it carry as | 6.92 / 6.89 | 0.269 |
| window | 554 | much of a picture as this. | 7.01 / 6.91 | 0.266 |
| window | 554 | Weather | 8.47 / 8.37 | 0.211 |
| window | 554 | Heaped cumulus, sun breaking through | 8.56 / 8.44 | 0.208 |
| window | 554 | Artist | 8.44 / 8.33 | 0.212 |
| window | 554 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 8.56 / 8.44 | 0.208 |
| window | 554 | Date | 8.44 / 8.36 | 0.212 |
| window | 554 | c. 1668–70 | 8.56 / 8.56 | 0.208 |
| window | 554 | Medium | 8.44 / 8.33 | 0.212 |
| window | 554 | Oil on canvas | 8.55 / 8.47 | 0.208 |
| window | 554 | Size | 8.44 / 8.33 | 0.212 |
| window | 554 | 83 × 101 cm | 8.47 / 8.47 | 0.211 |
| window | 554 | Collection | 8.47 / 8.37 | 0.211 |
| window | 554 | Rijksmuseum, Amsterdam | 8.55 / 8.47 | 0.208 |
| window | 554 | Credit | 8.44 / 8.37 | 0.212 |
| window | 554 | On loan from the City of Amsterdam (A. van | 8.47 / 8.47 | 0.211 |
| window | 554 | der Hoop Bequest) | 8.47 / 8.47 | 0.211 |
| window | 554 | Number | 8.44 / 8.36 | 0.212 |
| window | 554 | SK-C-211 | 8.44 / 8.44 | 0.212 |
| window | 554 | Photograph: Rijksmuseum, Amsterdam , open access, public | 6.89 / 6.83 | 0.271 |
| window | 554 | domain. | 6.83 / 6.73 | 0.273 |

### CSS tier at DPR 2, collapsed body · dark · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.48 / 7.47 | 0.247 |
| window | 0 | Room 3 of 8 | 7.3 / 7.2 | 0.254 |
| window | 0 | Clearing (large) | 7.5 / 7.49 | 0.246 |
| window | 0 | View from Mount Holyoke, (large) | 7.49 / 7.4 | 0.247 |
| window | 0 | Northampton, Massachusetts, (large) | 7.49 / 7.37 | 0.247 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 7.47 / 7.3 | 0.248 |
| window | 0 | Thomas Cole | 7.51 / 7.49 | 0.246 |
| window | 0 | American, born England, 1801–1848 · 1836 | 7.47 / 7.37 | 0.248 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.48 | 0.247 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 7.59 / 7.51 | 0.243 |
| window | 0 | valley. On the left it still hangs over wild, broken | 7.59 / 7.51 | 0.243 |
| window | 0 | trees, and rain falls in grey veils across the hills. On | 7.59 / 7.51 | 0.243 |
| window | 0 | the right the air has cleared over cleared land: fields, | 7.59 / 7.49 | 0.243 |
| window | 0 | farms and the river’s great loop. | 7.59 / 7.49 | 0.243 |
| Rooms | 0 | 3 | 7.9 / 7.83 | 0.231 |
| Rooms | 0 | / 8 | 7.83 / 7.71 | 0.234 |
| Audio guide | 0 | Audio guide | 7.52 / 7.26 | 0.246 |
| Audio guide | 0 | About 0:50 | 7.52 / 7.35 | 0.246 |
| Rooms | 0 | icon: Previous room: Cloud | 7.93 / 7.93 | 0.231 |
| Rooms | 0 | icon: Next room: Thunder | 7.93 / 7.9 | 0.231 |
| Audio guide | 0 | icon: Play the audio guide | 7.52 / 7.52 | 0.246 |
| window | 610 | Cole divided the picture along a diagonal, and the | 7.47 / 7.37 | 0.248 |
| window | 610 | weather does the dividing. He painted it for the 1836 | 7.49 / 7.28 | 0.247 |
| window | 610 | annual exhibition of the National Academy of Design, | 7.49 / 7.28 | 0.247 |
| window | 610 | calling the view from Mount Holyoke “about the finest | 7.49 / 7.28 | 0.247 |
| window | 610 | scene I have in my sketchbook.” | 7.5 / 7.47 | 0.246 |
| window | 610 | Look for the painter himself near the bottom of the | 7.47 / 7.37 | 0.248 |
| window | 610 | canvas: a small figure at an easel among the rocks, | 7.47 / 7.37 | 0.248 |
| window | 610 | turning back toward us. | 7.5 / 7.47 | 0.246 |
| window | 610 | Weather | 9 / 8.99 | 0.192 |
| window | 610 | Thunderstorm passing, sun on the valley | 8.91 / 8.87 | 0.196 |
| window | 610 | Artist | 8.91 / 8.91 | 0.195 |
| window | 610 | Thomas Cole ( American, born England, | 8.91 / 8.87 | 0.196 |
| window | 610 | 1801–1848 ) | 9 / 8.99 | 0.192 |
| window | 610 | Date | 8.88 / 8.88 | 0.196 |
| window | 610 | 1836 | 9 / 9 | 0.192 |
| window | 610 | Medium | 8.99 / 8.91 | 0.193 |
| window | 610 | Oil on canvas | 9 / 9 | 0.192 |
| window | 610 | Size | 9 / 9 | 0.192 |
| window | 610 | 130.8 × 193 cm | 9.1 / 9 | 0.189 |
| window | 610 | Collection | 9.11 / 9.1 | 0.189 |
| window | 610 | The Metropolitan Museum of Art, New York | 9.13 / 9.03 | 0.188 |
| window | 610 | Credit | 9.03 / 9.03 | 0.191 |
| window | 610 | Gift of Mrs. Russell Sage, 1908 | 9.13 / 9 | 0.188 |
| window | 610 | Number | 9.1 / 9.03 | 0.189 |
| window | 610 | 08.228 | 9.13 / 9.13 | 0.188 |
| window | 610 | Photograph: The Metropolitan Museum of Art, New York , open | 7.61 / 7.47 | 0.242 |
| window | 610 | access, public domain. | 7.61 / 7.61 | 0.242 |

### CSS tier at DPR 2, collapsed body · dark · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.67 / 7.67 | 0.24 |
| window | 0 | Room 4 of 8 | 7.67 / 7.67 | 0.24 |
| window | 0 | Thunder (large) | 7.67 / 7.67 | 0.24 |
| window | 0 | Approaching Thunder Storm (large) | 7.67 / 7.6 | 0.24 |
| window | 0 | Martin Johnson Heade | 7.57 / 7.57 | 0.244 |
| window | 0 | American, 1819–1904 · 1859 | 7.48 / 7.45 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.57 / 7.48 | 0.244 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 7.45 / 7.36 | 0.248 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 7.45 / 7.36 | 0.248 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 7.65 / 7.57 | 0.241 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 7.77 / 7.7 | 0.236 |
| window | 0 | rower pulls for shore; a white sail stands out against | 7.8 / 7.77 | 0.235 |
| window | 0 | the dark. | 7.8 / 7.8 | 0.235 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 7.68 / 7.38 | 0.239 |
| Rooms | 0 | 4 | 6.27 / 6.22 | 0.297 |
| Rooms | 0 | / 8 | 6.27 / 6.22 | 0.297 |
| Audio guide | 0 | Audio guide | 6.39 / 6.3 | 0.292 |
| Audio guide | 0 | About 0:53 | 6.39 / 6.3 | 0.292 |
| Rooms | 0 | icon: Previous room: Clearing | 6.22 / 6.13 | 0.3 |
| Rooms | 0 | icon: Next room: Rain | 6.18 / 5.99 | 0.301 |
| Audio guide | 0 | icon: Play the audio guide | 6.39 / 6.36 | 0.292 |
| window | 618 | holds: not the storm itself but the minute before it. | 7.67 / 7.67 | 0.24 |
| window | 618 | Painted two years before the Civil War, it has often | 7.67 / 7.67 | 0.24 |
| window | 618 | been read as a picture of a country waiting for | 7.67 / 7.6 | 0.24 |
| window | 618 | something to break. Heade based it on a storm he | 7.57 / 7.57 | 0.244 |
| window | 618 | had watched from Prudence Island, in the bay, | 7.55 / 7.46 | 0.245 |
| window | 618 | around 1858. | 7.57 / 7.47 | 0.244 |
| window | 618 | Weather | 8.96 / 8.96 | 0.194 |
| window | 618 | Thunderstorm approaching over still water | 8.88 / 8.86 | 0.196 |
| window | 618 | Artist | 8.96 / 8.96 | 0.194 |
| window | 618 | Martin Johnson Heade ( American, 1819–1904 | 8.88 / 8.88 | 0.196 |
| window | 618 | 1819–1904 ) | 8.96 / 8.96 | 0.194 |
| window | 618 | Date | 8.96 / 8.88 | 0.194 |
| window | 618 | 1859 | 8.96 / 8.96 | 0.194 |
| window | 618 | Medium | 8.99 / 8.99 | 0.193 |
| window | 618 | Oil on canvas | 9.09 / 8.99 | 0.189 |
| window | 618 | Size | 8.99 / 8.99 | 0.193 |
| window | 618 | 71.1 × 111.8 cm | 8.99 / 8.99 | 0.193 |
| window | 618 | Collection | 8.88 / 8.88 | 0.196 |
| window | 618 | The Metropolitan Museum of Art, New York | 8.96 / 8.88 | 0.194 |
| window | 618 | Credit | 9.11 / 9.09 | 0.189 |
| window | 618 | Gift of Erving Wolf Foundation and Mr. and | 9.13 / 9.11 | 0.188 |
| window | 618 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9.2 / 9.13 | 0.185 |
| window | 618 | 1975 | 9.23 / 9.23 | 0.184 |
| window | 618 | Number | 9.23 / 9.23 | 0.184 |
| window | 618 | 1975.160 | 9.21 / 9.13 | 0.185 |
| window | 618 | Photograph: The Metropolitan Museum of Art, New York , open | 7.57 / 7.12 | 0.244 |
| window | 620 | holds: not the storm itself but the minute before it. | 7.67 / 7.67 | 0.24 |
| window | 620 | Painted two years before the Civil War, it has often | 7.67 / 7.67 | 0.24 |
| window | 620 | been read as a picture of a country waiting for | 7.67 / 7.6 | 0.24 |
| window | 620 | something to break. Heade based it on a storm he | 7.6 / 7.57 | 0.243 |
| window | 620 | had watched from Prudence Island, in the bay, | 7.57 / 7.46 | 0.244 |
| window | 620 | around 1858. | 7.57 / 7.48 | 0.244 |
| window | 620 | Weather | 8.96 / 8.96 | 0.194 |
| window | 620 | Thunderstorm approaching over still water | 8.88 / 8.86 | 0.196 |
| window | 620 | Artist | 8.96 / 8.96 | 0.194 |
| window | 620 | Martin Johnson Heade ( American, 1819–1904 | 8.88 / 8.88 | 0.196 |
| window | 620 | 1819–1904 ) | 8.96 / 8.96 | 0.194 |
| window | 620 | Date | 8.96 / 8.88 | 0.194 |
| window | 620 | 1859 | 8.96 / 8.96 | 0.194 |
| window | 620 | Medium | 8.99 / 8.99 | 0.193 |
| window | 620 | Oil on canvas | 9.07 / 8.99 | 0.19 |
| window | 620 | Size | 8.99 / 8.99 | 0.193 |
| window | 620 | 71.1 × 111.8 cm | 8.99 / 8.99 | 0.193 |
| window | 620 | Collection | 8.88 / 8.88 | 0.196 |
| window | 620 | The Metropolitan Museum of Art, New York | 8.96 / 8.88 | 0.194 |
| window | 620 | Credit | 9.11 / 9.09 | 0.189 |
| window | 620 | Gift of Erving Wolf Foundation and Mr. and | 9.13 / 9.11 | 0.188 |
| window | 620 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9.2 / 9.12 | 0.185 |
| window | 620 | 1975 | 9.23 / 9.23 | 0.184 |
| window | 620 | Number | 9.23 / 9.23 | 0.184 |
| window | 620 | 1975.160 | 9.21 / 9.13 | 0.185 |
| window | 620 | Photograph: The Metropolitan Museum of Art, New York , open | 7.57 / 7.17 | 0.244 |
| window | 620 | access, public domain. | 7.55 / 7.31 | 0.245 |

### CSS tier at DPR 2, collapsed body · dark · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.53 / 6.5 | 0.286 |
| window | 0 | Room 5 of 8 | 6.63 / 6.61 | 0.282 |
| window | 0 | Rain (large) | 6.71 / 6.62 | 0.278 |
| window | 0 | Paris Street; Rainy Day (large) | 6.71 / 6.69 | 0.278 |
| window | 0 | Gustave Caillebotte | 6.71 / 6.71 | 0.278 |
| window | 0 | French, 1848–1894 · 1877 | 6.79 / 6.71 | 0.275 |
| window | 0 | The whole work. The outline marks the part around you. | 6.79 / 6.73 | 0.275 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 6.73 / 6.71 | 0.278 |
| window | 0 | paints the rain through what it does: the paving | 6.71 / 6.71 | 0.278 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 6.71 / 6.71 | 0.278 |
| window | 0 | everyone carries an umbrella, the newly invented | 6.71 / 6.71 | 0.278 |
| window | 0 | retractable kind. | 6.79 / 6.73 | 0.275 |
| window | 0 | The place is a busy intersection a short walk from the | 6.73 / 6.71 | 0.278 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 6.73 / 6.73 | 0.278 |
| Rooms | 0 | 5 | 6.43 / 6.43 | 0.29 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 0.29 |
| Audio guide | 0 | Audio guide | 6 / 5.97 | 0.31 |
| Audio guide | 0 | About 0:46 | 6.17 / 6 | 0.302 |
| Rooms | 0 | icon: Previous room: Thunder | 6.43 / 6.34 | 0.29 |
| Rooms | 0 | icon: Next room: Wind | 6.34 / 6.34 | 0.294 |
| Audio guide | 0 | icon: Play the audio guide | 6.17 / 6 | 0.302 |
| window | 580 | painter’s home, in a Paris rebuilt with wide streets | 6.71 / 6.62 | 0.278 |
| window | 580 | and uniform stone façades. A green lamppost splits | 6.71 / 6.69 | 0.278 |
| window | 580 | the canvas in two; the couple on the right walk | 6.71 / 6.69 | 0.278 |
| window | 580 | straight toward us, looking at something beyond | 6.73 / 6.69 | 0.278 |
| window | 580 | the frame. | 6.71 / 6.71 | 0.278 |
| window | 580 | Nearly life-size, it is Caillebotte’s largest painting. He | 6.79 / 6.71 | 0.275 |
| window | 580 | showed it at the third Impressionist exhibition in 1877, | 6.79 / 6.71 | 0.275 |
| window | 580 | the year he made it. | 6.73 / 6.71 | 0.278 |
| window | 580 | Weather | 8.36 / 8.33 | 0.215 |
| window | 580 | Light rain, overcast | 8.36 / 8.36 | 0.215 |
| window | 580 | Artist | 8.44 / 8.36 | 0.212 |
| window | 580 | Gustave Caillebotte ( French, 1848–1894 ) | 8.36 / 8.36 | 0.215 |
| window | 580 | Date | 8.54 / 8.46 | 0.208 |
| window | 580 | 1877 | 8.33 / 8.33 | 0.216 |
| window | 580 | Medium | 8.46 / 8.44 | 0.211 |
| window | 580 | Oil on canvas | 8.33 / 8.33 | 0.216 |
| window | 580 | Size | 8.46 / 8.44 | 0.211 |
| window | 580 | 212.2 × 276.2 cm | 8.33 / 8.33 | 0.216 |
| window | 580 | Collection | 8.33 / 8.33 | 0.216 |
| window | 580 | The Art Institute of Chicago | 8.33 / 8.33 | 0.216 |
| window | 580 | Credit | 8.44 / 8.33 | 0.212 |
| window | 580 | Charles H. and Mary F. S. Worcester | 8.33 / 8.33 | 0.216 |
| window | 580 | Number | 8.36 / 8.33 | 0.215 |
| window | 580 | 1964.336 | 8.33 / 8.33 | 0.216 |
| window | 580 | Photograph: The Art Institute of Chicago , open access, public | 6.73 / 6.71 | 0.278 |
| window | 580 | domain. | 6.79 / 6.73 | 0.275 |

### CSS tier at DPR 2, collapsed body · dark · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.61 / 6.53 | 0.282 |
| window | 0 | Room 6 of 8 | 6.59 / 6.53 | 0.283 |
| window | 0 | Wind (large) | 6.73 / 6.67 | 0.278 |
| window | 0 | Wheat Field with Cypresses (large) | 6.71 / 6.71 | 0.278 |
| window | 0 | Vincent van Gogh | 6.73 / 6.61 | 0.278 |
| window | 0 | Dutch, 1853–1890 · 1889 | 6.73 / 6.7 | 0.278 |
| window | 0 | The whole work. The outline marks the part around you. | 6.74 / 6.73 | 0.277 |
| window | 0 | Everything in this field is moving the same way. The | 6.74 / 6.73 | 0.277 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 6.74 / 6.73 | 0.277 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 6.82 / 6.73 | 0.274 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 6.83 / 6.73 | 0.273 |
| window | 0 | the paint on so heavily that the brushstrokes | 6.83 / 6.73 | 0.273 |
| window | 0 | themselves take the shape of the wind. | 6.83 / 6.73 | 0.273 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 6.83 / 6.81 | 0.273 |
| Rooms | 0 | 6 | 6.43 / 6.37 | 0.29 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 0.29 |
| Audio guide | 0 | Audio guide | 6.43 / 6.36 | 0.29 |
| Audio guide | 0 | About 0:51 | 6.39 / 6.36 | 0.292 |
| Rooms | 0 | icon: Previous room: Rain | 6.37 / 6.34 | 0.293 |
| Rooms | 0 | icon: Next room: Gale | 6.36 / 6.27 | 0.294 |
| Audio guide | 0 | icon: Play the audio guide | 6.43 / 6.36 | 0.29 |
| window | 580 | He painted it in late June or early July 1889 at Saint-Rémy | 6.71 / 6.63 | 0.278 |
| window | 580 | Saint-Rémy in Provence, where he was a patient at the | 6.71 / 6.71 | 0.278 |
| window | 580 | asylum of Saint-Paul-de-Mausole, working outdoors | 6.71 / 6.71 | 0.278 |
| window | 580 | in front of the motif. | 6.71 / 6.63 | 0.278 |
| window | 580 | He counted it among his best summer canvases, and | 6.73 / 6.7 | 0.278 |
| window | 580 | that September made two studio versions of it: one | 6.73 / 6.72 | 0.278 |
| window | 580 | now in the National Gallery, London, the other a | 6.73 / 6.73 | 0.278 |
| window | 580 | smaller copy for his mother and sister. | 6.73 / 6.73 | 0.278 |
| window | 580 | Weather | 8.36 / 8.25 | 0.215 |
| window | 580 | Summer wind, fast cloud | 8.36 / 8.36 | 0.215 |
| window | 580 | Artist | 8.33 / 8.25 | 0.216 |
| window | 580 | Vincent van Gogh ( Dutch, 1853–1890 ) | 8.36 / 8.33 | 0.215 |
| window | 580 | Date | 8.33 / 8.25 | 0.216 |
| window | 580 | 1889 | 8.36 / 8.36 | 0.215 |
| window | 580 | Medium | 8.33 / 8.25 | 0.216 |
| window | 580 | Oil on canvas | 8.36 / 8.36 | 0.215 |
| window | 580 | Size | 8.33 / 8.25 | 0.216 |
| window | 580 | 73.2 × 93.4 cm | 8.36 / 8.36 | 0.215 |
| window | 580 | Collection | 8.36 / 8.25 | 0.215 |
| window | 580 | The Metropolitan Museum of Art, New York | 8.36 / 8.33 | 0.215 |
| window | 580 | Credit | 8.33 / 8.25 | 0.216 |
| window | 580 | Purchase, The Annenberg Foundation Gift, | 8.37 / 8.37 | 0.215 |
| window | 580 | 1993 | 8.37 / 8.36 | 0.215 |
| window | 580 | Number | 8.33 / 8.25 | 0.216 |
| window | 580 | 1993.132 | 8.39 / 8.37 | 0.214 |
| window | 580 | Photograph: The Metropolitan Museum of Art, New York , open | 6.83 / 6.82 | 0.273 |
| window | 580 | access, public domain. | 6.82 / 6.74 | 0.274 |

### CSS tier at DPR 2, collapsed body · dark · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.72 / 6.7 | 0.278 |
| window | 0 | Room 7 of 8 | 6.72 / 6.7 | 0.278 |
| window | 0 | Gale (large) | 6.81 / 6.81 | 0.274 |
| window | 0 | Northeaster (large) | 6.81 / 6.81 | 0.274 |
| window | 0 | Winslow Homer | 6.81 / 6.79 | 0.274 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 6.79 / 6.73 | 0.275 |
| window | 0 | The whole work. The outline marks the part around you. | 6.82 / 6.81 | 0.274 |
| window | 0 | A northeaster is a winter storm that drives in off the | 6.82 / 6.79 | 0.274 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 6.89 / 6.73 | 0.271 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 6.89 / 6.79 | 0.271 |
| window | 0 | lived and painted for the last decades of his life. | 6.91 / 6.73 | 0.27 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 7.08 / 6.82 | 0.263 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 7.1 / 6.99 | 0.262 |
| window | 0 | lower left. By 1900 he had painted them out and | 7.1 / 7.08 | 0.262 |
| Rooms | 0 | 7 | 7.59 / 7.59 | 0.243 |
| Rooms | 0 | / 8 | 7.59 / 7.59 | 0.243 |
| Audio guide | 0 | Audio guide | 8.12 / 7.93 | 0.224 |
| Audio guide | 0 | About 0:50 | 7.9 / 7.9 | 0.231 |
| Rooms | 0 | icon: Previous room: Wind | 7.59 / 7.59 | 0.243 |
| Rooms | 0 | icon: Next room: Fog | 7.59 / 7.59 | 0.243 |
| Audio guide | 0 | icon: Play the audio guide | 7.83 / 7.83 | 0.234 |
| window | 508 | When he first exhibited this canvas in 1895, two men | 6.72 / 6.71 | 0.278 |
| window | 508 | in foul-weather gear crouched on the rocks at the | 6.73 / 6.72 | 0.278 |
| window | 508 | lower left. By 1900 he had painted them out and | 6.73 / 6.72 | 0.278 |
| window | 508 | raised a much larger column of spray. What is left is | 6.73 / 6.72 | 0.278 |
| window | 508 | rock, water and air: the dark ledge, the green body of | 6.79 / 6.72 | 0.275 |
| window | 508 | the wave and the white burst where they meet. | 6.79 / 6.73 | 0.275 |
| window | 508 | A critic in 1901 praised it for “great natural spaces | 6.79 / 6.73 | 0.275 |
| window | 508 | unmarked by the presence of puny man.” | 6.79 / 6.73 | 0.275 |
| window | 508 | Weather | 8.36 / 8.33 | 0.215 |
| window | 508 | Winter northeaster off the Atlantic | 8.36 / 8.36 | 0.215 |
| window | 508 | Artist | 8.36 / 8.33 | 0.215 |
| window | 508 | Winslow Homer ( American, 1836–1910 ) | 8.36 / 8.36 | 0.215 |
| window | 508 | Date | 8.33 / 8.33 | 0.216 |
| window | 508 | 1895; reworked by 1901 | 8.44 / 8.36 | 0.212 |
| window | 508 | Medium | 8.36 / 8.33 | 0.215 |
| window | 508 | Oil on canvas | 8.46 / 8.44 | 0.211 |
| window | 508 | Size | 8.36 / 8.36 | 0.215 |
| window | 508 | 87.6 × 127 cm | 8.44 / 8.44 | 0.212 |
| window | 508 | Collection | 8.47 / 8.36 | 0.211 |
| window | 508 | The Metropolitan Museum of Art, New York | 8.44 / 8.33 | 0.212 |
| window | 508 | Credit | 8.58 / 8.57 | 0.207 |
| window | 508 | Gift of George A. Hearn, 1910 | 8.58 / 8.44 | 0.207 |
| window | 508 | Number | 8.68 / 8.66 | 0.203 |
| window | 508 | 10.64.5 | 8.66 / 8.66 | 0.204 |
| window | 508 | Photograph: The Metropolitan Museum of Art, New York , open | 7.1 / 7.08 | 0.262 |
| window | 508 | access, public domain. | 7.1 / 7.08 | 0.262 |

### CSS tier at DPR 2, collapsed body · dark · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 6.73 / 6.71 | 0.278 |
| window | 0 | Room 8 of 8 | 6.73 / 6.63 | 0.278 |
| window | 0 | Fog (large) | 6.8 / 6.73 | 0.275 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 6.82 / 6.8 | 0.274 |
| window | 0 | Claude Monet | 6.82 / 6.73 | 0.274 |
| window | 0 | French, 1840–1926 · 1900 | 6.82 / 6.8 | 0.274 |
| window | 0 | The whole work. The outline marks the part around you. | 6.91 / 6.91 | 0.27 |
| window | 0 | Without the fog, Monet once remarked, London | 6.93 / 6.91 | 0.269 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 6.93 / 6.91 | 0.269 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 6.91 / 6.89 | 0.27 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 6.93 / 6.82 | 0.269 |
| window | 0 | he came to paint it. | 6.82 / 6.82 | 0.274 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 6.91 / 6.82 | 0.27 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 6.91 / 6.82 | 0.27 |
| Rooms | 0 | 8 | 6.43 / 6.43 | 0.29 |
| Rooms | 0 | / 8 | 6.43 / 6.43 | 0.29 |
| Audio guide | 0 | Audio guide | 6.82 / 6.74 | 0.274 |
| Audio guide | 0 | About 0:50 | 6.82 / 6.73 | 0.274 |
| Rooms | 0 | icon: Previous room: Gale | 6.43 / 6.34 | 0.29 |
| Audio guide | 0 | icon: Play the audio guide | 6.84 / 6.76 | 0.273 |
| window | 534 | He painted Waterloo Bridge in the mornings from his | 6.82 / 6.8 | 0.274 |
| window | 534 | fifth-floor window at the Savoy Hotel, moving on to | 6.82 / 6.8 | 0.274 |
| window | 534 | Charing Cross Bridge later in the day. Here the bridge | 6.82 / 6.8 | 0.274 |
| window | 534 | is a dark band of arches, and the city behind it is only | 6.8 / 6.8 | 0.275 |
| window | 534 | chimneys and towers in the haze. | 6.8 / 6.8 | 0.275 |
| window | 534 | He finished the London pictures in his studio at | 6.82 / 6.81 | 0.274 |
| window | 534 | Giverny, and would not release any of them until he | 6.82 / 6.82 | 0.274 |
| window | 534 | was satisfied with the series as a whole. | 6.82 / 6.82 | 0.274 |
| window | 534 | Weather | 8.36 / 8.33 | 0.215 |
| window | 534 | Winter fog and coal smoke | 8.36 / 8.36 | 0.215 |
| window | 534 | Artist | 8.38 / 8.36 | 0.214 |
| window | 534 | Claude Monet ( French, 1840–1926 ) | 8.46 / 8.46 | 0.211 |
| window | 534 | Date | 8.48 / 8.38 | 0.21 |
| window | 534 | 1900 | 8.46 / 8.46 | 0.211 |
| window | 534 | Medium | 8.48 / 8.4 | 0.21 |
| window | 534 | Oil on canvas | 8.46 / 8.46 | 0.211 |
| window | 534 | Size | 8.48 / 8.4 | 0.21 |
| window | 534 | 65.4 × 92.6 cm | 8.48 / 8.46 | 0.21 |
| window | 534 | Collection | 8.46 / 8.38 | 0.211 |
| window | 534 | The Art Institute of Chicago | 8.49 / 8.44 | 0.21 |
| window | 534 | Credit | 8.36 / 8.33 | 0.215 |
| window | 534 | Gift of Mrs. Mortimer B. Harris | 8.49 / 8.36 | 0.21 |
| window | 534 | Number | 8.36 / 8.33 | 0.215 |
| window | 534 | 1984.1173 | 8.37 / 8.36 | 0.215 |
| window | 534 | Photograph: The Art Institute of Chicago , open access, public | 6.91 / 6.82 | 0.27 |
| window | 534 | domain. | 6.8 / 6.71 | 0.275 |

## GPU tier, Reduce Transparency on

the page's own setting, active pose, label view. 861 line readings, 0 under floor. Worst p10 7.28: dark, active, frost, label view, window, “Room 1 of 8”.

### GPU tier, Reduce Transparency on · light · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 14.27 / 14.26 | 0.973 |
| window | 0 | Room 1 of 8 | 14.56 / 14.55 | 0.985 |
| window | 0 | Frost (large) | 14.26 / 14.17 | 0.973 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 14.38 / 14.1 | 0.977 |
| window | 0 | Hendrick Avercamp | 14.19 / 14.17 | 0.969 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 14.28 / 14.19 | 0.973 |
| window | 0 | The whole work. The outline marks the part around you. | 13.87 / 13.66 | 0.957 |
| window | 0 | Avercamp made his name painting winter, in the years | 13.89 / 13.68 | 0.957 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 13.98 / 13.83 | 0.961 |
| window | 0 | Countries. Here a whole village has moved onto the | 14 / 13.87 | 0.962 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 13.82 / 13.7 | 0.954 |
| window | 0 | sledge on the right, a church on the left. | 13.81 / 13.68 | 0.954 |
| window | 0 | Look at how the air is built. The figures in front are | 13.77 / 13.62 | 0.952 |
| window | 0 | sharp and full of colour; a few hundred metres back | 13.7 / 13.62 | 0.95 |
| Rooms | 0 | 1 | 14.26 / 14.09 | 0.973 |
| Rooms | 0 | / 8 | 14.36 / 14.29 | 0.976 |
| Audio guide | 0 | Audio guide | 14.45 / 14.27 | 0.98 |
| Audio guide | 0 | About 0:51 | 14.45 / 14.37 | 0.98 |
| Rooms | 0 | icon: Next room: Cloud | 14.39 / 14.37 | 0.978 |
| Audio guide | 0 | icon: Play the audio guide | 14.36 / 14.17 | 0.976 |
| window | 560 | Look at how the air is built. The figures in front are | 14.45 / 14.27 | 0.98 |
| window | 560 | sharp and full of colour; a few hundred metres back | 14.45 / 14.26 | 0.98 |
| window | 560 | they thin into grey-white haze, and the far bank all but | 14.39 / 14.19 | 0.978 |
| window | 560 | dissolves. That haze is the weather: cold, damp air | 14.37 / 14.08 | 0.977 |
| window | 560 | thick enough to carry the light. | 14.28 / 14.1 | 0.973 |
| window | 560 | Avercamp signed the picture on the wall of a wooden | 14.37 / 14.19 | 0.977 |
| window | 560 | shed on the right, among the scratched graffiti, where | 14.36 / 14.19 | 0.976 |
| window | 560 | it is easy to miss. | 14.17 / 14.17 | 0.969 |
| window | 560 | Weather | 12.72 / 12.54 | 0.908 |
| window | 560 | Hard frost, haze over the ice | 12.92 / 12.52 | 0.917 |
| window | 560 | Artist | 12.54 / 12.54 | 0.901 |
| window | 560 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 12.84 / 12.54 | 0.913 |
| window | 560 | Date | 12.52 / 12.45 | 0.9 |
| window | 560 | c. 1608 | 12.61 / 12.54 | 0.904 |
| window | 560 | Medium | 12.45 / 12.45 | 0.897 |
| window | 560 | Oil on panel | 12.72 / 12.56 | 0.908 |
| window | 560 | Size | 12.47 / 12.47 | 0.898 |
| window | 560 | 77.3 × 131.9 cm | 12.57 / 12.4 | 0.902 |
| window | 560 | Collection | 12.74 / 12.72 | 0.91 |
| window | 560 | Rijksmuseum, Amsterdam | 12.76 / 12.66 | 0.91 |
| window | 560 | Credit | 12.58 / 12.49 | 0.903 |
| window | 560 | Purchased with the support of the Vereniging | 12.66 / 12.49 | 0.906 |
| window | 560 | Rembrandt | 12.66 / 12.58 | 0.906 |
| window | 560 | Number | 12.47 / 12.4 | 0.898 |
| window | 560 | SK-A-1718 | 12.66 / 12.66 | 0.906 |
| window | 560 | Photograph: Rijksmuseum, Amsterdam , open access, public | 13.7 / 13.62 | 0.95 |
| window | 560 | domain. | 13.7 / 13.68 | 0.95 |

### GPU tier, Reduce Transparency on · light · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 13.69 / 13.68 | 0.949 |
| window | 0 | Room 2 of 8 | 13.69 / 13.69 | 0.949 |
| window | 0 | Cloud (large) | 13.69 / 13.66 | 0.949 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 13.69 / 13.69 | 0.949 |
| window | 0 | Jacob van Ruisdael | 13.69 / 13.69 | 0.949 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 13.69 / 13.69 | 0.949 |
| window | 0 | The whole work. The outline marks the part around you. | 13.87 / 13.76 | 0.957 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 13.88 / 13.79 | 0.957 |
| window | 0 | more than half the canvas, and he paints it as a | 13.88 / 13.79 | 0.957 |
| window | 0 | structure: banks of cumulus heaped over one another, | 13.88 / 13.79 | 0.957 |
| window | 0 | grey underneath, lit at their edges by a sun we | 13.88 / 13.87 | 0.957 |
| window | 0 | cannot see. | 13.88 / 13.88 | 0.957 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 14.14 / 14.05 | 0.968 |
| window | 0 | A sailing boat is out on the water, the towers of | 14.07 / 14.05 | 0.965 |
| Rooms | 0 | 2 | 13.78 / 13.71 | 0.953 |
| Rooms | 0 | / 8 | 13.78 / 13.78 | 0.953 |
| Audio guide | 0 | Audio guide | 13.78 / 13.78 | 0.953 |
| Audio guide | 0 | About 0:49 | 13.78 / 13.78 | 0.953 |
| Rooms | 0 | icon: Previous room: Frost | 13.78 / 13.71 | 0.953 |
| Rooms | 0 | icon: Next room: Clearing | 13.78 / 13.71 | 0.953 |
| Audio guide | 0 | icon: Play the audio guide | 13.78 / 13.78 | 0.953 |
| window | 560 | Below, the mill stands near the bank of the river Lek. | 13.69 / 13.69 | 0.949 |
| window | 560 | A sailing boat is out on the water, the towers of | 13.69 / 13.68 | 0.949 |
| window | 560 | Duurstede castle and the church rise in the distance, | 13.69 / 13.68 | 0.949 |
| window | 560 | and a few women walk along the bank, very small | 13.69 / 13.69 | 0.949 |
| window | 560 | against the mill. | 13.69 / 13.69 | 0.949 |
| window | 560 | Dutch painters of the seventeenth century made the | 13.69 / 13.69 | 0.949 |
| window | 560 | sky a subject in its own right. Few made it carry as | 13.79 / 13.69 | 0.953 |
| window | 560 | much of a picture as this. | 13.69 / 13.69 | 0.949 |
| window | 560 | Weather | 12.65 / 12.57 | 0.906 |
| window | 560 | Heaped cumulus, sun breaking through | 12.56 / 12.47 | 0.902 |
| window | 560 | Artist | 12.72 / 12.66 | 0.909 |
| window | 560 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 12.57 / 12.47 | 0.902 |
| window | 560 | Date | 12.72 / 12.66 | 0.909 |
| window | 560 | c. 1668–70 | 12.57 / 12.47 | 0.902 |
| window | 560 | Medium | 12.72 / 12.66 | 0.909 |
| window | 560 | Oil on canvas | 12.65 / 12.57 | 0.906 |
| window | 560 | Size | 12.74 / 12.74 | 0.91 |
| window | 560 | 83 × 101 cm | 12.72 / 12.66 | 0.909 |
| window | 560 | Collection | 12.74 / 12.66 | 0.91 |
| window | 560 | Rijksmuseum, Amsterdam | 12.63 / 12.57 | 0.905 |
| window | 560 | Credit | 12.72 / 12.66 | 0.909 |
| window | 560 | On loan from the City of Amsterdam (A. van | 12.66 / 12.57 | 0.906 |
| window | 560 | der Hoop Bequest) | 12.72 / 12.66 | 0.909 |
| window | 560 | Number | 12.72 / 12.66 | 0.909 |
| window | 560 | SK-C-211 | 12.75 / 12.75 | 0.91 |
| window | 560 | Photograph: Rijksmuseum, Amsterdam , open access, public | 14.06 / 14.04 | 0.964 |
| window | 560 | domain. | 14.06 / 14.04 | 0.964 |

### GPU tier, Reduce Transparency on · light · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 13.78 / 13.78 | 0.953 |
| window | 0 | Room 3 of 8 | 13.87 / 13.87 | 0.957 |
| window | 0 | Clearing (large) | 13.78 / 13.78 | 0.953 |
| window | 0 | View from Mount Holyoke, (large) | 13.78 / 13.78 | 0.953 |
| window | 0 | Northampton, Massachusetts, (large) | 13.78 / 13.78 | 0.953 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 13.79 / 13.78 | 0.953 |
| window | 0 | Thomas Cole | 13.78 / 13.68 | 0.953 |
| window | 0 | American, born England, 1801–1848 · 1836 | 13.78 / 13.71 | 0.953 |
| window | 0 | The whole work. The outline marks the part around you. | 13.78 / 13.7 | 0.953 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 13.7 / 13.68 | 0.95 |
| window | 0 | valley. On the left it still hangs over wild, broken trees, | 13.68 / 13.68 | 0.949 |
| window | 0 | and rain falls in grey veils across the hills. On the right | 13.68 / 13.68 | 0.949 |
| window | 0 | the air has cleared over cleared land: fields, farms | 13.69 / 13.68 | 0.949 |
| window | 0 | and the river’s great loop. | 13.68 / 13.68 | 0.949 |
| Rooms | 0 | 3 | 13.78 / 13.71 | 0.953 |
| Rooms | 0 | / 8 | 13.8 / 13.8 | 0.953 |
| Audio guide | 0 | Audio guide | 13.81 / 13.62 | 0.954 |
| Audio guide | 0 | About 0:50 | 13.7 / 13.68 | 0.95 |
| Rooms | 0 | icon: Previous room: Cloud | 13.69 / 13.69 | 0.949 |
| Rooms | 0 | icon: Next room: Thunder | 13.69 / 13.69 | 0.949 |
| Audio guide | 0 | icon: Play the audio guide | 13.68 / 13.68 | 0.949 |
| window | 612 | Cole divided the picture along a diagonal, and the | 13.78 / 13.78 | 0.953 |
| window | 612 | weather does the dividing. He painted it for the 1836 | 13.78 / 13.78 | 0.953 |
| window | 612 | annual exhibition of the National Academy of Design, | 13.78 / 13.78 | 0.953 |
| window | 612 | calling the view from Mount Holyoke “about the finest | 13.78 / 13.78 | 0.953 |
| window | 612 | scene I have in my sketchbook.” | 13.78 / 13.71 | 0.953 |
| window | 612 | Look for the painter himself near the bottom of the | 13.79 / 13.78 | 0.953 |
| window | 612 | canvas: a small figure at an easel among the rocks, | 13.79 / 13.78 | 0.953 |
| window | 612 | turning back toward us. | 13.78 / 13.69 | 0.953 |
| window | 612 | Weather | 12.56 / 12.49 | 0.902 |
| window | 612 | Thunderstorm passing, sun on the valley | 12.65 / 12.56 | 0.906 |
| window | 612 | Artist | 12.59 / 12.56 | 0.903 |
| window | 612 | Thomas Cole ( American, born England, | 12.58 / 12.56 | 0.903 |
| window | 612 | 1801–1848 ) | 12.56 / 12.49 | 0.902 |
| window | 612 | Date | 12.65 / 12.65 | 0.906 |
| window | 612 | 1836 | 12.56 / 12.49 | 0.902 |
| window | 612 | Medium | 12.56 / 12.56 | 0.902 |
| window | 612 | Oil on canvas | 12.56 / 12.49 | 0.902 |
| window | 612 | Size | 12.56 / 12.49 | 0.902 |
| window | 612 | 130.8 × 193 cm | 12.49 / 12.49 | 0.899 |
| window | 612 | Collection | 12.49 / 12.47 | 0.899 |
| window | 612 | The Metropolitan Museum of Art, New York | 12.47 / 12.47 | 0.898 |
| window | 612 | Credit | 12.56 / 12.56 | 0.902 |
| window | 612 | Gift of Mrs. Russell Sage, 1908 | 12.47 / 12.47 | 0.898 |
| window | 612 | Number | 12.56 / 12.49 | 0.902 |
| window | 612 | 08.228 | 12.47 / 12.47 | 0.898 |
| window | 612 | Photograph: The Metropolitan Museum of Art, New York , open | 13.68 / 13.68 | 0.949 |
| window | 616 | Cole divided the picture along a diagonal, and the | 13.78 / 13.78 | 0.953 |
| window | 616 | weather does the dividing. He painted it for the 1836 | 13.78 / 13.78 | 0.953 |
| window | 616 | annual exhibition of the National Academy of Design, | 13.78 / 13.78 | 0.953 |
| window | 616 | calling the view from Mount Holyoke “about the finest | 13.78 / 13.78 | 0.953 |
| window | 616 | scene I have in my sketchbook.” | 13.78 / 13.71 | 0.953 |
| window | 616 | Look for the painter himself near the bottom of the | 13.78 / 13.78 | 0.953 |
| window | 616 | canvas: a small figure at an easel among the rocks, | 13.79 / 13.78 | 0.953 |
| window | 616 | turning back toward us. | 13.78 / 13.69 | 0.953 |
| window | 616 | Weather | 12.56 / 12.49 | 0.902 |
| window | 616 | Thunderstorm passing, sun on the valley | 12.65 / 12.56 | 0.906 |
| window | 616 | Artist | 12.59 / 12.56 | 0.903 |
| window | 616 | Thomas Cole ( American, born England, | 12.58 / 12.56 | 0.903 |
| window | 616 | 1801–1848 ) | 12.56 / 12.49 | 0.902 |
| window | 616 | Date | 12.65 / 12.64 | 0.906 |
| window | 616 | 1836 | 12.56 / 12.49 | 0.902 |
| window | 616 | Medium | 12.58 / 12.56 | 0.903 |
| window | 616 | Oil on canvas | 12.56 / 12.49 | 0.902 |
| window | 616 | Size | 12.56 / 12.49 | 0.902 |
| window | 616 | 130.8 × 193 cm | 12.49 / 12.49 | 0.899 |
| window | 616 | Collection | 12.49 / 12.47 | 0.899 |
| window | 616 | The Metropolitan Museum of Art, New York | 12.47 / 12.47 | 0.898 |
| window | 616 | Credit | 12.56 / 12.56 | 0.902 |
| window | 616 | Gift of Mrs. Russell Sage, 1908 | 12.47 / 12.47 | 0.898 |
| window | 616 | Number | 12.56 / 12.49 | 0.902 |
| window | 616 | 08.228 | 12.47 / 12.47 | 0.898 |
| window | 616 | Photograph: The Metropolitan Museum of Art, New York , open | 13.69 / 13.68 | 0.949 |
| window | 616 | access, public domain. | 13.68 / 13.68 | 0.949 |

### GPU tier, Reduce Transparency on · light · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 13.71 / 13.71 | 0.95 |
| window | 0 | Room 4 of 8 | 13.71 / 13.71 | 0.95 |
| window | 0 | Thunder (large) | 13.78 / 13.71 | 0.953 |
| window | 0 | Approaching Thunder Storm (large) | 13.78 / 13.71 | 0.953 |
| window | 0 | Martin Johnson Heade | 13.78 / 13.78 | 0.953 |
| window | 0 | American, 1819–1904 · 1859 | 13.81 / 13.78 | 0.954 |
| window | 0 | The whole work. The outline marks the part around you. | 13.78 / 13.78 | 0.953 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 13.89 / 13.78 | 0.957 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 13.91 / 13.78 | 0.958 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 13.69 / 13.69 | 0.949 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 13.69 / 13.69 | 0.949 |
| window | 0 | rower pulls for shore; a white sail stands out against | 13.69 / 13.69 | 0.949 |
| window | 0 | the dark. | 13.69 / 13.69 | 0.949 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 13.69 / 13.69 | 0.949 |
| Rooms | 0 | 4 | 13.72 / 13.72 | 0.95 |
| Rooms | 0 | / 8 | 13.83 / 13.79 | 0.955 |
| Audio guide | 0 | Audio guide | 14.1 / 13.92 | 0.966 |
| Audio guide | 0 | About 0:53 | 14.1 / 14.01 | 0.966 |
| Rooms | 0 | icon: Previous room: Clearing | 13.81 / 13.72 | 0.954 |
| Rooms | 0 | icon: Next room: Rain | 14.1 / 14 | 0.966 |
| Audio guide | 0 | icon: Play the audio guide | 13.9 / 13.81 | 0.958 |
| window | 612 | before such a storm, and that is what the picture | 13.71 / 13.71 | 0.95 |
| window | 612 | holds: not the storm itself but the minute before it. | 13.78 / 13.71 | 0.953 |
| window | 612 | Painted two years before the Civil War, it has often | 13.78 / 13.71 | 0.953 |
| window | 612 | been read as a picture of a country waiting for | 13.78 / 13.71 | 0.953 |
| window | 612 | something to break. Heade based it on a storm | 13.78 / 13.78 | 0.953 |
| window | 612 | he had watched from Prudence Island, in the bay, | 13.81 / 13.78 | 0.954 |
| window | 612 | around 1858. | 13.78 / 13.78 | 0.953 |
| window | 612 | Weather | 12.65 / 12.65 | 0.906 |
| window | 612 | Thunderstorm approaching over still water | 12.67 / 12.67 | 0.906 |
| window | 612 | Artist | 12.65 / 12.65 | 0.906 |
| window | 612 | Martin Johnson Heade ( American, 1819–1904 | 12.67 / 12.65 | 0.906 |
| window | 612 | 1819–1904 ) | 12.65 / 12.65 | 0.906 |
| window | 612 | Date | 12.65 / 12.65 | 0.906 |
| window | 612 | 1859 | 12.65 / 12.65 | 0.906 |
| window | 612 | Medium | 12.56 / 12.56 | 0.902 |
| window | 612 | Oil on canvas | 12.56 / 12.56 | 0.902 |
| window | 612 | Size | 12.58 / 12.58 | 0.903 |
| window | 612 | 71.1 × 111.8 cm | 12.58 / 12.56 | 0.903 |
| window | 612 | Collection | 12.75 / 12.66 | 0.91 |
| window | 612 | The Metropolitan Museum of Art, New York | 12.58 / 12.49 | 0.903 |
| window | 612 | Credit | 12.47 / 12.47 | 0.898 |
| window | 612 | Gift of Erving Wolf Foundation and Mr. and | 12.47 / 12.47 | 0.898 |
| window | 612 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 12.47 / 12.47 | 0.898 |
| window | 612 | 1975 | 12.47 / 12.47 | 0.898 |
| window | 612 | Number | 12.47 / 12.47 | 0.898 |
| window | 612 | 1975.160 | 12.47 / 12.47 | 0.898 |
| window | 626 | holds: not the storm itself but the minute before it. | 13.78 / 13.71 | 0.953 |
| window | 626 | Painted two years before the Civil War, it has often | 13.78 / 13.71 | 0.953 |
| window | 626 | been read as a picture of a country waiting for | 13.78 / 13.71 | 0.953 |
| window | 626 | something to break. Heade based it on a storm | 13.78 / 13.78 | 0.953 |
| window | 626 | he had watched from Prudence Island, in the bay, | 13.78 / 13.78 | 0.953 |
| window | 626 | around 1858. | 13.78 / 13.78 | 0.953 |
| window | 626 | Weather | 12.65 / 12.65 | 0.906 |
| window | 626 | Thunderstorm approaching over still water | 12.67 / 12.67 | 0.906 |
| window | 626 | Artist | 12.65 / 12.65 | 0.906 |
| window | 626 | Martin Johnson Heade ( American, 1819–1904 | 12.67 / 12.67 | 0.906 |
| window | 626 | 1819–1904 ) | 12.65 / 12.65 | 0.906 |
| window | 626 | Date | 12.65 / 12.65 | 0.906 |
| window | 626 | 1859 | 12.67 / 12.65 | 0.906 |
| window | 626 | Medium | 12.65 / 12.65 | 0.906 |
| window | 626 | Oil on canvas | 12.59 / 12.56 | 0.903 |
| window | 626 | Size | 12.56 / 12.56 | 0.902 |
| window | 626 | 71.1 × 111.8 cm | 12.56 / 12.56 | 0.902 |
| window | 626 | Collection | 12.73 / 12.66 | 0.909 |
| window | 626 | The Metropolitan Museum of Art, New York | 12.66 / 12.66 | 0.906 |
| window | 626 | Credit | 12.49 / 12.47 | 0.899 |
| window | 626 | Gift of Erving Wolf Foundation and Mr. and | 12.47 / 12.47 | 0.898 |
| window | 626 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 12.47 / 12.47 | 0.898 |
| window | 626 | 1975 | 12.47 / 12.47 | 0.898 |
| window | 626 | Number | 12.47 / 12.47 | 0.898 |
| window | 626 | 1975.160 | 12.47 / 12.47 | 0.898 |
| window | 626 | Photograph: The Metropolitan Museum of Art, New York , open | 13.69 / 13.69 | 0.949 |
| window | 626 | access, public domain. | 13.71 / 13.69 | 0.95 |

### GPU tier, Reduce Transparency on · light · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 14.39 / 13.97 | 0.978 |
| window | 0 | Room 5 of 8 | 13.98 / 13.96 | 0.961 |
| window | 0 | Rain (large) | 14.08 / 13.98 | 0.965 |
| window | 0 | Paris Street; Rainy Day (large) | 14.06 / 13.96 | 0.964 |
| window | 0 | Gustave Caillebotte | 13.98 / 13.86 | 0.961 |
| window | 0 | French, 1848–1894 · 1877 | 13.96 / 13.88 | 0.96 |
| window | 0 | The whole work. The outline marks the part around you. | 14.07 / 13.62 | 0.965 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 14.16 / 13.79 | 0.968 |
| window | 0 | paints the rain through what it does: the paving | 14.16 / 13.79 | 0.968 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 14.16 / 13.9 | 0.968 |
| window | 0 | everyone carries an umbrella, the newly invented | 14.16 / 13.87 | 0.968 |
| window | 0 | retractable kind. | 13.98 / 13.69 | 0.961 |
| window | 0 | The place is a busy intersection a short walk from the | 14.07 / 13.79 | 0.965 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 14.06 / 13.79 | 0.964 |
| Rooms | 0 | 5 | 13.78 / 13.78 | 0.953 |
| Rooms | 0 | / 8 | 13.87 / 13.79 | 0.957 |
| Audio guide | 0 | Audio guide | 14.06 / 14 | 0.964 |
| Audio guide | 0 | About 0:46 | 14.06 / 13.97 | 0.964 |
| Rooms | 0 | icon: Previous room: Thunder | 13.78 / 13.69 | 0.953 |
| Rooms | 0 | icon: Next room: Wind | 14.06 / 13.97 | 0.964 |
| Audio guide | 0 | icon: Play the audio guide | 14 / 13.99 | 0.962 |
| window | 586 | painter’s home, in a Paris rebuilt with wide streets | 14.16 / 13.96 | 0.968 |
| window | 586 | and uniform stone façades. A green lamppost splits | 14.08 / 13.96 | 0.965 |
| window | 586 | the canvas in two; the couple on the right walk | 14.08 / 13.97 | 0.965 |
| window | 586 | straight toward us, looking at something beyond | 14.07 / 13.98 | 0.965 |
| window | 586 | the frame. | 14 / 13.95 | 0.962 |
| window | 586 | Nearly life-size, it is Caillebotte’s largest painting. He | 13.98 / 13.88 | 0.961 |
| window | 586 | showed it at the third Impressionist exhibition in 1877, | 13.98 / 13.96 | 0.961 |
| window | 586 | the year he made it. | 14.05 / 13.96 | 0.964 |
| window | 586 | Weather | 12.71 / 12.65 | 0.908 |
| window | 586 | Light rain, overcast | 12.65 / 12.62 | 0.905 |
| window | 586 | Artist | 12.55 / 12.45 | 0.901 |
| window | 586 | Gustave Caillebotte ( French, 1848–1894 ) | 12.62 / 12.45 | 0.904 |
| window | 586 | Date | 12.38 / 12.38 | 0.894 |
| window | 586 | 1877 | 12.74 / 12.65 | 0.91 |
| window | 586 | Medium | 12.39 / 12.36 | 0.894 |
| window | 586 | Oil on canvas | 12.77 / 12.75 | 0.911 |
| window | 586 | Size | 12.38 / 12.36 | 0.894 |
| window | 586 | 212.2 × 276.2 cm | 12.84 / 12.75 | 0.913 |
| window | 586 | Collection | 12.84 / 12.77 | 0.913 |
| window | 586 | The Art Institute of Chicago | 12.84 / 12.77 | 0.913 |
| window | 586 | Credit | 12.47 / 12.38 | 0.898 |
| window | 586 | Charles H. and Mary F. S. Worcester | 12.84 / 12.77 | 0.913 |
| window | 586 | Number | 12.57 / 12.47 | 0.902 |
| window | 586 | 1964.336 | 12.75 / 12.75 | 0.91 |
| window | 586 | Photograph: The Art Institute of Chicago , open access, public | 14.07 / 13.79 | 0.965 |
| window | 586 | domain. | 13.79 / 13.69 | 0.953 |

### GPU tier, Reduce Transparency on · light · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 14.08 / 13.94 | 0.965 |
| window | 0 | Room 6 of 8 | 14.18 / 14.16 | 0.969 |
| window | 0 | Wind (large) | 13.96 / 13.87 | 0.96 |
| window | 0 | Wheat Field with Cypresses (large) | 14.16 / 14.07 | 0.968 |
| window | 0 | Vincent van Gogh | 14.07 / 14.05 | 0.965 |
| window | 0 | Dutch, 1853–1890 · 1889 | 14.05 / 13.96 | 0.964 |
| window | 0 | The whole work. The outline marks the part around you. | 13.96 / 13.94 | 0.96 |
| window | 0 | Everything in this field is moving the same way. The | 14.02 / 13.95 | 0.963 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 13.96 / 13.79 | 0.96 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 13.85 / 13.68 | 0.956 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 13.76 / 13.66 | 0.952 |
| window | 0 | the paint on so heavily that the brushstrokes | 13.76 / 13.73 | 0.952 |
| window | 0 | themselves take the shape of the wind. | 13.85 / 13.76 | 0.955 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 13.78 / 13.66 | 0.953 |
| Rooms | 0 | 6 | 13.9 / 13.9 | 0.958 |
| Rooms | 0 | / 8 | 13.9 / 13.88 | 0.958 |
| Audio guide | 0 | Audio guide | 13.9 / 13.86 | 0.958 |
| Audio guide | 0 | About 0:51 | 13.88 / 13.79 | 0.957 |
| Rooms | 0 | icon: Previous room: Rain | 13.88 / 13.81 | 0.957 |
| Rooms | 0 | icon: Next room: Gale | 13.97 / 13.88 | 0.96 |
| Audio guide | 0 | icon: Play the audio guide | 13.79 / 13.79 | 0.953 |
| window | 586 | He painted it in late June or early July 1889 at Saint-Rémy | 14.18 / 13.94 | 0.969 |
| window | 586 | Saint-Rémy in Provence, where he was a patient at the | 14.18 / 13.87 | 0.969 |
| window | 586 | asylum of Saint-Paul-de-Mausole, working outdoors | 14.16 / 13.96 | 0.968 |
| window | 586 | in front of the motif. | 14.16 / 14.07 | 0.968 |
| window | 586 | He counted it among his best summer canvases, and | 14.07 / 14.05 | 0.965 |
| window | 586 | that September made two studio versions of it: one | 14.05 / 13.96 | 0.964 |
| window | 586 | now in the National Gallery, London, the other a | 14.05 / 13.96 | 0.964 |
| window | 586 | smaller copy for his mother and sister. | 14 / 13.87 | 0.962 |
| window | 586 | Weather | 12.73 / 12.71 | 0.909 |
| window | 586 | Summer wind, fast cloud | 12.73 / 12.7 | 0.909 |
| window | 586 | Artist | 12.73 / 12.73 | 0.909 |
| window | 586 | Vincent van Gogh ( Dutch, 1853–1890 ) | 12.71 / 12.71 | 0.908 |
| window | 586 | Date | 12.65 / 12.64 | 0.905 |
| window | 586 | 1889 | 12.71 / 12.71 | 0.908 |
| window | 586 | Medium | 12.73 / 12.73 | 0.909 |
| window | 586 | Oil on canvas | 12.71 / 12.71 | 0.908 |
| window | 586 | Size | 12.73 / 12.73 | 0.909 |
| window | 586 | 73.2 × 93.4 cm | 12.73 / 12.71 | 0.909 |
| window | 586 | Collection | 12.73 / 12.73 | 0.909 |
| window | 586 | The Metropolitan Museum of Art, New York | 12.63 / 12.54 | 0.905 |
| window | 586 | Credit | 12.73 / 12.73 | 0.909 |
| window | 586 | Purchase, The Annenberg Foundation Gift, | 12.53 / 12.45 | 0.901 |
| window | 586 | 1993 | 12.54 / 12.51 | 0.901 |
| window | 586 | Number | 12.73 / 12.72 | 0.909 |
| window | 586 | 1993.132 | 12.54 / 12.51 | 0.901 |
| window | 586 | Photograph: The Metropolitan Museum of Art, New York , open | 13.77 / 13.66 | 0.952 |
| window | 586 | access, public domain. | 13.77 / 13.66 | 0.952 |

### GPU tier, Reduce Transparency on · light · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 14.06 / 13.98 | 0.964 |
| window | 0 | Room 7 of 8 | 14.37 / 13.95 | 0.977 |
| window | 0 | Gale (large) | 14.06 / 13.96 | 0.964 |
| window | 0 | Northeaster (large) | 14.15 / 13.96 | 0.968 |
| window | 0 | Winslow Homer | 14.17 / 14.06 | 0.969 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 14.27 / 14.17 | 0.973 |
| window | 0 | The whole work. The outline marks the part around you. | 14.05 / 13.96 | 0.964 |
| window | 0 | A northeaster is a winter storm that drives in off the | 14.05 / 13.96 | 0.964 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 13.98 / 13.96 | 0.961 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 13.98 / 13.88 | 0.961 |
| window | 0 | lived and painted for the last decades of his life. | 13.79 / 13.6 | 0.953 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 13.58 / 13.5 | 0.944 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 13.58 / 13.5 | 0.944 |
| window | 0 | lower left. By 1900 he had painted them out and | 13.51 / 13.5 | 0.941 |
| Rooms | 0 | 7 | 13.79 / 13.79 | 0.953 |
| Rooms | 0 | / 8 | 13.79 / 13.79 | 0.953 |
| Audio guide | 0 | Audio guide | 13.69 / 13.69 | 0.949 |
| Audio guide | 0 | About 0:50 | 13.78 / 13.69 | 0.953 |
| Rooms | 0 | icon: Previous room: Wind | 13.69 / 13.69 | 0.949 |
| Rooms | 0 | icon: Next room: Fog | 13.79 / 13.78 | 0.953 |
| Audio guide | 0 | icon: Play the audio guide | 13.81 / 13.69 | 0.954 |
| window | 514 | When he first exhibited this canvas in 1895, two men | 14.46 / 14.06 | 0.981 |
| window | 514 | in foul-weather gear crouched on the rocks at the | 14.44 / 14.05 | 0.98 |
| window | 514 | lower left. By 1900 he had painted them out and | 14.43 / 14.05 | 0.98 |
| window | 514 | raised a much larger column of spray. What is left is | 14.43 / 14.06 | 0.98 |
| window | 514 | rock, water and air: the dark ledge, the green body of | 14.35 / 14.15 | 0.976 |
| window | 514 | the wave and the white burst where they meet. | 14.27 / 14.17 | 0.973 |
| window | 514 | A critic in 1901 praised it for “great natural spaces | 14.34 / 14.17 | 0.976 |
| window | 514 | unmarked by the presence of puny man.” | 14.34 / 14.15 | 0.976 |
| window | 514 | Weather | 12.82 / 12.76 | 0.913 |
| window | 514 | Winter northeaster off the Atlantic | 12.92 / 12.85 | 0.917 |
| window | 514 | Artist | 12.82 / 12.76 | 0.913 |
| window | 514 | Winslow Homer ( American, 1836–1910 ) | 12.76 / 12.75 | 0.91 |
| window | 514 | Date | 12.82 / 12.76 | 0.913 |
| window | 514 | 1895; reworked by 1901 | 12.75 / 12.73 | 0.91 |
| window | 514 | Medium | 12.82 / 12.76 | 0.913 |
| window | 514 | Oil on canvas | 12.73 / 12.73 | 0.909 |
| window | 514 | Size | 12.66 / 12.64 | 0.906 |
| window | 514 | 87.6 × 127 cm | 12.73 / 12.73 | 0.909 |
| window | 514 | Collection | 12.66 / 12.64 | 0.906 |
| window | 514 | The Metropolitan Museum of Art, New York | 12.75 / 12.66 | 0.91 |
| window | 514 | Credit | 12.38 / 12.36 | 0.894 |
| window | 514 | Gift of George A. Hearn, 1910 | 12.38 / 12.36 | 0.894 |
| window | 514 | Number | 12.29 / 12.29 | 0.89 |
| window | 514 | 10.64.5 | 12.3 / 12.29 | 0.89 |
| window | 514 | Photograph: The Metropolitan Museum of Art, New York , open | 13.58 / 13.51 | 0.944 |
| window | 514 | access, public domain. | 13.58 / 13.51 | 0.944 |

### GPU tier, Reduce Transparency on · light · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 13.95 / 13.95 | 0.96 |
| window | 0 | Room 8 of 8 | 13.98 / 13.98 | 0.961 |
| window | 0 | Fog (large) | 13.97 / 13.95 | 0.961 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 13.97 / 13.95 | 0.961 |
| window | 0 | Claude Monet | 13.88 / 13.86 | 0.957 |
| window | 0 | French, 1840–1926 · 1900 | 13.88 / 13.86 | 0.957 |
| window | 0 | The whole work. The outline marks the part around you. | 13.77 / 13.74 | 0.952 |
| window | 0 | Without the fog, Monet once remarked, London | 13.77 / 13.68 | 0.952 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 13.77 / 13.68 | 0.952 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 13.76 / 13.67 | 0.952 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 13.77 / 13.67 | 0.952 |
| window | 0 | he came to paint it. | 13.88 / 13.87 | 0.957 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 13.77 / 13.67 | 0.952 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 13.76 / 13.67 | 0.952 |
| Rooms | 0 | 8 | 13.79 / 13.76 | 0.953 |
| Rooms | 0 | / 8 | 13.79 / 13.79 | 0.953 |
| Audio guide | 0 | Audio guide | 13.76 / 13.74 | 0.952 |
| Audio guide | 0 | About 0:50 | 13.77 / 13.76 | 0.952 |
| Rooms | 0 | icon: Previous room: Gale | 13.85 / 13.85 | 0.956 |
| Audio guide | 0 | icon: Play the audio guide | 13.74 / 13.74 | 0.951 |
| window | 540 | He painted Waterloo Bridge in the mornings from his | 13.97 / 13.95 | 0.961 |
| window | 540 | fifth-floor window at the Savoy Hotel, moving on to | 13.97 / 13.95 | 0.961 |
| window | 540 | Charing Cross Bridge later in the day. Here the bridge | 13.97 / 13.95 | 0.961 |
| window | 540 | is a dark band of arches, and the city behind it is only | 13.97 / 13.95 | 0.961 |
| window | 540 | chimneys and towers in the haze. | 13.97 / 13.88 | 0.961 |
| window | 540 | He finished the London pictures in his studio at | 13.97 / 13.86 | 0.961 |
| window | 540 | Giverny, and would not release any of them until he | 13.88 / 13.86 | 0.957 |
| window | 540 | was satisfied with the series as a whole. | 13.86 / 13.86 | 0.956 |
| window | 540 | Weather | 12.66 / 12.64 | 0.906 |
| window | 540 | Winter fog and coal smoke | 12.66 / 12.64 | 0.906 |
| window | 540 | Artist | 12.65 / 12.55 | 0.906 |
| window | 540 | Claude Monet ( French, 1840–1926 ) | 12.57 / 12.55 | 0.902 |
| window | 540 | Date | 12.55 / 12.53 | 0.901 |
| window | 540 | 1900 | 12.55 / 12.55 | 0.901 |
| window | 540 | Medium | 12.53 / 12.53 | 0.9 |
| window | 540 | Oil on canvas | 12.55 / 12.53 | 0.901 |
| window | 540 | Size | 12.53 / 12.46 | 0.9 |
| window | 540 | 65.4 × 92.6 cm | 12.55 / 12.55 | 0.901 |
| window | 540 | Collection | 12.55 / 12.46 | 0.901 |
| window | 540 | The Art Institute of Chicago | 12.45 / 12.45 | 0.897 |
| window | 540 | Credit | 12.65 / 12.63 | 0.906 |
| window | 540 | Gift of Mrs. Mortimer B. Harris | 12.47 / 12.45 | 0.898 |
| window | 540 | Number | 12.65 / 12.63 | 0.906 |
| window | 540 | 1984.1173 | 12.65 / 12.63 | 0.906 |
| window | 540 | Photograph: The Art Institute of Chicago , open access, public | 13.76 / 13.67 | 0.952 |
| window | 540 | domain. | 13.88 / 13.87 | 0.957 |

### GPU tier, Reduce Transparency on · dark · frost · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.39 / 7.38 | 0.251 |
| window | 0 | Room 1 of 8 | 7.38 / 7.28 | 0.251 |
| window | 0 | Frost (large) | 7.49 / 7.39 | 0.247 |
| window | 0 | Winter Landscape with Ice Skaters (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Hendrick Avercamp | 7.49 / 7.49 | 0.247 |
| window | 0 | Dutch, 1585–1634 · c. 1608 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | Avercamp made his name painting winter, in the years | 7.49 / 7.49 | 0.247 |
| window | 0 | when the Little Ice Age brought hard frosts to the Low | 7.49 / 7.49 | 0.247 |
| window | 0 | Countries. Here a whole village has moved onto the | 7.49 / 7.49 | 0.247 |
| window | 0 | ice: skaters, walkers, players of kolf, a horse-drawn | 7.49 / 7.49 | 0.247 |
| window | 0 | sledge on the right, a church on the left. | 7.49 / 7.49 | 0.247 |
| window | 0 | Look at how the air is built. The figures in front are | 7.49 / 7.49 | 0.247 |
| window | 0 | sharp and full of colour; a few hundred metres back | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 1 | 7.39 / 7.39 | 0.248 |
| Rooms | 0 | / 8 | 7.39 / 7.39 | 0.251 |
| Audio guide | 0 | Audio guide | 7.39 / 7.38 | 0.251 |
| Audio guide | 0 | About 0:51 | 7.39 / 7.38 | 0.251 |
| Rooms | 0 | icon: Next room: Cloud | 7.38 / 7.38 | 0.251 |
| Audio guide | 0 | icon: Play the audio guide | 7.38 / 7.38 | 0.251 |
| window | 565 | Look at how the air is built. The figures in front are | 7.39 / 7.38 | 0.251 |
| window | 565 | sharp and full of colour; a few hundred metres back | 7.49 / 7.41 | 0.247 |
| window | 565 | they thin into grey-white haze, and the far bank all but | 7.49 / 7.39 | 0.247 |
| window | 565 | dissolves. That haze is the weather: cold, damp air | 7.49 / 7.49 | 0.247 |
| window | 565 | thick enough to carry the light. | 7.49 / 7.49 | 0.247 |
| window | 565 | Avercamp signed the picture on the wall of a wooden | 7.49 / 7.49 | 0.247 |
| window | 565 | shed on the right, among the scratched graffiti, where | 7.49 / 7.49 | 0.247 |
| window | 565 | it is easy to miss. | 7.49 / 7.49 | 0.247 |
| window | 565 | Weather | 9 / 9 | 0.192 |
| window | 565 | Hard frost, haze over the ice | 9 / 9 | 0.192 |
| window | 565 | Artist | 9 / 9 | 0.192 |
| window | 565 | Hendrick Avercamp ( Dutch, 1585–1634 ) | 9 / 9 | 0.192 |
| window | 565 | Date | 9 / 9 | 0.192 |
| window | 565 | c. 1608 | 9 / 9 | 0.192 |
| window | 565 | Medium | 9 / 9 | 0.192 |
| window | 565 | Oil on panel | 9 / 9 | 0.192 |
| window | 565 | Size | 9 / 9 | 0.192 |
| window | 565 | 77.3 × 131.9 cm | 9 / 9 | 0.192 |
| window | 565 | Collection | 9 / 9 | 0.192 |
| window | 565 | Rijksmuseum, Amsterdam | 9 / 9 | 0.192 |
| window | 565 | Credit | 9 / 9 | 0.192 |
| window | 565 | Purchased with the support of the Vereniging | 9 / 9 | 0.192 |
| window | 565 | Rembrandt | 9 / 9 | 0.192 |
| window | 565 | Number | 9 / 9 | 0.192 |
| window | 565 | SK-A-1718 | 9 / 9 | 0.192 |
| window | 565 | Photograph: Rijksmuseum, Amsterdam , open access, public | 7.49 / 7.49 | 0.247 |
| window | 565 | domain. | 7.49 / 7.49 | 0.247 |

### GPU tier, Reduce Transparency on · dark · cloud · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.49 / 7.49 | 0.247 |
| window | 0 | Room 2 of 8 | 7.49 / 7.49 | 0.247 |
| window | 0 | Cloud (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | The Windmill at Wijk bij Duurstede (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Jacob van Ruisdael | 7.49 / 7.49 | 0.247 |
| window | 0 | Dutch, 1628/29–1682 · c. 1668–70 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | Ruisdael sets the horizon very low, so the sky takes | 7.49 / 7.49 | 0.247 |
| window | 0 | more than half the canvas, and he paints it as a | 7.49 / 7.49 | 0.247 |
| window | 0 | structure: banks of cumulus heaped over one another, | 7.49 / 7.49 | 0.247 |
| window | 0 | grey underneath, lit at their edges by a sun we | 7.49 / 7.49 | 0.247 |
| window | 0 | cannot see. | 7.49 / 7.49 | 0.247 |
| window | 0 | Below, the mill stands near the bank of the river Lek. | 7.49 / 7.49 | 0.247 |
| window | 0 | A sailing boat is out on the water, the towers of | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 2 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | / 8 | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | Audio guide | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | About 0:49 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Previous room: Frost | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Next room: Clearing | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | icon: Play the audio guide | 7.49 / 7.49 | 0.247 |
| window | 565 | Below, the mill stands near the bank of the river Lek. | 7.49 / 7.49 | 0.247 |
| window | 565 | A sailing boat is out on the water, the towers of | 7.49 / 7.49 | 0.247 |
| window | 565 | Duurstede castle and the church rise in the distance, | 7.49 / 7.49 | 0.247 |
| window | 565 | and a few women walk along the bank, very small | 7.49 / 7.49 | 0.247 |
| window | 565 | against the mill. | 7.49 / 7.49 | 0.247 |
| window | 565 | Dutch painters of the seventeenth century made the | 7.49 / 7.49 | 0.247 |
| window | 565 | sky a subject in its own right. Few made it carry as | 7.49 / 7.49 | 0.247 |
| window | 565 | much of a picture as this. | 7.49 / 7.49 | 0.247 |
| window | 565 | Weather | 9 / 9 | 0.192 |
| window | 565 | Heaped cumulus, sun breaking through | 9 / 9 | 0.192 |
| window | 565 | Artist | 9 / 8.92 | 0.192 |
| window | 565 | Jacob van Ruisdael ( Dutch, 1628/29–1682 ) | 9 / 9 | 0.192 |
| window | 565 | Date | 9 / 8.91 | 0.192 |
| window | 565 | c. 1668–70 | 9 / 9 | 0.192 |
| window | 565 | Medium | 9 / 8.92 | 0.192 |
| window | 565 | Oil on canvas | 9 / 9 | 0.192 |
| window | 565 | Size | 9 / 8.89 | 0.192 |
| window | 565 | 83 × 101 cm | 9 / 9 | 0.192 |
| window | 565 | Collection | 9 / 9 | 0.192 |
| window | 565 | Rijksmuseum, Amsterdam | 9 / 9 | 0.192 |
| window | 565 | Credit | 9 / 9 | 0.192 |
| window | 565 | On loan from the City of Amsterdam (A. van | 9 / 9 | 0.192 |
| window | 565 | der Hoop Bequest) | 9 / 9 | 0.192 |
| window | 565 | Number | 9 / 9 | 0.192 |
| window | 565 | SK-C-211 | 9 / 9 | 0.192 |
| window | 565 | Photograph: Rijksmuseum, Amsterdam , open access, public | 7.49 / 7.49 | 0.247 |
| window | 565 | domain. | 7.49 / 7.38 | 0.247 |

### GPU tier, Reduce Transparency on · dark · clearing · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.49 / 7.49 | 0.247 |
| window | 0 | Room 3 of 8 | 7.46 / 7.39 | 0.248 |
| window | 0 | Clearing (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | View from Mount Holyoke, (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Northampton, Massachusetts, (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | after a Thunderstorm—The Oxbow (large) | 7.49 / 7.46 | 0.247 |
| window | 0 | Thomas Cole | 7.49 / 7.49 | 0.247 |
| window | 0 | American, born England, 1801–1848 · 1836 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | A thunderstorm is leaving the Connecticut River | 7.49 / 7.49 | 0.247 |
| window | 0 | valley. On the left it still hangs over wild, broken trees, | 7.49 / 7.49 | 0.247 |
| window | 0 | and rain falls in grey veils across the hills. On the right | 7.49 / 7.49 | 0.247 |
| window | 0 | the air has cleared over cleared land: fields, farms | 7.49 / 7.49 | 0.247 |
| window | 0 | and the river’s great loop. | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 3 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | / 8 | 7.49 / 7.46 | 0.247 |
| Audio guide | 0 | Audio guide | 7.49 / 7.46 | 0.247 |
| Audio guide | 0 | About 0:50 | 7.49 / 7.46 | 0.247 |
| Rooms | 0 | icon: Previous room: Cloud | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Next room: Thunder | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | icon: Play the audio guide | 7.49 / 7.49 | 0.247 |
| window | 607 | Cole divided the picture along a diagonal, and the | 7.49 / 7.49 | 0.247 |
| window | 607 | weather does the dividing. He painted it for the 1836 | 7.49 / 7.46 | 0.247 |
| window | 607 | annual exhibition of the National Academy of Design, | 7.49 / 7.46 | 0.247 |
| window | 607 | calling the view from Mount Holyoke “about the finest | 7.49 / 7.39 | 0.247 |
| window | 607 | scene I have in my sketchbook.” | 7.49 / 7.49 | 0.247 |
| window | 607 | Look for the painter himself near the bottom of the | 7.49 / 7.49 | 0.247 |
| window | 607 | canvas: a small figure at an easel among the rocks, | 7.49 / 7.49 | 0.247 |
| window | 607 | turning back toward us. | 7.49 / 7.49 | 0.247 |
| window | 607 | Weather | 9 / 9 | 0.192 |
| window | 607 | Thunderstorm passing, sun on the valley | 9 / 9 | 0.192 |
| window | 607 | Artist | 9 / 9 | 0.192 |
| window | 607 | Thomas Cole ( American, born England, | 9 / 9 | 0.192 |
| window | 607 | 1801–1848 ) | 9 / 9 | 0.192 |
| window | 607 | Date | 9 / 9 | 0.192 |
| window | 607 | 1836 | 9 / 9 | 0.192 |
| window | 607 | Medium | 9 / 9 | 0.192 |
| window | 607 | Oil on canvas | 9 / 9 | 0.192 |
| window | 607 | Size | 9 / 9 | 0.192 |
| window | 607 | 130.8 × 193 cm | 9 / 9 | 0.192 |
| window | 607 | Collection | 9 / 9 | 0.192 |
| window | 607 | The Metropolitan Museum of Art, New York | 9.01 / 9 | 0.192 |
| window | 607 | Credit | 9 / 9 | 0.192 |
| window | 607 | Gift of Mrs. Russell Sage, 1908 | 9.01 / 9 | 0.192 |
| window | 607 | Number | 9 / 9 | 0.192 |
| window | 607 | 08.228 | 9.01 / 9.01 | 0.192 |
| window | 621 | Cole divided the picture along a diagonal, and the | 7.49 / 7.49 | 0.247 |
| window | 621 | weather does the dividing. He painted it for the 1836 | 7.49 / 7.46 | 0.247 |
| window | 621 | annual exhibition of the National Academy of Design, | 7.49 / 7.46 | 0.247 |
| window | 621 | calling the view from Mount Holyoke “about the finest | 7.49 / 7.39 | 0.247 |
| window | 621 | scene I have in my sketchbook.” | 7.49 / 7.49 | 0.247 |
| window | 621 | Look for the painter himself near the bottom of the | 7.49 / 7.49 | 0.247 |
| window | 621 | canvas: a small figure at an easel among the rocks, | 7.49 / 7.49 | 0.247 |
| window | 621 | turning back toward us. | 7.49 / 7.49 | 0.247 |
| window | 621 | Weather | 9 / 9 | 0.192 |
| window | 621 | Thunderstorm passing, sun on the valley | 9 / 9 | 0.192 |
| window | 621 | Artist | 9 / 9 | 0.192 |
| window | 621 | Thomas Cole ( American, born England, | 9 / 9 | 0.192 |
| window | 621 | 1801–1848 ) | 9 / 9 | 0.192 |
| window | 621 | Date | 9 / 9 | 0.192 |
| window | 621 | 1836 | 9 / 9 | 0.192 |
| window | 621 | Medium | 9 / 9 | 0.192 |
| window | 621 | Oil on canvas | 9 / 9 | 0.192 |
| window | 621 | Size | 9 / 9 | 0.192 |
| window | 621 | 130.8 × 193 cm | 9 / 9 | 0.192 |
| window | 621 | Collection | 9 / 9 | 0.192 |
| window | 621 | The Metropolitan Museum of Art, New York | 9 / 9 | 0.192 |
| window | 621 | Credit | 9 / 9 | 0.192 |
| window | 621 | Gift of Mrs. Russell Sage, 1908 | 9.01 / 9 | 0.192 |
| window | 621 | Number | 9 / 9 | 0.192 |
| window | 621 | 08.228 | 9.01 / 9.01 | 0.192 |
| window | 621 | Photograph: The Metropolitan Museum of Art, New York , open | 7.49 / 7.49 | 0.247 |
| window | 621 | access, public domain. | 7.49 / 7.49 | 0.247 |

### GPU tier, Reduce Transparency on · dark · thunder · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.49 / 7.49 | 0.247 |
| window | 0 | Room 4 of 8 | 7.49 / 7.49 | 0.247 |
| window | 0 | Thunder (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Approaching Thunder Storm (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Martin Johnson Heade | 7.49 / 7.49 | 0.247 |
| window | 0 | American, 1819–1904 · 1859 | 7.49 / 7.46 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | A man and his dog sit on the shore of Narragansett | 7.46 / 7.39 | 0.248 |
| window | 0 | Bay, Rhode Island, with sunlight still at their backs. | 7.39 / 7.37 | 0.251 |
| window | 0 | Ahead of them the sky has gone almost black, and a | 7.49 / 7.49 | 0.247 |
| window | 0 | thin red bolt of lightning cuts down on the left. A | 7.49 / 7.49 | 0.247 |
| window | 0 | rower pulls for shore; a white sail stands out against | 7.49 / 7.49 | 0.247 |
| window | 0 | the dark. | 7.49 / 7.49 | 0.247 |
| window | 0 | A critic of Heade’s day spoke of the “ominous hush” | 7.49 / 7.46 | 0.247 |
| Rooms | 0 | 4 | 7.46 / 7.46 | 0.248 |
| Rooms | 0 | / 8 | 7.46 / 7.46 | 0.248 |
| Audio guide | 0 | Audio guide | 7.39 / 7.39 | 0.251 |
| Audio guide | 0 | About 0:53 | 7.46 / 7.46 | 0.248 |
| Rooms | 0 | icon: Previous room: Clearing | 7.39 / 7.39 | 0.251 |
| Rooms | 0 | icon: Next room: Rain | 7.39 / 7.37 | 0.251 |
| Audio guide | 0 | icon: Play the audio guide | 7.46 / 7.46 | 0.248 |
| window | 607 | before such a storm, and that is what the picture | 7.49 / 7.49 | 0.247 |
| window | 607 | holds: not the storm itself but the minute before it. | 7.49 / 7.49 | 0.247 |
| window | 607 | Painted two years before the Civil War, it has often | 7.49 / 7.49 | 0.247 |
| window | 607 | been read as a picture of a country waiting for | 7.49 / 7.49 | 0.247 |
| window | 607 | something to break. Heade based it on a storm | 7.49 / 7.49 | 0.247 |
| window | 607 | he had watched from Prudence Island, in the bay, | 7.49 / 7.46 | 0.247 |
| window | 607 | around 1858. | 7.49 / 7.46 | 0.247 |
| window | 607 | Weather | 8.98 / 8.98 | 0.193 |
| window | 607 | Thunderstorm approaching over still water | 8.98 / 8.9 | 0.193 |
| window | 607 | Artist | 8.98 / 8.98 | 0.193 |
| window | 607 | Martin Johnson Heade ( American, 1819–1904 | 8.98 / 8.98 | 0.193 |
| window | 607 | 1819–1904 ) | 8.98 / 8.98 | 0.193 |
| window | 607 | Date | 8.98 / 8.98 | 0.193 |
| window | 607 | 1859 | 8.98 / 8.98 | 0.193 |
| window | 607 | Medium | 9 / 9 | 0.192 |
| window | 607 | Oil on canvas | 9 / 9 | 0.192 |
| window | 607 | Size | 8.98 / 8.98 | 0.193 |
| window | 607 | 71.1 × 111.8 cm | 8.98 / 8.9 | 0.193 |
| window | 607 | Collection | 8.87 / 8.87 | 0.197 |
| window | 607 | The Metropolitan Museum of Art, New York | 9 / 8.98 | 0.192 |
| window | 607 | Credit | 9 / 9 | 0.192 |
| window | 607 | Gift of Erving Wolf Foundation and Mr. and | 9 / 9 | 0.192 |
| window | 607 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9 / 9 | 0.192 |
| window | 607 | 1975 | 9 / 9 | 0.192 |
| window | 607 | Number | 9 / 9 | 0.192 |
| window | 607 | 1975.160 | 9 / 9 | 0.192 |
| window | 631 | holds: not the storm itself but the minute before it. | 7.49 / 7.49 | 0.247 |
| window | 631 | Painted two years before the Civil War, it has often | 7.49 / 7.49 | 0.247 |
| window | 631 | been read as a picture of a country waiting for | 7.49 / 7.49 | 0.247 |
| window | 631 | something to break. Heade based it on a storm | 7.49 / 7.49 | 0.247 |
| window | 631 | he had watched from Prudence Island, in the bay, | 7.49 / 7.49 | 0.247 |
| window | 631 | around 1858. | 7.49 / 7.49 | 0.247 |
| window | 631 | Weather | 8.98 / 8.98 | 0.193 |
| window | 631 | Thunderstorm approaching over still water | 8.9 / 8.9 | 0.196 |
| window | 631 | Artist | 8.98 / 8.98 | 0.193 |
| window | 631 | Martin Johnson Heade ( American, 1819–1904 | 8.98 / 8.98 | 0.193 |
| window | 631 | 1819–1904 ) | 8.98 / 8.98 | 0.193 |
| window | 631 | Date | 8.98 / 8.98 | 0.193 |
| window | 631 | 1859 | 8.98 / 8.98 | 0.193 |
| window | 631 | Medium | 8.98 / 8.98 | 0.193 |
| window | 631 | Oil on canvas | 8.98 / 8.98 | 0.193 |
| window | 631 | Size | 9 / 9 | 0.192 |
| window | 631 | 71.1 × 111.8 cm | 9 / 9 | 0.192 |
| window | 631 | Collection | 8.9 / 8.9 | 0.196 |
| window | 631 | The Metropolitan Museum of Art, New York | 8.9 / 8.87 | 0.196 |
| window | 631 | Credit | 9 / 9 | 0.192 |
| window | 631 | Gift of Erving Wolf Foundation and Mr. and | 9 / 9 | 0.192 |
| window | 631 | Mrs. Erving Wolf, in memory of Diane R. Wolf, | 9 / 9 | 0.192 |
| window | 631 | 1975 | 9 / 9 | 0.192 |
| window | 631 | Number | 9 / 9 | 0.192 |
| window | 631 | 1975.160 | 9 / 9 | 0.192 |
| window | 631 | Photograph: The Metropolitan Museum of Art, New York , open | 7.49 / 7.39 | 0.247 |
| window | 631 | access, public domain. | 7.49 / 7.46 | 0.247 |

### GPU tier, Reduce Transparency on · dark · rain · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.38 / 7.38 | 0.251 |
| window | 0 | Room 5 of 8 | 7.49 / 7.38 | 0.247 |
| window | 0 | Rain (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Paris Street; Rainy Day (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Gustave Caillebotte | 7.49 / 7.49 | 0.247 |
| window | 0 | French, 1848–1894 · 1877 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | There are no raindrops in this picture. Caillebotte | 7.49 / 7.49 | 0.247 |
| window | 0 | paints the rain through what it does: the paving | 7.49 / 7.49 | 0.247 |
| window | 0 | stones shine, the light is flat and pearly, and almost | 7.49 / 7.49 | 0.247 |
| window | 0 | everyone carries an umbrella, the newly invented | 7.49 / 7.49 | 0.247 |
| window | 0 | retractable kind. | 7.49 / 7.49 | 0.247 |
| window | 0 | The place is a busy intersection a short walk from the | 7.49 / 7.49 | 0.247 |
| window | 0 | painter’s home, in a Paris rebuilt with wide streets | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 5 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | / 8 | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | Audio guide | 7.38 / 7.38 | 0.251 |
| Audio guide | 0 | About 0:46 | 7.41 / 7.38 | 0.25 |
| Rooms | 0 | icon: Previous room: Thunder | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Next room: Wind | 7.38 / 7.38 | 0.251 |
| Audio guide | 0 | icon: Play the audio guide | 7.38 / 7.38 | 0.251 |
| window | 591 | and uniform stone façades. A green lamppost splits | 7.49 / 7.49 | 0.247 |
| window | 591 | the canvas in two; the couple on the right walk | 7.49 / 7.49 | 0.247 |
| window | 591 | straight toward us, looking at something beyond | 7.49 / 7.49 | 0.247 |
| window | 591 | the frame. | 7.49 / 7.49 | 0.247 |
| window | 591 | Nearly life-size, it is Caillebotte’s largest painting. He | 7.49 / 7.49 | 0.247 |
| window | 591 | showed it at the third Impressionist exhibition in 1877, | 7.49 / 7.49 | 0.247 |
| window | 591 | the year he made it. | 7.49 / 7.49 | 0.247 |
| window | 591 | Weather | 9 / 9 | 0.192 |
| window | 591 | Light rain, overcast | 9 / 9 | 0.192 |
| window | 591 | Artist | 9 / 9 | 0.192 |
| window | 591 | Gustave Caillebotte ( French, 1848–1894 ) | 9 / 9 | 0.192 |
| window | 591 | Date | 9 / 9 | 0.192 |
| window | 591 | 1877 | 9 / 9 | 0.192 |
| window | 591 | Medium | 9 / 9 | 0.192 |
| window | 591 | Oil on canvas | 9 / 9 | 0.192 |
| window | 591 | Size | 9 / 9 | 0.192 |
| window | 591 | 212.2 × 276.2 cm | 9 / 9 | 0.192 |
| window | 591 | Collection | 9 / 9 | 0.192 |
| window | 591 | The Art Institute of Chicago | 9 / 9 | 0.192 |
| window | 591 | Credit | 9 / 9 | 0.192 |
| window | 591 | Charles H. and Mary F. S. Worcester | 9 / 9 | 0.192 |
| window | 591 | Number | 9 / 9 | 0.192 |
| window | 591 | 1964.336 | 9 / 9 | 0.192 |
| window | 591 | Photograph: The Art Institute of Chicago , open access, public | 7.49 / 7.49 | 0.247 |
| window | 591 | domain. | 7.49 / 7.49 | 0.247 |

### GPU tier, Reduce Transparency on · dark · wind · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.41 / 7.38 | 0.25 |
| window | 0 | Room 6 of 8 | 7.38 / 7.38 | 0.251 |
| window | 0 | Wind (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Wheat Field with Cypresses (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Vincent van Gogh | 7.49 / 7.49 | 0.247 |
| window | 0 | Dutch, 1853–1890 · 1889 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | Everything in this field is moving the same way. The | 7.49 / 7.49 | 0.247 |
| window | 0 | wheat bends, the olive trees toss, the cypresses | 7.49 / 7.49 | 0.247 |
| window | 0 | flicker like dark flames, and the clouds curl across the | 7.49 / 7.49 | 0.247 |
| window | 0 | sky in thick ridges of white and blue. Van Gogh laid | 7.49 / 7.49 | 0.247 |
| window | 0 | the paint on so heavily that the brushstrokes | 7.49 / 7.49 | 0.247 |
| window | 0 | themselves take the shape of the wind. | 7.49 / 7.49 | 0.247 |
| window | 0 | He painted it in late June or early July 1889 at Saint-Rémy | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 6 | 7.46 / 7.46 | 0.248 |
| Rooms | 0 | / 8 | 7.46 / 7.46 | 0.248 |
| Audio guide | 0 | Audio guide | 7.49 / 7.46 | 0.247 |
| Audio guide | 0 | About 0:51 | 7.49 / 7.46 | 0.247 |
| Rooms | 0 | icon: Previous room: Rain | 7.46 / 7.46 | 0.248 |
| Rooms | 0 | icon: Next room: Gale | 7.46 / 7.39 | 0.248 |
| Audio guide | 0 | icon: Play the audio guide | 7.49 / 7.46 | 0.247 |
| window | 591 | Saint-Rémy in Provence, where he was a patient at the | 7.49 / 7.49 | 0.247 |
| window | 591 | asylum of Saint-Paul-de-Mausole, working outdoors | 7.49 / 7.49 | 0.247 |
| window | 591 | in front of the motif. | 7.49 / 7.49 | 0.247 |
| window | 591 | He counted it among his best summer canvases, and | 7.49 / 7.49 | 0.247 |
| window | 591 | that September made two studio versions of it: one | 7.49 / 7.49 | 0.247 |
| window | 591 | now in the National Gallery, London, the other a | 7.49 / 7.49 | 0.247 |
| window | 591 | smaller copy for his mother and sister. | 7.49 / 7.49 | 0.247 |
| window | 591 | Weather | 9 / 9 | 0.192 |
| window | 591 | Summer wind, fast cloud | 9 / 9 | 0.192 |
| window | 591 | Artist | 9 / 9 | 0.192 |
| window | 591 | Vincent van Gogh ( Dutch, 1853–1890 ) | 9 / 9 | 0.192 |
| window | 591 | Date | 9 / 9 | 0.192 |
| window | 591 | 1889 | 9 / 9 | 0.192 |
| window | 591 | Medium | 9 / 9 | 0.192 |
| window | 591 | Oil on canvas | 9 / 9 | 0.192 |
| window | 591 | Size | 9 / 9 | 0.192 |
| window | 591 | 73.2 × 93.4 cm | 9 / 9 | 0.192 |
| window | 591 | Collection | 9 / 9 | 0.192 |
| window | 591 | The Metropolitan Museum of Art, New York | 9 / 9 | 0.192 |
| window | 591 | Credit | 9 / 9 | 0.192 |
| window | 591 | Purchase, The Annenberg Foundation Gift, | 9 / 9 | 0.192 |
| window | 591 | 1993 | 9 / 9 | 0.192 |
| window | 591 | Number | 9 / 9 | 0.192 |
| window | 591 | 1993.132 | 9 / 9 | 0.192 |
| window | 591 | Photograph: The Metropolitan Museum of Art, New York , open | 7.49 / 7.49 | 0.247 |
| window | 591 | access, public domain. | 7.49 / 7.49 | 0.247 |

### GPU tier, Reduce Transparency on · dark · gale · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.48 / 7.41 | 0.247 |
| window | 0 | Room 7 of 8 | 7.48 / 7.41 | 0.247 |
| window | 0 | Gale (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Northeaster (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Winslow Homer | 7.49 / 7.49 | 0.247 |
| window | 0 | American, 1836–1910 · 1895; reworked by 1901 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | A northeaster is a winter storm that drives in off the | 7.49 / 7.49 | 0.247 |
| window | 0 | Atlantic on a northeast wind. Homer watched them | 7.49 / 7.49 | 0.247 |
| window | 0 | from Prouts Neck, on the coast of Maine, where he | 7.49 / 7.49 | 0.247 |
| window | 0 | lived and painted for the last decades of his life. | 7.49 / 7.49 | 0.247 |
| window | 0 | When he first exhibited this canvas in 1895, two men | 7.49 / 7.49 | 0.247 |
| window | 0 | in foul-weather gear crouched on the rocks at the | 7.49 / 7.49 | 0.247 |
| window | 0 | lower left. By 1900 he had painted them out and | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 7 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | / 8 | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | Audio guide | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | About 0:50 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Previous room: Wind | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Next room: Fog | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | icon: Play the audio guide | 7.49 / 7.49 | 0.247 |
| window | 519 | When he first exhibited this canvas in 1895, two men | 7.49 / 7.48 | 0.247 |
| window | 519 | in foul-weather gear crouched on the rocks at the | 7.49 / 7.48 | 0.247 |
| window | 519 | lower left. By 1900 he had painted them out and | 7.49 / 7.49 | 0.247 |
| window | 519 | raised a much larger column of spray. What is left is | 7.49 / 7.49 | 0.247 |
| window | 519 | rock, water and air: the dark ledge, the green body of | 7.49 / 7.49 | 0.247 |
| window | 519 | the wave and the white burst where they meet. | 7.49 / 7.49 | 0.247 |
| window | 519 | A critic in 1901 praised it for “great natural spaces | 7.49 / 7.49 | 0.247 |
| window | 519 | unmarked by the presence of puny man.” | 7.49 / 7.49 | 0.247 |
| window | 519 | Weather | 9 / 9 | 0.192 |
| window | 519 | Winter northeaster off the Atlantic | 9 / 9 | 0.192 |
| window | 519 | Artist | 9 / 8.91 | 0.192 |
| window | 519 | Winslow Homer ( American, 1836–1910 ) | 9 / 9 | 0.192 |
| window | 519 | Date | 9 / 8.91 | 0.192 |
| window | 519 | 1895; reworked by 1901 | 9 / 9 | 0.192 |
| window | 519 | Medium | 9 / 9 | 0.192 |
| window | 519 | Oil on canvas | 9 / 9 | 0.192 |
| window | 519 | Size | 9 / 9 | 0.192 |
| window | 519 | 87.6 × 127 cm | 9 / 9 | 0.192 |
| window | 519 | Collection | 9 / 9 | 0.192 |
| window | 519 | The Metropolitan Museum of Art, New York | 9 / 9 | 0.192 |
| window | 519 | Credit | 9 / 9 | 0.192 |
| window | 519 | Gift of George A. Hearn, 1910 | 9 / 9 | 0.192 |
| window | 519 | Number | 9 / 9 | 0.192 |
| window | 519 | 10.64.5 | 9.03 / 9 | 0.191 |
| window | 519 | Photograph: The Metropolitan Museum of Art, New York , open | 7.49 / 7.49 | 0.247 |
| window | 519 | access, public domain. | 7.51 / 7.49 | 0.246 |

### GPU tier, Reduce Transparency on · dark · fog · label view

| where | scroll | line | active | surface |
|---|---|---|---|---|
| window | 0 | Weather in Painting | 7.49 / 7.39 | 0.247 |
| window | 0 | Room 8 of 8 | 7.41 / 7.38 | 0.25 |
| window | 0 | Fog (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Waterloo Bridge, Gray Weather (large) | 7.49 / 7.49 | 0.247 |
| window | 0 | Claude Monet | 7.49 / 7.49 | 0.247 |
| window | 0 | French, 1840–1926 · 1900 | 7.49 / 7.49 | 0.247 |
| window | 0 | The whole work. The outline marks the part around you. | 7.49 / 7.49 | 0.247 |
| window | 0 | Without the fog, Monet once remarked, London | 7.49 / 7.49 | 0.247 |
| window | 0 | “wouldn’t be a beautiful city. It’s the fog that gives it | 7.49 / 7.49 | 0.247 |
| window | 0 | its magnificent breadth.” Much of that fog was the | 7.49 / 7.49 | 0.247 |
| window | 0 | smoke of coal fires, thickest in winter, which is when | 7.49 / 7.49 | 0.247 |
| window | 0 | he came to paint it. | 7.49 / 7.49 | 0.247 |
| window | 0 | He painted Waterloo Bridge in the mornings from his | 7.49 / 7.49 | 0.247 |
| window | 0 | fifth-floor window at the Savoy Hotel, moving on to | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | 8 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | / 8 | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | Audio guide | 7.49 / 7.49 | 0.247 |
| Audio guide | 0 | About 0:50 | 7.49 / 7.49 | 0.247 |
| Rooms | 0 | icon: Previous room: Gale | 7.49 / 7.41 | 0.247 |
| Audio guide | 0 | icon: Play the audio guide | 7.49 / 7.49 | 0.247 |
| window | 545 | He painted Waterloo Bridge in the mornings from his | 7.49 / 7.49 | 0.247 |
| window | 545 | fifth-floor window at the Savoy Hotel, moving on to | 7.49 / 7.49 | 0.247 |
| window | 545 | Charing Cross Bridge later in the day. Here the bridge | 7.49 / 7.49 | 0.247 |
| window | 545 | is a dark band of arches, and the city behind it is only | 7.49 / 7.49 | 0.247 |
| window | 545 | chimneys and towers in the haze. | 7.49 / 7.49 | 0.247 |
| window | 545 | He finished the London pictures in his studio at | 7.49 / 7.49 | 0.247 |
| window | 545 | Giverny, and would not release any of them until he | 7.49 / 7.49 | 0.247 |
| window | 545 | was satisfied with the series as a whole. | 7.49 / 7.49 | 0.247 |
| window | 545 | Weather | 9 / 9 | 0.192 |
| window | 545 | Winter fog and coal smoke | 9 / 9 | 0.192 |
| window | 545 | Artist | 9 / 9 | 0.192 |
| window | 545 | Claude Monet ( French, 1840–1926 ) | 9 / 9 | 0.192 |
| window | 545 | Date | 9 / 9 | 0.192 |
| window | 545 | 1900 | 9 / 9 | 0.192 |
| window | 545 | Medium | 9 / 9 | 0.192 |
| window | 545 | Oil on canvas | 9 / 9 | 0.192 |
| window | 545 | Size | 9 / 9 | 0.192 |
| window | 545 | 65.4 × 92.6 cm | 9 / 9 | 0.192 |
| window | 545 | Collection | 9 / 9 | 0.192 |
| window | 545 | The Art Institute of Chicago | 9 / 9 | 0.192 |
| window | 545 | Credit | 9 / 9 | 0.192 |
| window | 545 | Gift of Mrs. Mortimer B. Harris | 9 / 9 | 0.192 |
| window | 545 | Number | 9 / 9 | 0.192 |
| window | 545 | 1984.1173 | 9 / 9 | 0.192 |
| window | 545 | Photograph: The Art Institute of Chicago , open access, public | 7.49 / 7.49 | 0.247 |
| window | 545 | domain. | 7.49 / 7.41 | 0.247 |
