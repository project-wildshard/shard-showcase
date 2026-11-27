# E9 · Storm Hour beacon rehearsal

Use the existing E9 switch, tower and charged insert. The single named lens
receives one of two linear-RGB palettes in `states.json`: amber before use,
mint when lit. Play the existing 0.32 s lever clip once on acceptance, then
show the existing charged insert at the tower. The pose also changes, so
the close interaction doesn't rely just on color. No new GLB, texture,
lights or bloom are required. Apply colors to per-instance material clones.

The rehearsal enters the north gate, walks all four archived corner pads,
and leaves at the west gate using Engine 0.1.44's stock motor. Static fit
uses the Round 5 wall/pedestal proxies and a flat floor. Ground controls and
lamp inserts are exact pinned GLBs. A synthetic interaction checks the
1.7 m reach, front-facing approach, sightline to the lens, and repeat use.
All four accepted, with zero airborne movement ticks. Four distant, four
behind-wall and four repeated attempts rejected. This doesn't install
the route in the game, simulate patrols, implement Lights Out or weather,
handle reloads, emit audio, or show that a physical phone can read it.
No dependency on the Vault Warden reward.

From the art checkout, point `WSC_NODE_PROJECT` at a Node project with
Engine 0.1.44, its Rapier dependency, and Three r186 installed:

```sh
WSC_NODE_PROJECT=/path/to/pinned-deps node --experimental-transform-types \
  demos/native-storm-beacons/sample.mjs /tmp/e9-storm-beacon-route.json
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-storm-beacons/render.py -- /tmp/e9-route-review
```
