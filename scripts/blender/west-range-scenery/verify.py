import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
P=OUT
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256();h.update(str(tuple(v for row in o.matrix_world for v in row)).encode());h.update(str([(v.co.x,v.co.y,v.co.z) for v in o.data.vertices]).encode());h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode());h.update(str([(m.name,tuple(m.diffuse_color)) for m in o.data.materials]).encode());out[o.name]=h.hexdigest()
 return out

from mathutils.bvhtree import BVHTree
base=snapshot(P/'prior/physics-yard-editable.blend')
new=snapshot(P/'range-landscape-editable.blend')
assert all(new.get(k)==v for k,v in base.items())
assert all(k.startswith('RANGE LAND | ') for k in set(new)-set(base))
S=bpy.context.scene
def mesh(n):return next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(n))
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(v):return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def bvh(group,minz=None):
 vs=[];fs=[]
 for o in group:
  i=len(vs);v=points(o);vs.extend(v);fs.extend(tuple(i+k for k in f.vertices) for f in o.data.polygons if minz is None or max(v[k].z for k in f.vertices)>minz)
 return BVHTree.FromPolygons(vs,fs)
b=(P/'range-landscape-WIP.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert all('uri' not in a for a in g.get('buffers',[])+g.get('images',[])) and not g.get('skins') and not g.get('animations')
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'range-landscape-WIP.glb'))
berm=mesh('RANGE LAND | south landscape berm');bb=bounds(points(berm))
for i,p in enumerate([[-92,-168,.012],[-14,-156,10]]):assert all(abs(a-b)<.0002 for a,b in zip(bb[i],p))
mass=bvh([berm]);samples=[]
for x in [-86,-75,-60,-52,-36,-21]:
 p,*_=mass.ray_cast(Vector((x,-162,11)),Vector((0,0,-1)),11)
 assert p is not None;samples.append([x,p.z])
assert abs(samples[2][1]-10)<.0001 and abs(samples[3][1]-10)<.0001
added=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('RANGE LAND | ')]
ob=bvh(added,.10)
for x in [-13.6,-12,-11,-10,-8.4]:
 for z in [.2,1.0,1.7]:
  p,*_=ob.ray_cast(Vector((x,-69,z)),Vector((0,-1,0)),106)
  assert p is None,(x,z,p)
for x in [-39,-37,-36,-35,-33]:
 p,*_=ob.ray_cast(Vector((x,-59,1.7)),Vector((0,-1,0)),19)
 assert p is None,(x,p)
yard=mesh('PHYS | ball ramp core');p,*_=bvh([yard]).ray_cast(Vector((-30,-196,8)),Vector((0,0,-1)),8);assert p and abs(p.z-3)<.0001
c=points(mesh('W08 illustrative cable'));assert all(min((v-Vector(a)).length for v in c)<.067 for a in [(-212,34,45),(-115,16.5,14)])
for h in [2.4,3.6,4.8]:
 p=[v for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('HOVER | ramp %.1f'%h) for v in points(o)]
 assert abs(max(v.z for v in p)-h)<.0001 and abs(max(v.x for v in p)+157)<.0001
T=[sum(g['accessors'][a['indices']]['count']//3 for a in m['primitives']) for m in g['meshes']]
q={'preserved_native_mesh_signatures':len(base),'added_meshes':len(new)-len(base),'reimport_berm_bounds':bb,'reimport_berm_crown_sample':samples,'blocked_sampled_rays_east_walk':0,'blocked_sampled_rays_immediate_gate':0,'retained_zip_hover_yard_anchors':True,'glb_bytes':len(b),'glb_sha256':hashlib.sha256(b).hexdigest(),'unique_triangles':sum(T),'instanced_triangles':sum(T[n['mesh']] for n in g['nodes'] if 'mesh'in n),'scope':'fictional static pedestrian scenery only; no weapon equipment, functional range design, collision/gameplay or performance validation'}
(P/'QA.json').write_text(json.dumps(q,indent=2));print(q)
