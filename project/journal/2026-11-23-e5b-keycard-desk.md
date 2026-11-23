# November 23 · E5b foreman desk and Vault keycard

Two props for the WSC-KIT-006 family. E5b places the keycard on a desk
in the foreman's hut. The exterior shed (WSC-PROP-065) and shipping
containers (WSC-PROP-058) have existing meshes, so this pass does not
remake them. The card is a fictional pickup with the keyhole marking
used on the Training Vault portal. It exports separately so it can
move independently of the desk.

The desk has a 1.78 m top, painted drawer fronts, a ledger, and a
work lamp. It is 113,836 bytes / 1,936 triangles. The separate
14.3 × 8.7 cm card is 28,412 bytes / 440 triangles. Both use local
pivots and require no baked textures. The generated previews use
the exact reimported GLBs; the spot by the card is studio lighting.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/keycard_desk.py -- /tmp/e5b
python scripts/blender/showcase-studies/check_keycard_desk.py /tmp/e5b
```

Set `WSC_KEYCARD_RENDER=1` for the desk view and card close-up. There
is no pickup, alarm, patrol AI, Vault unlock, shed fit, or placement
change. The kit remains incomplete.
