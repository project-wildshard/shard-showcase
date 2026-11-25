# W0b · Stable, Movers and West Gate nameplate fit

The three remaining faces in the existing six-sign kit fit at
their archived Round 5 gate centers, facing back into town.
Stable and West use the original rebuilt timber boards. At
Movers, the original piers had crowns but no lintel, so this
adds one removable oak header with blue steel straps.

| Gate | Round 5 x/z | Clear width at existing piers | Frame spare above and below |
|---|---|---:|---:|
| Stable | −36, −60 | 12.0 m | 155 mm |
| Movers | −95, −60 | 10.4 m | 85 mm |
| West | −128, 0 | 12.0 m | 10 mm |

Four mounting pads per gate pass five actual triangle-ray
samples each, and 145 rays per gate clear the measured beam
and pier envelope between 0.25 m and 4.5 m above ground.
The header overlaps each original Movers crown by 1.925 m in
plan along X. It weighs 47,272 bytes with 708 triangles and
four material draws. No textures. Source pivot is centered
on the main beam, 0.4 m above the seat plane.

Existing architecture and plaque kit files are unchanged.
Stable's old overlap-prone face and lettering are disabled
for these renders only; its timber backing and exterior
return sign remain. The 10.4 m Movers clear opening is the
existing pier geometry, not the wall's nominal 12 m break.
Nothing here changes native routing, collision or placements.

```sh
out=/tmp/w0b-north-west
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-town/build.py -- --output "$out/town"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/town_north_west_gate_fit.py -- \
  "$out/town/whole-town-editable.blend" "$out/fit"
node project/check-movers-header.mjs
```

Set `WSC_METADATA_ONLY=1` for the second command to skip the
three matched-height renders. Archival layout: Round 5 blob
`5d019a020361c47187ec889f2bc947f82cd9f98a`. The whole-town
build must pass its existing normalized semantic-parity check.
Only the new header, recipe and fit receipt are committed,
not the town bake or any private scene.
