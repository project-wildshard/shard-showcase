"""Matched West Plaza relight using the pinned W01 props and the shared lantern."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
root=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
s=bpy.context.scene
clear_scene()
pins={
 "post":("wsc-prop-004-lantern-post.glb","fbaa76a0606141fcac37d45553b26072025586ac0f53be41d57daaf3beeb405b"),
 "lantern":("wall-lantern.glb","bdbdce040eee6e60693e110cdcdb25e1abc93d80ed4f79f7d2e72fc5490ecc09"),
 "board":("quest-board.glb","84b82ec701da4529f5d9403e137d10a28ea370b87ada4ba28f837dc0ba1472aa"),
 "house":("town-gate-merchant-house.glb","266fc52858b80847add0627c536c1421d1305e3092c846625937d1d6d80017fe"),
 "paving":("wsc-arch-005-plaza-paving-kit.glb","85b9ddb3f5c13a5168325fd4b6c34ccf0fde319a5c3511d67232ce6d762f97ea"),
 "stall":("market-awning-stall.glb","b240fd8056db68d9b1caeaefc61459de4171f1345782726b0da40d0a1c614f04")
}
cached={}
def donor(key):
    if key in cached:return cached[key]
    name,sha=pins[key];path=root/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
    got=sorted(set(s.objects)-old,key=lambda o:o.name)
    raw=[(o.name,o.data,o.matrix_world.copy()) for o in got if o.type=="MESH"]
    pts=[w@v.co for _,m,w in raw for v in m.vertices]
    lo,hi=[Vector([fn(v[i] for v in pts) for i in range(3)]) for fn in (min,max)]
    for o in got:bpy.data.objects.remove(o,do_unlink=True)
    cached[key]=(raw,Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)))
    return cached[key]

def T(p,yaw=0,scale=1):
    return Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(yaw),4,"Z")@Matrix.Scale(scale,4)

def prop(key,m,recenter=True):
    meshes,p=donor(key)
    if recenter:m=m@Matrix.Translation(-p)
    for n,g,w in meshes:
        o=bpy.data.objects.new(key+" | "+n,g);s.collection.objects.link(o);o.matrix_world=m@w

# W01 lighting stage reuses the same shops, board, paving positions and
# board scale from quest_trio_reimport.py. A wider camera includes the lamps.
prop("board",T((.54,.33,0),0,.81))
prop("house",T((.47,6.05,0),0,.86))
prop("stall",T((-3.65,1.64,0),-11,.66))
for x in (-4.80,0,4.80):
    for y in (-3.56,1.24,6.04):prop("paving",T((x,y,-.154)))
material=bpy.data.materials.new("Underlay");material.diffuse_color=(.32,.235,.141,1)
bpy.ops.mesh.primitive_plane_add(size=140,location=(0,0,-.158))
bpy.context.object.data.materials.append(material)

post_poses=[((-2.95,-.71,0),20),((3.05,-.21,0),-16),((3.45,3.55,0),-8)]
mount=(0,-.182,2.270)
glass=Vector((0,-.732,2.661))
below_forward=Vector((0,-.077,-.212))
emit=[]
for p,yaw in post_poses:
    transform=T(p,yaw)
    prop("post",transform,False)
    prop("lantern",transform@T(mount),False)
    emit.append((transform@glass,transform@(glass+below_forward)))

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def light(name,kind,p,q,power,color,radius):
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
    if kind=="AREA":d.shape="DISK";d.size=radius
    if kind=="POINT":d.shadow_soft_size=radius
    if kind=="SUN":d.angle=radius
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=p
    if q is not None:aim(o,q)
    return o
def world(label,sky_color,strength):
    w=bpy.data.worlds.new(label);w.use_nodes=True
    b=w.node_tree.nodes["Background"];b.inputs[0].default_value=(*sky_color,1);b.inputs[1].default_value=strength
    s.world=w
def day():
    world("West Plaza day",(.36,.59,.89),.52)
    return [light("Sun","SUN",(-6,-9,11),(0,2,0),2.25,(1,.79,.57),.17),
      light("Sky bounce","AREA",(5,-4,7),(0,1,.7),390,(.67,.83,1),7)]
def night():
    world("West Plaza blue hour",(.046,.105,.247),.40)
    out=[light("Moon rim","SUN",(-3,6,8),(0,0,0),.66,(.35,.55,1),.15),
         light("Blue hour foreground","AREA",(4,-7,7),(1,1,0),635,(.35,.54,1),8),
         light("Warm shop bounce","AREA",(.3,3.35,2.6),(.4,2,1.10),96,(1,.53,.29),2.6)]
    for i,(_,p) in enumerate(emit):
        out.append(light(f"Lantern {i+1} separate emitter","POINT",p,None,(112,118,90)[i],(1,.56,.25),.18))
    return out

cam=bpy.data.cameras.new("Fixed 1.7 m West Plaza camera")
s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
s.camera.location=(-.3,-8.8,1.7)
aim(s.camera,(.20,1.6,1.91));cam.lens=35
s.render.engine="CYCLES";s.cycles.samples=64;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.view_settings.exposure=0
s.render.resolution_x=1540;s.render.resolution_y=1020;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=93
bpy.context.view_layer.update()
coords=[world_to_camera_view(s,s.camera,g) for g,_ in emit]
assert all(.02<x.x<.98 and .02<x.y<.98 and x.z>0 for x in coords),coords
def stage_signature():
    bpy.context.view_layer.update()
    return tuple((o.name,tuple(v for row in o.matrix_world for v in row)) for o in s.objects if o.type in ("MESH","CAMERA"))
fixed=stage_signature()
for mode,build in (("day",day),("night",night)):
    lamps=build()
    assert fixed==stage_signature()
    s.render.filepath=str(out/f"nov23-west-plaza-{mode}.jpg")
    bpy.ops.render.render(write_still=True)
    for o in lamps:bpy.data.objects.remove(o,do_unlink=True)
(out/"validation.json").write_text(json.dumps({
 "donor_sha256":pins,"camera":[-.3,-8.8,1.7],"lens_mm":35,"same_scene_transforms":True,
 "measured_glass_centres":[list(g) for g,p in emit],
 "preview_light_centres":[list(p) for g,p in emit],"renderer_exposure_both":0,"runtime":False
},indent=2)+"\n")
