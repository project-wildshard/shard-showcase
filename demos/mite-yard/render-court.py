"""Blender proof of the standalone placement, not a runtime screenshot.

Usage: blender -b -t 8 -P demos/mite-yard/render-court.py -- /tmp/court.webp
Run from the repo root. Actual yard layout and asset edits live alongside it.
"""
import json
import math
from pathlib import Path
import subprocess
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out = str(Path(args[0]).resolve())
shot = args[1] if len(args) > 1 else "court"
if shot not in ("court", "bite", "overclock", "recover"):
    raise ValueError(f"Unknown proof shot: {shot}")
repo = Path(__file__).resolve().parents[2]
assets = repo / "public/assets/wildshard-art"
source = """
import {DOCK, STACK, CRATES} from './demos/mite-yard/yard-layout.mjs'
import {ARENA,MITE_TIMING,createGame} from './demos/mite-yard/combat.mjs'
const {player,mite}=createGame()
console.log(JSON.stringify({DOCK,STACK,CRATES,ARENA,MITE_TIMING,player,mite}))
"""
cfg = json.loads(subprocess.check_output(
    ["node", "--input-type=module", "-e", source], cwd=repo, text=True,
))
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.fps = 30

def mat(name, color, metal=0, rough=.7):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    return m

def box(name, loc, size, material, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new("Machined edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return ob

def glb(name, x, y, z):
    old = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets / name))
    added = set(bpy.data.objects) - old
    for o in added:
        if o.parent not in added:
            o.location += Vector((x, -z, y))
    return added

def point(ob, pt):
    ob.rotation_euler = (Vector(pt) - ob.location).to_track_quat("-Z", "Y").to_euler()

def light(name, loc, target, energy, size, color):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.size, d.color = energy, size, color
    ob = bpy.data.objects.new(name, d)
    s.collection.objects.link(ob)
    ob.location = loc
    point(ob, target)

concrete = mat("Ash concrete", (.16, .151, .126), rough=.56)
corrugated = mat("Oxidized blue steel", (.025, .052, .062), .59, .48)
stripe = mat("Yard ochre", (.58, .292, .042), .10)
frame = mat("Iron oxide enamel", (.235, .079, .035), .37)
plinth = mat("Dock asphalt", (.048, .062, .065), .16)
wood = mat("Old cargo wood", (.175, .095, .045), 0)
x0, z0 = cfg["DOCK"]["x"], cfg["DOCK"]["z"]
width, depth = cfg["ARENA"]["width"], cfg["ARENA"]["depth"]
box("Court", (0, 0, -.11), (width, depth, .22), concrete)
box("Rear wall", (0, depth/2, 1.32), (width, .26, 2.65), corrugated)
for i in range(50):
    box("Standing seam", (-8.75+i*.36, 10.82, 1.48), (.10,.105,2.3), corrugated)
for i in range(-8, 9, 2):
    box("Corner post", (i, 10.85, 1.51), (.19,.29,3.02), frame)
for x in [-width/2,width/2]:
    box("Side wall", (x,0,1.32), (.27,depth,2.65), corrugated)
for i in range(12):
    for x in [-2.9, 2.9]:
        box("Approach stripe", (x, 8-1.5*i, .004), (.065,.78,.006), stripe, 0)
box("Dock zone", (x0,-z0,.009), (2.75,2.9,.018), plinth)
for y in [-z0-1.35,-z0+1.35]:
    for j in range(9):
        o=box("Dock perimeter", (x0+(j-4)*.272,y,.021), (.245,.14,.009), stripe if not j % 2 else plinth, 0)
        o.rotation_euler.z=-.38
glb("wsc-prop-053-robot-dock.glb", x0,0,z0)
for crate in cfg["CRATES"]:
    glb("haul-crate.glb", *crate)
for x,z,w,d in cfg["ARENA"]["blocks"]:
    if x==cfg["STACK"]["x"] and z==cfg["STACK"]["z"]:
        box("Stack plinth", (x,-z,.032), (w,d,.065), plinth)
        continue
    box("Generic cover", (x,-z,.735), (w,d,1.47), wood)
    for side in [-.4,.4]:
        box("Cover irons", (x+w*side,-z,.776), (.102,d+.055,1.55), corrugated)
mite = cfg["mite"]
added = glb("wsc-actor-001-crate-mite-rig.glb", mite["x"],0,mite["z"])
for ob in added:
    if ob.type == "ARMATURE" and ob.animation_data:
        for track in ob.animation_data.nla_tracks:
            track.mute = True
        name = "telegraph" if shot == "court" else f"attack.{shot if shot != 'recover' else 'bite'}"
        ob.animation_data.action = next(a for a in bpy.data.actions if a.name in (name, f'{name}_{ob.name}'))
tell = round(cfg["MITE_TIMING"].get(shot, cfg["MITE_TIMING"]["bite"])["tell"] * s.render.fps)
s.frame_set(11 if shot == "court" else 31 if shot == "recover" else tell - 1)
if shot != "court":
    for ob in added:
        if ob.type != "MESH":
            continue
        for slot in ob.material_slots:
            m = slot.material
            node = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
            if not node:
                continue
            rgb = node.inputs["Emission Color"].default_value
            if rgb[0] < .25 and rgb[1] > .65 and rgb[2] > .65:
                node.inputs["Emission Strength"].default_value = 3.3 if shot=="overclock" else .38 if shot=="recover" else 2.8
s.world = bpy.data.worlds.new("High cyan overcast")
s.world.use_nodes = True
s.world.node_tree.nodes["Background"].inputs[0].default_value=(.24,.32,.39,1)
s.world.node_tree.nodes["Background"].inputs[1].default_value=.32
light("Late industrial sun", (-4,-2,8),(2,5,0),3400,5,(1,.76,.48))
light("Cold side fill", (7,9,5),(2,4,0),1250,4,(.49,.77,1))
cam = bpy.data.objects.new("Layout proof",bpy.data.cameras.new("Layout proof"))
s.collection.objects.link(cam)
cam.location = (-2.15,-3.8,4.6)
point(cam, (2.24, 4.5, .45))
cam.data.lens = 31
s.camera = cam
s.render.engine = "CYCLES"
s.cycles.samples = 32
s.cycles.use_denoising = False
s.render.resolution_x, s.render.resolution_y = 1250, 800
s.render.resolution_percentage = 100
if shot != "court":
    cam.location = (1.66, -1.50, 1.27)
    point(cam, (.23, 1.87, .34))
    cam.data.lens = 55
    s.render.resolution_x, s.render.resolution_y = 860, 585
s.render.image_settings.file_format = "WEBP"
s.render.image_settings.quality = 90
s.render.filepath = out
bpy.ops.render.render(write_still=True)
