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

from mathutils.bvhtree import BVHTree
base=snapshot(P/'prior/range-landscape-editable.blend');new=snapshot(P/'west-orientation-editable.blend')
assert all(new.get(k)==v for k,v in base.items())
S=bpy.context.scene
def family(p):return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(p)]
def mesh(p):return family(p)[0]
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def bvh(group,minz=None):
 vs=[];fs=[]
 for o in group:
  i=len(vs);v=points(o);vs.extend(v);fs.extend(tuple(i+k for k in f.vertices) for f in o.data.polygons if minz is None or max(v[k].z for k in f.vertices)>minz)
 return BVHTree.FromPolygons(vs,fs)
b=(P/'west-orientation-WIP.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert all('uri' not in a for a in g.get('buffers',[])+g.get('images',[])) and not g.get('skins') and not g.get('animations')
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'west-orientation-WIP.glb'))
add=family('WEST ORIENT | ');addv=[v for o in add for v in points(o)]
assert all(-250.00001<=v.x<=.00001 and -250.00001<=v.y<=250.00001 for v in addv)
t=bvh(add,.17);west=bvh(family('WEST ORIENT | west perimeter'),.2)
for yy in [-3.99,-3,-1,0,1,3,3.99]:
 for z in [.25,1.7,3.7]:
  v,*_=t.ray_cast(Vector((-250.05,yy,z)),Vector((1,0,0)),122.04);assert v is None,(yy,z,v)
for yy in [-4.01,4.01]:
 v,*_=west.ray_cast(Vector((-250.05,yy,1.7)),Vector((1,0,0)),4.0);assert v is not None
roads=bvh(family('WEST ORIENT | west avenue')+family('ZIP | West Gate exterior approach'))
samples=[]
for x in [-249.99,-247.01,-246.99,-237.01,-236.99,-225,-190,-150.01,-149.99,-130,-128.01]:
 for y in [-3.8,0,3.8]:
  v,*_=roads.ray_cast(Vector((x,y,.47)),Vector((0,0,-1)),.50);assert v is not None and .015<v.z<.065,(x,y,v)
  if y==0:samples.append((x,v.z))
ver=bvh(family('WEST ORIENT | west perimeter'))
for y in [-229,229]:
 v,*_=ver.ray_cast(Vector((-229,y,3)),Vector((0,0,-1)),3);assert v is not None and .025<v.z<.08,(y,v)
# Retained exact anchors are rechecked on export.
c=points(mesh('W08 illustrative cable'));assert all(min((v-Vector(a)).length for v in c)<.067 for a in [(-212,34,45),(-115,16.5,14)])
vv=[v for o in family('HOVER | ramp 4.8') for v in points(o)];assert abs(max(v.z for v in vv)-4.8)<.0001 and abs(max(v.x for v in vv)+157)<.0001
v,*_=bvh([mesh('PHYS | ball ramp core')]).ray_cast(Vector((-30,-196,8)),Vector((0,0,-1)),8);assert v and abs(v.z-3)<.0001
assert abs(max(v.z for v in points(mesh('RANGE LAND | south landscape berm')))-10)<.0001
q={'native_baseline_unchanged_meshes':len(base),'new_meshes':len(new)-len(base),'all_additions_inside_cell':True,'arrival_ray_clear_span_8m':True,'in_cell_road_centerline_samples':samples,'vista_corner_surfaces_at_pinned_xy':True,'retained_zip_hover_yard_berm_anchors':True,'glb_bytes':len(b),'glb_sha256':hashlib.sha256(b).hexdigest(),'scope':'fictional static art and orientation only; no W12 or runtime qualification'}
(P/'QA.json').write_text(json.dumps(q,indent=2));print(q)
