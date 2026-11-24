"""Fit an art-only set of deck shoes to the exact rebuilt West zip route.

blender -b -t 6 --python-exit-code 1 --python zip_finish_fit.py -- BASE OUT
BASE is the output of scripts/blender/west-zip/build.py. OUT is scratch.
"""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

base, out = (Path(p).resolve() for p in sys.argv[sys.argv.index("--") + 1:])
out.mkdir(parents=True, exist_ok=True)
assert (base / "parity.json").is_file(), "Use the verified West route rebuild"
bpy.ops.wm.open_mainfile(filepath=str(base / "west-zip-route-editable.blend"))
scene = bpy.context.scene
center = Vector((-115, 16.5, 12.42))
yaw = math.atan2(-17.5, 97)
axis = Vector((math.cos(yaw), math.sin(yaw), 0))
side = Vector((-axis.y, axis.x, 0))


def objects(prefix):
    result = [o for o in scene.objects if o.name.startswith(prefix)
              and o.type == "MESH"]
    assert result, prefix
    return result


def geometry(items):
    verts, faces = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for original in items:
        ob = original.evaluated_get(dg)
        m = ob.to_mesh()
        n = len(verts)
        verts.extend(ob.matrix_world @ v.co for v in m.vertices)
        faces.extend(tuple(n + x for x in p.vertices) for p in m.polygons)
        ob.to_mesh_clear()
    return verts, faces


def surface(mesh, direction):
    verts, faces = mesh
    tree = BVHTree.FromPolygons(verts, faces, all_triangles=False)

    def height(x, y):
        hit = tree.ray_cast(Vector((x, y, 12.42 + direction)), Vector((0, 0, -direction)), 1.15)[0]
        assert hit is not None, (x, y, direction)
        return hit.z

    return height


deck = surface(geometry(objects("MODULE-008")), 1)
under = surface(geometry(objects("PROP-035")), -1)
flange_verts, _ = geometry(objects("Illustrative roof tie-down | flange"))
flange_inset = min((v - center).dot(axis) for v in flange_verts)
pad_verts, _ = geometry(objects("PROP-035"))
flange_pad_margin = flange_inset - max((v - center).dot(axis) for v in pad_verts)


def metal(name, color, rough):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = .53
    bs.inputs["Roughness"].default_value = rough
    return m


dark = metal("ZIP shoe | blackened steel", (.075, .090, .098), .54)
edge = metal("ZIP shoe | weathered copper edge", (.27, .122, .045), .43)
parts, receipts = [], []
def fit_foot(ang, radius, footprint):
    mid = center + radius * (math.cos(ang) * axis + math.sin(ang) * side)
    v, faces, samples = [], [], []
    for j in range(8):
        a = ang + j * math.tau / 8
        xy = mid + footprint * (math.cos(a) * axis + math.sin(a) * side)
        lo, hi = deck(xy.x, xy.y), under(xy.x, xy.y)
        samples.append((lo, hi))
        # Seat just inside each donor, with a fine upper edge band.
        v.extend([(xy.x, xy.y, lo - .004),
                  (xy.x, xy.y, hi - .011),
                  (xy.x, xy.y, hi + .004)])
    center_lo, center_hi = deck(mid.x, mid.y), under(mid.x, mid.y)
    samples.append((center_lo, center_hi))
    v.extend([(mid.x, mid.y, center_lo - .004),
              (mid.x, mid.y, center_hi + .004)])
    seat_depths = []
    for j in range(8):
        a, b = j * 3, ((j + 1) % 8) * 3
        faces.extend([(24, b, a), (25, a+2, b+2),
                      (a, b, b+1, a+1), (a+1, b+1, b+2, a+2)])
        # Verify interior points, not just the authored vertices.
        for u, w in ((.25, .25), (.6, .2), (.2, .6), (.45, .45)):
            lo = Vector(v[24]) * (1-u-w) + Vector(v[a]) * u + Vector(v[b]) * w
            hi = Vector(v[25]) * (1-u-w) + Vector(v[a+2]) * u + Vector(v[b+2]) * w
            seat_depths.extend([deck(lo.x, lo.y)-lo.z, hi.z-under(hi.x, hi.y)])
    if min(seat_depths) <= .001 or max(seat_depths) >= .010:
        return None
    seam = min(hi - lo for lo, hi in samples)
    clearance = flange_inset - max((Vector(p) - center).dot(axis) for p in v)
    if seam <= .014 or clearance <= .12:
        return None
    return v, faces, samples, seat_depths, seam, clearance


# Place six compact shoes under the existing pad. At deck seams, step the
# shoe inboard or around the seam rather than spanning two deck elevations.
for i in range(6):
    found = None
    for radius in (1.21, 1.15, 1.09, 1.02, .94, .86):
        for correction in (0, 5, -5, 10, -10, 15, -15):
            angle = 30 + 60*i + correction
            found = fit_foot(math.radians(angle), radius, .116)
            if found:
                break
        if found:
            break
    assert found, ("no seat found", i)
    v, faces, samples, seat_depths, seam, clearance = found
    mesh = bpy.data.meshes.new(f"Deck shoe {i+1:02d}")
    mesh.from_pydata([Vector(p) - center for p in v], [], faces)
    mesh.materials.append(dark)
    mesh.materials.append(edge)
    for p in mesh.polygons:
        p.material_index = int(p.index % 4 == 3)
    node = bpy.data.objects.new(mesh.name, mesh)
    scene.collection.objects.link(node)
    node.location = center
    parts.append(node)
    receipts.append({"shoe": i+1, "radius_m": radius, "clock_deg": angle,
                     "gap_min_mm": round(seam*1000, 1),
                     "gap_max_mm": round(max(hi-lo for lo, hi in samples)*1000, 1),
                     "flange_axis_margin_mm": round(clearance*1000, 1),
                     "sampled_interpolated_seat_mm": [round(min(seat_depths)*1000, 1),
                                                       round(max(seat_depths)*1000, 1)]})

# Export an offset-from-pad-origin patch, not the reviewed West route donors.
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.location = (0, 0, 0)
    o.select_set(True)
asset = out / "west-zip-deck-shoes.glb"
bpy.ops.export_scene.gltf(filepath=str(asset), export_format="GLB", use_selection=True)
raw = asset.read_bytes()
assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
doc = json.loads(raw[20:20+struct.unpack_from("<I", raw, 12)[0]])
tris = sum(doc["accessors"][p["indices"]]["count"] // 3
           for m in doc["meshes"] for p in m["primitives"])
assert len(doc["nodes"]) == len(doc["meshes"]) == 6
assert tris == 288 and len(doc["materials"]) == 2
assert not any(k in doc for k in ("images", "skins", "animations", "cameras"))
for o in parts:
    o.location = center

# Work from exact geometry, with show lighting and matching exposures per view.
for o in list(scene.objects):
    if o.type in {"LIGHT", "CAMERA"}:
        bpy.data.objects.remove(o, do_unlink=True)
world = bpy.data.worlds.new("Zip fit overcast")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.25, .37, .54, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .38
scene.world = world


def light(name, local, color, watts, size, target):
    d = bpy.data.lights.new(name, "AREA")
    d.color, d.energy, d.size = color, watts, size
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = center + Vector(local)
    o.rotation_euler = (center + Vector(target) - o.location).to_track_quat("-Z", "Y").to_euler()


light("Warm key", (-4, -5, 6), (1, .79, .59), 3900, 6, (0, 0, 0))
light("Roof bounce", (3, 5, 3), (.52, .75, 1), 2200, 6, (0, 0, 0))
light("Seam fill", (-2, -3, 1.05), (1, .88, .67), 355, 2, (0, 0, 0))
cam = bpy.data.objects.new("Fit comparison camera", bpy.data.cameras.new("Fit comparison camera"))
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.cycles.max_bounces = 5
scene.view_settings.view_transform = "AgX"
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 91


def shot(name, location, target, focal, size, fitted):
    for o in parts:
        o.hide_render = not fitted
    cam.location = center + Vector(location)
    cam.rotation_euler = (center + Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = focal
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(out / (name + ".jpg"))
    bpy.ops.render.render(write_still=True)


for fitted in (False, True):
    shot("low-" + ("fitted" if fitted else "original"),
         (-.68, -3.75, .32), (.1, -.49, .075), 57, (960, 560), fitted)
shot("arrival", (-5.7, -.2, 3.35), (.22, .20, .43), 46, (1100, 700), True)

# Diagnostic view only: hide the pad, rather than change any roof meshes.
pad_objects = objects("PROP-035")
for o in pad_objects:
    o.hide_render = True
shot("revealed", (-3.25, -3.8, 4.7), (.1, -.1, .15), 55, (1050, 760), True)
for o in pad_objects:
    o.hide_render = False

report = {"scope": "Static art fit, not collision, support engineering or native traversal.",
          "baseline_signature": json.loads((base / "parity.json").read_text())["matched_signature"],
          "pad_origin_blender": list(center),
          "pad_to_flange_axis_margin_mm": round(flange_pad_margin * 1000, 1),
          "origin_gap_mm": round((under(center.x, center.y)-deck(center.x,center.y))*1000,1),
          "fit_samples_per_shoe": 9, "checks_per_contact_surface": 32,
          "authored_seat_into_mesh_mm": 4, "shoes": receipts,
          "changed_donors_or_cable": False,
          "asset": {"bytes": len(raw), "triangles": tris,
                    "sha256": hashlib.sha256(raw).hexdigest()}}
(out / "fit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
