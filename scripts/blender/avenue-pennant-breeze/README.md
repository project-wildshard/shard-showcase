# W11a / WSC-PROP-015: avenue pennant breeze

Optional lighter version of the original town pennant string. Drops the tiny rope twists and thread-relief geometry, retains the main rope and cloth shapes and colors, and adds a three-second loop to the existing silhouettes. Use the same local origin and mounting transforms as the original. The posts in the comparison are render-only and not included.

The export has five primitives and no textures. Against the 387,620-byte / 19,811-triangle donor, the animated export is 238,180 bytes / 6,256 triangles. In five below-mount neutral-pose views the sampled projected silhouette overlaps the original by 98.87–99.11% (intersection over union). The neutral cloth vertices match retained donor positions within 2 μm; the rope and 341 upper edge vertices stay pinned. Lower tips move up to 182 mm from neutral. Reimported clip returns to the same pose at three seconds; independently verified with Three.js GLTFLoader and AnimationMixer, including an unchanged carrier. The two photos show frames 5 and 41 at 24 fps from the same camera.

Use the exact original for close hero shots where the stitching matters. The new alternative has no automatic distance selection, clock/wind connection, production placement, or change to the original GLB.

Rebuild from repo root with Blender 4.3.2 and the existing Three.js dependencies; set `WSC_NODE_PROJECT` to their package root if needed.
```sh
d=scripts/blender/avenue-pennant-breeze
out=/tmp/wsc-pennants
blender -b -t 5 --factory-startup --python-exit-code 1 --python "$d/build.py" -- "$out"
node "$d/check-three.mjs" "$out/wsc-prop-015-pennant-breeze.glb"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$d/render.py" -- "$out"
```
Two fresh builds match byte-for-byte. Details: `project/layouts/w11a-pennant-breeze-proof.json`.
