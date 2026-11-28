"""Four original foundry enemy rigs. World forward -Y, ground +Z."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'art/actors/dock-foundry'
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

spec=[('recycler','Bellows Recycler',(.27,.42,.20),'vacuum'),
      ('stilt','Tidehook Stilt',(.16,.48,.55),'stilt'),('relay','Lantern Relay',(.53,.36,.13),'relay'),
      ('winch','Indigo Winch',(.26,.23,.48),'recoil')]
for i,(slug,label,tint,motif) in enumerate(spec,13):
 c=bpy.data.collections.new(label);S.collection.children.link(c)
 paint=mat(label+' enamel',tint,.52,.36);defs={};groups={}
 def joint(n,p,par='body'):defs[n]=(p,par)
 def attach(n,*o):groups.setdefault(n,[]).extend(o)
 joint('root',(0,0,0),None)
 if motif=='vacuum':
  joint('body',(0,.04,.60),'root');joint('intake',(0,-.43,.85));joint('bellows',(0,-.14,.85),'intake')
  attach('body',box(c,'Cast recycler carriage',(0,.14,.52),(1.04,1.14,.54),paint,b=.10),
   cyl(c,'Vertical inspection tower',(0,.33,1.10),.29,.72,steel,v=8),
   box(c,'Pressure safe mark',(0,.073,1.28),(.22,.042,.11),glow,b=.02))
  for q in (-1,1):
   attach('body',box(c,'Tracked skid',(q*.59,.08,.24),(.29,1.35,.30),rubber,b=.08),
    cyl(c,'Track shaft',(q*.75,.18,.23),.103,.03,bright,'X'))
  attach('intake',cyl(c,'Brass intake flare',(0,-.68,.86),.37,.37,copper,'Y',12),
   cyl(c,'Intake dark throat',(0,-.876,.86),.302,.03,rubber,'Y',12))
  for q in (-1,0,1):
   attach('intake',box(c,'Intake rib',(q*.108,-.901,.86),(.029,.044,.46 if not q else .39),bright,b=.014))
  for y in (-.18,-.27,-.36,-.45):
   attach('bellows',cyl(c,'Bellows rotating convolution',(0,y,.86),.265,.075,steel,'Y',14))
  sockets={'weak':((0,.039,1.28),'body'),'attack':((0,-.92,.86),'intake')}
 elif motif=='stilt':
  joint('body',(0,0,1.66),'root');joint('scythe_L',(-.35,-.09,1.81));joint('scythe_R',(.35,-.09,1.81))
  attach('body',orb(c,'Pointed central shell',(0,0,1.87),(.48,.40,.32),paint),
   cyl(c,'Forward sight',(0,-.34,1.86),.185,.2,steel,'Y',12),
   cyl(c,'Sight core',(0,-.452,1.86),.12,.03,glow,'Y',8))
  for q,k in [(-1,'L'),(1,'R')]:
   ankle=(q*.57,.16,.14)
   joint('leg_'+k,(q*.25,.18,1.67))
   attach('leg_'+k,rod(c,'Inverted femur',(q*.25,.16,1.64),(q*.55,.35,.88),.088,bright),
    rod(c,'Slender tendon',(q*.55,.35,.88),ankle,.069,steel),
    box(c,'Tapered landing shoe',(q*.57,.06,.13),(.24,.47,.23),rubber,b=.053))
   attach('scythe_'+k,rod(c,'High sweep arm',(q*.37,-.10,1.85),(q*.74,-.34,1.59),.074,steel),
    rod(c,'Curved forged prong',(q*.74,-.34,1.59),(q*.88,-.62,.95),.077,copper),
    box(c,'Forged edge',(q*.88,-.676,1.0),(.10,.16,.59),bright,b=.043),
    box(c,'Edge tell',(q*.88,-.763,1.07),(.061,.014,.30),warm,b=.007))
  sockets={'weak':((0,-.477,1.86),'body'),'attack':((-.88,-.78,1.00),'scythe_L')}
 elif motif=='relay':
  joint('body',(0,0,1.17),'root');joint('orbit',(0,0,1.34));joint('lamp_L',(-.72,0,1.28),'orbit');joint('lamp_R',(.72,0,1.28),'orbit')
  attach('body',cyl(c,'Inverted cup',(0,0,1.16),.37,.51,steel,v=8),
   cyl(c,'Hover emitter',(0,0,.88),.245,.058,glow,v=12),
   box(c,'Central golden eye',(0,-.364,1.21),(.24,.044,.14),warm,b=.033))
  ring=cyl(c,'Central spindle',(0,0,1.47),.16,.24,copper)
  attach('orbit',ring)
  for q,k in [(-1,'L'),(1,'R')]:
   attach('orbit',rod(c,'Curved boom spar',(0,0,1.47),(q*.63,0,1.53),.041,bright))
   attach('lamp_'+k,cyl(c,'Pylon lid',(q*.65,0,1.54),.195,.10,copper,v=6),
    orb(c,'Separate lantern housing',(q*.65,0,1.29),(.20,.20,.27),paint),
    cyl(c,'Downward light',(q*.65,0,1.07),.12,.032,glow,v=8))
   for y in (-.154,.154):
    attach('lamp_'+k,rod(c,'External lantern cage',(q*.65,y,1.49),(q*.65,y*.65,1.11),.021,steel))
  sockets={'weak':((0,-.397,1.21),'body'),'attack':((.65,0,1.05),'lamp_R')}
 else:
  joint('body',(0,0,.49),'root');joint('flywheel',(0,.08,1.00));joint('exhaust',(0,-.34,.46))
  attach('body',box(c,'Low wide base',(0,0,.41),(1.18,.85,.47),paint,b=.08),
   box(c,'Flywheel bracket',(-.42,.08,.97),(.20,.54,1.20),steel,b=.06),
   box(c,'Flywheel bracket',(.42,.08,.97),(.20,.54,1.20),steel,b=.06),
   box(c,'Voltage stripe',(-.42,-.207,1.24),(.14,.054,.25),warm,b=.022))
  for q in (-1,1):
   for y in (-.30,.30):
    attach('body',cyl(c,'Grip roller',(q*.55,y,.23),.21,.24,rubber,'X',12))
  attach('flywheel',cyl(c,'Indiana shear wheel',(0,.07,1.05),.47,.44,paint,'X',16),
   cyl(c,'Brass rim',(0,.07,1.05),.49,.11,copper,'X',16))
  for j in range(8):
   a=j*math.tau/8
   attach('flywheel',box(c,'Rim tooth',(0,.07+.49*math.cos(a),1.05+.49*math.sin(a)),(.24,.125,.123),bright,b=.022))
  for x in (-.29,.29):
   attach('exhaust',cyl(c,'Reverse recoil nozzle',(x,-.49,.48),.15,.3,steel,'Y',8),
    cyl(c,'Jet contact',(x,-.65,.48),.093,.03,glow,'Y',8))
  sockets={'weak':((-.42,-.24,1.24),'body'),'attack':((0,-.68,.47),'exhaust')}
 a=bpy.data.armatures.new(label+' rig');rig=bpy.data.objects.new(f'WSC-ENM-{i:03d} '+label,a);c.objects.link(rig)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.object.mode_set(mode='EDIT')
 for name,(p,par) in defs.items():
  b=a.edit_bones.new(name);b.head=p;b.tail=(p[0],p[1],p[2]+.135)
  if par:b.parent=a.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT')
 def bind(o,b):
  w=o.matrix_world.copy();o.parent=rig;o.parent_type='BONE';o.parent_bone=b
  bpy.context.view_layer.update();o.matrix_world=w
 for name,objects in groups.items():
  for o in objects:bind(o,name)
 for name,(p,parent) in {**sockets,'ground':((0,0,0),'root')}.items():
  o=bpy.data.objects.new(name+'_socket',None);o.location=p;c.objects.link(o);bpy.context.view_layer.update();bind(o,parent)
 for b in rig.pose.bones:b.rotation_mode='XYZ'
 sig={'vacuum':('intake','bellows'),'stilt':('scythe_L','scythe_R'),'relay':('orbit','lamp_R'),'recoil':('flywheel','exhaust')}[motif]
 def pose(kind,strength):
  f={k:[0.,0.,0.,0.,0.,0.] for k in defs};x=strength;P,Q=sig
  if kind=='idle':f['body'][4]=x*(.10 if motif=='relay' else .021);f[Q][2]=x*.09
  if kind=='move':
   if motif=='stilt':f['leg_L'][0]=x*.55;f['leg_R'][0]=-x*.55
   elif motif=='relay':f[P][1]=x*.61;f['lamp_L'][4]=x*.18;f[Q][4]=-x*.18
   elif motif=='recoil':f[P][0]=x*1.08;f['body'][0]=x*.086
   else:f[P][0]=x*.13;f[Q][5]=x*.082
  if kind=='turn':f['root'][1]=x*.88;f[P][1]=x*.18
  if kind=='windup':
   if motif=='vacuum':f[P][5]=x*.21;f[Q][5]=x*.14
   if motif=='stilt':f[P][1]=x*.75;f[Q][1]=-x*.75
   if motif=='relay':f[P][1]=x*1.14;f[Q][4]=-x*.38;f['lamp_L'][4]=-x*.37
   if motif=='recoil':f[P][0]=x*1.76;f[Q][0]=-x*.14
  if kind in ('attack','special'):
   k=1.47 if kind=='special' else 1
   if motif=='vacuum':f[P][5]=-x*.26*k;f[Q][5]=-x*.14*k;f['body'][0]=x*.22*k
   elif motif=='stilt':f[P][1]=-x*1.32*k;f[Q][1]=x*.87*k;f['body'][0]=x*.24*k
   elif motif=='relay':f[P][1]=-x*2.38*k;f[Q][4]=-x*.39*k;f['lamp_L'][4]=-x*.43*k
   else:f[P][0]=-x*2.50*k;f[Q][5]=x*.23*k;f['body'][0]=x*.40*k
  if kind=='recover':f[P][0]=x*.21;f[Q][2]=-x*.16
  if kind=='hit':f['body'][2]=x*.35;f[P][0]=x*.23
  if kind=='defeat':f['body'][2]=x*1.34;f['body'][4]=-x*(.81 if motif=='relay' else .42);f[Q][0]=x*.43
  return f
 for title,role,frames in [
  ('Idle','idle',[(1,0),(13,1),(25,0),(37,-1),(49,0)]),('Move','move',[(1,0),(7,1),(13,0),(19,-1),(25,0)]),
  ('Turn','turn',[(1,0),(12,1),(23,0)]),('Windup','windup',[(1,0),(11,.60),(24,1)]),
  ('Attack','attack',[(1,0),(9,1),(21,0)]),('Special','special',[(1,0),(11,.45),(18,1),(34,0)]),
  ('Recover','recover',[(1,1),(18,0)]),('Hit','hit',[(1,0),(4,1),(14,0)]),
  ('Defeat','defeat',[(1,0),(10,.40),(25,1),(35,1)])]:
  for frame,x in frames:
   for b,v in pose(role,x).items():
    q=rig.pose.bones[b];q.rotation_euler=v[:3];q.location=v[3:]
    for k in ['rotation_euler','location']:q.keyframe_insert(data_path=k,frame=frame,group=b)
  act=rig.animation_data.action;act.name=label+' '+title;rig.animation_data.action=None
  t=rig.animation_data.nla_tracks.new();t.name=title;t.strips.new(title,1,act)
 bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(D/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animation_mode='NLA_TRACKS')
 for tr in rig.animation_data.nla_tracks:tr.mute=True
 for o in c.objects:
  if o.type=='EMPTY':o.name=label+' '+o.name
 for q in rig.pose.bones:q.rotation_euler=(0,0,0);q.location=(0,0,0)
 S.frame_set(1);rig.location.x=(i-14.5)*2.38
 font=bpy.data.curves.new(label,'FONT');font.body=label;font.size=.13;font.align_x='CENTER';font.materials.append(words)
 q=bpy.data.objects.new(label+' placard',font);S.collection.objects.link(q);q.location=(rig.location.x,-.94,.006);q.rotation_euler.x=math.radians(68)
bpy.ops.mesh.primitive_plane_add(size=72);bpy.context.object.data.materials.append(mat('Display stone',(.023,.048,.056),.12,.53))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,energy,col,z in [('Cyan key',(-4,-6,6),1600,(.65,.86,1),5),('Forge rim',(4,2,4),1450,(1,.49,.23),3)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.color=col;l.size=z
 o=bpy.data.objects.new(n,l);S.collection.objects.link(o);o.location=p;aim(o,(0,0,.8))
w=bpy.data.worlds.new('Slate sky');S.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
a=bpy.data.cameras.new('Roster plate');cam=bpy.data.objects.new('Roster plate',a);S.collection.objects.link(cam);S.camera=cam
cam.location=(-3.8,-10.8,4.40);aim(cam,(0,0,.89));a.type='ORTHO';a.ortho_scale=10.42
S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=False
S.render.resolution_x=1260;S.render.resolution_y=680;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(TMP/'dock-foundry.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'dock-foundry.blend'),compress=True)
bpy.ops.render.render(write_still=True)
