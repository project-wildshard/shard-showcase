"""An uninstalled West practice-range refill crate with removable decorative stock."""
import hashlib
import json
from math import pi
from pathlib import Path
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index("--")+1]).resolve();out.mkdir(parents=True,exist_ok=True)
for o in tuple(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
scene=bpy.context.scene
parts=[]
def material(n,c,rough=.64,metal=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    for k,v in [("Base Color",(*c,1)),("Roughness",rough),("Metallic",metal)]:p.inputs[k].default_value=v
    return m
wood=material("Oiled warm cedar",(.26,.121,.045))
light=material("Cedar slat warm edges",(.35,.169,.062))
steel=material("Rough blue black iron",(.060,.086,.098),.58,.63)
brass=material("Handle and bolt heads",(.47,.308,.117),.40,.57)
teal=material("Range enamel",(.032,.211,.199))
cream=material("Bone paint",(.81,.743,.54))
slate=material("Slate practice stock bands",(.081,.153,.202))
def obj(n,v,f,m):
    s=bpy.data.meshes.new(n);s.from_pydata(v,[],f);s.update()
    o=bpy.data.objects.new(n,s);scene.collection.objects.link(o);s.materials.append(m);parts.append(o);return o
def box(n,p,d,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m);parts.append(o)
    if b:
        mod=o.modifiers.new("Light-catching edge","BEVEL");mod.width=b;mod.segments=1
    return o
def beam(n,p,q,w,m,verts=6):
    a,b=Vector(p),Vector(q);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=w,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.name=n;o.rotation_mode="QUATERNION";o.rotation_quaternion=d.to_track_quat("Z","Y")
    o.data.materials.append(m);parts.append(o);return o

# Two horizontally adjacent wells are open from the top. Nothing is furnished as a working mechanism.
for x in (-.51,.51):
    for y in (-.248,.248):
        box("Raised skid seat",(x,y,.059),(.171,.184,.118),steel,.018)
box("Base plank bed",(0,0,.153),(1.26,.660,.099),light,.013)
for i,z in enumerate((.28,.425,.57,.715,.858)):
    for s in (-1,1):
        box("Front or back cedar board",(0,s*.301,z),(1.23,.052,.139),wood if i%2==0 else light,.008)
        box("End cedar board",(s*.598,0,z),(.048,.557,.139),light if i==3 else wood,.008)
for x in (-.579,.579):
    for y in (-.318,.318):
        box("Bent iron guard",(x,y,.552),(.101,.084,.866),steel,.009)
        for z in (.233,.492,.762,.883):
            beam("Copper washer",(x,y,z),(x,y+(.047 if y>0 else -.047),z),.019,brass,8)
for s in (-1,1):
    box("Top iron cap edge",(0,s*.303,.937),(1.19,.070,.035),steel,.008)
    box("End rim",(s*.60,0,.938),(.072,.544,.039),steel,.008)
    for x in (-.375,-.249,-.123,.123,.249,.375):
        box("Route color strip",(x,s*.332,.31),(.083,.009,.035),teal,.004)
box("Oak center divider",(0,0,.57),(.047,.552,.756),light,.010)
for x in (-.35,.35):
    box("Raised well floor",(x,0,.326),(.41,.491,.040),wood,.004)
plate=box("Separate enamel plaque",(0,-.35,.65),(.713,.036,.218),teal,.017)
for x in (-.314,.314):
    beam("Plaque hardware",(x,-.366,.645),(x,-.376,.645),.019,brass,8)
curve=bpy.data.curves.new("Refill label editable string","FONT");curve.body="REFILL";curve.align_x="CENTER";curve.size=.14
text=bpy.data.objects.new("REFILL | die-painted plaque",curve);scene.collection.objects.link(text)
text.location=(0,-.372,.608);text.rotation_euler=(pi/2,0,0)
curve.materials.append(cream);parts.append(text)

def export(name,group):
    bpy.ops.object.select_all(action="DESELECT")
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    o=bpy.context.object;o.name=name
    scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    p=out/f"{name}.glb"
    bpy.ops.export_scene.gltf(filepath=str(p),export_format="GLB",use_selection=True,
                             export_texcoords=False,export_animations=False)
    return o,p
crate,crate_file=export("w3b-range-refill-crate",parts)
parts=[]
# Solid colored mock stock with blunt points absent; this layer can be hidden without affecting the crate.
for s,base in [(-1,.97),(1,1.08)]:
    for i in range(4):
        x=.295*s+(i-1.5)*.079
        y=(-.099,.064,-.040,.11)[i]
        z=base+(-.035,.034,-.020,.017)[i]
        beam("Practice stock silhouette",(x,y,.35),(x+.024,y,z+.14),.0105,light,5)
        # Broad faceted fletching, double-sided so it reads from eye level.
        for sign in (-1,1):
            obj("Decorative feather",
                [(x+.014,y,z-.018),(x+.024,y+sign*.045,z+.062),
                 (x+.024,y+sign*.045,z+.143),(x+.026,y,z+.125)],
                [(0,1,2,3)],slate if s>0 else cream)
stock,stock_file=export("w3b-refill-display-stock",parts)
def bring(path):
    a=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
    return sorted(set(scene.objects)-a,key=lambda q:q.name)
def get_bvh(obs):
    v,f=[],[]
    for o in obs:
        if o.type!="MESH":continue
        i=len(v);v.extend(o.matrix_world @ w.co for w in o.data.vertices)
        f.extend(tuple(i+j for j in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(v,f),v
bpy.data.objects.remove(crate,do_unlink=True);bpy.data.objects.remove(stock,do_unlink=True)
c=bring(crate_file);s=bring(stock_file)
cr,cv=get_bvh(c);_,sv=get_bvh(s)
cbase=min(v.z for v in cv);assert abs(cbase)<1e-6
hits=[]
for side in (-1,1):
    for dx in (-.15,-.075,0,.075,.15):
        for y in (-.18,-.09,0,.09,.18):
            hit=cr.ray_cast((side*.35+dx,y,1.3),(0,0,-1),1.3)[0]
            assert hit is not None and abs(hit.z-.346)<1e-6,hit
            hits.append(hit.z)
assert all(.14<abs(v.x)<.46 and abs(v.y)<.21 for v in sv)
def stats(glb):
    b=glb.read_bytes();x=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    assert len(x["meshes"])==1 and not any(x.get(k) for k in ("images","textures","animations","skins"))
    p=x["meshes"][0]["primitives"]
    return dict(bytes=len(b),triangles=sum(x["accessors"][v["indices"]]["count"]//3 for v in p),
                primitives=len(p),sha256=hashlib.sha256(b).hexdigest())
proof={"crate":stats(crate_file),"stock":stats(stock_file),"wellClearRays":len(hits),
       "wellFloorM":round(min(hits),4),"nominalOrigin":"ground under crate center",
       "baseSizeXZMetres":[round(max(v.x for v in cv)-min(v.x for v in cv),4),
                           round(max(v.y for v in cv)-min(v.y for v in cv),4)],
       "visualsOnly":True}
assert proof["crate"]["bytes"]<190000 and proof["stock"]["bytes"]<34000,proof
(out/"w3b-range-refill-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print(proof,flush=True)
if "--no-render" in sys.argv:sys.exit(0)

# Studio staging only. The geometry is not pinned to a range map position.
floor=material("West stone flagway",(.155,.161,.143))
wall=material("Deep slate workshop plaster",(.071,.105,.115))
box("Preview floor",(0,0,-.052),(100,100,.1),floor)
box("Preview backdrop",(0,1.9,2),(100,.24,4),wall)
for i in range(3):
    box("Preview curb",(-1.45+i*1.48,1.49,.11),(1.45,.14,.235),steel,.018)
scene.world.color=(.22,.29,.33)
scene.render.engine="CYCLES";scene.cycles.samples=30;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()
def area(p,t,w,l,s):
    bpy.ops.object.light_add(type="AREA",location=p)
    q=bpy.context.object;q.data.energy=w;q.data.color=l;q.data.shape="DISK";q.data.size=s;aim(q,t)
area((-3.6,-4.6,6),(0,0,.7),560,(.70,.85,1),5)
area((4,.8,4),(0,0,.8),820,(1,.75,.48),4)
for name,p,t,l,d in [
    ("front",(2.1,-4.25,1.75),(0,0,.63),54,(1200,870)),
    ("wells",(-2.2,-2.8,3.05),(0,0,.61),57,(1110,890)),
]:
    bpy.ops.object.camera_add(location=p)
    q=bpy.context.object;aim(q,t);q.data.lens=l;scene.camera=q
    scene.render.resolution_x,scene.render.resolution_y=d;scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    assert all(.045<v.x<.955 and .045<v.y<.955 for v in (world_to_camera_view(scene,q,x) for x in cv+sv)),name
    scene.render.image_settings.file_format="WEBP";scene.render.image_settings.quality=88
    scene.render.filepath=str(out/f"nov25-w3b-refill-{name}.webp");bpy.ops.render.render(write_still=True)
