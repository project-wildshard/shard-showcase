# Band 6: two types of cover

The archived Round 5 lab uses a 12 × 3 × 0.6 m straight sight
screen between pack centers, and a separate 1.1 m-high cover
piece with a right return. These neutral art donors preserve
both blockout envelopes; the name “arc screen” does not mean
this original instance curves. Both renders use the surveyed
anchor/yaw rows from the pinned placement data. Across Band 6
Round 5 has 14 sight walls and 31 low covers. This is not a
placement of all of them or a revision of spawn counts.

All 37 evenly spaced local rays per asset at 0.85 m hit both
pieces. At 1.70 m, they hit the tall screen and pass above the
low cover. At 3.10 m all the sampled rays pass above both. The
sampled line between the exact pack centers next to the new
screen is blocked at 1.70 m and clear at 3.10 m. The low
piece's perpendicular return also blocks 15 sampled rays.
These are isolated Blender mesh rays, not detection tests or
a guarantee about every possible eye position.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/band6_duel_cover.py -- /tmp/e6-duel
```

Set `WILDSHARD_VALIDATE_ONLY=1` to skip photographs. Same
editable Blender Python rebuilds the textureless exports
byte-for-byte. Each uses six material groups. Three loads
the 192,052 B / 2,916-triangle screen and the 78,644 B /
1,176-triangle low return with exact bounds. Ground and
lighting are review only. No actor, combat, collision or
spawn wiring. See `project/layouts/e6-duel-cover.json`.
