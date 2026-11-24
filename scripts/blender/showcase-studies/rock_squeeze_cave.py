"""W9a static cave liner, sectional camera and interior lighting proof.

Run with the regenerated climb-rock-editable.blend from west-climb-rock:
blender -b /abs/climb-rock-editable.blend -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/rock_squeeze_cave.py -- /abs/out
"""
import json
import os
import math
import random
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import output_directory

out = output_directory()
scene = bpy.context.scene
X, START = -200, -14
# Coordinate s is distance from the north source mouth. Blender Y is -world Z.
# Stations deliberately include both flush starts, the full 4 m squeeze and
# the shaft footprint. Art proposals, not navigation or capsule clearance.
profile = [
    (0,0,2.0,2.80), (2,-.545,2.15,3.10), (7,-1.909,2.3,3.35),
    (15,-4.091,2.05,3.18), (22,-6,3.35,4.40),
    (23,-6,3.50,4.80), (27,-6,3.10,4.80),
    (28,-6,1.03,1.10), (29.25,-6,1.02,1.10),
    (30.8,-6,1.04,1.10), (32,-6,1.03,1.10),
    (34,-6,2.95,3.90), (38,-6,2.78,3.60), (43,-4.636,2.40,3.32),
    (53,-1.909,2.25,3.24), (58,-.545,2.08,2.98), (60,0,2.0,2.80)
]
shaft_start, shaft_end = 23, 27
shaft_half_width = .59
shaft_center = START - (shaft_start+shaft_end)/2
def vectors(mesh):
    return [tuple(v.co) for v in mesh.vertices], [tuple(f.vertices) for f in mesh.polygons]
crag = next(o for o in scene.objects if "CLIMB | crag mesh" in o.name)
bench = [o for o in scene.objects if o.type == "MESH" and o.name.startswith("CLIMB | native lookout bench")]
assert len(bench)==10
cv, cf = vectors(crag.data)
bounds = [crag.matrix_world @ Vector(v) for v in cv]
crown = BVHTree.FromPolygons(bounds,cf,all_triangles=True)
tops = [crown.ray_cast(Vector((X+dx,shaft_center+dy,25)),Vector((0,0,-1)),20)[0]
        for dx in (-.9,0,.9) for dy in (-2.1,0,2.1)]
assert all(h is not None and abs(h.z-16)<.0001 for h in tops)
benchx = max((o.matrix_world@v.co).x for o in bench for v in o.data.vertices)
assert X-.9-benchx>7
# Retain a setback section of the exact donor crag silhouette as context, not
# as the actual terrain cut. Nothing in this script saves over the donor.
for o in tuple(scene.objects):
    if o not in [crag,*bench]:
        bpy.data.objects.remove(o,do_unlink=True)
crag.data = crag.data.copy()
bm = bmesh.new()
bm.from_mesh(crag.data)
bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
    dist=.0001, plane_co=(X-3.6,0,0), plane_no=(1,0,0), clear_outer=True)
bm.to_mesh(crag.data)
bm.free()
assert len(crag.data.polygons) > 200

def mat(name, dark, light, scale=4, emit=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*light,1); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; p=n.get("Principled BSDF")
    p.inputs["Roughness"].default_value=.84
    co=n.new("ShaderNodeTexCoord"); noise=n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=scale
    l.new(co.outputs["Object"],noise.inputs["Vector"])
    ramp=n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(*dark,1)
    ramp.color_ramp.elements[1].position=.79; ramp.color_ramp.elements[1].color=(*light,1)
    l.new(noise.outputs["Fac"],ramp.inputs["Fac"]); l.new(ramp.outputs["Color"],p.inputs["Base Color"])
    grit=n.new("ShaderNodeTexNoise"); grit.inputs["Scale"].default_value=32
    l.new(co.outputs["Object"],grit.inputs["Vector"])
    bump=n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.23
    bump.inputs["Distance"].default_value=.049
    l.new(grit.outputs["Fac"],bump.inputs["Height"]); l.new(bump.outputs["Normal"],p.inputs["Normal"])
    if emit: p.inputs["Emission Color"].default_value=(*light,1); p.inputs["Emission Strength"].default_value=emit
    return m

slate=mat("Cold wet basalt",(.029,.049,.052),(.108,.157,.158),.91)
shale=mat("Oxide veins",(.064,.038,.026),(.187,.111,.069),1.22)
sand=mat("Weathered cut sandstone",(.077,.055,.035),(.301,.208,.126),1.52)
floor=mat("Dark worn shale",(.03,.034,.025),(.158,.156,.113),1.66)
quartz=mat("Low light teal inclusions",(.072,.230,.203),(.181,.66,.49),4,1.4)

def mesh(name, verts, faces, material, group=None):
    m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update()
    o=bpy.data.objects.new(name,m); scene.collection.objects.link(o)
    for a in material: m.materials.append(a)
    if group is not None:
        for f,i in zip(m.polygons,group,strict=True): f.material_index=i
    return o

def yz(s): return START-s
def ring(s,z,w,h):
    # Level floor. Exact rise and width through the central tight band.
    return [(X+a,yz(s),z+b) for a,b in [
      (-w,0),(-w*.91,h*.42),(-w*.71,h*.82),(-shaft_half_width,h),
      (0,h),(shaft_half_width,h),(w*.71,h*.82),(w*.91,h*.42),(w,0),(0,0)]]
verts=[v for p in profile for v in ring(*p)]
n=10
# One ring liner split into near/far for the section camera only.
liners=[]; all_faces=[]
for name,edges in [("Far half",range(5)),("Near half",range(5,10))]:
    faces=[]; ids=[]
    for i,(p,q) in enumerate(zip(profile,profile[1:])):
        for j in edges:
            if p[0]==shaft_start and q[0]==shaft_end and j in (3,4):
                continue
            k=(j+1)%n
            faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
            ids.append(3 if j in (8,9) else (2 if i in (0,len(profile)-2) else (1 if (i*7+j)%8<2 else 0)))
    all_faces+=faces
    liners.append(mesh(name+" | continuous hollow liner",verts,faces,[slate,shale,sand,floor],ids))
# Roof opening shares the two parallel roof edges and expands to an exact
# tested X/Y footprint through the presentation crown plane.
shaft=[]; sf=[]
rings=[(-1.2,.59,2.),(2,.70,1.83),(7,.64,1.65),(12,.79,1.9),(16,.9,2.1)]
for h,w,l in rings:
    shaft.extend([(X+dx,shaft_center+dy,h) for dx,dy in [(-w,l),(-w,-l),(w,-l),(w,l)]])
for i in range(len(rings)-1):
    for j in range(4):
        k=(j+1)%4
        sf.append((i*4+j,i*4+k,(i+1)*4+k,(i+1)*4+j))
sp=mesh("Shaft lining | four open walls",shaft,sf,[slate,shale],[i%3==1 for i in range(len(sf))])
# End trim wraps each continuous ring opening; it does not use or touch
# the two original blind recess modules.
for s,z,w,h,sign in ((0,0,2,2.8,1),(60,0,2,2.8,-1)):
    a=ring(s,z,w,h)
    b=[(X+(x-X)*1.16,y+sign*.38,z+(v-z)*1.16+.11) for x,y,v in a]
    mesh("Hollow rock lip | "+str(s),a+b,[(j,j+1,j+11,j+10) for j in range(8)],[sand,shale],[0,1,0,0,1,0,1,0])
# Small crystals, out of the center path.
for i,(dx,s,h,scale) in enumerate([(-2,21.6,-5.94,.51),(-2.28,22.1,-5.94,.37),
    (-2.42,22.26,-5.89,.53),(2.5,25.3,-5.91,.40),(-2.1,34.2,-5.94,.40),(-2.32,34.52,-5.96,.31)]):
    x,y=X+dx,yz(s)
    outer=[(x+math.cos(j*math.tau/5)*scale*.28,y+math.sin(j*math.tau/5)*scale*.28,h) for j in range(5)]
    mesh(f"Quartz fleck {i}",outer+[(x+.18*scale,y+.17*scale,h+scale)],
         [(j,(j+1)%5,5) for j in range(5)],[quartz])
# Secondary silhouettes keep the landing readable without narrowing the checked
# centerline. These meshes are visual dressing, not part of the liner proof.
rng=random.Random(795)
for i in range(38):
    station=rng.uniform(22,27) if i<28 else rng.uniform(33.8,37)
    dx=rng.choice((-1,1))*rng.uniform(1.94,2.75)
    radius=rng.uniform(.11,.46); h=rng.uniform(.08,.35)
    x,y=X+dx,yz(station)
    poly=[(x+math.cos(j*math.tau/6)*radius,y+math.sin(j*math.tau/6)*radius,-6-.03)
          for j in range(6)]
    peak=(x+rng.uniform(-.1,.1),y+rng.uniform(-.09,.09),-6+h)
    mesh(f"Loose shale {i:02}",poly+[peak],[(j,(j+1)%6,6) for j in range(6)],[slate if i%3 else shale])
# Validate the liner, independently of the artwork camera. Standing-height
# and crouch fit, floor collisions, and live alignment remain runtime work.
route=BVHTree.FromPolygons([Vector(v) for v in verts],all_faces)
checks=[]
for s,z,w,h in profile[1:-1]:
    o=Vector((X,yz(s),z+.4))
    down=route.ray_cast(o,Vector((0,0,-1)),6)[0]
    assert down and abs(down.z-z)<.001
    if 28<=s<=32:
        up=route.ray_cast(o,Vector((0,0,1)),4)[0]
        assert up and abs(up.z-z-1.1)<.001
    checks.append([s,z,w,h])
full=BVHTree.FromPolygons([Vector(v) for v in verts+shaft],all_faces+[tuple(i+len(verts) for i in f) for f in sf])
assert full.ray_cast(Vector((X,shaft_center,-5.6)), Vector((0,0,1)),23)[0] is None
trim=[o for o in scene.objects if o.name.startswith("Hollow rock lip")]
for o in trim:
    v,f=vectors(o.data); bvh=BVHTree.FromPolygons([Vector(p) for p in v],f)
    for y,d in ((-13, -1),(-75,1)):
        assert bvh.ray_cast(Vector((X,y,1.1)),Vector((0,d,0)),1.6)[0] is None
(out/"w9a-rock-squeeze-study.json").write_text(json.dumps({
    "readiness":"static cave liner and alignment section; proposed art dimensions, not runtime cuts or collision",
    "north_x_y_z_world":[X,0,14],"south_x_y_z_world":[X,0,74],
    "bench_source_world":[-210,16,40],"shaft_world_center":[X,16,-shaft_center],
    "shaft_crown_sample_count":len(tops),"shaft_clear_vertical_center":True,
    "shaft_bottom_half_size_m":[.59,2],"shaft_top_half_size_m":[.9,2.1],
    "minimum_x_clearance_shaft_to_bench_m":round(X-.9-benchx,3),
    "ramp_run_m":22,"ramp_angle_deg":round(math.degrees(math.atan2(6,22)),3),
    "squeeze_station_interval_m":[28,32],"candidate_clear_height_m":1.1,
    "section_donor_is_clipped_at_world_x_m":X-3.6,"profile":profile,
    "validated_floor_stations":len(checks)},indent=2)+"\n")

def area(name,p,target,power,size,color,shape="DISK",width=None):
    d=bpy.data.lights.new(name,"AREA"); d.energy=power; d.shape=shape; d.size=size
    if width: d.size_y=width
    d.color=color
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o)
    o.location=p; o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    return o
world=bpy.data.worlds.new("West limestone dawn"); world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.15,.22,.26,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.45
scene.world=world
cut_lights=[
    area("Section key",(-168,-37,31),(-204,-45,1),76000,29,(.83,.92,1)),
    area("Section warm edge",(-190,-75,18),(-202,-44,3),33000,20,(1,.68,.43))]
cave_bounce=area("Interior reflected key",(-200.88,-38,-2.16),(-198.1,-42,-5.12),
                 90,2.2,(.52,.76,1))
edge=area("Wet wall grazing",(-198.2,-39,-4.35),(-202.8,-41,-4.3),29,1.7,(1,.52,.28))
shaftlight=area("Cool shaft key",(X,shaft_center,14),(X,shaft_center,-6),4100,1.05,(.60,.81,1),"RECTANGLE",3.4)
area("Northern bounce",(X,-13,2.6),(X,-30,-3),1450,3,(1,.68,.40))
area("Southern bounce",(X,-75,2.6),(X,-60,-4),1050,3,(1,.77,.56))
data=bpy.data.cameras.new("W9a lab"); camera=bpy.data.objects.new("W9a lab",data)
scene.collection.objects.link(camera); scene.camera=camera
scene.render.engine="CYCLES"; scene.cycles.samples=38; scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"; scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"; scene.render.image_settings.quality=89
for name,p,target,res,lens in ([] if os.getenv("WILDSHARD_CAVE_SKIP_RENDER") == "1" else [
    ("section",(-140,-44,19),(-202,-44,4.9),(1450,710),74),
    ("interior",(-198.6,-35.75,-4.37),(-200.2,-44.7,-4.9),(1000,1080),25)]):
    section=name=="section"
    liners[1].hide_render=section # keep near floor and right wall for interior
    crag.hide_render=not section
    for o in bench+cut_lights: o.hide_render=not section
    for o in (cave_bounce,edge): o.hide_render=section
    world.node_tree.nodes["Background"].inputs[1].default_value=.45 if section else .055
    data.type="ORTHO" if section else "PERSP"; data.ortho_scale=65; data.lens=lens
    camera.location=p; camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/f"nov23-rock-cave-{name}.jpg")
    bpy.ops.render.render(write_still=True)
