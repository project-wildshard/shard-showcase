# W9b / WSC-PROP-049: cache chest with an opening lid

The original W12 exterior study stays unchanged. The opening model reuses
its authored mesh islands for the lid, corners, medallion, seals and body.
The new rear pivot splits the opening geometry from the fixed lock and base.
The long front latch needed its own split at the seam. The formerly solid
body was opened and fitted with a liner, lip and underside ribs. The tray
is empty; nothing here selects a reward or affects D26.

- Closed reimport envelope: 1.606 m wide, 1.161 m deep, .892 m high.
- Rear hinge `Cache_Lid`: glTF (0, .660, -.529) meters and rotation about X.
  One studio clip, `Cache open`, opens to −1.95 radians in 28 frames at 24 fps,
  with a brief closed hold. Static body and lock are separate from moving lid.
- Nine rays check that the opening exposes the liner floor. In six samples
  from mid-opening to fully open, overlapping triangle pairs are confined
  to the rear hinge/hardware zone. The closed seal, early contact and hinge
  intentionally overlap as part of the art; this is not a collision proof.
- 497,608 raw bytes and 17,842 triangles versus the original exterior's
  818,176 B and 16,421 triangles. Packed with quantized positions/normals,
  no UV stream needed, and clean reimport renders the exact packed variant.
  Repeat build matches bytes. Requires `KHR_mesh_quantization`.

From repository root, with Blender 4.3.2, Node, and version 4.5.0 of
`@gltf-transform/core`, `@gltf-transform/extensions`, and
`@gltf-transform/functions` available in a local node_modules directory:

```sh
WSC_GLTF_MODULES=/absolute/node_modules blender -b -t 6 --factory-startup \
  --python-exit-code 1 --python scripts/blender/showcase-studies/cache_lid.py -- /tmp/cache-art
```

The raw export is a temporary intermediate. The packed file and diagnostic
report are tracked; no .blend or duplicated donor is needed. The native
flag-driven chest renderer currently uses its own generated meshes;
inventory, flags, glint, opening state, collisions and cache placements
have not been connected or tested with this export.
