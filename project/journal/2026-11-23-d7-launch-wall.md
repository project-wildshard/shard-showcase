# November 23 · D7 Hover Park launch wall

WSC-KIT-003 now has a standalone wall cut from the verified existing
Hover Park scene, not a second design. One 76,800-byte GLB (1,438
triangles) replaces neither the live layout nor the historical W07
halfpipe entry. Its pivot is the floor at the center of the toe. Each
wall spans 45 m, runs 9 m from toe to crest, and has a 4.5 m design
crest excluding decorative coping. The 8 m flat center is separate.

Rebuild the production source and extract outside the checkout:

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-hover/build.py -- --output /tmp/d7/park
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-hover/extract_launch_wall.py -- \
  --park-build /tmp/d7/park --output /tmp/d7/module
```

The park build passes its existing semantic parity test. The extracted
GLB reimports at both original toe positions, with a 180 degree yaw for
the west side. Both vertex sets match the donors within 0.02 mm, and
the tested surface max rise/run is 0.959 excluding coping. Set
`WSC_D7_RENDER=1` for the studio comparison, which uses two instances
of the exact GLB and a separate floor. This is static geometry proof,
not collision or rideability. No editable scene or cache is committed;
the original tracked builder and dependencies reproduce the source.
