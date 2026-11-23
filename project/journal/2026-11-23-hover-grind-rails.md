# November 23 · W5c hover grind rail family

WSC-PLAN-009 is one catalogue family with three new, standalone static
GLBs: a 12 m level rail, a straight funbox descent, and a rail with one
turn toward the bowl. The 1.8 m platform and 3.5 m bowl lip in the existing
Hover Park static assembly inform the latter two rail starting heights;
all placement and non-flat dimensions are art proposals.

The continuous crown and mounts are separate meshes. Shared materials,
local origins and ground datums support visual fit-up. Each variant has a
worn steel crown, capped ends, braced posts and bolted foot plates. The
current scene's three 20 m straight rails remain untouched. No placement,
collider, catch, grind, scoring, or performance validation is claimed.

Rebuild in Blender 4.3.2 and check with standard Python:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/grind_rails.py -- /tmp/w5c
python scripts/blender/showcase-studies/check_grind_rails.py /tmp/w5c
```

Set `WSC_RAIL_RENDER=1` to reimport all three exact exports for the studio
comparison. The floor and lines appear only in the render. The three
GLBs total 223,772 bytes and 4,144 triangles. No baked textures, caches,
or duplicate Blender files are required to resume.
