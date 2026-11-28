# Executioner look development

Not playable. The viewer opens one static Blender pose at a gameplay-like camera distance, then switches to close, profile and rear. No rigs, hitboxes or attack clips are loaded by this demo. The camera projection puts the figure at 241 px tall in 1280 × 720 Chromium and 293 px tall in 402 × 874 portrait Chromium. These are inspection views, not the game camera implementation or phone performance results.

From the repo root:

```sh
npm --prefix demos/forge-yard ci
blender -b art/actors/foundry-executioner/executioner-pose-study.blend --python-exit-code 1 \
  --python art/actors/foundry-executioner/export_look.py -- demos/executioner-look/look.glb 25
python -m http.server 5250
```

Open local `http://127.0.0.1:5250/demos/executioner-look/`. For browser proof, install Playwright Chromium in the Forge Yard dependencies, then create a local dependency symlink `ln -s ../forge-yard/node_modules demos/executioner-look/node_modules` (ESM resolution) and run `node demos/executioner-look/smoke.mjs`. The reproducible review export is ignored by Git. The exporter flattens the pose, decimates the geometry and approximates the Blender shader with vertex color plus PBR constants. A real skin, atlas-baked material stack and meaningful clips will be separate work.

## Shape experiment: fitted surfaces vs. reconstructed mesh

Generate a rest-pose sample and the normalized underlay with:

```sh
blender -b art/actors/foundry-executioner/executioner-pose-study.blend --python-exit-code 1 \
  --python art/actors/foundry-executioner/export_look.py -- demos/executioner-look/authored.glb 1
blender -b art/actors/foundry-executioner/reconstruction/sculpt-underlay.blend --python-exit-code 1 \
  --python art/actors/foundry-executioner/reconstruction/export_underlay_look.py -- demos/executioner-look/reconstructed.glb
node demos/executioner-look/compare.mjs
```

The experiment uses the same 1280 × 720 Chrome viewport, cameras, directional/ambient light, and untextured gray material. Silhouettes are 243 px and 241 px tall in the distance view. Their stances are not identical. The underlay has a better low-contrast adult silhouette in the shoulder and forearm, but the mask melts into the hood and the skirt joins into a single volume. Fitted geometry preserves the real mask opening, separate panels and boots, but the cloth drape, boots, and posture still need stronger human shapes. Do not promote the underlay directly. Carry its macro proportions into fitted geometry and use independent fabric/armor weights and separations. Use the same exact pose when evaluating a material-only change.
