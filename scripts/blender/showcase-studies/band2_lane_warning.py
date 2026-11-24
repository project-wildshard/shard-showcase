"""E2 static red-lane art proposal; separate meshes, no actor or gameplay."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

out=output_directory()
asset=out/'e2-charge-lane-warning.glb'
crate=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art/haul-crate.glb'
assert hashlib.sha256(crate.read_bytes()).hexdigest()=='d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44'
clear_scene()
s=bpy.context.scene
width,length=1.70,8.40    # Visual review dimensions only.
edge=.85
def mat(n,c,rough=.68,emit=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*c,1)),('Roughness',rough),
                ('Emission Color',(*c,1)),('Emission Strength',emit)]:
        p.inputs[k].default_value=v
    return m
ink=mat('Red warning ink',(.35,.030,.018),.77,0)
red=mat('Hot red outline',(.84,.05,.034),.62,.63)
bright=mat('Pale directional enamel',(1,.67,.44),.61,.38)
def polygon(n,xy,z,m):
    verts=[(*p,z) for p in xy]
    if sum(x*y2-x2*y for (x,y),(x2,y2) in zip(xy,xy[1:]+xy[:1]))<0:verts.reverse()
    me=bpy.data.meshes.new(n);me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update()
    o=bpy.data.objects.new(n,me);s.collection.objects.link(o);me.materials.append(m);return o
def rect(n,x0,x1,y0,y1,z,m):
    return polygon(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z,m)
parts=[]
for side in (-1,1):
    def cross(x0,x1):return sorted((side*x0,side*x1))
    lo,hi=cross(.752,edge)
    parts.append(rect('Outer dark keyline',lo,hi,0,length,.003,ink))
    lo,hi=cross(.784,.829)
    parts.append(rect('Continuous red rail',lo,hi,.035,length-.035,.004,red))
    lo,hi=cross(.582,.735)
    for y in (.12,1.57,3.02,4.47,5.92,7.37):
        parts.append(rect('Range pulse dash',lo,hi,y,y+.27,.004,red))
for y in (1.05,2.73,4.41,6.09,7.77):
    points=[(-.49,y-.20),(0,y+.19),(.49,y-.20),(.36,y-.25),(0,y+.028),(-.36,y-.25)]
    parts.append(polygon('Directional chevron',points,.0048,bright))
for y in (.02,8.34):
    parts.append(rect('Transverse end cap',-.75,.75,y,y+.045,.004,red))
export(parts,asset)

def load(path,off=(0,0,0)):
    prior=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects=sorted(set(s.objects)-prior,key=lambda o:o.name)
    for o in objects:
        if o.parent is None:o.location+=Vector(off)
    bpy.context.view_layer.update()
    return objects

clear_scene()
proof_parts=load(asset)
coords=[o.matrix_world@v.co for o in proof_parts if o.type=='MESH' for v in o.data.vertices]
assert abs(max(q.x for q in coords)-edge)<1e-5 and abs(min(q.x for q in coords)+edge)<1e-5
assert abs(max(q.y for q in coords)-length)<1e-5 and abs(min(q.y for q in coords))<1e-5
assert .0029<min(q.z for q in coords) and max(q.z for q in coords)<.0049
for o in proof_parts:
    if 'chevron' in o.name.lower():
        p=[o.matrix_world@v.co for v in o.data.vertices]
        a=max(p,key=lambda q:q.y)
        assert abs(a.x)<1e-4 and a.y>max(q.y for q in p if abs(q.x)>.1)
stage=mat('Dusty slate yard',(.16,.192,.192),.85)
def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.data.materials.append(m)
    return o
box('Stage planar ground',(0,0,-.075),(95,95,.15),stage)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
# Rays start below marks to test all staged grade points at exact local XY.
ground_hits=0
for y in [.02,1.2,2.4,3.6,4.8,6,7.2,8.39]:
    for x in (-edge,0,edge):
        h,p,*_=s.ray_cast(dg,Vector((x,y,.002)),Vector((0,0,-1)),distance=.05)
        assert h and abs(p.z)<1e-5
        ground_hits+=1
proof={'candidate_size_m':[width,length],'mark_offset_m':[.003,.0048],
       'floor_sample_count':ground_hits,'local_gltf_direction':'-Z',
       'source_plan_telegraph_s':.9,'visual_duration_implemented':False,
       'native_gameplay':False}
(out/'e2-lane-warning-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

for p in ((-2.67,7.8,0),(-2.67,9.42,0),(2.91,8.26,0),(2.91,9.94,0)):
    load(crate,p)
wall=mat('Kept 3 m sight-wall staging',(.223,.246,.239),.76)
steel=mat('Folded cover seam',(.090,.13,.14),.62)
box('Staged Band 2 cover wall',(0,12.1,1.5),(8.5,.67,3),wall)
for x in (-3.78,-2.53,-1.28,0,1.28,2.53,3.78):
    box('Cover wall seam',(x,11.748,1.47),(.043,.037,2.86),steel)
for i in range(8):
    y=.4+i*1.42
    for x in (-3.65,3.65):
        rect('Yard seam, not a warning',x-.29,x+.29,y,y+.026,.002,steel)
def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.23,.32,.40,1);bg.inputs[1].default_value=.40
for p,t,w,c,sz in [
    ((-4,1,7),(0,6,0),1400,(.61,.79,1),6),
    ((7,10,7),(0,3,0),1900,(1,.74,.56),8)
]:
    bpy.ops.object.light_add(type='AREA',location=p)
    o=bpy.context.object;o.data.energy=w;o.data.color=c;o.data.size=sz;aim(o,t)
bpy.ops.object.camera_add()
s.camera=bpy.context.object
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x=1320;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
for name,eye,target,f in [
    ('e2-lane-reader',(2.37,-2.3,1.7),(.15,4.15,.18),38),
    ('e2-lane-shape',(-4.9,.7,8.9),(0,4.7,0),34),
]:
    s.camera.location=eye;aim(s.camera,target);s.camera.data.lens=f
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
