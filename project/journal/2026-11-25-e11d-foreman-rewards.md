# E11d · Foreman's Whistle and hard hat

The final E11d loot plan names the worn hard hat and Foreman's Whistle
as distinct rewards, separate from Foreman's Capacitor. The exact E12
mockup image (Git blob `03833f41a2c703599fad5373dc01374fd55436a6`)
provides the yellow reinforced dome, front brim and side fasteners, and
the ochre whistle with its right-side loop. This branch adds only these
two independent props.

- Whistle: 51,108 B / 1,220 triangles, 136.3 mm across at its author
  scale. A real cutout and open retaining loop remain visible. A
  negative ray passes through its loop center; the positive control
  hits the loop wall. The existing 12-frame donor is unchanged. One
  temporary 2.75× display uses the 0.518 m opening with 71.5 mm
  minimum edge margin and 13.75 mm forward gap. No final slot assigned.
- Hard hat: 94,476 B / 3,344 triangles, vent-free yellow shell with
  raised crown reinforcement, formed brim, dark interior band and
  offset crossed straps. Six underside rays see the recessed interior;
  four reach the webbing at 87.4–93.0 mm. The provisional origin is at
  the centered wear plane, crown +Z and brim forward −Y in Blender.
  There is no head rig, attachment, fit guarantee or equip test.

Both are texture-free deterministic GLBs. Blender reimport checks the
real meshes and Three verifies the bytes, triangles, bounds and rays.
No audio, whistle mechanic, unlock, perks, inventory binding, enemy,
different frame order or native game change.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/foreman_rewards.py -- /tmp/foreman-rewards
node project/check-foreman-rewards.mjs
```

Set `WILDSHARD_VALIDATE_ONLY=1` to skip photos. The frame is staged
only in the whistle view; full scene and derived review pictures are not
part of the art source.
