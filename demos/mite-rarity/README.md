# E7a: Steel trim and gold stencil on the existing Crate Mite

E7a calls for steel on the uncommon Mite and gold stencils on the rare.
Here are two material-only presets for the 1,734-triangle yard rig.
Common stays exactly as shipped in the prototype. Uncommon preserves
the powder coat and changes four trim/hardware slots. Rare darkens the
shell and makes the existing stencil and accents gold. Both leave the
cyan lens and its material exactly as they were.

`palette.json` is the only new visual data. The optional
`KHR_materials_variants` build adds 2,172 bytes of JSON to the existing
asset, with no second skin, mesh, buffer, texture, or clip. A reader
without the optional extension still loads the common look. The generated
GLB is deliberately not committed as a second copy of the donor's data.

The donor binary chunk is byte-identical. Removing only the variant
extension and new materials gives back the exact original glTF document.
Three loads all 11 skinned primitives and seven joints, selects and
reverts both finish mappings, then replays all 11 existing clips and
matches all 33 sampled skeleton poses. Images show common, uncommon
and rare left to right in matched Blender light and rest pose. The second
frame is 402 × 874 at a 10 m ground setback with 80° vertical FOV;
it is not a phone playtest or HUD capture.

This is a visual variant only. No additional actor, rarity roll, drop,
extra part, damage, runtime integration, or new clip. Night variants
and attack cue materials are left alone.

```sh
T=/tmp/wildshard-mite-palette
python demos/mite-rarity/build.py "$T"
node demos/mite-rarity/check.mjs "$T/e7a-mite-rarity.glb"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/mite-rarity/render.py -- "$T"
```

The check uses the repo's Three install. See
`project/layouts/e7a-mite-rarity-proof.json` for the exact result.
