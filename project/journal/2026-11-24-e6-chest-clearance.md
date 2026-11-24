# Band 6 payout chest: resolve a static mesh clip

At the first Round 5 Band 6 anchor, the existing Scrip
chest clips the archived half-wall return. The blockout
proxy is 0.9 m deep, but the pinned remastered GLB
includes a 1 m Blender local depth. Check its actual
vertices and triangles, not the proxy footprint alone.

Keep both positions in Three world X/Z: (112.593, 17.015)
and the candidate (112.593, 17.615). The second is −0.600 m
on Blender local Y. The two wall boxes keep the original
overall dimensions and yaw. The original anchor has
139 triangle pairs overlapping the return; the candidate
has none. All reimported chest vertices clear the wall end
plane by at least 123.361 mm on the return's local axis.
Floor pivot, facing, camera, light and other objects stay
fixed. See the receipt in project/layouts/e6-chest-fit.json.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/e6_chest_fit.py -- /tmp/e6-fit
```

This is a single static fit in a local stage, not a full
band layout or a relocation in the game. No new model,
payout, quest, collision or interactable state.
