# East plant pot distance model | WSC-PROP-056

The existing full-detail potted foliage was already tracked. Reimport
confirmed 11,068 triangles and 232,684 bytes. The near model is the
unchanged `wsc-prop-056-plant-pot.glb`, SHA-256
`17ecd61ec7a0169370fc708f4879df210bcec4eeeb2a57ad0b73c821234e8c09`.

Built one simplified representation, preserving the dark spun pot, bright
rim, loose radial silhouette, ground origin and height. The first test
was too thin and the pot body was narrower than the donor; measured donor
dimensions informed the second pass. The final measured bounding boxes in
Blender X/Y/Z are 1.115 × 1.036 × .971 m near and 1.054 × .955 × .967 m far.

The distant model uses 680 triangles, 53,604 bytes and one indexed glTF
primitive with vertex color and no textures. That's 94% fewer triangles
and 77% fewer raw bytes than the near file, not a runtime benchmark.
The lower detail model is intentionally not a full-detail replacement.
No LOD switch distance, fade or placement has been tested.

From the repository root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/plant_pot_far.py -- /tmp/plant-pot
```

The script rebuilds the distance GLB and renders both GLBs after reimport.
