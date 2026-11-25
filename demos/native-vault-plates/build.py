"""Extract the exact Room 1 contact triangles and make a recessed plate option."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'scripts/blender/showcase-studies'))
from common import clear_scene, export, output_directory

out=output_directory()
layout=json.loads((root/'project/layouts/e10c-vault-room-01.json').read_text())
assets=root/'public/assets/wildshard-art'
n=assets/layout['sources']['plate']['file']
assert hashlib.sha256(n.read_bytes()).hexdigest()==layout['sources']['plate']['sha256']
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(n))
bpy.context.view_layer.update()
meshes=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name)
assert [o.name for o in meshes]==['Fixed_Frame','Moving_Tread']

def geometry(o, transform=None, dz=0):
    m=(transform @ o.matrix_world) if transform is not None else o.matrix_world
    o.data.calc_loop_triangles()
    vertices=[m @ v.co for v in o.data.vertices]
    return {'name':o.name,'v':[round(v,6) for p in vertices for v in (p.x,p.z-dz,-p.y)],
            't':[i for t in o.data.loop_triangles for i in t.vertices]}

plates={}
for p in layout['placements']:
    if p['asset']!='plate':continue
    transform=Matrix.Translation(p['origin_m'])@Matrix.Scale(p['uniform_scale'],4)
    plates[p['name']]=[geometry(o,transform,p['tread_travel_mm']/1000 if o.name=='Moving_Tread' else 0) for o in meshes]

# Alternate insert: retain the 2 m frame and 1.77 m tread outline. Only Z is
# compressed, with a 0.8 mm veneer above the old floor to avoid coplanar shading.
# Mechanics use one uninterrupted floor plane; the veneer is not the collider.
scale=.036/.17125
for o in meshes:
    o.matrix_world=Matrix.Translation((0,0,.0008))@Matrix.Diagonal((.5,.5,.5*scale,1))@o.matrix_world
    hi=max((o.matrix_world @ v.co).z for v in o.data.vertices)
    if o.name=='Fixed_Frame':
        o.location.z-=hi+.0006
    else:
        o.location.z-=hi-.0008
export(meshes,out/'e10c-vault-flush-plate.glb')
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(out/'e10c-vault-flush-plate.glb'))
bpy.context.view_layer.update()
parts={o.name:geometry(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert sorted(parts)==['Fixed_Frame','Moving_Tread']
for name,span in [('Fixed_Frame',2),('Moving_Tread',1.77)]:
    g=parts[name]['v']; assert abs(max(g[::3])-min(g[::3])-span)<1e-6
    assert abs(max(g[2::3])-min(g[2::3])-span)<1e-6
assert max(parts['Moving_Tread']['v'][1::3])==.0008
(out/'geometry.json').write_text(json.dumps({'plates':plates,'flushVisual':parts},separators=(',',':'))+'\n')
