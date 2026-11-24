# W10a: paddock exit to the oval

The Round 5 layout puts a 48 × 60 m paddock north opening
at Three.js x/z (−40, −132). The fence center lines run
14 m toward the oval, 12 m apart. This local art study
follows those coordinates, not the newer R02 oval layout.
Existing fence modules are linked. Five 2.8 m bays per
side reduce their local span to 89.229% without modifying
the source. Rail and post geometry leaves 11.67 m clear.

The mounting block and trough use the known pads from the
archive. Reuse the new enamel OVAL waymarker on both sides
of the entrance, outside the lane and 135 mm clear of the fence. The portable model is
16,048 B, 165 triangles, ground origin, face −Y in Blender.
Trees and stubble are staging only. Only the new waymarker
enters the export, not the ground and re-used donors.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/paddock_chute.py -- /tmp/w10a-chute
```

Shows a 2.6 m rider-height camera and an elevated layout
comparison. No native game placement, horse clearance test,
track merge into the R02 course, gates, or lap triggers.
