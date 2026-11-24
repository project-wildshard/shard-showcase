"""W6b static dark/aqua direction marks for the exact WSC-PROP-037 belt."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
root=Path(__file__).resolve().parents[3]
belt=root/'public/assets/wildshard-art/wsc-prop-037-conveyor-module.glb'
marker=out/'wsc-prop-037-conveyor-direction.glb'
sha='1d0d5e0ac6fb0fd201daef538ed3e277824a2a0f6b9677968fe2f8dbb18debdb'
assert hashlib.sha256(belt.read_bytes()).hexdigest()==sha

# Verify against the established reconstructed transforms, not the wider historic proxies.
movers=root/'scripts/blender/west-movers-roof/movers.py'
assert "for i,x in enumerate([-84,-90,-96]):put(belt,'Station1 static belt '+str(i+1),x,103,.10,0 if i%2==0 else math.pi)" in movers.read_text()
poses=[(-84,103,.10,0),(-90,103,.10,math.pi),(-96,103,.10,0)]

def load(path,pose=(0,0,0,0)):
    past=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objs=sorted(set(bpy.context.scene.objects)-past,key=lambda o:o.name)
    T=Matrix.Translation(pose[:3])@Matrix.Rotation(pose[3],4,'Z')
    for o in objs:
        if o.parent is None:o.matrix_world=T@o.matrix_world
    bpy.context.view_layer.update()
    return objs

def material(n,c,rough=.66,metal=0,emit=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*c,1)),('Emission Strength',emit)]:
        q.inputs[k].default_value=v
    return m

def mesh(n,points,faces,m):
    a=bpy.data.meshes.new(n)
    a.from_pydata(points,[],faces)
    a.update()
    o=bpy.data.objects.new(n,a)
    bpy.context.collection.objects.link(o)
    a.materials.append(m)
    return o

def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    return o

def points(objs):
    return [o.matrix_world @ v.co for o in objs if o.type=='MESH' for v in o.data.vertices]

clear_scene()
scene=bpy.context.scene
b=load(belt)
bp=points(b)
assert abs(max(v.z for v in bp)-.4205)<1e-5
assert abs((max(v.x for v in bp)-min(v.x for v in bp))-4.768)<1e-5
assert abs((max(v.y for v in bp)-min(v.y for v in bp))-1.696)<1e-5
ink=material('Ink outline',(.010,.035,.040),.84)
paint=material('Directional aqua enamel',(.12,.84,.73),.68,.055,.16)
# Rows sit outside the donor's central 45 mm dash strip. Tip is local -X.
outline=[(-.45,0),(-.11,-.231),(-.11,-.102),(.412,-.102),
         (.412,.102),(-.11,.102),(-.11,.231)]
faces=tessellate_polygon([[Vector((x,y,0)) for x,y in outline]])
# Blender 4.x tessellation yields input vertex indices.
indices=[tuple(f) for f in faces]
sample=[(i,j) for i in (-1.28,0,1.28) for j in (-.33,.33)]
rayref=bpy.context.evaluated_depsgraph_get()
hits=[]
for x,y in sample:
    for dx,dy in outline+[(0,0),(.21,0),(-.18,0)]:
        hit,pos,_,_,obj,_=scene.ray_cast(rayref,Vector((x+dx,y+dy,1)),Vector((0,0,-1)),distance=1)
        assert hit and obj and any('Rubber tread' in m.name for m in obj.data.materials), (x,y,dx,dy,obj)
        hits.append(pos.z)
assert min(hits)>.36 and max(hits)<.421
z=.422
objects=[]
for i,(x,y) in enumerate(sample):
    for suffix,scale,dz,m in [('keyline',1,0,ink),('inlay',.85,.0004,paint)]:
        vs=[(x+dx*scale,y+dy*scale,z+dz) for dx,dy in outline]
        triangles=indices
        if (Vector(vs[triangles[0][1]])-Vector(vs[triangles[0][0]])).cross(
                Vector(vs[triangles[0][2]])-Vector(vs[triangles[0][0]])).z<0:
            triangles=[tuple(reversed(t)) for t in triangles]
        o=mesh(f'Arrow {i+1} {suffix}',vs,triangles,m)
        assert all(p.normal.z>.99 for p in o.data.polygons)
        objects.append(o)
export(objects,marker)
clear_scene()
p=points(load(marker))
assert abs(max(v.z for v in p)-.4224)<1e-5
assert max(abs(v.y) for v in p)<.563
assert max(abs(v.x) for v in p)<1.74
directions=[]
for pose in poses:
    direction=Matrix.Rotation(pose[-1],3,'Z') @ Vector((-1,0,0))
    directions.append(round(direction.x))
assert directions==[-1,1,-1]
metrics=dict(course_poses=poses,preview_world_x_directions=directions,tread_hits=len(hits),
             tread_hit_height_range=[min(hits),max(hits)],mark_plane_y=[.422,.4224],
             model_tread_max_y=.4195,donor_clear_gap_m=1.232,
             cue="Art-only: positive motion is defined towards the course progression (west) for this preview. No engine axis, speed or UV behavior.")
(out/'conveyor-direction.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(metrics)
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)
clear_scene()

for pose in poses:
    load(belt,pose)
    load(marker,pose)
slab=material('Boardformed concrete',(.22,.249,.245),.74)
dark=material('Sealed yard',(.058,.079,.079),.73)
amber=material('Worn line ochre',(.59,.295,.058),.65)
box('Existing 20 m Station 1 slab',(-90,103,.045),(20,5,.09),slab)
box('Staging ground',(-90,103,-.125),(190,190,.24),dark)
for y in [101.44,104.56]:
    for x in range(-98,-80,2):
        box('Illustrative safety paint',(x,y,.091),(.56,.043,.002),amber)
for (x,y) in [(-81,101.04),(-81,104.96),(-99,101.04),(-99,104.96)]:
    box('Illustrative recessed bolt',(x,y,.093),(.19,.19,.006),dark)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

s=bpy.context.scene
w=s.world;w.use_nodes=True
w.node_tree.nodes.get('Background').inputs[0].default_value=(.19,.29,.35,1)
w.node_tree.nodes.get('Background').inputs[1].default_value=.36
bpy.ops.object.light_add(type='SUN',location=(-79,94,11))
o=bpy.context.object
aim(o,(-89,104,0));o.data.energy=2.9;o.data.angle=.22;o.data.color=(1,.78,.48)
bpy.ops.object.light_add(type='AREA',location=(-95,106,6))
o=bpy.context.object
aim(o,(-90,103,.5));o.data.energy=1600;o.data.size=9;o.data.color=(.52,.74,1)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x=1440;s.render.resolution_y=860;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
s.view_settings.view_transform='AgX'
bpy.ops.object.camera_add()
s.camera=bpy.context.object
for name,eye,target,lens in [
    ('conveyor-approach',(-78.7,96.45,1.71),(-89.7,102.95,.36),38),
    ('conveyor-direction-review',(-80.35,93.3,8.45),(-90.1,103,.36),40),
]:
    s.camera.location=eye
    aim(s.camera,target)
    s.camera.data.lens=lens
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
