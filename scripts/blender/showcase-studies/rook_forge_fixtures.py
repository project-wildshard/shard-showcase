"""W2b · two removable, surface-checked fixtures for Rook's original frontage."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

OUT = output_directory()
only = os.environ.get("WSC_METADATA_ONLY")
clear_scene()


def material(name, c, metal, rough):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*c,1)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    for k,v in (("Base Color",(*c,1)),("Metallic",metal),("Roughness",rough)):
        p.inputs[k].default_value=v
    return m


wood = material("Forge | Ebonised oak",(.090,.043,.023),.0,.71)
nest = material("Forge | Deep petrol lining",(.025,.100,.111),.0,.86)
brass = material("Fixture | Brushed brass",(.54,.286,.094),.66,.4)
ink = material("Fixture | Linen enamel lettering",(.85,.77,.56),.04,.54)
face = material("Bench | Petrol green enamel",(.025,.169,.176),.17,.42)
iron = material("Forge I | Dark forged iron",(.103,.126,.143),.70,.56)
steel = material("Forge II | Bright steel",(.32,.40,.415),.72,.33)
alloy = material("Forge III | Amber alloy",(.55,.29,.092),.71,.39)
titanium = material("Forge IV | Blue-grey titanium",(.205,.37,.42),.82,.37)
parts=[]


def bake(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target="MESH")
    parts.append(bpy.context.object)
    return bpy.context.object


def box(name,p,dim,m,b=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=name
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new("Finger-safe edges","BEVEL")
        mod.width,mod.segments=b,2
        o.modifiers.new("Planar reflection","WEIGHTED_NORMAL")
    return bake(o)


def text(s,p,height,material,width,vertical=False,name=None):
    f=bpy.data.curves.new(s,"FONT")
    f.body=s
    f.align_x="CENTER"
    f.align_y="CENTER"
    f.size=height
    f.resolution_u=3
    f.materials.append(material)
    o=bpy.data.objects.new(name or s,f)
    bpy.context.collection.objects.link(o)
    o.location=p
    bpy.context.view_layer.update()
    if o.dimensions.x>width:
        o.scale.x=width/o.dimensions.x
    if vertical:
        o.rotation_euler.x=math.pi/2
    return bake(o)


def pin(name,p,r,depth,m,front=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=depth,location=p,
                                       rotation=(math.pi/2 if front else 0,0,0))
    o=bpy.context.object
    o.name=name
    o.data.materials.append(m)
    parts.append(o)
    return o


def artifact(slug,limit):
    by_material={}
    for o in parts:
        # Keep the carrier separate from both components of the replaceable face.
        group="Replaceable face" if o.name.startswith("Replaceable") else "Fixture"
        by_material.setdefault((group,o.data.materials[0].name),[]).append(o)
    reduced=[]
    for (group,finish),group_parts in sorted(by_material.items()):
        bpy.ops.object.select_all(action="DESELECT")
        for o in group_parts:o.select_set(True)
        bpy.context.view_layer.objects.active=group_parts[0]
        if len(group_parts)>1:bpy.ops.object.join()
        o=bpy.context.object
        o.name=group+" | "+finish
        reduced.append(o)
    p=OUT/(slug+".glb")
    export(reduced,p)
    raw=p.read_bytes()
    assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
    doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    primitives=[p for m in doc["meshes"] for p in m["primitives"]]
    tris=sum(doc["accessors"][p["indices"]]["count"]//3 for p in primitives)
    assert len(primitives)==len(reduced) and tris<=limit and len(raw)<230000
    assert not any(k in doc for k in ("images","skins","animations","cameras"))
    parts.clear()
    for o in reduced:bpy.data.objects.remove(o,do_unlink=True)
    return p,dict(bytes=len(raw),triangles=tris,draws=len(primitives),
                  sha256=hashlib.sha256(raw).hexdigest())


box("Tray walnut plinth",(0,0,.019),(.640,.376,.038),wood,.010)
box("Inset lining",(0,.001,.040),(.612,.350,.008),nest,.004)
for side in (-1,1):
    box("Brass perimeter plate",(side*.307,0,.050),(.012,.354,.020),brass)
for y in (-.175,.173):
    box("Brass edge rail",(0,y,.051),(.610,.012,.021),brass)
for x in (-.151,0,.151):
    box("Removable dividers",(x,.006,.052),(.006,.259,.015),wood,.002)
box("Raised Forge header",(0,.141,.080),(.593,.044,.066),wood,.005)
text("FORGE  /  ALL WEAPONS",(0,.141,.1138),.033,ink,.51)
cols=[(-.229,"I","IRON",iron),(-.076,"II","STEEL",steel),
      (.076,"III","ALLOY",alloy),(.229,"IV","TITANIUM",titanium)]
for i,(x,grade,label,metal) in enumerate(cols):
    text(label,(x,-.133,.0448),.022,ink,.126)
    text(grade,(x,-.081,.0448),.026,ink,.105)
    # Four fabricated coupons with progressively cleaner edge profiles.
    o=box("Metal coupon "+grade,(x,.030,.069),(.091,.141,.049),metal,.004+.003*i)
    o.rotation_euler.z=math.radians((-7,-2,4,8)[i])
    if i==0:
        for dx in (-.028,.026):
            pin("Forging dimple",(x+dx,.048,.0944),.009,.003,wood)
    if i in (1,2):
        for j in range(2 if i==1 else 3):
            box("Raised pass line",(x-.025+j*.019,.040,.0942),(.006,.078,.003),brass if i==2 else iron,0)
    if i==3:
        for dy in (.011,.052):
            pin("Bright fastener",(x+.011,dy,.095),.014,.003,steel)
tray,tm=artifact("w2b-rook-forge-tray",3400)

box("Bench stand foot",(0,0,.018),(.460,.256,.036),wood,.010)
for x in (-.151,.151):
    box("Bench brass upright",(x,.042,.124),(.024,.042,.183),brass,.006)
box("Bench carrier",(0,.017,.211),(.434,.070,.206),wood,.012)
box("Replaceable face | tile",(0,-.026,.211),(.412,.023,.188),face,.008)
for x in (-.189,.189):
    for z in (.135,.288):
        pin("Retaining stud",(x,-.0375,z),.0065,.007,brass,True)
text("BENCH",(0,-.0388,.237),.075,ink,.302,True,"Replaceable face | BENCH")
text("AMMO ONLY",(0,-.0388,.170),.035,ink,.263,True,"Replaceable face | AMMO ONLY")
bench,bm=artifact("w2b-rook-bench-placard",3300)

# Rebuild the original donor composition at the same frame without its renders.
os.environ["WSC_METADATA_ONLY"]="1"
base=runpy.run_path(str(HERE/"rook_counter.py"))
if only is None: del os.environ["WSC_METADATA_ONLY"]
orig=json.loads((HERE.parents[2]/"project/layouts/w2b-rook-counter-study.json").read_text())
assert json.loads(json.dumps(base["manifest"]))==orig, "Original Rook donor or staging changed"
scene=bpy.context.scene
scene.frame_set(19)
scene.cycles.samples=38
scene.cycles.adaptive_threshold=.07
raw_parts,center,*_=base["sources"]["counter"]
counter_t=Matrix.Translation((1.45,-1.56,0))@Matrix.Rotation(math.radians(-7),4,"Z")@Matrix.Translation(-Vector(center))
# Work in unrecentered counter geometry. Cloth and original pots come from
# exact triangles, not proxy dimensions; convert raw glTF z to Blender -y.
tops=[]; faces=[]
for mesh,m in raw_parts:
    j=len(tops)
    tops.extend([m@v.co for v in mesh.vertices])
    faces.extend(tuple(j+i for i in f.vertices) for f in mesh.polygons)
bvh=BVHTree.FromPolygons(tops,faces)
bounds=[]
specs=[]
for name,p,sz,raw_x,raw_z in (
    ("forge",tray,(.640,.376),-.025,1.01),
    ("bench",bench,(.460,.256),.650,1.02),
):
    # Middle square and outer edges all sit on the same undisturbed cloth level.
    heights=[]
    for i in range(13):
        for j in range(9):
            x=raw_x+(i/12-.5)*sz[0]
            y=-raw_z+(j/8-.5)*sz[1]
            hit,normal,_,_=bvh.ray_cast(Vector((x,y,1.76)),Vector((0,0,-1)),.95)
            assert hit is not None and normal.z>.985,(name,x,y,hit,normal)
            heights.append(hit.z)
    assert max(heights)-min(heights)<.001 and 1.027<min(heights)<=max(heights)<1.032,heights
    h=max(heights)+.0005
    W=counter_t@Matrix.Translation((raw_x,-raw_z,h))
    obs=base["imported"](p)
    assert all(o.type in ("MESH","EMPTY") for o in obs)
    assert sum(o.name.startswith("Replaceable face") for o in obs)==(2 if name=="bench" else 0)
    for o in obs:
        if o.parent not in obs:o.matrix_world=W@o.matrix_world
    bpy.context.view_layer.update()
    inv=counter_t.inverted()
    pts=[inv@(o.matrix_world@v.co) for o in obs if o.type=="MESH" for v in o.data.vertices]
    assert -.001<min(v.z for v in pts)-h<.001
    bounds.append((min(v.x for v in pts),max(v.x for v in pts),min(v.y for v in pts),max(v.y for v in pts)))
    specs.append(dict(name=name,xyz_blender_m=[round(v,7) for v in W.translation],
                      yaw_deg=-7,counter_raw_glb_xz_m=[raw_x,raw_z],surface_contact_rays=len(heights),
                      surface_height_range_raw_m=[round(min(heights),7),round(max(heights),7)]))

pot_edge=max(v.x for v in tops if v.z>1.034)
gaps=[bounds[0][0]-pot_edge,bounds[1][0]-bounds[0][1]]
assert min(gaps)>.09,gaps
for a,b,c,d in bounds: assert -1.065<a<b<1.065 and -1.313<c<d<-.703

if only!="1":
    base["camera"](scene,"nov25-w2b-rook-frontage",(.05,-6.8,1.73),(.63,-1.50,1.39),(1440,900),lens=36)
    base["camera"](scene,"nov25-w2b-rook-forge-detail",(1.07,-2.60,1.94),(1.73,-1.61,1.12),(1440,900),lens=36)
def clean(v): return round(v,6)
(OUT/"w2b-rook-forge-fit.json").write_text(json.dumps({
    "scope":"Existing Rook frontage, static removable art; no panel logic, prices, inventory or purchases.",
    "catalogue_id":"WSC-SCENE-002",
    "counter_sha256":orig["donors"]["counter"]["sha256"],
    "actor_sha256":orig["actor"]["sha256"],
    "actor_frame":19,
    "forge_labels":[s[2] for s in cols],
    "exports":{"forge-tray":tm,"bench-placard":bm},
    "pot_right_edge_raw_m":clean(pot_edge),
    "minimum_gaps_pot_tray_and_tray_bench_m":[clean(g) for g in gaps],
    "reimported_footprints_raw_blender_m":[[clean(v) for v in row] for row in bounds],
    "placements":specs,
},indent=2)+"\n")
print(tm,bm,gaps,specs,flush=True)
