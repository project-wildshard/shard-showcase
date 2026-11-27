# Rook's lethal cut: native collapse, rewards, and cleanup

Run `node demos/mite-yard/jack-warning/native-corner.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT 3 inside left finish` against the pinned Fable build on loopback, then pass its output directory to `corner-finish-proof.mjs`. Prepare Pallet Jack at 8 HP at setup (native healing brings it to 8.77 before the swing). Do not write enemy health, player movement or rewards after setup. The trusted touch runner uses the existing dock crate and native first light cut.

- Tick 135: the native ram hits the existing crate. Tick 154: trusted tap on the sword button. Tick 165: sword1 reduces Jack to zero, ends targeting on the same tick, and records one normal level-4 Pallet Jack kill, one +22 XP award, and one scrip drop. Rook remains at 204 HP. Scrip drop is not tested collection.
- Tick 186: the existing death pose is mid-collapse. The enemy is still drawn but cannot be targeted. Tick 203: the breakup effect fires once and the rig leaves the live enemy list and the scene. That is 38 browser-simulation ticks after the hit (about 0.63 seconds, including hit-stop/scaled updates), not a new animation duration.
- The replay continues through tick 225: no duplicate XP, drop, breakup, or removal; no stale scene body or target. In the frames, the lethal flash obscures the initial pose but the later tilt is legible. A useful next readability check is lethal feedback versus the rewards already visible during the fall, not a replacement model.

This verifies a staged low-health end of the encounter in portrait Chromium, not the entire fight from full health or an iPhone playtest. No native source or playable build changed; private captures are not part of the repository.
