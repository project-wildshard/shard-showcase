# Whole-West orientation: source-only static art WIP

From repository root, use Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-orientation/build.py -- --output /absolute/scratch/west-orientation
```

This recipe regenerates the reviewed Range Gate scenery predecessor using
tracked inputs only. All new West orientation geometry is procedural, with
no added donors or duplicated binaries. Output stays outside this checkout.
The recipe does not render fresh images or add catalog entries.

Historical placement sources: ce1cf050b3 round-five layout.js and lab.js
buildGround(), W0a road apertures, W9b west corner vistas. The authored road
joins a retained apron, and the West-only strip and corner seats leave the
east/seam and outside-cell geometry untouched. The two corner pads are
visual only. Range is pedestrian scenery, and the Rock is exterior-only.

Native and reimport checks preserve inherited mesh signatures, sample the
entry aperture and artery through the apron, bound additions to the West
cell portion, and assert corner and inherited zip/Hover/Yard/berm anchors.
Semantic comparison permits only the already scoped W08 untextured arm UV
exception (5.96e-8); the emitted GLB is unchanged. Static art WIP only,
not gameplay, collision, traversal, performance or W12 qualification.
