"""E12h shot 1: a stationary stack of the tracked haul crate; no actor geometry."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'public/assets/wildshard-art/haul-crate.glb'
PIN='d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44'
assert hashlib.sha256(D.read_bytes()).hexdigest()==PIN
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(D))
source,=[o for o in bpy.context.scene.objects if o.type=='MESH']
mesh=source.data
mesh.name='Shared haul crate | exact donor topology'
vertices=[source.matrix_world @ v.co for v in mesh.vertices]
assert source.matrix_world.is_identity
lo=Vector([min(v[i] for v in vertices) for i in range(3)])
hi=Vector([max(v[i] for v in vertices) for i in range(3)])
assert abs(lo.z)<1e-6
dims=hi-lo
bpy.data.objects.remove(source,do_unlink=True)

# Footprint cells are separated within each tier. Rotations make the cargo
# insignia face several angles without changing the mesh or adding decals.
# Each third of the height includes the donor's skids and braces.
tiers=(
    (2.25,((-1.58,-1.48,2.94,2.72,0),(1.44,-1.42,2.74,2.62,180),
           (-1.53,1.39,2.84,2.68,180),(1.49,1.40,2.68,2.58,0))),
    (2.04,((-.91,-1.05,2.60,2.06,180),(1.08,1.11,2.42,2.10,0),
           (-1.65,1.25,2.35,2.13,0))),
    (1.71,((-.72,.60,2.15,2.02,0),)),
)
placements=[]
z=0
for layer,(h,cells) in enumerate(tiers,1):
    for i,(x,y,w,d,rot) in enumerate(cells,1):
        ob=bpy.data.objects.new(f'Tier {layer} | haul crate {i}',mesh)
        bpy.context.scene.collection.objects.link(ob)
        ob.location=(x,y,z)
        ob.scale=(w/dims.x,d/dims.y,h/dims.z)
        ob.rotation_euler.z=math.radians(rot)
        placements.append({'name':ob.name,'layer':layer,'slab_local_xyz':[x,y,z],
                           'dimensions_m':[w,d,h],'blender_yaw_deg':rot})
    z+=h
bpy.context.view_layer.update()
p=OUT/'e12h-dormant-haul-stack.glb'
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',export_yup=True,
                         export_cameras=False,export_lights=False,export_animations=False)
b=p.read_bytes()
j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert len(j['nodes'])==8 and len(j['meshes'])==1 and len(j['materials'])==6
assert not any(k in j for k in ('textures','images','animations','skins'))
(OUT/'stack-source.json').write_text(json.dumps({'donor_sha256':PIN,'placements':placements},indent=2)+'\n')
