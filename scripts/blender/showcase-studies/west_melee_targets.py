"""Static W3a/W3d target models and sample arm poses, not a gameplay simulation."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

out=output_directory()
scene=bpy.context.scene
clear_scene()


def mat(name,rgb,metal=0,rough=.55):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*rgb,1)
    n.inputs["Metallic"].default_value=metal;n.inputs["Roughness"].default_value=rough
    return m


iron=mat("Slate cast iron",(.061,.096,.107),.53)
oxide=mat("Orange enamel shoulders",(.51,.156,.056),.22)
canvas=mat("Oat canvas",(.50,.278,.121),0,.87)
leather=mat("Dark hide bands",(.129,.063,.033),.04,.74)
wood=mat("Warm timber",(.197,.084,.032),.0,.71)
brass=mat("Burnished fasteners",(.49,.254,.065),.64)
cream=mat("Ivory hoop accents",(.64,.49,.23),.15,.51)


def box(name,at,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new("Soft cast silhouette","BEVEL");mod.width=bevel;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o


def cyl(name,at,r,depth,m,n=10,along=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=at)
    o=bpy.context.object;o.name=name;o.rotation_euler=Vector(along).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(m)
    return o


def join(name,items,origin):
    bpy.ops.object.select_all(action="DESELECT")
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=o.data.name=name
    scene.cursor.location=origin;bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return o


def export(name,objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:o.select_set(True)
    f=out/(name+".glb")
    bpy.ops.export_scene.gltf(filepath=str(f),export_format="GLB",
                             use_selection=True,export_texcoords=False,export_animations=False)
    raw=f.read_bytes()
    assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
    doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    tris=sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
    assert len(raw)<65536 and "animations" not in doc and "images" not in doc
    return f,{"bytes":len(raw),"triangles":tris,"sha256":hashlib.sha256(raw).hexdigest()}


# The 1.9 m silhouette and 1.8 m bar at 1.3 m are the archived art proxy.
# The neutral bar sits in front of the torso with a separate z-axis pivot.
post=(0,-.52,1.30)
base=[
    box("Ground shoe",(0,0,.067),(.86,.74,.134),iron,.044),
    box("Bolted step",(0,0,.175),(.53,.48,.09),wood,.02),
    box("Practice frame",(0,.06,.72),(.25,.29,1.16),iron,.028),
    box("Lower canvas packing",(0,.034,1.08),(.56,.44,.79),canvas,.092),
    box("Shoulder packing",(0,.034,1.54),(.64,.46,.33),canvas,.096),
    box("Top cap",(0,.035,1.74),(.37,.36,.32),canvas,.075),
    box("Learning emblem",(0,-.206,1.56),(.198,.04,.12),oxide,.019),
    box("Pivot stay",(0,-.30,1.30),(.17,.54,.175),iron,.026),
    cyl("Fixed hub",post,.117,.17,brass,12),
]
for x in (-.27,.27):
    for y in (-.22,.22):base.append(cyl("Floor screw",(x,y,.137),.034,.028,brass,6))
anchor=join("Parry stand | static",(base),(0,0,0))
arm=[
    box("Crossbar core",post,(1.58,.155,.128),iron,.018),
    cyl("Rotating collar",(0,-.52,1.385),.094,.06,oxide,12),
]
for sign in (-1,1):
    arm.extend([
        box("Padded arm",(sign*.51,-.52,1.30),(.78,.252,.24),canvas,.058),
        box("Leather binding",(sign*.395,-.52,1.30),(.085,.264,.253),leather,.02),
        box("Leather binding",(sign*.756,-.52,1.30),(.070,.262,.25),leather,.016),
        box("Orange end boot",(sign*.852,-.52,1.30),(.083,.227,.215),oxide,.019),
    ])
swing=join("Parry arm | pose pivot",arm,post)
world=swing.matrix_world.copy();swing.parent=anchor;swing.matrix_world=world
parry=export("w3d-padded-parry-stand",[anchor,swing])
clear_scene()

# Keep the original ring plane offset, height and dimensions. A fork
# replaces the full-height middle proxy above the opening so it stays clear.
ring_base=[
    box("Anchor foot",(0,0,.063),(.87,.69,.126),iron,.046),
    box("Timber lower post",(0,0,.69),(.30,.30,1.19),wood,.025),
    box("Fork saddle",(0,.065,1.315),(1.36,.25,.15),iron,.025),
]
for x in (-.626,.626):
    ring_base.extend([
        box("Hoop fork upright",(x,.045,1.86),(.156,.23,1.08),iron,.026),
        box("Upper fork cap",(x,.045,2.365),(.178,.25,.07),brass,.012),
        box("Ring seat tab",(x,-.105,1.67),(.147,.24,.116),oxide,.018),
    ])
for x in (-.30,.30):
    ring_base.append(cyl("Floor screw",(x,-.20,.134),.036,.026,brass,6))
bpy.ops.mesh.primitive_torus_add(location=(0,-.2,2),rotation=(math.pi/2,0,0),
                                major_segments=28,minor_segments=8,
                                major_radius=.6,minor_radius=.12)
ring=bpy.context.object;ring.name="Measured ring | clear bore"
ring.data.materials.append(oxide);ring.data.materials.append(cream)
for f in ring.data.polygons:
    at=f.center; a=math.atan2(at.y,at.x)
    f.material_index=1 if int((a+math.pi)*28/math.tau) % 7 in (0,1) else 0
joined=join("Spear ring target",ring_base+[ring],(0,0,0))
spear=export("w3a-spear-ring",[joined])
clear_scene()


def load(path,at=(0,0,0)):
    before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    objects=[o for o in scene.objects if o not in before]
    for o in objects:
        if o.parent not in objects:o.location+=Vector(at)
    bpy.context.view_layer.update()
    return objects


def tree(objects):
    vv=[]; ff=[]
    for o in objects:
        if o.type!="MESH":continue
        off=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        o.data.calc_loop_triangles()
        ff.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
    return BVHTree.FromPolygons(vv,ff,all_triangles=True)


ring_import=load(spear[0])
geom=tree(ring_import)
clear=0
for x in (-.43,-.31,-.20,0,.20,.31,.43):
    for z in (-.43,-.31,-.20,0,.20,.31,.43):
        if math.hypot(x,z)>.44:continue
        assert geom.ray_cast(Vector((x,-2,2+z)),Vector((0,1,0)),4)[0] is None, (x,z)
        clear+=1
assert geom.ray_cast(Vector((.6,-2,2)),Vector((0,1,0)),4)[0] is not None
assert geom.ray_cast(Vector((0,-2,2.6)),Vector((0,1,0)),4)[0] is not None

def pose(obj,angle,rest):
    a=rest.translation
    obj.matrix_world=Matrix.Translation(a) @ Matrix.Rotation(math.radians(angle),4,"Z") @ Matrix.Translation(-a) @ rest
    bpy.context.view_layer.update()


rig=load(parry[0])
moving=[o for o in rig if o.name.startswith("Parry arm")][0]
rest=moving.matrix_world.copy()
assert abs(rest.translation.z-1.30)<.001 and abs(rest.translation.y+.52)<.001
width=max((rest@v.co).x for v in moving.data.vertices)-min((rest@v.co).x for v in moving.data.vertices)
assert abs(width-1.8)<.001
# Test the padded body away from the intentionally overlapping hub only.
a=Vector((0,-.52,1.30)); extents=[]
for angle in (0,28):
    pose(moving,angle,rest)
    assert (moving.matrix_world.translation-a).length<.001
    vv=[moving.matrix_world@v.co for v in moving.data.vertices]
    padded_core=[v for v in vv if abs(v.x)<.28]
    assert max(v.y for v in padded_core)<-.210, max(v.y for v in padded_core)
    extents.append([angle,round(min(v.y for v in vv),4),round(max(v.y for v in vv),4)])
assert extents[1][2]-extents[0][2] > .22

(out/"w3a-w3d-melee-targets.json").write_text(json.dumps({
    "scope":"reusable static art and two arm poses; no actor, attack timing, collider or scoring",
    "archive":"Raynos/project-wildshard-singleplayer@ce1cf050b3:art/showcase-template/round-5-blockout",
    "sword_row_world_xz":[[-30,86],[-24,86],[-18,86]],
    "spear_row_world_xz":[[-30,104],[-24,104],[-18,104]],
    "arm_pivot_blender_m":list(post),"arm_span_m":round(width,4),"arm_pose_y_extents_m":extents,
    "ring_centerline_m":.6,"ring_tube_m":.12,"ring_opening_m":.96,"ring_outer_m":1.44,
    "ring_front_offset_m":.2,"ring_center_height_m":2,"fork_height_m":2.4,
    "clear_axial_samples_in_inner_bore":clear,
    "assets":{"parry":parry[1],"spear":spear[1]},
},indent=2)+"\n")

if os.getenv("WILDSHARD_VALIDATE_ONLY")!="1":
    clear_scene()
    models=[]
    for x,angle in [(-1.06,0),(1.06,28)]:
        group=load(parry[0],(x,0,0))
        mm=[o for o in group if o.name.startswith("Parry arm")][0]
        pose(mm,angle,mm.matrix_world.copy())
        models.append(group)
    spear_objects=load(spear[0],(0,0,0))
    ground=mat("Range studio cast slate",(.040,.074,.084),.06,.70)
    box("Studio ground",(0,0,-.15),(150,150,.30),ground)
    scene.world=bpy.data.worlds.new("Blue range skylight");scene.world.color=(.13,.20,.23)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for n,p,energy,size,color in [
        ("Warm canvas softbox",(-3.4,-4,5),590,3.4,(1,.76,.49)),
        ("Neutral skylight",(3.6,-2.2,4.6),430,3.8,(.54,.76,1)),
        ("Blue shoulder rim",(0,2.5,4.3),520,3.3,(.39,.64,1)),
    ]:
        d=bpy.data.lights.new(n,"AREA");o=bpy.data.objects.new(n,d)
        d.energy,d.size,d.color=energy,size,color;scene.collection.objects.link(o);o.location=p;aim(o,(0,0,1.3))
    d=bpy.data.cameras.new("Melee target gallery")
    c=bpy.data.objects.new(d.name,d);scene.collection.objects.link(c);scene.camera=c
    d.type="ORTHO";scene.render.engine="CYCLES";scene.cycles.samples=44;scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format="JPEG"
    scene.render.image_settings.quality=90
    for key,v,t,scale,w,h in [
        ("parry",(2.35,-7.1,3.05),(0,-.10,.98),4.83,1440,880),
        ("spear",(2.4,-6.3,3.13),(0,0,1.32),3.18,1100,1130),
    ]:
        for o in spear_objects:o.hide_render=key!="spear"
        for group in models:
            for o in group:o.hide_render=key!="parry"
        c.location=v;aim(c,t);d.ortho_scale=scale
        scene.render.resolution_x=w;scene.render.resolution_y=h
        scene.render.filepath=str(out/f"nov24-west-melee-{key}.jpg");bpy.ops.render.render(write_still=True)
