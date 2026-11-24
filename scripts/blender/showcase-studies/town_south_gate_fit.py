"""Fit two existing W0b signs on the rebuilt Park and Range lintels."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("town", type=Path, help="whole-town-editable.blend from west-town/build.py")
parser.add_argument("output", type=Path)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
repo = Path(__file__).resolve().parents[3]
kit = repo / "public/assets/wildshard-art/w0b-town-gate-nameplates.glb"
digest = hashlib.sha256(kit.read_bytes()).hexdigest()
assert digest == "2daf80f5fa5f5bcdf22aeec26d2113a72d36250c864064fdb403d9a50718e480"

bpy.ops.wm.open_mainfile(filepath=str(args.town.resolve()))
scene = bpy.context.scene
wall = scene.objects["TOWN | east south walls and three gates"]
existing = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(kit))
nodes = {o.name: o for o in set(scene.objects) - existing}
gates = {"Park": -95., "Range": -36.}
for name, node in [(n, o) for n,o in nodes.items() if o.parent is None]:
    if name not in {f"{k} Gate" for k in gates}:
        for child in tuple(node.children):
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(node, do_unlink=True)

mount = bpy.data.materials.new("Blackened steel · interface proof")
mount.use_nodes = True
shader = mount.node_tree.nodes["Principled BSDF"]
shader.inputs["Base Color"].default_value = (.040, .032, .023, 1)
shader.inputs["Metallic"].default_value = .7
shader.inputs["Roughness"].default_value = .45

front, z_mid = -60.875, 6.62
rear = front - .030
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()


def vertices(obj):
    obj = obj.evaluated_get(dg)
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def interval(vs, i):
    return min(v[i] for v in vs), max(v[i] for v in vs)


def hit_depth(x, z):
    obj = wall.evaluated_get(dg)
    inv = obj.matrix_world.inverted()
    origin = inv @ Vector((x, front - .5, z))
    direction = inv.to_3x3() @ Vector((0, 1, 0))
    ok, at, normal, _ = obj.ray_cast(origin, direction, distance=.65)
    assert ok and (obj.matrix_world.to_3x3() @ normal).y < -.999
    return (obj.matrix_world @ at).y


beams = vertices(wall)
report = {"sign_kit_sha256": digest, "placements": {}, "engine_placement": False}
for gate, x in gates.items():
    plaque = nodes[gate + " Gate"]
    plaque.location = (x, rear, z_mid)
    bpy.context.view_layer.update()
    frame = next(o for o in plaque.children if o.name.startswith("Frame"))
    bounds = [interval(vertices(frame), i) for i in range(3)]
    assert abs(bounds[1][1] - rear) < .0001
    beam = [v for v in beams
            if abs(v.y-front) < .0001 and abs(v.z-z_mid) < .376 and abs(v.x-x) < 6.101]
    assert len(beam) == 4, (gate, beam)
    xs, zs = interval(beam, 0), interval(beam, 2)
    margins = [bounds[0][0]-xs[0], xs[1]-bounds[0][1],
               bounds[2][0]-zs[0], zs[1]-bounds[2][1]]
    assert all(abs(a-b) < .0001 for a,b in zip(margins,(4.44,4.44,.06,.06)))
    old = scene.objects[f"TOWN | {gate.upper()} GATE"]
    old_vs = vertices(old)
    old_x, old_y, old_z = [interval(old_vs, i) for i in range(3)]
    letter_gap = old_y[0] - rear
    assert letter_gap >= .006
    old.hide_render = True

    centers = []
    for dx in (-1.485, 1.485):
        for dz in (-.163, .163):
            # Stud seat checked at center and full metal pad footprint.
            ds = [hit_depth(x+dx+ox, z_mid+dz+oz)
                  for ox, oz in [(0,0),(.04,0),(-.04,0),(0,.04),(0,-.04)]]
            assert max(abs(v-front) for v in ds) < .0001
            centers.append((x+dx, ds[0], z_mid+dz))
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.045, depth=.039,
                                                location=(x+dx,rear+.0175,z_mid+dz),
                                                rotation=(math.pi/2,0,0))
            pad = bpy.context.object
            pad.name = f"Fit study only · {gate} seat {len(centers)}"
            pad.data.materials.append(mount)
    report["placements"][gate] = {
        "plaque_rear_center_blender_m": [x,rear,z_mid],
        "face_margin_left_right_bottom_top_m": [round(v,4) for v in margins],
        "legacy_mesh_bounds_blender_m": [old_x,old_y,old_z],
        "legacy_clearance_m": round(letter_gap,4),
        "legacy_mesh_hidden_in_render_only": old.name,
        "old_letters_extend_outside_rectangular_plaque": (
            old_x[0] < bounds[0][0] or old_x[1] > bounds[0][1] or
            old_z[0] < bounds[2][0] or old_z[1] > bounds[2][1]),
        "tested_pad_centers_blender_m": [[round(v,4) for v in p] for p in centers],
    }

assert abs(gates["Range"] - gates["Park"] - 59) < .0001
world = bpy.data.worlds.new("Matched southern gate daylight")
world.use_nodes = True
background = world.node_tree.nodes["Background"]
background.inputs[0].default_value = (.50,.64,.86,1)
background.inputs[1].default_value = .43
scene.world = world
for obj in scene.objects:
    if obj.type == "LIGHT":
        obj.hide_render = True
sun = bpy.data.lights.new("South-west sun", "SUN")
sun.energy = 2.6
sun.angle = math.radians(6)
sun.color = (1,.81,.62)
light = bpy.data.objects.new(sun.name, sun)
scene.collection.objects.link(light)
light.rotation_euler = Vector((.62,.47,-.78)).to_track_quat("-Z","Y").to_euler()
cam = bpy.data.objects.new("Matched south approach", bpy.data.cameras.new("Matched south approach"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 36
cam.data.clip_end = 350
scene.render.engine = "CYCLES"
scene.cycles.samples = 44
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = .08
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 90
scene.render.resolution_x, scene.render.resolution_y = 1280, 880
scene.render.resolution_percentage = 100
for gate,x in gates.items():
    cam.location = (x+2.35,-76.8,1.70)
    cam.rotation_euler = (Vector((x,-60.9,4.2))-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.view_layer.update()
    low = world_to_camera_view(scene,cam,Vector((x,rear-.17,z_mid-.1495)))
    high = world_to_camera_view(scene,cam,Vector((x,rear-.17,z_mid+.1495)))
    px = abs(high.y-low.y)*scene.render.resolution_y
    assert .1 < low.y < high.y < .95 and px > 20
    report["placements"][gate]["camera_letter_height_px"] = round(px,1)
    scene.render.filepath = str(out/f"nov24-{gate.lower()}-gate-fit.jpg")
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)

(out/"south-gate-fit.json").write_text(json.dumps(report,indent=2)+"\n")
