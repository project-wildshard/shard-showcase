# E9 · Storm Hour corner mounting study

Round 5 `ce1cf050b3`, `art/showcase-template/round-5-blockout/{layout,lab}.js` (layout blob `5d019a020361c47187ec889f2bc947f82cd9f98a`, lab blob `51a3b4bef1f2d4891172164d10893d98d450a3b9`) and the E9 design pin four Band 5 corner anchors: (126,14), (232,14), (232,118), (126,118) world X/Z. The 2.6 m-high, 0.60 m-thick walls join the 4 m × 4 m, 12 m-high pedestal intentionally. North and west gaps remain 16 m. The empty yard is not a replacement for the stealth yard; route furniture, shed, cover, and gameplay are out of scope.

The old 1.4 m stem cannot seat the exact 2.180 m foot. One 2.94 m square platform extends the original pedestal; the unchanged reimports set the mounting plane at y=14.533658 m and the crown at y=20 m. The charged insert spans y=19.203658–19.778658 m. Eight geometric rays between adjacent lamp positions (both directions, clipping 1.1 m per endpoint to exclude its own cage) clear the rebuilt boundary. Roof Gold has its unchanged base position witness (232,20,118); the open cage does not provide a solid seat there. No Gold mesh, support, collision, mechanics, or native placement is exported.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/beacon_corner_fit.py -- /tmp/beacon-corners
node scripts/blender/showcase-studies/check_beacon_corner_fit.mjs
```

The Python script pins both donor GLBs, reconstructs the bounding walls and exact placement, exports and reimports the seat, checks the four crowns and sightlines, writes the measurements, and renders two art-only views. Use `WILDSHARD_VALIDATE_ONLY=1` to skip the two renders. The 45,096 B / 496-triangle GLB has an origin at the pedestal cap and can be reused at every corner. Staging lights and apron marks are illustrative. No `.blend`, raw render, or duplicated donor is needed in Git.
