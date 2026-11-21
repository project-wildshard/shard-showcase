# Range Gate pedestrian scenery: source-only static art WIP

From the repository root, use Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-range-scenery/build.py -- --output /absolute/scratch/west-range-scenery
```

The build regenerates the tracked Physics Yard predecessor and the reviewed
pedestrian landscape. All additions are procedural; there are no additional
donors or private inputs. The output stays outside this checkout. The recipe
does not render fresh images or add catalogue entries.

Placement follows the West map footprint and east pedestrian path at
ce1cf050b3. The added visual earth forms, garden routes, seats, stone edges,
plantings and wayfinding are fictional scenery only. Nothing recreates
equipment or a functional range layout. The inherited scenery is unchanged.
No gameplay, traversal, collision, performance or real-environment claims.

The native and reimport checks preserve predecessor meshes and pedestrian
route and inherited placement anchors. Semantic comparison allows only the
previously documented untextured W08 arm UV exception (5.96e-8). The actual
GLB remains untouched. This is static art, not runtime qualification.
