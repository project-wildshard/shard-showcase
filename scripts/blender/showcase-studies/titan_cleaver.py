"""Stylized nonfunctional Titan Cleaver inventory mesh from the WSC-GEAR-006 artwork."""
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory
out=output_directory()
s=bpy.context.scene
clear_scene()
by_mat={}

def mat(name,color,metal,rough,strength=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    n=m.node_tree.nodes["Principled BSDF"]
    for k,v in (("Base Color",(*color,1)),("Metallic",metal),("Roughness",rough),
                ("Emission Color",(*color,1)),("Emission Strength",strength)):
        n.inputs[k].default_value=v
    return m

alloy=mat("Blackened blue alloy",(.075,.105,.123),.71,.48)
steel=mat("Cool faceted panels",(.167,.207,.223),.62,.47)
bronze=mat("Gold oxide shadow",(.45,.217,.042),.67,.46)
gold=mat("Titan gold",(.78,.395,.072),.59,.36)
rubber=mat("Dark graphite wrap",(.051,.042,.035),.06,.73)
cyan=mat("Clear turquoise insignia",(.019,.67,.80),.26,.38,1.25)

def add(m,v,f):
    vs,fs=by_mat.setdefault(m,([],[]));base=len(vs);vs.extend(v)
    fs.extend(tuple(base+j for j in q) for q in f)

def shape(points,near,far,m):
    # Abstract closed silhouette, not a manufactured object drawing.
    n=len(points)
    area=sum(x*zz-xx*z for (x,z),(xx,zz) in zip(points,points[1:]+points[:1]))
    if area<0: points=points[::-1]
    add(m,[(x,y,z) for y in (near,far) for x,z in points],
        [tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
        +[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)])

housing=[(-.233,.23),(-.233,.52),(-.201,.57),(-.201,1.40),(-.246,1.46),(-.246,1.66),
         (.127,1.603),(.216,1.54),(.254,1.46),(.254,1.29),(.20,1.245),(.20,1.04),
         (.236,1.003),(.236,.52),(.197,.452),(.212,.245),(.135,.188),(-.126,.188)]
outer=[(-.247,.28),(-.247,.527),(-.211,.576),(-.211,1.408),(-.254,1.459),(-.254,1.699),
       (-.083,1.649),(-.136,1.59),(-.172,1.574),(-.167,1.456),(-.156,1.419),
       (-.156,.56),(-.186,.50),(-.186,.303)]
mid=[(-.139,.36),(-.132,1.548),(-.027,1.594),(.125,1.551),(.205,1.474),(.207,1.329),
     (.149,1.284),(.151,1.087),(.181,1.052),(.176,.413),(.095,.351)]
trace=[(-.032,.50),(-.027,.81),(-.087,.89),(-.087,1.424),(-.069,1.424),(-.069,.897),
       (-.006,.815),(-.010,.50)]
cap=[(-.175,.284),(-.146,.383),(-.086,.397),(-.036,.35),(.06,.35),(.123,.404),
     (.211,.332),(.214,.252),(.151,.184),(-.127,.184)]
insert=[(-.026,.216),(-.054,.246),(-.054,.329),(-.031,.36),(.031,.36),(.054,.329),(.054,.246),(.027,.216)]
shape(housing,-.057,.057,alloy)
shape(outer,-.063,.063,bronze)
shape(cap,-.092,.092,alloy)
for side in (-1,1):
    def plate(points,a,b,m):
        shape(points,*sorted((a*side,b*side)),m)
    def mark(points,a,m):
        area=sum(x*zz-xx*z for (x,z),(xx,zz) in zip(points,points[1:]+points[:1]))
        if (area<0)==(side<0): points=points[::-1]
        add(m,[(x,a*side,z) for x,z in points],[tuple(range(len(points)))])
    plate(mid,.059,.071,steel)
    plate([(-.232,.315),(-.232,.521),(-.197,.571),(-.197,1.41),(-.238,1.472),(-.239,1.681),
           (-.161,1.652),(-.173,1.53),(-.164,1.427),(-.163,.56),(-.194,.507),(-.194,.331)],.063,.070,gold)
    mark(trace,.076,cyan)
    plate(insert,.093,.103,bronze)
    mark([(-.018,.231),(-.030,.26),(-.030,.312),(-.015,.343),(.014,.343),(.029,.312),(.029,.26),(.018,.231)],.107,cyan)
    for sign in (-1,1):
        points=[(sign*x,z) for x,z in ((.076,.319),(.116,.352),(.198,.301),(.221,.247),(.189,.215),(.151,.25),(.11,.253))]
        plate(points,.089,.098,bronze)
        plate([(sign*x,z) for x,z in ((.088,.310),(.117,.333),(.189,.287),(.202,.245),(.186,.235),(.15,.27))],.099,.109,gold)
    # Visually recessed vents are shallow dark marks, not holes.
    for i in range(3):
        k=.56+i*.095
        mark([(.092,k),(.173,k+.068),(.173,k+.092),(.092,k+.026)],.075,alloy)
    for x,z in ((-.117,1.47),(.138,1.428),(.167,1.328),(.095,.454),(-.104,.460),(-.143,.278),(.154,.281)):
        pts=[(x+.011*math.cos(t*math.tau/6),z+.011*math.sin(t*math.tau/6)) for t in range(6)]
        mark(pts,.079 if z>.42 else .104,alloy)
    for x,z in ((-.213,1.08),(-.226,.485),(-.220,1.58)):
        mark([(x-.009,z+.012),(x+.023,z-.008),(x+.013,z-.017),(x-.012,z+.005)],.073,bronze)

def lathe(rings,n,m,phase=0):
    v=[(r*math.cos(a*math.tau/n+phase),r*.89*math.sin(a*math.tau/n+phase),z)
       for z,r in rings for a in range(n)]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(len(v)-n,len(v)))]
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    add(m,v,faces)

lathe([(-.242,.051),(-.195,.060),(.140,.055),(.178,.060),(.20,.059)],10,rubber)
for i in range(6):
    z=(-.185+i*.057)
    # Tiny diagonal shading rings on the fantasy inventory grip.
    n=10;v=[]
    for dz,rr in ((-.006,.059),(.004,.061)):
        for j in range(n):
            a=math.tau*j/n
            v.append((rr*math.cos(a),rr*.91*math.sin(a),z+dz+.010*math.sin(a)))
    add(alloy,v,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
lathe([(-.277,.052),(-.256,.085),(-.208,.079),(-.192,.055)],8,steel,.39)
lathe([(-.265,.072),(-.251,.085),(-.224,.082),(-.214,.075)],8,bronze,.39)
lathe([(.151,.055),(.164,.072),(.190,.071),(.201,.06)],8,steel,.39)
for side in (-1,1):
    a,b=sorted((.073*side,.077*side))
    shape([(-.018,-.251),(-.026,-.239),(-.014,-.218),(.014,-.218),(.026,-.239),(.018,-.251)],a,b,cyan)

parts=[]
for m,(v,f) in by_mat.items():
    mesh=bpy.data.meshes.new(m.name);mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(m.name,mesh);s.collection.objects.link(o);o.data.materials.append(m);parts.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
obj=bpy.context.object;obj.name="WSC-GEAR-006 Titan Cleaver | Grip Pivot"
f=out/"wsc-gear-006-titan-cleaver.glb"
export([obj],f)
blob=f.read_bytes();assert struct.unpack_from("<4sII",blob)==(b"glTF",2,len(blob))
doc=json.loads(blob[20:20+struct.unpack_from("<I",blob,12)[0]])
assert not any(k in doc for k in ("animations","images","skins"))
assert len(blob)<=65536,len(blob)
count=sum(doc["accessors"][p["indices"]]["count"]//3 for p in doc["meshes"][0]["primitives"])
clear_scene();bpy.ops.import_scene.gltf(filepath=str(f))
re=next(obj for obj in s.objects if obj.type=="MESH");assert re.location.length<.0001
(out/"validation.json").write_text(json.dumps({"bytes":len(blob),"triangles":count,
  "primitives":len(doc["meshes"][0]["primitives"]),"grip_pivot":True,"animations":0,"images":0},indent=2)+"\n")

# Two reimported angles in a floating gallery. Only the asset is in the GLB.
re.location=(-.48,0,.39);re.rotation_mode="XYZ"
re.rotation_euler.y=-.19;re.rotation_euler.z=-.19
other=re.copy();s.collection.objects.link(other)
other.location=(.64,.075,.38);other.rotation_mode="XYZ"
other.rotation_euler.y=.27;other.rotation_euler.z=math.pi+.84
ground=mat("Gallery slate",(.052,.090,.107),.18,.66)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.24))
bpy.context.object.data.materials.append(ground)

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()

def area(name,p,target,power,tint,size):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.color=tint;d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=p;aim(o,target)

s.world=bpy.data.worlds.new("Ink gallery");s.world.color=(.14,.18,.29)
area("Gold key",(-2.2,-2.4,3.2),(0,0,1),400,(1,.73,.49),3.2)
area("Blue edge",(1.8,1.2,3.1),(0,0,1),410,(.32,.69,1),2.8)
area("Cool polar fill",(1.3,-2.2,1.8),(0,0,1),116,(.62,.83,1),2.4)
cam=bpy.data.cameras.new("Inventory angles");s.camera=bpy.data.objects.new(cam.name,cam)
s.collection.objects.link(s.camera);s.camera.location=(.04,-6.2,1.38);aim(s.camera,(0,0,1.08))
cam.type="ORTHO";cam.ortho_scale=3.20
s.render.engine="CYCLES";s.cycles.samples=60;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1340;s.render.resolution_y=1060;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=92
s.render.filepath=str(out/"nov23-titan-cleaver-study.jpg");bpy.ops.render.render(write_still=True)
