"""Original playable Walker character. Forward -Y, ground +Z."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'art/actors/forge-walker'
TMP=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else D
TMP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene;S.render.fps=30
def mat(n,c,m=.61,r=.4,e=0):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True
 p=a.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1)
 p.inputs['Metallic'].default_value=m;p.inputs['Roughness'].default_value=r
 p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=e
 return a
steel=mat('Blued steeling',(.072,.109,.133));bright=mat('Brushed edge',(.33,.39,.43),.87,.25)
rubber=mat('Track graphite',(.019,.028,.031),.19,.58);copper=mat('Dull copper',(.57,.28,.11),.61,.35)
glow=mat('Synthetic turquoise filament',(.06,.66,.57),.14,.29,2.0)
warm=mat('Signal amber',(.94,.29,.066),.22,.25,2.15);words=mat('Placard ink',(.77,.85,.79),0,.44,.55)
def geom(a,c,n,m,bevel=0):
 a.name=n
 for o in list(a.users_collection):o.objects.unlink(a)
 c.objects.link(a);a.data.materials.append(m)
 if bevel:
  b=a.modifiers.new('Industrial chamfer','BEVEL');b.width=bevel;b.segments=1
  a.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return a
def box(c,n,p,d,m,b=.045,rotation=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=rotation
 return geom(o,c,n,m,b)
def orb(c,n,p,d,m):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=p);o=bpy.context.object;o.scale=d
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return geom(o,c,n,m)
def cyl(c,n,p,r,d,m,axis='Z',v=12):
 rot={'X':(0,math.pi/2,0),'Y':(math.pi/2,0,0),'Z':(0,0,0)}[axis]
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=p,rotation=rot)
 return geom(bpy.context.object,c,n,m,min(r*.12,.020))
def rod(c,n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(c,n,(a+b)/2,r,(b-a).length,m,v=8)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

# Material-only authoring keeps the prototype editable and cheap to load.
indigo=mat('Deep indigo duck canvas',(.026,.081,.136),.09,.57)
blue=mat('Worn Petrol enamel',(.044,.263,.297),.53,.42)
leather=mat('Russet belt leather',(.176,.077,.041),.05,.55)
cloth=mat('Fired orange neck wrap',(.54,.159,.062),.04,.63)
brass=mat('Brushed bronze plates',(.57,.313,.126),.68,.30)
titan=mat('Pale ceramic mask',(.66,.70,.62),.32,.32)
lens=mat('Sea-glass visor',(.020,.34,.38),.50,.22,1.42)
c=bpy.data.collections.new('Walker | Yard Warden');S.collection.children.link(c)
defs={};groups={}
def joint(n,p,par=None):defs[n]=(p,par)
def attach(n,*o):groups.setdefault(n,[]).extend(o)
def profile(name,levels,m):
 # octagonal bevel integrated in each inset ring rather than a hard cube
 vertices=[(x+w*math.cos(a*math.tau/8+math.pi/8),y+d*math.sin(a*math.tau/8+math.pi/8),z)
           for x,y,z,w,d in levels for a in range(8)]
 faces=[tuple(range(7,-1,-1)),tuple(range(len(vertices)-8,len(vertices)))]
 for j in range(len(levels)-1):
  for a in range(8):faces.append((j*8+a,j*8+(a+1)%8,(j+1)*8+(a+1)%8,(j+1)*8+a))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);c.objects.link(o);o.data.materials.append(m)
 b=o.modifiers.new('Wear rounded edges','BEVEL');b.width=.014;b.segments=2
 o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
joint('root',(0,0,0));joint('pelvis',(0,0,.91),'root');joint('chest',(0,.014,1.22),'pelvis')
joint('head',(0,-.035,1.59),'chest');joint('pack',(0,.17,1.35),'chest');joint('coat',(0,.12,.89),'pelvis')
attach('pelvis',profile('Waisted utility breeches',[(0,.02,.78,.24,.14),(0,0,.93,.24,.15),(0,0,1.00,.21,.135)],indigo),
 box(c,'Wide leather duty belt',(0,0,.984),(.47,.30,.079),leather,b=.025),
 box(c,'Setback bronze buckle',(0,-.157,.984),(.14,.041,.10),brass,b=.024))
attach('chest',profile('Moulded canvas jacket',[(0,.005,.99,.212,.14),(0,.005,1.23,.25,.175),(0,.016,1.43,.31,.165),(0,.012,1.50,.238,.12)],indigo),
 profile('Petrol overlapping chest plates',[(0,-.122,1.075,.196,.057),(0,-.139,1.32,.257,.057),(0,-.115,1.463,.234,.056)],blue),
 box(c,'Bronze undertorso nameplate',(.055,-.196,1.333),(.16,.024,.045),brass,b=.010),
 cyl(c,'Sealed collar',(0,-.014,1.547),.125,.118,cloth,v=12))
for q in (-1,1):
 attach('chest',rod(c,'Cross-body webbing',(q*.208,-.061,1.45),(q*.104,-.175,1.074),.020,leather),
  box(c,'Torso latch',(q*.16,-.177,1.21),(.087,.045,.044),titan,b=.012))
 for z in (1.135,1.196):
  attach('chest',box(c,'Rib reinforcement',(q*.212,-.105,z),(.072,.063,.030),bright,b=.009))
attach('head',profile('Faceted hard-shell helmet',[(0,-.034,1.565,.11,.102),(0,-.040,1.638,.151,.136),(0,-.022,1.766,.154,.131),(0,.002,1.866,.114,.104),(0,.011,1.886,.066,.07)],blue),
 profile('Ceramic lower respirator',[(0,-.131,1.588,.084,.057),(0,-.146,1.64,.123,.055),(0,-.149,1.702,.119,.045)],titan),
 box(c,'Obsidian visor cavity',(0,-.151,1.738),(.27,.075,.092),rubber,b=.035),
 box(c,'Saturated narrow face strip',(0,-.189,1.742),(.217,.014,.041),lens,b=.011),
 cyl(c,'Respirator canister',(-.103,-.176,1.638),.045,.073,brass,'Y',10))
for j in range(4):
 attach('head',box(c,'Ceramic breathing slot',(-.023+.028*j,-.194,1.627),(.011,.017,.053),rubber,b=.004))
attach('pack',profile('Waxed canvas coil pack',[(0,.173,1.11,.181,.103),(0,.212,1.22,.197,.128),(0,.215,1.47,.173,.124),(0,.173,1.50,.132,.092)],leather),
 box(c,'Worn pack plate',(0,.326,1.31),(.25,.045,.28),blue,b=.058),
 box(c,'Back cell gauge',(0,.352,1.32),(.067,.022,.126),lens,b=.015),
 cyl(c,'Left cooling flask',(-.193,.243,1.28),.066,.291,brass,v=10),
 cyl(c,'Right cooling flask',(.193,.241,1.28),.067,.291,steel,v=10))
for x in (-.082,.082):
 attach('coat',profile('Split lower coat',[(x,.142,.62,.071,.037),(x,.127,.83,.075,.042),(x,.092,.96,.074,.048)],cloth),
  box(c,'Coat binding',(x,.159,.645),(.097,.032,.047),leather,b=.011))
for q,key in [(-1,'L'),(1,'R')]:
 u='upper_'+key;e='elbow_'+key;h='hand_'+key;g='hip_'+key;k='knee_'+key;f='boot_'+key
 joint(u,(q*.284,.012,1.445),'chest');joint(e,(q*.361,.005,1.176),u);joint(h,(q*.399,-.041,1.002),e)
 joint(g,(q*.139,.055,.91),'pelvis');joint(k,(q*.169,.010,.515),g);joint(f,(q*.174,-.013,.144),k)
 attach(u,rod(c,'Padded shoulder sleeve',(q*.294,.013,1.42),(q*.360,.012,1.178),.098,indigo),
  orb(c,'Rounded shoulder pauldron',(q*.312,.026,1.441),(.134,.123,.127),brass if q==1 else blue),
  box(c,'Pauldron fastener',(q*.339,-.098,1.42),(.054,.028,.05),bright,b=.015))
 attach(e,rod(c,'Canvas forearm',(q*.361,.004,1.179),(q*.398,-.022,1.016),.075,indigo),
  profile('Overlapping forearm bracer',[(q*.398,-.017,1.027,.083,.076),(q*.372,-.015,1.167,.102,.086)],blue),
  box(c,'Small bronze strap',(q*.391,-.105,1.078),(.105,.034,.045),brass,b=.017))
 attach(h,orb(c,'Leather glove',(q*.400,-.042,.987),(.079,.079,.085),leather),
  box(c,'Padded knuckle keeper',(q*.411,-.101,.991),(.113,.035,.078),titan,b=.022))
 attach(g,profile('Jointed upper trousers',[(q*.168,.008,.525,.105,.100),(q*.146,.052,.76,.136,.128),(q*.137,.043,.908,.119,.112)],indigo))
 attach(k,profile('Armoured lower leg',[(q*.173,-.017,.139,.086,.078),(q*.171,-.002,.310,.101,.093),(q*.169,.014,.532,.114,.101)],indigo),
  profile('Split petrol shin cover',[(q*.174,-.076,.195,.07,.036),(q*.171,-.062,.390,.092,.060)],blue),
  orb(c,'Bronze knee cap',(q*.173,-.100,.515),(.105,.048,.084),brass))
 attach(f,profile('Industrial grip boot',[(q*.174,-.070,.035,.107,.168),(q*.174,-.070,.089,.106,.174),(q*.174,-.047,.178,.099,.137)],rubber),
  box(c,'Safety bronze toe',(q*.174,-.200,.106),(.17,.104,.079),brass,b=.032))
arm=bpy.data.armatures.new('Walker skeleton');rig=bpy.data.objects.new('WSC-ACTOR-WALKER Forge Warden',arm);c.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for n,(p,par) in defs.items():
 b=arm.edit_bones.new(n);b.head=p;b.tail=(p[0],p[1],p[2]+.125)
 if par:b.parent=arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT')
def bind(o,name):
 w=o.matrix_world.copy();o.parent=rig;o.parent_type='BONE';o.parent_bone=name
 bpy.context.view_layer.update();o.matrix_world=w
for n,objects in groups.items():
 for o in objects:bind(o,n)
for n,p,par in [('grip_R',(.415,-.049,.995),'hand_R'),('grip_L',(-.415,-.049,.995),'hand_L'),('ground_socket',(0,0,0),'root')]:
 o=bpy.data.objects.new(n,None);o.location=p;c.objects.link(o);bpy.context.view_layer.update();bind(o,par)
for q in rig.pose.bones:q.rotation_mode='XYZ'
def pose(role,x):
 f={n:[0.,0.,0.,0.,0.,0.] for n in defs}
 f['upper_R'][0]=-.21;f['elbow_R'][0]=-.52;f['upper_L'][0]=-.08;f['elbow_L'][0]=-.16
 if role=='idle':
  f['chest'][4]=x*.018;f['head'][1]=x*.11;f['coat'][0]=x*.08
 elif role=='stride':
  f['hip_L'][0]=x*.68;f['hip_R'][0]=-x*.68
  f['knee_L'][0]=max(0,-x)*.51;f['knee_R'][0]=max(0,x)*.51
  f['upper_L'][0]-=x*.41;f['upper_R'][0]+=x*.20;f['pelvis'][4]=abs(x)*.043;f['coat'][0]=x*.27
 elif role=='turn':
  f['pelvis'][1]=x*.20;f['chest'][1]=x*.29;f['head'][1]=x*.40;f['hip_R'][0]=-x*.23;f['coat'][1]=-x*.22
 elif role=='dodge':
  f['pelvis'][4]=-x*.29;f['chest'][0]=-x*.60;f['head'][0]=x*.33
  f['hip_L'][0]=-x*.73;f['hip_R'][0]=-x*.52;f['knee_L'][0]=x*1.22;f['knee_R'][0]=x*1.10
  f['upper_R'][0]-=x*.43;f['coat'][0]=-x*.40
 elif role=='hit':
  f['pelvis'][2]=x*.16;f['chest'][0]=x*.32;f['head'][0]=x*.25;f['upper_L'][2]=x*.51
 elif role=='defeat':
  f['pelvis'][4]=-x*.64;f['chest'][0]=x*.87;f['hip_L'][0]=-x*1.15
  f['hip_R'][0]=-x*.89;f['knee_L'][0]=x*1.42;f['knee_R'][0]=x*1.18;f['head'][0]=x*.50
 elif role=='sweep':
  f['chest'][1]=-x*.69;f['upper_R'][1]=-x*.53;f['upper_R'][2]=x*.80
  f['elbow_R'][0]-=x*.53;f['hand_R'][1]=-x*.36;f['hip_L'][0]=-abs(x)*.25
 elif role=='chop':
  f['chest'][0]=-x*.27;f['upper_R'][0]=-.39+x*.96;f['elbow_R'][0]=-.64+x*.50
  f['hand_R'][0]=x*.26;f['hip_L'][0]=-abs(x)*.24;f['coat'][0]=x*.34
 else:
  f['chest'][0]=-x*.28;f['chest'][1]=x*.26;f['upper_R'][0]=-.43-x*.78
  f['elbow_R'][0]=-.53+x*.34;f['hand_R'][0]=x*.36;f['hip_L'][0]=-abs(x)*.40
 return f
att=[(1,0),(7,-.63),(15,1.0),(22,.54),(30,0)]
clips=[('Idle','idle',[(1,0),(13,1),(25,0),(37,-1),(49,0)]),
 ('Stride','stride',[(1,0),(7,1),(13,0),(19,-1),(25,0)]),
 ('Turn','turn',[(1,0),(7,1),(15,0)]),
 ('Dodge','dodge',[(1,0),(5,1),(10,.68),(16,0)]),
 ('Hit','hit',[(1,0),(5,1),(15,0)]),
 ('Defeat','defeat',[(1,0),(10,.34),(25,1),(36,1)]),
 ('Sweep','sweep',att),('Chop','chop',att),('Thrust','thrust',att)]
for title,role,frames in clips:
 for frame,x in frames:
  for n,v in pose(role,x).items():
   b=rig.pose.bones[n];b.rotation_euler=v[:3];b.location=v[3:]
   b.keyframe_insert(data_path='rotation_euler',frame=frame,group=n)
   b.keyframe_insert(data_path='location',frame=frame,group=n)
 a=rig.animation_data.action;a.name='Walker '+title;rig.animation_data.action=None
 t=rig.animation_data.nla_tracks.new();t.name=title;t.strips.new(title,1,a)
bpy.ops.object.select_all(action='DESELECT')
for o in c.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(D/'walker.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animation_mode='NLA_TRACKS')
for t in rig.animation_data.nla_tracks:t.mute=True
for n,v in pose('idle',0).items():
 b=rig.pose.bones[n];b.rotation_euler=v[:3];b.location=v[3:]
S.frame_set(1)
bpy.ops.mesh.primitive_plane_add(size=72);bpy.context.object.data.materials.append(mat('Neutral charcoal floor',(.027,.046,.052),.15,.57))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,pp,e,col,s in [('Cool key',(-3,-5,4.4),1000,(.67,.88,1.0),3.3),('Foundry rim',(3,2,3.8),1200,(1,.58,.31),2.7),
 ('Cool back fill',(-2,3,3.5),400,(.55,.81,1),2.9)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=e;l.color=col;l.size=s
 o=bpy.data.objects.new(n,l);S.collection.objects.link(o);o.location=pp;aim(o,(0,0,1.00))
world=bpy.data.worlds.new('Studio');S.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
camdata=bpy.data.cameras.new('Studio portrait');cam=bpy.data.objects.new('Studio portrait',camdata);S.collection.objects.link(cam);S.camera=cam
cam.location=(3.28,-5.5,2.62);aim(cam,(0,0,1.0));camdata.type='ORTHO';camdata.ortho_scale=2.38
S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=False
S.render.resolution_x=640;S.render.resolution_y=792;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(TMP/'front.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'walker.blend'),compress=True)
bpy.ops.render.render(write_still=True)
cam.location=(-3.28,5.5,2.64);aim(cam,(0,0,1.0));S.render.filepath=str(TMP/'back.png');bpy.ops.render.render(write_still=True)
