"""E10a arrival lobby and return pedestal. Authored models, not the interior host."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
clear_scene()
scene=bpy.context.scene
repo=Path(__file__).resolve().parents[3]
door=repo/"public/assets/wildshard-art/wsc-prop-063-round-vault-bulkhead.glb"
before=hashlib.sha256(door.read_bytes()).hexdigest()
assert before=="25db93c5d45901a6599674ea857982700f57705c1b171e23978140537e41eedf"


def material(name,c,metal=0,r=.62,e=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*c,1);m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*c,1)
    b.inputs["Metallic"].default_value=metal
    b.inputs["Roughness"].default_value=r
    b.inputs["Emission Color"].default_value=(*c,1)
    b.inputs["Emission Strength"].default_value=e
    return m


black=material("E10a dark seam",(.014,.021,.027),.32)
navy=material("E10a pressure-blue enamel",(.055,.101,.123),.3)
iron=material("E10a machined graphite",(.085,.108,.113),.58,.38)
slate=[material("E10a cast tread "+str(i),(v,v*1.06,v*1.13),.24) for i,v in enumerate((.093,.112,.135))]
bronze=material("E10a weathered copper",(.37,.149,.055),.48,.46)
chalk=material("E10a pale wayfinding",(.65,.67,.55),.05,.55,.16)
cyan=material("E10a cyan channel",(.018,.54,.68),.1,.32,1.0)
amber=material("E10a amber aisle",(.78,.239,.036),.15,.32,.85)


def box(label,p,d,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=label
    o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        md=o.modifiers.new("Machined corners","BEVEL")
        md.width=min(bevel,min(d)*.39)
        md.segments=1
        bpy.ops.object.modifier_apply(modifier=md.name)
    return o


def beam(label,a,b,width,depth,m,bevel=.02):
    a,b=Vector(a),Vector(b)
    p=box(label,(a+b)*.5,(width,depth,(a-b).length),m,bevel)
    p.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    return p


def rod(label,p,r,dep,m,n=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=dep,location=p,rotation=(math.pi/2,0,0))
    a=bpy.context.object;a.name=label;a.data.materials.append(m)
    return a


def line_text(label,at,size,paint,align="CENTER"):
    data=bpy.data.curves.new(label,"FONT")
    data.body=label
    data.align_x=align
    data.size=size
    data.resolution_u=4
    o=bpy.data.objects.new(label,data)
    scene.collection.objects.link(o)
    o.location=at
    o.rotation_euler.x=math.pi/2
    o.data.materials.append(paint)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target="MESH")
    return o


def merged(name, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    ob=bpy.context.object
    ob.name=ob.data.name=name
    scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bm=bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    def subpixel(f):
        a,b,c=[Vector(tuple(round(x,6) for x in v.co)) for v in f.verts]
        return (b-a).cross(c-a).length*.5<=1e-8
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if subpixel(f)],context="FACES_ONLY")
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    return ob


# Treads are individual level pads over a single backbone. Outer floor sits at -0.003 m.
box("Arrival slab",(0,0,-.157),(12,11.4,.29),black,.022)
for x in range(-2,3):
    for y in range(-3,4):
        w=2.36;d=1.61
        box("Staggered grip tile",(x*2.38,y*1.625,-.036),(w,d,.066),slate[(x+2*y)%3],.009)
for sign in (-1,1):
    xx=sign*5.92
    box("Subterranean side shell",(xx,0,2.30),(.23,11.4,4.62),navy,.05)
    for i in range(5):
        yy=-4.4+2.2*i
        box("Recessed slate side tile",(xx-sign*.16,yy,1.63),(.09,2.11,2.51),iron,.028)
        box("Copper interruption",(xx-sign*.22,yy,.46),(.050,1.77,.115),bronze,.013)
        box("Aisle emitter, outside center lane",(sign*2.03,yy,.014),(.062,.89,.027),amber,.010)
    for y in (-5.1,-2.6,0,2.6,5.12):
        beam("Raked pressure rib",(sign*5.69,y,.05),(sign*5.69,y,3.45),.28,.25,black,.032)
        beam("Shoulder rib",(sign*5.69,y,3.45),(sign*4.23,y,4.63),.28,.25,iron,.037)
        beam("Copper rib seam",(sign*5.52,y-.132,2.95),(sign*5.52,y-.132,3.46),.043,.049,bronze,.006)
    for r in (-1,1):
        box("Four high cyan channels",(sign*(3.7+.21*r),0,4.515),(.031,10.8,.028),cyan,.006)
    box("Upper overhead tray",(sign*3.7,0,4.59),(.58,11.2,.13),iron,.019)
    box("Wall shoulder",(sign*4.94,0,4.65),(2.2,11.4,.28),navy,.034)
box("Ceiling catch plane",(0,0,4.83),(12,11.4,.21),navy,.02)
for y in (-3.9,-1.95,0,1.95,3.9):
    box("Recessed overhead service cassette",(0,y,4.669),(2.51,1.82,.122),iron,.031)
    for x in (-1.12,1.12):
        box("Cassette folded edge",(x,y,4.562),(.067,1.68,.086),black,.019)
    for yy in (y-.71,y+.71):
        box("Recessed overhead return vent",(0,yy,4.594),(1.78,.11,.029),black,.009)
for sign in (-1,1):
    for y,k in [(-5.6,"Arrival"),(5.6,"Training")]:
        box(k+" wing",(sign*3.76,y,2.3),(4.20,.28,4.60),navy,.041)
        if sign>0: box(k+" lintel",(0,y,4.07),(3.25,.29,1.06),iron,.030)
        box(k+" copper stanchion",(sign*1.67,y-.18,1.49),(.18,.11,2.93),bronze,.023)
        for z in (.19,2.91):
            rod(k+" fastener",(sign*1.67,y-.245,z),.037,.018,iron)
for x in (-1.57,1.57):
    box("Approach cyan locator",(x,-5.393,1.50),(.052,.03,1.72),cyan,.008)
box("Training inset fascia",(0,5.555,3.32),(3.1,.16,.56),black,.038)
for x in (-1.28,1.28):
    box("Warm lintel aperture",(x,5.447,3.31),(.22,.018,.052),amber,.005)
line_text("TRAINING",(0,5.418,3.24),.28,chalk)
room=merged("E10a 12m arrival shell",list(scene.objects))
room_name="e10a-vault-arrival-shell.glb"
export([room],out/room_name)

# The surface wayfinding fixture is independent of the portal trigger and may be staged elsewhere.
before_console=set(scene.objects)
box("Return foundation",(0,0,.071),(.72,.60,.142),iron,.047)
box("Return armored body",(0,.03,.53),(.34,.34,.87),navy,.06)
for sign in (-1,1):
    beam("Return copper edge",(sign*.194,-.154,.20),(sign*.194,-.154,.82),.037,.055,bronze,.015)
box("Return bezel",(0,-.025,1.02),(.86,.36,.59),bronze,.046)
box("Tinted face glass",(0,-.211,1.02),(.75,.027,.47),black,.025)
box("Cyan status slit",(0,-.229,.859),(.45,.012,.026),cyan,.008)
line_text("SURFACE",(0,-.227,1.115),.118,chalk)
for x in (-.342,.342):
    for z in (.825,1.214):
        rod("Return front bolt",(x,-.230,z),.024,.020,iron,8)
# A physical white chevron pointing towards the backed-out surface ring, not a light pulse.
for a,b in [((-.12,-.233,.997),(0,-.233,.938)),((0,-.233,.938),(.12,-.233,.997))]:
    beam("Return chevron",a,b,.019,.018,chalk,.004)
console=merged("E10a surface return pedestal",[o for o in scene.objects if o not in before_console])
console_name="e10a-vault-return-pedestal.glb"
export([console],out/console_name)

# Keep the art donor untransformed in Git; instance only in the staging scene.
old=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(door))
roots=[o for o in scene.objects if o not in old and o.parent is None]
for a in roots:
    a.location.y += 5.62
console.location=(-3.38,-3.79,0)
console.rotation_euler.z=math.pi/2
bpy.context.view_layer.update()

# Check the two distinct paths as model space occupancy. Trigger and resident-room state are not implemented.
obs=[room,console]
vs,fs=[],[]
for o in obs:
    i=len(vs)
    vs.extend(o.matrix_world@p.co for p in o.data.vertices)
    fs.extend(tuple(i+j for j in p.vertices) for p in o.data.polygons)
tree=BVHTree.FromPolygons(vs,fs)
rays=0
for y in (-5.72,-5.30,-4.50,-2.5,0,2.5,4.7,5.40):
    for i in range(-8,9):
        for z in (.09,.40,.95,1.55,1.95,2.28):
            x=i*.141
            p,n,j,l=tree.ray_cast(Vector((x,y,z)),Vector((0,1,0)),.16)
            assert p is None,(x,y,z,p)
            rays+=1
for i in range(-8,9):
    for z in (.12,.55,1.15,1.76,2.45,2.75):
        x=i*.141
        for y,d in [(-5.8,1),(5.30,1)]:
            p,*_=tree.ray_cast(Vector((x,y,z)),Vector((0,d,0)),.60)
            assert p is None,(x,y,z,p)
            rays+=1
floor_heights=[]
for xi in range(-11,12):
    for yi in range(-55,56):
        p,n,j,l=tree.ray_cast(Vector((xi*.10,yi*.10,.30)),Vector((0,0,-1)),.4)
        assert p is not None and -.016<p.z<0 and n.z>.69,(xi,yi,p,n)
        floor_heights.append(p.z)
assert hashlib.sha256(door.read_bytes()).hexdigest()==before
world=[166,-38,-83]
room_coords=[room.matrix_world @ v.co for v in room.data.vertices]
world_bounds=[[round(fn([world[0]+p.x for p in room_coords]),4),
               round(fn([world[1]+p.z for p in room_coords]),4),
               round(fn([world[2]-p.y for p in room_coords]),4)] for fn in (min,max)]
assert all(minval<=lo<hi<=maxval for (minval,maxval),lo,hi in zip([(151,221),(-40,-30),(-99,-29)],*world_bounds))
summary={"scope":"Blender visual fit only; nominal placement, no portal traversal or live collisions",
         "reference_floor_three_m":world,"world_bounds_xyz_m":world_bounds,
         "floor_support_samples":len(floor_heights),"floor_sample_z_range_m":[round(min(floor_heights),5),round(max(floor_heights),5)],
         "center_aisle_nominal_width_m":2.256,"clear_mesh_line_samples":rays,
         "ordered_layout":["surface arrival ring (unbuilt trigger)","optional side return console","training bulkhead"],
         "training_bulkhead_sha256":before,"training_bulkhead_local_blender_m":[0,5.62,0],
         "console_local_blender_m":list(console.location),"assets":{}}
for ob,name in [(room,room_name),(console,console_name)]:
    ob.data.calc_loop_triangles()
    summary["assets"][name]={"bytes":(out/name).stat().st_size,"triangles":len(ob.data.loop_triangles)}
(out/"receipt.json").write_text(json.dumps(summary,indent=2)+"\n")
print("E10a receipt",json.dumps(summary),flush=True)

# Render-only lights: cyan ceiling contrast, warmer floor, no KHR_lights bundled in the GLBs.
scene.render.engine="CYCLES"
scene.cycles.samples=42
scene.cycles.use_denoising=False
scene.render.resolution_x,scene.render.resolution_y=1480,970
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=92
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.17
scene.view_settings.view_transform="AgX"
for label,at,aim,energy,size,color in [
    ("Ceiling cool wash",(0,2.8,4.38),(0,-1.3,.3),1050,4.4,(.48,.82,1)),
    ("Deep cyan rim",(-4.5,-2.1,3.64),(-.6,1,1.45),380,3.3,(.29,.67,1)),
    ("Warm gate key",(1.3,4.6,3.4),(0,2.1,.53),440,2.4,(1,.54,.30)),
    ("Console fill",(-2.0,-2.8,2.7),(-3.38,-3.82,.91),230,1.65,(1,.73,.49)),
    ("Entry fill",(0,-4.0,3.9),(0,2.7,1.0),290,2.3,(.47,.80,1)),
]:
    bpy.ops.object.light_add(type="AREA",location=at)
    l=bpy.context.object
    l.name=label;l.data.energy=energy;l.data.shape="DISK";l.data.size=size;l.data.color=color
    l.rotation_euler=(Vector(aim)-l.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
for name,at,aim,lens in [
    ("arrival",(.22,-4.82,1.68),(0,5.55,1.73),21),
    ("return",(-.36,-4.32,1.53),(-3.38,-3.74,1.05),53),
]:
    cam.location=at
    cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.filepath=str(out/f"{name}.jpg")
    bpy.ops.render.render(write_still=True)
