# E5b Stealth Yard alarm gates

The Round 5 blockout fixes two 16 m openings: north (x 140–156
at z 14) and west (z 58–74 at x 126). This art proposal uses
the same 7.98 m sliding leaf twice at each opening, with a
half-turn around Y for its opposite. The base datums in meters
are (148, 0, 14) and (126, 0, 66), and the prototype leaves
are seated 15 mm above the local floor. The clear pose calls
for 8.12 m of storage to each side. Local GLB +Z is towards
the entrance; rotate the pair 180° for north and −90° for
west. The dark plate and saffron edge mark the motion;
the cyan circle and red square are distinct signal meshes.

The renderer reimports both exported GLBs. On the gate pair,
318 horizontal samples across the width and height hit the
closed leaf geometry and none hit the open leaf geometry. The
test checks only the two poses. Outer guide piers, wall pockets
and traffic markings are illustrative and not exported. The
three existing shipping containers in the backdrop are reused,
not part of the new payload. The original north and west map
openings, not staged collider or clearance data, are binding.

In the GLB both lens materials are authored bright. A caller
should place a dim, nonemissive material on the inactive
named lens node, as the Blender preview does. No embedded
lights, animations, trigger, detection, lock timer, colliders
or keycard behavior. The planned 20-second gate shutdown
is not implemented.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 --python \
  scripts/blender/showcase-studies/stealth_alarm_gate.py -- /tmp/e5b-alarm-gate
node scripts/blender/showcase-studies/check_e5b_alarm_gate.mjs /tmp/e5b-alarm-gate
```

The machine-readable receipt is `project/layouts/e5b-alarm-gate-fit.json`.
