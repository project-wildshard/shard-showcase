# W6d Movers course start pad and records board

Round 5's archived start at (−74, −90) and board at (−66, −96)
are 10 m apart. Reuse the original 3 m pad radius and the plan's
BEST/LAST fields, but display dashes rather than invented records.
The pad chevrons face the first conveyor and the board faces the pad.

The recipe opens the exact static Movers rebuild, verifies its
fingerprint, samples the approach under the pad and the terrain
at both board feet, and checks the view toward the board title.
Disk stack and housing are separate, small exports. No existing
station geometry or tank finish is imported into the new GLBs.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-movers-roof/build.py -- \
  --output /absolute/scratch/movers-base
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/movers_start_record.py -- \
  /absolute/scratch/movers-base /absolute/scratch/movers-start
```

These are art pieces only. Times, checkpoints, trigger zones,
collision, native placement and traversal are not implemented.
