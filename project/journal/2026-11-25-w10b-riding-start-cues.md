# W10b riding lap board and first-ring cue

The Round 5 archive places the separate RIDING LAP
personal-best board at world (−80, 0, −137), 11 m from the
centre of the near straight. The board prototype follows that
anchor. The engraved heading and personal-best label frame
a blank graphite plane; a future record view can draw there
without rebaking the asset. No sample time is part of this GLB.
The independent carved arrow tells a rider to continue ahead
instead of turning onto the pullout. It does not duplicate the
OVAL waymarker at the paddock exit.

The portrait camera uses the Round 5 eye at rider height (2.6 m)
and looks west through reimported R02 gantry and ring geometry.
The R02 ring layouts and jumps were not reauthored; its first
ring in this direction is number 2, 25 m past the start gantry.
The older scoped oval preview looks east. Neither image decides
the shipped riding direction. The reused timer visible on the
gantry has a static example readout in its original donor asset.

The furthest mesh vertices stay 4.775 m (board) and 0.460 m
(arrow) outside the 12 m riding strip. Three rays from stand
positions in the pullout reach the empty readout; a separate
ray from the archive eye to the first ring centre is clear.
This verifies the Blender shot, not a mounted capsule, native
mobile readability, checkpoint, personal best or lap rule. The
approved +5 s per missed ring remains unchanged.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 --python \
  scripts/blender/showcase-studies/riding_start_cues.py -- /tmp/w10b-riding-cues
node scripts/blender/showcase-studies/check_riding_start_cues.mjs /tmp/w10b-riding-cues
```

See the receipt `project/layouts/w10b-riding-start-cues.json`.
