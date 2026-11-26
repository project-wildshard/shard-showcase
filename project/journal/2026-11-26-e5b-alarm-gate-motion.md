# E5b · Sliding alarm gate motion

Both original door leaves are shared instances of the same pinned mesh set,
not a second model. The new pair opens by default at local floor origin.
Keep the original north and west transforms from the fit receipt. Play
`Alarm_gate_close` (2.4 s) or `Alarm_gate_open` (2.8 s) once, clamping
to the end. Each leaf moves 8.12 m along local X and the right leaf has a
positive-scale 180° yaw. The durations are proposed art timings, not the
planned 20-second alarm hold. The lamp is still a separate original asset.

Three.js reads both clips through GLTFLoader. At each authored gate,
626 sampled poses validate the same continuous monotonic opening geometry.
The leaf-to-leaf gap is 16.24 m at rest, 8.12 m at midpoint and zero at
closure, with no crossed leaves. Across both gates, 1,536 face rays
validate sampled points on both sides of the moving aperture. This
doesn't prove collision, existing wall-pocket clearance, blocking a moving
player, the signal logic, alarm/quest behavior or device performance.

The GLB is 60,876 bytes: 736 unique triangles, 1,472 shown with both leaves.
Its geometry buffer prefix, mesh definitions and materials are identical
to the unchanged 52,068-byte single leaf. Only the extra nodes and the
motion clips are added.

From the repo root:

```sh
out=/tmp/e5b-motion
node scripts/blender/e5b-gate-motion/pack.mjs "$out"
node scripts/blender/e5b-gate-motion/check.mjs "$out"
WSC_E5B_MOTION_GLB="$out/e5b-alarm-gate-pair-motion.glb" blender -b -t 6 \
  --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/stealth_alarm_gate.py -- "$out/review"
```

The paired North cutaway renders read the animation from the exported
GLB at 1.2 and 2.1 seconds, with the alarm lamp set red for illustration.
The surrounding fence and container arrangement are the previous review
stage, not a new yard export.
