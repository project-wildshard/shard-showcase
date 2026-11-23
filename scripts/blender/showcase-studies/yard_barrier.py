"""A portable fictional pedestrian barrier for WSC-PROP-008, from its concept sheet."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory
out=output_directory()
s=bpy.context.scene
clear_scene()

def mat(n,c,metal,rough):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
    p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metal;p.inputs["Roughness"].default_value=rough
    return m
steel=mat("Pressed gunmetal panels",(.188,.210,.214),.60,.47)
orange=mat("Tangerine enamel end caps",(.86,.166,.024),.39,.45)
dark=mat("Black rubber foot shoes",(.056,.061,.063),.06,.81)
bolt=mat("Bright fasteners",(.32,.34,.35),.72,.37)
P=[]
def mesh(name,v,f,m,add=True):
    g=bpy.data.meshes.new(name);g.from_pydata(v,[],f);g.update()
    o=bpy.data.objects.new(name,g);s.collection.objects.link(o);g.materials.append(m)
    if add:P.append(o)
    return o
boxf=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def box(n,p,dim,m,bev=0,add=True):
    a,b,c=[v/2 for v in dim];x,y,z=p
    verts=[(x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    o=mesh(n,verts,boxf,m,add)
    if bev:
        bpy.context.view_layer.objects.active=o
        md=o.modifiers.new("One stamped chamfer","BEVEL");md.width=bev;md.segments=1
        bpy.ops.object.modifier_apply(modifier=md.name)
    return o
def foot(x):
    v=[(x+i*a,j*b,z) for a,b,z in [(.225,.235,0),(.178,.165,.115)] for j in (-1,1) for i in (-1,1)]
    return mesh("Wedge-shaped rubber foot",v,boxf,dark)
def insert(n,x,z,m,side):
    r=.030 if z>.88 else .022
    at=side*(.109 if z>.88 else .088)
    v=[(x+r*u,at+side*w,z+r*h) for w,k in [(0,1),(.015,.70)]
        for u,h in [(math.cos(a*math.tau/6)*k,math.sin(a*math.tau/6)*k) for a in range(6)]]
    f=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)]
    if side<0:f=[tuple(reversed(a)) for a in f]
    return mesh(n,v,f,m)
def gusset(sign):
    tri=[(sign*.76,-.088,.819),(sign*1.11,-.088,.819),(sign*1.11,-.088,.557)]
    v=tri+[(x,-.068,z) for x,y,z in tri]
    ff=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
    if sign>0:ff=[tuple(reversed(a)) for a in ff]
    return mesh("Front orange triangular plate",v,ff,orange)

for x in (-1.055,1.055):
    foot(x)
    box("Orange end", (x,0,.457),(.209,.185,.724),orange,.023)
    for side in (-1,1):
        for z in (.255,.706):insert("End stud",x,z,bolt,side)
box("Recessed bottom rail",(0,0,.135),(2.180,.111,.09),dark,.011)
box("Top rolled rail",(0,0,.888),(2.56,.203,.124),steel,.023)
for x in (-.64,0,.64):
    box("Stamped insert",(x,0,.463),(.616,.143,.651),steel,.018)
    for side in (-1,1):
        for z in (.207,.724):
            for dx in (-.226,.226):insert("Small panel rivet",x+dx,z,bolt,side)
for sign in (-1,1):gusset(sign)
for x in (-1.04,0,1.04):
    for side in (-1,1):insert("Rail button",x,.904,bolt,side)
# Keep one stable pivot, one visible mesh and material slots in the authored order.
bpy.ops.object.select_all(action="DESELECT")
for o in P:o.select_set(True)
bpy.context.view_layer.objects.active=P[0]
bpy.ops.object.join();obj=bpy.context.object;obj.name="WSC-PROP-008 | Yard barrier"
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
file=out/"wsc-prop-008-yard-barrier.glb"
export([obj],file)
# Grounded center origin and a visually closed middle across the main panels.
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(file))
meshes=[o for o in s.objects if o.type=="MESH"]
assert len(meshes)==1
re=meshes[0]
assert re.location.length<.001
positions=[re.matrix_world@v.co for v in re.data.vertices]
a,c=([round(fn(p[k] for p in positions),4) for k in range(3)] for fn in (min,max))
assert a[2]==0 and abs((a[0]+c[0])/2)<.001 and abs((a[1]+c[1])/2)<.001
f=[list(p.vertices) for p in re.data.polygons]
rays=BVHTree.FromPolygons(positions,f)
assert all(rays.ray_cast(Vector((x,-1,.51)),Vector((0,1,0)),2)[0] is not None for x in (-1.05,-.64,0,.64,1.05))
assert all(rays.ray_cast(Vector((x,-1,.057)),Vector((0,1,0)),2)[0] is None for x in (-.65,0,.65))
size=file.stat().st_size
assert size<=65_536,size
dims=[round(v-u,4) for u,v in zip(a,c)]
manifest={"asset_id":"WSC-PROP-008","convention":"meters; X span, glTF Y up, +Z front",
          "blender_bounds_min":a,"blender_bounds_max":c,"size_x_depth_height":dims,
          "bytes":size,"triangles":sum(len(x)-2 for x in f),"primitives":len(re.data.materials),
          "presentation":"procedural concept-derived prop; not an exact historic shot match",
          "verification":"GLB reimport, origin and five visual ray samples; no physics collision"}
(out/"wsc-prop-008-yard-barrier.json").write_text(json.dumps(manifest,indent=2)+"\n")

floor=mat("Studio slate",(.065,.100,.116),.08,.72)
base=mat("Backdrop",(.039,.059,.071),.04,.80)
ink=mat("Platform text",(.72,.77,.66),.08,.70)
def platform(x,y,n):
    box("Studio riser",(x,y,-.067),(3.04,1.19,.13),floor,.047,False)
    d=bpy.data.curves.new(n,"FONT");d.body=n;d.align_x="CENTER";d.size=.115;d.materials.append(ink)
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=(x,y-.52,.008);o.rotation_euler.x=.33
platform(-1.66,0,"FRONT  /  ORANGE GUSSETS")
platform(1.66,.06,"BACK  /  THREE STAMPED PANELS")
re.location=(-1.66,0,0);re.rotation_mode="XYZ";re.rotation_euler.z=-.15
back=re.copy();s.collection.objects.link(back);back.location=(1.66,.06,0);back.rotation_euler.z=math.pi+.22
box("Backdrop floor",(0,0,-.169),(60,60,.078),base,0,False)
def aim(o,a):o.rotation_euler=(Vector(a)-o.location).to_track_quat("-Z","Y").to_euler()
def area(p,aimat,power,scale,tint):
    d=bpy.data.lights.new("Studio",type="AREA");d.size=scale;d.energy=power;d.color=tint
    o=bpy.data.objects.new("Studio",d);s.collection.objects.link(o);o.location=p;aim(o,aimat)
area((-4,-5,6),(0,0,.6),1370,4.8,(1,.80,.59))
area((4,-4,4),(0,0,.6),720,4.1,(.69,.84,1))
area((0,3,3.5),(0,0,.6),1120,4.2,(.8,1,.9))
s.world=bpy.data.worlds.new("studio ambience");s.world.color=(.22,.24,.25)
c=bpy.data.cameras.new("Two views");s.camera=bpy.data.objects.new("Two views",c);s.collection.objects.link(s.camera)
s.camera.location=(.2,-9.1,4.05);aim(s.camera,(0,0,.40));c.type="ORTHO";c.ortho_scale=7.06
s.render.engine="CYCLES";s.cycles.samples=36;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1440;s.render.resolution_y=680;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-yard-barrier-r01.jpg")
bpy.ops.render.render(write_still=True)
