"""WSC-PROP-066 companion: exact-footprint E1c half-cover type, not a crate."""
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

out = Path(sys.argv[sys.argv.index("--")+2]).resolve()
src = json.loads(Path(sys.argv[sys.argv.index("--")+1]).read_text())
out.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[3]
assets = root/"public/assets/wildshard-art"
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def material(name, rgb, metal=0, rough=.65, noise=None):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    nodes=m.node_tree.nodes
    bs=nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    if noise:
        tex=nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=noise[0]
        ramp=nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color=(*rgb,1)
        ramp.color_ramp.elements[1].color=(*noise[1],1)
        m.node_tree.links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
        m.node_tree.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    return m

concrete=material("Cool mineral aggregate",(.19,.207,.190),rough=.86)
worn=material("Grey concrete cap",(.31,.324,.288),rough=.83)
dark=material("Blue-black undercut",(.047,.070,.067),.35)
oxide=material("Welded burnt orange shell",(.47,.168,.043),.29,.48)
bright=material("Ochre shoulder guards",(.72,.315,.058),.28,.51)
rivets=material("Brushed steel fasteners",(.25,.282,.247),.60,.47)
marker=material("Warm yellow enamel",(.76,.58,.17),.11,.56)
edgeWear=material("Exposed grey impact scrape",(.33,.32,.255),.28,.63)
def mesh(name,vs,faces,mats,idx=None):
    d=bpy.data.meshes.new(name)
    d.from_pydata(vs,[],faces);d.update()
    for mat in mats:d.materials.append(mat)
    if idx is not None:
        for p,i in zip(d.polygons,idx):p.material_index=i
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    return o

def box(name,origin,dims,m,bevel=0):
    a,b,c=(d/2 for d in dims)
    o=mesh(name,[(i*a,j*b,k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
        [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],[m])
    o.location=origin
    if bevel:
        mod=o.modifiers.new("Wear bevel","BEVEL");mod.width=bevel;mod.segments=1
        o.modifiers.new("Face normals","WEIGHTED_NORMAL")
    return o

# One monolithic casting preserves the old slab and right return plan.
# Three profiles keep a broad foot, vertical shoulder and softer cap.
def chamfer(poly,k):
    points=[]
    for i,(x,y) in enumerate(poly):
        for j in (-1,1):
            xx,yy=poly[(i+j)%len(poly)]
            d=math.hypot(xx-x,yy-y)
            points.append((x+(xx-x)*k/d,y+(yy-y)*k/d))
    return points # counter-clockwise normals, viewed from above

def loop(inset):
    return chamfer([(-2.5+inset,-.40+inset),(2.50+inset,-.40+inset),(2.50+inset,-2.60+inset),
       (3.30-inset,-2.60+inset),(3.30-inset,.40-inset),(-2.50+inset,.40-inset)],.065)

n=12
levels=[(0,.025),(.105,0),(.21,.035),(.78,.082),(.99,.105),(1.10,.181)]
verts=[(x,y,z) for z,inset in levels for x,y in loop(inset)]
faces=[tuple(reversed(range(n)))]; ids=[1]
for row in range(len(levels)-1):
    q=row*n
    for i in range(n):
        k=(i+1)%n
        faces.append((q+i,q+k,q+n+k,q+n+i));ids.append([1,1,0,0,2][row])
faces.append(tuple(range(len(verts)-n,len(verts))));ids.append(2)
parts=[mesh("L-shaped cast mineral ballast",verts,faces,[concrete,dark,worn],ids)]

# Segmented impact panel follows the same silhouette, with bare ends, guards,
# and end reflectors. All patches sit within the proxy envelope.
for sign in (-1,1):
    y=sign*.313
    for i,x in enumerate((-1.77,-.57,.63,1.83)):
        o=box("Formed orange impact plate",(x,y,.56),(1.05,.078,.38),oxide,.028)
        o.rotation_euler.x=sign*.07
        parts.append(o)
        for z in (.44,.68):
            for u in (-.40,.40):
                parts.append(box("Pressed square pin",(x+u,sign*.354,z),(.045,.018,.042),rivets))
    for x,d,z in [(-1.86,.21,.49),(-.79,.11,.56),(.67,.18,.63),(1.62,.22,.46)]:
        sc=box("Worn enamel nicks",(x,sign*(.352+(.56-z)*.07),z),(d,.006,.014),edgeWear)
        sc.rotation_euler.y=sign*.16
        parts.append(sc)
    for x in (-2.29,2.32):
        parts.append(box("High visibility end catch",(x,sign*.347,.54),(.15,.032,.42),bright,.019))
    for x in (-2.11,2.16):
        parts.append(box("Small reflector",(x,sign*.357,.69),(.12,.015,.045),marker,.006))
for x in (2.576,3.222):
    for y in (-2.03,-1.25,-.55):
        parts.append(box("Return panel",(x,y,.53),(.06,.58,.34),oxide,.023))
for x in (2.67,3.12):
    parts.append(box("Return end strike guard",(x,-2.52,.56),(.12,.055,.43),bright,.015))

bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
file=out/"e1-half-cover.glb"
bpy.ops.export_scene.gltf(filepath=str(file),export_format="GLB",use_selection=True,export_animations=False)
blob=file.read_bytes()
g=json.loads(blob[20:20+struct.unpack_from("<I",blob,12)[0]])
tris=sum(g["accessors"][p["indices"]]["count"]//3 for m in g["meshes"] for p in m["primitives"])
assert len(blob)<165000 and tris<1800
assert not any(g.get(k) for k in ("images","animations","skins"))
for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)

def load(path):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    new=sorted(set(scene.objects)-before,key=lambda o:o.name)
    a=[(o.name,o.data,o.matrix_world.copy()) for o in new if o.type=="MESH"]
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
    return a

def add(donor, xyz, angle=0):
    t=Matrix.Translation(xyz)@Matrix.Rotation(angle,4,"Z")
    items=[]
    for n,d,m in donor:
        o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);o.matrix_world=t@m
        items.append(o)
    return items

template=load(file)
body=[q for q in template if q[0].startswith("L-shaped")]
assert len(body)==1, [q[0] for q in template]
xyz=[q[2]@v.co for q in template for v in q[1].vertices]
bounds=[[round(fn(v[i] for v in xyz),5) for i in range(3)] for fn in (min,max)]
assert bounds==[[-2.5,-2.6,0.0],[3.3,.4,1.1]],bounds

def geom(items):
    v=[];ind=[]
    for ob in items:
        start=len(v)//3
        for vert in ob.data.vertices:
            x,y,z=ob.matrix_world@vert.co
            v.extend(round(k,6) for k in (x,z,-y))
        ob.data.calc_loop_triangles()
        ind.extend(start+i for face in ob.data.loop_triangles for i in face.vertices)
    return {"vertices":v,"indices":ind}

collision=[]
roadclear=[]
for r in src["rows"]:
    o=add(body,(r["x"],-r["z"],0),r["ry"])
    data=geom(o)
    roadclear.append(round(-src["ROAD"]["half"]-max(data["vertices"][2::3]),5))
    collision.append(data)
    for ob in o:bpy.data.objects.remove(ob,do_unlink=True)
assert min(roadclear)>1.7,roadclear
(out/"half-collision.json").write_text(json.dumps(collision,separators=(",",":"))+"\n")
(out/"half-art.json").write_text(json.dumps({"archive":src["archive"],"pins":src["pins"],
    "ROAD":src["ROAD"],"rows":src["rows"],"review":src["review"],
    "crateContext":src["context"],"dayPacks":src["dayPacks"],
    "bboxBlender":bounds,"roadClearances":roadclear,
    "model":{"file":file.name,"bytes":len(blob),"triangles":tris,
             "sha256":hashlib.sha256(blob).hexdigest()}},
    indent=2)+"\n")
if "--no-render" in sys.argv:sys.exit(0)

for r in src["rows"]:
    add(template,(r["x"],-r["z"],0),r["ry"])
a=assets/"haul-crate.glb"; c=assets/"e1-first-cover-cradle.glb"
old=json.loads((root/"project/layouts/e1-first-cover-cradle-proof.json").read_text())
assert hashlib.sha256(a.read_bytes()).hexdigest()==old["crate"]["sha256"]
assert hashlib.sha256(c.read_bytes()).hexdigest()==old["model"]["sha256"]
crate,cradle=load(a),load(c)
for r in src["context"]:
    x,y,ry=r["x"],-r["z"],r["ry"]
    add(cradle,(x,y,0),ry)
    t=Matrix.Translation((x,y,0))@Matrix.Rotation(ry,4,"Z")
    for px,pz,py in old["crateTranslationsXYZ"]:
        add(crate,t@Vector((px,-py,pz)),ry)
sand=material("Sun-caked clay",(.125,.086,.053),rough=.9,noise=(23,(.38,.29,.174)))
tarmac=material("Aggregate road",(.052,.053,.050),rough=.96,noise=(16,(.113,.117,.106)))
shoulder=material("Dusty gravel fringe",(.12,.105,.078),rough=.93,noise=(26,(.26,.211,.155)))
paint=material("Weathered road stripe",(.50,.48,.36),rough=.82)
bay=material("Blue freight siding",(.062,.13,.15),.42)
box("Yard terrain context",(72,29,-.16),(145,126,.32),sand)
box("17 m archived road width",(76,0,-.038),(136,17,.08),tarmac)
box("Road bedding",(76,8.86,-.039),(136,.81,.082),shoulder)
for x in range(8,140,6):box("Worn road edge mark",(x,8.13,.009),(3.8,.11,.012),paint)
# Far context only to avoid flattening the exact near silhouettes into sky.
for x,y,h in [(40,57,3.3),(43,59,4.7),(61,57,4.2),(84,54,3.5),(91,52,5.2),(104,41,3.6)]:
    box("Far freight body",(x,y,h/2),(4.8,3.8,h),bay,.09)
    for j in range(8):
        box("Rolled freight rib",(x-2.1+j*.60,y-1.92,h/2),(.14,.10,h*.92),dark,.02)
    box("Oxide upper band",(x,y-1.94,h-.14),(4.67,.12,.12),oxide)
rng=random.Random(278)
chips=material("Sunbleached stones",(.25,.219,.158),rough=.87)
for i in range(255):
    x,y=rng.uniform(46,95),rng.uniform(9,47)
    if any(math.hypot(x-r["x"],y+r["z"])<2.7 for r in src["rows"]):continue
    d=rng.uniform(.035,.115)
    box("Shoulder mineral",(x,y,.012),(d,d*.64,.023),chips).rotation_euler.z=rng.uniform(0,6.28)
sky=bpy.data.worlds.new("Dusk sand and blue");scene.world=sky;sky.use_nodes=True
world=sky.node_tree;sun=world.nodes.new("ShaderNodeTexSky");sun.sky_type="NISHITA"
sun.sun_elevation=.31;sun.sun_rotation=4.8;sun.sun_size=.05
world.links.new(sun.outputs[0],world.nodes["Background"].inputs[0])
world.nodes["Background"].inputs[1].default_value=.12
scene.view_settings.exposure=-.18
c=bpy.data.cameras.new("Field camera");o=bpy.data.objects.new(c.name,c);scene.collection.objects.link(o);scene.camera=o
scene.render.engine="CYCLES";scene.cycles.samples=40;scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.067
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=92
for name,eye,at,lens,w,h in [
 ("cover-eye",(67.2,7.4,1.70),(61,14.3,.62),25,820,1080),
 ("cover-yard",(75,-4,14.8),(67,25,0),27,1290,900),
]:
    o.location=eye;c.lens=lens;o.rotation_euler=(Vector(at)-o.location).to_track_quat("-Z","Y").to_euler()
    scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)
