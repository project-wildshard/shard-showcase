# E12h / WSC-KIT-010: dormant haul stack

Optional static prop for the opening of the Titan intro, before anything
assembles. Eight instances of the tracked haul crate create a 6 m silhouette.
The hierarchy is eight independently editable nodes over one shared mesh, so
the package is almost the size of a single crate. This is not a proxy for the
Titan's body or its animation rig. Once that rig exists, the runtime handoff
from loose crates to the exact rig still needs to be authored and checked.

Import the GLB at identity in the isolated Titan arena, origin at slab
centre, +Y up. The crate graph has no materials beyond the donor's six.
No textures, moving pieces, collision, gameplay or lighting are exported.
Per-instance triangles are real draw cost; instancing here saves download
and mesh storage, not GPU triangle count.

From repository root, Blender 4.3.2:

```sh
O=/tmp/titan-stack
blender -b -t 4 --factory-startup --python-exit-code 1 --python scripts/blender/titan-crate-pile/build.py -- "$O"
WSC_STACK_RENDER=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/titan-crate-pile/review.py -- "$O"
cmp "$O/e12h-dormant-haul-stack.glb" public/assets/wildshard-art/e12h-dormant-haul-stack.glb
cmp "$O/e12h-dormant-haul-stack-proof.json" project/layouts/e12h-dormant-haul-stack-proof.json
```

Omit `WSC_STACK_RENDER` for checks without rendering. Review pins the
original bowl and sky, verifies the 6 m height, checks for same-tier overlap
and proximity to the slab or tier below (169 downward samples per crate),
and checks framing at eye height and from the side. The existing center
finish overlaps the bottom skids by 25 mm in this visual placement. These are visual fit
checks, not rigid-body stability or a live camera path. Render lighting is
preview-only.
