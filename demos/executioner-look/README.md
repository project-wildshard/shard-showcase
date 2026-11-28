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
