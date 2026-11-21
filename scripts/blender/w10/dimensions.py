import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent;out={}
for f in sorted(p.glob('*.glb')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(f))
 pts=[o.matrix_world@Vector(c) for o in bpy.context.scene.objects if o.type=='MESH' for c in o.bound_box]
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 assert abs(lo[2])<.001
 out[f.name]={'blender_xyz_min':lo,'blender_xyz_max':hi,'width_depth_height_m':[round(hi[i]-lo[i],4) for i in range(3)],'ground_origin':'z=0 (glTF Y=0)','roundtrip_import':'PASS'}
(p/'dimensions.json').write_text(json.dumps(out,indent=2));print(out)
