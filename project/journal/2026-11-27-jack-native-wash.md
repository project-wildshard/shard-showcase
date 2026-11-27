# Same-frame counter A/B: body flash is only part of it

Replayed the stock Fable counter in the pinned local build, then rendered the same frozen frame twice at 402 × 874. All gameplay and camera state was unchanged: Rook 204 HP, Jack 84 HP, same simulation time, position and yaw. In the second render, only the Jack material flash uniform was capped at 0.22 instead of the measured 0.95917. No camera, effect, or game setting changed.

Less of the Jack is washed white, but the gold effect still dominates the left half of the contact area and the Jack remains cropped off the left edge. **Do not call the body cap a complete fix.** Separate the gold counter/break feedback and portrait camera composition before asking for an iPhone verdict. Do not change gameplay hit rules based on this comparison.

The checked-in probe now loads either CommonJS or ESM Playwright entry points; the packaged fixed import successfully repeated the 48-damage rising counter. Follow the [native replay directions](2026-11-27-jack-native-combat.md) and add `wash` as the last argument for the material-only paired render and a fixed-camera receipt. The captures remain private scratch outputs; no Fable files or visuals are committed or deployed. No live game patch or device test.
