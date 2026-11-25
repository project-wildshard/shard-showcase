# W0b: closed storefronts for the three reserved lots

W0b's Main Street has three signed TO LET fronts. The original signs and ochre awnings stay in place; these removable overlays close the existing vitrines with four sections of painted pine, dark iron straps, and bronze hardware. They do not add a shop inventory, interior, door, collider, or service.

The 14 m and 16 m labels refer to the **host lot widths**, not the mesh spans. The shutter spans are 7.72 m and 8.80 m. Each GLB uses a grade-level origin on the center of the original facade body plane and faces local glTF −Z. Use the exact world-local placements in `project/layouts/w0b-closed-front-fit.json`; all three retain 25.5 mm or better setback from their lot line, behind the 12 m street boundary. The meshes, shutters and any signs in the background were reviewed as art only. No old town files are replaced.

## Rebuild

```sh
d=/absolute/scratch/w0b-closed
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output "$d/town"
blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/west-closed-fronts/build.py -- "$d/town" "$d"
for w in 14 16; do
  cmp "$d/w0b-closed-front-${w}m.glb" "public/assets/wildshard-art/w0b-closed-front-${w}m.glb"
done
cmp "$d/proof.json" project/layouts/w0b-closed-front-fit.json
blender -b -t 6 "$d/closed-front-review.blend" --python-exit-code 1 --python scripts/blender/west-closed-fronts/render.py -- "$d"
```

The town's existing semantic parity check pins the rebuilt donor separately. The fit test uses the exact reimported GLBs, checking 100 street-facing rays per facade versus the original glass region and nine higher rays per facade so the canopy and fascia stay untouched. The viewport images use the exact reimported overlays, not new baked town exports.
