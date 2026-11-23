"""Build and measure distant versions without changing either near tree donor."""
from collections import defaultdict
from itertools import product
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

root=Path(__file__).resolve().parents[3]
assets=root/"public/assets/wildshard-art"
out=output_directory()
s=bpy.context.scene
specs=[
    ("wsc-prop-012-deciduous-tree","83685e45bd4ef2af08941de87909aaf0f7078dbecfe784bc06a9fc8fc4d8a355",.14,.55),
    ("wsc-prop-046-conifer-tree","a5b52da910f80f33a40fad2ba15d5e7904c0d2f3b1b438d4b6401971ace8c18d",.33,.42),
]

def open_glb(path):
    prior=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
    return sorted((o for o in set(s.objects)-prior if o.type=="MESH"),key=lambda o:o.name)

def stats(f):
    b=f.read_bytes();assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    d=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    assert not any(k in d for k in ("images","animations","skins"))
    return len(b),sum(d["accessors"][p["indices"]]["count"]//3 for m in d["meshes"] for p in m["primitives"])

def world_mesh(os,tree=False):
    vv=[];ff=[]
    for o in os:
        base=len(vv)
        vv.extend(o.matrix_world@p.co for p in o.data.vertices)
        ff.extend(tuple(base+i for i in p.vertices) for p in o.data.polygons)
    if tree:return BVHTree.FromPolygons(vv,ff)
    return tuple(tuple(fn(p[k] for p in vv) for k in range(3)) for fn in (min,max))

def canopy(o,frac,chosen_scale):
    # A welded component maps to a whole leaf or spray. Keep a spatially
    # stratified subset by projected extent, not disconnected triangle noise.
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    todo=set(bm.verts);components=[]
    bm.verts.index_update()
    while todo:
        start=min(todo,key=lambda v:v.index)
        todo.remove(start);q=[start];whole=[]
        while q:
            v=q.pop();whole.append(v)
            for e in v.link_edges:
                t=e.other_vert(v)
                if t in todo:todo.remove(t);q.append(t)
        world=[o.matrix_world@v.co for v in whole]
        center=sum(world,Vector((0,0,0)))/len(whole)
        reach=max((v-center).length for v in world)
        components.append((center,reach,whole))
    mid=sum((x[0] for x in components),Vector((0,0,0)))/len(components)
    cells=defaultdict(list)
    for i,(center,reach,vv) in enumerate(components):
        cells[tuple(int(math.floor(p/chosen_scale)) for p in center)].append((reach+.08*(center-mid).length,i,vv))
    drop=set()
    for val in cells.values():
        val.sort(reverse=True,key=lambda x:(x[0],-x[1]))
        keep=max(1,math.ceil(len(val)*frac))
        drop.update(v for _,_,vs in val[keep:] for v in vs)
    bmesh.ops.delete(bm,geom=list(drop),context="VERTS")
    bm.to_mesh(o.data);bm.free()
    return len(components),len(cells)

def collapse(o,ratio):
    bpy.context.view_layer.objects.active=o
    dec=o.modifiers.new("Distance reduction","DECIMATE")
    dec.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=dec.name)

def silhouettes(os,ts):
    a,b=world_mesh(os),world_mesh(ts)
    old,new=world_mesh(os,True),world_mesh(ts,True)
    lo,hi=a
    corners=[Vector(p) for p in product(*zip(lo,hi))]
    scale=(Vector(hi)-Vector(lo)).length*1.14
    aim=Vector(tuple((u+v)/2 for u,v in zip(lo,hi)))
    rows=[]
    for n,elev in product(range(8),(.0,.12)):
        angle=n*math.tau/8
        face=Vector((math.cos(angle),math.sin(angle),elev)).normalized()
        h=Vector((-math.sin(angle),math.cos(angle),0))
        v=face.cross(h)
        span_h=2.15*max(abs(h.dot(p-aim)) for p in corners)
        span_v=2.15*max(abs(v.dot(p-aim)) for p in corners)
        base=aim+face*scale*3
        hit=union=0
        for x,y in product(range(58),range(82)):
            pos=base+h*((x+.5-29)/58*span_h)+v*((y+.5-41)/82*span_v)
            p=old.ray_cast(pos,-face,scale*7)[0] is not None
            q=new.ray_cast(pos,-face,scale*7)[0] is not None
            hit+=p and q;union+=p or q
        rows.append(hit/union)
    return round(min(rows),5),round(sum(rows)/len(rows),5),round(max(abs(x-y) for i,j in zip(a,b) for x,y in zip(i,j)),4)

metrics={}
for i,(key,sha,frac,cell) in enumerate(specs):
    clear_scene()
    source=assets/(key+".glb")
    assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
    original=open_glb(source)
    candidates=[]
    for o in original:
        new=o.copy();new.data=o.data.copy();s.collection.objects.link(new)
        new.name="Distant · "+o.name;candidates.append(new)
    if i==0:
        for o in candidates:
            if "individual" in o.name:canopy(o,frac,cell)
            if "trunk" in o.name:collapse(o,.77)
    else:
        for o in candidates:
            if "sprays" in o.name:canopy(o,frac,cell)
            else:collapse(o,.84)
    dz=world_mesh(original)[0][2]-world_mesh(candidates)[0][2]
    for o in candidates:o.location.z+=dz
    bpy.context.view_layer.update()
    f=out/(key+"-far.glb");export(candidates,f)
    loaded=open_glb(f)
    iou,mean,delta=silhouettes(original,loaded)
    orig=stats(source);far=stats(f)
    metrics[key]={"near_bytes":orig[0],"near_triangles":orig[1],"far_bytes":far[0],"far_triangles":far[1],
        "min_silhouette_iou_16_views":iou,"mean_silhouette_iou_16_views":mean,"bounds_max_delta_m":delta,
        "bounds_z_min_near_far":[round(world_mesh(original)[0][2],4),round(world_mesh(loaded)[0][2],4)]}
    print(key,metrics[key],flush=True)
    assert far[0]<orig[0]*.73 and far[1]<orig[1]*.70
    assert iou>=.90 and mean>=.91
    assert abs(world_mesh(original)[0][2]-world_mesh(loaded)[0][2])<.025
(out/"validation.json").write_text(json.dumps(metrics,indent=2)+"\n")

clear_scene()
for idx,(key,*_) in enumerate(specs):
    for j,far in enumerate((False,True)):
        src=out/(key+"-far.glb") if far else assets/(key+".glb")
        os=open_glb(src)
        lo,hi=world_mesh(os)
        z=(hi[2]-lo[2])
        # Each species is displayed normalized to the same view height, never
        # used as a runtime transform. The two views of a species share scale.
        scale=1.45/z if not far else kept
        kept=scale
        for o in os:
            o.scale*=scale
            o.location*=scale
            o.location.x+=(-2.25,-.75,.75,2.25)[idx*2+j]
            o.location.z-=lo[2]*scale

def material(n,base):
    m=bpy.data.materials.new(n);m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"];bs.inputs["Base Color"].default_value=(*base,1)
    bs.inputs["Roughness"].default_value=.8
    return m

ground=material("Soft desaturated blue studio",(.068,.118,.144))
ink=material("Ground label",(.6,.69,.65))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.017))
bpy.context.object.data.materials.append(ground)
for j,name in enumerate(("OAK   /   NEAR","OAK   /   FAR","CONIFER   /   NEAR","CONIFER   /   FAR")):
    font=bpy.data.curves.new(name,"FONT");font.body=name;font.align_x="CENTER";font.size=.139
    font.materials.append(ink)
    o=bpy.data.objects.new(name,font);s.collection.objects.link(o);o.location=((j-1.5)*1.5,-.81,-.012)
    o.rotation_euler.x=.43

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(name,p,power,color,size):
    l=bpy.data.lights.new(name,"AREA");l.energy=power;l.color=color;l.size=size
    o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.location=p;aim(o,(0,0,.75))
s.world=bpy.data.worlds.new("Cool ambient");s.world.color=(.12,.19,.24)
area("Sunlit warm key",(-2,-3,4.7),650,(1,.79,.56),3.2)
area("Neutral broad bounce",(4,-2,3),430,(.65,.85,1),3.2)
area("Green-blue rim",(0,3,3.3),850,(.68,.88,1),3.1)
c=bpy.data.cameras.new("Distance geometry comparison");s.camera=bpy.data.objects.new(c.name,c)
s.collection.objects.link(s.camera);s.camera.location=(0,-8,3);aim(s.camera,(0,0,.68))
c.type="ORTHO";c.ortho_scale=6.35
s.render.engine="CYCLES";s.cycles.samples=58;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1512;s.render.resolution_y=620;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=92
s.render.filepath=str(out/"nov23-tree-distance-study.jpg")
bpy.ops.render.render(write_still=True)
