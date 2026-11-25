"""Pin and reimport the W10b rail at the first westbound R02 jump."""
import bpy
import hashlib
import json
import math
from mathutils import Matrix
from pathlib import Path
import sys

path=Path(__file__).resolve().parents[2]/"public/assets/wildshard-art/w10b-reusable-riding-jump-wip.glb"
assert hashlib.sha256(path.read_bytes()).hexdigest()=="0881ec693a68897ff8eadc60cd648237ec8bd969c4d05c7fd6faef09445c3680"
out=Path(sys.argv[sys.argv.index("--")+1])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(path))
bpy.context.view_layer.update()
placement=Matrix.Translation((-125,148,.025))@Matrix.Rotation(math.pi/2,4,"Z")
parts=[]
for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
    if o.type!="MESH":continue
    mesh=o.data
    mesh.calc_loop_triangles()
    pts=[placement@o.matrix_world@v.co for v in mesh.vertices]
    verts=[round(a,7) for x,y,z in pts for a in (x,z,-y)]
    parts.append({"name":o.name,"v":verts,"t":[i for tri in mesh.loop_triangles for i in tri.vertices]})
out.write_text(json.dumps(parts,separators=(",",":"))+"\n")
