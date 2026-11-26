"""Build the optional lightweight WSC-PROP-015 wind loop from the exact donor."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/"showcase-studies"))
from common import clear_scene,output_directory
O=output_directory()
src=D.parents[2]/"public/assets/wildshard-art/wsc-prop-015-pennant-string.glb"
pin="eddeb06d8d0a2f62925aba6c288fb801671b3555c2d4f42bfd1cec320a9d3825"
assert hashlib.sha256(src.read_bytes()).hexdigest()==pin
clear_scene()
S=bpy.context.scene
S.render.fps=24
S.frame_start=0
S.frame_end=72

def load(path):
    prev=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted(set(S.objects)-prev,key=lambda o:o.name)
donor,=load(src)
stem="wsc-prop-015-pennant-breeze"
rope={"Flax rope"}
cloth={"Boulevard pumpkin","Unbleached linen","Dusk red","Sun dye"}
orig_vertices=[donor.matrix_world@v.co for v in donor.data.vertices]
names=[m.name for m in donor.data.materials]

def part(name,keep):
    vertices,faces,mat_ids,index=[],[],[],{}
    use=[m for m in donor.data.materials if m.name in keep]
    for p in donor.data.polygons:
        n=names[p.material_index]
        if n not in keep:continue
        for i in p.vertices:
            if i not in index:
                index[i]=len(vertices);vertices.append(orig_vertices[i])
        faces.append(tuple(index[i] for i in p.vertices))
        mat_ids.append([m.name for m in use].index(n))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    for m in use:mesh.materials.append(m)
    for f,i in zip(mesh.polygons,mat_ids):
        f.material_index=i;f.use_smooth=True
    o=bpy.data.objects.new(name,mesh)
    S.collection.objects.link(o)
    return o

carrier=part("Pennant flax carrier | fixed",rope)
flags=part("Pennant cloth | breeze",cloth)
unchanged=[v.co.copy() for v in flags.data.vertices]

def envelope(co):
    x,_,z=co
    # Fixed upper seam: cap motion 65 mm below the donor rope's fitted parabola.
    depth=.762+.045*x*x-z
    return max(0,min(1,(depth-.065)/.49))**1.37

def delta(co,phase):
    x,y,z=co
    w=envelope(co)
    f=4.3*x-2.6*z+phase
    return Vector((.026*w*math.sin(f),.180*w*math.sin(f),.048*w*math.cos(f)))

base=flags.shape_key_add(name="Basis")
a=flags.shape_key_add(name="Breeze sine")
b=flags.shape_key_add(name="Breeze cosine")
for i,p in enumerate(unchanged):
    u,v=delta(p,0),delta(p,math.pi/2)
    base.data[i].co=p-u-v
    a.data[i].co=p+u-v
    b.data[i].co=p-u+v
for frame in range(0,73,4):
    ph=math.tau*(frame%72)/72
    for k,w in ((a,.50+.50*math.sin(ph)),(b,.50+.50*math.cos(ph))):
        k.value=w;k.keyframe_insert("value",frame=frame)
action=flags.data.shape_keys.animation_data.action
action.name="Avenue pennants - breeze"
for fc in action.fcurves:
    for pt in fc.keyframe_points:pt.interpolation="LINEAR"
S.frame_set(0)
bpy.ops.object.select_all(action="DESELECT")
for o in (flags,carrier):o.select_set(True)
bpy.context.view_layer.objects.active=flags
output=O/(stem+".glb")
bpy.ops.export_scene.gltf(filepath=str(output),export_format="GLB",use_selection=True,export_animations=True,
    export_animation_mode="ACTIONS",export_force_sampling=False,export_morph_normal=True)
for o in (flags,carrier):bpy.data.objects.remove(o,do_unlink=True)
result=load(output)
fixed,=tuple(o for o in result if not o.data.shape_keys)
anim,=tuple(o for o in result if o.data.shape_keys)
keys=anim.data.shape_keys
assert len(keys.key_blocks)==3 and keys.animation_data.action.frame_range[:]==(0,72)
basis,k_a,k_b=keys.key_blocks
neutral=[anim.matrix_world@((p.co+q.co)*.5) for p,q in zip(k_a.data,k_b.data)]
def point_dist(src,dst):
    tree=KDTree(len(dst))
    for i,p in enumerate(dst):tree.insert(p,i)
    tree.balance()
    return max(tree.find(p)[2] for p in src)
assert max(point_dist(neutral,unchanged),point_dist(unchanged,neutral))<2e-6
sewn=[i for i,p in enumerate(neutral) if envelope(p)<1e-8]
assert len(sewn)>100
def at(f):
    S.frame_set(f);bpy.context.view_layer.update()
    e=anim.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [e.matrix_world@v.co for v in e.data.vertices]
start=at(0);end=at(72)
assert max((p-q).length for p,q in zip(start,end))<2e-6
max_tip=0.;max_sewn=0.
for f in range(0,73,3):
    v=at(f)
    max_tip=max(max_tip,max((p-q).length for p,q in zip(v,neutral)))
    max_sewn=max(max_sewn,max((v[i]-neutral[i]).length for i in sewn))
assert max_sewn<2e-6 and .145<max_tip<.190
fixed_positions=[fixed.matrix_world@v.co for v in fixed.data.vertices]
assert min(p.x for p in fixed_positions)<-3.45 and max(p.x for p in fixed_positions)>3.45

def bvh(objects):
    v,f=[],[]
    for o,p in objects:
        f.extend(tuple(i+len(v) for i in t.vertices) for t in o.data.polygons)
        v.extend(p)
    return BVHTree.FromPolygons(v,f)
baseBVH=bvh([(donor,orig_vertices)])
farBVH=bvh([(fixed,fixed_positions),(anim,neutral)])
# Base-pose silhouettes from below the street mount. This is a sampling
# approximation, not a perceptual claim or automatic runtime LOD choice.
views=[]
for yaw in (-40,-25,0,25,40):
    n=Vector((math.sin(math.radians(yaw)),-math.cos(math.radians(yaw)),-.22)).normalized()
    right=Vector((-n.y,n.x,0)).normalized();up=n.cross(right).normalized()
    both=either=0
    for j in range(70):
        for i in range(280):
            p=Vector((0,0,.75))+n*12+right*((i+.5)/280-.5)*7.1+up*((j+.5)/70-.5)*1.67
            a=baseBVH.ray_cast(p,-n,30)[0] is not None
            b=farBVH.ray_cast(p,-n,30)[0] is not None
            both+=a and b;either+=a or b
    views.append({"angle_deg":yaw,"samples":19600,"silhouette_iou":both/either})
assert min(v["silhouette_iou"] for v in views)>.86,views
triangles=sum(len(o.data.polygons) for o in result)
r={"scope":"Optional lightweight replacement and finite breeze clip. No weather or street install.",
   "source_sha256":pin,"source_bytes":src.stat().st_size,"source_triangles":len(donor.data.polygons),
   "replacement_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"replacement_bytes":output.stat().st_size,
   "replacement_triangles":triangles,"root_vertices":len(sewn),"max_root_shift_m":max_sewn,
   "max_tip_motion_m":max_tip,"loop_seconds":3,"clip":"Avenue pennants - breeze","silhouette_views":views}
(O/"pennant-proof.json").write_text(json.dumps(r,indent=2)+"\n")
print(json.dumps(r))
