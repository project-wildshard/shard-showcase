# W5a · Tall-kicker exit, exact launch-wall collision

Follow-up to [the plane-only exit fixture](../native-hover-exit/README.md). The stock board coasts across the unchanged D7 paving and the byte-matched receiver on normal 60 Hz input frames. The only A/B difference is whether Rapier receives the original east launch-wall mesh (1,438 triangles) as a static WORLD collider. No proxy plane, west wall, or channel collider is installed. The plane is retained only as a reporting reference.

Each release repeats at lane center and ±0.75 m, with and without the wall: 12 runs total. Early release at X −171 stopped 3.18–3.33 m short of the wall plane and produced identical replay frames in both variants. Late release at X −195 reached the original wall at about 12 m/s in all three installed runs. The player center stopped at X −206.600, about 0.345 m outside the mesh bound; the same inputs with the wall omitted coasted to about X −231. All runs held full health. The first divergence is measured against the matched control; the following tick's speed is calculated from position, not the board's internal velocity, which takes longer to decay.

**Design consequence:** show riders when to let go before the descent. The wall is a backstop, not a braking affordance. These are straight-line server fixtures, not an authored collision hookup, a touch-input test, or an iPhone playability claim. The blue negative-control trace is lifted 5 m in the comparison render so the wall doesn't hide it; colored dots are Blender overlays of sampled positions.

## Reproduce

```sh
d=/absolute/scratch/hover-wall
mkdir -p "$d"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output "$d/park"
park="$d/park/hover-park-editable.blend"
blender -b -t 6 "$park" --python-exit-code 1 --python demos/native-hover-kickers/extract.py -- "$d/base.json"
blender -b -t 6 "$park" --python-exit-code 1 --python demos/native-hover-receiver/build.py -- "$d"
cmp "$d/w5a-high-kicker-receiver.glb" public/assets/wildshard-art/w5a-high-kicker-receiver.glb
blender -b -t 6 "$park" --python-exit-code 1 --python demos/native-hover-wall/extract.py -- "$d/wall.json"
node --experimental-transform-types demos/native-hover-wall/sample.mjs "$d/base.json" "$d/receiver.json" "$d/wall.json" "$d/replay.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/w5a-launch-wall-contact-proof.json
blender -b -t 6 "$d/receiver-review.blend" --python-exit-code 1 --python demos/native-hover-wall/render.py -- "$d/replay.json" "$d"
```

Set `WSC_NODE_PROJECT` to a package root with Engine 0.1.44 and Rapier if needed. Runtime constants, scene assets, and public map placement are unchanged.
