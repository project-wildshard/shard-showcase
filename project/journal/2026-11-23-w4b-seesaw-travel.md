# W4b see-saw: flat-ground and brace fit

WSC-PLAN-003 already has a fixed stand and hinged deck. This pass asks what
the shipped art would hit under tilt. The two test poses reuse its exact GLB
(SHA-256 asserted in the script) and its 1.47 m pivot. There is no donor copy
and no additional runtime mesh.

- Both ±10° poses have 211 mm between the lowest deck vertex and level
  ground. No triangle crossing outside the axle/boss envelope was detected
  at 0.25° steps across that range.
- The historical 0.2 rad visual pose leaves 38 mm to the floor. At the
  sampled ±11.75° poses, the deck intersects the orange A-frame braces
  outside the joint envelope while still about 4 mm clear of the floor.
  At ±12° it also penetrates the floor by 25 mm. Estimated flat-ground
  crossing is ±11.785°. These are measured samples, not a continuous sweep
  proof, a recommended physics stop, or a runtime collision setting.
- The static check uses the reimported render triangles and ignores
  intersections confined to the 0.30 m-radius, 1.49 m-half-length axle
  cylinder. It does not cover colliders, players, crates, a load-bearing
  joint or contacts on non-flat terrain. No native behavior was changed.

Reproduce from the art branch:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/seesaw_fit.py -- /tmp/w4b-art-fit
```

The output contains two JPEGs and validation.json. The shop floor and
legends are presentation only. The exact authored mesh remains at
`public/assets/wildshard-art/wsc-plan-003-hinged-seesaw.glb`.
