# E8d named trophy reliefs: Warden's Plate and Titan's Core

The Warden's trophy is a wide, dark plate with two raised latch tabs, a small cyan status slit and a bronze rim. The Titan's trophy puts a faceted cyan center inside the approved cargo-orange and iron palette. Matched camera views show representative dark silhouette placeholders and the earned art, not unlock state.

| Relief | Bytes | Triangles | Forward gap | Left/right · top/bottom margin |
| --- | ---: | ---: | ---: | ---: |
| Warden's Plate | 27,464 | 508 | 8 mm | 55 · 108 mm |
| Titan's Core | 33,920 | 604 | 8 mm | 79 · 58 mm |

The exact twelve-frame donor is unchanged. Two instances were staged for fit with the earlier cache wall camera; left in the renders is Titan, right is Warden. Each trophy's locked preview is the convex envelope of its frontal mesh projection, not a shipped mesh or a functional state. The reliefs reopened in Blender and Three.js and contain no textures, packaged lights, rigs or reward rules. Real slot accounting, grant logic, bonuses, disclosure, bosses and public game deployment are unchanged.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/reward_trophy_reliefs.py -- /tmp/e8d-rewards
```

Receipt: `project/layouts/e8d-named-reward-reliefs.json`. Plans: E8d, E10d and E12h.
