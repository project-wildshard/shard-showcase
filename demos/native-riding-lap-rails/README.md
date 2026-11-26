# W10b · All four rails on one native oval lap

Keep the four R02 striped rails exactly where they are. Reimport the
real `WSC-PROP-080` geometry at each placement and exercise it in one
uninterrupted stock Engine 0.1.44 mounted lap. This extends the earlier
flat-oval test and the isolated first-rail proof without changing either
old outcome.

Three matched sets of six runs use ±0.5 m starts, clean and Ring 1
bypass (scripted reins, 13 m/s top gait, no jump button):

| Setup | Full-body lower-envelope clearance |
| --- | --- |
| Original rails alone | All 24 crossings stayed at floor height, underneath |
| Oak apron flush at all four rails | Three rails clear; first eastbound rail misses by 31–49 mm in all six runs |
| Same apron 0.80 m downstream on that first eastbound rail | All 24 clear; minimum 74 mm overall and 97 mm at corrected rail |

The tight rail is R02 placement 4, world X/Z (−160, −224), first on
the south straight. Set the existing apron at Three (−159.2, .025,
−224), yaw −90°, on the new pair of oak stands. Keep the original
striped beam at X=−160. The support GLB is 30,084 bytes, 352 triangles,
no textures, and shares the apron pivot. The other three panels
remain at their existing rail pivots.

Every corrected run lands at all four and retains full mount HP.
The clean runs cross all eight horizontal checkpoint bands in
45.468–45.469 s. Bypasses score exactly one miss and +5 s offline.
A second centre start reproduces the same corrected trace. The old
flat-lap receipt is unchanged. Envelope checks use interpolated
feet samples over the full 2.4 m mount body length; this is not a
rider/horse rig-mesh clearance measurement.

The stock mounted motor ran on a synthetic flat floor and exact
rail colliders. Ring volumes remain horizontal test bands, and the
trial does not establish installed scoring, native course terrain,
camera, pet behavior, or iPhone play. The stands' conservative boxes
stay outside the sampled centre trajectories.

```sh
d=/absolute/scratch/w10b-four-rails
mkdir -p "$d"
blender -b -t 4 --factory-startup --python-exit-code 1 \
  --python demos/native-riding-lap-rails/stand.py -- "$d"
blender -b -t 4 --factory-startup --python-exit-code 1 \
  --python demos/native-riding-lap-rails/extract.py -- "$d/geometry.json"
WSC_NODE_PROJECT=/path/to/pinned/engine/project node --experimental-transform-types \
  demos/native-riding-lap-rails/sample.mjs "$d/geometry.json" "$d/proof.json" "$d/replays.json"
cmp "$d/proof.json" project/layouts/w10b-native-lap-rails-proof.json
WSC_RIDING_LAP_RAIL_REVIEW="$d" blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/riding_course.py -- "$d"
```

The review images show two actual centre-run feet traces (amber and
mint) at the original rail, not a rigged animation or an in-game HUD.
