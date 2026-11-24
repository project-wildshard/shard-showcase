# W9b · Two ground-level west vistas

Round 5 `ce1cf050b3` supplies the NW/SW discovery anchors (−229,0,−229) and (−229,0,229). Its lab draws the actual bench proxy 2 m to the positive world-Z side of each anchor. The setup holds those original coordinates apart rather than moving either marker to the render camera. See `art/showcase-template/round-5-blockout/layout.js` at line 295 (blob `5d019a020361c47187ec889f2bc947f82cd9f98a`) and `lab.js` at line 771 (blob `51a3b4bef1f2d4891172164d10893d98d450a3b9`).

The current lookout bench is instanced at those two exact proxy positions. One optional 5.58 m flush granite pad supports both; its rim leaves 5.21 m and 3.21 m clear of the historic perimeter strip, respectively. The NW pad is 15.58 m from the 12 m oval's outer track edge. The SW pad is 7.43 m from the reimported bowl footprint. Blender reimport also checks both existing benches' ground contacts. Only the pad is added to the asset folder, not the two assemblies.

Both art cameras sit 1.48 m above the original ground level. NW frames the oval bend and starting gantry. Looking directly into the SW bowl fails: the unscaled imported 3.5 m lip blocks the ray to the floor. An oblique camera instead looks past the lip and retains the park silhouette. The candidate center ray is checked separately with the bowl and in the full staging scene. Sightlines, pad clearances and anchors can be read in `project/layouts/w9b-corner-vista-proof.json`.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/corner_vista_pair.py -- /tmp/w9-corners
```

Use `WILDSHARD_VALIDATE_ONLY=1` for the reimports and geometry-only checks without rendering. The pad is 26,036 B / 598 triangles; Blender rebuilt it byte-identically and Three loaded the same bounds. Existing donors are pinned and not copied. Terrain dressing, paths, lighting, vegetation, and horizon are for the images, not level geometry. No bench interaction, discovery, movement, collision, rewards, or native camera edits.
