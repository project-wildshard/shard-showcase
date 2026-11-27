"""WSC-PROP-058: simpler, pivot-matched container for far shelter rows."""
import hashlib
import json

from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index("--")+1:]
out=Path(args[0])
out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[3]
donor=root/"public/assets/wildshard-art/wsc-prop-058-shipping-container.glb"
pin="8bd1c2bca075256315a8bf5a76b5da489b3e42fca0def63d06088031695232af"
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(donor))
s=bpy.context.scene
original=[o for o in s.objects if o.type=="MESH"]
palette={m.name:m for m in bpy.data.materials}
buckets={}

def put(m,verts,faces):
    p,f=buckets.setdefault(m,([],[]))
    n=len(p)
    p.extend(verts)
    f.extend(tuple(i+n for i in poly) for poly in faces)

def box(m,x,y,z,sx,sy,sz):
    p=[(x+i*sx/2,y+j*sy/2,z+k*sz/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    faces=((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5))
    put(m,p,faces)

deep="deep"
shell="orange2"
edge="orange3"
rib="orange4"
steel="steel"
box(shell,0,.009,1.30,2.134,4.30,2.223)
# Matching side planes and formed corrugations without disconnected bevel blocks.
for sign in (-1,1):
    step=(2.14-(-2.05))/21
    for i in range(21):
        start=-2.05+i*step
        pts=[(sign*x,start+step*t) for t,x in ((0,1.08),(.24,1.175),(.77,1.175),(1,1.08))]
        for j,(a,b) in enumerate(zip(pts,pts[1:])):
            vs=[(*a,.19),(*b,.19),(*b,2.36),(*a,2.36)]
            put(rib if j==1 else shell,vs,[(0,1,2,3) if sign>0 else (3,2,1,0)])
    for z in (.10,2.44):
        box(edge,sign*1.132,.01,z,.139,4.53,.161)
    for y in (-2.198,2.18):
        box(edge,sign*1.135,y,1.275,.140,.203,2.545)
        for z in (.135,2.408):
            box(deep,sign*1.173,y,z,.098,.213,.124)
for y in (-2.209,2.202):
    for z in (.126,2.448):
        box(edge,0,y,z,2.295,.139,.165)
box(edge,0,.013,2.463,2.19,4.362,.126)
for x in (-.89,-.59,-.29,0,.29,.59,.89):
    box(rib,x,.04,2.520,.089,4.18,.017)
# Bottom skids preserve the original 2.5 mm ground offset.
for x in (-.99,.99):
    box(deep,x,.008,.053, .16,4.23,.101)

# Rear doors open toward Blender -Y. Keep their seam, keep the locking bars
# and replace the tiny label geometry with one subdued maker plate.
box(deep,0,-2.160,1.285,2.16,.115,2.14)
for x in (-.539,.539):
    box(rib,x,-2.233,1.286,1.042,.102,2.04)
    for h in (-.30,-.10,.10,.30):
        box(shell,x+h,-2.287,1.29,.079,.042,1.86)
    for pole in (-.247,.247):
        xx=x+pole
        box(steel,xx,-2.317,1.286,.036,.040,1.997)
        for z in (.408,2.14):
            box(deep,xx,-2.335,z,.095,.028,.061)
    for z in (.46,1.36,2.08):
        box(steel,(-.959 if x<0 else .959),-2.318,z,.137,.054,.091)
    box(steel,x-.081,-2.371,1.18,.242,.087,.064)
box(steel,-.67,-2.322,1.60,.272,.035,.151)
box("ink",.74,-2.317,1.61,.119,.008,.037)
box(shell,0,2.197,1.285,2.12,.125,2.196)
for x in [i*.159 for i in range(-6,7)]:
    box(rib,x,2.253,1.28,.066,.045,2.12)

far=[]
for m,(p,f) in sorted(buckets.items()):
    me=bpy.data.meshes.new("Far container | "+m)
    me.from_pydata(p,[],f); me.update()
    ob=bpy.data.objects.new(me.name,me)
    s.collection.objects.link(ob)
    me.materials.append(palette[m])
    far.append(ob)
bpy.ops.object.select_all(action="DESELECT")
for ob in far:ob.select_set(True)
bpy.context.view_layer.objects.active=far[0]
glb=out/"wsc-prop-058-shipping-container-far.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,export_animations=False)

def inventory(file):
    b=file.read_bytes()
    assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    j=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    prim=[p for m in j["meshes"] for p in m["primitives"]]
    assert not any(k in j for k in ("images","textures","skins","animations"))
    return dict(bytes=len(b),triangles=sum(j["accessors"][p["indices"]]["count"]//3 for p in prim),
                primitives=len(prim),sha256=hashlib.sha256(b).hexdigest())

a,b=inventory(donor),inventory(glb)
assert b["triangles"]<=1700 and b["bytes"]<100000 and b["primitives"]<=7
for ob in far:bpy.data.objects.remove(ob,do_unlink=True)
before=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(glb))
far=[o for o in s.objects if o.type=="MESH" and o not in before]
assert len(far)==b["primitives"] and all(o.matrix_world.is_identity for o in far)

def geo(obs):
    p,f=[],[]
    for o in obs:
        n=len(p)
        p.extend(o.matrix_world@v.co for v in o.data.vertices)
        f.extend(tuple(n+i for i in poly.vertices) for poly in o.data.polygons)
    bounds=[(min(v[i] for v in p),max(v[i] for v in p)) for i in range(3)]
    return bounds,BVHTree.FromPolygons(p,f)
ba,ta=geo(original)
bb,tb=geo(far)
delta=max(abs(x-y) for ar,br in zip(ba,bb) for x,y in zip(ar,br))
assert delta<.000002,(ba,bb,delta)
assert abs(ba[2][0]-bb[2][0])<1e-5

# Occupancy comparison on three axes; this uses silhouette overlap, not photometry.
overlap={}
for axis in range(3):
    u,v=[i for i in range(3) if i!=axis]
    hits=union=0
    for i in range(81):
        for j in range(81):
            p=Vector((0,0,0));p[axis]=ba[axis][1]+1
            p[u]=(ba[u][0]-.10)+(ba[u][1]-ba[u][0]+.20)*(i+.5)/81
            p[v]=(ba[v][0]-.10)+(ba[v][1]-ba[v][0]+.20)*(j+.5)/81
            d=Vector((0,0,0));d[axis]=-1
            x=ta.ray_cast(p,d)[0] is not None
            y=tb.ray_cast(p,d)[0] is not None
            hits+=int(x and y);union+=int(x or y)
    overlap["XYZ"[axis]]=round(hits/union,5)
assert min(overlap.values())>.970,overlap

# Reuse all full-scale positions and scales from the existing shadow-pool
# composition. Report exact differences rather than duplicating the scene.
yard=json.loads((root/"project/layouts/e5b-shadow-study.json").read_text())
placements=[o for o in yard["placements"] if o["asset"]=="container"]
assert len(placements)>1
(out/"e5b-container-far-proof.json").write_text(json.dumps(dict(
    scope="Far static art only. Source/near model, placement, collision, shadow pools and runtime unchanged.",
    catalogue_id="WSC-PROP-058",source=a,far=b,
    max_bound_delta_m=round(delta,6),source_bounds_m=ba,far_bounds_m=bb,
    orthographic_silhouette_iou_by_axis=overlap, rays_per_axis=81*81,
    placement_reference="project/layouts/e5b-shadow-study.json",
    existing_container_placements=len(placements),
),indent=2)+"\n")
if "--proof-only" in args: raise SystemExit(0)

# Same camera/lighting per comparison; no changes to the production scene.
bpy.ops.mesh.primitive_plane_add(size=125,location=(0,0,.002))
floor=bpy.context.object
floor_mat=bpy.data.materials.new("Yard floor")
floor_mat.use_nodes=True
bs=floor_mat.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(.118,.15,.16,1)
bs.inputs["Roughness"].default_value=.79
floor.data.materials.append(floor_mat)
s.world=bpy.data.worlds.new("Clear yard sky");s.world.use_nodes=True
bg=s.world.node_tree.nodes.get("Background")
bg.inputs[0].default_value=(.26,.42,.63,1);bg.inputs[1].default_value=.55
bpy.ops.object.light_add(type="SUN",rotation=(.49,-.51,-.29))
bpy.context.object.data.energy=2.60;bpy.context.object.data.angle=.06
bpy.context.object.data.color=(1,.86,.68)
bpy.ops.object.camera_add()
cam=bpy.context.object;s.camera=cam
cam.data.lens=34
t=Vector((0,0,1.25))
s.render.engine="CYCLES";s.cycles.samples=30
s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.081
s.render.resolution_x=760;s.render.resolution_y=900
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=94
for meter,eye in [(15,(.78,-1.0,.21)),(32,(1.0,-.44,.13))]:
    cam.location=t+Vector(eye).normalized()*meter
    cam.rotation_euler=(t-cam.location).to_track_quat("-Z","Y").to_euler()
    for name,selected,hidden in [("source",original,far),("far",far,original)]:
        for o in selected:o.hide_render=False
        for o in hidden:o.hide_render=True
        s.render.filepath=str(out/f"container-{meter}m-{name}.jpg")
        bpy.ops.render.render(write_still=True)
