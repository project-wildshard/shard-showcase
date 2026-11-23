"""WSC-SCENE-007: build the C2 Pit around the checked-in split lift donors."""
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
from common import clear_scene, export, output_directory

root = Path(__file__).resolve().parents[3]
layout = json.loads((root/"project/layouts/wsc-scene-007-c2-pit.json").read_text())
out = output_directory()
s = bpy.context.scene
clear_scene()
x0,_,z0 = layout["origin_world_x_y_z"]
rng = random.Random(215)
groups = {}

def mat(name,c,metal=.10,rough=.70,glow=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
    n=m.node_tree.nodes.get("Principled BSDF")
    for k,v in (("Base Color",(*c,1)),("Metallic",metal),("Roughness",rough),
                ("Emission Color",(*c,1)),("Emission Strength",glow)):
        n.inputs[k].default_value=v
    return m

concrete=mat("Basalt concrete",(.174,.157,.128))
concrete2=mat("Patchwork aprons",(.211,.190,.151))
joint=mat("Expansion seams",(.093,.079,.064))
steel=mat("Blue charcoal steel",(.087,.118,.125),.66,.53)
rib=mat("Pressed steel ribs",(.142,.166,.163),.58,.56)
rust=mat("Faded pit orange",(.52,.172,.033),.38)
ink=mat("Pale stamped chevrons",(.69,.51,.224),.18)
dark=mat("Blind portal recess",(.036,.045,.047),.24)
lampmat=mat("Ceramic lamp face",(1,.78,.43),.16,.5,3)
cloth=mat("Heavy orange cloth",(.58,.115,.024),.0,.85)
cloth2=mat("Cloth shaded edge",(.32,.062,.025),.0,.85)

def polys(group,m,vertices,faces):
    vs,fs=groups.setdefault((group,m),([],[]))
    i=len(vs)
    vs.extend((x-x0,z0-z,y) for x,z,y in vertices)
    fs.extend(tuple(i+j for j in face) for face in faces)

def box(name,m,x,z,y,w,d,h,angle=0):
    a,b,c=w/2,d/2,h/2
    co,si=math.cos(angle),math.sin(angle)
    vs=[(x+co*i*a-si*j*b,z+si*i*a+co*j*b,y+k*c)
        for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    # The world x/z/y tuples reflect once to Blender, so reverse box winding.
    polys(name,m,vs,[(1,3,2,0),(6,7,5,4),(4,5,1,0),(3,7,6,2),(2,6,4,0),(5,7,3,1)])

def span(name,m,bottom,top,x1,x2,z1,z2):
    if x2>x1 and z2>z1:
        box(name,m,(x1+x2)/2,(z1+z2)/2,(bottom+top)/2,x2-x1,z2-z1,top-bottom)

# Floor is four solid volumes around a real 7.2 m shaft, plus a separate base
# slab. The art void has no collision or script; all poses are checked below.
f1,f2,g1,g2=layout["floor_x0_x1_z0_z1"]
lx,lz=layout["lift_x_z"]
r=layout["art_shaft_width"]/2
depth=layout["art_shaft_floor"]
for limits in ((f1,f2,g1,lz-r),(f1,lx-r,lz-r,lz+r),(lx+r,f2,lz-r,lz+r),(f1,f2,lz+r,g2)):
    span("01 Floor around shaft",concrete,depth,0,*limits)
span("01 Floor around shaft",dark,depth-.4,depth,lx-r,lx+r,lz-r,lz+r)
# Panel grid stays clear of the lift/shaft and has only millimetres of relief.
for a in range(17,94,7):
    for b in range(199,234,6):
        if abs(a-lx)<8 and abs(b-lz)<8: continue
        if rng.random()<.62: box("02 Ground panel wear",concrete2,a,b,.008,6.84,5.82,.014)
        for dz in (-2.8,2.8):
            box("02 Ground panel wear",joint,a,b+dz,.022,6.53,.044,.012)
for a in (33,77):
    for b in range(199,228,2):
        box("02 Floor stencils",ink,a,b,.026,.19,1.30,.012)

# The built Round 5 wedges start at the ledge edge, not at the layout pins.
span("03 North entry ledge",concrete,-.4,2.5,14,96,190,197)
for left,right in ((14,44.5),(51.5,72.5),(79.5,96)):
    box("03 North entry ledge",rust,(left+right)/2,196.84,2.52,right-left,.29,.04)
def wedge(rx,front,back,width):
    a,b=rx-width/2,rx+width/2
    polys("03 North entry ledge",concrete2,
          [(a,front,0),(b,front,0),(a,back,0),(b,back,0),(a,front,2.5),(b,front,2.5)],
          [(2,3,5,4),(1,3,2,0),(0,4,5,1),(4,0,2),(5,3,1)])
for rx in layout["ramp_x"]:
    front,back=layout["descent_ramp_z_high_low"]
    wedge(rx,front,back,layout["descent_ramp_width"])
    for i in range(8):
        z=front+.25+i
        box("03 North entry ledge",ink,rx,z,(back-z)/(back-front)*2.5+.025,5.7,.08,.05)

# West/east maintain exact named opening positions. Faces and closets are art
# shapes, not stand-ins for connected gameplay.
def wall(name,x1,x2,z1,z2):
    span(name,steel,0,5,x1,x2,z1,z2)
    span(name,rust,4.65,4.86,x1-.10,x2+.10,z1-.10,z2+.10)
    vertical=(z2-z1)>(x2-x1)
    l=(z2-z1) if vertical else (x2-x1)
    for i in range(max(1,int(l/2.05))):
        q=(i+.5)*l/max(1,int(l/2.05))
        x,z=((x1+x2)/2,z1+q) if vertical else (x1+q,(z1+z2)/2)
        box(name,rib,x,z,2.1,1.17 if vertical else .11,.11 if vertical else 1.17,4.05)

wall("04 South retaining shell",14,96,233.35,234)
wall("05 North shell",14,25,190,190.68)
wall("05 North shell",35,96,190,190.68)
for a,b in ((190,213.5),(218.5,234)):
    wall("06 West shell",14,14.68,a,b)
for a,b in ((190,210),(218,225.5),(230.5,234)):
    wall("07 East shell",95.32,96,a,b)

for id,x,z,px in (("D3",14,216,8.25),("D4",96,228,103.75)):
    g=f"08 {id} storage recess"
    span(g,concrete,-.4,0,min(x,px),max(x,px),z-6,z+6)
    box(g,dark,px,z,2.06,.48,11.55,4.1)
    for end in (-2.64,2.64):
        box(g,rust,x,z+end,1.83,1.25,.41,3.66)
        box(g,lampmat,x+(1 if id=="D3" else -1)*.66,z+end,2.98,.14,.16,.43)
    box(g,steel,x,z,3.92,1.28,5.86,.64)
wedge(30,190,184,10)
span("10 G2 exit stub",concrete,-.4,0,96,110,210,218)
box("10 G2 exit stub",dark,109.75,214,2.14,.49,7.88,4.28)
for z in (210.25,217.75):
    box("10 G2 exit stub",steel,103,z,2,14,.5,4)
    box("10 G2 exit stub",lampmat,98,z+(.28 if z<214 else -.28),2.9,.53,.10,.18)

# Plan silhouettes, deliberately no native cover collision.
for kind,x,z,rot in layout["cover"]:
    g="11 Set dressing | "+kind
    if kind=="pillar":
        box(g,steel,x,z,3,1.75,1.75,6)
        box(g,rust,x,z,.26,2.10,2.10,.52);box(g,rib,x,z,5.87,2.04,2.04,.26)
    elif kind=="half":
        box(g,concrete2,x,z,.53,4.2,.82,1.06,rot)
        box(g,steel,x,z,1.065,4.3,.91,.10,rot)
    else:
        for dx,dz,hh in ((-1.36,0,0),(0,0,0),(1.36,0,0),(-.64,.08,1.18),(.73,.1,1.18)):
            box(g,steel,x+dx,z+dz,hh+.59,1.32,1.36,1.18)
            for sign in (-1,1):
                box(g,rust,x+dx,z+dz+.63*sign,hh+.39,1.21,.10,.38)
                box(g,rib,x+dx,z+dz,hh+.10,1.39,1.39,.20)

# The banner hangs from the south wall, not from poles in the lift travel.
bx,bz=layout["banner_x_z"];bw,bh,bd=layout["banner_dims_width_height_depth"]
yb=layout["banner_bottom_y"]
for x in (bx-bw/2-.23,bx+bw/2+.23):
    box("12 Banner cantilever",steel,x,233.56,7.81,.38,.58,5.8)
    box("12 Banner cantilever",steel,x,232.8,yb+bh,.37,1.76,.48)
box("12 Banner cantilever",rust,bx,bz,yb+bh+.15,9.03,.3,.31)
for i in range(28):
    a,b=bx-bw/2+bw*i/28,bx-bw/2+bw*(i+1)/28
    def folds(x):return .11*math.cos((x-bx)*4.7)
    polys("13 Cloth banner",cloth2 if i in (0,27) else cloth,
          [(a,bz+folds(a),yb+abs(a-bx)*.14),(b,bz+folds(b),yb+abs(b-bx)*.14),
           (b,bz+folds(b)*.3,yb+bh),(a,bz+folds(a)*.3,yb+bh)],
          [(0,1,2,3)])
for yy in (9.8,10.62,11.44):
    points=[(bx+dx,bz-.14,yy+dy) for dx,dy in ((-2.7,1.16),(0,.17),(2.7,1.16),(2.7,.7),(0,-.33),(-2.7,.7))]
    polys("13 Cloth banner",ink,points,[(0,1,2,3,4,5)])

for x in (29,81):
    box("14 Work lamps",steel,x,233.04,5.77,.29,.30,8.2)
    box("14 Work lamps",steel,x,232.88,9.54,2.25,.7,.92)
    for dx in (-.71,0,.71):
        box("14 Work lamps",lampmat,x+dx,232.48,9.55,.47,.15,.55)

parts=[]
for (name,m),(v,f) in groups.items():
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(name,mesh);s.collection.objects.link(o);o.data.materials.append(m);parts.append(o)

donors={}
for part in ("frame","deck"):
    filename=root/"public/assets/wildshard-art"/f"wsc-kit-009-reveal-lift-{part}.glb"
    assert hashlib.sha256(filename.read_bytes()).hexdigest()==layout["donors_sha256"][part]
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(filename))
    new=set(s.objects)-before
    assert len(new)==1 and next(iter(new)).type=="MESH"
    obj=next(iter(new));donors[part]=obj;parts.append(obj)
    obj.location=(lx-x0,z0-lz,0)
bpy.context.view_layer.update()
def bounds(obj):
    v=[obj.matrix_world@p.co for p in obj.data.vertices]
    return tuple((min(p[i] for p in v),max(p[i] for p in v)) for i in range(3))
frame=donors["frame"];deck=donors["deck"]
fb=bounds(frame);db=bounds(deck)
assert -fb[0][0]<r and fb[0][1]<r
assert z0-lz-r<fb[1][0]<fb[1][1]<z0-lz+r
assert depth<db[2][0]<0 and abs(db[2][1])<.0001
assert abs(fb[2][1])<.0001 and depth<fb[2][0]<0
wall_gap=233.35-(z0-fb[1][0])
crate_gap=(z0-fb[1][1])-(222+.68+.01)
assert wall_gap>.8 and crate_gap>2.7
deck.location.z=layout["lift_rise"]
bpy.context.view_layer.update()
raised=bounds(deck)
assert abs(raised[2][1]-4)<.0001 and raised[2][1]+3.99<yb

f=out/"wsc-scene-007-c2-pit.glb"
export(parts,f)
raw=f.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert not any(k in doc for k in ("animations","skins","images"))
assert len(raw)<1_700_000
tri=sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(f))
named={o.name:o for o in s.objects if o.type=="MESH"}
redeck=next(o for n,o in named.items() if n.startswith("C2_Lift_Moving_Deck"))
assert abs(bounds(redeck)[2][1]-4)<.0001
(out/"validation.json").write_text(json.dumps({"bytes":len(raw),"triangles":tri,"meshes":len(named),
    "low_guide_y":round(db[2][0],3),"shaft_base_y":depth,"lift_south_wall_clearance_m":round(wall_gap,3),
    "lift_crate_gap_m":round(crate_gap,3),"lift_top_exported_y":4,"images":0,"animations":0},indent=2)+"\n")

def aim(obj,p):
    obj.rotation_euler=(Vector(p)-obj.location).to_track_quat("-Z","Y").to_euler()
def light(name,kind,p,q,power,color,size):
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
    if kind=="AREA":d.shape="DISK";d.size=size
    if kind=="SUN":d.angle=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=p;aim(o,q)

s.world=bpy.data.worlds.new("C2 slate blue")
s.world.use_nodes=True
bg=s.world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.20,.38,.68,1);bg.inputs[1].default_value=.44
light("Low sun","SUN",(-35,20,40),(0,-10,0),2.2,(1,.76,.53),.11)
light("Soft skylight","AREA",(0,9,27),(0,-10,0),16600,(.53,.68,1),28)
light("Banner silk wash","AREA",(0,-8,6.8),(0,-20,10),3400,(1,.73,.48),6.5)
light("Shaft inspection light","AREA",(0,-17,3.9),(0,-17,-4.3),950,(.54,.67,1),2)
gg=mat("Studio ground not exported",(.043,.059,.067))
bpy.ops.mesh.primitive_plane_add(size=450,location=(0,0,-6.1))
bpy.context.object.data.materials.append(gg)
cam=bpy.data.cameras.new("C2 review camera");s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
s.render.engine="CYCLES";s.cycles.samples=38;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_percentage=100;s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=92
for label,pos,target,fl,res in (
    ("nov23-gauntlet-pit-overlook",(51,54,63),(2,-3,1.5),37,(1450,1000)),
    ("nov23-gauntlet-pit-lift",(-6,0,3),(0,-18,6.6),27,(1080,1230)),
):
    s.camera.location=pos;aim(s.camera,target);cam.lens=fl
    s.render.resolution_x,s.render.resolution_y=res
    s.render.filepath=str(out/(label+".jpg"));bpy.ops.render.render(write_still=True)
