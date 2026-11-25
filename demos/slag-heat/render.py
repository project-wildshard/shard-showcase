"""Matched Blender visuals driven by the checked Three heat stops. Not browser screenshots."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector

receipt,out=[Path(x) for x in sys.argv[sys.argv.index("--")+1:]]
out.mkdir(parents=True,exist_ok=True)
art=Path(__file__).resolve().parents[2]/"public/assets/wildshard-art"
heat={t:v for t,v in json.loads(receipt.read_text())["samples"]}
s=bpy.context.scene
for o in tuple(s.objects):bpy.data.objects.remove(o,do_unlink=True)
def load(filename,transform):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(art/filename))
    obs=sorted(set(s.objects)-before,key=lambda x:x.name)
    for o in obs:
        if o.parent not in obs:o.matrix_world=transform@o.matrix_world
    return obs
load('e4-cover-bay-shell.glb',Matrix.Identity(4))
load('wsc-prop-057-foundry-furnace.glb',Matrix.Translation((.52,.56,0)))
patch,=load('e4-ground-slag-decal.glb',Matrix.Translation((0,-1.2,.003))@Matrix.Rotation(math.pi,4,'Z'))
mats=[]
for m in patch.data.materials:
    n=m.node_tree.nodes
    p=n.get("Principled BSDF")
    color=tuple(p.inputs["Base Color"].default_value)
    strength=p.inputs["Emission Strength"].default_value
    lp=n.new("ShaderNodeLightPath")
    mul=n.new("ShaderNodeMath")
    mul.operation="MULTIPLY"
    m.node_tree.links.new(lp.outputs["Is Camera Ray"],mul.inputs[0])
    m.node_tree.links.new(mul.outputs[0],p.inputs["Emission Strength"])
    mats.append((p,color,strength,mul))
assert sum(strength>0 for _,_,strength,_ in mats)==3

def pose(t):
    h=heat[t]
    patch.hide_render=h is None
    if h is None:return
    for p,c,e,mul in mats:
        scale=.56-(.56-.11)*(1-h) if e>0 else .56
        p.inputs["Base Color"].default_value=(*[v*scale for v in c[:3]],1)
        mul.inputs[1].default_value=e*h*.58

def lamp(n,power,at,target,col,size):
    d=bpy.data.lights.new(n,"AREA");d.energy=power;d.color=col;d.size=size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=at
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

lamp("Review moon wash",235,(-2,-4,6),(0,-1,0),(.69,.78,1),6)
lamp("Review warm bounce",46,(3,1,3),(0,0,0),(1,.65,.38),4)
s.world=bpy.data.worlds.new("Foundry dusk");s.world.use_nodes=True
p=s.world.node_tree.nodes["Background"];p.inputs[0].default_value=(.13,.18,.26,1);p.inputs[1].default_value=.35
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
s.render.engine="CYCLES";s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.045
s.render.resolution_percentage=100;s.render.use_compositing=False
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=94
s.view_settings.view_transform="AgX"
def shot(name,t,eye,target,vert,w,h):
    pose(t);cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.sensor_fit="VERTICAL";cam.data.sensor_height=36;cam.data.lens=18/math.tan(math.radians(vert/2))
    s.render.resolution_x=w;s.render.resolution_y=h
    s.render.filepath=str(out/(name+".jpg"));bpy.ops.render.render(write_still=True)

for name,t in (("impact",0),("mid",3.8),("cool",5.9),("gone",6)):
    shot("detail-"+name,t,(-1.28,-3.05,1.64),(0,-1.2,.14),44,1120,770)
for name,t in (("impact",0),("cool",5.9)):
    shot("portrait-"+name,t,(.20,-6.2,1.70),(0,-1.2,.47),48,804,1748)
