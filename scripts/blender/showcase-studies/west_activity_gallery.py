"""Compose a compact West courtyard study without duplicating any donor in Git."""
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

root=Path(__file__).resolve().parents[3]
cfg=json.loads((root/"project/layouts/wsc-kit-001-west-gallery.json").read_text())
out=output_directory()
scene=bpy.context.scene
clear_scene()
rng=random.Random(1147)
parts=[]
donors={}
buckets={}

def mat(name,c,metal,rough):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
    n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Metallic"].default_value=metal;n.inputs["Roughness"].default_value=rough
    return m

trim=mat("Court graphite",(.074,.093,.094),.54,.46)
earth=mat("Tan limestone sides",(.170,.105,.063),.1,.85)
amber=mat("Ochre enamel accents",(.63,.245,.062),.38,.49)
paint=mat("Inlaid cream court stripe",(.72,.62,.40),.03,.78)
tiles=[mat(f"Limestone mottling {i+1}",(v*1.23,v,v*.71),.04,.84)
       for i,v in enumerate((.149,.175,.197,.209,.220,.239,.252,.275))]
pebbles=mat("Court weathering",(.31,.249,.167),.04,.81)

def box(g,m,p,d):
    x,y,z=p;a,b,c=(v/2 for v in d)
    points,faces=buckets.setdefault((g,m),([],[]));n=len(points)
    points.extend((x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1))
    faces.extend(tuple(n+i for i in f) for f in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)))

def meshes(g,m,points,faces):
    mesh=bpy.data.meshes.new(g);mesh.from_pydata(points,[],faces);mesh.update()
    obj=bpy.data.objects.new(g,mesh);scene.collection.objects.link(obj);mesh.materials.append(m);parts.append(obj)

for tag,(filename,digest) in cfg["donors"].items():
    f=root/"public/assets/wildshard-art"/filename
    assert hashlib.sha256(f.read_bytes()).hexdigest()==digest
    prior=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(f))
    bpy.context.view_layer.update()
    added=sorted(set(scene.objects)-prior,key=lambda o:o.name)
    ready=[(o.name,o.data,o.matrix_world.copy()) for o in added if o.type=="MESH"]
    assert ready,tag
    donors[tag]=ready
    for o in added:bpy.data.objects.remove(o,do_unlink=True)

placed=[]
for label,x,y,z,deg in cfg["placement"]:
    seq=[]
    world=Matrix.Translation((x,y,z))@Matrix.Rotation(math.radians(deg),4,"Z")
    for n,mesh,source in donors[label]:
        obj=bpy.data.objects.new(label+" | "+n,mesh);scene.collection.objects.link(obj)
        obj.matrix_world=world@source;parts.append(obj);seq.append(obj)
    placed.append((label,seq))
bpy.context.view_layer.update()

def bounds(seq):
    ps=[o.matrix_world@Vector(p) for o in seq for p in o.bound_box]
    return [[round(fn(v[i] for v in ps),4) for i in range(3)] for fn in (min,max)]

bs={k:[bounds(g) for l,g in placed if l==k] for k in donors}
gaps=[round(bs["wall"][i+1][0][0]-bs["wall"][i][1][0],4) for i in (0,1)]
assert gaps==[.02,.02],gaps
assert all(abs(b[0][2])<.001 for b in bs["wall"])
assert all(0<=b[0][2]<.01 for b in bs["curb"])
# The timer donor is grounded in an actual sill; pennants have paired brackets.
assert abs(bs["timer"][0][0][2]-2.30)<.001
box("Timer | plinth",trim,(0,2.43,2.22),(2.28,.79,.16))
for x in (-1.11,1.11):box("Timer | posts",trim,(x,2.628,1.34),(.141,.15,2.68))
for x in (-5.92,1.0,7.92):
    box("Pennant posts",trim,(x,.04,2.27),(.126,.138,4.54))
    box("Pennant posts",amber,(x,.04,.19),(.24,.245,.35))
# Tiny dark seam strips bridge the scenery fascia, not seams in any collision mesh.
for x in (-2.65,2.65):
    box("Decorative wall mullions",trim,(x,2.633,1.23),(.052,.059,2.46))

box("Diorama base",earth,(0,-.55,-.32),(16.66,8.10,.63))
box("Diorama base",trim,(0,-.55,-.65),(16.82,8.24,.09))
for row in range(16):
    y=-4.48+row*.486
    for col in range(28):
        x=-8.10+col*.598+(row%2)*.299
        if x>8.10: continue
        tile=rng.choices(tiles,(1,2,4,7,5,4,2,1))[0]
        box("Stone pavers",tile,(x,y,-.025+rng.uniform(-.002,.002)),(.588,.472,.05))
for x in (-6.15,6.15):
    for y in (-3.83,-3.18,-2.53,-1.88,-1.23,-.58,.07,.72,1.37,2.02):
        box("Art paving inset",paint,(x,y,.001),(.085,.43,.006))
for _ in range(101):
    x=rng.uniform(-7.1,7.1);y=rng.uniform(-4.1,2.31)
    box("Courtyard speckling",pebbles,(x,y,.002),(rng.uniform(.015,.05),rng.uniform(.014,.035),.006))
for (g,m),(p,f) in buckets.items():meshes(g,m,p,f)

f=out/"wsc-kit-001-west-gallery.glb"
export(parts,f)
raw=f.read_bytes();assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert not any(k in doc for k in ("animations","skins","images"))
triangles=sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
clear_scene();bpy.ops.import_scene.gltf(filepath=str(f))
assert len([o for o in scene.objects if o.type=="MESH"])==len(parts)
(out/"validation.json").write_text(json.dumps({"asset":cfg["asset"],"authored_wall_seam_m":gaps,
  "unique_donors":len(donors),"donor_instances":len(placed),"world_bounds":bs,"glb_bytes":len(raw),
  "unique_mesh_triangles":triangles,"gameplay":False},indent=2)+"\n")

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def light(name,kind,p,q,power,c,size):
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=c
    if kind=="SUN":d.angle=size
    else:d.shape="DISK";d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=p;aim(o,q)
scene.world=bpy.data.worlds.new("Gallery sky")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.13,.29,.52,1);bg.inputs[1].default_value=.36
light("Afternoon sun","SUN",(-6,-5,7),(0,0,0),2.2,(1,.77,.53),.09)
light("Sky strip","AREA",(4,-2,7),(0,1,1),750,(.50,.72,1),7)
light("Wood bounce","AREA",(-3,-3,3),(0,2,1.3),220,(1,.60,.33),4)
g=mat("Studio background not exported",(.039,.071,.102),.04,.77)
bpy.ops.mesh.primitive_plane_add(size=160,location=(0,0,-.7003))
bpy.context.object.data.materials.append(g)
cam=bpy.data.cameras.new("West gallery")
scene.camera=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(scene.camera)
scene.render.engine="CYCLES";scene.cycles.samples=55;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=92
for label,pos,target,lens,res in (
  ("nov23-west-gallery-eye",(-5.5,-14.2,2.65),(.45,1.1,1.65),28,(1450,910)),
  ("nov23-west-gallery-overhead",(11,-13,12),(.25,0,1.2),33,(1400,980)),
):
    scene.camera.location=pos;aim(scene.camera,target);cam.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/(label+".jpg"));bpy.ops.render.render(write_still=True)
