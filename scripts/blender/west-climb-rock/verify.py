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
base=snapshot(P/'prior/whole-town-editable.blend');new=snapshot(P/'climb-rock-editable.blend')
assert all(new.get(k)==v for k,v in base.items())
m=json.loads((P/'integration.json').read_text())
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
b=(P/'climb-rock-WIP.glb').read_bytes();g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert not g.get('skins') and not g.get('animations') and all('uri' not in o for o in g.get('buffers',[])+g.get('images',[]))
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'climb-rock-WIP.glb'))
S=bpy.context.scene
def obj(prefix):return next(o for o in S.objects if o.type=='MESH' and o.name.startswith('CLIMB | '+prefix))
targets=[('deck A','deck B'),('deck B','deck C'),('deck C','crag mesh')]
joins=[]
for r,names in zip(m['bridges'],targets):
 assert abs(Vector(r['anchors_blender'][0]).__sub__(Vector(r['anchors_blender'][1])).length-r['straight_m'])<1e-5
 br=bvh(obj('bridge '+r['name']))
 for a,n in zip(r['anchors_blender'],names):
  q=Vector(a)+Vector((0,0,.20))
  p,*_=br.ray_cast(q,Vector((0,0,-1)),.25)
  platform,*_=bvh(obj(n)).ray_cast(q,Vector((0,0,-1)),.30)
  assert p and platform,(r['name'],a,n)
  assert abs(platform.z-a[2])<.02 and abs(p.z-a[2])<.03,(a,platform,p)
  joins.append({'span':r['name'],'anchor':a,'target':n,'threshold_z':p.z,'deck_or_crag_z':platform.z})
# Ray from camera side hits authored dark backstop after entering each shallow visible native arch, no tunnel path.
back=bvh(obj('north and south exterior recess backing'));rock=bvh(obj('crag mesh'))
mouths=[]
for n,y,sg in [('north',-9,-1),('south',-79,1)]:
 a=Vector((-200,y,1.05));d=Vector((0,sg,0));p,*_=back.ray_cast(a,d,15.);q,*_=rock.ray_cast(a,d,15.)
 assert p is not None
 # Record raw shell depth; visual inspection judges the mouth integration, not a cavity claim.
 mouths.append({'mouth':n,'dark_backstop_y':p.y,'shell_surface_y_on_centre_ray':q.y if q else None})
cr=m['bridges'][-1];A,B=map(Vector,cr['anchors_blender']);D=B-A;span=bvh(obj('bridge C Rock'));L=math.hypot(D.x,D.y);V=Vector((-D.y/L,D.x/L,0));N=round(L/.43);low=[]
for i in range(N):
 t=(i+.5)/N
 if t<.63:continue
 for w in [-.76,0,.76]:
  xy=A+D*t+V*w
  q=Vector((xy.x,xy.y,16.78))
  p,*_=span.ray_cast(q,Vector((0,0,-1)),3.7)
  r,*_=rock.ray_cast(q,Vector((0,0,-1)),6.)
  if p is not None and r is not None:low.append(p.z-r.z)
assert low and min(low)>=.005,min(low)
c=next(o for o in S.objects if o.name.startswith('W08 illustrative cable'));vs=[c.matrix_world@v.co for v in c.data.vertices]
for a in [Vector((-212,34,45)),Vector((-115,16.5,14))]:assert min((v-a).length for v in vs)<.067
t=[sum(g['accessors'][a['indices']]['count']//3 for a in me['primitives']) for me in g['meshes']]
q={'unchanged_baseline_meshes':len(base),'new_meshes':len(new)-len(base),'actual_export_measured_bridge_joins':joins,'exterior_mouth_shallow_checks':mouths,'minimum_rock_fit_top_clearance_sampled_m':min(low),'glb_bytes':len(b),'glb_sha256':hashlib.sha256(b).hexdigest(),'unique_triangles':sum(t),'instanced_triangles':sum(t[n['mesh']] for n in g['nodes'] if 'mesh' in n),'status':'static scene geometry only, no cave interior or runtime qualification'}
(P/'QA.json').write_text(json.dumps(q,indent=2));print(q)
