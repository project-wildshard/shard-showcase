# W0b Avenue service cover · WSC-MODULE-004 accessory

A small shoulder-side rainwater cover: blackened cast iron in a warm
limestone mount, open angled slots over a dark recess, and four worn
bronze fasteners. One origin-centered 0.468 × 0.780 m mesh can be
instanced on either side. The exact paving, planter and previous litter
exports are not modified. No new catalogue ID is needed.

Two review placements in metres at the identity paving tile in Three.js
coordinates: `[2.338, 0, 0.74]` (yaw 0) and `[-2.338, 0, -1.36]`
(yaw π). Each GLB is 4.0 mm beyond the paving footprint; the highest
fastener sits 4.5 mm below the original curb's maximum. This does not
specify a trench cut or a finish grade for the assembled town scene.
The review's neighboring tiles, shoulder and planters are staging only.
301 centerline checks in the reimport found 148 openings to the recess
and 153 hits on bars. The textureless GLB is 72,816 bytes, 1,280 tris and
five material primitives. No collision, water behavior or game install.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/avenue-service-cover/build.py -- /tmp/avenue-service-cover
```

Set `WSC_METADATA_ONLY=1` to skip renders. The rebuild and fit receipt
both compared byte-for-byte with a second isolated build. Exact receipt:
`project/layouts/w0b-avenue-service-cover-proof.json`.
