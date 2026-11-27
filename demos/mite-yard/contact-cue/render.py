"""Depth-aware portrait framing test for the contact cue. Uses existing art only."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index("--")+1:]
out=Path(args[0]); out.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[3]
donor=repo/"public/assets/wildshard-art/wsc-actor-002-pallet-jack-study.glb"
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(donor))
s=bpy.context.scene
parts=[o for o in s.objects if o.type=="MESH"]

def data(obs):
    pts=[]; faces=[]
    for o in obs:
        n=len(pts)
        pts.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(n+i for i in f.vertices) for f in o.data.polygons)
    return pts,faces

p,f=data(parts)
actor=BVHTree.FromPolygons(p,f)
tgt=Vector((.0,0,.96))
contact,normal,_,_=actor.ray_cast(Vector((.15,-4,1.09)),Vector((0,1,0)),5)
assert contact is not None and normal.y<-.25,(contact,normal)

def xyz(v):return [v.x,v.z,-v.y]
def bl(v):return Vector((v[0],-v[2],v[1]))
event=dict(point=xyz(contact),normal=xyz(normal),tangent=[1,.39,0])
frames=[0,1,2,3,4,6,8,10]
module=(Path(__file__).resolve().parent/"contact.mjs").as_uri()
program=f'import {{sampleContact}} from {json.dumps(module)};console.log(JSON.stringify({frames}.map(f=>sampleContact(f/60,{json.dumps(event)}))))'
items=json.loads(subprocess.check_output(["node","--input-type=module","-e",program],text=True))

faces=[(0,2,4),(4,2,1),(1,2,5),(5,2,0),(4,3,0),(1,3,4),(5,3,1),(0,3,5)]
def spark_data(row):
    center=bl(row["center"])
    y=bl(row["axis"]).normalized()
    q=Vector((0,0,1)).rotation_difference(y)
    x=q@Vector((1,0,0))
    z=q@Vector((0,-1,0))
    a,b=row["radius"],row["reach"]
    return [center+x*a,center-x*a,center+y*b,center-y*b,center+z*a,center-z*a]
def spark_tree(frame):
    p=[];f=[]
    for row in frame:
        k=len(p); p+=spark_data(row); f += [tuple(k+i for i in face) for face in faces]
    return BVHTree.FromPolygons(p,f) if p else None

# Deliberately overbroad, explicit negative control, not a capture of Fable's shader.
widecenter=contact+Vector((0,-.36,0))
def wide_distance(origin,d):
    oc=widecenter-origin
    t=oc.dot(d); discriminant=.64*.64-oc.length_squared+t*t
    return math.inf if discriminant<0 else t-math.sqrt(discriminant)
trees=[spark_tree(v) for v in items]
results=[]
vFov=math.radians(50)
width,height=402,874
for distance in [3.7,5.5]:
    for heading in [-27,0,27]:
        a=math.radians(heading)
        origin=tgt+Vector((math.sin(a)*distance,-math.cos(a)*distance,1.05))
        look=(tgt-origin).normalized();right=look.cross(Vector((0,0,1))).normalized();up=right.cross(look)
        count=wide=0
        blocked=[0]*len(trees)
        shown=[0]*len(trees)
        for row in range(2,height,4):
            v=(1-2*row/height)*math.tan(vFov/2)
            for col in range(2,width,4):
                u=(2*col/width-1)*math.tan(vFov/2)*width/height
                d=(look+right*u+up*v).normalized()
                hit,_,_,depth=actor.ray_cast(origin,d)
                if hit is not None:
                    count+=1
                    wide+=int(0<wide_distance(origin,d)<depth)
                else:
                    depth=20
                for i,tree in enumerate(trees):
                    if not tree: continue
                    k,_,_,_=tree.ray_cast(origin,d,depth)
                    shown[i]+=int(k is not None)
                    blocked[i]+=int(k is not None and hit is not None)
        assert count>150
        results.append(dict(distance_m=distance,yaw_deg=heading,actor_samples=count,
            broad_control_overlap_pct=round(100*wide/count,2),
            candidate_overlap_pct=[round(100*k/count,2) for k in blocked],
            visible_effect_ray_samples=shown))
assert min(v["broad_control_overlap_pct"] for v in results)>15,results
assert min(max(v["visible_effect_ray_samples"][:3]) for v in results)>8,results
assert max(max(v["candidate_overlap_pct"]) for v in results)<2,results
assert max(max(v["candidate_overlap_pct"]) for v in results)>.25
(out/"wsc-portrait-contact-proof.json").write_text(json.dumps(dict(
    scope="Geometric silhouette overlap on a fixed existing Pallet Jack art mesh, not renderer luminance or live Fable combat.",
    donor_sha256=digest(donor),pixels=[width,height],pixel_sample_spacing=4,
    vertical_fov_deg=50,contact_three=event,frame_times_60hz=frames,
    broad_control="synthetic 0.64 m radius sphere in front of the contact, not Fable",
    candidate=results,
),indent=2)+"\n")
if "--proof-only" in args:raise SystemExit(0)

def emission(name,color,gain):
    m=bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear()
    out=nodes.new("ShaderNodeOutputMaterial");src=nodes.new("ShaderNodeEmission")
    src.inputs[0].default_value=(*color,1);src.inputs[1].default_value=gain
    m.node_tree.links.new(src.outputs[0],out.inputs[0])
    return m
def material(name,color,metal,rough):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metal;bs.inputs["Roughness"].default_value=rough
    return m
bpy.ops.mesh.primitive_plane_add(size=90)
bpy.context.object.data.materials.append(material("Cool slate",(.076,.103,.121),.05,.78))
s.world=bpy.data.worlds.new("Warm dusk");s.world.use_nodes=True
bg=s.world.node_tree.nodes.get("Background");bg.inputs[0].default_value=(.29,.45,.63,1);bg.inputs[1].default_value=.39
def aim(o,t):o.rotation_euler=(t-o.location).to_track_quat("-Z","Y").to_euler()
for name,power,location,color,size in [
    ("Warm key",490,(2,-3.8,4.5),(1,.73,.49),3.1),("Cold rim",555,(-2,2,3.6),(.34,.74,1),2.4),
    ("Soft face fill",110,(-3,-2,2.8),(.63,.83,1),3.1)]:
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.color=color;d.shape="DISK";d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=location;aim(o,tgt)
bpy.ops.object.camera_add(location=(1.57,-3.36,2.01))
cam=bpy.context.object;s.camera=cam;aim(cam,tgt)
cam.data.sensor_fit="VERTICAL";cam.data.lens=cam.data.sensor_height/(2*math.tan(vFov/2))
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.062
s.render.resolution_x=width*2;s.render.resolution_y=height*2
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=95
for index,name in ((2,"contact"),(5,"recovery")):
    obs=[]
    for i,row in enumerate(items[index]):
        m=bpy.data.meshes.new(f"Contact facet {i}");m.from_pydata(spark_data(row),[],faces);m.update()
        o=bpy.data.objects.new(m.name,m);s.collection.objects.link(o);obs.append(o)
        m.materials.append(emission(m.name,row["color"],row["gain"]))
    s.render.filepath=str(out/f"portrait-{name}.jpg")
    bpy.ops.render.render(write_still=True)
    for o in obs:bpy.data.objects.remove(o,do_unlink=True)
