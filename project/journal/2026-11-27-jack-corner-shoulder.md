# Which shoulder keeps Rook's first cut readable?

Run `node demos/mite-yard/jack-warning/native-corner.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT 3 inside left shoulder` against the pinned Fable build on loopback, then `python demos/mite-yard/jack-warning/corner-shoulder-proof.py REPLAY_OUTPUT_DIR` (Pillow). The runner uses the existing dock crate and trusted touch route. It freezes two ticks before damage, on damage, and two ticks after, then restores the native game between samples.

Each frozen state compares stock, 0.60 m left or right, 0.45 m up, and 0.35 m right plus 0.45 m up. The test camera pivots just enough to hold Jack's core at the same screen location. No change to FOV, animation, VFX settings, HP, or the touch movement basis. Every lens has weapon shown, hidden, then restored. Pixels changing by at least 16 in any RGB channel in a tight crop around the projected blade measure the weapon's on-screen contribution, including local post-processing, not its exact visible mesh area. Restored controls had zero such changes in each crop.

- Stock before / at / after damage: **371 / 164 / 161** contributing pixels.
- Raised-right: **444 / 233 / 224**. At damage the projected base-to-tip span grew from 25.4 to 30.4 px, while horizontal spacing between Rook's head and Jack's eye grew from 49 to 61 px.
- Raised only: **441 / 204 / 249**. Simply sliding right: **361 / 137 / 102**. Simply sliding left almost erased the sword at impact (**12 px**).

The local 0.24 m radius sweeps from the stock lens to the candidate offsets were clear of physics and drawn blockers in these three frames. This is not a live camera path or a full collision test. The higher-right view is the better next candidate than a pure shoulder slide, not a proven default. Test a smooth transition and return with the quieter impact enabled before an iPhone pass. Fable and the playable build remain unchanged; no private screenshots are in this tree.
