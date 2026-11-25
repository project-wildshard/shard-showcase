"""Annotate sampled stock board paths on the exact assembled park. No markers are exported."""
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

mint = material("Stock board path | no jump input", (.035, .78, .68))
gold = material("Stock board path | jump input", (1, .44, .089))

def mark(row, material, radius):
    x, y, z = row["feet"]
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(x, -z, y))
    bpy.context.object.data.materials.append(material)

for run in runs:
    if not run["fit"]:
        continue
    for f in run["frames"][::5]:
        if f["feet"][0] > -160 or f["feet"][0] < -200:
            continue
        if run["jumpTick"] is None:
            mark(f, mint, .095)
        elif f["air"]:
            mark(f, gold, .109)

scene.render.engine = "CYCLES"
scene.cycles.samples = 28
scene.cycles.use_denoising = False
scene.cycles.adaptive_threshold = .047
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 93
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
    scene.render.filepath = str(out / (name + ".jpg"))
    bpy.ops.render.render(write_still=True)


render("nov25-w5a-receiver-overview",(-190,-179,22),(-181,-153,2.20),31,1320,850)
render("nov25-w5a-receiver-sightline",(-166,-167,7.3),(-182,-154,3.1),39,1170,800)
