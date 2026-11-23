# W10b riding course: geometry and sightline proof

WSC-KIT-005 now has a focused, rebuildable study, not a playable race. Reimport the unchanged WSC-MODULE-010/011 and WSC-PROP-042/043/080 from this branch. The trees are existing scene dressing. There is no duplicate mesh export. Run from the repo root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/riding_course.py -- /tmp/w10b-proof
```

The JSON in `project/layouts` records donor hashes, source bounds, point placements, and three cameras. It uses the R02 208 × 88 m stadium (12 m riding surface; 478.761 m centreline) and its angled/straight slots, snapping the four end checkpoints to the centreline and rotating them across the direction of travel. The four jumps keep R02 placement and asset scale. R02 and the older Round 5 blockout are different layouts; do not use these coordinates as historical racing anchors.

- The donor ring has a 2.636 m nominal clear opening. The visual alternative at 1.730× matches Round 5's 4.56 m nominal aperture and 3.4 m centre. The bottom of its full outer arc is ~0.70 m above the track datum; the clear opening starts 1.12 m above datum. The visible lower arc is intentionally kept for review, with no collision assigned. Neither diameter establishes horse/rider clearance. The W10b ≥4 m logical checkpoint volume is a separate requirement.
- The donor jump pole spans 4.1 m; complete standards span 4.75 m. The Round 5 proxy spanned 10 m. No jump geometry was stretched to hide this.
- The gantry stays at the R02 anchor. The timer is a separate static prop facing approach. The camera at 2.6 m is height-matched, not attached to a rig. Horse, gameplay fit, checkpoints, timing, lap PBs, +5 second penalties and performance are untested.
