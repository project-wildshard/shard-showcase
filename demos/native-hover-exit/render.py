"""Plot measured stock hover exit paths in the exact park. Dots are review overlays."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
runs = json.loads(Path(args[0]).read_text())["results"]
out = Path(args[1])
out.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene

def material(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    q = m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value = (*color, 1)
    q.inputs["Emission Color"].default_value = (*color, 1)
    q.inputs["Emission Strength"].default_value = .65
    q.inputs["Roughness"].default_value = .54
    return m

mint = material("Counter-input", (.035, .78, .68))
gold = material("Late neutral release", (1, .44, .089))
blue = material("Left rollout turn", (.12, .36, 1))
coral = material("Early shelf drop", (1, .17, .08))

def mark(row, material, radius, offset_z=0):
    x, y, z = row["feet"]
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=(x, -z+offset_z, y+.08))
    bpy.context.object.data.materials.append(material)
    return bpy.context.object

def trace(run, color, sideways=0):
    marks = []
    for f in run["frames"][run["start"]["tick"]+1::5]:
        marks.append(mark(f, color, .108, sideways))
    marks += [mark(run["start"], color, .24, sideways),mark(run["last"], color, .27, sideways)]
    return marks

by_key = {r["key"]:r for r in runs}
groups = [
    trace(by_key["counter-input"],mint,.19) + trace(by_key["late-release"],gold,-.20),
    trace(by_key["rollout-hard-left"],blue) + trace(by_key["shelf-right"],coral),
]
scene.render.engine = "CYCLES"
scene.cycles.samples = 28
scene.cycles.use_denoising = False
scene.cycles.adaptive_threshold = .047
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "WEBP"
scene.render.image_settings.quality = 88
scene.view_settings.view_transform = "AgX"
scene.world = bpy.data.worlds.new("Warm overcast park study")
scene.world.use_nodes = True
world = scene.world.node_tree.nodes["Background"]
world.inputs[0].default_value = (.48, .57, .69, 1)
world.inputs[1].default_value = .55
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.rotation_euler = Vector((.43, -.40, -.81)).to_track_quat("-Z", "Y").to_euler()
sun.data.energy = 2.5
sun.data.angle = .18
sun.data.color = (1, .87, .73)
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera

def render(name, eye, target, lens, width, height):
    camera.location = eye
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.filepath = str(out / (name + ".webp"))
    bpy.ops.render.render(write_still=True)


for ob in groups[1]: ob.hide_render = True
render("nov25-w5a-exit-brake",(-202,-164,11),(-199,-154,1.6),35,1300,880)
for ob in groups[0]: ob.hide_render = True
for ob in groups[1]: ob.hide_render = False
render("nov25-w5a-exit-steer",(-190,-183,25),(-193,-154,2.1),31,1370,900)
