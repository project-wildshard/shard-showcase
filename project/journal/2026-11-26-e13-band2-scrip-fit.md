# E13 · Two Band 2 Scrip chest placements

E13 / LW5 assigns two 25-Scrip chest claims to Band 2. Fit the same
articulated case used in Band 1 at the unchanged Round 5 locations, with
the archived zero yaw. No new GLB, rig, texture or reward script.

| Anchor | Three X | Three Z | Minimum lid gap | Margin outside approach |
| --- | ---: | ---: | ---: | ---: |
| A | 27.495608 | −202.052123 | 1.225 m | 0.206 m |
| B | 110.758256 | −218.892414 | 1.453 m | 2.683 m |

At each anchor, Blender reimported and checked 109 hinge poses against
local cover and spawn envelopes. Clear approach: 0.90 m wide from +0.98
to +3.00 m along Three Z. Gaps are lower bounds measured along world axes.
Squared wall and crate proxies are checked before adding render-only
bevels. Pallet Jack body, forks and pack marker use conservative boxes.
The matched views are staged for review; not final terrain or live enemies.
No payout, crate interaction, route test, FINDS or runtime install.

```sh
# Optional re-extract from the pinned Round 5 archive.
node scripts/blender/e1d-band1-fit/extract.mjs /path/to/round-5-blockout 2 \
  | cmp - project/layouts/e13-band2-scrip-anchors.json
# Build from this checkout without the archive.
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e1d-band1-fit/build.py -- /tmp/e13-band2-scrip --band2
cmp /tmp/e13-band2-scrip/proof.json project/layouts/e13-band2-scrip-fit-proof.json
```

Append `--proof-only` to skip stills. Without `--band2`, the original
Band 1 proof and archive extract both reproduce byte-for-byte.
