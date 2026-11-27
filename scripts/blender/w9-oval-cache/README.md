# W9b oval cache sight screen

Use the existing WSC-PROP-049 opening GLB unchanged. Its exact Round 5
anchor is Three `(-233, 0, -150)`, identity yaw. The new dry-stone screen
uses the same pivot, leaving the south approach open. Do not merge the
asset into the chest or change the existing clip. Restoring the studied
placement requires only these two models; render soil, grass and loose
chips are not packaged.

After reimport, 57 poses of the actual lid clip do not intersect the
screen. The wall hides lid corners/center from 78 sampled eye rays
on the west riding bend at two eye heights. The screen stays at
least 19.1 m beyond the 38 m radius bend's running line.
Three grounded stock headless approaches from the south reach the
normal 2.5 m prompt radius. From one screened position inside the
same radius, the stock picker does not select it; removing only
the stone screen restores selection. No actual interaction executes.
This does not modify the racing line, terrain, economy, prompt art,
live loot or W9b progression. The existing empty cavity stays empty.

Save the original Round 5 layout from the repository and ref
embedded in `extract.mjs`. The tool rejects files with other Git
blob hashes. The extracted exact placement is also in the tracked proof.

```sh
d=/tmp/w9-cache
mkdir -p "$d"
node scripts/blender/w9-oval-cache/extract.mjs /path/to/exact/layout.js > "$d/placement.json"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/w9-oval-cache/build.py -- "$d/placement.json" "$d"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  scripts/blender/w9-oval-cache/check.mjs "$d/art.json" "$d/geo.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/w9-oval-cache-screen-proof.json
```

## Behind the Rock variant

Run the same recipe with `--rock` after the layout path in the extractor.
Compare the new proof to `project/layouts/w9-rock-cache-outcrop-proof.json`
and the new GLB to the tracked `w9-rock-cache-outcrop.glb`. The fractured
shale shelves tuck the same chest into its Round 5 position west of the
Rock. The south lane stays open. These are local, flat-ground tests; the
render's distant ridge, path and grass are not exported.
