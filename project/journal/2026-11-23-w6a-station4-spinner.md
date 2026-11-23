# W6a: standalone Station 4 spinner | WSC-KIT-002

The existing six-station source and gallery stay unchanged. This file
extracts the four Station 4 objects from the pinned Movers rebuild
script: pedestal, 9 m disc, center axle and sweep arm. The disc top is
6.00 m. The source platform ends 0.30 m below the disc. A separate
fixed decorative collar bridges that gap in this standalone variant.

The neutral export matches all four original dimensions and relative
placements. Origin is ground center; its original Blender translation
is (-147, 103, 0) and its glTF world translation is (-147, 0, -103).
The separate named `Movers_DiscYaw` and `Movers_ArmYaw` nodes turn around
local glTF +Y. The former carries only the disc; the latter carries the
axle and sweep arm. The pedestal and collar do not move.

The 75,812-byte, 1,176-triangle GLB is a blockout articulation study.
In Blender reimport the first adjustment changed only the disc subtree
(+45°); the second changed only the arm subtree (+115°). Teal arrows
in the comparison are studio marks, not part of the GLB. There is no
baked animation, gameplay timing, rotating deck carry, push/collision,
course entry, placement, or D21 checkpoint behavior.

From the repository root in Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
 --python scripts/blender/showcase-studies/station4_spinner.py -- /tmp/spinner
```

The script extracts only the original station factory definitions and
four creation statements. The geometry report and editable extraction
are tracked. No combined park mesh or scratch project is needed.
