# Market awning: light breeze

Keep the WSC-PROP-005 freestanding stall and its existing static
export intact. Split canopy faces by material and height. Reuse the
same model-space rest vertices, UVs, corner normals and the original
embedded canvas and linen swatches. Only the fabric subset ships in
the alternate GLB; don't overlay it on top of the original canopy.

A single three-second keyframed clip bends the slack panels and hem.
On clean reimport the first and last poses match, 968 ridge or outer
vertices remain fixed at the tested peak, and maximum travel between
the two displayed peaks is 126 mm. These are visual animation checks,
not clearance, physical cloth, global wind or native placement checks.
The render stand uses the unchanged rigid donor geometry.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/market_awning_breeze.py -- \
  /absolute/scratch/market-awning
```

The alternate canopy is 269,708 bytes and 5,976 triangles including
the original embedded texture swatches. No new stall model, live
instance, skeleton or world interaction is added.
