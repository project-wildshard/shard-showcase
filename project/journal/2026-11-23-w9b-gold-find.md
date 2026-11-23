# W9b Gold find: tank-roof art study

W9b uses Gold finds to draw the player to the West activities. The archived
Round 5 placement at x −206, z −104 uses y 18.5 as the bottom of a 1 m cube.
The original position intersects the pinned art junction’s static roof-hook
pedestal. The study moves only the collectible, 2.5 m south to x −206,
z −101.5. Import bounds checks found no remaining overlap at that position
and five rays sampled the flat 18 m roof below. The studio and roof photos
use the same reimported GLB, hovering about 0.5 m above the roof in situ.
This is not the separate Movers top-deck spot. There is no size stencil,
following Round 11 v2; the small diamond is a nonverbal mark.

The asset has a shared cast face used six times, muted bright insets and a
dark brass core. Preview lights are not shipped. The local origin is at the
bottom center. The Station 6 roof asset is not duplicated or modified. This
is one art-only collectible, not an implemented touch reward, revised route
plan, or confirmation of any other pickup coordinates.

Rebuild the roof reference and the Gold model and previews:

```sh
blender -b -t 6 --python scripts/blender/west-movers-roof/build.py -- --output /tmp/west-static
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/gold_find_cube.py -- \
  /tmp/west-static/junction/west-shared-roof-WIP.glb /tmp/w9b-gold-find
```

References: [W9b plan](../../docs/plans/kitchen-sink-v2/slices/W9b-vistas-caches-gold-finds.md),
[Round 5 Gold placements](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L299),
[Round 11 v2 art constraints](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/COMMON-v2.txt#L10).
