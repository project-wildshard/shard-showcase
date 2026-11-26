"""Reimport the eight shared crate nodes and frame the still E12h opening."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import struct

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

here=Path(__file__).resolve()
os.environ['WSC_STANDS_RAYS_ONLY']='1'
base=runpy.run_path(str(here.parent.parent/'showcase-studies/titan_stands_review.py'))
S,O,C,aim,light,bowl=[base[k] for k in ('S','O','C','aim','lamp','bvh')]
A=here.parents[3]/'public/assets/wildshard-art'
skyfile=A/'e12h-titan-interior-sky.glb'
skypin='a18d14cb35ee4dc1eac30e75882b6b877cbd768cedf99c1bedb64852f6b249fe'
assert hashlib.sha256(skyfile.read_bytes()).hexdigest()==skypin
for o in S.objects:
    if 'scale-only guide' in o.name:
        o.hide_render=True
base['ground'].hide_render=True
base['sky'].inputs[1].default_value=0
before=set(S.objects)
bpy.ops.import_scene.gltf(filepath=str(skyfile))
sky,=set(S.objects)-before
for flag in ('shadow','diffuse','glossy','transmission','volume_scatter'):
    setattr(sky,'visible_'+flag,False)
before=set(S.objects)
p=O/'e12h-dormant-haul-stack.glb'
raw=p.read_bytes()
j=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(j['meshes'])==1 and len(j['nodes'])==8
assert not any(k in j for k in ('animations','images','textures','skins'))
bpy.ops.import_scene.gltf(filepath=str(p))
bpy.context.view_layer.update()
crates=sorted(set(S.objects)-before,key=lambda o:o.name)
source=json.loads((O/'stack-source.json').read_text())
assert [o.name for o in crates]==[row['name'] for row in source['placements']]
assert len({o.data for o in crates})==1
def shape(o):
    mesh=o.data
    mesh.calc_loop_triangles()
    v=[o.matrix_world@q.co for q in mesh.vertices]
    f=[tuple(q.vertices) for q in mesh.loop_triangles]
    lim=[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)]
    return (v,f,lim,BVHTree.FromPolygons(v,f,all_triangles=True))
shapes={o.name:shape(o) for o in crates}
tops={row['name']:row['layer'] for row in source['placements']}
verts=[v for pts,_,_,_ in shapes.values() for v in pts]
axis=[[min(v[k] for v in verts),max(v[k] for v in verts)] for k in range(3)]
assert abs(axis[2][0])<.0001 and abs(axis[2][1]-6)<.0001
assert max(math.hypot(v.x,v.y) for v in verts)<4.2
stats=[]
for name,(_,_,(xr,yr,zr),_) in shapes.items():
    tier=tops[name]
    for other,(_,_,(ux,uy,uz),_) in shapes.items():
        if other<=name or tops[other]!=tier:
            continue
        assert max(xr[0],ux[0])>=min(xr[1],ux[1])-.0001 or max(yr[0],uy[0])>=min(yr[1],uy[1])-.0001
    supports=[bowl] if tier==1 else [s[3] for n,s in shapes.items() if tops[n]==tier-1]
    distances=[]
    for i in range(13):
        for k in range(13):
            pos=Vector((xr[0]+(xr[1]-xr[0])*(i+.5)/13,yr[0]+(yr[1]-yr[0])*(k+.5)/13,zr[0]+.03))
            hits=[b.ray_cast(pos,Vector((0,0,-1)),.22)[3] for b in supports]
            if any(d is not None for d in hits):
                distances.append(min(d for d in hits if d is not None)-.03)
    assert len(distances)>=65 and -.026<=min(distances)<.12,(name,len(distances),distances[:1])
    stats.append({'node':name,'valid_overlap_samples':len(distances),'total_samples':169,
                  'nearest_slab_or_lower_roof_m':round(min(distances),4)})
ntri=len(next(iter(shapes.values()))[1])
S.render.image_settings.file_format='WEBP'
S.render.image_settings.quality=88
S.cycles.samples=30
S.cycles.adaptive_threshold=.045
light('Warm loading fixture preview',(-7,-9,11),(0,0,3),4500,8,(1,.61,.35))
light('Cool reflected fill preview',(6,4,10),(0,0,3),2800,7,(.49,.76,1))
views={}
for key,xyz,target,dims,fov in (
    ('opening',(1.9,-17.8,1.72),(0,0,3.25),(900,1500),43),
    ('footing',(13,-13,6.5),(0,0,2.7),(1240,840),34),
):
    C.lens=24/(2*math.tan(math.radians(fov)/2))
    S.camera.location=xyz
    aim(S.camera,target)
    S.render.resolution_x,S.render.resolution_y=dims
    bpy.context.view_layer.update()
    projections=[world_to_camera_view(S,S.camera,v) for v in verts]
    assert all(.015<v.x<.985 and .015<v.y<.985 and v.z>0 for v in projections),(key,[(min(v[i] for v in projections),max(v[i] for v in projections)) for i in range(3)])
    cx=[v.x for v in projections]
    cy=[v.y for v in projections]
    views[key]={'camera_xyz_m':xyz,'screen_bounds_xy':[[round(min(v),4),round(max(v),4)] for v in (cx,cy)]}
    if os.environ.get('WSC_STACK_RENDER')=='1':
        S.render.filepath=str(O/f'nov26-titan-haul-stack-{key}.webp')
        bpy.ops.render.render(write_still=True)
proof={'scope':'E12h opening set prop. Static optional GLB; no assembled Titan, animation, collision, timeline or game installation.',
       'bowl_sha256':base['PIN'],'sky_sha256':skypin,'export_sha256':hashlib.sha256(raw).hexdigest(),
       'bytes':len(raw),'mesh_definitions':1,'material_primitives':6,'unique_triangles':ntri,
       'visible_triangles_at_full_stack':ntri*len(crates),'bounds_xyz_m':[[round(x,4) for x in par] for par in axis],
       'placements':source,'vertical_overlap_probes':stats,'views':views}
(O/'e12h-dormant-haul-stack-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('E12h stack validated',ntri,'unique triangles across eight nodes',axis)
