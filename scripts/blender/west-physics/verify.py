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
base=snapshot(P/'prior/hover-park-editable.blend');new=snapshot(P/'physics-yard-editable.blend')
assert all(new.get(k)==v for k,v in base.items())
S=bpy.context.scene
def family(n):return sorted([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('PHYS | '+n)],key=lambda o:o.name)
def verts(group):return [o.matrix_world@v.co for o in group for v in o.data.vertices]
def bounds(group):
 v=verts(group);return [[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
def bvh(group,minz=None):
 vs=[];fs=[]
 for o in group:
  i=len(vs);v=[o.matrix_world@p.co for p in o.data.vertices];vs.extend(v);fs.extend(tuple(i+k for k in f.vertices) for f in o.data.polygons if minz is None or max(v[k].z for k in f.vertices)>minz)
 return BVHTree.FromPolygons(vs,fs)
b=(P/'physics-yard-WIP.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert all('uri' not in a for a in g.get('buffers',[])+g.get('images',[])) and not g.get('skins') and not g.get('animations')
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'physics-yard-WIP.glb'))
for n,num in [('see-saw instance',2),('ball ',4),('pin ',10)]:
 oo=[o for o in family(n) if 'study' in o.name];assert len(oo)==num and all(o.data==oo[0].data for o in oo),(n,len(oo))
expected={'see-saw instance':[(-80,-224,0),(-62,-224,0)],'ball ':[(-19.5-i*1.8,-196,(-19.5-i*1.8+42)*.25+.8) for i in range(4)],'pin ':[(-50-r*1.2,-196-(i-r/2)*1.1,.04) for r in range(4) for i in range(r+1)]}
for n,coords in expected.items():
 oo=[o for o in family(n) if 'study' in o.name]
 for o,p in zip(oo,coords):assert (o.matrix_world.translation-Vector(p)).length<.0001,(o.name,p)
rr=family('ball ramp core');r=bvh(rr);checks=[]
for x in [-41.99,-36,-30,-24,-18.01]:
 p,*_=r.ray_cast(Vector((x,-196,8)),Vector((0,0,-1)),9)
 assert p and abs(p.z-(x+42)*.25)<.0001,(x,p)
 checks.append([x,p.z])
# Test clearance at the eye-height through the complete protected alley width, plus northern Range walk.
allnew=family('');tree=bvh(allnew,.25)
obstructions=[]
for x in [-99.98,-98,-96,-94,-92.02]:
 p,*_=tree.ray_cast(Vector((x,-180.01,1.7)),Vector((0,-1,0)),53.98)
 if p:obstructions.append(tuple(p))
for x in [-13.60,-11,-8.4]:
 p,*_=tree.ray_cast(Vector((x,-69,1.7)),Vector((0,-1,0)),106)
 if p:obstructions.append(tuple(p))
assert not obstructions,obstructions
def anchor(name):return next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(name))
c=verts([anchor('W08 illustrative cable')]);assert all(min((v-Vector(a)).length for v in c)<.067 for a in [(-212,34,45),(-115,16.5,14)])
for h in [2.4,3.6,4.8]:
 vv=verts([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('HOVER | ramp %.1f'%h)]);assert abs(max(v.z for v in vv)-h)<.0001 and abs(max(v.x for v in vv)+157)<.0001
T=[sum(g['accessors'][a['indices']]['count']//3 for a in m['primitives']) for m in g['meshes']]
q={'preserved_native_mesh_signatures':len(base),'added_meshes':len(new)-len(base),'reimported_shared_instances':{'see_saws':2,'balls':4,'pins':10},'all_pinned_positions_pass':True,'ramp_core_centerline_x_z_samples':checks,'open_alley_width_m':8,'named_clearance_obstructions':obstructions,'retained_zip_and_hover_anchors':True,'glb_bytes':len(b),'glb_sha256':hashlib.sha256(b).hexdigest(),'unique_triangles':sum(T),'instanced_triangles':sum(T[n['mesh']] for n in g['nodes'] if 'mesh'in n),'status':'static art placement only; no gameplay/physics/runtime verification'}
(P/'QA.json').write_text(json.dumps(q,indent=2));print(q)
