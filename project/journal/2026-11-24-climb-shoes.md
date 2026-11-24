# West Climb Yard ladder ground fit

The canonical Climb Yard and Rock build passes semantic parity and
its reimport checks. In that rebuilt scene, the rail caps on decks A,
B and C start at 0.170 m. The yard top is 0.0275 m. Samples at each
rail center and four offsets reproduce the 142.5 mm gap.

One low cast shoe can be reused at all six positions. It seats 2 mm
into the terrain and has 24 mm of modeled overlap with the rail.
The top of each shoe is 107 mm below the first rung's nominal lower
edge. No rail, rung, deck, guard opening or donor mesh was moved.
These are visual geometry checks, not structural or traversal work.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- \
  --output /absolute/scratch/climb-base
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/climb_yard_shoes.py -- \
  /absolute/scratch/climb-base /absolute/scratch/climb-shoes
```

Only one reusable shoe is exported. The latter script verifies the
reimport and renders a matched ground pair plus the original Deck A
exit. The base scene remains a separate canonical build.
