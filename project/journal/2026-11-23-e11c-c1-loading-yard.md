# E11c C1 Loading Yard, a static art pass

This is the missing first Gauntlet court under WSC-SCENE-007, not an
edit to the C2 Pit. The audited Round 5 footprint is 82 × 42 m: a 34 m
deep floor plus an eight-meter-deep entry terrace, +3 m. The separate
G1 passage starts at the south wall. D1 and D2 retain their west/east
center coordinates and recessed closets; the facade and lamp design
are art proposals. Cover keeps two nominal 1.1 m half walls, three
piles of cargo, and a six-meter service pier at their Round 5 positions.
E11 is a palette reference to the later C2 wave, not the C1 layout.

The compact GLB carries only the architecture, dock recess shells,
floor marks and hard cover, with a local origin at world (55, 0, 163)
in game x/y/z. The entry ramp runs are art refinements to connect the
terrace edge to the floor. The G1 transfer rises to the current C2
north ledge’s height of +2.5 m; the two courts were not joined in a
native world. Six side recess rays and three G1 approach rays check
opening geometry in the reimported mesh, not player collision.

The pre-existing `haul-crate.glb` is pinned by hash and linked as
15 staging instances, scaled to three 2.4 m stack silhouettes.
The crate faces are not copied into the architecture export. Keep both
the layout JSON and the builder to regenerate the staged composition.
The outer ground, door labels and illumination are preview-only.
No wave, spawn, gate state, or other gameplay was implemented.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/gauntlet_loading_yard.py -- /tmp/wildshard-c1
```

[Active E11c plan](../../docs/plans/kitchen-sink-v2/slices/E11c-gauntlet-courts-supervisor.md)
and [original Round 5 C1 rows](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L324).
