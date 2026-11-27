# E10d · Vault Room 4 warning sweep

The existing 8,780-byte tile insert now has an exact visual
timeline across all 29 whole floor plates of the Lockdown study.
No plates, bulkheads, hatch or GLB were replaced. The nearest row
changes last, leaving the next section legible before it activates.

- 30 Hz timebase: each row gets 30 frames (1 second) of amber warning,
  then 19 active frames, then returns to idle. The next row starts
  11 frames after the previous one.
- Warning lights the continuous amber bar. Active darkens that bar
  and lights the smaller red center and chevrons; the pattern changes
  as well as the hue.
- Three states from one fixed portrait camera: 0.80, 1.67 and 2.63 s, with no
  active tiles until the first full second of warning has elapsed.
- 4,176 vertices of the exact reimported insert cleared the underlying
  metal surface by 6.0–14.5 mm. Hatch and insert bytes reproduce.

No new hazard, Warden, health effect, encounter timer, dynamic
lighting, mobile frame-rate measurement or native room placement.
The control module is a reusable visual fixture, not encounter code.

```sh
node demos/vault-lockdown-look/check.mjs /tmp/vault-r4-sweep.json
WSC_VAULT_SWEEP=/tmp/vault-r4-sweep.json \
  blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_lockdown_room.py -- /tmp/vault-r4-sweep
cmp /tmp/vault-r4-sweep/vault-r4-sweep-geometry.json project/layouts/e10d-lockdown-sweep-geometry.json
```

Set `WILDSHARD_VALIDATE_ONLY=1` to skip images. With no
`WSC_VAULT_SWEEP`, the original five-tile comparison is unchanged.
