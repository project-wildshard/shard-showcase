"""Fit a common-grade apron between the tested C3 floor and the exact G3 slab."""
import hashlib,json,math,runpy,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
A,O=map(Path,args[:2]);O.mkdir(parents=True,exist_ok=True)
# The previous build is deterministic and supplies exact geometry already in the correct C3 space.
sys.argv=['blender','--',str(A),str(O/'c3')]
previous=runpy.run_path(str(D.parent/'native-c3-floor'/'build.py'))
S=previous['S'];load=previous['load'];row=previous['row'];export=previous['export']
assert previous['rc']['meshSha']=='d646f3123ff33da48c0f56eef87db157d9ebefdf087fb70df578d3e363751692'
donor=A/'g3-titan-lane-junction.glb'
assert hashlib.sha256(donor.read_bytes()).hexdigest()=='d8d061f6f206b886971c245e97b0d5692a21daba339011fa7fc5791c8c75de62'
g3=load(donor,Matrix.Translation((52,0,0)))
g3=[o for o in g3 if o.type=='MESH']
cap,=tuple(o for o in g3 if o.name=='C3 exact eastern fight floor')
g3.remove(cap);bpy.data.objects.remove(cap,do_unlink=True)

def mat(n,rgb,r=.8):
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=r
    return m
apron=mat('Grey copper casting',(.306,.277,.238))
dark=mat('Brushed dark drainage edges',(.096,.111,.106))
yellow=mat('Oxide enamel fastenings',(.54,.302,.086))
def mesh(n,v,f,m):
    d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update()
    d.materials.append(m);o=bpy.data.objects.new(n,d);S.collection.objects.link(o);return o
# Match the exact 128-edge C3 fitting envelope at the left seam. 6 m inner
# width within the .22-radian cut, growing to the G3 passage slab at x188.
outer=[(28*math.cos(k*math.tau/128),28*math.sin(k*math.tau/128)) for k in range(-9,10)]
ys=[-3.0]+[y for x,y in outer if abs(y)<3.0]+[3.0]
def edge(y):
    for (x,a),(xx,b) in zip(outer,outer[1:]):
        if a<=y<=b:return x+(xx-x)*(y-a)/(b-a)
    raise AssertionError(y)
vertices=[]
for y in ys:
    vertices.extend(((edge(y),y,.05),(42,y*1.28,.05)))
f=[(i,i+1,i+3,i+2) for i in range(0,len(vertices)-2,2)]
floor=mesh('01 C3-G3 matching apron floor',vertices,f,apron)
# Low dark seam and narrow gold brackets are visual finish only and are not colliders.
def deco(n,x):
    vs=[];fs=[]
    for side in (-1,1):
        y=side*(2.86+(x-28)*.057)
        for i in range(5):
            b=len(vs);a=x+i*.43
            vs.extend(((a,y-.051,.053),(a+.25,y-.051,.053),(a+.29,y+.051,.053),(a+.04,y+.051,.053)))
            fs.append((b,b+1,b+2,b+3))
    return mesh(n,vs,fs,dark if x<35 else yellow)
parts=[floor,deco('90 Near side slot detail',28.24),deco('90 Far side enamel fixings',37.88)]
path=O/'e11c-c3-g3-apron.glb'
export(parts,path)
for obj in parts:bpy.data.objects.remove(obj,do_unlink=True)
fresh=load(path,Matrix.Identity(4));floor,=tuple(o for o in fresh if o.name.startswith('01 '))
def cast(o,x,y):
    g=BVHTree.FromPolygons([o.matrix_world@p.co for p in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    a,n,i,d=g.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),1.1)
    return a.z if a else None
old=previous['floor']
right,=tuple(o for o in g3 if o.name=='G3 passage slab')
for k in range(41):
    y=-2.9+k*5.8/40
    e=edge(y)
    for o,x in ((old,e-.012),(floor,e+.012),(floor,41.988),(right,42.012)):
        z=cast(o,x,y)
        assert z is not None and abs(z-.05)<2e-6,(o.name,x,y,z)
    for o,x in ((old,e+.012),(floor,e-.012),(floor,42.012),(right,41.988)):
        assert cast(o,x,y) is None,(o.name,x,y)
# Extract structural geometry only. Decorative labels and surface paint are visual.
def structural(o):return not o.name.startswith(('Batched trim | Worn route stripe','COURT ','TITAN','G3    /'))
geom=previous['payload']+[row('g3',o) for o in g3 if structural(o)]+[row('apron',floor)]
raw=json.dumps(geom,separators=(',',':'))+'\n'
(O/'route-geometry.json').write_text(raw)
receipt=dict(originThree=[146,0,186],gradeY=.05,yardDatum=0,laneY=.045,
  discardedName='C3 exact eastern fight floor',donorSha=hashlib.sha256(donor.read_bytes()).hexdigest(),
  geometrySha=hashlib.sha256(raw.encode()).hexdigest(),bothSeamsProbePoints=82,bytes=path.stat().st_size,
  triangles=sum(len(o.data.polygons) for o in fresh if o.type=='MESH'),
  sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(O/'apron-export.json').write_text(json.dumps(receipt,indent=2)+'\n')
if len(args)==3:
    runpy.run_path(str(D/'render.py'),init_globals=dict(S=S,O=O,receipt=receipt,motion=Path(args[2])))
