# W5a: recovery deck for the 4.8 m Hover Park kicker

This optional receiver holds the top level for 17.11 m before a 16.5 m rollout
onto paving. It continues the unmodified tallest D7 lip with 10 mm overlap
and a 2 mm step down. The 4.6 m wide deck ends 5.945 m before the separate east
launch wall. The GLB has a ground-level pivot at Three X -167.39, Z 154.
Use the named D7 Receiver Riding Surface as the top collider; the legs,
trusses, and fascia are visual only. The turquoise stripes are coplanar.

With the exact reimported top and stock Engine 0.1.44 input, 15 passive rides
rolled through and all 120 accepted jumps in 135 attempts kept full HP.
The trial varies three starts, five offsets and nine one-tick timings. The
15 refused inputs simply rolled through. The same 15 matched jump controls
without the receiver hit bare paving at 14.50–14.75 m/s and lost about 8 HP;
with it they landed at 8.25–8.50 m/s and kept full HP. The fastest accepted
contact in the broader sweep was 9 m/s, right at the limit. These trials
don't establish safe speeds, lateral turns, braking, phone feel, or park-wide
fit and do not install native gameplay.

## Rebuild from repository root

```sh
d=/absolute/scratch/receiver
mkdir -p "$d"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output "$d/park"
blender -b -t 6 "$d/park/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-kickers/extract.py -- "$d/base.json"
blender -b -t 6 "$d/park/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-receiver/build.py -- "$d"
node --experimental-transform-types demos/native-hover-receiver/sample.mjs "$d/base.json" "$d/receiver.json" "$d/replay.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/w5a-high-kicker-receiver-proof.json
blender -b -t 6 "$d/receiver-review.blend" --python-exit-code 1 --python demos/native-hover-receiver/render.py -- "$d/replay.json" "$d"
```

Set WSC_NODE_PROJECT to a package root containing Engine 0.1.44 and Rapier
if needed. The proof pins the exact donor extraction. Mint dots show a
no-jump route and amber dots its jump counterpart. They are Blender overlays
of stock input replay; no snapshots or experimental donor files are needed.
