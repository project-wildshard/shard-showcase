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
base=snapshot(P/'prior/climb-rock-editable.blend');new=snapshot(P/'hover-park-editable.blend')
assert all(new.get(k)==v for k,v in base.items())
S=bpy.context.scene
family=lambda n:[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('HOVER | '+n)]
def verts(obs):return [o.matrix_world@v.co for o in obs for v in o.data.vertices]
def bounds(obs):
 vs=verts(obs);return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
for i in range(7):
 oo=[next(o for o in family('run-up '+c) if o.name.endswith(' %02d'%i)) for c in ('2.4','3.6','4.8')]
 assert all(o.data==oo[0].data for o in oo)
b=(P/'hover-park-WIP.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert all('uri' not in x for x in g.get('buffers',[])+g.get('images',[])) and not g.get('skins') and not g.get('animations')
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'hover-park-WIP.glb'))
for i in range(7):
 oo=[next(o for o in family('run-up '+c) if o.name.endswith(' %02d'%i)) for c in ('2.4','3.6','4.8')]
 assert all(o.data==oo[0].data for o in oo)
def bvh(group):
 vs=[];fs=[]
 for o in group:
  i=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(i+k for k in f.vertices) for f in o.data.polygons)
 return BVHTree.FromPolygons(vs,fs)
lanes=[]
for h,y in [(2.4,-132),(3.6,-143),(4.8,-154)]:
 ra,st=family(f'ramp {h}'),family(f'run-up {h}');assert len(ra)==8 and len(st)==7
 rb,sb=bounds(ra),bounds(st)
 assert abs(rb[1][2]-h)<.0001 and abs(rb[1][0]+157)<.0001
 assert abs((rb[0][1]+rb[1][1])/2-y)<.0002
 assert abs(sb[0][0]+157)<.0001 and abs(sb[1][0]+112)<.0001 and abs(sb[1][1]-sb[0][1]-3.9)<.0001
 ry=bvh(ra).ray_cast(Vector((-157.10,y,1)),Vector((0,0,-1)),1.2)[0]
 sy=bvh(st).ray_cast(Vector((-156.90,y,1)),Vector((0,0,-1)),1.2)[0]
 assert ry and sy and abs(ry.z-sy.z)<.12,(h,ry,sy)
 lanes.append({'height_m':rb[1][2],'lane_center_blender_y':y,'ramp_toe_x':rb[1][0],'run_up_bounds':sb,'sampled_0p1m_either_side_z_delta':abs(ry.z-sy.z)})
walls=[bounds(family('launch wall '+n)) for n in ['west','east']]
assert all(abs(v[1][1]-v[0][1]-45)<.0002 for v in walls)
# Polygon profile is reconstructed independently from actual exported surface screen samples.
slopes=[]
for n,x,sg in [('west',-224,-1),('east',-216,1)]:
 tree=bvh(family('launch wall '+n));samp=[]
 for i in range(89): # last 0.10m excluded: separate 0.055m decorative coping at crest
  d=.05+i*.10; p=tree.ray_cast(Vector((x+d*sg,-146,5)),Vector((0,0,-1)),5.01)[0]
  assert p is not None,(n,d);samp.append(p.z)
 slopes.append(max((b-a)/.1 for a,b in zip(samp,samp[1:])))
assert max(slopes)<=1.0005,slopes
c=next(o for o in bpy.context.scene.objects if o.name.startswith('W08 illustrative cable'));vs=verts([c])
for a in [Vector((-212,34,45)),Vector((-115,16.5,14))]:assert min((v-a).length for v in vs)<.067
T=[sum(g['accessors'][a['indices']]['count']//3 for a in m['primitives']) for m in g['meshes']]
q={'baseline_meshes_retained_exact':len(base),'new_meshes':len(new)-len(base),'source_asset_lanes_measured_clean_reimport':lanes,'shared_strip_submeshes_clean_reimport':7,'launch_wall_measured_bounds_m':walls,'launch_wall_measured_max_surface_gradients_excluding_crest_coping':slopes,'zip_endpoints_retained':True,'export_bytes':len(b),'export_sha256':hashlib.sha256(b).hexdigest(),'unique_triangles':sum(T),'instanced_triangles':sum(T[n['mesh']] for n in g['nodes'] if 'mesh'in n),'status':'static art only; no runtime/physics/ride-fit qualification'}
(P/'QA.json').write_text(json.dumps(q,indent=2));print(q)
