"""Front and rear plates from the actual W1a Surveyor GLB and imported idle."""
import math
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out=output_directory()
clear_scene()
s=bpy.context.scene;s.render.fps=24
def put(x,yaw):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/"surveyor-decoded-for-blender.glb"))
    new=set(s.objects)-before
    arm,=[o for o in new if o.type=="ARMATURE"]
    assert len(arm.data.bones)==21 and arm.animation_data
    bound,=[o for o in new if o.type=="MESH" and o.vertex_groups]
    assert len(bound.data.materials)==1 and len(bound.vertex_groups)==21
    pose=Matrix.Translation((x,0,0))@Matrix.Rotation(math.radians(yaw),4,"Z")
    for ob in new:
        if ob.parent not in new:ob.matrix_world=pose@ob.matrix_world
put(-.84,-15)
put(.84,165)
s.frame_set(19)
def material(n,c,e=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Roughness"].default_value=.71;p.inputs["Emission Strength"].default_value=e
    p.inputs["Emission Color"].default_value=(*c,1)
    return m
stone=material("Slate display block",(.053,.082,.098))
ground=material("Deep stone backdrop",(.042,.065,.075))
ink=material("Warm proof labels",(.85,.80,.68),.22)
mint=material("Cool proof markings",(.20,.63,.57),.35)
def label(word,size,p,ma):
    c=bpy.data.curves.new(word,"FONT");c.body=word;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(word,c);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=math.radians(65);c.materials.append(ma)
for x,name in [(-.84,"01   /   FRONT"),(.84,"02   /   REAR")]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,0,-.051))
    ob=bpy.context.object;ob.dimensions=(1.38,1.24,.10)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(stone)
    b=ob.modifiers.new("Fine rail","BEVEL");b.width=.025;b.segments=2
    label(name,.091,(x,-.598,.026),ink)
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-.109))
bpy.context.object.data.materials.append(ground)
label("WEST PLAZA  /  SURVEYOR",.178,(0,.46,2.12),ink)
label("WSC-ACTOR-017     ·     RIGGED TOWN NPC STUDY",.081,(0,.45,1.961),mint)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,w,r,c in [((-2.8,-4.4,4.2),660,3.5,(1,.84,.64)),((3.8,-2,3),490,4,(.70,.87,1)),((0,4,4),720,3,(.72,1,.91))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=w;o.data.size=r;o.data.color=c;aim(o,(0,0,.9))
s.world.color=(.19,.21,.22)
bpy.ops.object.camera_add(location=(0,-6.8,3.1))
s.camera=bpy.context.object;aim(s.camera,(0,0,.95));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=3.55
s.render.engine='CYCLES';s.cycles.samples=45;s.cycles.use_denoising=False
s.render.resolution_x=1320;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-w1a-surveyor-reimport.jpg")
bpy.ops.render.render(write_still=True)
