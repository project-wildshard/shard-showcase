# E7b: night-shift headlamp and chevrons

The E7b look calls for an amber cosmetic headlamp and hi-vis accents.
This batch adds two reusable parts, not a partial robot:

- `e7b-headlamp-beam.glb`: 3,112 B / 80 triangles. Two crossed
  cards, 2.72 m long, with radial and far-edge fades in RGBA
  vertex colours. The origin is at the socket, forward is glTF −Z.
- `e7b-hi-vis-chevron.glb`: 11,020 B / 144 triangles. A small
  patterned enamel panel with a local centre origin.

The beam's portable GLB is unlit and alpha blended. Additive
blending is a Three.js material override, not a feature of the
export or proof of native shard integration. The supplied Three
check applies it to the exact reimport with depth testing on and
depth writes off and verifies the fade and absence of any light.
The Blender review shot gates the cosmetic emission to camera
rays; it does not light the rig, cards or floor.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/night_shift_vfx.py \
  -- /tmp/e7b-night-components
node project/check-night-shift-components.mjs
```

Set `WILDSHARD_VALIDATE_ONLY=1` for export and Blender reimport
without the renders. See [asset receipt](../layouts/e7b-night-shift-vfx.json).
The stage uses a generic sample socket, not any new creature. No
palette swap, variant binding, real light, respawn or native deploy.
