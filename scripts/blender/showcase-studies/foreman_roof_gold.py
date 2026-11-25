"""E13 Foreman roof: dress the pinned office and check the actual Gold fit."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene
assets = HERE.parents[2] / "public/assets/wildshard-art"
pins = {
    "c3-office-sector.glb": "631f39353d7eed6d4bba196f71a30342f7a5aac1fb1d3579560807c8db971f31",
    "w9b-gold-find-cube.glb": "3dfd3a95e261b340911f5b93ffce91a8840a91a0464b915336567aa2f3b6bce0",
}
c = math.sqrt(.5)
roof = Vector((70 * c, 0, 8.5))


def load(path, transform=Matrix.Identity(4)):
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    added = set(scene.objects) - before
    for obj in sorted(added, key=lambda o: o.name):
        if obj.parent not in added:
            obj.matrix_world = transform @ obj.matrix_world
    bpy.context.view_layer.update()
    return sorted((o for o in added if o.type == "MESH"), key=lambda o: o.name)


def donor(name, transform=Matrix.Identity(4)):
    path = assets / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pins[name], name
    return load(path, transform)


def points(objects):
    return [o.matrix_world @ v.co for o in objects for v in o.data.vertices]


def tree(objects):
    vv, ff = [], []
    for obj in objects:
        i = len(vv)
        vv += points([obj])
        ff += [tuple(i + n for n in face.vertices) for face in obj.data.polygons]
    return BVHTree.FromPolygons(vv, ff)


def surface(bvh, position):
    return bvh.ray_cast(Vector((position.x, position.y, 12)), Vector((0, 0, -1)), 4)[0]


def mat(name, rgb, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    return m


parts = []
forged = mat("C3 roof blackened repair steel", (.054, .083, .090), .64, .47)
cap = mat("C3 roof zinc bolt heads", (.285, .329, .334), .71, .41)
paint = mat("C3 roof worn teal index enamel", (.041, .246, .210), .30, .62)
dull = mat("C3 roof oxidized red seam", (.190, .056, .030), .51, .72)


def block(name, xy, z, dimensions, material, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(*xy, z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("Rolled steel edge", "BEVEL")
        mod.width, mod.segments = bevel, 1
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    parts.append(obj)


# Four open corners frame the roof marker without lifting the cube. Welded
# lap seams run away from the marker, not under it. Everything is add-on art.
for sx in (-1, 1):
    for sy in (-1, 1):
        block("Riveted corner, long leg", (sx*.967, sy*.854), .024, (.54,.14,.050), forged, .012)
        block("Riveted corner, short leg", (sx*1.167, sy*.600), .024, (.14,.368,.050), forged, .012)
        block("One faded locator stripe", (sx*.967, sy*.858), .050, (.325,.062,.006), paint, .002)
        for x,y in ((sx*1.167,sy*.529),(sx*1.167,sy*.824),(sx*.769,sy*.854)):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.033, depth=.018, location=(x,y,.055))
            bolt = bpy.context.object
            bolt.name = "Roof patch hex bolt"
            bolt.data.materials.append(cap)
            parts.append(bolt)
for x in (-2.78,2.78):
    block("Roof lap seam, interrupted around find", (x,0), .007, (.062,5.3,.016), dull, .005)
    for y in (-2.4,2.4):
        block("Lap seam captive tab", (x,y), .015, (.232,.118,.032), forged, .007)

path = out / "e13-foreman-roof-dressing.glb"
export(parts, path)
raw = path.read_bytes()
assert struct.unpack_from("<4sII",raw) == (b"glTF",2,len(raw))
doc = json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
tris = sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
assert "images" not in doc and "animations" not in doc and tris < 1500
for o in parts:
    bpy.data.objects.remove(o, do_unlink=True)

orientation = Matrix.Rotation(-math.pi/4, 4, "Z")
placement = Matrix.Translation(roof) @ orientation
office = donor("c3-office-sector.glb")
trim = load(path, placement)
base = tree(office)
dressing = tree(trim)
footprint = [placement @ Vector((x/20,y/20,0)) for x in range(-9,10) for y in range(-9,10)]
assert all(abs(surface(base, p).z - roof.z) < 3e-5 for p in footprint)
assert all(surface(dressing, p) is None for p in footprint)
trim_pts = points(trim)
assert all(abs(surface(base, p).z - roof.z) < 3e-5 for p in trim_pts)
gold = donor("w9b-gold-find-cube.glb", Matrix.Translation(roof + Vector((0,0,.0003))))
g = points(gold)
assert abs(min(v.z for v in g)-8.5) < .00005


def visibility(p):
    bvh = tree(office + trim)
    box = [sum(v[i] for v in g)/len(g) for i in range(3)]
    cx, cy, _ = box
    sample = [Vector((cx, cy, z)) for z in (8.55, 8.75, 9., 9.25, 9.45)]
    clear = []
    for v in sample:
        ray = v - Vector(p)
        clear.append(bvh.ray_cast(Vector(p), ray.normalized(), ray.length)[0] is None)
    return clear


floor_eye = (20, -4.7, 1.75)
roof_eye = roof + orientation @ Vector((3.75, -4.45, 1.70))
assert abs(surface(base, roof_eye).z - 8.5) < 3e-5
floor_visibility, roof_visibility = visibility(floor_eye), visibility(roof_eye)
assert floor_visibility.count(True) < 5 and all(roof_visibility)

world = bpy.data.worlds.new("Storm-cleared C3 sky")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.29,.43,.69,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .38
scene.world = world


def light(name, kind, at, look, power, spread, color):
    d = bpy.data.lights.new(name, kind)
    d.energy, d.color = power, color
    if kind == "SUN":
        d.angle = spread
    else:
        d.size = spread
    obj = bpy.data.objects.new(name,d)
    scene.collection.objects.link(obj)
    obj.location = at
    obj.rotation_euler = (Vector(look)-obj.location).to_track_quat("-Z","Y").to_euler()


light("Last light over C3","SUN",(16,-23,29),(45,0,2),2.9,.107,(1,.72,.49))
light("Cyan roof bounce","AREA",(47,8,13),roof,1250,6.3,(.51,.73,1))
light("Warm glazing bounce","AREA",(34,-5,7.3),(43,1,4.5),420,5.2,(1,.65,.38))
cam = bpy.data.objects.new("Roof review",bpy.data.cameras.new("Roof review"))
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = .071
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "AgX"
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 93


def render(name, at, focus, lens):
    cam.location = at
    cam.rotation_euler = (Vector(focus)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens = lens
    scene.render.resolution_x,scene.render.resolution_y = (1320,880)
    bpy.context.view_layer.update()
    coords = [world_to_camera_view(scene,cam,v) for v in g]
    assert all(0.015<v.x<.985 and .015<v.y<.985 and v.z>0 for v in coords)
    scene.render.filepath = str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)


render("rooftop-eye",roof_eye,roof+Vector((-.36,0,.27)),43)
render("court-eye",floor_eye,(45,0,7.6),46)
summary = {
    "scope": "Static dressing of existing C3 roof; no new collectible, route, actor, collision, pickup or tracking.",
    "source_archive": "Raynos/project-wildshard-singleplayer@ce1cf050b3 art/showcase-template/round-5-blockout",
    "archive_blobs": {"layout.js":"5d019a020361c47187ec889f2bc947f82cd9f98a","lab.js":"51a3b4bef1f2d4891172164d10893d98d450a3b9"},
    "map_gold_xyz_m": [181,8.5,151],
    "roof_height_m": 8.5,
    "glb_origin": "Map Gold xyz, with glTF axes aligned to original map world axes.",
    "sampled_gold_footprint_points": len(footprint),
    "sampled_dressing_vertices_over_roof": len(trim_pts),
    "cube_actual_bottom_y_m": round(min(v.z for v in g),6),
    "court_eye_height_above_floor_m": 1.70,
    "roof_eye_height_above_cap_m": 1.70,
    "centerline_sample_heights_m": [8.55,8.75,9,9.25,9.45],
    "line_of_sight_court": floor_visibility,
    "line_of_sight_roof": roof_visibility,
    "donor_pins": pins,
    "asset": {"bytes":len(raw),"triangles":tris,"sha256":hashlib.sha256(raw).hexdigest()}
}
(out/"foreman-roof-gold.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary))
