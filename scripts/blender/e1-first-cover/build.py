"""Low-cost pallet cradle for exact round-five Band 1 crate placements.
Only the cradle is a new export: the five haul crates remain instances.
"""
import bpy
from mathutils import Matrix,Vector
import hashlib,json,math,random,struct,sys
from pathlib import Path
a,out=map(Path,sys.argv[sys.argv.index('--')+1:][:2]);out.mkdir(parents=True,exist_ok=True)
source=json.loads(a.read_text())
root=Path(__file__).resolve().parents[3]
donor=root/'public/assets/wildshard-art/haul-crate.glb'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(donor)=='d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene

def mat(name,rgb,metal=0,rough=.66,tone=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 n=m.node_tree.nodes;bs=n.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=rough
 bs.inputs['Metallic'].default_value=metal
 if tone is not None:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=14
  c=n.new('ShaderNodeValToRGB');c.color_ramp.elements[0].color=(*rgb,1);c.color_ramp.elements[1].color=(*tone,1)
  m.node_tree.links.new(t.outputs['Fac'],c.inputs[0]);m.node_tree.links.new(c.outputs[0],bs.inputs['Base Color'])
 return m

def box(name,p,d,m,r=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=d
 o.data.materials.append(m);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if r:
  mod=o.modifiers.new('Chipped chamfer','BEVEL');mod.width=r;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def select(obs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]

steel=mat('Blistered blue steel',(.075,.127,.119),.62,.46)
amber=mat('Kiln yellow enamel',(.63,.27,.055),.16,.53)
dark=mat('Black iron fork aperture',(.034,.045,.041),.46)
shoes=mat('Bright worn steel',(.24,.30,.26),.65,.46)
oak=[mat('Seasoned dunnage '+str(i),c) for i,c in enumerate([
 (.18,.104,.052),(.23,.135,.072),(.252,.148,.080),(.20,.121,.056)])]
sand=mat('Packed tan earth',(.19,.132,.073),rough=.94,tone=(.34,.233,.136))
tarmac=mat('Road dust',(.078,.080,.073),rough=.94,tone=(.14,.145,.123))
gravel=mat('Dark road shoulder',(.14,.12,.083),rough=.97,tone=(.25,.228,.183))
cream=mat('Scuffed white paint',(.58,.52,.39),rough=.86)
container=mat('Olive grey cargo behind lane',(.11,.15,.136),rough=.86)
part=[]
for i in range(8):
 part.append(box('Oak deck slat',(-1.575+.45*i,0,.128),(.426,1.31,.066),oak[i%4],.009))
for y in (-.61,.61):
 part.append(box('Heavy steel perimeter',(0,y,.082),(3.64,.118,.15),steel,.012))
 for x in (-1.66,1.66):
  part.append(box('Corner shoe',(x,y,.143),(.11,.175,.024),shoes,.004))
for x in (-1.62,-.57,.57,1.62):
 part.append(box('Fork channel separator',(x,0,.058),(.142,1.33,.115),dark,.009))
 for y in (-.648,.648):
  part.append(box('Seat stop',(x,y,.107),(.192,.078,.15),amber,.01))
  bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.025,depth=.012,location=(x,y,.187))
  o=bpy.context.object;o.name='Fastener';o.data.materials.append(shoes);part.append(o)
select(part);bpy.ops.object.join();cradle=bpy.context.object;cradle.name='E1CrateCradle'
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
f=out/'e1-first-cover-cradle.glb';bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,export_animations=False)
data=f.read_bytes();size=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+size])
tri=sum(g['accessors'][q['indices']]['count']//3 for m in g['meshes'] for q in m['primitives'])
assert tri<1500 and len(data)<110000 and not g.get('textures')
bpy.data.objects.remove(cradle,do_unlink=True)

def get_mesh(path):
 b=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
 obs=sorted(set(s.objects)-b,key=lambda o:o.name)
 ret=[(o.data,o.matrix_world.copy()) for o in obs if o.type=='MESH']
 for o in obs:bpy.data.objects.remove(o,do_unlink=True)
 return ret

# Blender +Y is glTF -Z. A Three Y yaw produces the same Blender Z yaw.
cal=lambda p,r=0: Matrix.Translation(p)@Matrix.Rotation(r,4,'Z')
def put(mesh,name,tr):
 obs=[]
 for d,m in mesh:
  o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.matrix_world=tr@m;obs.append(o)
 return obs
base=get_mesh(f);crate=get_mesh(donor)
# Exact elevations are proof inputs, not inferred at install time.
def extrema(mesh,axis):
 v=[(m@q.co)[axis] for d,m in mesh for q in d.vertices]
 return min(v),max(v)
crate_low,crate_high=extrema(crate,2)
assert abs(crate_low)<.00001 and abs(crate_high-.8635)<.00001
assert abs(extrema(base,2)[0])<.001
crates=[(-1.15,.161,-.095),(0,.161,0),(1.15,.161,.045),(-.88,1.0245,-.095),(.27,1.0245,0)]
assert .128+.066/2==crates[0][1] and abs(crates[0][1]+crate_high-crates[3][1])<1e-5
bundles=[]
for i,row in enumerate(source['rows']):
 tf=cal((row['x'],-row['z'],0),row['ry'])
 obs=put(base,'Dunnage skid '+str(i),tf)
 for j,(x,y,z) in enumerate(crates):
  obs+=put(crate,'Reusable haul crate '+str(j),tf@cal((x,-z,y)))
 bundles.append(obs)
# Receiver data is small and retains shared assets. Only the unmodified exact
# GLB triangles are used by the native geometry receipt (not proxy volumes).
def dump(obs):
 v=[];idx=[]
 for o in obs:
  off=len(v)//3
  for q in o.data.vertices:
   p=o.matrix_world@q.co;v.extend(round(x,6) for x in (p.x,p.z,-p.y))
  o.data.calc_loop_triangles()
  idx.extend(off+j for t in o.data.loop_triangles for j in t.vertices)
 return {'vertices':v,'indices':idx}

assembled=[dump(oo) for oo in bundles]
road_edge=-source['ROAD']['half']
road_clearances=[round(road_edge-max(b['vertices'][2::3]),4) for b in assembled]
assert min(road_clearances)>4.0
manifest={**source,'scope':'Three optional static cover fits on flat terrain; no map install or actor.',
 'model':{'file':f.name,'bytes':len(data),'triangles':tri,'sha256':sha(f)},
 'crate':{'file':donor.name,'sha256':sha(donor),'sharedInstancesPerCover':5},
 'crateTranslationsXYZ':crates,'roadClearanceM':road_clearances}
(out/'art.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'geometry.json').write_text(json.dumps(assembled,separators=(',',':'))+'\n')
if '--no-render' in sys.argv:raise SystemExit(0)
box('Yard hardpack',(35,21,-.19),(94,66,.38),sand)
box('Exact road edge context',(35,0,-.049),(94,17,.1),tarmac)
box('Gravel shoulder',(34,9.15,-.046),(93,1.18,.1),gravel)
for i in range(16):box('Road edge paint',(5+i*4,8.07,.005),(2.9,.16,.015),cream)
rng=random.Random(19621)
for i in range(95):
 x=rng.uniform(15,44);y=rng.uniform(11,28)
 if min(math.hypot(x-r['x'],y+r['z']) for r in source['rows'])<2.5:continue
 rx=rng.uniform(.045,.13)
 box('Broken mineral chip',(x,y,.014),(rx,.65*rx,.024),gravel).rotation_euler.z=rng.random()*6
# A little depth behind the exact front cover; scenery, not baked into GLB.
for i,(x,y) in enumerate(((12,31),(17,34),(30,32),(39,34),(48,29),(47,37))):
 box('Distant freight hulk',(x,y,1.28),(3.6,2.2,2.56),container,.035)
 for sgn in (-1,1):box('Freight top rail',(x,y+sgn*1.038,2.52),(3.62,.076,.08),steel,.006)
 for j in range(6):box('Freight side rib',(x-1.48+.59*j,y-1.112,1.31),(.073,.046,2.36),steel,.005)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('Clear dusk');world.use_nodes=True;s.world=world
n=world.node_tree.nodes;sk=n.new('ShaderNodeTexSky');sk.sky_type='NISHITA';sk.sun_elevation=.58;sk.sun_rotation=2.9;sk.sun_size=.025
world.node_tree.links.new(sk.outputs[0],n['Background'].inputs[0]);n['Background'].inputs[1].default_value=.21
c=bpy.data.cameras.new('Cover fit');cam=bpy.data.objects.new('Cover fit',c);s.collection.objects.link(cam);s.camera=cam
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=88
for name,eye,at,lens,size in [
 ('detail',(25.3,12.2,1.68),(28.9,16.1,1.0),36,(924,1180)),
 ('road',(28.5,-4.25,6.1),(28.5,15.2,.82),24,(1280,848)),
]:
 cam.location=eye;cam.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler();c.lens=lens
 s.render.resolution_x,s.render.resolution_y=size
 s.render.filepath=str(out/('nov26-e1-first-cover-'+name+'.webp'));bpy.ops.render.render(write_still=True)
