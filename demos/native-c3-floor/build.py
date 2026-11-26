"""Join the exact two C3 donor floor sectors with a non-overlapping 28 m-radius infill."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import bpy
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent.parent/'scripts/blender/showcase-studies'))
from common import clear_scene,export
A,O=map(Path,sys.argv[sys.argv.index('--')+1:][:2])
O.mkdir(parents=True,exist_ok=True)
clear_scene()
S=bpy.context.scene
# Origin is C3 center. Blender Y is negative world Three Z.
files=[
    ('g2','e11c-g2-c3-threshold.glb','777bed81fd7369c604faf6e666cd33d0c5c826c93e02d136a58e672ea2b5d101',
     Matrix.Translation((-36,-28,0)),'01 G2 level paving'),
    ('office','c3-office-sector.glb','631f39353d7eed6d4bba196f71a30342f7a5aac1fb1d3579560807c8db971f31',
     Matrix.Rotation(math.pi/4,4,'Z'),'Visible fight floor cropped'),
]
def load(path,trans):
    before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    objects=sorted(set(S.objects)-before,key=lambda o:o.name)
    for o in objects:
        if o.parent not in objects:o.matrix_world=trans@o.matrix_world
    bpy.context.view_layer.update()
    return objects
donors=[]
v,f=[],[]
for key,file,digest,M,prefix in files:
    p=A/file
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,p
    objects=load(p,M);donors.extend((key,o) for o in objects if o.type=='MESH')
    for o in objects:
        if o.type!='MESH' or not o.name.startswith(prefix):continue
        o.data.calc_loop_triangles()
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        for t in o.data.loop_triangles:
            a=[pts[i] for i in t.vertices]
            if not all(abs(q.z-.05)<2e-6 for q in a):continue
            if max(q.xy.length for q in a)>50:continue
            n=len(v);v+=a;f.append((n,n+1,n+2))
assert len(f)>70
bvh=BVHTree.FromPolygons(v,f,all_triangles=True)
outer=[Vector((28*math.cos(j*math.tau/128),28*math.sin(j*math.tau/128))) for j in range(128)]
edges=[(i,(i+1)%128) for i in range(128)]
coords=outer+[p.xy for p in v]
edges += [(128+i,128+j) for triangle in f for i,j in zip(triangle,triangle[1:]+triangle[:1])]
vs,_,ts,*_=delaunay_2d_cdt(coords,edges,[],0,1e-5,False)
def witness(x,y):
    return bvh.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),1.05)[0] is not None
def inside(x,y):
    a=math.atan2(y,x)%math.tau
    side=a*128/math.tau
    distance=x*math.cos((int(side)+.5)*math.tau/128)+y*math.sin((int(side)+.5)*math.tau/128)
    return distance<28*math.cos(math.pi/128)-1e-6
new=[]
for tri in ts:
    assert len(tri)==3
    p=[vs[i] for i in tri];c=sum(p,Vector((0,0)))/3
    if inside(*c) and not witness(*c):
        u=p[1]-p[0];w=p[2]-p[0]
        a=u.x*w.y-u.y*w.x
        if abs(a)>1e-7:new.append(tuple(tri if a>0 else reversed(tri)))
assert new and len(new)<360
# Subdivide each fitted surface triangle around its centroid for a very soft, vertex-only
# poured aggregate variation. The donor joint vertices stay exactly in place.
xyz=[(p.x,p.y,.05) for p in vs]
faces=[]
for i,j,k in new:
    q=(vs[i]+vs[j]+vs[k])/3;n=len(xyz);xyz.append((q.x,q.y,.05))
    faces.extend([(i,j,n),(j,k,n),(k,i,n)])
used=sorted({i for p in faces for i in p});idx={k:i for i,k in enumerate(used)}
d=bpy.data.meshes.new('Foreman floor | fitted slabs')
d.from_pydata([xyz[i] for i in used],[],[tuple(idx[i] for i in t) for t in faces])
d.update()
color=d.color_attributes.new(name='Warm concrete',type='FLOAT_COLOR',domain='POINT')
for v,c in zip(d.vertices,color.data):
    x,y,z=v.co
    # Fade to the two donor color families, then add restrained variation away from seams.
    t=(math.tanh((x+y)*.10)+1)*.5
    k=.008*math.sin(x*.87+y*.51)+.006*math.cos(y*1.46-x*.17)
    c.color=(.36+k,.307*(1-t)+.223*t+k,.235*(1-t)+.125*t+k,1)
mat=bpy.data.materials.new('C3 matched warm aggregate');mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.86
a=mat.node_tree.nodes.new('ShaderNodeVertexColor');a.layer_name='Warm concrete'
mat.node_tree.links.new(a.outputs['Color'],p.inputs['Base Color']);d.materials.append(mat)
floor=bpy.data.objects.new('C3 fitted center floor',d);S.collection.objects.link(floor)
path=O/'e11c-c3-fitted-floor.glb'
export([floor],path)
raw=path.read_bytes()
g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert 'images' not in g and len(g['meshes'])==1
bpy.data.objects.remove(floor,do_unlink=True)
floor,=load(path,Matrix.Identity(4))
# Reimport and check for holes/occlusion in the flat floor, not transitions through walls.
newBVH=BVHTree.FromPolygons([floor.matrix_world@u.co for u in floor.data.vertices],
    [p.vertices[:] for p in floor.data.polygons])
measures={'both':0,'old':0,'new':0,'none':0}
for j in range(34):
    for i in range(34):
        x=-27.2+i*1.65;y=-27.15+j*1.65
        if math.hypot(x,y)>27.75:continue
        hit=newBVH.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),1.05)[0]
        ref=witness(x,y)
        measures['both' if hit and ref else 'new' if hit else 'old' if ref else 'none']+=1
assert measures['none']==measures['both']==0,measures
def row(asset,o):
    o.data.calc_loop_triangles()
    vertices=[]
    for v in o.data.vertices:
        x,y,z=o.matrix_world@v.co
        vertices.extend(round(t,7) for t in [x+146,z,186-y])
    return dict(asset=asset,name=o.name,vertices=vertices,triangles=[i for t in o.data.loop_triangles for i in t.vertices])
payload=[row(k,o) for k,o in donors if not o.name.startswith('90 ')]+[row('infill',floor)]
geom=json.dumps(payload,separators=(',',':'))+'\n'
(O/'c3-geometry.json').write_text(geom)
rc=dict(originThree=[146,0,186],floorY=.05,outerRadiusM=28,flatProbes=measures,
    bytes=len(raw),triangles=len(faces),sha256=hashlib.sha256(raw).hexdigest(),meshSha=hashlib.sha256(geom.encode()).hexdigest(),
    donors=[dict(asset=key,sha256=sha) for key,_,sha,_,_ in files],
    scope='Exact static floor inlay, two donor sectors unchanged; not full arena')
(O/'c3-export.json').write_text(json.dumps(rc,indent=2)+'\n')
args=sys.argv[sys.argv.index('--')+1:]
if len(args)==3:
    import runpy
    runpy.run_path(str(D/'render.py'),init_globals=dict(S=S,O=O,receipt=rc,motion=Path(args[2])))
