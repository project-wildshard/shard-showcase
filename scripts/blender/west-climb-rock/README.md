# West Climb Yard and The Rock: source-only static art WIP

From the repository root, use Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-climb-rock/build.py -- --output /absolute/scratch/west-climb-rock
```

The build checks two additional tracked donor hashes (WSC-PROP-011 and
WSC-PROP-044), regenerates the whole-town predecessor, and constructs the
Climb Yard and the Rock exterior without changing a predecessor mesh.
Generated Blender and GLB outputs stay outside the checkout; no private or
external dependency is needed. No fresh render is generated.

The six bridge endpoints and exterior mouth centers match the reviewed
historical layout (Raynos/project-wildshard-singleplayer ce1cf050b3, round-4
layout.js and lab.js buildClimb/buildRock, W8a/W9a). The bridge decks reach
6/10/14 m; the 16 m crown keeps the source zone envelope. The final approach
is shaped to the crown; as in the reviewed version, threshold skins sit 11 mm
above nominal walking planes. Native-scale donor cave arches describe the
exterior mouths only. No tunnel, hidden cache, collision, swing, traversal,
phone, runtime performance or production qualification; no new catalogue IDs.

Reimport QA checks the exterior and route geometry, while the fingerprint
compares the reviewed primitives. The only allowed raw difference is the
inherited W08 untextured arm UV exception (5.96e-8, already scoped by the
predecessor recipe). That check never modifies the exported asset.
