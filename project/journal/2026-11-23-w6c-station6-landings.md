# W6c: both Station 6 bridge landings measured

The full-size bridge and tank already exist in `scripts/blender/west-movers-roof`.
The original [Round 5 call](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/lab.js#L371)
sets anchors 22.023 m apart at 18 m, with 26 intervals, 1.6 m sag and
1.5 m-wide planks. The checked authored art shares the same anchors, but has
54 plank placements, 0.65 m sag, 1.6 m-wide planks and a full-sized 16 m-radius
tank roof. The short walkway and small vessel in the catalogue are different
assets, and neither was stretched. No additional bridge or tank was created.

A mesh reimport with the established semantic fingerprint measured both
joins. The deck and roof each have a level 18.000 m standing plane near
the threshold. Both threshold caps are 12 mm higher. At its center, the
first plank is about 36 mm below the cap. The first open seam after that
plank is about 25 mm wide in each of three sampled lanes at both ends.
Near midspan, the checked plank top is 17.350 m. The two photographs are
new close-up renders of the same export, with presentation lights only.
Neither the measurements nor the photos validate collision, traversal,
rope behavior, safety, or a gameplay step threshold.

To rebuild from the existing source, then inspect both ends:

```sh
blender -b -t 6 --python scripts/blender/west-movers-roof/build.py -- --output /tmp/west-static
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/bridge_landing_check.py -- \
  /tmp/west-static/junction/west-shared-roof-WIP.glb /tmp/station6-proof
```

Append `--measure-only` after the output directory to skip rendering.
The study audits a single known bridge. It does not infer the fifth bridge
not individually located in W6c.
