"""Extract the actual WSC-PROP-034 hoop and stage a W7a roof-mount proposal."""
import collections
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
source=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art/wsc-prop-034-grapple-hook-post.glb"
assert hashlib.sha256(source.read_bytes()).hexdigest()=="e37691b7e816021608a3da7e1936dee501fa903662723eb7e405dd59869950c7"
clear_scene()

def imported(path):
    pre=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return set(bpy.context.scene.objects)-pre

def points(o,delta=Vector((0,0,0))):
    return [o.matrix_world@v.co+delta for v in o.data.vertices]

def fingerprint(ob,delta=Vector((0,0,0))):
    # Geometry parity, ignoring point order and seam-induced vertex duplication.
    obs=collections.Counter()
    for o in ob:
        c=[tuple(round(x,5) for x in v) for v in points(o,delta)]
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            obs[(o.data.materials[o.data.polygons[t.polygon_index].material_index].name.split(".")[0],
                 tuple(sorted(c[i] for i in t.vertices)))]+=1
    return obs

post=imported(source)
assert len(post)==6 and all(o.type=="MESH" for o in post)
select=sorted([o for o in post if o.data.name in {"Continuous compact cyan hoop","Recessed mint channel"}],key=lambda x:x.data.name)
assert len(select)==2
xyz=[v for o in select for v in points(o)]
center=Vector([(max(v[k] for v in xyz)+min(v[k] for v in xyz))*.5 for k in range(3)])
assert (center-Vector((0,0,2.557))).length<1e-5
want=fingerprint(select,-center)
for o in select:
    mesh=o.data.copy();mesh.transform(Matrix.Translation(-center)@o.matrix_world)
    p=bpy.data.objects.new("Grapple hoop | "+o.data.name,mesh)
    bpy.context.collection.objects.link(p)
hoop=out/"wsc-kit-004-grapple-hoop.glb"
extract=sorted(set(bpy.context.scene.objects)-post,key=lambda x:x.name)
export(extract,hoop)
for o in extract:bpy.data.objects.remove(o,do_unlink=True)
fresh=imported(hoop)
assert len(fresh)==2 and fingerprint(fresh)==want
assert sum(want.values())==2112
coords=[v for o in fresh for v in points(o)]
dims=[round(max(v[k] for v in coords)-min(v[k] for v in coords),4) for k in range(3)]
assert dims==[.736,.0896,.736],dims

# Representative ring-center heights. These are *not* evaluated eye positions.
anchors=[
    ("1 · Pole",(-150,12,-44),"W08 pole proxy"),
    ("2 · Pole",(-170,16,-68),"W08 pole proxy"),
    ("3 · Tank roof",(-198,19.25,-92),"study rim point; 1.25 m above the roof"),
    ("4 · Mast",(-200,28,-68),"W08 mast proxy"),
    ("5 · Tower",(-214.5,45.8,-34),"W08 tower proxy"),
]
old_tank=(-206,19.7,-104)
def dist(a,b):return round(math.dist(a,b),2)
report={
    "scope":"Static placement study; center distances are not player reach, clearance or sightline tests.",
    "floor_plan_coordinates":"world x,y,z with y up",
    "source_donor":{"asset":"WSC-PROP-034","sha256":hashlib.sha256(source.read_bytes()).hexdigest()},
    "hoop":{"origin":"ring center","normal_axis_gltf":"+Z convention","triangles":2112,"bounds_blender_m":dims,"bytes":hoop.stat().st_size},
    "centers":[dict(label=name,world_m=p,provenance=why) for name,p,why in anchors],
    "adjacent_spans_m":[dist(a[1],b[1]) for a,b in zip(anchors,anchors[1:])],
    "old_roof_proxy_m":old_tank,"pole_2_to_old_roof_proxy_m":dist(anchors[1][1],old_tank),
    "candidate_tank_rim_inset_m":round(16-math.hypot(8,12),2),
    "default_eye_to_hook_limit_m":38,
    "w7a_plan_hops_m":[23,31,35,21,36],
    "w7b_separate_endpoints_m":[[-212,45,-34],[-115,14,-16.5]],
}
(out/"w7a-hoop-placement-study.json").write_text(json.dumps(report,indent=2)+"\n")
print(report)

def mat(n,c,rough=.54,metal=.16,glow=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Emission Color"].default_value=(*c,1);p.inputs["Emission Strength"].default_value=glow
    p.inputs["Roughness"].default_value=rough;p.inputs["Metallic"].default_value=metal
    return m
blue=mat("Slate tank deck",(.083,.159,.187),.61)
orange=mat("Clipped orange mounting shoe",(.71,.21,.04),.41,.28)
gray=mat("Unpainted mount steel",(.13,.151,.157),.57,.3)
shadow=mat("Studio slate",(.045,.065,.074),.82)
text=mat("Warm-grey type",(.82,.87,.82),.79,.05,.18)
cyan=mat("Cyan annotation",(.103,.65,.70),.5,.0,.49)

def box(n,xyz,d,ma,bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
    if bevel:
        b=o.modifiers.new("Soft edges","BEVEL");b.width=bevel;b.segments=2
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

def label(value,size,p,ma):
    c=bpy.data.curves.new(value,"FONT");c.body=value;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(value,c);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=.96;c.materials.append(ma)

for o in post:o.matrix_world=Matrix.Translation((-1.65,0,0))@o.matrix_world
for o in fresh:o.matrix_world=Matrix.Translation((1.65,0,1.25))@o.matrix_world

box("Post stage",(-1.65,0,-.14),(2.80,2.31,.28),blue,.054)
box("Tank rim example stage",(1.65,0,-.14),(2.80,2.31,.28),blue,.054)
box("Foot bolted to deck",(1.65,.04,.046),(.74,.59,.092),gray,.033)
box("Tank rim mount body",(1.65,.073,.43),(.22,.21,.73),orange,.036)
box("Supporting saddle",(1.65,.030,.86),(.295,.20,.105),gray,.022)
for x in (1.41,1.89):
    for y in (-.133,.205):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.046,depth=.033,location=(x,y,.099))
        bpy.context.object.data.materials.append(orange)
for x,cap in [(-1.65,"01   /   EXISTING POST"),(1.65,"02   /   ROOF MOUNT TEST")]:
    label(cap,.147,(x,-1.11,.073),text)
label("WEST GRAPPLE  /  SHARED HOOP",.277,(0,1.29,3.21),text)
label("WSC-KIT-004     ·     RING CENTER ORIGIN",.129,(0,1.23,2.97),cyan)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.281))
bpy.context.object.data.materials.append(shadow)
s=bpy.context.scene;s.world.color=(.20,.22,.23)

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,power,size,col in [((-4,-6,7),1300,5,(1,.87,.69)),((5,-1,6),770,5,(.70,.88,1)),((0,5,6),1050,5,(.73,1,.88))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=col
    aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(0,-9.3,5.28))
s.camera=bpy.context.object;aim(s.camera,(0,0,1.45));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=7.00
s.render.engine="CYCLES";s.cycles.samples=44;s.cycles.use_denoising=False
s.render.resolution_x=1500;s.render.resolution_y=1040;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-grapple-hoop-reuse.jpg")
bpy.ops.render.render(write_still=True)
