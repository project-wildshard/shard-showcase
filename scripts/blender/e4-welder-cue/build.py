"""An intermittent amber floor boundary for E4's fictional Welder attack."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = argparse.ArgumentParser()
args.add_argument("out", type=Path)
args.add_argument("--half-angle", type=float, default=28)
args.add_argument("--no-render", action="store_true")
a = args.parse_args(sys.argv[sys.argv.index("--") + 1:])
assert 15 <= a.half_angle <= 45, "Supported preview half-angle: 15–45°"
out = a.out.resolve()
out.mkdir(parents=True, exist_ok=True)
asset_dir = Path(__file__).resolve().parents[3] / "public/assets/wildshard-art"
def clear():
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def import_glb(path, offset=(0, 0, 0), digest=None):
    if digest:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
    prior = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    new = sorted(set(bpy.context.scene.objects) - prior, key=lambda o: o.name)
    for obj in new:
        if obj.parent not in new:
            obj.location += Vector(offset)
    bpy.context.view_layer.update()
    return new

def material(name, color, emit=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = .75
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = emit
    return m

clear()
half = math.radians(a.half_angle)
R = 6
Z = .006
points, faces, indices = [], [], []
def polar(r, t):
    return (r * math.sin(t), -r * math.cos(t), Z)
def quad(ps, mat):
    k = len(points)
    points.extend(ps)
    p, q, r = map(Vector, ps[:3])
    order = range(4) if (q - p).cross(r - p).z > 0 else range(3, -1, -1)
    faces.append(tuple(k + i for i in order))
    indices.append(mat)
def arc(r0, r1, t0, t1, mat, n):
    for i in range(n):
        u = t0 + (t1 - t0) * i / n
        v = t0 + (t1 - t0) * (i+1) / n
        quad([polar(r0, u), polar(r1, u), polar(r1, v), polar(r0, v)], mat)
# Outer line reads the stop edge; the gaps and hatching keep the ground visible.
arc(R-.044, R, -half, half, 1, 32)
for i in range(12):
    step = 2 * half / 12
    u = -half + i * step
    arc(R-.155, R-.050, u + .08*step, u + .56*step, 0, 3)
for side in (-1, 1):
    for i in range(7):
        r = .36 + i * .79
        t = half - .046 / r
        length = .53 if i < 6 else .84
        ps = [polar(r, side*(t-.093/r)), polar(r+length, side*(half-.108/(r+length))),
              polar(r+length, side*half), polar(r+.06, side*half)]
        quad(ps, 1 if i in (1, 4, 6) else 0)
for r in (1.76, 3.26, 4.76):
    for s in (-1, 1):
        quad([(s*.423,-r,Z),(s*.067,-r-.260,Z),(s*.067,-r-.132,Z),(s*.423,-r+.103,Z)],0)
mesh = bpy.data.meshes.new("Six metre sector | interrupted amber perimeter")
mesh.from_pydata(points, [], faces)
mesh.update()
obj = bpy.data.objects.new("Welder cone floor boundary", mesh)
bpy.context.collection.objects.link(obj)
mesh.materials.append(material("Oxide amber | secondary hatching", (.78,.16,.018), .95))
mesh.materials.append(material("Amber white | leading edge", (1,.42,.059), 1.45))
for f,i in zip(mesh.polygons,indices):
    f.material_index = i
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
glb = out / "e4-welder-cone-cue.glb"
bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True,
                         export_normals=True, export_texcoords=False, export_tangents=False)
clear()
models = import_glb(glb)
ob = next(o for o in models if o.type == "MESH")
vertices = [ob.matrix_world @ v.co for v in ob.data.vertices]
assert len([o for o in models if o.type == "MESH"]) == 1
assert max(abs(v.z-Z) for v in vertices) < 1e-6
assert all(p.normal.z > .999 for p in ob.data.polygons)
assert abs(max(math.hypot(v.x,v.y) for v in vertices)-R) < 1e-6
assert max(abs(math.atan2(v.x,-v.y)) for v in vertices) <= half + 1e-7
# Parse exporter output rather than assuming the file has retained a procedural setup.
blob = glb.read_bytes()
n = struct.unpack_from("<I",blob,12)[0]
doc = json.loads(blob[20:20+n])
prims = doc["meshes"][0]["primitives"]
triangles = sum(doc["accessors"][p["indices"]]["count"]//3 for p in prims)
assert len(prims) == 2 and triangles == 176 and len(blob) < 18000
assert all(not doc.get(k) for k in ("images", "textures", "animations", "skins"))
assert len(doc["materials"]) == 2 and all(m.get("emissiveFactor") for m in doc["materials"])
proof = {"asset":"e4-welder-cone-cue.glb","sha256":hashlib.sha256(blob).hexdigest(),
         "bytes":len(blob),"triangles":triangles,"primitives":2,
         "extent_radius_m":R,"half_angle_degrees_art_provisional":a.half_angle,
         "plane_height_m":Z,"glTF_forward":"-Z","plan_windup_ms":800,
         "visual_only":True,"follows_runtime_wedge":False}
(out / "e4-welder-cone-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print(proof, flush=True)
if a.no_render:
    sys.exit(0)

import_glb(asset_dir/"e4-cover-bay-shell.glb", (0,2.75,0),
           "f58972a6d877906fa16f28527e8b0e46c78750a5c04aad9a45c641821228cdc9")
import_glb(asset_dir/"wsc-prop-057-foundry-furnace.glb", (.52,3.31,0),
           "0c47183c8f38699661f527d01b8e85a4891e03ec898cabd028b07568e32b8530")
ground = material("Preview concrete only", (.14,.16,.178))
nt = ground.node_tree
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 15
noise.inputs["Roughness"].default_value = .74
coord = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(coord.outputs["Object"],noise.inputs["Vector"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .21
ramp.color_ramp.elements[0].color = (.066,.078,.087,1)
ramp.color_ramp.elements[1].position = .76
ramp.color_ramp.elements[1].color = (.163,.179,.190,1)
nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
bsdf = nt.nodes.get("Principled BSDF")
nt.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .34
bump.inputs["Distance"].default_value = .019
nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
bpy.ops.mesh.primitive_plane_add(size=120)
bpy.context.object.data.materials.append(ground)
scene = bpy.context.scene
scene.world.color = (.12,.15,.20)
scene.render.engine = "CYCLES"
scene.cycles.samples = 30
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "AgX"
def aim(obj,target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
def area(loc, at, watts, color, size):
    bpy.ops.object.light_add(type="AREA",location=loc)
    ob=bpy.context.object
    ob.data.energy, ob.data.color, ob.data.shape, ob.data.size=watts,color,"DISK",size
    aim(ob,at)
area((-4,-5,9),(0,0,0),1870,(.64,.78,1),8)
area((5,3,5),(0,1,1),1380,(1,.68,.41),6)
for name, pos, target, lens, dimensions in [
    ("approach",(0,-10,1.68),(0,-2,.66),13,(804,1748)),
    ("footprint",(6.5,-9.3,8.45),(0,-.98,.47),29,(1320,900)),
]:
    bpy.ops.object.camera_add(location=pos)
    cam=bpy.context.object
    aim(cam,target)
    cam.data.lens=lens
    scene.camera=cam
    scene.render.resolution_x,scene.render.resolution_y=dimensions
    scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    projected = [world_to_camera_view(scene, cam, v) for v in vertices]
    print(name, {k: tuple(round(f(kv),4) for f in (min,max)) for k,kv in zip("xy",zip(*projected))}, flush=True)
    assert all(.035 < p.x < .965 and .035 < p.y < .965 and p.z > 0 for p in projected), name
    scene.render.image_settings.file_format="WEBP"
    scene.render.image_settings.quality=89
    scene.render.filepath=str(out/f"nov25-e4-welder-{name}.webp")
    bpy.ops.render.render(write_still=True)
