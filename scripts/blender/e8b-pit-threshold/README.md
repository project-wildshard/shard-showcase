# E8b pit openings: shoulder lantern model and walk witness

Keep the exact pit center, radius, rim openings, +0.05 m floor and
two interior pillars. Two lanterns sit outside each opening on the
outer approaches, at local x ±3.55 m and z ±15.6 m. The four reuse
one ground-origin GLB. Its amber glass is cosmetic, not a runtime
light or a gate switch. The render paving and rubble are not exported.

Check the Blender reimports for no contact between the new model and
the existing shell. The motor test applies the exact GLB triangles
as static collision (flat surrounding terrain). Five lines each way
through the original openings keep their original headless replay
metrics with the lanterns inserted. Four separate shoulder approaches
stop at the new plinths; removing them clears the same four routes.

```sh
D=/tmp/wsc-e8b-shoulders
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e8b-pit-threshold/build.py -- "$D"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  scripts/blender/e8b-pit-threshold/check.mjs "$D/art-fit.json" \
  "$D/e8b-pit-shoulder-lantern.glb" "$D/proof.json"
cmp "$D/proof.json" project/layouts/e8b-pit-threshold-proof.json
```

The asset is an environment marker only. No Big Pallet model, damage,
pillar stun, scripted encounter, or live level/phone test is included.
