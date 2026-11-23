"""Animated ember art for WSC-PROP-057. A standalone looping display GLB."""
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
root=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
s=bpy.context.scene
clear_scene()
s.render.fps=24
s.frame_start=0
s.frame_end=72
rng=random.Random(172)
origin_name="Foundry ember loop | socket"
origin=bpy.data.objects.new(origin_name,None);s.collection.objects.link(origin)

def mat(n,c,rough=.58,energy=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    node=m.node_tree.nodes["Principled BSDF"]
    for k,v in (("Base Color",(*c,1)),("Roughness",rough),("Emission Color",(*c,1)),("Emission Strength",energy)):
        node.inputs[k].default_value=v
    return m

hot=mat("Gold ember core",(1,.45,.045),.46,2.7)
warm=mat("Copper ember core",(1,.16,.022),.52,2.2)
shapes=[]
for m in (hot,warm):
    mesh=bpy.data.meshes.new(m.name)
    mesh.from_pydata([(0,0,-1.4),(0,0,1.4),(-.60,0,0),(0,-.53,0),(.60,0,0),(0,.53,0)],[],
        [(0,3,2),(0,4,3),(0,5,4),(0,2,5),(1,2,3),(1,3,4),(1,4,5),(1,5,2)])
    mesh.materials.append(m);mesh.update();shapes.append(mesh)

def ease(a,b,x):
    y=max(0,min(1,(x-a)/(b-a)))
    return y*y*(3-2*y)

for i in range(18):
    o=bpy.data.objects.new(f"Ember {i+1:02d}",shapes[i%2]);s.collection.objects.link(o);o.parent=origin
    a,b,c=(rng.uniform(-1,1) for _ in range(3))
    radius=rng.uniform(.014,.028)
    o.rotation_euler.y=a*.53
    o.rotation_euler.x=b*.49
    for f in range(0,73,2):
        u=((f+4*i)%72)/72
        visible=ease(.015,.12,u)*(1-ease(.77,.94,u))
        o.location=(a*(.26+.74*u)+math.sin(5.6*u+i)*.09*u,
                    b*.114-.43*u+.18*math.sin(u*math.pi),
                    (1.12+.24*c)*u+.11*u*u)
        z=radius*max(.0002,visible)*(1-.48*u)
        o.scale=(z,z,z*(1.15+.45*abs(a)))
        o.keyframe_insert(data_path="location",frame=f)
        o.keyframe_insert(data_path="scale",frame=f)
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation="LINEAR"

s.frame_set(0)
f=out/"wsc-prop-057-foundry-ember-loop.glb"
bpy.ops.export_scene.gltf(filepath=str(f),export_format="GLB",
    export_animations=True,export_animation_mode="SCENE",export_frame_step=2)
raw=f.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
n=struct.unpack_from("<I",raw,12)[0]
d=json.loads(raw[20:20+n])
# Blender's scene exporter emits one clip per simultaneously sampled
# object; combine compatible channels without touching binary bufferViews.
single={"name":"Foundry_Embers_Loop_3s","channels":[],"samplers":[]}
for part in d["animations"]:
    offset=len(single["samplers"])
    single["samplers"].extend(part["samplers"])
    single["channels"].extend({**c,"sampler":c["sampler"]+offset} for c in part["channels"])
d["animations"]=[single]
body=json.dumps(d,separators=(",",":"),ensure_ascii=True).encode()
body+=b" "*(-len(body)%4)
binary=raw[20+n:]
raw=struct.pack("<4sIII4s",b"glTF",2,20+len(body)+len(binary),len(body),b"JSON")+body+binary
f.write_bytes(raw)
n=len(body)
assert len(raw)<100_000 and len(d["animations"])==1 and len(d["meshes"])==2
assert not any(k in d for k in ("images","skins","extensionsRequired"))
def values(uniform):
    a=d["accessors"][uniform];v=d["bufferViews"][a["bufferView"]]
    assert a["componentType"]==5126
    stride={"SCALAR":1,"VEC3":3}[a["type"]]
    off=28+n+v.get("byteOffset",0)+a.get("byteOffset",0)
    return [struct.unpack_from("<"+"f"*stride,raw,off+i*v.get("byteStride",stride*4)) for i in range(a["count"])]
anim=d["animations"][0]
assert len(anim["channels"])==36
for c in anim["channels"]:
    sp=anim["samplers"][c["sampler"]]
    ts=values(sp["input"]);vs=values(sp["output"])
    assert ts[0]==(0.0,) and ts[-1]==(3.0,)
    assert vs[0]==vs[-1]
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(f))
fx=bpy.data.objects[origin_name]
assert len(fx.children)==18
fx.location=(0,-1.31,.54)
furnace=root/"wsc-prop-057-foundry-furnace.glb"
assert hashlib.sha256(furnace.read_bytes()).hexdigest()=="0c47183c8f38699661f527d01b8e85a4891e03ec898cabd028b07568e32b8530"
bpy.ops.import_scene.gltf(filepath=str(furnace))
ground=mat("Foundry floor studio",(.096,.094,.099),.84)
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-.003))
bpy.context.object.data.materials.append(ground)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(n,p,q,power,c,sz):
    l=bpy.data.lights.new(n,"AREA");l.energy=power;l.color=c;l.size=sz
    o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=p;aim(o,q)

s.world=bpy.data.worlds.new("Dark foundry studio");s.world.color=(.071,.086,.114)
area("Warm mouth bounce",(0,-1.36,.66),(0,-2.7,.08),82,(1,.33,.065),.66)
area("Cool softbox",(-2,-4,3.4),(0,0,1),320,(.52,.74,1),3.1)
area("Hot side bounce",(2,-2.8,2.3),(0,0,1.2),190,(1,.62,.36),2.9)
cam=bpy.data.cameras.new("Furnace reimport proof");s.camera=bpy.data.objects.new(cam.name,cam)
s.collection.objects.link(s.camera);s.camera.location=(2.5,-6.65,2.34);aim(s.camera,(0,-.28,1.30))
cam.type="ORTHO";cam.ortho_scale=4.1
s.render.engine="CYCLES";s.cycles.samples=44;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1150;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=92
for frame in (16,48):
    s.frame_set(frame)
    s.render.filepath=str(out/f"nov23-foundry-embers-{frame:02d}.jpg")
    bpy.ops.render.render(write_still=True)
(out/"validation.json").write_text(json.dumps({"bytes":len(raw),"duration_s":3,"nodes":18,"meshes":2,
    "channels":36,"animations":1,"loop_endpoints_exact":True,"runtime":False},indent=2)+"\n")
