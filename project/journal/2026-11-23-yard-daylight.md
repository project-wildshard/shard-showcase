# Paint a clear sky over East 01

The original East 01 board has a blue sky and soft cloud strata above the orange gantry; the browser yard had one solid fill. The sky now moves with yaw and pitch, but not with the player, and keeps the clouds clear of the brightest fight cues. The fallback paints the sky and a few feathered cloud silhouettes before the scene. The WebGL yard uses the same ramp and cloud recipe on an inverted sphere and distant cards.

The editable source is `demos/mite-yard/yard-sky.mjs`, three seeded 192 × 80 masks generated at startup. No texture files, GLBs, collision, combat, or native client changes. The new proof is the **Canvas** path in 402 × 874 cloud Chrome. The WebGL yard is not visually verified in this session because that Chrome could not create WebGL2.

Tests check deterministic cloud masks, fade at the edges, unit directions, and the daylight ramp. All 29 standalone tests pass. Touch QA: clear at 77 HP and Servo salvaged.
