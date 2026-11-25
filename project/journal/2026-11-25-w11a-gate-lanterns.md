# W11a · Warm approach light at Stable and West gates

Three copies of the existing wall lantern fit the approach faces of
the original stone piers: one at Stable and two at West. The proposed
left Stable lantern intersected the Lot 18 facade and was omitted. Each
installed fit uses 12 rays into the exact pier face and has no triangle
intersection with nearby geometry apart from the intended mount. They are mounted 2.95 m above the ground coordinate, more than
0.63 m outside the 12 m approach opening. The exact lantern and nameplate
GLBs and the regenerated town geometry stay unchanged (2,692 parity
entries). Temporary stages hide the old Stable sign lettering before
putting the already-reviewed nameplates back on the beams.

Each auxiliary preview spot aims down and inward under its lantern;
the center ray clears the fixture and the gate to its near-ground aim
point. Measured runs are 3.58–3.65 m. The Stable comparison locks camera,
geometry, and ambient blue-hour lighting, so the only changes are its single
lamp and lens emission. West uses the same design at the original
90° yaw, from a second 1.7 m eye-height approach. See the fit receipt for
world-space mounts, emitter origins and target positions.

No new mesh, native light rows, clock/weather hooks, visibility-distance
budget, or performance claims. The three authoring transforms are the
deliverable. Blender photometric settings are review values, not engine
intensities.

```sh
O=/tmp/w11a-gate-lanterns
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-town/build.py -- --output "$O/town"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/gate_lanterns.py -- \
  "$O/town/whole-town-editable.blend" "$O/review"
cmp "$O/review/w11a-gate-lanterns-proof.json" project/layouts/w11a-gate-lanterns-proof.json
```
