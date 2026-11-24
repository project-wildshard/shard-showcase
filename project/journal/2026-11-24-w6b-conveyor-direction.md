# W6b · Alternating conveyor direction cue

The existing WSC-PROP-037 donor repeats seven centered, half-turn-symmetric cyan dashes. Round 5 depicts tilted slats with opposite orientations on the middle belt; W6b explicitly requests alternating movement. This art study keeps the current meshes and their authored rebuild transforms from `scripts/blender/west-movers-roof/movers.py`: x = −84/−90/−96 m, y = 103 m, z = .10 m, yaw = 0/π/0 in Blender. The new directional mark points along local −X, towards course progression on the first and third belts. It points +X on the middle belt. This is a study convention, not an assertion about an engine axis or speed.

Two rows of aqua directional marks on a dark keyline avoid the original 45 mm dash band. The visualization uses flat planes 2.5–2.9 mm over the .4195 m rubber crest; they span existing tread grooves and do not follow the valley surfaces. All 60 sampled vertical rays hit rubber below the pads. There are no new colliders or feet. The unchanged donor spans 4.768 × 1.696 m in plan; the clear gap at the existing 6 m spacing is 1.232 m. These are authored fit measurements, not replacements for Round 5’s larger 6 × 4 m proxies.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/conveyor_direction.py -- /tmp/conveyor-direction
```

`WILDSHARD_VALIDATE_ONLY=1` skips two renders. The 9,244 B / 60-triangle standalone mark set rebuilt byte-identically and loaded in Blender and Three. Existing model untouched; do not infer native belt integration, animation, velocity, crate behavior, scrolling UVs, player collision, or phone readability. A production art integration could bake the mark into a tread material instead of mounting an overlay.
