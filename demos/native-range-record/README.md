# W3a · Six Dummies to the Range Records board

This fixture connects the existing native gate-to-yard replay to the
existing WSC-PROP-027 record face. It reads the engine's six accepted
contacts, times from entry to the last contact at 60 Hz, keeps the lower
valid time and verifies a serialized round trip. A closed gate or an
unfinished run never sets a score. Duplicate or malformed successful hits
are rejected; unsuccessful attempts do not count. The two other rows
stay blank. Slower/faster comparisons shift replay ticks and are synthetic,
not additional measured runs. Nothing is stored in a real player save.

Run the `--entry` steps in
[the native Range Gate rehearsal](../native-six-targets/README.md) to get
`entry-run.json`, then:

```sh
D=demos/native-range-record
node "$D/check.mjs" "$T/entry-run.json" "$T/range-record.json"
WSC_RANGE_RECORD_REPLAY="$T/range-record.json" blender -b -t 6 \
  --factory-startup --python-exit-code 1 \
  --python scripts/blender/w3-range-record-face/build.py -- "$T/record"
```

The script doesn't modify either existing GLB. It projects the active value
into the measured slot on the original face for two matched renders,
swapping the placeholder mesh only for the scored view. No new GLB,
fonts, textures, live records host, UI bindings, equipment loan or
phone/game testing. Integration should use actual accepted contact
events, the shard's real timer lifecycle, and versioned player saves.
