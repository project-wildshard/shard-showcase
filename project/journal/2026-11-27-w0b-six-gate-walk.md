# W0b · Walk the six West town gates

The town replots from a point just inside the West Gate at
Three (−120, 0), not a claim about the live spawn. Test each
arch at center and ±0.42 m using ordinary stock player movement.
The collider input is a bounded exact triangle extract with no
fallback ground plane. The West barrier control stops the player.

Town shell alone: all six arch centers are reachable, but Park
and Range lose their floor just outside the wall. Their three
routes each fall after crossing the mouth. The existing expanded
West scene already includes the Park path and Range approach.
With that scene in place 18/18 routes finish 3–4 m past the
gate centers, grounded and with zero stall ticks. No new slope,
bridge, invisible box or position teleport is needed.

The expanded scene reproduced its 3,025-part semantic signature;
the original shell matched its 2,692-part signature. The exact
collision inputs differ by four meshes and 46 triangles inside the
fixture bounds. The route overview plots actual center-lane samples.
Portrait frames 05 and 06 use the archived Round 5 gate-plaza
and Main Street eye vectors and vertical FOV, at 1.70 m eye height.

See [rebuild and replay](../../demos/native-town-gates/README.md)
and [result](../layouts/w0b-native-town-gates-proof.json). No
developer build deploy, draw-call budget, phone or original-W0b
polish sign-off. These are bounded native tests on the art branch.
