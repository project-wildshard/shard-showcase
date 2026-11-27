# Turn a blocked ram into a sword opening

Keep the same staged low cover and native Fable fight from [the cover bench](2026-11-27-jack-charge-cover.md). When Jack locks its aim, start sprinting around the crate’s side, then use a light sword attack once the ray at waist height to Jack clears. The second run waits 46 frames into the recovery before starting the same route. The fixture uses the ordinary movement, sprint and attack inputs without moving an actor directly after setup. No roll, invulnerability, forced charge, damage tuning or new rigs.

| Timing | Rook HP | Jack at sword contact | Light hit after crash |
|---|---:|---|---:|
| Move on heading lock | 204 → 204 | Recovering, 132 → 119 HP | 0.33 s |
| Move 46 frames after crash | 204 → 204 | Already chasing, 132 → 117 HP | 1.63 s |

The late hit still lands, but it misses the protected opening: Jack left recovery at 1.12 s and still had all 132 HP. The important result is when the attack lands relative to recovery, not the damage difference. The early cut is normal `sword1`, not the perfect-dodge counter. The stock hit flash in the capture still obscures some armor; do not read the capture as precise blade-to-surface proof.

Reproduce with `node demos/mite-yard/jack-warning/charge-cover.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT riposte`, using the same loopback build as the cover bench. Each run used independent disposable portrait Chromium storage. These are scripted native keyboard controls, not a physical iPhone run. Fable and the playable builds were not edited.
