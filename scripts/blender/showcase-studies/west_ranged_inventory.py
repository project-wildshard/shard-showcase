"""Two nonfunctional Wildshard inventory meshes from the WSC-GEAR-003/004 concept plates."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
scene = bpy.context.scene
palette = [
    ("Black walnut", (.112, .047, .027), .02, .44, 0),
    ("Caramel edgewood", (.225, .087, .038), .02, .48, 0),
    ("Aged brass", (.48, .249, .072), .66, .36, 0),
    ("Chocolate leather", (.115, .084, .060), .0, .71, 0),
    ("Cream cord", (.42, .25, .115), .0, .75, 0),
    ("Blued iron", (.054, .072, .098), .65, .45, 0),
    ("Graphite patina", (.044, .058, .069), .55, .56, 0),
    ("Shard glass", (.017, .51, .65), .21, .27, .46),
]
WALNUT, EDGE, BRASS, LEATHER, CORD, IRON, PATINA, SHARD = range(len(palette))


def pbr(name, color, metal=0, rough=.5, emissive=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    node = mat.node_tree.nodes["Principled BSDF"]
    for key, value in {
        "Base Color": (*color, 1), "Metallic": metal, "Roughness": rough,
        "Emission Color": (*color, 1), "Emission Strength": emissive,
    }.items():
        node.inputs[key].default_value = value
    return mat


class Model:
    def __init__(self):
        self.verts, self.faces, self.ids = [], [], []

    def add(self, coords, faces, mats):
        start = len(self.verts)
        self.verts.extend(coords)
        self.faces.extend(tuple(start + i for i in f) for f in faces)
        self.ids.extend([mats] * len(faces) if isinstance(mats, int) else mats)

    def loft(self, rings, material, sides=8, smooth_shape=False, tilt=None):
        """Closed polygonal envelope. Cross sections follow the authored art silhouette."""
        coords = []
        bevel = .66
        for c, a, b, ra, rb in rings:
            section = [(math.cos(i * math.tau / sides), math.sin(i * math.tau / sides))
                       for i in range(sides)] if smooth_shape else [
                (1, bevel), (bevel, 1), (-bevel, 1), (-1, bevel),
                (-1, -bevel), (-bevel, -1), (bevel, -1), (1, -bevel),
            ]
            assert len(section) == sides
            coords.extend(Vector(c) + Vector(a) * x * ra + Vector(b) * y * rb
                          + Vector((0, 0, tilt(c, x, y) if tilt else 0))
                          for x, y in section)
        planes = [tuple(reversed(range(sides))), tuple(range(len(coords) - sides, len(coords)))]
        indices = [material if isinstance(material, int) else material(0, 1)] * 2
        for j in range(len(rings) - 1):
            for i in range(sides):
                a, b = j * sides + i, j * sides + (i + 1) % sides
                planes.append((a, b, b + sides, a + sides))
                indices.append(material if isinstance(material, int) else material(j, i))
        self.add(coords, planes, indices)

    def rod(self, a, b, radius, material, sides=6):
        a, b = Vector(a), Vector(b)
        tangent = (b - a).normalized()
        axis = Vector((0, 0, 1)) if abs(tangent.z) < .8 else Vector((1, 0, 0))
        v = axis.cross(tangent).normalized()
        w = tangent.cross(v)
        self.loft([(a, v, w, radius, radius), (b, v, w, radius, radius)],
                  material, sides=sides, smooth_shape=True)

    def build(self, name):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.verts, [], self.faces)
        assert not mesh.validate(verbose=True)
        for materials in palette:
            mesh.materials.append(pbr(*materials))
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        for f, i in zip(bm.faces, self.ids, strict=True):
            f.material_index = i
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        assert all(f.calc_area() > 1e-9 for f in bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        return obj


def bow():
    m = Model()
    # Citation: catalogue turnaround WSC-GEAR-003; not a working bow.
    # X is the visible sweep; Z is the length; the grip centre is zero.
    stations = [
        (0, 0, .034, .030), (.105, -.002, .029, .033), (.143, -.007, .026, .032),
        (.225, -.027, .026, .033), (.319, -.040, .025, .034),
        (.367, -.039, .024, .033), (.405, -.035, .023, .031),
        (.430, -.031, .022, .030), (.454, -.026, .021, .028),
        (.482, -.019, .020, .026), (.526, -.003, .018, .023),
        (.586, .028, .015, .019), (.649, .067, .012, .015),
        (.708, .110, .010, .011), (.760, .144, .009, .010),
        (.796, .151, .010, .010), (.814, .149, .005, .006),
    ]
    for sign in (-1, 1):
        rings = [((x, 0, z * sign), (1, 0, 0), (0, 1, 0), w, d)
                 for z, x, w, d in stations]
        m.loft(rings, lambda j, i: BRASS if j >= 14 or (j in (5, 7, 9) and i in (1, 5))
               else EDGE if i in (0, 4, 7) else WALNUT,
               tilt=lambda c, x, y: sign * .009 * x if .35 < abs(c[2]) < .54 else 0)
        coords = [(sign * z, x, w, d) for z, x, w, d in [
            (.096, -.002, .036, .035), (.102, -.002, .042, .041),
            (.118, -.003, .042, .041), (.127, -.004, .036, .035)]]
        m.loft([((x, 0, z), (1, 0, 0), (0, 1, 0), w, d)
                for z, x, w, d in coords], BRASS)
    # Leather ribbons share the body vertices, so no coplanar overlays flicker.
    wrap = [(-.106, .034), (-.087, .039), (-.058, .040), (-.054, .040),
            (-.025, .041), (-.021, .040), (.009, .041), (.013, .040),
            (.045, .040), (.049, .039), (.080, .039), (.106, .034)]
    m.loft([((0, 0, z), (1, 0, 0), (0, 1, 0), w, w*.90) for z, w in wrap],
           lambda j, i: WALNUT if j in (2, 4, 6, 8) else LEATHER,
           tilt=lambda c, x, y: .011 * x if abs(c[2]) < .082 else 0)
    m.rod((.145, 0, -.775), (.145, 0, .775), .0043, CORD)
    return m


def crossbow():
    m = Model()
    # The dark fork and crystal are the concept's graphic silhouette.
    # Entire center is solid art geometry with no working mechanism.
    body = [
        (-.38, -.033, .058, .080), (-.357, -.031, .067, .088),
        (-.28, -.020, .064, .078), (-.19, .00, .055, .058),
        (-.10, .027, .044, .037), (-.016, .021, .044, .044),
        (.066, .006, .055, .059), (.145, .016, .055, .052),
        (.27, .022, .056, .049), (.39, .020, .059, .061),
        (.447, .021, .054, .067), (.465, .021, .046, .061),
    ]
    m.loft([((0, y, z), (1, 0, 0), (0, 0, 1), w, h)
            for y, z, w, h in body],
           lambda j, i: IRON if j in (0, 10) else EDGE if i in (0, 1, 7) else WALNUT)
    for sign in (-1, 1):
        wing = [(0, .391, .046, .052), (.104, .395, .033, .048),
                (.218, .370, .021, .044), (.323, .337, .019, .035),
                (.408, .290, .016, .024), (.444, .275, .018, .023)]
        m.loft([((x*sign, y, .034), (0, 1, 0), (0, 0, 1), w, h)
                for x, y, w, h in wing],
               lambda j, i: IRON if i in (0, 1, 7) else PATINA)
        m.rod((.420*sign, .279, .060), (0, .278, .101), .0045, CORD)
        for x in (.407, .418, .429):
            m.loft([((xx*sign, .289, .034), (0, 1, 0), (0, 0, 1), .023, .029)
                    for xx in (x-.004, x+.004)], CORD)
        m.loft([((.033*sign, y, .074), (1, 0, 0), (0, 0, 1), .015, h)
                for y, h in [(.09, .009), (.114, .011), (.39, .011), (.414, .008)]], IRON)
        for y in (.130, .208, .288, .371):
            m.rod((.033*sign, y, .081), (.033*sign, y, .088), .006, BRASS)
        # Flat warm filigree on the beveled stock, not mechanical detailing.
        for y, w, dz in [(-.333, .065, .016), (-.269, .064, .022), (-.209, .057, .031)]:
            m.add([(w*sign, y-.012, dz), (w*sign, y+.015, dz-.023),
                   (w*sign, y+.037, dz-.022), (w*sign, y+.013, dz-.010)],
                  [(0, 1, 2, 3)], BRASS)
    m.loft([((0, y, .024), (1, 0, 0), (0, 0, 1), w, h)
            for y, w, h in [(.447, .047, .058), (.465, .061, .078), (.477, .054, .070)]], IRON)
    for y, z, sign in [(.479, .023, 1), (-.382, -.032, -1)]:
        # Squashed faceted turquoise emblem stands proud of the solid shell.
        points = [(0, y, z+.042), (.023, y, z), (0, y, z-.042),
                  (-.023, y, z), (0, y+sign*.009, z)]
        m.add(points, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], SHARD)
    return m


assets = [
    ("WSC-GEAR-003", "bow", bow, (.65, -3.9, .63), (0, 0, .04), 1.94),
    ("WSC-GEAR-004", "crossbow", crossbow, (1.05, 1.25, .66), (0, .035, 0), 1.24),
]
receipts = {}
for aid, slug, builder, view, target, scale in assets:
    clear_scene()
    obj = builder().build(aid + " | " + slug.title() + " | Inventory")
    f = out / f"{aid.lower()}-{slug}.glb"
    export([obj], f)
    blob = f.read_bytes()
    assert struct.unpack_from("<4sII", blob) == (b"glTF", 2, len(blob))
    doc = json.loads(blob[20:20+struct.unpack_from("<I", blob, 12)[0]])
    assert len(doc["meshes"]) == len(doc["nodes"]) == 1
    assert not any(k in doc for k in ("animations", "images", "skins"))
    assert len(blob) <= 65536, (slug, len(blob))
    primitives = doc["meshes"][0]["primitives"]
    count = sum(doc["accessors"][p["indices"]]["count"] // 3 for p in primitives)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(f))
    reimported, = [o for o in scene.objects if o.type == "MESH"]
    assert reimported.location.length < .00001
    assert all(math.isfinite(n) and n > .02 for n in reimported.dimensions)
    reimported.data.calc_loop_triangles()
    assert len(reimported.data.loop_triangles) == count
    receipts[aid] = dict(bytes=len(blob), triangles=count, primitives=len(primitives),
                         blender_dimensions=[round(x, 5) for x in reimported.dimensions],
                         pivot="authored model origin", textures=0, skins=0, animations=0,
                         sha256=hashlib.sha256(blob).hexdigest())
    if os.getenv("WILDSHARD_VALIDATE_ONLY") == "1":
        continue

    def aim(o, p):
        o.rotation_euler = (Vector(p) - o.location).to_track_quat("-Z", "Y").to_euler()

    def area(name, loc, power, color, size):
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.color, light.size = power, color, size
        o = bpy.data.objects.new(name, light)
        scene.collection.objects.link(o)
        o.location = loc
        aim(o, target)

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.87 if slug == "bow" else -.16))
    bpy.context.object.data.materials.append(pbr("Backdrop | ink", (.022, .048, .061), .08, .66))
    scene.world = bpy.data.worlds.new("Inventory gallery")
    scene.world.color = (.15, .23, .30)
    area("Warm shaped softbox", (-1.75, -2.3, 2.5), 260 if slug == "bow" else 178, (1, .77, .57), 2.2)
    area("Mineral blue edge", (.7, 1.35, 1.45), 162 if slug == "bow" else 105, (.39, .76, 1), 1.8)
    area("Broad front bounce", (2.1, -.5, .9), 107 if slug == "bow" else 80, (.73, .86, 1), 1.7)
    d = bpy.data.cameras.new("Catalogue portrait")
    scene.camera = bpy.data.objects.new(d.name, d)
    scene.collection.objects.link(scene.camera)
    d.type, d.ortho_scale = "ORTHO", scale
    scene.camera.location = view
    aim(scene.camera, target)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 46
    scene.cycles.use_denoising = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.resolution_x = 1020 if slug == "bow" else 1240
    scene.render.resolution_y = 1180 if slug == "bow" else 930
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 91
    scene.render.filepath = str(out / f"nov24-w3b-{slug}-inventory.jpg")
    bpy.ops.render.render(write_still=True)

(out / "west-ranged-inventory.json").write_text(json.dumps({
    "readiness": "nonfunctional static inventory art, no hands, equip poses, draw/reload, or game integration",
    "source": "WSC-GEAR-003 and WSC-GEAR-004 provisional Art Catalog turnarounds; W3b plan",
    "assets": receipts,
}, indent=2) + "\n")
