"""Extract the source Station 4 turntable and add a separately named fixed collar."""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory
out=output_directory()
clear_scene()
s=bpy.context.scene
origin=Vector((-147,103,0))
source=Path(__file__).resolve().parents[1]/"west-movers-roof/movers.py"
donor_sha="2b5a6983fde90b9374414559fe51603aa939eaa46df42de913d012eda9e2df15"
assert hashlib.sha256(source.read_bytes()).hexdigest()==donor_sha
tree=ast.parse(source.read_bytes())
factory=[]
for e in tree.body:
    if isinstance(e,ast.FunctionDef) and e.name in {"mat","box","beam","cyl"}:factory.append(e)
    if isinstance(e,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="M" for t in e.targets):factory.append(e)
    if isinstance(e,ast.Expr) and isinstance(e.value,ast.Call) and e.value.args:
        a=e.value.args[0]
        if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.startswith("Station4 "):factory.append(e)
assert len(factory)==9
env=dict(bpy=bpy,Vector=Vector)
exec(compile(ast.Module(factory,[]),str(source),"exec"),env)
donors=sorted(s.objects,key=lambda o:o.name)
assert len(donors)==4
base=next(o for o in donors if "pedestal" in o.name);base.name="Movers_Pedestal"
disc=next(o for o in donors if "rotating disc" in o.name);disc.name="Movers_Disc"
axle=next(o for o in donors if "axle" in o.name);axle.name="Movers_Axle"
arm=next(o for o in donors if "sweep arm" in o.name);arm.name="Movers_SweepArm"
def get_bounds(ob):
    v=[ob.matrix_world@p.co for p in ob.data.vertices]
    return [[round(f(p[i] for p in v),4) for i in range(3)] for f in (min,max)]
for o in donors:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    for m in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=m.name)
    o.location-=origin
bpy.context.view_layer.update()
before={o.name:get_bounds(o) for o in donors}
assert before[base.name][1][2]==5.4 and before[disc.name][0][2]==5.7
assert before[disc.name][0][0]==-4.5 and before[disc.name][1][0]==4.5 and before[disc.name][1][2]==6
assert before[axle.name][0][2]==5.85 and before[axle.name][1][2]==7.05

def empty(n,p):
    o=bpy.data.objects.new(n,None);bpy.context.collection.objects.link(o);o.location=p
    bpy.context.view_layer.update()
    return o
dp=empty("Movers_DiscYaw",(0,0,5.85))
ap=empty("Movers_ArmYaw",(0,0,6.65))
for o,p in [(disc,dp),(axle,ap),(arm,ap)]:
    keep=o.matrix_world.copy();o.parent=p;o.matrix_world=keep

# Just a studio art closure of the existing vertical gap, not a claim about hardware or friction.
cyl=env["cyl"]
collar=cyl("Art-only bearing collar",(0,0,5.55),.87,.304,"rubber");collar.name="Movers_BearingCollar"
shoulder=cyl("Collar reveal",(0,0,5.57),.89,.085,"light");shoulder.name="Movers_BearingCollar_Accent"
for m in (collar,shoulder):
    v=m.modifiers.new("Soft seam","BEVEL");v.width=.016;v.segments=2
    bpy.context.view_layer.objects.active=m;m.select_set(True);bpy.ops.object.modifier_apply(modifier=v.name)
all_objects=[*donors,collar,shoulder,dp,ap]
file=out/"wsc-kit-002-station4-spinner.glb"
export(all_objects,file)
for o in all_objects:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(file))
names={o.name:o for o in s.objects if o.name.startswith("Movers_")}
assert len(names)==8
base,disc,axle,arm,dp,ap=[names[k] for k in ("Movers_Pedestal","Movers_Disc","Movers_Axle","Movers_SweepArm","Movers_DiscYaw","Movers_ArmYaw")]
bpy.context.view_layer.update()
assert disc.parent==dp and arm.parent==ap and axle.parent==ap and not base.parent
for k,b in before.items():assert get_bounds(names[k])==b,(k,get_bounds(names[k]),b)
assert [round(v,4) for v in dp.location]==[0,0,5.85]
assert [round(v,4) for v in ap.location]==[0,0,6.65]
for pivot in (dp,ap):pivot.rotation_mode="XYZ"
def mats():return {k:o.matrix_world.copy() for k,o in names.items()}
def unchanged(a,b):return all(abs(x-y)<1e-6 for r,t in zip(a,b) for x,y in zip(r,t))
neutral=mats()
dp.rotation_euler.z=math.radians(45);bpy.context.view_layer.update()
d_only=mats()
assert {k for k in names if not unchanged(neutral[k],d_only[k])}=={"Movers_DiscYaw","Movers_Disc"}
ap.rotation_euler.z=math.radians(115);bpy.context.view_layer.update()
second=mats()
assert {k for k in names if not unchanged(d_only[k],second[k])}=={"Movers_ArmYaw","Movers_Axle","Movers_SweepArm"}
for o in names.values():
    if o.type=="MESH":o.data.calc_loop_triangles()
tris=sum(len(o.data.loop_triangles) for o in names.values() if o.type=="MESH")
data=dict(scope="Static two-pivot art handoff; preview angles are not movement timing or collision.",
          origin_blender_world_m=list(origin),gltf_world_m=(-147,0,-103),disc_diameter_m=9,deck_top_m=6,
          donor_sha256=donor_sha,original_bounds_blender_m=before,source_gap_m=.30,
          fixed_collar_added=True,test_pose_deg=dict(disc=45,arm=115),triangles=tris,bytes=file.stat().st_size)
(out/"w6a-station4-spinner-check.json").write_text(json.dumps(data,indent=2)+"\n")

def mat(n,c,rough=.64,em=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Roughness"].default_value=rough;q.inputs["Emission Color"].default_value=(*c,1);q.inputs["Emission Strength"].default_value=em
    return m
stage=mat("Graphite plaque",(.065,.097,.108))
bg=mat("Blue studio floor",(.033,.065,.082))
cream=mat("Offwhite labels",(.82,.84,.74),.68,.28)
teal=mat("Temporary pose marks",(.12,.69,.65),.44,.23)
def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    b=o.modifiers.new("Edge softness","BEVEL");b.width=.14;b.segments=3
    return o
def label(word,size,p,m):
    c=bpy.data.curves.new(word,"FONT");c.body=word;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(word,c);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=.72;c.materials.append(m)
for x,labeltext,pose,ang in [(-5.6,"01  /  SOURCE POSE",neutral,0),(5.6,"02  /  INDEPENDENT YAW",second,45)]:
    off=Matrix.Translation((x,0,0))
    for k,o in names.items():
        if o.type!="MESH":continue
        w=bpy.data.objects.new(labeltext+" | "+k,o.data);bpy.context.collection.objects.link(w);w.matrix_world=off@pose[k]
    for i,(r,w) in enumerate([(3.22,.64),(3.64,.45),(3.98,.25)]):
        d=math.radians(ang+22)
        o=box("Pose-only deck marker",(x+r*math.cos(d),r*math.sin(d),6.007),(.23,w,.012),teal);o.rotation_euler.z=d
    box("Studio stand",(x,0,-.23),(10.28,10.08,.46),stage)
    label(labeltext,.47,(x,-4.74,.046),cream)
for o in tuple(names.values()):bpy.data.objects.remove(o,do_unlink=True)
box("Neutral background",(0,0,-.64),(200,200,.32),bg)
label("WEST MOVERS  /  STATION 4",.81,(0,5.82,8.48),cream)
label("9 M DISC     •     TWO INDEPENDENT PIVOTS",.40,(0,5.6,7.93),teal)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,w,sz,c in [((-12,-14,19),9400,15,(1,.84,.65)),((14,-2,15),7400,17,(.69,.87,1)),((0,15,18),9000,14,(.73,.98,.94))]:
    bpy.ops.object.light_add(type="AREA",location=p);o=bpy.context.object;o.data.energy=w;o.data.size=sz;o.data.color=c;aim(o,(0,0,3))
bpy.ops.object.camera_add(location=(0,-27,22))
s.camera=bpy.context.object;aim(s.camera,(0,0,3.9));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=23.3
s.world.color=(.23,.24,.25)
s.render.engine='CYCLES';s.cycles.samples=42;s.cycles.use_denoising=False
s.render.resolution_x=1440;s.render.resolution_y=1020;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-w6a-station4-spinner.jpg")
bpy.ops.render.render(write_still=True)
