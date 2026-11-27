# W9b · Gold on tower deck four and the Zip House roof

Two placements of the same existing one-metre Gold GLB, neither
touching the rendered environment. Round 5 coordinates are in Three
XYZ, Y up. Do not add a duplicate model, patch the roof, or move the pad.

| Place | Archive | Candidate | Measure |
| --- | --- | --- | --- |
| Tower deck 4 | (-212, 36.6, -34) | (-213, 36.6, -34.75) | 1.25 m west/north; pickup hovers 0.55 m above the retained deck |
| Zip House roof | (-110, 12.5, -12) | unchanged | pickup hovers 0.50 m above the original roof, off the landing pad |

The archived tower point has no flat deck directly below it within the
target tier. The fit scans in 25 cm steps and takes the closest viable
center with the authored height retained wherever it gives the right
hover. At each fitted point, 49 roof samples across 1.11 × 1.11 m
match in height. An exact reimported Gold mesh overlap test and a
1.70 m eye sample from a nearby standable patch both pass. Sky, light
and camera are review-only. These checks do not prove the ladder or
zipline approach, a touch pickup, FINDS persistence, or live placement.

```sh
T=/tmp/west-rooftop-gold
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output "$T/w08"
blender -b "$T/w08/west-zip-route-editable.blend" -t 8 --python-exit-code 1   --python scripts/blender/west-rooftop-gold/check.py -- "$T/out"
```

Add `--proof-only` after the output directory to skip renders.
See [receipt](../../../project/layouts/w9b-rooftop-gold-proof.json)
and the [Round 5 marker list](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L299).
