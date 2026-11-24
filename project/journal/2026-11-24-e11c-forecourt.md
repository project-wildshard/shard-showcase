# E11c Gauntlet forecourt: separate C1 and Titan approaches

Return to Round 5 zone 08F, not C1's interior descents. The west
16 m cut in the SE wall aligns to the exterior ramp at x 62, z 132–142
and up 3 m. The east 16 m cut feeds the 12 m Titan road. This model
includes the first 32 m of that road beyond the forecourt only.
The checkpoint and 9 × 4 m run board are restored as static props at
their archived positions. The board shows five slots and no best time.

The export is in local coordinates around game (80, 0, 132). The
rebuild imports the exact C1 Loading Yard as its neighbor; those
bytes are not duplicated or modified. Both cuts have 155 clear
sampled sightlines. Twenty clearance samples cross the C1 seam.
Seven downward samples on either side of that seam see at most
13.51 mm height difference (includes being 5 mm upstream on the
ramp). The nominal C1 floor is +3 m; panel tops are +3.012 m.
Do not call this a flush collider match, a playable checkpoint,
an opening animation, timer, or a tested route in game.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/gauntlet_forecourt.py -- /tmp/gauntlet-forecourt
```

The builder emits the forecourt-only GLB, the joined preview photos,
and geometry measurements. The far yard blocks and ground backdrop
are presentation only.

[Round 5 layout](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L315)
· [Ramp and board source](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/lab.js#L521)
· [E11c plan](../../docs/plans/kitchen-sink-v2/slices/E11c-gauntlet-courts-supervisor.md).

The wall caps sit 12 mm proud of the field so visible faces are not
coplanar. This changes neither gap width nor the ramp proof.
