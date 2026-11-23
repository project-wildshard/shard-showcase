"""W10a trough: small portable mesh ripple loop, same inset and basin."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
trough=assets/'w10a-paddock-trough-wip.glb'
assert hashlib.sha256(trough.read_bytes()).hexdigest()=='ff0e65ffce361608b0872bd9368bdcced1b19f00d635c460dc6c3dcb6430d56d'
out=output_directory()
dst=out/'wsc-prop-079-trough-ripple.glb'
s=bpy.context.scene
clear_scene()
s.render.fps=24
s.frame_start,s.frame_end=0,72

def mat(n,c,rough=.68,metal=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal
    return m

nx,ny=49,15
length,width,z0=3.16,.82,.6775
vs=[((i/(nx-1)-.5)*length,(j/(ny-1)-.5)*width,z0) for j in range(ny) for i in range(nx)]
fs=[(k,k+1,k+nx+1,k+nx) for j in range(ny-1) for i in range(nx-1) for k in [j*nx+i]]
mesh=bpy.data.meshes.new('Trough replacement inset')
mesh.from_pydata(vs,[],fs)
mesh.materials.append(mat('Cool turquoise glazed water',(.021,.153,.175),.23,.12))
mesh.update()
for f in mesh.polygons:f.use_smooth=True
o=bpy.data.objects.new('Paddock ripple inset',mesh);s.collection.objects.link(o)
o.shape_key_add(name='Still')
keys=[]
for i in range(4):
    k=o.shape_key_add(name='Ripple phase '+str(i+1))
    p=i*math.pi/2
    for idx,(x,y,z) in enumerate(vs):
        ix,iy=idx%nx,idx//nx
        # Fade smoothly into solid shores; exactly immobile boundary vertices.
        if ix in (0,nx-1) or iy in (0,ny-1):continue
        u,v=ix/(nx-1),iy/(ny-1)
        falloff=min(1,u/.08,(1-u)/.08)*math.sin(v*math.pi)**.75
        a=math.hypot(x+1.35,y-.22)
        wave=.0059*math.sin(13*a-p)+.0018*math.cos(8*x+6*y+p)
        k.data[idx].co.z=z+falloff*wave
    keys.append(k)
for f in range(0,73,2):
    t=(f%72)*math.tau/72
    for i,k in enumerate(keys):
        k.value=max(0,math.cos(t-i*math.pi/2))
        k.keyframe_insert(data_path='value',frame=f)
action=o.data.shape_keys.animation_data.action
action.name='Trough_Ripple_Loop_3s'
for fc in action.fcurves:
    for mark in fc.keyframe_points:mark.interpolation='LINEAR'
s.frame_set(0)
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',export_animations=True,
    export_animation_mode='ACTIONS',export_frame_step=2,export_morph_normal=True)

raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n])
assert len(d['meshes'])==len(d['animations'])==len(d['nodes'])==1
prim=d['meshes'][0]['primitives'][0]
assert len(prim['targets'])==4 and len(raw)<150000
assert not any(d.get(k) for k in ('images','skins','extensionsRequired'))
def values(idx):
    a=d['accessors'][idx]
    assert a['componentType']==5126
    stride={'SCALAR':1,'VEC3':3}[a['type']]
    def read(src,count,fmt):
        bv=d['bufferViews'][src['bufferView']]
        off=28+n+bv.get('byteOffset',0)+src.get('byteOffset',0)
        step=bv.get('byteStride',struct.calcsize(fmt))
        return [struct.unpack_from(fmt,raw,off+i*step) for i in range(count)]
    fmt='<'+'f'*stride
    result=read(a,a['count'],fmt) if 'bufferView' in a else [(0.0,)*stride]*a['count']
    if sp:=a.get('sparse'):
        idx='<'+{5121:'B',5123:'H',5125:'I'}[sp['indices']['componentType']]
        for (i,),value in zip(read(sp['indices'],sp['count'],idx),read(sp['values'],sp['count'],fmt)):
            result[i]=value
    return result
anim=d['animations'][0]
assert len(anim['channels'])==1 and anim['channels'][0]['target']['path']=='weights'
sp=anim['samplers'][anim['channels'][0]['sampler']]
time=values(sp['input']); weights=values(sp['output'])
assert time[0]==(0.0,) and time[-1]==(3.0,) and time==sorted(time)
assert len(weights)==len(time)*4 and weights[:4]==weights[-4:]
for t in prim['targets']:
    dv=values(t['POSITION'])
    assert max(abs(y) for x,y,z in dv)<.008
    assert all(x==z==0 for x,y,z in dv)

clear_scene()
bpy.ops.import_scene.gltf(filepath=str(trough))
old=s.objects['Inset water surface']
old.hide_render=True
old.hide_set(True)
bpy.ops.import_scene.gltf(filepath=str(dst))
fx=s.objects['Paddock ripple inset']
assert len(fx.data.shape_keys.key_blocks)==5

def evaluated(frame):
    s.frame_set(frame);bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    return [p.co.z for p in fx.evaluated_get(graph).data.vertices]
a,b=evaluated(0),evaluated(72)
assert len(a)==len(b)==nx*ny and max(abs(x-y) for x,y in zip(a,b))<1e-6
d1,d2=evaluated(16),evaluated(46)
assert max(abs(x-y) for x,y in zip(d1,d2))>.007
verts=fx.data.vertices
rim=[v.index for v in verts if abs(v.co.x)>1.57999 or abs(v.co.y)>.40999]
assert len(rim)==2*nx+2*ny-4 and all(abs(d1[i]-d2[i])<1e-6 for i in rim)
(out/'validation.json').write_text(json.dumps({'id':'WSC-PROP-079','bytes':len(raw),'duration_s':3,
    'triangles':d['accessors'][prim['indices']]['count']//3,'targets':4,
    'perimeter_vertices_fixed':len(rim),'endpoint_match':True,'native_runtime':False},indent=2)+'\n')

ground=mat('Paddock tamped limestone',(.198,.207,.143))
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-.008))
bpy.context.object.data.materials.append(ground)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def lamp(n,p,q,power,c,x,y):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=c;d.shape='RECTANGLE';d.size=x;d.size_y=y
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new('Paddock soft bounce')
s.world.color=(.19,.23,.26)
lamp('Warm outdoor key',(-2.9,-3.2,5.8),(0,0,.7),830,(1,.74,.50),2.5,3)
lamp('Long sky reflection',(.4,2.2,2.75),(0,0,.64),430,(.62,.82,1),2.0,.8)
lamp('Subtle cool rim',(-3,2.5,4.35),(0,0,.6),585,(.77,.90,1),3.1,2.1)
c=bpy.data.cameras.new('Trough ripple proof')
s.camera=bpy.data.objects.new(c.name,c);s.collection.objects.link(s.camera)
c.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=38;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=92
s.render.resolution_x,s.render.resolution_y=1300,830
for name,frame,pos,target,scale in (
    ('nov23-trough-ripple-overview',16,(2.58,-5.0,4.8),(0,0,.49),4.56),
    ('nov23-trough-ripple-detail',46,(-1.8,-3.35,4.1),(-.66,.02,.72),2.29)):
    s.frame_set(frame);s.camera.location=pos;aim(s.camera,target);c.ortho_scale=scale
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
