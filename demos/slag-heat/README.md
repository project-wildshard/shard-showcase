# E4 foundry slag cooling cue

E4 calls for six seconds of visible slag without light sources. This is
the presentation only. The caller supplies time, validated locations and
which patches should exist. No creature, damage, hazard spawn, terrain
queries or world installation. The original static donor GLB stays unchanged.

One Three InstancedMesh collapses the donor's six material primitives into
one shader material with per-vertex base and heat colors. Up to 12
instances use independent ages. No new mesh donor, textures, light
source, transparency, postprocessing or per-instance material clone.
The leading fracture is brightest at birth, becomes dark crust at
5.90 s, and is absent at 6 s. The batch compacts expired slots. No
coverage changes or real game-state decisions are made here.

The checked CPU path pins the donor by SHA-256, verifies exact transformed
bounds, 703 triangles, an ungrouped one-material batch, independent ages,
correct expiry and retriggers. A separate optional WebGL capture harness
is included; it was not executed in this workspace because Chromium
was not present. Do not treat the one-batch structure as measured GPU
performance or read the Blender portraits as browser/client footage.

## Reproduce

From repository root with Three 0.186 available to Node, Blender 4.3.2:

```sh
out=/absolute/scratch/e4-slag
mkdir -p "$out"
node demos/slag-heat/sample.mjs public/assets/wildshard-art/e4-ground-slag-decal.glb "$out/cpu.json"
cmp "$out/cpu.json" project/layouts/e4-slag-heat-proof.json
blender -b -t 8 --factory-startup --python-exit-code 1 --python demos/slag-heat/render.py -- "$out/cpu.json" "$out/photos"
```

Optional Chromium replay (esbuild, playwright, and Chromium installed):
prepare a local staging folder with `index.html`, bundle `preview.mjs`
to `preview.js`, and place the three GLBs named in `preview.mjs` under
`assets/`. Serve it with any local static server, then run
`node demos/slag-heat/check.mjs http://127.0.0.1:8449/ "$out/webgl"`.
Set `CHROMIUM` if using a system browser outside the Playwright cache.
The harness asserts one isolated rendered call for 12 patches and zero
after expiry. The stage uses the original bay shell and exact furnace
asset at the editorial local position from the cover-bay study.
