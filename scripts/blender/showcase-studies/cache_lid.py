"""WSC-PROP-049 articulation study: turn donor mesh islands into a hinged cache."""
from collections import defaultdict
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
donor=assets/"wsc-prop-049-cache-chest.glb"
assert hashlib.sha256(donor.read_bytes()).hexdigest()=="03e5a5be98a5053a196c57977775c3984beb088df2b69d750cf1809d58e8d34a"
clear_scene()
s=bpy.context.scene;s.render.fps=24;s.frame_start=0;s.frame_end=28
def importer(p):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    return sorted(set(s.objects)-before,key=lambda o:o.name)
original,=importer(donor)
model=original.data
coords=[original.matrix_world@v.co for v in model.vertices]
parents=list(range(len(coords)))
def rep(i):
    while parents[i]!=i:
        parents[i]=parents[parents[i]];i=parents[i]
    return i
def join(a,b):parents[rep(a)]=rep(b)
weld={}
for i,v in enumerate(coords):
    k=tuple(round(q,6) for q in v)
    if k in weld:join(i,weld[k])
    else:weld[k]=i
for f in model.polygons:
    for j in f.vertices[1:]:join(f.vertices[0],j)
islands=defaultdict(list)
for p in model.polygons:islands[rep(p.vertices[0])].append(p)
work={k:[] for k in ('body','lid','shell','gasket','latch','barrels')}
def span(polys):
    xyz=[coords[i] for f in polys for i in f.vertices]
    return ([min(v[k] for v in xyz) for k in range(3)],[max(v[k] for v in xyz) for k in range(3)])
for polys in islands.values():
    lo,hi=span(polys)
    extent=[b-a for a,b in zip(lo,hi)]
    if len(polys)==108 and extent[0]>1.35 and extent[1]>.85 and lo[2]<.1<hi[2]:
        kind='shell'
    elif len(polys)==108 and extent[0]>1.4 and extent[1]>.9 and .62<lo[2]<.64:
        kind='gasket'
    elif extent[2]>.5 and extent[0]<.2 and hi[1]<-.5 and lo[2]>.14:
        kind='latch'
    elif .48<lo[1] and hi[1]>.54 and .61<lo[2]<.67 and hi[2]<.72:
        kind='barrels'
    elif lo[2]>.646 or (.632<lo[2] and hi[2]<.682 and any(p.material_index in (8,9) for p in polys)):
        kind='lid'
    else:kind='body'
    work[kind].extend(polys)
assert len(work['shell'])==108 and len(work['gasket'])==108 and len(work['latch'])==219
assert sum(map(len,work.values()))==16421
assert len(work['barrels'])>80
# Split by original welded islands, but retain donor normals on untouched surfaces.
def make(n,faces,shift=None,solid=False):
    mesh=bpy.data.meshes.new(n);vs=[];remap={};loops=[];ps=[]
    for face in faces:
        row=[]
        for st,i in enumerate(face.vertices):
            use=tuple(round(v,6) for v in coords[i]) if solid else i
            if use not in remap:
                remap[use]=len(vs);vs.append(coords[i] if shift is None else coords[i]-shift)
            row.append(remap[use]);loops.append(model.corner_normals[face.loop_start+st].vector.copy())
        ps.append(row)
    mesh.from_pydata(vs,[],ps)
    for m in model.materials:mesh.materials.append(m)
    for f,p in zip(mesh.polygons,faces):
        f.material_index=p.material_index;f.use_smooth=p.use_smooth
    mesh.update()
    if not solid:mesh.normals_split_custom_set(loops)
    o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o)
    if shift is not None:o.location=shift
    return o

hinge=Vector((0,.529,.66))
fixed=make("Cache_Body",work['body'])
barrels=make("Cache_HingeBarrels",work['barrels'])
lid=make("Cache_Lid",work['lid'],hinge)
shell=make("Cache_Tray",work['shell'],solid=True)
gasket=make("Cache_Gasket",work['gasket'],solid=True)
catch=make("Cache_Latch_Lower",work['latch'],solid=True)
catch_top=make("Cache_Latch_Upper",work['latch'],solid=True)

def apply_mod(obj,mod):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
def carved(obj,where,dim,othermat,keep=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=where)
    c=bpy.context.object;c.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    c.data.materials.append(model.materials[othermat])
    m=obj.modifiers.new(("Isolate" if keep else "Cut")+" volume","BOOLEAN")
    m.operation='INTERSECT' if keep else 'DIFFERENCE';m.solver='EXACT';m.object=c
    apply_mod(obj,m)
    bpy.data.objects.remove(c,do_unlink=True)
    assert len(obj.data.polygons)>0, obj.name
# Replace only hidden interior geometry. Opening is 1.204 × .684 m, with bottom at .16.
carved(shell,(0,0,.48),(1.204,.684,.64),7)
carved(gasket,(0,0,.48),(1.204,.684,.64),7)
# Front latch overlaps the accent medallion in the donor; separate it just below the cap.
carved(catch,(0,-.53,.322),(1,.45,.644),4,True)
carved(catch_top,(0,-.53,.827),(1,.45,.354),4,True)
catch_top.data.transform(Matrix.Translation(-hinge))
catch_top.parent=lid
bpy.context.view_layer.update()

def material(n,c,metal,rough):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Metallic"].default_value=metal;q.inputs["Roughness"].default_value=rough
    return m
interior=material("Cache interior | graphite liner",(.047,.065,.077),.15,.58)
rail=material("Cache liner | brass lip",(.52,.285,.084),.62,.32)
darker=material("Cache liner | underside pressed panel",(.071,.096,.111),.37,.43)
def box(n,p,d,ma,bevel=.014,apply=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
    if bevel:
        v=o.modifiers.new("Soft edges","BEVEL");v.width=bevel;v.segments=2
        o.modifiers.new("Face normals","WEIGHTED_NORMAL")
        if apply:
            for mod in tuple(o.modifiers):apply_mod(o,mod)
    return o

inners=[box("Cache_Interior_Tray", (0,0,.163),(1.190,.670,.035),interior, .010,True)]
for x in (-.592,.592):
    inners.append(box("Cache_Interior_LinerSide",(x,0,.303),(.015,.666,.264),interior,.004,True))
for y in (-.334,.334):
    inners.append(box("Cache_Interior_LinerEnd",(0,y,.303),(1.19,.013,.263),interior,.004,True))
for x in (-.529,.529):
    inners.append(box("Cache_Interior_BrassRib",(x,0,.19),(.038,.632,.021),rail,.006,True))
for y in (-.291,.291):
    inners.append(box("Cache_Interior_BrassEnd",(0,y,.19),(1.028,.028,.021),rail,.006,True))

# Compute object local translation relative to the hinge in the closed pose.
moving=[lid,catch_top]
liner=box("Cache_Lid_Underside",(0,0,.647),(1.152,.660,.028),darker,.012,True)
liner.parent=lid;liner.location-=hinge;moving.append(liner)
for x in (-.426,.426):
    strip=box("Cache_Lid_Underside_Rib",(x,0,.628),(.049,.545,.023),rail,.004,True)
    strip.parent=lid;strip.location-=hinge;moving.append(strip)
static=[fixed,barrels,shell,gasket,catch,*inners]

def check_empty_center(pieces):
    # Downward beam through the opening should hit only the bowl bottom.
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    bvh=[(o,BVHTree.FromObject(o,dg),o.matrix_world.inverted()) for o in pieces]
    for x in (-.49,0,.49):
        for y in (-.24,0,.24):
            hits=[]
            for o,b,t in bvh:
                hit,_n,_i,_t=b.ray_cast(t@Vector((x,y,2)),t.to_3x3()@Vector((0,0,-1)),5)
                if hit is not None:hits.append((float((o.matrix_world@hit).z),o.name))
            assert hits and max(hits)[0]<.20,(x,y,hits)
check_empty_center(static)
bpy.data.objects.remove(original,do_unlink=True)
lid.rotation_mode='XYZ'
for f,r in [(0,0),(4,0),(20,-1.77),(28,-1.95)]:
    lid.rotation_euler.x=r;lid.keyframe_insert(data_path='rotation_euler',frame=f)
lid.animation_data.action.name="Cache open"
s.frame_set(0)
bpy.ops.object.select_all(action='DESELECT')
for o in static+moving:o.select_set(True)
bpy.context.view_layer.objects.active=lid
glb=out/"wsc-prop-049-cache-chest-opening.glb"
raw=out/"cache-articulation-raw.glb"
bpy.ops.export_scene.gltf(filepath=str(raw),use_selection=True,export_format='GLB',export_animations=True,
                        export_animation_mode='ACTIONS',export_force_sampling=True,export_texcoords=False)
subprocess.run(["node",str(Path(__file__).with_name("cache_lid_pack.mjs")),os.environ["WSC_GLTF_MODULES"],str(raw),str(glb)],check=True)
for o in static+moving:bpy.data.objects.remove(o,do_unlink=True)
now=importer(glb)
pivot=next(o for o in now if o.name=='Cache_Lid')
assert (pivot.location-hinge).length<1e-5
# Child hardware travels exactly with the hinge, but the fixed lower lock stays on its base.
def moving_part(o):
    return o==pivot or bool(o.parent and moving_part(o.parent))
fixedagain=[o for o in now if o.type=="MESH" and not moving_part(o)]
movingagain=[o for o in now if o.type=="MESH" and moving_part(o)]
def build_bvh(items):
    vertices=[];faces=[]
    for o in items:
        n=len(vertices)
        vertices.extend(o.matrix_world@q.co for q in o.data.vertices)
        o.data.calc_loop_triangles()
        faces.extend(tuple(n+j for j in f.vertices) for f in o.data.loop_triangles)
    return BVHTree.FromPolygons(vertices,faces,all_triangles=True),vertices,faces
check_empty_center(fixedagain)
s.frame_set(0);bpy.context.view_layer.update()
key=next(o for o in now if o.name=='Cache_Latch_Upper')
before=key.matrix_world.copy()
bounds=[v for o in now if o.type=='MESH' for v in (o.matrix_world@p.co for p in o.data.vertices)]
# Beyond the first opening contact, overlap should be confined to the modeled rear hinge zone.
anchor,xyz,tri=build_bvh(fixedagain)
late_sweep={}
for f in (11,14,17,20,23,28):
    s.frame_set(f);bpy.context.view_layer.update()
    moving_bvh,_,_=build_bvh(movingagain)
    hits=anchor.overlap(moving_bvh)
    if hits:
        assert min(xyz[k].y for a,_ in hits for k in tri[a])>.43,f
    late_sweep[f]=len(hits)
dim=[round(max(v[k] for v in bounds)-min(v[k] for v in bounds),4) for k in range(3)]
assert all(abs(a-b)<.005 for a,b in zip(dim,(1.606,1.161,.892))),dim
s.frame_set(28);bpy.context.view_layer.update()
assert abs(key.matrix_world.to_quaternion().rotation_difference(before.to_quaternion()).angle-1.95)<.001
for o in now:
    if o.type=='MESH':o.data.calc_loop_triangles()
num=sum(len(o.data.loop_triangles) for o in now if o.type=='MESH')
print(dict(bytes=glb.stat().st_size,triangles=num,closed_size=dim))
(out/"cache-lid-check.json").write_text(json.dumps(dict(size_bytes=glb.stat().st_size,triangles=num,closed_size_m=dim,
    gltf_hinge_m=(0,hinge.z,-hinge.y),open_radians=-1.95,seconds=28/24,open_cavity_rays=9,late_sweep_pairs_inside_hinge_zone=late_sweep),indent=2)+"\n")

stage=material("Graphite studio plinth",(.042,.083,.11),.22,.71)
bg=material("Blue studio floor",(.044,.065,.075),.11,.78)
typeink=material("Cream proof type",(.83,.87,.85),.05,.58)
tealink=material("Mint proof type",(.155,.68,.59),.05,.56)
for ma in (typeink,tealink):
    q=ma.node_tree.nodes.get("Principled BSDF")
    q.inputs["Emission Color"].default_value=q.inputs["Base Color"].default_value
    q.inputs["Emission Strength"].default_value=.31
def label(word,size,co,ma):
    c=bpy.data.curves.new(word,"FONT");c.body=word;c.size=size;c.align_x="CENTER"
    o=bpy.data.objects.new(word,c);bpy.context.collection.objects.link(o)
    o.location=co;o.rotation_euler.x=.85;c.materials.append(ma)
for x,f,title in [(-1.52,0,"01  /  CLOSED"),(1.52,28,"02  /  OPEN · 111.7°")]:
    s.frame_set(f);bpy.context.view_layer.update()
    pose=Matrix.Translation((x,0,0))@Matrix.Rotation(math.radians(-16),4,'Z')
    for o in now:
        if o.type=="MESH":
            q=bpy.data.objects.new(title+" | "+o.name,o.data)
            bpy.context.collection.objects.link(q);q.matrix_world=pose@o.matrix_world
    box(title+" display", (x,0,-.064),(2.64,2.43,.128),stage,.052)
    label(title,.138,(x,-1.13,.030),typeink)
for o in now:bpy.data.objects.remove(o,do_unlink=True)
box("Studio ground",(0,0,-.208),(200,200,.15),bg,0)
label("WEST CACHE  /  HINGE STUDY",.251,(0,1.54,2.18),typeink)
label("WSC-PROP-049    ·    REIMPORT OF THE OPENING CLIP",.106,(0,1.47,1.91),tealink)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,w,sz,c in [((-3,-4,6),860,4,(1,.84,.66)),((4,-1,4),510,4,(.71,.9,1)),((0,4,5),920,4,(.74,1,.94))]:
    bpy.ops.object.light_add(type="AREA",location=p);o=bpy.context.object;o.data.energy=w;o.data.size=sz;o.data.color=c
    aim(o,(0,0,.6))
bpy.ops.object.camera_add(location=(0,-6.9,4.8));s.camera=bpy.context.object;aim(s.camera,(0,0,.79))
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=6.08
s.world.color=(.14,.18,.20)
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1500;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-cache-opening-study.jpg")
bpy.ops.render.render(write_still=True)
