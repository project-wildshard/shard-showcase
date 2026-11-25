"""Render sample.mjs's actual deck and player positions on the exact existing C2 scene."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
trace, out = map(lambda p: Path(p).resolve(),sys.argv[sys.argv.index("--")+1:])
snap = json.loads(trace.read_text())
out.mkdir(parents=True,exist_ok=True)
for ob in tuple(bpy.context.scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
s = bpy.context.scene
files = ROOT / "public/assets/wildshard-art"
scene = files / "wsc-scene-007-c2-pit.glb"
layout = json.loads((ROOT/"project/layouts/wsc-scene-007-c2-pit.json").read_text())
for part,h in layout["donors_sha256"].items():
    assert hashlib.sha256((files/f"wsc-kit-009-reveal-lift-{part}.glb").read_bytes()).hexdigest()==h
assert snap["layout"]==layout["donors_sha256"]
bpy.ops.import_scene.gltf(filepath=str(scene))
deck,=[o for o in s.objects if o.type=="MESH" and o.name.startswith("C2_Lift_Moving_Deck")]
frame,=[o for o in s.objects if o.type=="MESH" and o.name.startswith("C2_Lift_Fixed_Frame")]
x0,y0,z0=layout["origin_world_x_y_z"]
assert tuple(snap["worldOrigin"])==(55,0,229)


def bounds(o):
    coords=[o.matrix_world@v.co for v in o.data.vertices]
    return [min(v.z for v in coords),max(v.z for v in coords)]


bpy.context.view_layer.update()
assert abs(bounds(deck)[1]-4)<.0001 and abs(bounds(frame)[1])<.0001
old=deck.location.z


def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()


def lamp(name,kind,at,target,energy,r,color):
    d=bpy.data.lights.new(name,kind)
    d.energy=energy
    d.color=color
    if kind=="SUN": d.angle=r
    else: d.shape,d.size="DISK",r
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o);o.location=at;aim(o,target)


s.world=bpy.data.worlds.new("C2 deep slate daylight")
s.world.use_nodes=True
bg=s.world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.22,.34,.49,1)
bg.inputs[1].default_value=.57
lamp("Warm court key","SUN",(-28,14,25),(0,-14,0),2.45,.09,(1,.80,.59))
lamp("Cold shaft rim","AREA",(4,-19,10),(0,-17,1),3600,6,(.48,.69,1))
lamp("Banner bounce","AREA",(-3,-10,6),(0,-19,9),1600,5,(1,.63,.34))
lamp("Floor fill","AREA",(-5,-5,14),(1,-17,0),3800,10,(.70,.86,1))

markmat=bpy.data.materials.new("Trace marker: not an actor")
markmat.use_nodes=True
p=markmat.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value=(1,.35,.047,1)
p.inputs["Emission Color"].default_value=(1,.28,.034,1)
p.inputs["Emission Strength"].default_value=2.4
p.inputs["Roughness"].default_value=.40
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.135)
flare=bpy.context.object;flare.name="Sampled feet visual marker";flare.data.materials.append(markmat)
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=6,major_radius=.34,minor_radius=.017)
ring=bpy.context.object;ring.name="Feet ground projection marker";ring.data.materials.append(markmat)

bpy.ops.object.camera_add(location=(10.5,-2.6,7.4))
cam=bpy.context.object
s.camera=cam
aim(cam,(0,-17.3,3.9));cam.data.lens=31
s.render.engine="CYCLES"
s.cycles.samples=42
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.069
s.cycles.use_denoising=False
s.view_settings.view_transform="AgX"
s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x,s.render.resolution_y=1440,900
s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG"
s.render.image_settings.quality=91
for name,key in (("flush","rest"),("raised","end")):
    shot=snap[key]
    deck.location.z=old+shot["y"]-4
    x,y,z=shot["feet"]
    ring.location=(x-x0,z0-z,max(shot["y"]+.027,y+.025)-y0)
    flare.location=(ring.location.x,ring.location.y,ring.location.z+.11)
    bpy.context.view_layer.update()
    assert abs(bounds(deck)[1]-shot["y"])<.0001 and abs(bounds(frame)[1])<.0001
    s.render.filepath=str(out/f"nov25-e11c-lift-{name}.jpg")
    bpy.ops.render.render(write_still=True)
