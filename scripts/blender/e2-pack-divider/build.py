"""E2 sight-break add-on, built and checked on the exact existing MODULE-020."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/blender/showcase-studies'))
from common import clear_scene, export, output_directory

out=output_directory()
donor=ROOT/'public/assets/wildshard-art/wsc-module-020-corrugated-yard-wall.glb'
pin='b91f2dd3ccfebab574f5dfb682db6bfc04ea4bd1a2d56e53482e2a219bc52153'
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
clear_scene()
scene=bpy.context.scene

def material(n,c,metal):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=.56
    m.diffuse_color=(*c,1)
    return m

steel=material('Graphite framing',(.047,.062,.072),.46)
orange=material('Baked ochre enamel',(.46,.105,.020),.19)
grey=material('Galvanized zinc edges',(.202,.249,.271),.51)
parts=[]

def box(n,c,d,m,r=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=c)
    ob=bpy.context.object
    ob.name=n
    ob.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(m)
    if r:
        mod=ob.modifiers.new('Stamped edge','BEVEL')
        mod.width=r
        mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(ob)

box('Opaque crown panel',(0,.010,2.75),(2.375,.100,.468),steel)
box('Folded top lip',(0,.010,2.985),(2.375,.318,.030),grey)
for side in (-1,1):
    x=side*1.11375
    box('Opaque seam plate',(x,.010,1.496),(.1475,.085,2.992),steel)
    box('Seam channel lip',(side*1.083,.011,1.51),(.035,.264,2.904),grey,.003)
    box('End clamp',(side*1.029,.015,2.739),(.139,.300,.278),grey,.008)
for facing in (-1,1):
    for i in range(10):
        x=(i-4.5)*.190
        box('Orange raised cassette',(x,.010+facing*.069,2.816),(.176,.039,.253),orange,.009)
    box('Receiver angle',(0,.010+facing*.103,2.615),(2.051,.076,.054),grey,.006)
    for sign in (-1,1):
        for z in (.34,1.65,2.17,2.74):
            box('Blind rivet', (sign*1.137,.010+facing*.066,z),(.025,.035,.024),grey,.005)

bpy.ops.object.select_all(action='DESELECT')
for ob in parts: ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
obj=bpy.context.object
obj.name='E2 | 3 m crown and seam kit'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
path=out/'e2-pack-divider-crown.glb'
export([obj],path)
clear_scene()

def load(p,x=0,y=0):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    loaded=sorted(set(scene.objects)-before,key=lambda ob:ob.name)
    for ob in loaded:
        if ob.parent is None:
            ob.matrix_world=Matrix.Translation((x,y,0))@ob.matrix_world
    bpy.context.view_layer.update()
    return loaded

def mesh_data(obs):
    verts, faces=[],[]
    for ob in obs:
        if ob.type!='MESH': continue
        faces.extend(tuple(i+len(verts) for i in p.vertices) for p in ob.data.polygons)
        verts.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
    return verts,faces

def bvh(obs):
    return BVHTree.FromPolygons(*mesh_data(obs))

center=load(path)
v,_=mesh_data(center)
assert abs(max(p.z for p in v)-3)<1e-6
assert min(v.y for v in v)>=-.167 and max(v.y for v in v)<=.2375
assert abs(max(p.x for p in v)-1.1875)<1e-6 and abs(min(p.x for p in v)+1.1875)<1e-6
old=[]
up=list(center)
for x in (-2.375,0,2.375):
    old+=load(donor,x)
    if x: up+=load(path,x)

base=bvh(old)
full=bvh(old+up)
levels=(.09,.55,.98,1.4,1.70,2.25,2.58,2.78,2.95)
by_height={z:[0,0] for z in levels}
old_hits=0
samples=0
for direction in (-1,1):
    for x in [i*.0475 for i in range(-74,75)]+[s*(1.1875+d) for s in (-1,1) for d in (-.001,0,.001)]:
        for z in levels:
            a=Vector((x,-4*direction,z))
            b=Vector((0,direction,0))
            hit=base.ray_cast(a,b,8)[0] is not None
            old_hits+=hit
            by_height[z][0]+=hit
            by_height[z][1]+=1
            assert full.ray_cast(a,b,8)[0] is not None,(direction,x,z)
            samples+=1
for x in (-4,0,4):
    assert full.ray_cast((x,-4,3.03),(0,1,0),8)[0] is None
for side in (-1,1):
    # Nothing pokes out beyond the three-bay length.
    assert full.ray_cast((side*3.575,-4,1.4),(0,1,0),8)[0] is None

raw=path.read_bytes()
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
p=doc['meshes'][0]['primitives']
tri=sum(doc['accessors'][q['indices']]['count']//3 for q in p)
assert len(p)==3 and tri<1900 and len(raw)<155000 and not doc.get('textures')
rec={'donorSHA256':pin,'pitchM':2.375,'heightM':3,'testSpanM':7.125,
     'rays':{'count':samples,'originalHits':old_hits,'assembledHits':samples,'clearControls':5},
     'heightBreakdown':[{'heightM':z,'originalHits':n,'assembledHits':total} for z,(n,total) in by_height.items()],
     'export':{'bytes':len(raw),'triangles':tri,'primitives':len(p),'sha256':hashlib.sha256(raw).hexdigest()},
     'scope':'local art fixture, not placed; no collision, perception, or gameplay changes'}
(out/'proof.json').write_text(json.dumps(rec,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'divider-review.blend'))
print(json.dumps(rec))
