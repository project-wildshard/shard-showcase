# W6a: Station 4 rotating deck, native carry rehearsal

This keeps the existing WSC-KIT-002 art and uses the real
`MoverScriptDriver`, Rapier world, and player motor. The native row has
an eight-second quaternion track with quarter-turn keys. Rehearsal
colliders use 30 overlapping cuboids inside the original 9 m, 32-sided
disc, not a square standing surface. The top is 6.00 m; the original
2 × 8 m Station 3 arrival ledge and 0.50 m nominal visual gap remain.

- Four idle starts at radii 0.85, 2.00, 3.30 and 3.85 m rode for ten
  seconds each. All 2,400 checked ticks remained grounded on the moving
  deck. Deck-local drift stayed below 0.08 mm even across a loop.
- No-rotation control moved 0 m. Restarting from a snapshot at the
  3.30 m test radius reproduced the next 389 feet and yaw samples exactly.
- Three straight walking starts (center and ±0.75 m) entered in 22
  ticks and all stayed on the deck during an additional 48 idle ticks.
  No airborne tick was observed before first deck contact.
- Scripted jumping at the same approach point made contact but did not
  stay grounded at the 48-tick check: 0 of 3 with rotation and 0 of 3
  with rotation off. No recommendation to jump into the spinner from
  this test. The failure does not isolate the cause to the drive.

This is a headless bench with the normal resident plus a locally
installed stock driver. The arm is unchanged visual context, not a
shove or collision check. There was no native course install, timer,
complete Station 3→5 run, touch test or runtime deployment.

```sh
WSC_NODE_PROJECT=/path/to/pinned/node/deps \
node --experimental-transform-types demos/native-mover-spinner/sample.mjs \
  /path/to/admitted/native/plan /tmp/spinner-proof.json
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-mover-spinner/render.py -- /tmp/spinner-proof.json /tmp/spinner-render
```

Dependencies: Engine 0.1.44, Format 0.43.0 and the matching Rapier from
the admitted plan workspace. Review trails are drawn from actual
measured feet, not from a moving character mesh, and are not in the GLB.
The two entry traces offset 10 cm sideways to let both read.
