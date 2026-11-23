# E04 foundry ember loop (WSC-PROP-057)

A standalone animated visual for the existing furnace, not a new
furnace export or a simulated fire. E04 provides the warm foundry
look. The original furnace GLB remains byte-for-byte unchanged.
The preview places the effect root just forward of the mouth in
Blender and adds separate studio light. That light is not in the
download, and the authored root has no level transform.

The GLB is 32,312 bytes: 18 motes reuse two tiny emissive meshes,
with one three-second clip and 36 translation/scale channels. The
validator checks that all channel endpoints match exactly, with
no textures, skin, or required extension. Fading the size nearly
to zero at the wrap conceals each looping reset. Two stills are
rendered from the reimported animation.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/foundry_embers.py -- /tmp/wsc-embers
```

No native particle system, heat, hazard, physics, audio, collision,
gameplay lighting, or mobile performance benchmark is included.
