# WSC-SCENE-009: north-up surface atlas and depth section

Extracted the shown venue bounds directly from
`Raynos/project-wildshard-singleplayer@ce1cf050b3`,
`art/showcase-template/round-5-blockout/layout.js`, blob
`5d019a020361c47187ec889f2bc947f82cd9f98a`. The normalized JSON is enough
to rebuild the drawn atlas without access to that repo. The extractor
hash-checks the historical source before reading it and does not run it.

The surface uses a uniform north-up 500 × 500 m scale: +X east, +Z south.
The West Town masonry arch is X −8; the seam is X 7.5, not the local X 0
of the separate Blender gate composition. The three Gauntlet courts,
passages and Titan gate's three rectangles draw on the same datum.
Only the Titan entrance is on the surface. M01–M03 remain historic
references and are not silently overwritten.

The depth inset uses a separate linear Y scale. It applies D41 for
the four-room Vault volume at Y −50…−30; the Titan sky at −80 lies 30 m
below that, with the 104 m arena floor at −150 and 140 m across the
stands. The depth rectangle widths are explanatory, not footprints.
D7 updates the park to launch walls; D61 omits level heat and band
boundaries. D4 lists ordered stops but does not draw a travel route.

```sh
python scripts/art/render-round5-atlas.py \
  project/layouts/wsc-scene-009-round5-atlas.json /tmp/nov23-round5-atlas.svg
```

The art is a planned layout, not an implemented level, navigation guide,
QA claim about routes, or a player map UI.
