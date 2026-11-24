"""Static Titan bowl environment framing study. No actor, timeline, or native assets."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

S = bpy.context.scene
O = output_directory()
D = Path(__file__).resolve().parents[3] / "public/assets/wildshard-art/wsc-scene-008-titan-bowl.glb"
PIN = "cd4b20016133bab16940d85f0b3319aecd19708626a5fe9cdb35f68f83a92021"
assert hashlib.sha256(D.read_bytes()).hexdigest() == PIN
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(D))
bpy.context.view_layer.update()
meshes = [o for o in S.objects if o.type == "MESH"]
all_v, all_f = [], []
for o in meshes:
    start = len(all_v)
    all_v.extend(o.matrix_world @ v.co for v in o.data.vertices)
    all_f.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
bvh = BVHTree.FromPolygons(all_v, all_f)


def polar(r, angle, z):
    t = math.radians(angle)
    return (r*math.cos(t), -r*math.sin(t), z)


def aim(o, target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()


def lamp(name, pos, target, energy, size, color):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.size, d.color, d.shape = energy, size, color, "DISK"
    o = bpy.data.objects.new(name,d)
    S.collection.objects.link(o)
    o.location=pos
    aim(o,target)


for i,t in enumerate((28,152,208,332)):
    lamp("Bridge fixture",polar(64.9,t,24.9),polar(21,t+(-8 if i%2 else 8),0),
         29000,8,(.61,.79,1))
lamp("Checkpoint bounce",(0,-48,11),(0,-63,2),26000,14,(1,.56,.30))
lamp("Cool skylight",(-25,16,59),(0,0,8),59000,65,(.72,.86,1))
lamp("Mechanical bounce",(36,26,31),(8,6,2),21000,17,(1,.59,.34))
lamp("Blue edge",(-41,-10,32),(0,0,0),19500,20,(.47,.71,1))


def surface(name, color, metal, rough, emit=0):
    m = bpy.data.materials.new(name)
    m.use_nodes=True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*color,1)
    n.inputs["Roughness"].default_value=rough
    n.inputs["Metallic"].default_value=metal
    n.inputs["Emission Color"].default_value=(*color,1)
    n.inputs["Emission Strength"].default_value=emit
    return m


# A simple dimensions overlay, not the crate pile or Titan model.
aqua = surface("15 m tape | teal",(.045,.68,.80),.06,.78,.59)
amber = surface("6 m tape | amber",(.93,.41,.086),.05,.77,.54)


def guide(x, h, m):
    def beam(location, dims):
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        o=bpy.context.object
        o.name=f"{h} m scale-only guide"
        o.dimensions=dims
        o.data.materials.append(m)
    beam((x,0,h/2),(.42,.42,h))
    for z in (0.14,h):
        beam((x,0,z),(2.05,.42,.33))
    for z in range(3,h,3):
        beam((x,0,z),(1.08,.32,.20))


guide(-7,6,amber)
guide(4,15,aqua)

world=bpy.data.worlds.new("Constant working light, camera backdrop separate")
world.use_nodes=True
nodes=world.node_tree.nodes
links=world.node_tree.links
light=nodes.get("Background")
light.inputs[0].default_value=(.119,.205,.326,1)
light.inputs[1].default_value=.42
sky=nodes.new("ShaderNodeBackground")
sky.inputs[0].default_value=(.037,.083,.135,1)
sky.inputs[1].default_value=.54
path=nodes.new("ShaderNodeLightPath")
mix=nodes.new("ShaderNodeMixShader")
links.new(path.outputs["Is Camera Ray"],mix.inputs[0])
links.new(light.outputs[0],mix.inputs[1])
links.new(sky.outputs[0],mix.inputs[2])
links.new(mix.outputs[0],nodes.get("World Output").inputs[0])
S.world=world

# The staged underlay is the original presentation idea, not shipped scenery.
underlay=surface("Non-exported presentation underlay",(.035,.053,.073),.12,.73)
bpy.ops.mesh.primitive_plane_add(size=1500,location=(0,0,-6.05))
ground=bpy.context.object
ground.name="Preview underlay | outside GLB"
ground.data.materials.append(underlay)

C=bpy.data.cameras.new("30 m stand height")
S.camera=bpy.data.objects.new(C.name,C)
S.collection.objects.link(S.camera)
C.sensor_fit="VERTICAL"
C.sensor_height=24
C.clip_end=1750
C.lens=24/(2*math.tan(math.radians(55)/2))
S.render.engine="CYCLES"
S.cycles.samples=38
S.cycles.use_denoising=False
S.render.resolution_percentage=100
S.render.image_settings.file_format="JPEG"
S.render.image_settings.quality=92
S.view_settings.view_transform="AgX"
S.view_settings.look="AgX - Medium High Contrast"

cameras=(
    ("north-portrait",(-3.4,63.91,30),(0,0,10),(804,1748),55),
    ("angled-portrait",(15,62.2,30),(0,-3,10),(804,1748),55),
    ("north-wide",(-3.4,63.91,30),(0,0,10),(1400,940),55),
    ("floor-first-portrait",(-3.4,63.91,30),(0,0,0),(804,1748),45),
)
report={}


def inspect(label, dims, fov):
    bpy.context.view_layer.update()
    cam=S.camera
    raw=C.view_frame(scene=S)
    left,right=min(p.x for p in raw),max(p.x for p in raw)
    bottom,top=min(p.y for p in raw),max(p.y for p in raw)
    z=raw[0].z
    rotation=cam.matrix_world.to_quaternion()
    # Sample points uniformly in pixel space. This is geometric line of sight
    # to donor only, not a measured pixel segmentation of rendered materials.
    nx,ny=72,100
    missing=[]
    for yy in range(ny):
        misses=0
        for xx in range(nx):
            v=rotation @ Vector((left+(right-left)*(xx+.5)/nx,
                                 bottom+(top-bottom)*(yy+.5)/ny,z))
            hit=bvh.ray_cast(cam.location,v.normalized(),350)[0]
            misses += hit is None
        missing.append(misses)
    h=math.degrees(2*math.atan(math.tan(math.radians(fov/2))*dims[0]/dims[1]))
    samples={}
    for key,p in {"6m_base":(-7,0,.2),"6m_tip":(-7,0,6),
                  "15m_base":(4,0,.2),"15m_tip":(4,0,15),
                  "south_checkpoint_inside_mouth":(0,-53,4.1),
                  "south_checkpoint_back_panel":(0,-64,4.0)}.items():
        v=Vector(p)
        screen=world_to_camera_view(S,cam,v)
        ray=v-cam.location
        hit=bvh.ray_cast(cam.location,ray.normalized(),max(0,ray.length-.21))[0]
        samples[key]={"xy":[round(screen.x,4),round(screen.y,4)],
                      "occluded":hit is not None}
    for key in ("6m_base","6m_tip","15m_base","15m_tip"):
        assert all(0<x<1 for x in samples[key]["xy"]) and not samples[key]["occluded"]
    down=bvh.ray_cast(cam.location,Vector((0,0,-1)),50)[3]
    assert down is not None, (label,list(cam.location))
    report[label]={"camera_xyz":[round(x,3) for x in cam.location],"raster":dims,"vertical_fov_deg":fov,"horizontal_fov_deg":round(h,3),
                   "sample_grid":[nx,ny],"no_mesh_ray_fraction":round(sum(missing)/(nx*ny),4),
                   "top_quarter_no_mesh_ray_fraction":round(sum(missing[-25:])/(nx*25),4),
                   "screen_guides":samples,
                   "camera_clearance_vertical_m":round(down,3)}
    for key, a in report[label]["screen_guides"].items():
        assert len(a["xy"])==2,key


def render(name, on):
    ground.hide_render=not on
    sky.inputs[1].default_value=.54 if on else 0
    S.render.filepath=str(O/f"nov24-titan-stands-{name}.jpg")
    bpy.ops.render.render(write_still=True)


for name,pos,target,dims,fov in cameras:
    C.lens=24/(2*math.tan(math.radians(fov)/2))
    S.camera.location=pos
    aim(S.camera,target)
    S.render.resolution_x,S.render.resolution_y=dims
    inspect(name,dims,fov)
    if os.environ.get("WSC_STANDS_RAYS_ONLY")=="1" or os.environ.get("WSC_STANDS_RENDER_ONLY",name)!=name:
        continue
    if name=="north-portrait":
        render("north-backdrop",True)
        render("north-export-boundary",False)
    elif name=="north-wide":
        render("wide",True)
    elif name=="angled-portrait":
        render("oblique",True)
    else:
        render("floor-first",True)

(O/"titan-stands-review-proof.json").write_text(json.dumps({
    "scope":"Static bowl-only art and scale guides; no actor, timeline, cutscene, reward, or native placement.",
    "axis_test_x0_y64_z30_has_stand_below":bvh.ray_cast(Vector((0,64,30)),Vector((0,0,-1)),50)[0] is not None,
    "donor_sha256":PIN,"shots":report,
},indent=2)+"\n")
