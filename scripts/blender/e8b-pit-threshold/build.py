"""Shoulder lanterns for both existing E8b openings. No new floor or trim on the rim."""
import bpy,hashlib,json,math,random,struct,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(exist_ok=True,parents=True)
root=Path(__file__).resolve().parents[3]
assets=root/'public/assets/wildshard-art'
pit=assets/'e8b-big-pallet-pit.glb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pit)=='37816bad3b38f8b8d72b8fe87af478488ee1243c9f6cfed9b92f5d7336ce799f'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def mat(name,c,rough=.65,metal=0,glow=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF')
 for k,v in [('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal),('Emission Color',(*c,1)),('Emission Strength',glow)]:b.inputs[k].default_value=v
 return m
iron=mat('Waxed cast iron',(.046,.064,.067),.59,.43)
paint=mat('Cured ochre enamel',(.40,.145,.036),.51,.17)
used=mat('Scuffed ochre edge',(.55,.297,.105),.66,.13)
steel=mat('Oil-black anchor bolts',(.101,.112,.126),.43,.72)
lens=mat('Amber sealed glass',(.88,.286,.061),.25,.05,.42)
mineral=mat('Aggregate shoulder plinth',(.211,.201,.173),.85)
def box(n,p,sz,m,b=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p)
 o=bpy.context.object;o.name=n;o.dimensions=sz;o.data.materials.append(m)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  d=o.modifiers.new('Cast rolled corner','BEVEL');d.width=b;d.segments=1
  bpy.ops.object.modifier_apply(modifier=d.name)
 return o
parts=[
 box('Low plinth',(0,0,.075),(.89,.88,.15),mineral,.043),
 box('Foot casting',(0,0,.172),(.63,.61,.074),iron,.028),
 box('Ribbed vertical enclosure',(0,0,.656),(.39,.386,.94),paint,.054),
 box('Lamp gasket',(0,0,1.10),(.45,.415,.073),iron,.02),
 box('Shade lip',(0,0,1.31),(.51,.48,.13),iron,.047),
 box('Sealed amber lens',(0,0,1.196),(.337,.336,.14),lens,.023),
]
for x in (-.262,.262):
 for y in (-.249,.249):
  bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.039,depth=.032,location=(x,y,.219))
  o=bpy.context.object;o.name='Recessed foundation fastener';o.data.materials.append(steel);parts.append(o)
for x in (-.17,.17):
 for y in (-.175,.175):
  parts.append(box('Armored lens corner',(x,y,1.176),(.073,.072,.18),iron,.022))
for face in (-1,1):
 for y in (-.106,.106):
  parts.append(box('Cast impact rib',(face*.201,y,.56),(.037,.046,.48),used,.014))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
o=bpy.context.object;o.name='Pallet Pit Enclosed Shoulder Lantern'
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
dest=out/'e8b-pit-shoulder-lantern.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_animations=False,export_texcoords=False)
raw=dest.read_bytes();g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
assert tri<930 and len(raw)<78000 and not g.get('textures')
bpy.data.objects.remove(o,do_unlink=True)
def load(path):
 prior=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(path));return list(set(s.objects)-prior)
def geometry(objs):
 v=[];f=[]
 for o in sorted(objs,key=lambda o:o.name):
  if o.type!='MESH':continue
  m=o.data;m.calc_loop_triangles()
  a=len(v);v.extend(o.matrix_world@p.co for p in m.vertices)
  f.extend(tuple(a+x for x in t.vertices) for t in m.loop_triangles)
 return v,f
pobjs=load(pit)
bpy.context.view_layer.update()
v,f=geometry(pobjs)
pitB=BVHTree.FromPolygons(v,f,all_triangles=True)
placements=[]
for sign in (-1,1):
 for x in (-3.55,3.55):
  objs=load(dest)
  for o in objs:
   if o.parent not in objs:o.matrix_world=Matrix.Translation((x,-15.6*sign,0))@o.matrix_world
  bpy.context.view_layer.update()
  a,b=geometry(objs)
  for q in a:assert abs(q.x)>3.10 and q.xy.length>14
  assert not pitB.overlap(BVHTree.FromPolygons(a,b,all_triangles=True))
  placements.append({'local':[x,0,15.6*sign],'radiusToPitM':round(min(q.xy.length for q in a),6)})
res={'scope':'Static geometry fit only. Separate flat fixture tests the stock path.', 'center':[96,0,-206],'pitSha256':sha(pit),'lantern':{'name':dest.name,'sha256':sha(dest),'bytes':len(raw),'triangles':tri},'placements':placements}
(out/'art-fit.json').write_text(json.dumps(res,indent=2)+'\n')
if '--no-render' in sys.argv:sys.exit(0)
concrete=mat('Worn ground',(.218,.191,.155),.924)
pave=mat('Pale approach stones',(.304,.274,.227),.88)
deep=mat('Worn iron service joint',(.057,.064,.057),.91)
box('Ground review only',(0,0,-.145),(79,79,.29),concrete)
for sign in (-1,1):
 for j in range(6):
  for i in (-1,0,1):
   box('Road flags',(i*1.84,(16+j*1.68)*sign,-.007),(1.81,1.65,.018),pave)
 for k in (-1,1):
  box('Dark approach drainage lip',(k*3.01,19.1*sign,.006),(.15,9.8,.015),deep,.002)
rng=random.Random(283)
for k in range(100):
 x,y=rng.uniform(-18,18),rng.uniform(-25,25)
 if math.hypot(x,y)<14 or abs(x)<3.15:continue
 ob=box('Weathered clinker',(x,y,.018),(.16,.11,.062),pave,.013);ob.rotation_euler.z=rng.random()*math.pi
s.world=bpy.data.worlds.new('Cloud break above the pit');s.world.use_nodes=True
w=s.world.node_tree.nodes['Background'];w.inputs[0].default_value=(.31,.43,.59,1);w.inputs[1].default_value=.51
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=2.3;sun.data.angle=.09;sun.data.color=(1,.81,.61)
sun.rotation_euler=Vector((.34,-.67,-.73)).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=27;s.cycles.adaptive_threshold=.029;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=88
bpy.ops.object.camera_add()
cam=bpy.context.object;s.camera=cam
for key,eye,target,lens,width,height in [
 ('entry',(0,-23.5,1.72),(0,-12.1,.85),25,980,1150),
 ('pit',(20,-29,25),(0,.4,.7),34,1350,940),
]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.resolution_x,s.render.resolution_y=width,height
 s.render.filepath=str(out/f'nov27-pallet-pit-{key}.webp')
 bpy.ops.render.render(write_still=True)
