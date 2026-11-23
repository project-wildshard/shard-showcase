"""Rebuild the WSC-SCENE-008 Crate Titan arena environment study with Blender."""
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
layout = json.loads((Path(__file__).resolve().parents[3] / "project/layouts/wsc-scene-008-titan-bowl.json").read_text())
scene = bpy.context.scene
clear_scene()
buckets = {}
rng = random.Random(899)

def material(name, color, metal, rough, emission=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    node = mat.node_tree.nodes.get("Principled BSDF")
    for key, value in (("Base Color", (*color, 1)), ("Metallic", metal), ("Roughness", rough),
                       ("Emission Color", (*color, 1)), ("Emission Strength", emission)):
        node.inputs[key].default_value = value
    return mat

iron = material("Blue-black iron", (.061,.102,.123), .58, .58)
slab = material("Slate concrete", (.31,.35,.37), .10, .78)
light_slab = material("Raised concrete", (.40,.44,.45), .10, .75)
lane = material("Slate runway pavers", (.153,.23,.25), .35, .62)
band = material("Oxidized bronze band", (.42,.211,.097), .50, .66)
trim = material("Oxide steel", (.33,.112,.039), .70, .55)
void = material("Recess black", (.032,.048,.062), .49, .69)
amber = material("Amber photoluminescent ceramic", (1,.49,.11), .1, .40, 3)
ice = material("Blue-white lamp faces", (.37,.81,1), .12, .45, 6)
joints = material("Fine expansion joint", (.192,.222,.23), .06, .85)
paint = material("Mineral lane marking", (.48,.46,.32), .10, .80)

def mesh(group, mat, verts, faces):
    points, polys = buckets.setdefault((group, mat), ([], []))
    offset = len(points)
    points.extend(verts)
    polys.extend(tuple(offset + i for i in f) for f in faces)

box_faces = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]

def box(group, mat, p, dims, angle=0):
    x,y,z=p
    a,b,c=(v/2 for v in dims)
    co,si=math.cos(angle),math.sin(angle)
    mesh(group,mat,[(x+i*a*co-j*b*si,y+i*a*si+j*b*co,z+k*c)
                    for k in (-1,1) for j in (-1,1) for i in (-1,1)],box_faces)

def polar(r, degree, z=0):
    a = math.radians(degree)
    return r*math.cos(a), -r*math.sin(a), z

def ring(group, mat, a, b, r0, r1, bottom, top, steps=None):
    """Solid annular sector. Walls and stairs share exact local coordinates."""
    steps = steps or math.ceil((b-a)/3.75)
    for i in range(steps):
        lo, hi = a+(b-a)*i/steps, a+(b-a)*(i+1)/steps
        points = [polar(r,t,z) for z in (bottom,top) for t in (hi,lo) for r in (r0,r1)]
        faces=[(0,2,3,1),(4,5,7,6),(0,4,6,2),(1,3,7,5)]
        if i == 0: faces.append((2,6,7,3))
        if i == steps-1: faces.append((0,1,5,4))
        if r0 == 0:
            # Avoid degenerate faces and make the fan's inner axis one edge.
            remap=[0,1,0,2,3,4,3,5]
            faces=[tuple(dict.fromkeys(remap[j] for j in f)) for f in faces]
            points=[points[j] for j in (0,1,3,4,5,7)]
            faces=[f for f in faces if len(f)>=3]
        mesh(group,mat,points,faces)

def radial(group, mat, r, theta, z, dims):
    box(group,mat,polar(r,theta,z),dims,-math.radians(theta))

floor,wall,top = (layout[k] for k in ("floor_radius","wall_radius","stands_radius"))
ring("01 Circular slab",slab,0,360,0,floor,-6,0)
ring("01 Circular slab",void,0,360,0,11,.003,.025)
ring("01 Circular slab",paint,0,360,10.85,11,.028,.055)
# Survey grid cuts are inlaid strips (less than 1 cm proud), stopping before the edge band.
for r in (16,24,32,39.5):
    for theta in (0,90,180,270):
        ring("01 Circular slab",joints,theta-32,theta+32,r-.055,r,.0015,.009)
for theta in range(0,360,30):
    radial("01 Circular slab",joints,25,theta,.003,(28,.105,.008))
r0,r1=layout["leap_band_radii"]
ring("02 Edge band",band,0,360,r0,r1,.004,.033)
for i in range(48):
    theta=7.5*i
    ring("02 Edge band",trim,theta+.4,theta+7.1,49.6,50,.035,.11,2)
    radial("02 Edge band",paint,41.25,theta,.041,(2.0,.14,.027))
    radial("02 Edge band",paint,42.0,theta+.72,.041,(.46,.10,.027))

for index,theta in enumerate(layout["lane_headings_degrees_east_toward_south"],1):
    name=f"03 Diagonal lane {index}"
    width=layout["lane_width"]
    def span(r,y,z):
        a=math.radians(theta)
        return r*math.cos(a)+y*math.sin(a), -r*math.sin(a)+y*math.cos(a), z
    for step in range(10):
        r=13+step*3.85
        if step<9:
            length=3.77
        else:
            length=3.08
        mesh(name,lane,[span(rr,y,z) for z in (.035,.075) for y in (-width/2,width/2)
                        for rr in (r-length/2,r+length/2)],box_faces)
        for offset in (-4.74,4.74):
            box(name,paint,span(r,offset,.091),(length*.75,.13,.025),-math.radians(theta))
        if step % 3 == 0:
            radial(name,paint,r,theta,.09,(.32,1.35,.02))
    for offset in (-3.9,-2.7,2.7,3.9):
        box(name,amber,span(48.95,offset,.14),(.5,.27,.08),-math.radians(theta))

# The south gap through the wall is cut to the 16 m alcove width at the
# inner wall radius. The other 342 degrees carry a continuous ribbon wall.
angle=math.degrees(math.asin(layout["alcove_width"]/2/floor))
for a,b in ((0,90-angle),(90+angle,360)):
    ring("04 Retaining wall",iron,a,b,floor,wall,0,layout["wall_height"])
    ring("04 Retaining wall",light_slab,a,b,51.78,56.16,7.65,8.02)
    ring("04 Retaining wall",void,a,b,51.84,52.2,3.86,4.24)
    ring("04 Retaining wall",trim,a,b,51.76,52.17,4.22,4.44)
for i in range(32):
    t=i*11.25
    if abs(t-90)<17: continue
    radial("04 Retaining wall",slab,51.9,t,3.73,(.65,.69,7.25))
    radial("04 Retaining wall",amber,51.47,t,4.04,(.12,.43,.16))
    radial("04 Retaining wall",iron,52.25,t,7.9,(1.6,1.28,.41))

for i in range(16):
    a,b=i*22.5+1,i*22.5+21.5
    if i in (3,4):   # split bowl on either side of the south opening
        if i==3: b=min(b,90-angle)
        else: a=max(a,90+angle)
    if b<=a: continue
    for j in range(8):
        inn=56+j*1.73
        outer=56+(j+1)*1.73 if j<7 else top
        z=10+(j+1)*1.75
        ring("05 Segmented terraces",iron if j in (0,4,7) else slab,a,b,inn,outer,7.65,z)
        ring("05 Segmented terraces",light_slab,a,b,inn,inn+.18,z-.13,z+.025)
    ring("05 Segmented terraces",trim,a,b,69.3,70,23.76,24)
    # Two metal ribs per sector pin the terraces to the floor datum.
    for t in (a+2,b-2):
        radial("05 Segmented terraces",iron,68.84,t,10.6,(1.55,.88,23.8))

# Alcove graphic stand-ins, not working exits. The architecture sits within the
# 16 × 14 m pocket; it begins at the south tangent of the main slab.
alc_y=-floor-layout["alcove_depth"]/2
box("06 South checkpoint pocket",slab,(0,alc_y+.45,-.6),(16,14.9,1.20))
for x in (-7.65,7.65):
    box("06 South checkpoint pocket",iron,(x,alc_y,3.2),(.70,14,6.4))
    box("06 South checkpoint pocket",amber,(x*.94,alc_y,2.75),(.07,12.75,.18))
box("06 South checkpoint pocket",iron,(0,-65.65,3.2),(16,.70,6.4))
box("06 South checkpoint pocket",trim,(0,-53.6,6.3),(16,1.20,.65))
box("06 South checkpoint pocket",ice,(0,-54.28,6.24),(10,.19,.15))
for x in (-2.17,2.17):
    box("06 South checkpoint pocket",trim,(x,-65.15,2.12),(.41,.47,4.24))
    box("06 South checkpoint pocket",ice,(x*.925,-64.86,2.05),(.095,.10,3.50))
box("06 South checkpoint pocket",trim,(0,-65.13,4.47),(4.78,.48,.46))
box("06 South checkpoint pocket",void,(0,-65.18,2.15),(3.83,.31,4.1))
box("06 South checkpoint pocket",trim,(-4.7,-62,.70),(1.18,.90,1.4))
box("06 South checkpoint pocket",amber,(-4.7,-62,1.44),(.8,.61,.12))
for x in (-6.2,-5.4,-4.6,-3.8,3.8,4.6,5.4,6.2):
    box("06 South checkpoint pocket",paint,(x,-52.61,.022),(.35,1.15,.04),.34)

# Four asymmetric cover silhouettes; individual crate panels are art, not collision.
for n,theta in enumerate((0,90,180,270)):
    bx,by,_=polar(layout["cardinal_cover_radius"],theta)
    for i,(dx,dy,z) in enumerate([(-2.45,.15,0),(0,0,0),(2.37,.19,0),(-1.3,.91,1.84),(1.15,.68,1.84)][:4+n%2]):
        rot=math.radians((n*90)+rng.choice((-8,-3,0,4,7)))
        a=math.radians(n*90)
        x,y=bx+dx*math.cos(a)-dy*math.sin(a),by+dx*math.sin(a)+dy*math.cos(a)
        group=f"07 Crate cover {n+1}"
        box(group,void,(x,y,z+.92),(2.16,1.96,1.84),rot)
        def local(mat,u,v,h,size):
            box(group,mat,(x+u*math.cos(rot)-v*math.sin(rot),y+u*math.sin(rot)+v*math.cos(rot),z+h),size,rot)
        for h in (.18,1.67): local(iron,0,0,h,(2.23,2.03,.32))
        for u in (-.85,.85):
            for v in (-.78,.78): local(trim,u,v,.94,(.22,.22,1.35))
        for v in (-1.0,1.0):
            local(slab,0,v,.91,(1.55,.10,.89))
            for u in (-.44,0,.44): local(iron,u,v*1.06,.91,(.14,.06,.87))

# Cloth-like vertical bands and raised enamel chevrons. No painted danger telegraphs.
for t in (8,36,68,112,144,172,188,216,248,292,324,352):
    group="09 Stand banners"
    radial(group,trim,54.5,t,11.8,(.16,2.15,4.4))
    radial(group,void,54.48,t,13.94,(.25,2.3,.26))
    def face(u,h):
        a=math.radians(t)
        return 54.39*math.cos(a)+u*math.sin(a),-54.39*math.sin(a)+u*math.cos(a),h
    for h in (11.5,12.27,13.04):
        mesh(group,paint,[face(u,h+z) for u,z in ((-.79,.24),(0,-.13),(.79,.24),(.79,.45),(0,.10),(-.79,.45))],
             [(5,4,3,2,1,0)])

def aim(obj,p):
    obj.rotation_euler=(Vector(p)-obj.location).to_track_quat("-Z","Y").to_euler()

def lamp(name,position,target,energy,size,color):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=energy; data.shape="DISK"; data.size=size; data.color=color
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=position; aim(obj,target)

masts=(28,152,208,332)
assert len(masts)==layout["floodlight_count"]
for i,t in enumerate(masts,1):
    group=f"08 Floodlight bridge {i}"
    for shift in (-1.55,1.55):
        radial(group,iron,67.5,t+shift,19.65,(1.25,1.25,12.3))
    radial(group,trim,67.5,t,25.2,(2.50,6.6,2.38))
    for shift in (-1.75,-.59,.59,1.75):
        radial(group,void,66.04,t+shift,24.99,(.92,1.2,1.36))
        radial(group,ice,65.48,t+shift,24.91,(.18,1.0,.89))

# Asset buckets stay individually editable and avoid hundreds of scene objects.
parts=[]
for (group,mat),(verts,faces) in sorted(buckets.items(),key=lambda item:(item[0][0],item[0][1].name)):
    name=f"{group} | {mat.name}"
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);data.materials.append(mat)
    parts.append(obj)

f=out/"wsc-scene-008-titan-bowl.glb"
export(parts,f)
with f.open("rb") as fp:
    assert fp.read(4)==b"glTF"; _,filesize,jslen,_=struct.unpack("<4I",fp.read(16))
    doc=json.loads(fp.read(jslen))
assert f.stat().st_size==filesize and filesize<=2_097_152
assert not doc.get("images") and not doc.get("animations")
tris=sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(f))
re=[o for o in scene.objects if o.type=="MESH"]
assert len(re)==len(parts)
vs=[o.matrix_world@v.co for o in re for v in o.data.vertices]
mins=[round(min(v[k] for v in vs),2) for k in range(3)]
maxs=[round(max(v[k] for v in vs),2) for k in range(3)]
assert abs(mins[0]+70) < .25 and -70 <= mins[1] < -69 and mins[2] == -6, mins
assert max(abs(v-70) for v in maxs[:2])<.25
(out/"validation.json").write_text(json.dumps({"bytes":filesize,"triangles":tris,"meshes":len(re),
    "blender_bounds":[mins,maxs],"images":0,"animations":0},indent=2)+"\n")

scene.world=bpy.data.worlds.new("Separated cool chamber sky")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get("Background")
bg.inputs[0].default_value=(.119,.205,.326,1);bg.inputs[1].default_value=.42

for i,t in enumerate(masts):
    lamp("Floodlight",polar(64.9,t,24.9),polar(21,t+(-8 if i%2 else 8),0),29000,8,(.61,.79,1))
lamp("Warm alcove bounce",(0,-48,11),(0,-63,2),24000,14,(1,.56,.30))
lamp("High cool skylight",(-25,16,59),(0,0,8),54000,65,(.72,.86,1))
lamp("Warm mechanical bounce",(36,26,31),(8,6,2),21000,17,(1,.59,.34))
lamp("Opposite blue edge",(-41,-10,32),(0,0,0),19500,20,(.47,.71,1))
ground=material("Presentation underlay, not exported",(.035,.053,.073),.12,.73)
bpy.ops.mesh.primitive_plane_add(size=1500,location=(0,0,-6.05))
bpy.context.object.data.materials.append(ground)
cam=bpy.data.cameras.new("Arena camera")
scene.camera=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(scene.camera)
scene.render.engine="CYCLES";scene.cycles.samples=52;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=92
for name,pos,target,focal,res in (
    ("nov23-titan-bowl-overlook",(101,-137,113),(0,-1,6),37,(1500,1010)),
    ("nov23-titan-bowl-floor",(-4.3,-58.1,2.6),(17,22,7.2),26,(1380,920)),
):
    scene.camera.location=pos;aim(scene.camera,target);cam.lens=focal
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)
