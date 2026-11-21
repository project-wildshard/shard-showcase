# West zipline continuation: static art WIP

From repository root, rebuild with Blender 4.3.2:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output /absolute/scratch/west-zip
```

The driver verifies four additional tracked model hashes, regenerates the W08
tower, roof, pad and cable fittings from those models, and builds the cable
curve and tie-downs procedurally. Cable fittings are extracted by the historical
BMesh vertex selection, not a hand-modeled substitute or a private input.
The tracked parent recipe regenerates the prior West stages. Generated GLB,
native files and parity receipt stay outside the checkout.

The fingerprint compares geometry (positions, normals, UVs and winding),
materials and instance transforms against the reviewed assembled zipline.
The reviewed export and clean rebuild differ by one UV value on one untextured
tie-down arm (0.3125000596046448 versus 0.3125, delta 5.96e-8). The comparison
normalizes only that exact UV pair in a temporary copy; positions, normals,
winding, materials, transforms and all other UVs compare exactly. The raw
fingerprints remain recorded. No exported geometry is altered by the check.
It does not require identical exporter byte order. This recipe does not render
new frames or claim updated visual approval.

The historic route is about 99 m horizontally, with endpoints at map
(-212,45,-34) and (-115,14,-16.5). W08's 1.2 m illustrative sag is not
the historical runtime sag. The tower mesh uses the original roughly 6 m
placement offset to align with the pinned attachment, not a source-accurate
tower base. Street and roof dressing remain illustrative. No rider, motion,
collision, gameplay, phone or runtime signoff. No new catalogue IDs.
