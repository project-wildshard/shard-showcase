# W6b · Moving rubber tread, fixed arrows

An opt-in Three r186 material adapter for the exact original
`wsc-prop-037-conveyor-module.glb`. It touches just the three named rubber
primitives, assigning U from local X (1.32 m per repeat) and multiplying
their existing rubber color by a 512-byte procedural tile. It clones
geometry/materials to avoid mutating other instances. It adds no triangles,
does not move any vertex, and leaves the seven non-rubber primitives and
separate static arrows untouched. It does not add a source texture file.

Call `attachTread(THREE, root)` on an instance, then
`handle.setTime(seconds, localSpeedMps)`. A phase crest moves with
`localSpeedMps`; the exact existing poses 0/π/0 make the calibrated world
X speeds −3/+4/−5 m/s. The numbers are borrowed from the headless bench,
not asserted to exist as native engine rows. Use `handle.dispose()` to
restore the original mesh/material references. Do not attach twice to
the same root. There is no phase flash, emissive surface, crate motion,
player physics, deployment, or device performance result.

From repository root, use a project that resolves pinned Three r186:

```sh
T=/tmp/conveyor-tread
D=demos/conveyor-tread-look
mkdir -p "$T"
WSC_NODE_PROJECT=/path/to/pinned/node/project node "$D/proof.mjs" "$T/proof.json"
node --input-type=module -e 'import {treadTile} from "./demos/conveyor-tread-look/tread.mjs";process.stdout.write(treadTile())' >"$T/tile.rgba"
blender -b -t 8 --factory-startup --python-exit-code 1 --python "$D/render.py" -- "$T"
```

The proof reimports the exact original GLB into Three, checks every rubber
vertex's UV, phase speed/wrap and cleanup. The Blender stills use the
exact same tile/mapping at fixed times. The optional browser harness
`preview.html` can be served locally beside `tread.mjs`: put the installed
Three package under `vendor/three`, and the original conveyor-module and
conveyor-direction GLBs under `fixtures/`. Query `?t=0&view=close` for
a still, or omit `t` for the visual loop. The visual proof here is Blender
plus the headless Three CPU checks, not a browser or phone FPS test.
