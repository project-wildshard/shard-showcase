# E03 paired pillar and suspended screen

Round 5 used this repeated overhead module in Band 3, separately
from its opaque ground-level sight walls. The archived shell is two
7 m posts on 8 m centers, a 9.6 m head beam, and a 7.6 m wide
suspended panel from +2.2 to +6.2 m. The decoration is new:
precast collars, a worn ochre beam, dark formed steel and cyan
inlays. The model stays visually open below the panel and in the
200 mm slot between the panel and head beam.

Source: [layout.js, Band 3 entry][layout],
[lab.js, coverPiece][lab], and [placement.js][placement]
at `ce1cf050b3`. The nearest recorded pillar is at archive
x/z (138.638, −221.816), yaw 3.28656 radians. The first camera
stands at (122, −224), 1.7 m up, 16.78 m from the frame center.
The source x/y/z maps to Blender (x, −z, y) and the positive
yaw maps to Blender Z. The second camera is editorial and shows
the under-panel space more directly.

The apron is review staging inspired by the existing E03 pale
paving. The recipe reuses the tracked dock and planter at editorial
offsets; these are not authored neighboring positions. The
standalone GLB contains neither donor, ground, light nor camera.
No runtime scene, navigation, collision, combat or drone perch
has been authored. Do not create an alias for the E03 dock or
lantern, or confuse this with the 3 m sight wall.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/e03_pillar_frame.py -- /tmp/e03-pillar
```

The script reimports the GLB, verifies total bounds (9.6 × 1.6 ×
7 m), checks block/open visual rays, pins the donor hashes, and
writes the SHA-256, size and two camera fit receipts. Only the
source and standalone module are retained in Git.

[layout]: https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L123
[lab]: https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/lab.js#L718
[placement]: https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/placement.js#L129
