# W3a · Range Records display face

The original WSC-PROP-027 has a fixed stopwatch readout. This removable
petrol enamel face covers that readout without editing the timer
housing, amber rim or separate board lamp. It lists the plan's three
drills (Six Dummies, Lanes, Rifle). No fictitious scores are baked;
all three values are unset. The dashes live in a separate named mesh,
`RangeRecordUnsetValues`, that a real record display can hide. Each
right-aligned value anchor is in the fit receipt.

The reimported 68,376-byte GLB measures 1.608 m across its front face.
It is already offset for the original timer's origin: use the original
pose, not a second placement adjustment. There are 1,426 triangles,
six material primitives and no textures or embedded lights.
The back is 2 mm clear of the nearest original readout front.
27,378 rays from three review viewpoints cross the new face before
reaching a sampled vertex of the original title or digits. This is
a geometric occlusion check, not an on-device readability test.

```sh
out=/tmp/w3a-range-record-face
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/w3-range-record-face/build.py -- "$out"
node scripts/blender/w3-range-record-face/check.mjs "$out"
```

Set `WSC_METADATA_ONLY=1` to skip the two renders. The preview
uses the original housing and lamp with a studio pedestal and lighting.
Only the overlay is exported. No live records, persistence, drill
completion, runtime lettering or geometry install.
