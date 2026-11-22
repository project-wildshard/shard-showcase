# Crate Mite first-person calibration

A standalone Three.js combat test, not a native Wildshard shard or game release.
It runs the rigged phone-budget Mite while testing movement, line of sight,
waking, turning, chase, bite, overclock, hit reactions and death. The viewmodel
is an editable procedural forearm, hand and sword with a timed swing.
One copper-coil Servo lands where the Mite breaks apart. Walk within 1.1 m
to add it to the demo counter before it expires. This does not modify a
native inventory or save, and the art is generated in `yard.mjs`.

```sh
node --test demos/mite-yard/combat.test.mjs
node demos/mite-yard/build.mjs /tmp/mite-yard
python3 -m http.server 8080 --directory /tmp/mite-yard
```

Open localhost:8080. WASD, new mouse look after entering, space or click to
strike, R to reset. On touch, drag the view and use the directional/Swing
buttons. The build uses the pinned Three dependency, copies only the needed
module closure, and stages the committed rig GLB. Do not commit the generated
dist, vendored libraries, or browser artifacts. The CPU canvas fallback
renders the same skinned asset and simulation when WebGL is unavailable.

Browser smoke: Chrome's software renderer loaded the rig, walked into wake
range and completed a sword kill. Native product admission and phone
performance have not been verified. The fixed-step simulation tests also
cover direction, line-of-sight checks and an overclock strike killing the
player.

The first-person iron work sword and hand are procedural in `viewmodel.mjs`.
Its windup, impact, follow-through and recovery share the simulation's
impact time. The hit indicator only appears after confirmed damage. A
projection check covers landscape and 402 × 874 portrait framing; it is
not an iPhone performance test.

The East E01 court uses the committed robot dock and haul crate GLBs, with
layout in `yard-layout.mjs`. The dock is a movement obstacle, not opaque tall
cover. The stack sits on the existing east cover footprint. The central
wake/fight lane remains clear. This standalone layout is not a native shard
placement.
