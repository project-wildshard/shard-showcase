"""Compact feed station beside the approved W10a water trough."""
import bpy,hashlib,json,math,random,struct,sys
from pathlib import Path
from mathutils import Matrix,Vector
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(exist_ok=True,parents=True)
assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
pins={
 'w10a-paddock-trough-wip.glb':'ff0e65ffce361608b0872bd9368bdcced1b19f00d635c460dc6c3dcb6430d56d',
 'wsc-module-011-riding-fence.glb':'4b080d634287a167eba8cc4690b7fbedd0323244154a7bb96402262b71c4afe0',
}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
def mat(n,rgb,r=.74,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=metal
 return m
wood=[mat(n,r) for n,r in [('Toasted oak',(.265,.122,.043)),('Aged golden oak',(.37,.191,.069)),('Weathered edge',(.31,.144,.049)),('Endgrain shadow',(.147,.079,.031))]]
iron=mat('Blackened steel',(.064,.108,.108),.44,.52)
bronze=mat('Oxidized brass',(.336,.217,.106),.51,.38)
hay=[mat('Compressed hay '+str(i),c) for i,c in enumerate(((.42,.332,.114),(.52,.413,.178),(.59,.47,.197)))]
def box(n,p,dim,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=dim;o.data.materials.append(m)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Rounded wear','BEVEL');b.width=bevel;b.segments=1;bpy.ops.object.modifier_apply(modifier=b.name)
 return o
models=[]
for x in (-1.04,1.04):
 for y in (-.44,.44):
  models.append(box('Oiled corner upright',(x,y,.64),(.19,.17,1.28),wood[0],.026))
  models.append(box('Formed shoe',(x,y,.092),(.245,.224,.181),iron,.021))
for j in range(4):
 z=.44+j*.182
 for y in (-.48,.48):models.append(box('Weathered long stave',(0,y,z),(2.10,.106,.168),wood[j%3],.019))
 for x in (-1.06,1.06):models.append(box('End stave',(x,0,z),(.109,.88,.164),wood[(j+1)%3],.016))
models.append(box('Dark basin liner',(0,0,.416),(2.03,.85,.081),iron,.022))
for y in (-.495,.495):models.append(box('Rolled feeder rim',(0,y,1.129),(2.26,.129,.102),iron,.031))
for x in (-1.10,1.10):models.append(box('Rolled end lip',(x,0,1.129),(.124,.93,.10),iron,.029))
for x in (-.83,-.41,0,.45,.86):
 for y in (-.539,.539):models.append(box('Flush carriage head',(x,y,.981),(.045,.02,.045),bronze))
rng=random.Random(9753)
for i in range(25):
 x=rng.uniform(-.90,.90);y=rng.uniform(-.345,.345);z=.73+.115*(1-(x/.94)**2)+rng.uniform(-.026,.032)
 o=box('Loose hay sweep',(x,y,z),(rng.uniform(.20,.47),rng.uniform(.08,.22),.11),hay[i%3],.009 if i%4==0 else 0)
 o.rotation_euler.z=rng.uniform(-.54,.54);models.append(o)
for x in (-.54,.53):
 o=box('Bale binding',(x,.031,.864),(.023,.70,.038),wood[3],.006);o.rotation_euler.z=.076;models.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in models:o.select_set(True)
bpy.context.view_layer.objects.active=models[0];bpy.ops.object.join()
o=bpy.context.object;o.name='Paddock Feed Bin';bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
file=out/'w10a-paddock-feed-bin.glb'
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_animations=False,export_texcoords=False)
d=file.read_bytes();g=json.loads(d[20:20+struct.unpack_from('<I',d,12)[0]])
nt=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
assert len(d)<135000 and nt<2700 and not g.get('textures')
bpy.data.objects.remove(o,do_unlink=True)
def load(file,p):
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(file));obs=set(s.objects)-old
 for o in obs:
  if o.parent not in obs:o.matrix_world=Matrix.Translation(p)@o.matrix_world
 bpy.context.view_layer.update()
 return obs
feed=(-17,-32,0); trough=(-12,-32,0)
def donor(f,p):
 path=assets/f;assert sha(path)==pins[f];return load(path,p)
def bounds(obs):
 v=[o.matrix_world@p.co for o in obs if o.type=='MESH' for p in o.data.vertices]
 return [[round(k(p[i] for p in v),6) for i in range(3)] for k in (min,max)]
fb=bounds(load(file,feed))
tb=bounds(donor('w10a-paddock-trough-wip.glb',trough))
clear=tb[0][0]-fb[1][0]
assert clear>2 and fb[0][0]>-21.6 and fb[1][0]<-6 and fb[0][2]==0
(out/'fit.json').write_text(json.dumps({'scope':'Static paddock dressing, no equine use or level install','threeWorldChuteOrigin':[-40,0,-132],
 'threeFeedOrigin':[-57,0,-100],'threeTroughOrigin':[-52,0,-100],'feedBoundsLocalBlender':fb,
 'troughBoundsLocalBlender':tb,'horizontalGapToTroughM':round(clear,6),
 'minLateralGapTo12mChuteAxisZoneM':round(-6-fb[1][0],6),
 'glb':{'file':file.name,'sha256':sha(file),'bytes':len(d),'triangles':nt}},indent=2)+'\n')
if '--no-render' in sys.argv:sys.exit(0)
# Surrounding ground is a review stage.
soil=mat('Dry paddock earth',(.298,.211,.119),.90);grass=mat('Trampled meadow',(.151,.217,.088),.96)
box('Flat paddock ground',(-10,-32,-.15),(64,64,.30),soil)
box('Staged verge',(-20.65,-32,.017),(2.8,19,.042),grass)
for j in range(5):
 pose=(-21.8,-39+j*3.13,0);o=donor('wsc-module-011-riding-fence.glb',pose)
 for i in o:
  if i.parent not in o:i.matrix_world=Matrix.Translation(pose)@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(tuple(-x for x in pose))@i.matrix_world
v=[];f=[]
for k in range(300):
 x,y=rng.uniform(-21.6,-7),rng.uniform(-42,-24)
 if abs(x-feed[0])<1.4 and abs(y-feed[1])<.8 or abs(x-trough[0])<2 and abs(y-trough[1])<1.1:continue
 n=len(v);v.extend([(x-.025,y,0),(x+.025,y,0),(x+.079,y+.091,rng.uniform(.034,.23))]);f.append((n,n+1,n+2))
m=bpy.data.meshes.new('Dry grass staging');m.from_pydata(v,[],f);m.update();m.materials.append(grass)
ob=bpy.data.objects.new('Dry grass staging',m);s.collection.objects.link(ob)
s.world=bpy.data.worlds.new('Open stable yard sky');s.world.use_nodes=True
n=s.world.node_tree.nodes;n['Background'].inputs[0].default_value=(.31,.46,.61,1);n['Background'].inputs[1].default_value=.49
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object;sun.data.energy=2.48;sun.data.angle=.11;sun.data.color=(1,.84,.66)
sun.rotation_euler=Vector((.32,.72,-.55)).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=30;s.cycles.adaptive_threshold=.026;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=89
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
for k,eye,t,lens,w,h in [('feed',(-18.8,-35.2,2.34),(-16.72,-31.82,.75),38,1040,980),
                       ('pair',(-17.6,-39.8,4.8),(-14.72,-32.14,.72),36,1250,860)]:
 cam.location=eye;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.resolution_x=w;s.render.resolution_y=h
 s.render.filepath=str(out/f'nov27-w10a-paddock-{k}.webp');bpy.ops.render.render(write_still=True)
