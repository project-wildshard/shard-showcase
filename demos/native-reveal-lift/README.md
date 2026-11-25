# C2 reveal lift · shared-stage rehearsal

The existing 6 × 6 m deck at (55, 0, 229) rises exactly 4 m in
150 ticks. The player can walk onto it at court height and stay
grounded while rising. A saved halfway pose resumes with zero
observed deviation over 115 ticks. Deasserting the shared stage
after arrival leaves the deck at the top. With the mover disabled
in a separate run, the same walk falls to the −5.6 m shaft floor.

This uses the pinned Format 0.43.0 mover row validator and Engine
0.1.44 `MoverScriptDriver` in a real native headless resident.
The engine installs and moves the collider and owns continuation.
Static collision in the rehearsal is only four floor strips and
one shaft floor, not an admitted copy of the full C2 court.
A test flag provides the shared stage value explicitly. The
usual standalone moored-mover install does not pass a shared
activation callback. A real wave host must provide that port
and own the end signal. Use a one-shot track here: the pinned
ride winch accepts an interaction trigger, not a shared stage.
No Supervisor, wave director, mounted client test, multiplayer
behavior, physics descent or deploy was added.

```sh
# Use an admitted local native calibration folder; it is not public.
# WSC_NODE_PROJECT is the dependency root pinned to the versions above.
export WSC_NODE_PROJECT=/path/to/pinned/dependencies
node --experimental-transform-types demos/native-reveal-lift/sample.mjs \
  /path/to/admitted/native-folder /tmp/c2-lift-trace.json
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-reveal-lift/render.py -- /tmp/c2-lift-trace.json /tmp/c2-lift
```

The render uses the existing unmodified C2 scene GLB and replaces
only the moving deck's vertical position with the measured pose.
The amber marker is the player's sampled foot location, not a
new character. Both views use one unchanged camera. Repeat runs
produced identical small receipts; see
`project/layouts/e11c-reveal-lift-native-proof.json`.
