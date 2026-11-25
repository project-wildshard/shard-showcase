# W7a: first grapple pole landing bench

Round 5's GRAPPLE start pad XZ is `(-142,-22)`
(singleplayer archive `ce1cf050b36fa236155ac26d43e721b9012c49df`,
`art/showcase-template/round-5-blockout/layout.js`,
blob `5d019a020361c47187ec889f2bc947f82cd9f98a`). The rebuilt W08
art has the first hoop at Three.js `(-150,12,-44)`.
From standstill at the pad, its eye distance is 25.567 m and
the line of sight is clear. The default 38 m reach is not
the blocker. Stock grapple also demands a standable landing
within 9 m vertically below the ring. The existing context
only has the ground and pole, so the stock lock fails.

The separate candidate perch's deck is 3.40 × 2.24 m, top 4.40 m,
with a bottom-centered pivot at Three.js `(-151,0,-46.62)`.
It adds a landing **past** the hoop without moving the hoop,
modifying the rebuilt W08 model, or increasing reach. The run
uses the pinned Engine 0.1.44 native server grapple extension,
its actual Rapier capsule, the exact extracted opening corridor
(292 triangles across six W08 meshes), a box matching the exported
deck's bounds, and triangles from every reimported detail part.
No static ground from SimHost is added on top.

The center first lands in 141 ticks (2.35 s from fire); the same
start repeats exactly, including if locked through camera projection
rather than by hook index. All 25 grid starts over ±1 m in X and Z
reach grounded contact in 137–144 ticks. After at least 12 successive
grounded ticks, the sampled capsule has at least 129 mm of deck
edge margin after subtracting its radius. See
`project/layouts/w7a-pole-one-perch-proof.json`.

**Scope:** one isolated opening hop. No actual shard placement,
control prompts, build/runtime install, safe descent/fall policy,
other four hooks, timer, best time, client, multiplayer, or on-phone
proof. The open platform edge belongs to the test fit, not a safety
or production decision. The cyan trajectory and amber landing dot
are review annotations; they are not in the GLB.

Rebuild from repo root using Blender 4.3.2 and installed Engine 0.1.44,
Format 0.43.0, Three, and Rapier as in `demos/native-jump-pad`. Set
`WSC_NODE_PROJECT` to the absolute project root if dependencies are elsewhere.

```sh
T=/tmp/w7a-bench
mkdir -p "$T"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output "$T/w08"
B="$T/w08/west-zip-route-editable.blend"
D=demos/native-grapple-perch
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/extract.py" -- "$T/opening.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/perch.py" -- "$T"
node --experimental-transform-types "$D/sample.mjs" "$T/opening.json" "$T/native.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/perch.py" -- "$T" "$T/native.json"
```

Only the small proof, editable recipes and optional GLB belong in
`art`; regenerated context meshes, collision scratch and full motion
samples do not.
