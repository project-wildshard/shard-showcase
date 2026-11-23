"""WSC-PROP-028 animation-only alternative for the existing three cloth meshes."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
root=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
donor=root/"wsc-prop-028-course-flag.glb"
clear_scene()
s=bpy.context.scene;s.render.fps=24;s.frame_start=0;s.frame_end=60

def load(path):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted(set(s.objects)-before,key=lambda x:x.name)
orig=load(donor)
cloth_parts={"Wind-shaped swallowtail sailcloth","Bound longitudinal edge","Weathered stitched hoist"}
cloth_parts_ob=[o for o in orig if o.data.name in cloth_parts]
rig=[o for o in orig if o.data.name not in cloth_parts]
assert len(cloth_parts_ob)==3 and len(rig)==5
donor_coords=[o.matrix_world@v.co for o in cloth_parts_ob for v in o.data.vertices]
orig_tris=0
for o in cloth_parts_ob:
    o.data.calc_loop_triangles();orig_tris+=len(o.data.loop_triangles)
# Keep the exact donor model-space coordinates and material slots.
copies=[]
for o in cloth_parts_ob:
    d=o.data.copy();d.transform(o.matrix_world)
    ob=bpy.data.objects.new(o.name+" reusable gust",d);bpy.context.collection.objects.link(ob)
    copies.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in copies:o.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.object.join()
cloth=bpy.context.object;cloth.name="CourseFlag_Cloth_Gust"
for o in cloth_parts_ob:bpy.data.objects.remove(o,do_unlink=True)
basis=cloth.shape_key_add(name="Basis")
keys=[cloth.shape_key_add(name="Wave A"),cloth.shape_key_add(name="Wave B")]
for i,v in enumerate(basis.data):
    base=v.co.copy();x,y,z=base
    u=max(0,min(1,(x+.40)/1.09));w=u**1.32
    def deflection(phase):
        f=4.45*u+phase
        return Vector((.030*w*math.sin(f),.225*w*math.sin(f),.092*w*math.cos(f)))
    a=deflection(0);b=deflection(math.pi/2)
    # Bake the negative envelope into the basis so both weights stay in [0,1].
    # At 0.5/0.5 the unchanged donor position is exactly restored.
    v.co=base-a-b
    keys[0].data[i].co=base+a-b
    keys[1].data[i].co=base-a+b
    if x<=-.40:assert all((k.data[i].co-base).length<1e-6 for k in keys)
for frame in range(0,61,5):
    t=(frame%60)*math.tau/60
    wave=math.sin(t);phase=math.cos(t)
    for k,v in zip(keys,((wave+1)*.5,(phase+1)*.5)):
        k.value=v;k.keyframe_insert("value",frame=frame)
cloth.data.shape_keys.animation_data.action.name="Course flag gust"
s.frame_set(0)
bpy.ops.export_scene.gltf(filepath=str(out/"wsc-prop-028-course-flag-gust.glb"),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=False,export_morph_normal=True)
bpy.data.objects.remove(cloth,do_unlink=True)
clip_path=out/"wsc-prop-028-course-flag-gust.glb"
re=load(clip_path)
assert len(re)==1
flag=re[0];flag.data.calc_loop_triangles()
assert len(flag.data.loop_triangles)==orig_tris
sk=flag.data.shape_keys
assert sk.animation_data and len(sk.key_blocks)==3
assert sk.animation_data.action.frame_range[:]==(0,60)
k0,k1,k2=sk.key_blocks
rest=[flag.matrix_world@((a.co+b.co)*.5) for a,b in zip(k1.data,k2.data)]
# Two .5 weights restore the donor. Reimport can merge/split coincident normals,
# so test point coverage in both directions instead of requiring matching indexes.
def check_points(src,tgt):
    tree=KDTree(len(tgt))
    for i,co in enumerate(tgt):tree.insert(co,i)
    tree.balance()
    assert all(tree.find(p)[2]<2e-6 for p in src)
check_points(rest,donor_coords)
check_points(donor_coords,rest)
vtx=max(range(len(flag.data.vertices)),key=lambda i:flag.data.vertices[i].co.x)
def movements(f):
    s.frame_set(f);bpy.context.view_layer.update()
    de=flag.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return de.data.vertices[vtx].co.copy()
a=movements(0);b=movements(25);c=movements(60)
assert (a-c).length<1e-6 and (a-b).length>.14,(a,b,c)
print(clips:=dict(bytes=clip_path.stat().st_size,triangles=orig_tris,
    tip_delta_m=round((a-b).length,4),seconds=2.5,
    donor_sha256=hashlib.sha256(donor.read_bytes()).hexdigest()))
(out/"wsc-prop-028-course-flag-gust.json").write_text(json.dumps(clips,indent=2)+"\n")

def mat(n,c,rough=.72,emit=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Roughness"].default_value=rough
    q.inputs["Emission Color"].default_value=(*c,1);q.inputs["Emission Strength"].default_value=emit
    return m
platform=mat("Graphite display footings",(.070,.107,.13))
background=mat("Steel-grey background",(.039,.072,.087))
ivory=mat("Ivory proof title",(.83,.86,.79),.76,.22)
mint=mat("Mint small labels",(.24,.72,.66),.7,.35)
def label(st,size,p,ink):
    c=bpy.data.curves.new(st,"FONT");c.body=st;c.align_x="CENTER";c.size=size
    ob=bpy.data.objects.new(st,c);bpy.context.collection.objects.link(ob);ob.location=p
    ob.rotation_euler.x=.96;c.materials.append(ink)
for i,(x,f,txt) in enumerate([(-2.15,0,"01   /   CREST"),(0,17,"02   /   CROSSWIND"),(2.15,35,"03   /   RETURN")]):
    s.frame_set(f);bpy.context.view_layer.update()
    # Freeze the exact imported clip evaluation for the comparison render.
    e=flag.evaluated_get(bpy.context.evaluated_depsgraph_get())
    d=bpy.data.meshes.new_from_object(e)
    o=bpy.data.objects.new(txt,d);bpy.context.collection.objects.link(o)
    pose=Matrix.Translation((x,0,0))@Matrix.Rotation(math.radians(-23),4,'Z')
    o.matrix_world=pose@flag.matrix_world
    for src in rig:
        q=bpy.data.objects.new(f"Donor hardware {i} | {src.name}",src.data)
        bpy.context.collection.objects.link(q);q.matrix_world=pose@src.matrix_world
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,0,-.071))
    o=bpy.context.object;o.dimensions=(1.76,1.86,.14)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(platform)
    b=o.modifiers.new("Chamfer","BEVEL");b.width=.027;b.segments=2
    label(txt,.109,(x,-.89,.064),ivory)
for o in [flag,*rig]:bpy.data.objects.remove(o,do_unlink=True)
label("COURSE FLAG  /  WIND LOOP",.258,(0,.83,2.85),ivory)
label("WSC-PROP-028     ·     EXACT MODEL, ANIMATED CLOTH",.115,(0,.82,2.59),mint)
bpy.ops.mesh.primitive_plane_add(size=140,location=(0,0,-.144))
bpy.context.object.data.materials.append(background)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
s.world.color=(.16,.20,.22)
for p,w,r,c in [((-3,-5,6),1160,5,(1,.86,.70)),((5,-2,5),710,5,(.67,.86,1)),((0,4,5),1030,4,(.73,1,.94))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=w;o.data.size=r;o.data.color=c;aim(o,(0,0,1))
bpy.ops.object.camera_add(location=(0,-9.3,5.20))
s.camera=bpy.context.object;aim(s.camera,(0,0,1.21));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=6.74
s.render.engine="CYCLES";s.cycles.samples=42;s.cycles.use_denoising=False
s.render.resolution_x=1460;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-w11a-course-flag-wind.jpg")
bpy.ops.render.render(write_still=True)
