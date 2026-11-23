# West activity courtyard, WSC-KIT-001

Six existing art assets are composed into one reusable scenery
study. W05 and W06 anchor the ochre wood, slate metal, colored
pennants, cream paint and limestone. This small arrangement
is inspired by those shots; it is not an exact screenshot match
or the complete native West area. The props are purely decorative.
In particular, the timer face is baked and does not run.

The layout pins each donor by SHA-256 and stores every art transform.
There are 11 instances of six source assets. Three panel bays are
grounded, separated by two 20 mm decorative seams, and fronted by
fitted trim. Two curbs and the planted bed anchor the sides. The
script checks those seams and the curb/timer datums on imported
meshes. The library donor files are unchanged. Small new studio
geometry is procedural; no staging mesh, cache, or duplicate donor
binary needs to be tracked.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_activity_gallery.py -- /tmp/wsc-west-gallery
```

This creates a local composed GLB for inspection, validation JSON,
and two reimported Blender views. No collision, interactions,
equipment, or runtime/wiring are part of the study.
