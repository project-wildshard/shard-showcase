# West props · wood fibre and oxidized hardware

WSC-PROP-020 cable spool and WSC-PROP-021 timber barrel retain their exact export meshes, winding, seams and proportions. This is a matched Blender material proposal. The only changes between images are 15 material slots: timber gets directional fibre and varied abrasion, and selected iron hardware gets oxide islands with separate roughness and fine bump. Each donor uses one shared local texture frame so adjacent mesh sections line up. Rope, wire, nails, and labels are unchanged.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/timber_hardware_materials.py -- /tmp/timber-review
```

The script pins both donor GLBs and tests a world-geometry/placement signature. `WILDSHARD_VALIDATE_ONLY=1` verifies the receipt without rendering; `WILDSHARD_SAVE_BLEND=1` saves an optional editable worn-state Blender scene outside the repository. Lighting, camera, framing, and geometry are constant across the comparison. The node recipes use no textures or network links. They are not baked glTF materials, and no native asset or in-game lighting was changed. If this look is accepted, UV and bake a portable texture set as a separate step.
