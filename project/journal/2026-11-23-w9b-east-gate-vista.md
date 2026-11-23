# W9b East Gatehouse vista: one bench, two portrait bearings

The historical Vista 6 marker at game coordinates (−10, 9, −10) misses the
roof in the current East Gate boundary art. This does not rewrite the
layout or disprove the prior detached camera on a different stage.
Reusing that boundary's pinned span and flanking towers, the supported
prop origin is (−8.00, 7.61, −4.70), 5.66 m away horizontally. The four
underside pads of the exact lookout bench were checked at their centers
and four inset corners. Their height spread is 0.81 mm over twenty hits.
This uses the upper visible roof surface; it does not establish roof access.

The two 402:874 frames hold one seated-eye position, an 80° vertical
field of view, and a fixed slight downward pitch. They yaw 26.5° apart.
The portrait's horizontal envelope is 42.21°; the four source-derived
band-center bearings cover 49.55°. Direct rays to all four center and
illustrative raised points miss the reimported span and tower geometry.
This verifies local obstruction and framing, not the current East
terrain. The hills and yard shapes are illustrative, not native band
geometry. The roof, tower, and bench GLBs remain unchanged. There is
no runtime bench interaction, discovery flag, camera or terrain change.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/east_gate_vista.py -- /tmp/east-vista
```

The build produces two views, one placement photo and `validation.json`.
Set `WILDSHARD_VALIDATE_ONLY=1` to skip rendering.

[W9b](../../docs/plans/kitchen-sink-v2/slices/W9b-vistas-caches-gold-finds.md)
· [Archived vista](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L292)
· [Band rectangles](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L100).
