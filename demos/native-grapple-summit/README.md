# W7a: five pulls to the original summit

The old W08 proxy ring is in the stock claw's 38 m range from the fourth deck, but the line of sight is blocked. The original cable launch anchor is visible and locks when used as a negative-control hook; that pull ends on the lower 36.07 m level, not the summit.

An optional outboard ring at Three (-211.4,46.4,-38.9) gives a clear approach past the rail to the existing 45.05 m summit floor. It sits to the side of the trajectory. Forty-nine downward probes check the base flange seats 10 mm into the exact deck. Keep the original tower, old proxy geometry, guardrails and both zipline endpoints. For this fixture only the new ring is selectable as hook 5. Its GLB origin is the ring centre; place it at that coordinate with identity rotation. The entire reimported pedestal and ring participate in collision.

All 25 starts over ±1 m in X and Z climb from the start to the original top deck in one pinned SimHost. The fifth pull is 32.86–32.97 m from the eye and reaches the verified summit in 172–174 ticks from fire. A 16-point sampling circle at radius 0.58 m around each settled capsule verifies that the standing spot is supported by the exact top floor, not a lower deck with the same collider handle. Model: 33,136 bytes / 872 triangles, no textures. The amber ribbon is a render overlay from measured motion.

This proves the full five-hook **headless ascent**, not a timed or published course, handoff to the trolley, phone controls, or player-tested difficulty. The zip-house release bench remains separate.

## Rebuild

Follow the [four-hop rebuild](../native-grapple-mast/README.md) through creation of its fixtures in directory `T`, with `B` pointing at the same exact W08 Blender file. Run:

```sh
D=demos/native-grapple-summit
blender -b "$B" -t 4 --python-exit-code 1 --python "$D/extract.py" -- "$T/summit.json"
blender -b "$B" -t 4 --python-exit-code 1 --python "$D/model.py" -- "$T"
node --experimental-transform-types demos/native-grapple-two/sample.mjs "$T" "$T/native-five.json" --summit
blender -b "$B" -t 12 --python-exit-code 1 --python "$D/model.py" -- "$T" "$T/native-five.json"
```

See [the compact receipt](../../project/layouts/w7a-summit-hop-proof.json). Scratch hulls, W08 Blender assembly, exploratory anchor sweep and full motion traces are regenerated, not tracked.
