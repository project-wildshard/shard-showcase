"""Rebuild the WSC-SCENE-004 West plaza / East seam threshold study."""
from pathlib import Path
import hashlib
import json
import math
import random
import sys

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
clear_scene()
s=bpy.context.scene
root=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
pin_path=Path(__file__).resolve().parents[3]/"project/layouts/w0a-east-gate-boundary-donors.json"
pins=json.loads(pin_path.read_text())
models={}
def donor(key):
    if key in models:return models[key]
    a=pins[key];p=root/a["file"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"], key
    before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    items=sorted(set(s.objects)-before,key=lambda o:o.name)
    models[key]=[(o.data,o.matrix_world.copy()) for o in items if o.type=="MESH"]
    for o in items:bpy.data.objects.remove(o,do_unlink=True)
    assert models[key]
    return models[key]

def place(key,name,transform):
    batch=[]
    for data,matrix in donor(key):
        o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.matrix_world=transform@matrix;batch.append(o)
    return batch

def matrix(p,yaw=0,scale=1):
    return Matrix.Translation(p)@Matrix.Rotation(yaw,4,"Z")@Matrix.Scale(scale,4)
def remodel(pos,depth,width,height):
    # Positive determinant, historical threshold transform: local width→+Y, depth→−X.
    return Matrix(((0,-depth,0,pos[0]),(width,0,0,pos[1]),(0,0,height,pos[2]),(0,0,0,1)))
span=place("span","Masonry gate | central span",remodel((-8,0,6.245),.67,1.78,.236))
flanks=[]
for sign in (-1,1):
    flanks+=place("tower","Masonry gate | flank",remodel((-8,sign*7.84,0),.65,.94,7.19/5.275))

seam=[]
for sign in (-1,1):
    for j in range(9):
        y=sign*(6.32+1.80+j*3.595)
        seam+=place("bay",f"Seam | bay {sign:+d} {j}",matrix((0,y,0),math.pi/2))
    seam+=place("post","Seam | post",matrix((0,sign*6.73,0),math.pi/2))
    seam+=place("leaf","Seam | leaf held open",matrix((1.42,sign*6.73,0),0 if sign>0 else math.pi))
    # Original west-side furnishings separate safe plaza from the road without props in the visual corridor.
    place("banner","Town | heraldry",matrix((-9.75,sign*8.36,2.13),-math.pi/2,.74))
    place("planter","Town | flowers",matrix((-12.2,sign*8.10,0),math.pi/2,.84))
    place("lantern","Town | wall lamp",matrix((-9.94,sign*6.61,3.14),-math.pi/2,.62))
place("stall","Town | shaded trade",matrix((-16.0,-9.0,0),-.12,.91))
for x,y,k in ((-16.8,11.2,1.17),(-20.4,-13.2,.85),(-9.5,-16.8,1.36)):
    place("tree","West plaza | canopy",matrix((x,y,0),x*.7,k))
for i,(x,y) in enumerate(((-15.2,-7.7),(-16.4,-8.1),(-12,9.23),(5.4,6.62))):
    place("crate","Town | timber cargo",matrix((x,y,0),.17*i,.87 if i<3 else .6))
for i,(x,y) in enumerate(((-18,7.4),(-13.6,6.5),(4.2,-6.5),(4.1,6.8))):
    place("cone","Boundary | safety cone",matrix((x,y,0),i*1.1,.89))

def mat(name,base,variation=None,size=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*base,1);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links; p=n.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*base,1)
    p.inputs["Roughness"].default_value=.83
    if variation:
        tex=n.new("ShaderNodeTexCoord");noise=n.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=size;l.new(tex.outputs["Object"],noise.inputs["Vector"])
        rgb=n.new("ShaderNodeValToRGB");rgb.color_ramp.elements[0].position=.19;rgb.color_ramp.elements[0].color=(*base,1)
        rgb.color_ramp.elements[1].position=.8;rgb.color_ramp.elements[1].color=(*variation,1)
        l.new(noise.outputs["Fac"],rgb.inputs[0]);l.new(rgb.outputs[0],p.inputs["Base Color"])
        fine=n.new("ShaderNodeTexNoise");fine.inputs["Scale"].default_value=23;l.new(tex.outputs["Object"],fine.inputs["Vector"])
        bump=n.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.16;bump.inputs["Distance"].default_value=.043
        l.new(fine.outputs["Fac"],bump.inputs["Height"]);l.new(bump.outputs["Normal"],p.inputs["Normal"])
    return m
asphalt=mat("East gray tarmac",(.078,.081,.082),(.164,.162,.154),.43)
clay=mat("Rust clay",(.168,.086,.048),(.325,.193,.127),.38)
stone=mat("Warm plaza limestone",(.29,.242,.172),(.53,.467,.350),.7)
stone2=mat("Warm plaza terracotta",(.276,.122,.063),(.465,.245,.135),.73)
shoulder=mat("East road curb",(.137,.135,.126),(.241,.235,.215),.87)
ivory=mat("Paint / light",(.71,.65,.46))
amber=mat("Paint / amber",(.69,.35,.09))
signal=mat("Readout / dark petrol",(.028,.089,.090))
sandstone=mat("Town wing masonry",(.28,.149,.063),(.47,.297,.151),1.2)
olive=mat("Road edge grass",(.115,.144,.063),(.201,.221,.088),.76)
graphite=mat("Outland dark cladding",(.113,.130,.137),(.206,.227,.216),1.32)
def box(name,p,dim,ma,rot=0):
    a,b,c=[d/2 for d in dim]
    v=[(x*a,y*b,z*c) for z in (-1,1) for y in (-1,1) for x in (-1,1)]
    v=[tuple(Matrix.Rotation(rot,3,"Z")@Vector(q)+Vector(p)) for q in v]
    f=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.materials.append(ma);me.update()
    o=bpy.data.objects.new(name,me);s.collection.objects.link(o);return o
box("Context ground | packed clay",(17,0,-.34),(196,178,.58),clay)
box("West plaza apron",(-29,0,-.09),(42,46,.15),stone)
box("East approach | tarmac",(33,0,-.10),(74,12.5,.20),asphalt)
for side in (-1,1):
    for i in range(6):
        y=side*(10.20+i*2.12)
        box("West gate | low stone wing",(-8.2,y,1.45),(1.26,2.107,2.90),sandstone)
        box("West gate | wing cap",(-8.20,y,2.97),(1.46,2.13,.17),stone)
    box("Continuous curb",(32,side*6.11,.04),(65,.26,.12),shoulder)
    box("East verge",(30,side*11.4,-.39),(62,9.5,.73),olive)
    for j in range(4):
        x=1.9+j*.91;y=side*(4.65+j*.19)
        box("Boundary lane paint",(x,y,.009),(1.3,.28,.016),amber,.44*side)
for i in range(20):box("East road center marking",(3+3.3*i,0,.005),(1.48,.11,.013),ivory)
rng=random.Random(30041)
for j in range(12):
    for i in range(23):
        x=-43+i*1.73+(j%2)*.86;y=-10.01+j*1.82
        box("Clipped plaza stone",(x,y,-.021+rng.uniform(0,.005)),(1.706,1.788,.041),
            stone2 if (i%9==3 and j in (2,8)) or (j in (2,9) and i%4==0) else stone)
def label(name,content,p,size,sign,color):
    data=bpy.data.curves.new(name,"FONT");data.body=content;data.align_x="CENTER";data.align_y="CENTER";data.size=size;data.extrude=.003
    data.materials.append(color);o=bpy.data.objects.new(name,data);s.collection.objects.link(o)
    orientation=Matrix(((0,0,sign),(sign,0,0),(0,1,0)))
    o.matrix_world=Matrix.Translation(p)@orientation.to_4x4()
for sign in (-1,1):
    x=-8+sign*1.62
    z=7.43 if sign<0 else 7.62
    box("Gate plaque",(x,0,z),(.14,3.32,.63),signal)
    label("Gate name","EAST GATE",(x+sign*.076,0,z),.43,sign,ivory)
    for j,(txt,y) in enumerate([("WEST / NO ENEMIES",7.82),("EAST / COMBAT LV 1–20",-7.82)]):
        box("Safety wayfinding",(x,y,4.2),(.14,2.67,.47),signal if j==0 else graphite)
        label("Safety wayfinding letter",txt,(x+sign*.076,y,4.2),.203,sign,ivory if j==0 else amber)
# East backdrop deliberately carries no combat camp or runtime placement.
for j,(x,y,w,d,h) in enumerate([(29,-23,6,5,4.2),(34,-26,9,6,3.2),(42,24,7,6,6.1),
        (59,-16,10,7,4.3),(62,21,7,5,7.3),(75,33,13,8,5.2),(80,-31,14,8,6.8)]):
    box("Outland silhouette",(x,y,h/2),(w,d,h),graphite)
    box("Warm roof edge",(x,y,h),(w+.3,d+.3,.24),shoulder)
for j in range(160):
    x=55+j*.6
    side=-1 if j%2 else 1
    y=side*(14+.20*j+1.6*math.sin(j*1.62))
    # Two soft, off-road silhouettes break the empty horizon.
    h=.55+.45*math.sin(.13*j+1.9)**2
    box("Outland foothill | far shoulder",(x,y,-.08),(4.5,6.0,h),clay)
for j in range(45):
    x=rng.uniform(12,80); y=rng.choice([-1,1])*rng.uniform(14,53)
    k=rng.uniform(.19,.72)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,k*.16))
    o=bpy.context.object;o.name="Landscape dressing | gravel";o.scale=(k,k*.6,k*.45);o.rotation_euler.z=rng.uniform(0,6);o.data.materials.append(shoulder)
# Geometry-only proof in the actual chosen stage, excludes frame/image crops.
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
points=0
for z in (.25,.8,1.7,2.4):
    for k in range(-12,13):
        y=k*.49
        h,_,_,_,ob,_=s.ray_cast(dg,(-25,y,z),(1,0,0),distance=39)
        assert not h,(y,z,ob.name if ob else None)
        points+=1
closed=[]
for y in (-23,-17,-11,11,17,23):
    hit,_,_,_,ob,_=s.ray_cast(dg,(-1.5,y,1.3),(1,0,0),distance=3)
    assert hit and ob.name.startswith("Seam | bay"), (y,ob.name if ob else None)
    closed.append(y)
def coords(seq):return [o.matrix_world@v.co for o in seq for v in o.data.vertices]
span_bottom=min(v.z for v in coords(span)); jamb_gap=2*min(abs(v.y) for v in coords(flanks))
assert abs(span_bottom-6.245)<.001
assert jamb_gap>12
(out/"w0a-east-gate-boundary.json").write_text(json.dumps({
    "scope":"self-contained static staging; not native terrain, collision or placement",
    "west_mockup":"round-11-remaster/west/m07.jpg",
    "world_axis":"x east / y up / z south; Blender x east / z up / y north",
    "staged_gate_world_x":-8,"candidate_industrial_seam_world_x":0,
    "span_mesh_min_world_y":round(span_bottom,3),"minimum_masonry_jamb_gap_m":round(jamb_gap,3),
    "clear_points":points,"clear_corridor_sample_width_m":11.76,"elevation_m":[.25,.8,1.7,2.4],
    "blocked_far_seam_samples_blender_y":closed,
    "asset_ids":["WSC-SCENE-004","WSC-ARCH-001","WSC-MODULE-005","WSC-ARCH-002","WSC-MODULE-003","WSC-MODULE-031"]
},indent=2)+"\n")

world=bpy.data.worlds.new("West morning sky");world.use_nodes=True
n=world.node_tree.nodes;l=world.node_tree.links
sky=n.new("ShaderNodeTexSky");sky.sky_type="NISHITA";sky.sun_rotation=math.radians(136);sky.sun_elevation=math.radians(29)
sky.sun_size=math.radians(2.2);sky.sun_intensity=.7;sky.altitude=.13
l.new(sky.outputs[0],n["Background"].inputs[0]);n["Background"].inputs[1].default_value=.2
s.world=world
s.render.engine="CYCLES";s.cycles.samples=31;s.cycles.use_denoising=False;s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=89
data=bpy.data.cameras.new("Boundary walk");cam=bpy.data.objects.new("Boundary walk",data);s.collection.objects.link(cam);s.camera=cam
for name,eye,at,w,h,f in [
  ("plaza",(-30,2.4,1.65),(-6,0,3.31),1080,1360,27),
  ("threshold",(-3.55,-1.05,1.68),(26,1.8,2.48),1340,820,28),
  ("overhead",(-15,-36,27),(2,1,0),1440,900,44)]:
    s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100; data.lens=f
    cam.location=eye;cam.rotation_euler=(Vector(at)-cam.location).to_track_quat("-Z","Y").to_euler()
    s.render.filepath=str(out/f"nov23-east-boundary-{name}.jpg");bpy.ops.render.render(write_still=True)
