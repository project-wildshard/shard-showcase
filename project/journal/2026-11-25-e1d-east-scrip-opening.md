# E1d · An opening Band 1 Scrip chest

The tracked closed East payout chest remains byte-for-byte unchanged.
This optional successor reuses its author primitives and finishes,
cuts a recessed chamber below the gasket, and moves the lid assembly
around the existing rear hinge axis. The original 1.4 × 1.0 × 0.9 m
closed bounds are unchanged. There is no spill, coin model, reward
amount, placement edit, collision binding or claim state.

The 110,120-byte GLB has 1,827 triangles in a fixed shell and a
single articulated lid. One non-looping 0.90 s rotation clip opens
to 102°. Closed seating overlaps are part of the donor clasp and
gasket; after the clasp releases, all 18 sampled Blender frames
(10–27) have zero lid/shell triangle intersections. Twenty-five
top-down rays hit the open chamber floor at 98.562 mm. Three
reimport checks 217 samples, a stationary rear pivot, monotonic
rotation, identical closed extents, and a clear open-center ray.

```sh
O=/tmp/e1d-scrip-opening
WSC_PAYOUT_OPENING=1 blender -b -t 6 --factory-startup \
  --python-exit-code 1 --python scripts/blender/showcase-studies/east_payout_chest.py -- "$O"
node project/check-east-scrip-opening.mjs
```

Set `WSC_PAYOUT_PROOF_ONLY=1` to skip renders. Running the original
command without `WSC_PAYOUT_OPENING` reproduces the old GLB and
receipt exactly. The matched screenshots show the reimported
endpoints, not an engine interaction.
