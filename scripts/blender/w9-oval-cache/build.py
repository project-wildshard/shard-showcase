"""Fit the unmodified animated West cache behind the exact Round 5 oval."""
import bpy, hashlib, json, math, random, struct, sys
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
p,out=map(Path,sys.argv[sys.argv.index('--')+1:][:2]);out.mkdir(parents=True,exist_ok=True)
anchor=json.loads(p.read_text())
root=Path(__file__).resolve().parents[3]
assets=root/'public/assets/wildshard-art'
chest_path=assets/'wsc-prop-049-cache-chest-opening.glb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(chest_path)=='57ceefd1b18329532ba060cc84e9ec74067f17b76ee02da0a9c90a61e591f278'
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.fps=24
rng=random.Random(9097)
def mat(name,c,rough=.8,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough
 bs.inputs['Metallic'].default_value=metal
 return m
rock=[mat('Dry limestone '+str(i),c) for i,c in enumerate(((.24,.233,.183),(.31,.293,.222),(.34,.30,.227),(.22,.222,.18),(.36,.327,.252)))]
moss=[mat('Moss tint '+str(i),c) for i,c in enumerate(((.132,.151,.079),(.194,.183,.104),(.245,.248,.136)))]
soil=mat('Old quarry path',(.211,.166,.110),.96)
turf=mat('West hillside',(.189,.242,.105),.95)
def select(obs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
def box(n,loc,dim,m,r=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=n;o.dimensions=dim;o.data.materials.append(m)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if r:
  d=o.modifiers.new('Stone chamfer','BEVEL');d.width=r;d.segments=1
  bpy.ops.object.modifier_apply(modifier=d.name)
 return o

parts=[]
# Five staggered courses with darker earth visible in the joints. A narrow
# blind pocket is concealed from the racing side, but open toward +Z.
for level in range(5):
 low=level*.43; height=.446
 for j in range(8):
  y=.39+j*.84+(.085 if level%2 else 0)
  x=1.70+.09*math.sin(j*.72)-.055*level
  h=height+rng.uniform(-.025,.026)
  o=box('Dry-set limestone',(x,y,low+h*.5),(.66+rng.uniform(-.065,.065),.86+rng.uniform(-.025,.033),h),rock[rng.randrange(len(rock))],.044 if level>=3 or (level>0 and j%3==0) else 0)
  o.rotation_euler.z=rng.uniform(-.102,.102);parts.append(o)
for j in range(7):
 y=.62+j*.96
 o=box('Irregular mossy coping',(1.58,y,2.17),(.67,.95,.18+rng.uniform(-.06,.085)),rock[rng.randrange(2,5)],.045)
 o.rotation_euler.z=rng.uniform(-.17,.17);parts.append(o)
 for k in range(2):
  peb=box('Thin lichen chips',(1.38+k*.19,y+rng.uniform(-.26,.26),2.26),(.16,.24,.034),moss[(j+k)%3],.012)
  peb.rotation_euler.z=rng.uniform(-1.2,1.2);parts.append(peb)
for j in range(3):
 # A low end return adds thickness away from the lid swing.
 parts.append(box('North pocket cheek',(.54-j*.46,4.73,.177),(.472,.64,.354),rock[(j+2)%5],.028))
select(parts);bpy.ops.object.join();o=bpy.context.object;o.name='OvalCacheDryStone'
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
export=out/'w9-oval-cache-screen.glb'
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_animations=False)
raw=export.read_bytes();g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tris=sum(g['accessors'][b['indices']]['count']//3 for m in g['meshes'] for b in m['primitives'])
assert tris<2850 and len(raw)<200000 and not g.get('textures')
bpy.data.objects.remove(o,do_unlink=True)

def load(path):
 old=set(s.objects)
 bpy.ops.import_scene.gltf(filepath=str(path))
 return sorted(set(s.objects)-old,key=lambda m:m.name)
screen=[o for o in load(export) if o.type=='MESH']
all_chest=load(chest_path)
chest=[o for o in all_chest if o.type=='MESH']
lid=next(o for o in all_chest if o.name=='Cache_Lid')
action=lid.animation_data.action
if not action:
 strip=lid.animation_data.nla_tracks[0].strips[0]
 first,last=strip.frame_start,strip.frame_end
else:first,last=action.frame_range
assert last-first>=25
def frame(t):
 s.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update()
def geo(objects,three=False):
 vertices=[]; faces=[]
 for o in objects:
  k=len(vertices)
  m=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
  for q in m.data.vertices:
   p=m.matrix_world@q.co
   vertices.append((p.x,p.z,-p.y) if three else p)
  m.data.calc_loop_triangles()
  faces.extend(tuple(k+i for i in f.vertices) for f in m.data.loop_triangles)
 return vertices,faces
def bvh(objs):
 v,f=geo(objs);return BVHTree.FromPolygons(v,f,all_triangles=True)
def between(tree,start,end):
 start=Vector(start);delta=Vector(end)-start
 return tree.ray_cast(start,delta.normalized(),delta.length-.0001)[0] is not None
frame(first)
screen_bvh=bvh(screen)
start_pose=lid.rotation_quaternion.copy()
paths={'screen':geo(screen,True),'chest':geo(chest,True)}
for t in [first+(last-first)*i/56 for i in range(57)]:
 frame(t)
 assert not screen_bvh.overlap(bvh(chest)),t
assert abs(start_pose.rotation_difference(lid.rotation_quaternion).angle)>1.7
frame(first)
outside=[]
ox=anchor['oval']['x']-anchor['oval']['halfLen'];oz=anchor['oval']['z'];r=anchor['oval']['runRadius'];ax,_,az=anchor['at']
for i in range(13):
 a=i*.065
 for h in (1.68,2.48):
  eye=(ox-r*math.cos(a)-ax,az-(oz+r*math.sin(a)),h)
  for target in ((0,0,.83),(-.68,0,.72),(.68,0,.72)):
   outside.append(between(screen_bvh,eye,target))
approach=[]
for x in (-.6,0,.6):
 for z in (1.35,1.7,2.15):
  for h in (1.48,1.68,1.85):approach.append(not between(screen_bvh,(x,-z,h),(0,-.64,.88)))
assert all(outside),(sum(outside),len(outside))
assert all(approach)
v,_=paths['screen']
clearance=min(math.hypot(ax+x-ox,az+z-oz)-r for x,_,z in v)
assert clearance>16
(out/'geo.json').write_text(json.dumps(paths,separators=(',',':'))+'\n')
(out/'art.json').write_text(json.dumps({**anchor,'scope':'Local flat witness only; clearances and concealment are sampled, no level install.',
 'screen':{'file':export.name,'sha256':sha(export),'bytes':len(raw),'triangles':tris},
 'chest':{'file':chest_path.name,'sha256':sha(chest_path),'yawDegrees':0},
 'clipSamplesWithoutScreenContact':57,'closedLidSightRaysBlocked':len(outside),
 'approachSightRaysClear':len(approach),'minScreenClearanceFrom38mRunningLineM':round(clearance,4),
 'promptLocalXYZ':[0,.88,.64]},indent=2)+'\n')
if '--no-render' in sys.argv:raise SystemExit(0)
box('Soft verge',(1,0,-.18),(43,44,.36),turf)
box('Packed dry access',(0,-1.3,-.08),(2.05,7.8,.15),soil)
for i in range(95):
 x=rng.uniform(-5.8,5.8);y=rng.uniform(-4.0,8)
 if -.95<x<.7 and y<.9:continue
 o=box('Weathered chips',(x,y,.026),(.15+rng.random()*.2,.1+rng.random()*.23,.052),rock[rng.randrange(5)],.012)
 o.rotation_euler.z=rng.random()*5
for i in range(135):
 x=rng.uniform(-6,6);y=rng.uniform(-6,8)
 if -1.4<x<1.22 and y<.9:continue
 for k in range(3):
  me=bpy.data.meshes.new('Dry grass')
  h=rng.uniform(.12,.38);w=rng.uniform(.018,.048);jx,jy=rng.uniform(-.14,.14),rng.uniform(-.14,.14)
  me.from_pydata([(x-w,y,0),(x+w,y,0),(x+jx,y+jy,h)],[],[(0,1,2)])
  o=bpy.data.objects.new('Grass blade',me);s.collection.objects.link(o);me.materials.append(moss[i%3])
world=bpy.data.worlds.new('Low orchard sun');world.use_nodes=True;s.world=world
n=world.node_tree.nodes;sk=n.new('ShaderNodeTexSky');sk.sky_type='NISHITA';sk.sun_elevation=.48;sk.sun_rotation=4.25;sk.sun_size=.034
world.node_tree.links.new(sk.outputs[0],n['Background'].inputs[0]);n['Background'].inputs[1].default_value=.23
s.render.engine='CYCLES';s.cycles.samples=28;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look="AgX - Medium High Contrast";s.view_settings.exposure=-.68
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=88
c=bpy.data.cameras.new('Cache fit');cam=bpy.data.objects.new('Cache fit',c);s.collection.objects.link(cam);s.camera=cam
for name,t,eye,at,lens,size in [
 ('discover',first,(-1.7,-4.2,1.7),(.50,.72,.94),30,(968,1216)),
 ('open',last,(-2.45,-3.42,2.45),(.04,.21,.88),39,(1220,872))]:
 frame(t);cam.location=eye;cam.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler();c.lens=lens
 s.render.resolution_x,s.render.resolution_y=size
 s.render.filepath=str(out/('nov26-w9-oval-cache-'+name+'.webp'));bpy.ops.render.render(write_still=True)
