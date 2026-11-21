# West whole-town shell: source-only static art WIP

Rebuild with Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output /absolute/scratch/west-town
```

The driver rebuilds the tracked West zipline predecessor, then generates the
town geometry. No external files or downloads. All generated GLBs, Blender
natives and receipts stay outside checkout. The earlier W08 arm UV comparison
rule is restricted to the one already documented UV component on that
inherited untextured fitting (delta 5.96e-8). The checker never alters the
exported GLB; all geometry, winding, materials and transforms match exactly.

`layout.mjs` carries only the placement inputs read by the original seed-31
`townPlan` from Raynos/project-wildshard-singleplayer at ce1cf050b3:
`art/showcase-template/round-5-blockout/layout.js` and companion `lab.js`.
Round 5 retains the West placements from Round 4. Generated lot JSON must
match the reviewed bytes. The predecessor recipes pin their tracked model inputs.

The 120×120 m town shell includes six openings, 40×40 m plaza and 22 m landmark.
35 seeded residences, two shops, three To Let lots and two gatehouses are
batched as 42 lot meshes; the existing zip house and stable are retained.
Placement is sourced; appearance, roof and facade finish, and plaza fixtures
are authored art. No NPCs, game logic, collision, gameplay, phone or runtime
validation, or art release. This build does not render fresh images.
