"""E8d: two proposed cache trophies, with static locked/earned artwork."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory
out=output_directory()
clear_scene()
scene=bpy.context.scene
def mat(name,color,metal=0,rough=.55):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m
brass=mat('Warm bronze alloy',(.53,.268,.064),.72,.35)
gold=mat('Worn golden face',(.83,.56,.18),.65,.37)
jade=mat('Oxidised petrol enamel',(.034,.249,.235),.27,.49)
iron=mat('Blackened steel',(.062,.086,.099),.51,.43)
ink=mat('Locked silhouette · graphite',(.035,.039,.038),0,.81)
wall=mat('Warm wall backdrop',(.37,.281,.182),.0,.78)
def piece(name,outline,front,back,ma):
    n=len(outline)
    v=[(x,y,z) for y in (back,front) for x,z in outline]
    f=[tuple(range(n)),tuple(reversed(range(n,n*2)))]
    f += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    d=bpy.data.meshes.new(name)
    d.from_pydata(v,[],f)
    d.update()
    d.materials.append(ma)
    o=bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    return o
def rect(x,z,w,h,e):
    a,b=w/2,h/2
    return [(x-a+e,z-b),(x+a-e,z-b),(x+a,z-b+e),(x+a,z+b-e),
            (x+a-e,z+b),(x-a+e,z+b),(x-a,z+b-e),(x-a,z-b+e)]
def radial(n,r,x=0,z=0,phase=0):
    return [(x+r*math.cos(phase+i*math.tau/n),z+r*math.sin(phase+i*math.tau/n)) for i in range(n)]
def merge(n,obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.object.join()
    o=obs[0]
    o.name=n
    o.data.name=n
    return o
mark1=[piece('Compass medallion',radial(16,.204),.044,0,brass),
       piece('Octagonal enamel',radial(8,.170,phase=math.pi/8),.060,.038,jade)]
# A pointed patinated compass emblem, an art motif, not an existing item reward.
star=[(math.cos(i*math.pi/4)*(.152 if i%2==0 else .057),
       math.sin(i*math.pi/4)*(.152 if i%2==0 else .057)) for i in range(8)]
mark1+=[piece('Raised star',star,.077,.058,gold),piece('Center rivet',radial(8,.024),.092,.075,iron)]
mark2=[piece('Relic plaque',rect(0,0,.365,.407,.070),.047,0,iron),
       piece('Set enamel panel',rect(0,0,.316,.349,.057),.067,.042,jade)]
# Three relief panels evoke a cache lock without modeling a working lock.
mark2+=[piece('Brass clasp',rect(0,.064,.211,.096,.015),.094,.063,brass),
        piece('Keyhole motif',[(0,.071),(.020,.049),(.013,.021),(.022,-.035),
                              (-.022,-.035),(-.013,.021),(-.020,.049)],.099,.090,iron)]
for s in (-1,1):
    mark2.append(piece('Lacquered rails',rect(s*.102,-.062,.032,.127,.007),.084,.065,gold))
a,b=merge('Cache I · Compass medallion',mark1),merge('Cache II · Relic plaque',mark2)
b.location.x=.60
file=out/'cache-trophy-marks.glb'
export([a,b],file)
raw=file.read_bytes()
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
assert len(d['meshes'])==2 and len(raw)<27000 and tri<800
assert not any(d.get(k) for k in ('images','animations','skins'))
for o in (a,b):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(file))
marks=sorted([o for o in scene.objects if o.type=='MESH'],key=lambda o:o.name)
assert len(marks)==2
donor=HERE.parents[2]/'public/assets/wildshard-art/west-plaza-empty-mounts.glb'
seal='3e7e28863742ebcdd2f494d97d98574d263d876dac01f03e21a2b0fd5b4a54c7'
assert hashlib.sha256(donor.read_bytes()).hexdigest()==seal
formed=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(donor))
frames=sorted(set(scene.objects)-formed,key=lambda o:o.name)
assert len(frames)==12 and len({o.data for o in frames})==1
for o in frames[2:]:bpy.data.objects.remove(o,do_unlink=True)
gaps=[]
for i,(item,frame) in enumerate(zip(marks,frames[:2])):
    center=(i-.5)*1.25
    frame.matrix_world=Matrix.Translation((center,0,1.42))
    item.matrix_world=Matrix.Translation((center,.040,1.42))
    bpy.context.view_layer.update()
    v=[item.matrix_world@p.co for p in item.data.vertices]
    f=[frame.matrix_world@p.co for p in frame.data.vertices]
    gap=min(p.y for p in v)-max(p.y for p in f)
    horiz=.259-max(abs(p.x-center) for p in v)
    vert=.259-max(abs(p.z-1.42) for p in v)
    assert gap>.007 and horiz>.05 and vert>.05,(gap,horiz,vert)
    gaps.append([round(x,5) for x in (gap,horiz,vert)])
piece('Framing plaster',rect(0,1.35,4.5,2.5,.02),-.030,-.16,wall)
for x in (-1.59,1.59):
    piece('Reeded wall trim',rect(x,1.35,.12,2.12,.02),.08,-.125,brass)
def lamp(name,p,t,power,color,size):
    d=bpy.data.lights.new(name,'AREA')
    d.energy,d.size,d.color=power,size,color
    o=bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location=p
    o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
lamp('Warm gallery source',(-2,2.8,3.23),(0,0,1.35),230,(1,.77,.56),3.0)
lamp('Plaza sky fill',(1.7,2.9,2.2),(0,0,1.45),138,(.72,.86,1),2.6)
bpy.ops.object.camera_add(location=(.10,3.8,1.89))
cam=bpy.context.object
scene.camera=cam
cam.rotation_euler=(Vector((0,0,1.36))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=49
scene.render.engine='CYCLES'
scene.cycles.samples=38
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.075
scene.cycles.use_denoising=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.resolution_x,scene.render.resolution_y=1320,840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=91
silhouettes=[]
for i,outline in enumerate((radial(16,.204),rect(0,0,.365,.407,.070))):
    o=piece('Flat locked cutout',outline,.005,0,ink)
    o.location=((i-.5)*1.25,.040,1.42)
    silhouettes.append(o)
for tag in ('locked','earned'):
    for o in marks:o.hide_render=tag=='locked'
    for o in silhouettes:o.hide_render=tag=='earned'
    scene.render.filepath=str(out/f'nov24-cache-trophy-{tag}.jpg')
    if not os.environ.get('WILDSHARD_VALIDATE_ONLY'):bpy.ops.render.render(write_still=True)
(out/'cache-trophy-validation.json').write_text(json.dumps({
    'frame_sha256':seal,'asset_bytes':len(raw),'asset_triangles':tri,
    'asset_sha256':hashlib.sha256(raw).hexdigest(),'gap_depth_width_height_m':gaps,
    'plaza_map_changed':False,'actual_item_or_unlock':False,
},indent=2)+'\n')
