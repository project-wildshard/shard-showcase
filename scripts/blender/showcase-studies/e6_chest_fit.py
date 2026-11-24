"""Compare the pinned Round 5 Band 6 anchor and one static art offset."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene
src = HERE.parents[2]/"public/assets/wildshard-art/e1d-band1-scrip-chest.glb"
seal = "a7c686bfdb7d004b133cfb8c0e535b5caf8daebb4ff439829e572f053269fcf9"
assert hashlib.sha256(src.read_bytes()).hexdigest() == seal
bpy.ops.import_scene.gltf(filepath=str(src))
chest, = [o for o in scene.objects if o.type=="MESH"]
bpy.context.view_layer.update()
base = chest.matrix_world.copy()
wall_xy = (109.5930,14.0150)  # Three.js world X/Z, local render origin.
before = (112.5930,17.0150)
after = (112.5930,17.6150)
yaw = -.1027041  # Same sign about Blender +Z after (x,y,z) -> (x,-z,y).
turn = Matrix.Rotation(yaw,4,"Z")

def stage(xz):
    return (xz[0]-wall_xy[0],wall_xy[1]-xz[1],0)

def mat(n,c,metal=0,rough=.66):
    a=bpy.data.materials.new(n)
    a.use_nodes=True
    p=a.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    return a

rust=mat("Band 6 half-wall proxy · burnt enamel",(.44,.123,.048),.35)
dark=mat("Deep concrete expansion joint",(.080,.097,.100),0,.86)
gray=[mat("Cast yard slab "+str(i),c,0,.72) for i,c in enumerate(
    [(.203,.226,.216),(.23,.247,.237),(.183,.209,.21),(.215,.231,.222)])]

def prism(n,p,d,m,turn=None,roundover=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o=bpy.context.object
    o.name=n
    o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if turn is not None:
        o.matrix_world=turn@o.matrix_world
    o.data.materials.append(m)
    if roundover:
        b=o.modifiers.new("Preview edge wear","BEVEL")
        b.width,b.segments=roundover,2
        o.modifiers.new("Face normals","WEIGHTED_NORMAL")
    return o

# The proxy is exact and not silently replaced with a remastered wall.
wall=prism("Archive half-wall main",(0,0,.55),(5,.8,1.1),rust,turn)
ret=prism("Archive half-wall return",(2.9,-1.1,.55),(.8,3,1.1),rust,turn)

def meshes(objs):
    vs,fs=[],[]
    dg=bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        o=ob.evaluated_get(dg)
        m=o.to_mesh()
        i=len(vs)
        vs.extend(o.matrix_world@v.co for v in m.vertices)
        fs.extend(tuple(i+j for j in p.vertices) for p in m.polygons)
        o.to_mesh_clear()
    return vs,BVHTree.FromPolygons(vs,fs)

rverts,rtree=meshes([ret])
_,wtree=meshes([wall])
wall_y=min((turn.inverted()@v).y for v in rverts)
assert abs(wall_y+2.6)<1e-5
report={}
for tag,point in (("archive",before),("offset",after)):
    chest.matrix_world=Matrix.Translation(stage(point))@base
    bpy.context.view_layer.update()
    vs,tree=meshes([chest])
    clearance=wall_y-max((turn.inverted()@v).y for v in vs)
    hits=len(tree.overlap(rtree))
    assert len(tree.overlap(wtree))==0
    assert abs(min(v.z for v in vs))<1e-5
    if tag=="archive":
        assert hits>0 and clearance<0,(hits,clearance)
    else:
        assert hits==0 and .09<clearance<.17,(hits,clearance)
    report[tag]={"three_xz_m":point,"blender_local_xyz_m":stage(point),
                 "return_intersecting_triangle_pairs":hits,
                 "signed_separation_along_return_axis_m":round(clearance,6)}

# Review stage only. Geological surroundings and the full band are not rebuilt.
prism("Stage substrate",(2,-2,-.18),(72,66,.24),dark)
for i in range(-5,7):
    for j in range(-5,5):
        prism("Stage concrete bay",(i*1.5,j*1.5,-.047),(1.484,1.484,.094),
              gray[(i*17+j*37)%4],roundover=.006)
world=bpy.data.worlds.new("Band 6 art look")
world.use_nodes=True
bg=world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.51,.63,.80,1)
bg.inputs[1].default_value=.55
scene.world=world
d=bpy.data.lights.new("Late industrial sun","SUN")
d.energy=2.65
d.angle=math.radians(5)
d.color=(1,.805,.62)
sun=bpy.data.objects.new(d.name,d)
scene.collection.objects.link(sun)
sun.rotation_euler=Vector((.42,.52,-1)).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(6.2,-6.25,1.7))
cam=bpy.context.object
scene.camera=cam
cam.data.lens=42
cam.rotation_euler=(Vector((2.54,-1.43,.535))-cam.location).to_track_quat("-Z","Y").to_euler()
scene.render.engine="CYCLES"
scene.cycles.samples=40
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.067
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x,scene.render.resolution_y=1340,880
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=91
for tag,point in (("archive",before),("offset",after)):
    chest.matrix_world=Matrix.Translation(stage(point))@base
    scene.render.filepath=str(out/f"nov24-e6-chest-{tag}.jpg")
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)
(out/"e6-chest-fit.json").write_text(json.dumps({
    "archive":"Raynos/project-wildshard-singleplayer@ce1cf050b3",
    "wall_three_xz_m":wall_xy,"wall_yaw_radians":yaw,"chest_sha256":seal,
    "positions":report,"camera_height_m":1.7,"native_placement":False},indent=2)+"\n")
