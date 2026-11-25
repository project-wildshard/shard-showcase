"""W4a gate insert and matched static D19 states; never changes the yard donor."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export

parser = argparse.ArgumentParser(__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("yard", type=Path, help="Validated west-physics build directory")
parser.add_argument("--draft", action="store_true")
parser.add_argument("--trace", type=Path, help="Optional native plate-gate rehearsal receipt")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
root = HERE.parents[2]
assets = root / "public/assets/wildshard-art"
hashes = {
    "haul-crate.glb": "d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44",
    "wsc-plan-006-pressure-plate.glb": "cdf40fa1f1036818e460ba5a29f95cbb547c09f8e361e5fbbb1d536d895847cc",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objs = sorted(set(scene.objects) - before, key=lambda o: o.name)
    bpy.context.view_layer.update()
    return objs


def verts(objs):
    return [obj.matrix_world @ v.co for obj in objs if obj.type == "MESH"
            for v in obj.data.vertices]


def bounds(vs):
    return [[min(v[i] for v in vs) for i in range(3)],
            [max(v[i] for v in vs) for i in range(3)]]


def shift(objs, p):
    members = set(objs)
    for obj in objs:
        if obj.parent not in members:
            obj.location += Vector(p)
    bpy.context.view_layer.update()


def bvh(objs):
    points, faces = [], []
    for obj in objs:
        n = len(points)
        points.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(n+i for i in f.vertices) for f in obj.data.polygons)
    return BVHTree.FromPolygons(points, faces)


def mat(name, col, metal, rough, emit=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*col, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["Emission Color"].default_value = (*col, 1)
    p.inputs["Emission Strength"].default_value = emit
    return m


class Solids:
    def __init__(self):
        self.points, self.faces, self.indices, self.mats = [], [], [], []
        self.chamfers = set()

    def box(self, p, size, m, slope=0, chamfer=False):
        if m not in self.mats:
            self.mats.append(m)
        x, y, z = p
        a, b, c = [q*.5 for q in size]
        cs, sn = math.cos(slope), math.sin(slope)
        n = len(self.points)
        if chamfer:
            self.chamfers.add(n//8)
        self.points += [(x+i*a, y+j*b*cs-k*c*sn, z+j*b*sn+k*c*cs)
                        for k in (-1, 1) for j in (-1, 1) for i in (-1, 1)]
        self.faces += [tuple(n+i for i in f) for f in
                       [(0,2,3,1),(4,5,7,6),(0,1,5,4),
                        (2,6,7,3),(0,4,6,2),(1,3,7,5)]]
        self.indices += [self.mats.index(m)]*6

    def object(self, name, bevel=0):
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.points, [], self.faces)
        data.update()
        for m in self.mats:
            data.materials.append(m)
        for f, i in zip(data.polygons, self.indices):
            f.material_index = i
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        if bevel:
            bpy.context.view_layer.objects.active = obj
            mod = obj.modifiers.new("Stamped edges", "BEVEL")
            mod.width = bevel
            mod.segments = 1
            if self.chamfers:
                weights = data.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
                for i, edge in enumerate(data.edges):
                    weights.data[i].value = float(edge.vertices[0]//8 in self.chamfers)
                mod.limit_method = "WEIGHT"
            bpy.ops.object.modifier_apply(modifier=mod.name)
        return obj


for name, digest in hashes.items():
    assert sha(assets / name) == digest, name
baseline = json.loads((root / "scripts/blender/west-physics/expected.json").read_text())
validation = json.loads((args.yard / "parity.json").read_text())
yard = args.yard / "physics-yard-WIP.glb"
assert validation["matched_signature"] in (
    baseline["semantic_signature"], baseline["normalized_semantic_signature"])
assert validation["rebuilt_sha256"] == sha(yard)
scene = bpy.context.scene
clear_scene()
yard_objects = load(yard)
court = [o for o in yard_objects if o.type == "MESH" and "static plate court" in o.name]
floor = [o for o in yard_objects if o.type == "MESH" and "yard 78x54m" in o.name]
assert court and floor, ([o.name for o in court], [o.name for o in floor])
points = verts(court)
west = bounds([p for p in points if abs(p.x+52)<.32 and p.y < -201.6 and p.z < 4.07])
east = bounds([p for p in points if abs(p.x+52)<.32 and p.y > -182.4 and p.z < 4.07])
header = min(p.z for p in points if abs(p.x+52)<.32 and abs(p.y+192)>9.95 and p.z>3.5)
assert abs(header-3.8)<.001, header
lo_y, hi_y = west[1][1], east[0][1]
width = hi_y - lo_y
assert abs(width-19.45)<.001, (lo_y, hi_y, width)
floor_tree = bvh(floor)


def floor_z(x, y):
    hit, *_ = floor_tree.ray_cast(Vector((x,y,1)), Vector((0,0,-1)), 2)
    assert hit is not None, (x,y)
    return hit.z


yc = (lo_y+hi_y)/2
floor_peak = max(floor_z(-52+dx, y) for dx in (-.17,0,.17)
                 for y in [-189, *[lo_y+i*width/390 for i in range(391)]])
bottom = math.ceil((floor_peak+.025)*1000)/1000
h = header-.085-bottom
span = width-.16
steel = mat("Grate | oxidized slate", (.105,.151,.165), .68, .46)
rib = mat("Grate | worn blue-grey ribs", (.223,.321,.337), .65, .49)
orange = mat("Grate | safety oxide enamel", (.70,.236,.059), .44, .38)
zinc = mat("Grate | exposed edges", (.45,.443,.353), .71, .46)
bays = []
bay = span/6
for index in range(6):
    y = (index-2.5)*bay
    w = bay-.034
    g = Solids()
    for dy in (-w/2+.075,w/2-.075):
        g.box((0,y+dy,h/2), (.29,.15,h), steel, chamfer=True)
    for z in (.104,h-.104):
        g.box((0,y,z), (.34,w,.208), steel, chamfer=True)
    for bar in range(8):
        g.box((0,y+(bar-3.5)*w/9,h/2), (.18,.081,h-.37), rib)
    for z in (h*.33,h*.67):
        g.box((.01,y,z), (.19,w-.17,.080), steel)
    sign = -1 if index % 2 else 1
    g.box((-.081,y,h/2), (.13,math.hypot(w-.25,h-.44),.112),
          steel, sign*math.atan2(h-.44,w-.25))
    for dy in (-w*.36,w*.36):
        g.box((-.179,y+dy,h-.12), (.08,.25,.17), orange, chamfer=True)
        for z in (.105,h-.12):
            g.box((-.225,y+dy,z), (.027,.053,.045), zinc)
    bays.append(g.object("Grate bay %02d" % (index+1), .016))

file = out / "w4a-plate-gate-grate.glb"
export(bays, file)
for obj in bays:
    bpy.data.objects.remove(obj, do_unlink=True)
bays = load(file)
gate_meshes = [o for o in bays if o.type == "MESH"]
assert len(gate_meshes) == 6 and all(o.location.length<.001 for o in gate_meshes)
shift(bays, (-52,yc,bottom))
mn,mx = bounds(verts(bays))
assert mn[1]>lo_y+.07 and mx[1]<hi_y-.07, (mn,mx)
assert mn[2]>floor_peak+.024 and mx[2]<header-.08, (mn,mx,floor_peak)
gate_bvh = bvh(gate_meshes)
z = bottom+h*.38
# Across every bay, a ray finds real vertical bars and a neighboring
# aperture still transmits a ray. No alpha, texture or empty proxy.
for i in range(6):
    y = yc+(i-2.5)*bay
    samples = [gate_bvh.ray_cast(Vector((-53,y+j*bay/100,z)),
                                 Vector((1,0,0)), 2)[0] is not None
               for j in range(-45,46)]
    assert any(samples) and not all(samples), (i, samples)

# Remove only the overlaid greybox plates in this scratch scene.
hidden = 0
for obj in court:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    drop = [f for f in mesh.faces if (lambda p: p.z < .34 and
            abs(p.y+192) < 2.002 and
            min(abs(p.x-x) for x in (-82,-72,-62)) < 2.002)(
                obj.matrix_world@f.calc_center_median())]
    hidden += len(drop)
    bmesh.ops.delete(mesh, geom=drop, context="FACES")
    mesh.to_mesh(obj.data)
    mesh.free()
assert hidden >= 30, hidden
plate_x = [-82,-72,-62]
crates, treads, bed_heights, crate_heights = [], [], [], []
for i,x in enumerate(plate_x):
    donor = load(assets/"wsc-plan-006-pressure-plate.glb")
    tread = next(o for o in donor if "Moving_Tread" in o.name)
    bed = max(floor_z(x+dx,-192+dy) for dx in (-2,0,2) for dy in (-2,0,2))
    bed_heights.append(bed)
    shift(donor, (x,-192,bed))
    if i < 2:
        tread.location.z -= .04
        bpy.context.view_layer.update()
        support = bounds(verts([tread]))[1][2]
        crate = load(assets/"haul-crate.glb")
        cb = bounds(verts(crate))
        shift(crate, (x-(cb[0][0]+cb[1][0])/2,
                      -192-(cb[0][1]+cb[1][1])/2, support-cb[0][2]))
        cb = bounds(verts(crate))
        assert abs(cb[0][2]-support)<.0001
        assert cb[0][0]>x-1.77 and cb[1][0]<x+1.77
        assert cb[0][1]>-193.77 and cb[1][1]<-190.23
        crate_heights.append(support)
        crates.append(crate)
    treads.append(tread)

receipt = {
    "source": "Round 5 W4a anchors and D19 hold-only states",
    "yard_sha256": sha(yard),
    "yard_signature": validation["matched_signature"],
    "donors_sha256": hashes,
    "frame_world_x": -52, "frame_inside_y": [lo_y,hi_y],
    "header_underside_m": header, "sampled_floor_max_z_m": floor_peak,
    "grate_bounds_blender_m": [mn,mx],
    "plate_centers_map_xz": [[x,192] for x in plate_x],
    "plate_bed_z_m": bed_heights,
    "crate_contact_z_m": crate_heights,
    "test": "Six GLB reimport bays, visible steel and real apertures, a sampled floor and jamb/header clearance. No physics.",
    "bytes": file.stat().st_size, "glb_sha256": sha(file),
    "triangles": sum(len(p.vertices)-2 for o in gate_meshes for p in o.data.polygons),
}
assert receipt["bytes"] < 180000, receipt
(out/"w4a-plate-gate-grate.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("W4A_RECEIPT", json.dumps(receipt), flush=True)

# These art-direction labels and silhouette marks are review-only.
# They describe which plate is held, not UI, IK, physics or logic.
ink = mat("Review markings | warm white", (.8,.77,.59), .06,.68,.16)
amber = mat("Review markings | unheld", (.95,.27,.06), .08,.44,.15)
mint = mat("Review markings | held", (.22,.97,.70), .10,.42,.17)
dark = mat("Review markings | charcoal wash", (.024,.034,.036), .10,.70)


def floor_text(name, text, at, size, material):
    data = bpy.data.curves.new(name, "FONT")
    data.body = text
    data.size = size
    data.align_x = "CENTER"
    data.materials.append(material)
    obj = bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location = at
    obj.rotation_euler.z = 0
    return obj


for i,x in enumerate(plate_x):
    floor_text("Plate label", f"0{i+1}  /  " + ("CRATE" if i<2 else "PLAYER"),
               (x,-195.18,.064), .38, ink)
    g = Solids()
    g.box((x,-195,.039), (2.75,.55,.031), dark)
    g.object("Plate review label backing")

third_z = bounds(verts([treads[2]]))[1][2]
foot = Solids()
for dx in (-.14,.17):
    foot.box((-62+dx,-192,third_z-.04+.011), (.18,.48,.022), mint)
footprint = foot.object("Illustrative player footprint; not a character", .04)
floor_text("Hold note", "PHYSICS YARD  /  D19",
           (-74,-200.5,.072), .67, ink)

def aim(o, p):
    o.rotation_euler = (Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()


scene.world = bpy.data.worlds.new("Slate yard daylight")
scene.world.use_nodes = True
back = scene.world.node_tree.nodes.get("Background")
back.inputs["Color"].default_value = (.49,.61,.74,1)
back.inputs["Strength"].default_value = .42
sun = bpy.data.lights.new("Raking autumn sun","SUN")
sun.energy = 2.5
sun.angle = .024
sun.color = (1,.819,.64)
key = bpy.data.objects.new(sun.name,sun)
scene.collection.objects.link(key)
key.location = (-100,-235,45)
aim(key,(-63,-192,0))
camera = bpy.data.cameras.new("Same yard camera")
cam = bpy.data.objects.new(camera.name,camera)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = 14 if args.draft else 42
scene.cycles.use_denoising = False
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = .065
scene.cycles.max_bounces = 5
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.resolution_percentage = 52 if args.draft else 100
scene.render.image_settings.file_format = "JPEG"
scene.render.image_settings.quality = 91
camera.type = "ORTHO"


def render(name, p, target, scale, w, h):
    cam.location = p
    aim(cam,target)
    camera.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = w,h
    scene.render.filepath = str(out / (name+".jpg"))
    bpy.ops.render.render(write_still=True)


closed = floor_text("Third plate not held", "2 / 3   |   GRATE CLOSED",
                    (-62,-198.4,.072), .52, amber)
opened = floor_text("Third plate held", "3 / 3   |   GATE OPEN",
                    (-62,-198.4,.072), .52, mint)
p, target = (-108,-233,34), (-66,-192,1.15)
if args.trace:
    trace = json.loads(args.trace.read_text())
    assert receipt["glb_sha256"] == trace["assets"]["w4a-plate-gate-grate.glb"]
    for name, expected in trace["assets"].items():
        assert sha(assets / name) == expected, name
    assert [list((row["x"],row["z"])) for row in trace["plates"]] == receipt["plate_centers_map_xz"]
    assert all(abs(trace["plates"][i]["y"] - h) < .0001
               for i,h in enumerate(receipt["crate_contact_z_m"]))
    released = [trace[key]["states"][2] for key in ("stock","proposed")]
    assert released[0]["held"] == released[1]["held"] == [True, True, False]
    assert [s["colliderEnabled"] for s in released] == [False, True]
    assert released[0]["playerFeet"] == released[1]["playerFeet"]
    fx,fy,fz = released[0]["playerFeet"]
    footprint.location += Vector((fx + 62, 192 - fz, fy - third_z + .04))
    footprint.data.materials.clear()
    footprint.data.materials.append(amber)
    footprint.hide_render=False
    opened.hide_render=True
    closed.hide_render=True
    labels=[
        floor_text("Native stock results", "STOCK  /  GRATE STAYS OPEN",
                   (-64,-198.6,.071), .55, amber),
        floor_text("Reversible adapter results", "REVERSIBLE  /  GRATE RE-CLOSES",
                   (-64,-198.6,.071), .55, mint)]
    scene.cycles.samples = 24
    for i,(tag,state) in enumerate(zip(("stock","reversible"),released,strict=True)):
        labels[0].hide_render=i!=0
        labels[1].hide_render=i!=1
        for o in gate_meshes:
            o.hide_render=not state["colliderEnabled"]
        render("nov25-w4a-"+tag,p,target,44,1440,820)
    sys.exit(0)
opened.hide_render = footprint.hide_render = True
render("nov24-w4a-grate-closed",p,target,44,1440,820)
for o in gate_meshes:
    o.hide_render = True
closed.hide_render = True
opened.hide_render = footprint.hide_render = False
treads[2].location.z -= .04
render("nov24-w4a-grate-open",p,target,44,1440,820)
for o in gate_meshes:
    o.hide_render = False
closed.hide_render = False
opened.hide_render = footprint.hide_render = True
treads[2].location.z += .04
render("nov24-w4a-grate-detail",(-71,-201,8),(-52,-192,1.8),23,1380,750)
