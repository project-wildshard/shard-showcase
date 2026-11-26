"""Export the exact ramp core/rails in world Three coordinates."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

out=Path(sys.argv[sys.argv.index('--')+1])
s=bpy.context.scene
matches=[o for o in s.objects if o.type=='MESH' and 'ball ramp core exactly 24m by 4m by 6m' in o.name]
assert len(matches)==1,[o.name for o in matches]
o=matches[0]
mesh=o.data
mesh.calc_loop_triangles()
pts=[o.matrix_world@v.co for v in mesh.vertices]
assert min(v.x for v in pts)<-42 and max(v.x for v in pts)>-18
raw=(json.dumps({'vertices':[round(a,7) for v in pts for a in (v.x,v.z,-v.y)],
    'triangles':[i for t in mesh.loop_triangles if t.area>1e-8 for i in t.vertices]},separators=(',',':'))+'\n').encode()
out.write_bytes(raw)
print(len(pts),sum(t.area>1e-8 for t in mesh.loop_triangles),hashlib.sha256(raw).hexdigest())
