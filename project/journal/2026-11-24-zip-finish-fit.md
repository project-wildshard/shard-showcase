# W7b West zip-house finish pad fit

The exact West route rebuild still passes its reviewed semantic fingerprint.
The staged pad was not touching the cyan deck. Center gap is 86 mm; around
the selected bearing points it is 23.5 to 33.0 mm. Six recessed metal shoes
use the local mesh height at each end rather than bridging stepped planks.
Each seat is checked at 32 additional points against each donor surface.
Sampled inset is 4.0 to 9.7 mm. After evaluating the bevels, the existing
pad and flange have only 8.4 mm between their projections on the cable
axis. The closest added shoe is 234.4 mm back from the flange on that axis.
These are projection margins, not an operational clearance qualification.

To rebuild, run the pinned `scripts/blender/west-zip/build.py` first. Then:

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/zip_finish_fit.py -- \
  /absolute/scratch/west-zip /absolute/scratch/seat-study
```

The 21,992-byte GLB holds 288 triangles and two materials, with no images,
textures, animation or native collision. Place the export at the existing
pad origin (map -115, 12.42, -16.5) without an additional rotation. Donor
models and route endpoints remain unchanged. The diagnostic render hides
the pad only to reveal the shoes; it is not an alternate route. The older
Gold marker and every gameplay checkpoint are out of scope.
