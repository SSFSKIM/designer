# Credits: the relief map's data

`relief.webp`, `relief.bin` and `relief.json` are built by
`apps/demo/scripts/build-terminal-relief.mjs` from **Terrain Tiles on AWS**
(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/`), in the Tilezen "terrarium"
encoding at zoom 12, about 30 m a pixel over the Lake Tahoe basin. Over the United States those
tiles are the USGS 3D Elevation Program, a public-domain dataset.

The attribution the source asks for, word for word:

> United States 3DEP (formerly NED) and global GMTED2010 and SRTM terrain data courtesy of the
> U.S. Geological Survey

The page shows a short form of it in a corner, the `tahoe` command prints the line in full, and
`relief.json` carries it as `attribution`.

The spot heights on the map (the summits in `relief.json`) are read from the 30 m grid: the
highest grid sample within 1.2 km of each named peak. A grid rounds a summit down, so they are
lower than the surveyed heights and are not survey values. The lake levels and areas are the
grid's reading of each lake's flat surface in the same way.
