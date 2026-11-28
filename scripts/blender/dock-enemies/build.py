"""Original rigid robots for the Wildshard demo; four initial locomotion shapes."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[3]; OUT=R/'art/actors/dock-enemies'
TMP=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else OUT
TMP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.fps=30
def mat(name,color,metal=.62,rough=.38,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
iron=mat('Iron . oiled',(.045,.075,.083));silver=mat('Nickel . edges',(.26,.36,.39),.81,.26)
brass=mat('Bronze . collars',(.48,.24,.076));tire=mat('Graphite . treads',(.018,.023,.032),.17,.56)
dark=mat('Arena slab',(.039,.051,.065),.18,.49)
labels=mat('Stand labels',(.65,.88,.86),0,.4,.7)

def attach_collection(o,c,m):
 for other in list(o.users_collection):other.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m)
 return o
def polish(o,r):
 b=o.modifiers.new('Tool bevel','BEVEL');b.width=r;b.segments=1
 o.modifiers.new('Weighted facets','WEIGHTED_NORMAL');return o
def box(c,n,p,d,m,r=.035,angle=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=angle
 return polish(attach_collection(o,c,m),r)
def orb(c,n,p,d,m):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=p);o=bpy.context.object;o.name=n
 o.scale=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return attach_collection(o,c,m)
def wheel(c,n,p,r,d,m,v=12,axis='X'):
 rot=(0,math.pi/2,0) if axis=='X' else (math.pi/2,0,0) if axis=='Y' else (0,0,0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=p,rotation=rot)
 o=bpy.context.object;o.name=n;return polish(attach_collection(o,c,m),.015)
def beam(c,n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=wheel(c,n,(a+b)/2,r,(b-a).length,m,8,axis='Z')
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def faceplate(c,n,x,y,z,w,h,color,glow):
 objs=[box(c,n,(x,y,z),(w,.23,h),iron,r=.055),
       box(c,'Sensor slot',(x,y-.122,z+.018),(w*.69,.035,h*.26),glow,r=.012)]
 for sign in (-1,1):objs.append(box(c,'Shell steel plate',(x+sign*w*.42,y-.10,z),(w*.11,.09,h*.73),color,r=.015))
 return objs

spec=[('sentry','Gate Sentry',(0.57,.27,.075),'windmill'),('skitter','Rivet Skitter',(.12,.48,.52),'pounce'),
      ('wasp','Beacon Wasp',(.41,.26,.65),'beam'),('ram','Ballast Ram',(.58,.155,.10),'charge')]
for i,(slug,label,col,style) in enumerate(spec):
 c=bpy.data.collections.new(label);s.collection.children.link(c)
 paint=mat(label+' enamel',col,.45,.34)
 eye=mat(label+' eye',(.08,.74,.68) if style in ('windmill','pounce') else (1,.37,.11),.1,.27,1.8)
 mapping={};defs={}
 def joint(n,p,parent='body'):defs[n]=p,parent
 def put(n,*objs):mapping.setdefault(n,[]).extend(objs)
 joint('root',(0,0,0),None)
 if style=='windmill':
  joint('body',(0,0,1.23),'root');joint('head',(0,-.07,2.05))
  slag=mat('Sentry . stoved graphite',(.037,.050,.054),.52,.45)
  heat=mat('Sentry . scorched yellow enamel',(.43,.198,.047),.46,.39)
  ivory=mat('Sentry . ceramic cheek guards',(.52,.43,.30),.38,.4)
  put('body',box(c,'Armature torso casting',(0,.017,1.51),(.70,.45,.61),slag,r=.08),
      box(c,'Bronze chest breastplate',(0,-.173,1.58),(.82,.26,.47),heat,r=.078),
      box(c,'Triple-ribbed sternum shield',(0,-.305,1.54),(.47,.11,.36),iron,r=.046),
      wheel(c,'Core aperture bezel',(0,-.362,1.54),.131,.043,brass,12,'Y'),
      wheel(c,'Inset core emitter',(0,-.390,1.54),.071,.027,eye,12,'Y'),
      box(c,'Waist saddle',(0,.023,1.13),(.50,.37,.25),slag,r=.063),
      box(c,'Ribbed back servo housing',(0,.224,1.55),(.46,.20,.405),iron,r=.045))
  for q in (-1,1):
   put('body',box(c,'Angled collar strut',(q*.334,-.083,1.81),(.159,.31,.112),ivory,r=.022,angle=q*.21),
       box(c,'Sternum copper retainer',(q*.206,-.362,1.51),(.047,.041,.23),brass,r=.010))
  for z in (1.43,1.52,1.61,1.70):
   put('body',box(c,'Servo exhaust slat',(0,.339,z),(.33,.035,.028),silver,r=.008))
  put('head',box(c,'Sloped armor brow',(0,-.130,2.09),(.63,.31,.188),heat,r=.054),
      box(c,'Graphite recessed eye bay',(0,-.232,2.016),(.44,.12,.113),slag,r=.021),
      box(c,'Three-quarter-width visor',(0,-.298,2.021),(.321,.021,.034),eye,r=.009),
      box(c,'Ceramic lower faceplate',(0,-.254,1.951),(.38,.11,.102),ivory,r=.022))
  for sign,name in [(-1,'L'),(1,'R')]:
   put('head',box(c,'Recessed comm terminal',(sign*.287,-.079,2.038),(.096,.192,.131),slag,r=.028),
       wheel(c,'Comms fender bolt',(sign*.338,-.085,2.038),.028,.018,silver,8))
   x=sign*.285;joint('leg_'+name,(x,0,1.20))
   put('leg_'+name,beam(c,'Piston shank',(x,0,1.12),(x,-.02,.23),.101,silver),
       box(c,'Lower leg armor face',(x,-.091,.47),(.241,.202,.447),slag,r=.042),
       box(c,'Shin plate collar',(x,-.203,.635),(.206,.066,.20),heat,r=.040),
       box(c,'Grip sole',(x,-.14,.098),(.32,.49,.14),iron,r=.042),
       box(c,'Forged toe cap',(x,-.285,.178),(.29,.212,.135),ivory,r=.035))
   x=sign*.54;joint('arm_'+name,(x,0,1.73))
   put('arm_'+name,box(c,'High drive shoulder' if sign>0 else 'Narrow stabilizing shoulder',(x,0,1.69),(.39,.48,.41) if sign>0 else (.29,.36,.29),heat,r=.074 if sign>0 else .054),
       wheel(c,'Rotary shoulder bearing',(x+sign*.177,.008,1.673),.12,.046,iron,12))
 elif style=='pounce':
  joint('body',(0,0,.55),'root');joint('head',(0,-.51,.69))
  put('body',orb(c,'Low shell',(0,0,.67),(.51,.64,.345),paint),box(c,'Carapace rail',(0,-.04,.97),(.43,.61,.14),iron))
  put('head',*faceplate(c,'Split head',0,-.55,.64,.46,.36,paint,eye))
  for xsign in (-1,1):
   for ysign in (-1,1):
    x,yy=xsign*.35,ysign*.35;n='leg_'+('L' if xsign<0 else 'R')+('F' if ysign<0 else 'B')
    joint(n,(x,yy,.59))
    end=(xsign*.69,yy+ysign*.19,.15)
    put(n,beam(c,'Knee strut',(x,yy,.58),end,.094,silver),orb(c,'Fore claw',end,(.15,.18,.10),iron),
        orb(c,'Exposed knee',(x,yy,.60),(.146,.13,.12),brass))
 elif style=='beam':
  joint('body',(0,0,1.27),'root');joint('head',(0,-.35,1.23))
  put('body',orb(c,'Hover nacelle',(0,.02,1.30),(.47,.52,.31),paint),box(c,'Cooling spine',(0,.12,1.54),(.23,.52,.14),iron))
  put('head',wheel(c,'Circular lens',(0,-.40,1.29),.222,.18,silver,16,'Y'),
      wheel(c,'Bright lens',(0,-.505,1.29),.128,.026,eye,16,'Y'))
  for sign,name in [(-1,'L'),(1,'R')]:
   x=sign*.63;joint('wing_'+name,(sign*.37,0,1.39))
   put('wing_'+name,box(c,'Gull strut',(x,.06,1.41),(.60,.22,.10),silver,r=.033,angle=sign*.3),
       wheel(c,'Rotor ring',(sign*.86,.08,1.41),.25,.116,iron,16,'Z'),
       wheel(c,'Rotor signal',(sign*.86,.08,1.49),.15,.034,eye,16,'Z'))
 elif style=='charge':
  joint('body',(0,0,.55),'root');joint('head',(0,-.65,.48))
  coat=mat('Ram . aged safety oxide',(.32,.113,.041),.51,.40)
  ivory=mat('Ram . heat-stained ceramic',(.51,.40,.24),.47,.42)
  def hull(n,rings,m):
   verts=[(math.cos(j*math.tau/8+math.pi/8)*w,y+math.sin(j*math.tau/8+math.pi/8)*d,z)
          for y,z,w,d in rings for j in range(8)]
   faces=[tuple(range(7,-1,-1)),tuple(range(len(verts)-8,len(verts)))]
   for k in range(len(rings)-1):
    for j in range(8):faces.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
   mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update()
   mesh.materials.append(m);o=bpy.data.objects.new(n,mesh);c.objects.link(o);return polish(o,.025)
  put('body',hull('Sloping segmented ballast hood',[(.01,.40,.46,.56),(.014,.76,.49,.65),(.092,1.01,.40,.51),(.139,1.103,.32,.363)],coat),
      box(c,'Low chassis casting',(0,.067,.42),(.88,1.09,.27),iron,r=.055),
      box(c,'Bronze corner hood panel',(0,.188,1.036),(.55,.59,.136),brass,r=.048),
      box(c,'Recessed radiator slot',(0,.176,1.112),(.44,.35,.028),iron,r=.021),
      box(c,'Rear counterweight bumper',(0,.61,.58),(.69,.135,.245),iron,r=.030))
  for j in range(5):
   put('body',box(c,'Radiator cross-vane',(0,.043+j*.059,1.135),(.369,.016,.021),silver,r=.005))
  put('head',hull('Forged plow base',[(-.730,.24,.44,.145),(-.759,.34,.59,.142),(-.711,.515,.57,.162),(-.697,.59,.47,.133)],iron),
      box(c,'Cold-struck plow edge',(0,-.844,.355),(.79,.13,.131),silver,r=.030),
      box(c,'Recessed optical housing',(0,-.754,.593),(.51,.111,.153),iron,r=.030),
      box(c,'Hot horizontal warning slit',(0,-.817,.616),(.404,.033,.043),eye,r=.010))
  for sign,name in [(-1,'L'),(1,'R')]:
   x=sign*.45;joint('roller_'+name,(x,0,.38))
   put('head',box(c,'Corner pushing shoe',(sign*.431,-.765,.448),(.22,.281,.197),ivory,r=.035,angle=sign*.15))
   put('body',box(c,'Armored axle fender',(sign*.458,.008,.768),(.145,.683,.111),coat,r=.039,angle=sign*.015))
   put('roller_'+name,wheel(c,'Graphite transport roller',(x,0,.37),.37,.235,tire,16),
       wheel(c,'Inset cast bronze hub',(sign*.584,0,.37),.251,.064,brass,14),
       wheel(c,'Outer dark hub',(sign*.626,0,.37),.177,.031,iron,14),
       wheel(c,'Octagonal bearing cap',(sign*.648,0,.37),.092,.039,silver,8))
   for j in range(6):
    t=j*math.tau/6
    put('roller_'+name,wheel(c,'Hub perimeter pin',(sign*.646,.132*math.cos(t),.37+.132*math.sin(t)),.020,.024,silver,6))
   for j in range(10):
    t=j*math.tau/10
    shoe=box(c,'Forged traction shoe',(x,.361*math.sin(t),.37+.361*math.cos(t)),(.221,.116,.050),iron,r=.010)
    shoe.rotation_euler.x=-t
    put('roller_'+name,shoe)
 # Make the larger right tool the obvious sweep side.
 if style=='windmill':
  for sign,name in [(-1,'L'),(1,'R')]:
   x=sign*.57
   put('arm_'+name,beam(c,'Forearm piston',(x,0,1.54),(x,-.12,1.14),.087,silver),
       box(c,'Steel tool sleeve',(x,-.069,1.295),(.253,.238,.31),slag,r=.044),
       box(c,'Capped impact tool',(x,-.20,1.11),(.345 if sign>0 else .22,.393,.28),heat if sign>0 else iron,r=.051),
       box(c,'Ivory strike face' if sign>0 else 'Bronze stabilizer pad',(x,-.389,1.11),(.294 if sign>0 else .167,.062,.193),ivory if sign>0 else brass,r=.023))
   if sign>0:
    for j in (-1,0,1):
     put('arm_'+name,box(c,'Sweeper tool reinforcement rib',(x+j*.083,-.229,1.259),(.032,.243,.026),silver,r=.008))
 rigdata=bpy.data.armatures.new(label+' armature')
 rig=bpy.data.objects.new('WSC-ENM-'+str(i+1).zfill(3)+' '+label,rigdata);c.objects.link(rig)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.object.mode_set(mode='EDIT')
 for n,(p,parent) in defs.items():
  b=rigdata.edit_bones.new(n);b.head=p;b.tail=(p[0],p[1],p[2]+.14)
  if parent:b.parent=rigdata.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT')
 for q in rig.pose.bones:q.rotation_mode='XYZ'
 def bind(o,b):
  w=o.matrix_world.copy();o.parent=rig;o.parent_type='BONE';o.parent_bone=b
  bpy.context.view_layer.update();o.matrix_world=w
 for n,objs in mapping.items():
  for o in objs:bind(o,n)
 attack_p={'sentry':(.57,-.39,1.11),'skitter':(0,-.69,.59),'wasp':(0,-.522,1.29),'ram':(0,-.88,.48)}[slug]
 for n,p in [('ground_socket',(0,0,0)),('weak_socket',((0,-.79,.61) if slug=='ram' else (0,-.40 if slug!='skitter' else -.68,2.04 if slug=='sentry' else 1.23 if slug=='wasp' else .65))),('attack_socket',attack_p)]:
  o=bpy.data.objects.new(n,None);o.location=p;c.objects.link(o);bpy.context.view_layer.update()
  bind(o,'root' if n=='ground_socket' else 'arm_R' if n=='attack_socket' and slug=='sentry' else 'head')
 limbs=[n for n in defs if n.startswith(('leg_','arm_','wing_','roller_'))]
 def pose(kind,amount,k):
  v={n:[0.,0.,0.,0.,0.,0.] for n in defs}
  if kind=='idle':v['body'][4]=amount*(.085 if slug=='wasp' else .025);v['head'][1]=amount*.045
  elif kind=='move':
   for j,n in enumerate(limbs):
    v[n][0]=amount*(.52 if n.startswith('leg') else .21)*(1 if j%2==0 else -1)
   if slug=='ram':
    for n in limbs:v[n][0]=k*math.pi
   v['body'][4]=abs(amount)*(.10 if slug=='wasp' else .045)
  elif kind=='turn':v['root'][1]=amount*.9;v['head'][1]=amount*.23
  elif kind=='windup':
   v['body'][0]=-.22*amount;v['head'][0]=-.16*amount
   if slug=='sentry':v['arm_R'][0]=-1.4*amount;v['arm_L'][0]=-.40*amount
   elif slug=='skitter':
    v['body'][4]=-.16*amount
    for n in limbs:v[n][0]=.34*amount
   elif slug=='wasp':
    for n in limbs:v[n][1]=1.15*amount*(1 if n.endswith('L') else -1)
   else:v['head'][0]=-.57*amount
  elif kind in ('attack','special'):
   v['body'][0]=(.31 if slug!='wasp' else -.18)*amount
   v['body'][5]=(.32 if kind=='special' else .20)*amount
   if slug=='sentry':v['arm_R'][0]=1.6*amount;v['arm_R'][1]=-.63*amount
   elif slug=='skitter':
    v['body'][4]=.31*amount
    for n in limbs:v[n][0]=-.67*amount
   elif slug=='wasp':
    v['head'][5]=.13*amount
    for n in limbs:v[n][1]=-.55*amount*(1 if n.endswith('L') else -1)
   else:v['head'][0]=.61*amount
   if kind=='special':
    if slug=='sentry':v['arm_L'][0]=1.27*amount;v['body'][1]=.74*amount
    elif slug=='skitter':v['body'][4]=.61*amount;v['head'][0]=.44*amount
    elif slug=='wasp':
     v['body'][4]=.28*amount
     for n in limbs:v[n][1]=1.38*amount*(1 if n.endswith('L') else -1)
    else:v['head'][0]=.96*amount;v['body'][0]=-.26*amount
  elif kind=='recover':v['body'][0]=.16*amount;v['head'][0]=.14*amount
  elif kind=='hit':v['body'][2]=.40*amount;v['head'][0]=-.29*amount
  elif kind=='defeat':
   v['body'][2]=1.43*amount;v['body'][4]=-(1 if slug=='sentry' else .95 if slug=='wasp' else .30)*amount
   v['head'][0]=.38*amount
   for j,n in enumerate(limbs):v[n][0]=amount*(.70 if j%2 else -.56)
  return v
 actions=[
 ('Idle','idle',[(1,0,0),(13,1,0),(25,0,0),(37,-1,0),(49,0,0)]),
 ('Move','move',[(1,0,0),(7,1,.5),(13,0,1),(19,-1,1.5),(25,0,2)]),
 ('Turn','turn',[(1,0,0),(11,1,0),(21,0,0)]),
 ('Windup','windup',[(1,0,0),(10,.35,0),(18,1,0),(24,1,0)]),
 ('Attack','attack',[(1,0,0),(9,1,0),(14,.68,0),(24,0,0)]),
 ('Recover','recover',[(1,1,0),(10,.52,0),(22,0,0)]),
 ('Hit','hit',[(1,0,0),(4,1,0),(13,0,0)]),
 ('Special','special',[(1,0,0),(13,.35,0),(19,1,0),(29,0,0)]),
 ('Defeat','defeat',[(1,0,0),(9,.32,0),(21,.9,0),(32,1,0)]),
 ]
 for name,kind,keys in actions:
  for frame,a,k in keys:
   for n,v in pose(kind,a,k).items():
    q=rig.pose.bones[n];q.rotation_euler=v[:3];q.location=v[3:]
    for prop in ('rotation_euler','location'):q.keyframe_insert(data_path=prop,frame=frame,group=n)
  action=rig.animation_data.action;action.name=label+' '+name;rig.animation_data.action=None
  track=rig.animation_data.nla_tracks.new();track.name=name;track.strips.new(name,1,action)
 bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animation_mode='NLA_TRACKS')
 for t in rig.animation_data.nla_tracks:t.mute=True
 for o in c.objects:
  if o.type=='EMPTY':o.name=label+' | '+o.name
 for q in rig.pose.bones:q.rotation_euler=(0,0,0);q.location=(0,0,0)
 s.frame_set(1);rig.location.x=(i-1.5)*2.10
 text=bpy.data.curves.new(label,'FONT');text.body=label;text.align_x='CENTER';text.size=.13;text.materials.append(labels)
 o=bpy.data.objects.new(label+' label',text);s.collection.objects.link(o);o.location=(rig.location.x,-.8,.02);o.rotation_euler.x=math.radians(68)
bpy.ops.mesh.primitive_plane_add(size=24);bpy.context.object.data.materials.append(dark)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,E,col,size in [('Key',(-4,-6,6),1600,(.63,.86,1),5),('Rim',(4,1,4),1300,(1,.42,.17),3)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=E;d.color=col;d.size=size
 o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=p;aim(o,(0,0,.8))
world=bpy.data.worlds.new('Night shop');s.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
d=bpy.data.cameras.new('Lineup');o=bpy.data.objects.new('Lineup',d);s.collection.objects.link(o);s.camera=o
o.location=(0,-9,4.5);aim(o,(0,0,.80));d.type='ORTHO';d.ortho_scale=9.0
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.resolution_x=1260;s.render.resolution_y=680
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(TMP/'dock-enemies.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'dock-enemies.blend'),compress=True)
bpy.ops.render.render(write_still=True)

# Render an isolated studio portrait of the updated Ram from the same source.
for slug,label,_,_ in spec:
 if slug!='ram':bpy.data.collections[label].hide_render=True
 bpy.data.objects[label+' label'].hide_render=True
focus=(3.15,0,.57);o.location=(5.4,-5.3,2.65);aim(o,focus);d.ortho_scale=2.6
s.render.resolution_x=800;s.render.resolution_y=660
s.render.filepath=str(TMP/'ballast-ram.png');bpy.ops.render.render(write_still=True)

bpy.data.collections['Ballast Ram'].hide_render=True
bpy.data.collections['Gate Sentry'].hide_render=False
focus=(-3.15,0,1.05);o.location=(-6.0,-5.6,3.10);aim(o,focus);d.ortho_scale=3.05
s.render.filepath=str(TMP/'gate-sentry.png');bpy.ops.render.render(write_still=True)
