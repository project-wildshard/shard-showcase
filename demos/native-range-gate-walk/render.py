"""Plot the native player trace over the unchanged compiled pedestrian scenery."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index("--")+1:]
source=Path(args[0]);out=Path(args[1])
record=json.loads(source.read_text())
scene=bpy.context.scene
out.mkdir(parents=True,exist_ok=True)
def material(name,col):
    m=bpy.data.materials.new(name);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*col,1)
    q.inputs['Emission Color'].default_value=(*col,1)
    q.inputs['Emission Strength'].default_value=.35
    q.inputs['Roughness'].default_value=.55
    return m
mint=material("Measured walking samples",(.044,.67,.64))
orange=material("Measured turns and arrival",(.94,.348,.049))

def point(p):return (p[0],-p[2],p[1])
def mark(p,r,mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=p)
    o=bpy.context.object;o.data.materials.append(mat);return o
run=record["samples"][1]
cyan_marks=[]
amber_marks=[]
for frame in run["frames"][4::4]:
    x,y,z=point(frame["feet"])
    cyan_marks.append(mark((x,y,z+.15),.071,mint))
for k in run["waypoints"]:
    x,y,z=point(k["feet"])
    amber_marks.append(mark((x,y,z+.24),.175,orange))
# Only the annotated preview adds guide dots and lights.
scene.render.engine="CYCLES";scene.cycles.samples=28;scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.047
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=93
scene.view_settings.view_transform="AgX"
scene.world=bpy.data.worlds.new("Late afternoon gate review");scene.world.use_nodes=True
p=scene.world.node_tree.nodes["Background"]
p.inputs[0].default_value=(.43,.52,.63,1);p.inputs[1].default_value=.48
bpy.ops.object.light_add(type="SUN",location=(-40,-56,20))
o=bpy.context.object
o.rotation_euler=Vector((.55,-.38,-.76)).to_track_quat('-Z','Y').to_euler()
o.data.energy=2.55;o.data.angle=.14;o.data.color=(1,.88,.72)
bpy.ops.object.camera_add()
camera=bpy.context.object;scene.camera=camera
def render(name,eye,target,lens,w,h):
    camera.location=eye;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+".jpg"));bpy.ops.render.render(write_still=True)
render("nov25-w12-range-gate-eye",(-35.25,-70.5,1.75),(-36,-59.5,3.50),26,1000,790)
for o in cyan_marks: o.scale*=2.4
for o in amber_marks: o.scale*=2
render("nov25-w12-range-walk-overlook",(-9,-86,58),(-33,-87,0),25,1360,850)
