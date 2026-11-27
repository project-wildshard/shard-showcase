# Keep the compact countdown through the whole opening

A staged, native Rook counter against a normal Pallet Jack runs to roughly 99%, 50% and 25% of the Broken window remaining. At each phase the default reference camera, time, damage, HUD and geometry are frozen. We compare the stock timer with a version centered on the full dark track. Both track and arc scale to 58%; the remaining arc uses 65% gold alpha. The exact native head sprite scales and moves with the shrinking arc. Its countdown order and fractions are unchanged, unlike a general flash reduction or deleting the ring.

| Flashes setting | Near opening: stock → compact | Half: stock → compact | Quarter: stock → compact |
| --- | ---: | ---: | ---: |
| Default | 8,220 → 4,072 | 3,105 → 884 | 1,453 → 410 |
| Zero | 8,265 → 4,204 | 3,100 → 883 | 1,637 → 493 |

Values are bright-gold pixels (R ≥ 235 and G ≥ 196) in the same local ring crop for the two views, not perceived brightness or absolute luminance. The paired reductions range from 49% to 72%. At half and quarter the full track is about 74 CSS px wide instead of 127. The dark track, shortening arc and moving head are distinct in those captures. Near the opening the stock camera can still crop Jack and the active combat labels can overlap the smaller ring. The effect does not solve these issues, and does not change other body, sword or contact effects.

Run `native-probe.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT gauge-cycle none` and again with `zero`, then pass the two output paths to `broken-cycle-proof.py`. The instrumentation rejects anything other than a single current Broken actor and its exact head; it does not tune vulnerable stuns or global visual effects. This checks only a scripted 402 × 874 Chromium replay. No assets, reference captures or Fable code changed or published; no automated claim of physical-device readability.
