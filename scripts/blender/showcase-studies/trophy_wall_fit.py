"""Fit the existing E8d trophy assets on the 12 archive wall anchors."""
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.geometry import convex_hull_2d

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, output_directory

OUT = output_directory()
ASSETS = HERE.parents[2] / "public/assets/wildshard-art"
clear_scene()
scene = bpy.context.scene

# Exact recovered donors; fail rather than silently recompute for new shapes.
PINS = {
    "west-plaza-empty-mounts": "3e7e28863742ebcdd2f494d97d98574d263d876dac01f03e21a2b0fd5b4a54c7",
    "wsc-module-017-trophy-wall-backing": "bfda7b2120a07b78d154f95698759032c58b604c28749b2c72d90e435335a7cb",
    "wsc-prop-052-big-pallet-trophy": "ea4bd4b80135019f0b0bdd03aab3f21f5870cd3e60515e133d55034e598114fc",
    "cache-trophy-marks": "32a35c5324974601cc8f6639e43f547f515d09bc993c8b25154f2a853544551e",
    "e8d-night-elite-reliefs": "aa67b5fe77d99e3f70e56f25f4805a88eee49e04f75c6cf7880bf0238dd6a9a5",
    "e8d-wardens-plate-relief": "5912935d78baff24bd3d966a5b703bc16a2337b0b57e3ecde95ee716d5dfbfee",
    "e8d-titans-core-relief": "16905f9282e3f16891b58b94ffa90e6b876433a9c92e0e1c1c5bfe1921799e09",
    "e11d-foreman-whistle": "8bce460baaf4fd596c70c4d34c63b3b7a63f520e319fdd0a7b6a49e6eb923d79",
}


def load(stem):
    path = ASSETS / (stem + ".glb")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == PINS[stem], path
    old = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = sorted(set(scene.objects) - old, key=lambda o: o.name)
    for obj in objects:
        obj["source_asset"] = stem + ".glb"
    return objects


def extents(points):
    points = list(points)
    return [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]


def vertex_points(obj):
    return (obj.matrix_world @ v.co for v in obj.data.vertices)


def rounded(vals):
    return [round(v, 6) for v in vals]


def stage(obj, xy, z, scale=1.0):
    # Read the actual local mesh, not a node's gallery display offset.
    (l, r), (b, _), (d, u) = extents(v.co for v in obj.data.vertices)
    x, y = xy
    translation = (x - scale*(l+r)/2, y - scale*b, z - scale*(d+u)/2)
    obj.matrix_world = Matrix.Translation(translation) @ Matrix.Scale(scale, 4)
    bpy.context.view_layer.update()
    return {"blender_translation_m": rounded(translation),
            "gltf_translation_m": rounded((translation[0], translation[2], -translation[1])),
            "scale": scale}


(back,) = load("wsc-module-017-trophy-wall-backing")
back.location = (-42, -18, .099)  # Pass 14 archive placement, unchanged.
frames = load("west-plaza-empty-mounts")
assert len(frames) == 12 and len({o.data for o in frames}) == 1
bpy.context.view_layer.update()
assert all(o.name.endswith(f"{i:02}") for i, o in enumerate(frames, 1))

# Presentation order only. Two unspecified elite art slots and the spare stay blank.
nights = {o.name: o for o in load("e8d-night-elite-reliefs")}
cache_a, cache_b = load("cache-trophy-marks")
(pallet,) = load("wsc-prop-052-big-pallet-trophy")
(warden,) = load("e8d-wardens-plate-relief")
(titan,) = load("e8d-titans-core-relief")
(whistle,) = load("e11d-foreman-whistle")
items = {
    1: ("big-pallet", pallet, .50, None),
    4: ("sir-nibbles", nights["sir-nibbles-earned"], 1, nights["sir-nibbles-locked"]),
    5: ("hot-mess", nights["hot-mess-earned"], 1, nights["hot-mess-locked"]),
    6: ("riveting-rita", nights["riveting-rita-earned"], 1, nights["riveting-rita-locked"]),
    7: ("warden", warden, 1, None),
    8: ("foreman-proposed-whistle", whistle, 2.75, None),
    9: ("titan", titan, 1, None),
    10: ("cache-compass-art", cache_a, 1, None),
    11: ("cache-clasp-art", cache_b, 1, None),
}
shadow = bpy.data.materials.new("Recessed graphite silhouette")
shadow.use_nodes = True
bs = shadow.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value = (.013, .019, .022, 1)
bs.inputs["Roughness"].default_value = .87


def cutout(o, front):
    # Existing authored cuts are preferred; a simple envelope is enough for
    # the other locked preview slots. No geometry or scenes are duplicated.
    points = sorted({(round(v.x, 6), round(v.z, 6)) for v in vertex_points(o)})
    order = convex_hull_2d([Vector(p) for p in points])
    mesh = bpy.data.meshes.new(o.name + " outline")
    mesh.from_pydata([(points[i][0], front, points[i][1]) for i in order],
                     [], [tuple(reversed(range(len(order))))])
    mesh.materials.append(shadow)
    ob = bpy.data.objects.new(mesh.name, mesh)
    scene.collection.objects.link(ob)
    return ob


rows, earned, locked = [], [], []
for i, frame in enumerate(frames, 1):
    x, y, z = frame.location
    (_, _), (rear, nose), (_, _) = extents(vertex_points(frame))
    wall_depths = set()
    for dx in (-.27, 0, .27):
        for dz in (-.27, 0, .27):
            hit, p, _, face = back.ray_cast(back.matrix_world.inverted() @ Vector((x+dx,y+1,z+dz)),
                                           Vector((0,-1,0)), distance=2)
            assert hit and back.data.materials[back.data.polygons[face].material_index].name.startswith("Fir")
            wall_depths.add(round((back.matrix_world @ p).y, 6))
    assert max(wall_depths)-min(wall_depths) <= .0021, (i, wall_depths)
    contact = max(wall_depths)-rear
    assert 0 <= min(wall_depths)-rear <= contact <= .004, (i, contact)
    row = {"frame": frame.name, "anchor_blender_m": rounded(frame.location),
           "support_rays": 9, "backing_contact_m": round(contact, 6)}
    if i in items:
        slug, obj, scale, authored_cut = items[i]
        front = nose+.008
        transform = stage(obj, (x, front), z, scale)
        (l,r),(b,f),(d,u) = extents(vertex_points(obj))
        margin = min(.259 - max(x-l,r-x), .259 - max(z-d,u-z))
        assert margin >= .049 and b-nose >= .00799 and f-b <= .43, (slug, margin, f-b)
        cut = authored_cut or cutout(obj,front)
        if authored_cut:
            # Use the same pivot transform; do not independently center the cut.
            cut.matrix_world = obj.matrix_world.copy()
        earned.append(obj)
        locked.append(cut)
        bpy.context.view_layer.update()
        (kl,kr),(kb,kf),(kd,ku) = extents(vertex_points(cut))
        assert min(.259-max(x-kl,kr-x),.259-max(z-kd,ku-z)) >= .049
        assert kb-nose >= .00799 and kf-kb < .012, slug
        row.update({"display": slug, "source_asset": obj["source_asset"], "source_node": obj.name,
                    "display_transform": transform,
                    "frame_clearance_m": round(margin, 6), "forward_gap_m": round(b-nose, 6),
                    "projection_m": round(f-nose, 6),
                    "locked": "authored relief cut" if authored_cut else "preview envelope"})
    else:
        row["display"] = None
        row["reserve"] = "spare" if i == 12 else "unspecified elite art"
    rows.append(row)


def orient(o, point):
    o.rotation_euler = (Vector(point)-o.location).to_track_quat("-Z","Y").to_euler()


def lamp(name, pos, power, color, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.color, data.size = power, color, size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = pos
    orient(light, (-42,-17.8,1.9))


lamp("Warm afternoon key",(-44.8,-13.4,5.1),650,(1,.78,.58),4.0)
lamp("Cool plaza bounce",(-38.6,-14.5,3.7),380,(.66,.81,1),4.5)
world = bpy.data.worlds.new("Muted plaza sky")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.18,.25,.36,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .50
cam_data = bpy.data.cameras.new("Plaza study, matched eye height")
camera = bpy.data.objects.new(cam_data.name,cam_data)
scene.collection.objects.link(camera)
camera.location = (-42,-9.15,1.74)
orient(camera,(-42,-17.8,1.88))
cam_data.lens = 35
scene.camera = camera
scene.render.resolution_x, scene.render.resolution_y = 1480, 800
scene.render.resolution_percentage = 100
bpy.context.view_layer.update()
for f in frames:
    point = f.location + Vector((0,.46,0))
    uv = world_to_camera_view(scene,camera,point)
    view = point-camera.location
    obstruction = scene.ray_cast(bpy.context.evaluated_depsgraph_get(),camera.location,view.normalized(),
                                 distance=view.length-.002)[0]
    assert not obstruction and .04 < uv.x < .96 and .04 < uv.y < .96, f.name

# Prove a visible sample of each actual reward mesh in the earned state.
for o in locked:
    o.hide_set(True)
bpy.context.view_layer.update()
graph = bpy.context.evaluated_depsgraph_get()
for row, ob in zip((r for r in rows if r["display"]), earned, strict=True):
    points = sorted(ob.data.polygons, key=lambda p: -p.area)
    count = 0
    for p in points:
        point = ob.matrix_world @ p.center
        view = point-camera.location
        uv = world_to_camera_view(scene, camera, point)
        if not (.04 < uv.x < .96 and .04 < uv.y < .96):
            continue
        hit, _, _, _, who, _ = scene.ray_cast(graph, camera.location, view.normalized(),
                                               distance=view.length+.001)
        count += int(hit and who == ob)
        if count == 9:
            break
    assert count >= 3, (ob.name, count)
    row["visible_earned_samples"] = count
for o in locked:
    o.hide_set(False)

(OUT/"receipt.json").write_text(json.dumps({
    "scope":"Detached wall presentation and placement fit only. No installed slots, perks, unlocks, or game changes.",
    "mount_count":len(frames), "existing_earned_meshes_fitted":len(earned),
    "slots_left_unassigned":3, "camera_blender_m":rounded(camera.location),
    "backing_blender_m":rounded(back.location), "sha256_by_asset_stem":PINS, "frames":rows,
},indent=2,ensure_ascii=False)+"\n")
print("E8d: 12 backing checks, 9 fitted trophies, 3 deliberately blank",flush=True)
if os.environ.get("WILDSHARD_VALIDATE_ONLY") != "1":
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 28
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = .085
    scene.cycles.use_denoising = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 92
    for state, active, inactive in (("locked",locked,earned),("earned",earned,locked)):
        for o in active:
            o.hide_render = False
        for o in inactive:
            o.hide_render = True
        scene.render.filepath = str(OUT/f"{state}.jpg")
        bpy.ops.render.render(write_still=True)
