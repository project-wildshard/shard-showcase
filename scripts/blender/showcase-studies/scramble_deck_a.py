"""W8b alternate art fit onto the exact archived six-metre Deck A."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import export

args = argparse.ArgumentParser()
args.add_argument("base",type=Path)
args.add_argument("out",type=Path)
a = args.parse_args(sys.argv[sys.argv.index("--")+1:])
out = a.out.resolve()
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.base.resolve()/"climb-rock-editable.blend"))
scene = bpy.context.scene
origin = Vector((-169.312 - (6-.0275)/math.tan(math.radians(70)), -27.73, .0275))
height=6-origin.z
angle=math.radians(70)
run=height/math.tan(angle)
width=2.65
outward=Vector((-math.sin(angle),0,math.cos(angle)))
up=Vector((math.cos(angle),0,math.sin(angle)))
cross=Vector((0,1,0))
rng=random.Random(168)


def mat(n,c,rough=.68,metal=.04):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    d=m.node_tree.nodes["Principled BSDF"]
    d.inputs["Base Color"].default_value=(*c,1)
    d.inputs["Roughness"].default_value=rough
    d.inputs["Metallic"].default_value=metal
    return m


mats = [
    mat("Dark slate slab",(.095,.119,.123),.73),
    mat("Honed edge slate",(.16,.19,.19),.65),
    mat("Oxidised seam graphite",(.046,.063,.068),.82),
    mat("Ochre holds",(.59,.247,.049)),
    mat("Hewn pale holds",(.46,.48,.425)),
    mat("Dull blue pumice holds",(.077,.235,.265)),
    mat("Visible steel fixings",(.186,.211,.203),.39,.65),
]
vs,fs,materials=[],[],[]
def add(points,faces,m):
    k=len(vs)
    vs.extend(points)
    fs.extend(tuple(k+i for i in f) for f in faces)
    materials.extend([m]*len(faces))


# Cast slab in a true 70 degree plane. Slate field is stitched from
# horizontal bands, with a tapered backside short of the existing deck.
levels=(0,.53,1.11,1.82,2.57,3.37,4.15,4.94,5.40,height)
for i in range(len(levels)-1):
    z,z1=levels[i:i+2]
    x,x1 = z/math.tan(angle),z1/math.tan(angle)
    add([(x,-width/2,z),(x,width/2,z),(x1,width/2,z1),(x1,-width/2,z1)],
        [(0,3,2,1)], 1 if i in (1,8) else 0)
for s in (-1,1):
    y=s*width/2
    seq=[(0,y,0),(run,y,height),(run,y,height-.32),(.36,y,0)]
    add(seq,[(0,1,2,3) if s<0 else (3,2,1,0)],2)
add([(.36,-width/2,0),(.36,width/2,0),(run,width/2,height-.32),
     (run,-width/2,height-.32),(run,-width/2,height),(run,width/2,height)],
    [(0,1,2,3),(3,2,5,4)],2)


def face(h,y,offset):
    return Vector((h/math.tan(angle),y,h)) + outward*offset


def tapered_hold(h,y,s,depth,roll,m):
    n=7
    points=[]
    for ring in range(2):
        for i in range(n):
            a=math.tau*i/n + roll
            factor=(.84+.16*rng.random()) * (1 if ring==0 else .62)
            points.append(tuple(face(h,y,-.002 if ring==0 else depth)
                + cross*(math.cos(a)*s*factor)
                + up*(math.sin(a)*s*.72*factor)))
    faces=[tuple(reversed(range(n,n*2)))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,i+n,j+n,j))
    add(points,faces,m)


# Staggered grip language: pale steps, amber path, cool alternate path.
holds=[]
for i in range(12):
    z=.40+i*.466
    for j,y in enumerate((-.74+.13*math.sin(i),.47+.23*math.cos(i*.89))):
        h=z+j*.16
        s=.145+.049*rng.random()
        depth=.051+.061*rng.random()
        tapered_hold(h,y,s,depth,rng.uniform(-.8,.8),3 if j==0 else (4 if i%2 else 5))
        tapered_hold(h,y,.023,depth+.008,0,6)
        holds.append([h,y,depth])
for y in (-1.05,1.05):
    for h in (.68,2.80,5.25):
        tapered_hold(h,y,.044,.015,0,6)

name="W8b Deck A scramble slab"
mesh=bpy.data.meshes.new(name)
mesh.from_pydata(vs,[],fs)
mesh.update()
for m in mats: mesh.materials.append(m)
for p,m in zip(mesh.polygons,materials): p.material_index=m
o=bpy.data.objects.new(name,mesh)
scene.collection.objects.link(o)
file=out/"w8b-deck-a-scramble.glb"
export([o],file)
raw=file.read_bytes()
assert raw[:4]==b"glTF" and struct.unpack_from("<I",raw,8)[0]==len(raw)
d=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
tri=sum(d["accessors"][p["indices"]]["count"]//3 for m in d["meshes"] for p in m["primitives"])
assert len(d["meshes"])==1 and len(raw)<85000 and tri<1100
assert not any(d.get(k) for k in ("images","animations","skins","cameras"))
bpy.data.objects.remove(o,do_unlink=True)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(file))
obj,=set(scene.objects)-before
obj.matrix_world=Matrix.Translation(origin)@obj.matrix_world
bpy.context.view_layer.update()
points=[obj.matrix_world@v.co for v in obj.data.vertices]
assert abs(max(p.x for p in points)+169.312)<.0001
assert abs(max(p.z for p in points)-6)<.001


def bvh(objects):
    vs,fs=[],[]
    for o in objects:
        k=len(vs)
        vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(k+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)


deck=[o for o in before if o.type=="MESH" and "deck A and ladder, walking plane " in o.name]
assert len(deck)==1
landing=bvh(deck)
surface=bvh([obj])
assert not surface.overlap(landing),"New slab intersects existing deck"
ends=[]
for y in (-1.08,0,1.08):
    h=landing.ray_cast(Vector((-169.276,origin.y+y,6.3)),Vector((0,0,-1)),.5)[0]
    v=surface.ray_cast(Vector((-169.315,origin.y+y,6.4)),Vector((0,0,-1)),.7)[0]
    assert h is not None and abs(h.z-6)<.001,(y,h)
    assert v is not None and 0<h.z-v.z<.012,(y,v)
    ends.append([y,v.z,h.z])
ground=[]
stage=bvh([o for o in before if o.type=="MESH" and "CLIMB | source yard footprint" in o.name])
for y in (-1.08,0,1.08):
    p=stage.ray_cast(origin+Vector((.18,y,.5)),Vector((0,0,-1)),1)[0]
    assert p is not None and abs(p.z-origin.z)<.003,p
    ground.append(p.z)

# Neutral outdoor lighting, only active in this review scene.
for q in before:
    if q.type=="LIGHT": q.hide_render=True
world=bpy.data.worlds.new("Climb yard clear morning")
world.use_nodes=True
bg=world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.46,.63,.84,1)
bg.inputs[1].default_value=.51
scene.world=world
d=bpy.data.lights.new("Late morning","SUN")
d.energy=2.45;d.angle=math.radians(7);d.color=(1,.83,.60)
sun=bpy.data.objects.new("Late morning",d)
scene.collection.objects.link(sun)
sun.rotation_euler=Vector((.63,.30,-.64)).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
cam.data.lens=37
cam.data.clip_end=260
scene.render.engine="CYCLES"
scene.cycles.samples=40
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.068
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x,scene.render.resolution_y=1390,940
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=91
for tag,ep,at in [
    ("approach",(-179.0,-33.7,1.70),(-169.0,-28.0,3.20)),
    ("landing",(-175.0,-23.1,7.40),(-168.5,-28.65,4.60)),
]:
    cam.location=ep
    cam.rotation_euler=(Vector(at)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(out/f"nov24-w8b-scramble-{tag}.jpg")
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)
(out/"scramble-fit.json").write_text(json.dumps({
    "slope_deg":70,"nominal_deck_m":6,"width_m":width,
    "origin_blender_m":list(origin),"run_m":run,"nominal_seam_m":.012,
    "pad_checks_blender_m":ends,"ground_samples_m":ground,
    "holds":len(holds),"bytes":len(raw),"triangles":tri,
    "sha256":hashlib.sha256(raw).hexdigest(),"native":False},indent=2)+"\n")
