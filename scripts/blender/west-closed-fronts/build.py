"""Removable closed storefront inserts for the three W0b reserved lots."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/blender/showcase-studies"))
from common import export

town, out = map(Path, sys.argv[sys.argv.index("--") + 1:])
out.mkdir(parents=True, exist_ok=True)
raw = (town / "town-lots.json").read_bytes()
pin = json.loads((ROOT / "scripts/blender/west-town/expected.json").read_text())["town_lots_sha256"]
assert hashlib.sha256(raw).hexdigest() == pin
lots = [(i, r) for i, r in enumerate(json.loads(raw), 1) if r["kind"] == "tolet"]
assert len(lots) == 3

def material(name, color, metallic):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = .66
    p.inputs["Metallic"].default_value = metallic
    return m

iron = material("Patinated iron rails", (.045, .065, .064), .42)
green = [material(f"Painted pine {i+1}", c, 0) for i,c in enumerate(
    [(.081,.151,.129),(.104,.181,.147),(.115,.195,.164)])]
bronze = material("Burnished bronze", (.38,.213,.065), .53)

def box(name, loc, size, mat, bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        q = obj.modifiers.new("Shaped edge","BEVEL")
        q.width, q.segments = bevel, 1
        bpy.ops.object.modifier_apply(modifier=q.name)
    return obj

def load(path):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted(set(bpy.context.scene.objects)-before,key=lambda o:o.name)

def bvh(objs):
    v, f = [], []
    for obj in objs:
        if obj.type != "MESH":
            continue
        f.extend(tuple(i+len(v) for i in p.vertices) for p in obj.data.polygons)
        v.extend(obj.matrix_world@p.co for p in obj.data.vertices)
    return BVHTree.FromPolygons(v, f)

def ray(tree, origin, dir, length):
    return tree.ray_cast(Vector(origin),Vector(dir),length)[0]

files={}
for width in (14,16):
    span=.54*width+.16
    p=[]
    for leaf in range(4):
        lgap=.018
        lane=(span-.24)/4
        x=(leaf-1.5)*lane
        p.append(box("Shutter backing",(x,-.294,1.65),(lane-lgap,.039,1.858),green[0],0))
        for slat in range(12):
            z=1.65+(slat-5.5)*.153
            p.append(box("Lapped pine",(x,-.318,z),(lane-lgap,.018,.148),green[(leaf+2*slat)%3],0))
        for q in (x-lane*.5+.031,x+lane*.5-.031):
            p.append(box("Leaf seam stile",(q,-.333,1.65),(.046,.018,1.888),iron))
        for z in (.94,2.36):
            p.append(box("Tapered iron strap",(x,-.346,z),(lane*.82,.020,.064),iron,.007))
            for dx in (-lane*.32,lane*.32):
                p.append(box("Bronze strap pin",(x+dx,-.360,z),(.025,.014,.024),bronze,.004))
        if leaf in (1,2):
            hx=x+(.45 if leaf==1 else -.45)*lane
            p.append(box("Keeper plate",(hx,-.344,1.51),(.115,.020,.178),iron,.006))
            p.append(box("Bronze latch bar",(hx,-.366,1.54),(.130,.017,.040),bronze,.005))
    for side in (-1,1):
        p.append(box("Stone-side rail",(side*(span/2-.049),-.309,1.65),(.098,.061,1.976),iron,.007))
    for z in (.674,2.626):
        p.append(box("Jamb header or sill",(0,-.304,z),(span,.059,.043),iron,.006))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in p:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = p[0]
    bpy.ops.object.join()
    united = bpy.context.object
    united.name = f"W0b | closed shutter for {width} m lot"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    path=out/f"w0b-closed-front-{width}m.glb"
    export([united],path)
    bpy.data.objects.remove(united,do_unlink=True)
    files[width]=path

bpy.ops.wm.open_mainfile(filepath=str(town/"whole-town-editable.blend"))

placements=[]
for i,r in lots:
    a,b,c,d=r["x0"],r["x1"],-r["z1"],-r["z0"]
    mid=(c+d)/2
    sign=-1 if mid>0 else 1
    x=(a+b)/2
    y=mid+sign*((d-c)/2-.4)
    lot=bpy.data.objects[f"TOWN | LOT {i:02d} tolet"]
    label=bpy.data.objects[f"TOWN | TO LET fascia {i}"]
    existing=bvh([lot])
    # At 5 x samples per shutter leaf, existing glass or its mullions are behind the new face.
    subj=load(files[b-a])
    for ob in subj:
        if ob.parent is None:
            place=Matrix.Translation((x,y,0)) @ Matrix.Rotation(0 if sign<0 else math.pi,4,"Z")
            ob.matrix_world=place @ ob.matrix_world
    bpy.context.view_layer.update()
    overlay=bvh(subj)
    verts=[ob.matrix_world@v.co for ob in subj if ob.type=="MESH" for v in ob.data.vertices]
    max_projection=max(sign*(v.y-y) for v in verts)
    min_projection=min(sign*(v.y-y) for v in verts)
    assert .264 < min_projection < .28 and .36 < max_projection < .39, (i,min_projection,max_projection)
    assert min(v.x for v in verts)>a and max(v.x for v in verts)<b
    lane=(.54*(b-a)+.16-.24)/4
    gaps=[]
    for leaf in range(4):
        for dx in (-.30,-.14,0,.14,.30):
            for z in (.88,1.18,1.78,2.13,2.49):
                origin=(x+(leaf-1.5+dx)*lane,y+sign*1.25,z)
                vec=(0,-sign,0)
                new, old=ray(overlay,origin,vec,2),ray(existing,origin,vec,2)
                assert new is not None and old is not None and sign*(new.y-old.y)>.035,(i,origin,new,old)
                gaps.append(sign*(new.y-old.y))
    for sx in (-.8,0,.8):
        for h in (3.06,3.7,4.18):
            assert ray(overlay,(x+sx,y+sign*2,h),(0,-sign,0),2.5) is None
    assert label.dimensions.z>0 and max(v.z for v in verts)<3.0
    placements.append({"lot":i,"asset":files[b-a].name,"threeOrigin":[x,0,-y],"yawRad":0 if sign<0 else math.pi,
        "lotLineInboardM":round(.4-max_projection,6),"frontOfDonorHitMinM":round(min(gaps),6),"fitRays":len(gaps)})
record={"plan":"W0b three reserved TO LET fronts","lotsSHA256":pin,"scope":"optional static shutters; signs and street unchanged",
    "assets":{p.name:{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files.values()},
    "placements":placements}
(out/"proof.json").write_text(json.dumps(record,indent=2)+"\n")
bpy.ops.wm.save_as_mainfile(filepath=str(out/"closed-front-review.blend"))
print(json.dumps(record))
