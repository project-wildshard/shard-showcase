"""Fit three W0b signs against exact rebuilt donors, adding only a Movers header."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import export
parser=argparse.ArgumentParser()
parser.add_argument("town",type=Path)
parser.add_argument("out",type=Path)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
out=args.out.resolve()
out.mkdir(parents=True,exist_ok=True)
repo=HERE.parents[2]
kit=repo/"public/assets/wildshard-art/w0b-town-gate-nameplates.glb"
kit_hash=hashlib.sha256(kit.read_bytes()).hexdigest()
assert kit_hash=="2daf80f5fa5f5bcdf22aeec26d2113a72d36250c864064fdb403d9a50718e480"
bpy.ops.wm.open_mainfile(filepath=str(args.town.resolve()))
scene=bpy.context.scene

def mat(n,c,r,metal=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*c,1)
    bs.inputs["Roughness"].default_value=r
    bs.inputs["Metallic"].default_value=metal
    m.diffuse_color=(*c,1)
    return m

oak=mat("Movers header | seasoned oak",(.233,.116,.055),.68)
end=mat("Movers header | smoked grain ends",(.096,.058,.029),.69)
band=mat("Movers header | blue steel",(.094,.198,.208),.40,.58)
pins=mat("Movers header | warm peened rivets",(.44,.259,.101),.40,.61)

def box(n,p,d,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        a=o.modifiers.new("Dressed tool edge","BEVEL")
        a.width=b;a.segments=1
        o.modifiers.new("Broad timber surface normals","WEIGHTED_NORMAL")
        bpy.ops.object.convert(target="MESH")
    return o

parts=[box("Carrier beam",(0,0,0),(13.85,1.36,.80),oak,.036)]
for side in (-1,1):
    x=side*6.895
    parts.append(box("End-grain steel cladding",(x,0,0),(.082,1.28,.715),end,.014))
    for at in (side*5.71,side*6.35):
        parts.append(box("Pressed face strap",(at,-.681,0),(.263,.051,.735),band,.009))
        parts.append(box("Top strap lug",(at,0,.397),(.263,1.335,.014),band,.003))
        for dz in (-.254,.254):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.052,depth=.024,location=(at,-.717,dz),rotation=(math.pi/2,0,0))
            o=bpy.context.object;o.name="Pin head";o.data.materials.append(pins);parts.append(o)
batches=[]
groups={m:[o for o in parts if o.data.materials[0]==m] for m in (oak,end,band,pins)}
for m,obs in groups.items():
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    if len(obs)>1:bpy.ops.object.join()
    o=bpy.context.object;o.name=m.name;batches.append(o)
asset=out/"w0b-movers-gate-header.glb"
export(batches,asset)
raw=asset.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
prims=[p for m in doc["meshes"] for p in m["primitives"]]
tris=sum(doc["accessors"][p["indices"]]["count"]//3 for p in prims)
assert len(prims)==4 and tris<950 and len(raw)<80000
assert not any(k in doc for k in ("images","skins","animations","cameras"))
for o in batches:bpy.data.objects.remove(o,do_unlink=True)

def load(p):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    return {o.name:o for o in set(scene.objects)-prior}

def coords(o,transform=None):
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    return vs if transform is None else [transform@p for p in vs]

def bounds(ps):
    return [(min(p[i] for p in ps),max(p[i] for p in ps)) for i in range(3)]

def bvh(os,T=None):
    vs=[];fs=[]
    for o in os:
        i=len(vs);vs.extend(coords(o,T))
        fs.extend(tuple(i+d for d in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)

header=load(asset)
assert len(header)==4
keystone=next(o for n,o in header.items() if n.startswith(oak.name))
header_origin=Vector((-95,60,6.8))
for o in header.values():o.matrix_world=Matrix.Translation(header_origin)@o.matrix_world
bpy.context.view_layer.update()
assert abs(bounds(coords(keystone))[2][0]-6.4)<1e-5
mover_piers=[o for o in scene.objects if o.type=="MESH" and o.name.startswith(("Gate pier","Pier crown")) and o.matrix_world.translation.x<-80]
assert len(mover_piers)==4,[(o.name,o.location[:]) for o in mover_piers]
crowns=[o for o in mover_piers if o.name.startswith("Pier crown")]
assert len(crowns)==2 and all(abs(bounds(coords(o))[2][1]-6.4)<.00001 for o in crowns)
cover=[]
carrier=bounds(coords(keystone))
for o in crowns:
    b=bounds(coords(o))
    cover.append(min(carrier[0][1],b[0][1])-max(carrier[0][0],b[0][0]))
assert min(cover)>1.9

signs=load(kit)
anchors={k:signs[k+" Gate"] for k in ("Stable","Movers","West")}
allowed=set(anchors.values())
for o in [o for o in signs.values() if o.parent is None and o not in allowed]:
    for ch in list(o.children_recursive):bpy.data.objects.remove(ch,do_unlink=True)
    bpy.data.objects.remove(o,do_unlink=True)
mount=mat("Removable pad | blackened iron",(.055,.051,.042),.48,.62)
config=(
    ("Stable",(-36,60),0,scene.objects["Stable Gate sign board"],12.0,
     [o for o in scene.objects if o.name.startswith("New Stable Gate stone pier")],
     ["Stable Gate sign inset","Stable Gate clear lettering"]),
    ("Movers",(-95,60),0,keystone,10.4,
     [o for o in mover_piers if o.name.startswith("Gate pier")],[]),
    ("West",(-128,0),math.pi/2,scene.objects["ZIP | West Gate beam"],12.0,
     [o for o in scene.objects if o.name.startswith("ZIP | West Gate pier")],[]),
)
proof={}
CAMERAS=[]
for key,(x,y),yaw,beam,width,piers,hide in config:
    assert len(piers)==2,(key, [o.name for o in piers])
    gate=Matrix.Translation((x,y,0))@Matrix.Rotation(yaw,4,"Z")
    inv=gate.inverted()
    bb=bounds(coords(beam,inv))
    mid=(bb[2][0]+bb[2][1])/2
    front=bb[1][0]
    sign=anchors[key]
    # Reset swatch position and rot in one transform; retain exact sign children.
    sign.matrix_world=gate@Matrix.Translation((0,front-.030,mid))
    for n in hide:
        o=scene.objects[n]
        o.hide_render=True
    bpy.context.view_layer.update()
    f,=[o for o in sign.children if o.name.startswith("Frame")]
    sb=bounds(coords(f,inv))
    margins=[sb[0][0]-bb[0][0],bb[0][1]-sb[0][1],sb[2][0]-bb[2][0],bb[2][1]-sb[2][1]]
    assert abs(sb[1][1]-front+.030)<.0001 and min(margins)>.006,(key,sb,bb,margins)
    plate=bvh([beam],inv)
    seats=[]
    for sx in (-1.485,1.485):
        for sz in (-.157,.157):
            for dx,dz in ((0,0),(-.04,0),(.04,0),(0,-.04),(0,.04)):
                hit,n,*_=plate.ray_cast(Vector((sx+dx,front-.21,mid+sz+dz)),Vector((0,1,0)),.4)
                assert hit and n.y<-.999 and abs(hit.y-front)<.0002,(key,hit,n)
            seats.append(tuple(gate@Vector((sx,front,mid+sz))))
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.045,depth=.034)
            pad=bpy.context.object
            pad.name=f"{key} · mount contact study"
            pad.data.materials.append(mount)
            pad.matrix_world=gate@Matrix.Translation((sx,front-.015,mid+sz))@Matrix.Rotation(math.pi/2,4,"X")
    ordered=sorted((bounds(coords(o,inv)) for o in piers),key=lambda a:a[0][0])
    left,right=ordered[0][0][1],ordered[1][0][0]
    assert abs(right-left-width)<.0001 and abs(left+right)<.0001
    clearance=bvh([beam,*piers],inv)
    rays=0
    for k in range(29):
        u=(k/28-.5)*(width-.10)
        for h in (.25,.8,1.7,2.6,4.5):
            hit,*_=clearance.ray_cast(Vector((u,-3,h)),Vector((0,1,0)),6)
            assert hit is None,(key,u,h,hit)
            rays+=1
    # Measured matching eye height; the view faces out of town.
    eye=gate@Vector((1.4,-16.5,1.7))
    look=gate@Vector((0,3,3.28))
    CAMERAS.append((key,eye,look))
    proof[key]=dict(world_three_xz_m=[x,-y],yaw_deg=round(math.degrees(yaw),4),
        beam=beam.name,front_local_y_m=round(front,4),frame_margins_m=[round(v,4) for v in margins],
        clear_at_piers_m=width,unblocked_through_beam_and_piers_rays=rays,
        mounting_rays=20,stud_contacts_blender_m=[[round(a,4) for a in p] for p in seats],
        legacy_render_only_hidden=hide)

preview=bool(os.environ.get("WSC_METADATA_ONLY")!="1")
world=bpy.data.worlds.new("Matched town-gate blue sky")
world.use_nodes=True
g=world.node_tree.nodes["Background"];g.inputs[0].default_value=(.53,.64,.85,1);g.inputs[1].default_value=.43
scene.world=world
for o in list(scene.objects):
    if o.type=="LIGHT":o.hide_render=True
d=bpy.data.lights.new("Gate light","SUN");d.energy=2.55;d.angle=.16;d.color=(1,.83,.64)
o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o)
o.rotation_euler=Vector((-.43,.60,-.87)).to_track_quat("-Z","Y").to_euler()
scene.render.engine="CYCLES";scene.cycles.samples=30
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.076;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x,scene.render.resolution_y=1440,900
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=91
for name,eye,target in CAMERAS:
    bpy.ops.object.camera_add(location=eye)
    cam=bpy.context.object;scene.camera=cam
    cam.data.lens=35;cam.data.clip_end=260
    cam.rotation_euler=(target-eye).to_track_quat("-Z","Y").to_euler()
    bpy.context.view_layer.update()
    f,=[o for o in anchors[name].children if o.name.startswith("Frame")]
    projected=[world_to_camera_view(scene,cam,p) for p in coords(f)]
    assert all(.1<q.x<.9 and .11<q.y<.93 and q.z>0 for q in projected),name
    proof[name]["frame_height_px"]=round((max(q.y for q in projected)-min(q.y for q in projected))*900,2)
    scene.render.filepath=str(out/("nov25-w0b-"+name.lower()+"-gate.jpg"))
    if preview:bpy.ops.render.render(write_still=True)
report={
    "scope":"Visual fit to regenerated art baseline, not native placement, navigation, performance or routing.",
    "archived_layout_blob":"5d019a020361c47187ec889f2bc947f82cd9f98a",
    "sign_kit_sha256":kit_hash,"placements":proof,
    "movers_header":{"bytes":len(raw),"triangles":tris,"draws":len(prims),
       "sha256":hashlib.sha256(raw).hexdigest(),"crown_overlap_each_m":[round(v,4) for v in cover]},
}
(out/"w0b-north-west-gate-fit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report),flush=True)
