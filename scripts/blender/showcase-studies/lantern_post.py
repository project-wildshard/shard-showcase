"""WSC-PROP-004 compatible street post: reuse the exact tracked wall lantern."""
import hashlib, math, os, sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT=output_directory()
DONOR=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art/wall-lantern.glb"
NAME="wsc-prop-004-lantern-post.glb"
assert hashlib.sha256(DONOR.read_bytes()).hexdigest()=="bdbdce040eee6e60693e110cdcdb25e1abc93d80ed4f79f7d2e72fc5490ecc09"
clear_scene()

def mat(n, rgb, metal=.55, rough=.61):
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*rgb,1)
    b.inputs["Metallic"].default_value=metal;b.inputs["Roughness"].default_value=rough
    return m

steel=mat("Forged slate iron",(.064,.083,.091))
bead=mat("Worn edges",(.15,.174,.173),.62,.54)
base=mat("Shaped basalt footing",(.16,.16,.147),.08,.87)
brass=mat("Burnished plate corners",(.25,.141,.049),.54,.46)

def box(name,p,ds,m,w=.018):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=ds
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if w:
        b=o.modifiers.new("Cast bevel","BEVEL");b.width=w;b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    o.data.materials.append(m)
    return o

def frustum(name,z,h,r1,r2,m):
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r1,radius2=r2,depth=h,
                                  location=(0,0,z+h*.5),rotation=(0,0,math.pi/8))
    o=bpy.context.object;o.name=name;o.data.materials.append(m)
    return o

parts=[
    box("Stone footing",(0,0,.105),(.60,.56,.21),base,.045),
    box("Flanged base",(0,0,.232),(.42,.41,.092),steel,.022),
    frustum("Pedestal housing",.245,.66,.215,.143,steel),
    frustum("Cast heel band",.3,.085,.223,.215,bead),
    frustum("Waist collar",.814,.12,.155,.153,bead),
    frustum("Tapered shaft",.922,2.14,.127,.100,steel),
    frustum("Shaft neck",2.21,.075,.124,.124,bead),
    frustum("Capital",3.19,.13,.155,.180,steel),
    frustum("Capital bead",3.304,.084,.185,.161,bead),
    frustum("Cap dome",3.377,.099,.162,.042,steel),
]
# Flat mounting face at Y=-.182 fits the donor's rectangular plaque.
parts.append(box("Planar plaque interface",(0,-.091,2.744),(.348,.182,1.046),steel,.014))
for z in (2.245,3.22):
    parts.append(box("Brass clasp",(0,-.093,z),(.353,.172,.055),brass,.011))
for x in (-.146,.146):
    for y in (-.14,.14):
        parts.append(box("Flange fixing",(x,y,.292),(.054,.054,.038),bead,.009))
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
p=bpy.context.object;p.name="Street_Lantern_Post"
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.export_scene.gltf(filepath=str(OUT/NAME),export_format="GLB",use_selection=True,
                        export_animations=False,export_texcoords=False)

clear_scene()
bpy.ops.import_scene.gltf(filepath=str(OUT/NAME))
post,=[o for o in bpy.context.scene.objects if o.type=="MESH"]
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(DONOR))
lantern,=[o for o in bpy.context.scene.objects if o not in before and o.type=="MESH"]
lantern.location=(0,-.182,2.27)
bpy.context.view_layer.update()
pv=[post.matrix_world@v.co for v in post.data.vertices]
lv=[lantern.matrix_world@v.co for v in lantern.data.vertices]
assert abs(min(v.z for v in pv))<.00001 and 3.46<max(v.z for v in pv)<3.49
assert abs(max(v.y for v in lv)+.182)<.00001
assert abs(min(v.z for v in lv)-2.27)<.00001 and abs(max(v.z for v in lv)-3.24)<.00001
# Beyond the common mounting plane the shell is entirely behind the donor.
for f in post.data.polygons:
    vs=[pv[i] for i in f.vertices]
    if max(v.z for v in vs)>=2.27 and min(v.z for v in vs)<=3.24:
        assert min(v.y for v in vs)>=-.18201
post.data.calc_loop_triangles()
print(f"{NAME}: {(OUT/NAME).stat().st_size} B, {len(post.data.loop_triangles)} triangles; verified exact donor fits mounting plane")
if os.getenv("WSC_LANTERN_POST_RENDER") != "1":
    raise SystemExit(0)

box("Studio slate",(0,0,-.09),(200,200,.18),mat("Slate paving",(.048,.068,.074),.05,.93),0)
s=bpy.context.scene;s.world.color=(.14,.16,.18)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,power,size,c in [((-3,-4,5),500,3,(1,.87,.73)),((3,-1,4),245,3,(.64,.81,1)),((0,4,5),515,3,(.79,.88,1))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=c;aim(o,(0,0,1.9))
bpy.ops.object.camera_add(location=(3.7,-6.1,3.9))
s.camera=bpy.context.object;aim(s.camera,(0,-.22,1.73));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=4.04
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1000;s.render.resolution_y=1230;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
s.render.filepath=str(OUT/"w01-shared-lantern-on-post.jpg")
bpy.ops.render.render(write_still=True)
