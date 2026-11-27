"""Fit-test the ride samples against the rebuilt W08 visual donor and render its new trolley."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--donor", type=Path, required=True)
parser.add_argument("--ride", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--proof-only", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo/"scripts/blender/showcase-studies"))
from common import clear_scene, export

clear_scene()
bpy.ops.import_scene.gltf(filepath=str(args.donor))
scene = bpy.context.scene
ride = json.loads(args.ride.read_text())

def bl(p):
    return Vector((p[0], -p[2], p[1]))


def render_bvh():
    vertices, faces, hosts = [], [], []
    for o in scene.objects:
        # The reference wire is intentionally kept out of swept-body floor rays.
        if o.type != "MESH" or o.name.startswith("W08 illustrative cable"):
            continue
        box = [o.matrix_world @ Vector(p) for p in o.bound_box]
        if (max(p.x for p in box)<-214 or min(p.x for p in box)>-113 or
            max(p.y for p in box)<15 or min(p.y for p in box)>35):
            continue
        i=len(vertices)
        vertices.extend(o.matrix_world @ v.co for v in o.data.vertices)
        faces.extend(tuple(i+j for j in p.vertices) for p in o.data.polygons)
        hosts.extend([o.name]*len(o.data.polygons))
    return BVHTree.FromPolygons(vertices, faces), hosts


bvh, hosts = render_bvh()
a,b=map(bl,[[-212,45,-34],[-115,14,-16.5]])
heading=b-a
side=Vector((-heading.y,heading.x,0)).normalized()
front=Vector((heading.x,heading.y,0)).normalized()
offsets=[Vector((0,0,0))]+[.26*(math.cos(i*math.tau/8)*front+math.sin(i*math.tau/8)*side) for i in range(8)]
landing=None
minimum=float("inf")
wall=float("inf")
for frame in ride["frames"]:
    pos=bl(frame["rider"])
    for i,offset in enumerate(offsets):
        # 1.70 m high sample, paired with radial points. This is a visual triangle test, not character physics.
        at=pos+offset+Vector((0,0,1.70))
        p,n,j,_ = bvh.ray_cast(at,Vector((0,0,-1)),at.z+1.0)
        assert p is not None, (frame["tick"],i)
        gap=pos.z-p.z
        minimum=min(minimum,gap)
        assert gap>.025 and n is not None, (frame["tick"],i,round(gap,4),hosts[j])
        if abs(pos.x+128)<.70:
            wall=min(wall,gap)
        if not frame["carried"]:
            assert "PROP-035" in hosts[j] and n.z>.995, (i,hosts[j],n)
            if i==0:
                landing=[round(p.z,4),round(gap,4),hosts[j]]
assert math.isfinite(wall) and landing
receipt={"scope":"Engine driver and art clearance sample only; no physics capsule or native level proof.",
 "donor_sha256":hashlib.sha256(args.donor.read_bytes()).hexdigest(),
 "donor_baseline_signature":["6e6b1692565a314162d3861223ab3454e9475e23bb1a2e01a88a14e76be6722f",2580],
 "samples":len(ride["frames"])*len(offsets), "visual_minimum_m":round(minimum,4),
 "wall_visual_minimum_m":round(wall,4),"landing":landing,
 "engine":ride["engine"],"row":ride["row"],"plan_span_m":round(ride["plan_span_m"],4),
 "wire_chord_m":round(ride["length_m"],4), "ride_ticks":ride["final"]["tick"],
 "seconds":round(ride["seconds"],4),"observed_max_mps":round(ride["maxSpeed_mps"],4),
 "sampled_release_step_m":round((bl(ride["frames"][-1]["rider"])-bl(ride["frames"][-2]["rider"])).length,4),
 "midpoint_restore_exact":ride["restoredExactly"]}
(out/"fit.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("W08 ride fit",json.dumps(receipt),flush=True)
if args.proof_only:
    raise SystemExit(0)


def mat(name,c,m=.0,r=.4, glow=0):
    a=bpy.data.materials.new(name)
    a.diffuse_color=(*c,1)
    a.use_nodes=True
    bs=a.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*c,1)
    bs.inputs["Metallic"].default_value=m
    bs.inputs["Roughness"].default_value=r
    bs.inputs["Emission Color"].default_value=(*c,1)
    bs.inputs["Emission Strength"].default_value=glow
    return a


yellow=mat("Trolley | worn ochre",(.63,.285,.041),.38,.42)
steel=mat("Trolley | blackened steel",(.047,.055,.056),.68,.31)
bright=mat("Trolley | turned bosses",(.38,.40,.38),.78,.23)
grip=mat("Trolley | graphite grip",(.024,.029,.028),0,.70)
teal=mat("Trolley | cyan status sliver",(.022,.45,.41),.1,.42,.55)
parts=[]


def block(name,p,dim,material,edge=.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o=bpy.context.object
    o.name=name
    o.dimensions=tuple(dim)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new("Caught edges","BEVEL")
    mod.width=min(edge, min(dim)*.40)
    mod.segments=1
    bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(material)
    parts.append(o)
    return o


def rod(name,a,b,r,material,sides=10):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=r,depth=(b-a).length,location=(a+b)*.5)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(material)
    parts.append(o)
    return o


# Authoring origin is wire contact, +X lies along the wire, +Z up. Six close components share the handgrip geometry.
for yy in (-.142,.142):
    block("Upper guard lip", (0,yy,.128),(.49,.044,.144),yellow,.023)
    block("Carrier web", (0,yy,-.10),(.38,.040,.24),yellow,.020)
    block("Inset teal reflector", (0,yy*1.165,-.105),(.204,.008,.026),teal,.003)
    for x in (-.176,.176):
        rod("Wheel washer boss",(x,yy-.031,.10),(x,yy+.031,.10),.049,bright)
for x in (-.176,.176):
    # Paired wheel flanges with a slightly smaller center barrel define a visual cable channel.
    for yy in (-.081,.081):
        rod("Guide wheel flange",(x,yy-.023,.10),(x,yy+.023,.10),.113,steel,12)
    rod("Central groove",(x,-.060,.10),(x,.060,.10),.080,steel,12)
    rod("Beaded through axle",(x,-.197,.10),(x,.197,.10),.030,bright)
block("Reinforced hanger yoke", (0,0,-.198),(.24,.25,.10),steel,.021)
for x in (-.092,.092):
    rod("Handle stirrup",(x,0,-.21),(x*1.82,0,-.52),.028,bright)
rod("Handle center",(-.205,0,-.52),(.205,0,-.52),.050,grip,12)
for x in (-.222,.222):
    rod("Turned end stop",(x-.025,0,-.52),(x+.025,0,-.52),.058,steel,12)
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
ob=bpy.context.object
ob.name="W08 ochre cable trolley"
ob.data.name="W08 trolley mesh"
scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
model=out/"w7b-ochre-cable-trolley.glb"
export([ob],model)
ob.data.calc_loop_triangles()
print(model.name,model.stat().st_size,len(ob.data.loop_triangles),flush=True)

# Use the engine's sampled tether positions and yaw. Pitch is a presentation-only correction:
# local X follows the cable tangent; no native saddle, hand IK, player or balance pose is claimed.
first=ride["frames"][48]
near_end=ride["frames"][-19]
last=ride["frames"][-1]
poses=[("trolley-launch",first),("trolley-landing",near_end)]
blue=mat("Test marker | finish",(.02,.69,.55),.1,.35,.8)
scene.render.engine="CYCLES"
scene.cycles.samples=30
scene.cycles.use_denoising=False
scene.render.resolution_x,scene.render.resolution_y=1460,930
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=92
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.25,.39,.58,1)
bg.inputs["Strength"].default_value=.48
bpy.ops.object.light_add(type="SUN",rotation=(.47,-.49,-.42))
sun=bpy.context.object
sun.data.energy=3.3
sun.data.color=(1,.885,.76)
sun.data.angle=.13
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
for name,frame in poses:
    target=bl(frame["trolley"])
    t=frame["s"]/ride["length_m"]
    span=b-a
    span.z -= 4*1.2*(1-2*t)
    X=span.normalized()
    Y=Vector((-X.y,X.x,0)).normalized()
    Z=X.cross(Y)
    ob.matrix_world=Matrix.Translation(target) @ Matrix((X,Y,Z)).transposed().to_4x4()
    cam.data.clip_end=480
    if name.endswith("launch"):
        cam.location=target-front*1.9+side*1.4+Vector((0,0,.25))
        aim=target+front*.40+Vector((0,0,-.27))
        cam.data.lens=33
    else:
        at=bl(last["rider"])
        # A locator makes the native driver's release visible without inventing a playable character.
        bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=5,
            location=(at.x,at.y,12.746+.021),major_radius=.26,minor_radius=.017)
        bpy.context.object.name="Debug | sampled release"
        bpy.context.object.data.materials.append(blue)
        cam.location=target-front*3.3+side*2.6+Vector((0,0,.64))
        aim=target+front*1.85+Vector((0,0,-.49))
        cam.data.lens=35
    cam.rotation_euler=(aim-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(out/f"{name}.jpg")
    bpy.ops.render.render(write_still=True)
