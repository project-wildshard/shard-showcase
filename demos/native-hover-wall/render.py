"""Render measured releases against the exact launch-wall collider. Dots are review overlays."""
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

mint = material("Early neutral release", (.035, .78, .68))
gold = material("Late neutral release", (1, .44, .089))
blue = material("Left rollout turn", (.095, .32, 1))

def mark(row, material, radius, offset_z=0, lift=0):
    x, y, z = row["feet"]
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=(x, -z+offset_z, y+.08+lift))
    bpy.context.object.data.materials.append(material)
    return bpy.context.object

def trace(run, color, sideways=0, lift=0):
    marks = []
    start = run["frames"][run["release"] - 1]
    stop = run.get("contactTick", len(run["frames"])-1)
    for f in run["frames"][run["release"]:stop:5]:
        if marks and (marks[-1].location - Vector((f["feet"][0], -f["feet"][2]+sideways, f["feet"][1]+.08+lift))).length < .27:
            continue
        marks.append(mark(f, color, .108, sideways, lift))
    marks += [mark(start, color, .24, sideways,lift),mark(run["frames"][stop], color, .27, sideways,lift)]
    return marks

early=next(r for r in runs if r["installed"] and r["releaseX"]==-171)
late=next(r for r in runs if r["installed"] and r["releaseX"]==-195)
control=next(r for r in runs if not r["installed"] and r["releaseX"]==-195)
neutral=trace(early,mint,.28)
installed=trace(late,gold,-.20)
comparison=trace(control,blue,.45,5.0)
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


for ob in comparison: ob.hide_render=True
render("nov25-w5a-wall-release",(-201,-174,14),(-199,-154,2.5),29,1300,880)
for ob in neutral: ob.hide_render=True
for ob in comparison: ob.hide_render=False
render("nov25-w5a-wall-control",(-224,-181,19),(-211,-154,2.8),32,1370,900)
