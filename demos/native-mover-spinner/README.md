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

## Optional bottom-cage approach

The nominal Station 4 disc ends at X −151.50 m; the existing 5.50 ×
6.20 m lift cage begins at X −154.25 m in its lower position. Try a
fixed, removable 2.49 × 6.00 m landing insert between them. Its top is
Y 6.00 m and its west edge stops 10 mm short of the cage.
The 0.25 m nominal spinner-side gap leaves the rotating disc clear.

The stock player walked on, waited 24 or 72 ticks for the disc to
carry them, walked around the axle, and stepped into the stationary
bottom cage from three entry offsets. All six installed cases stayed
grounded; six matched gap controls fell below the landing. The
test steers to waypoints, not free-input navigation. The cage does not
move and the sweep arm remains visual. This does not prove lift
boarding when in motion, safe guarding, timer, device play, or install.

```sh
D=/tmp/spinner-handoff
mkdir -p "$D"
node --experimental-transform-types demos/native-mover-spinner/sample.mjs \
  /path/to/admitted/native/plan "$D/handoff.json" --handoff "$D/replay.json"
blender -b -t 4 --factory-startup --python-exit-code 1 \
  --python demos/native-mover-spinner/lip.py -- "$D"
cmp "$D/handoff.json" project/layouts/w6a-spinner-lift-handoff.json
cmp "$D/lip-proof.json" project/layouts/w6a-spinner-lift-lip.json
cmp "$D/w6a-spinner-lift-lip.glb" public/assets/wildshard-art/w6a-spinner-lift-lip.glb
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-mover-spinner/render.py -- "$D/replay.json" "$D"
```

## Stand-trigger lift to the 18 m receiver

Keep the accepted 6 m approach insert and cage footprint. In this
separate test the cage is a native moving platform, driven by a
one-shot position track with a 1.25-second continuous grounded stand
delay. On this pinned engine/format, the interact winch rejects a
stand trigger; this fixture uses the supported stand-trigger track.
An unattended check held the cage at 6 m for 480 ticks.

All six guided walks from the Station 3 ledge carried through the
turntable, boarded at 6 m, rose to 18 m, and walked west onto the
original Station 6 deck without an airborne tick. With the original
head beam acting as a box collider, the matching center run lost
deck ownership; the cage stopped at 17.605 m and the player did not
reach Station 6. The correction raises the same head beam 2 m
to center 20.5 m, allowing 2.20 m from walking plane to beam underside.
Four same-section steel guide extensions support that pose visually
and clear the cage's side envelope by 175 mm. The beam and extension
transforms are recorded, and the review renderer rebuilds them
against the preserved WIP source. No duplicate GLBs are needed.

This is a one-way half-course bench, not an installed game feature.
The sweep arm and side guide/bracing/rail collision, reset, call or
return logic, mid-ride reload, free input and phone feel remain open.
The review traces show measured feet plus a small drawing offset;
unmodeled colliders should not be inferred from the stills.

```sh
D=/tmp/station5-ride
mkdir -p "$D"
node --experimental-transform-types demos/native-mover-spinner/sample.mjs \
  /path/to/admitted/native/plan "$D/ride.json" --ride "$D/trace.json"
cmp "$D/ride.json" project/layouts/w6a-station5-ride.json
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-mover-spinner/render-ride.py -- "$D/trace.json" "$D"
```
