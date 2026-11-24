# Training Vault Room 4: Lockdown art study

E10d calls for a sealed 12 m-radius room with wall hatches
and tiles that warn before a sweep. The E09 mockup supplies
the metal plates, round bulkhead and amber lighting language.
This is an original standalone room, not a recreation of a
shipped location. No Warden or enemy partial was made.

A 21-sided wall ring uses a nominal 12 m apothem. Fixed
bulkheads, hatches and ribs are set inside that reference.
Twenty-nine full linked 3.155 m plates fit the footprint,
with simple perimeter metal under the uncut tiles. Three
tracked donors are pinned and unchanged. Two new small GLBs
contain a sealed hatch (18,896 B, 236 triangles) and a
one-plate warning insert (8,780 B, 72 triangles). Local hatch
face is −Y in Blender; the insert is centered above Z=0.
Place repeated instances, not duplicated exports.

The script reimports both new files and measures clearance
on actual plates at 720 insert vertices. The same 1.70 m
camera, walls and fixtures are used for both looks. Only the
five insert materials change in the comparison. The download
contains the bright insert; idle is an object-local override
in the rebuild. No activation timeline, hazard, collision,
spawner, damage, mobile performance or native connection.

The original Room 3 final landing remains unchanged. A
straight-east 24 m room would overshoot D41's x=221 m edge.
A northward turn requires a separate spatial verification.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_lockdown_room.py -- /tmp/vault-r4
```

The recipe rebuilds both tiny GLBs, the comparison scene,
the visual pair and a measurement receipt; no .blend cache
or copied donor geometry is needed in the repository.
