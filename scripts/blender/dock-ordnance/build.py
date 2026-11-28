"""Four original ordnance enemy rigs. World forward -Y, ground +Z."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'art/actors/dock-ordnance'
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

spec=[('rasp','Rasp Turret',(.12,.39,.47),'salvo'),('railblade','Railblade Inspector',(.56,.18,.095),'lunge'),
      ('mortar','Salt Mortar',(.41,.43,.19),'mortar'),('spool','Turnstile Spool',(.37,.21,.48),'crosscut')]
for i,(slug,label,tint,motif) in enumerate(spec,9):
 c=bpy.data.collections.new(label);S.collection.children.link(c)
 paint=mat(label+' baked enamel',tint,.44,.36);defs={};groups={}
 def joint(n,p,par='body'):defs[n]=(p,par)
 def attach(n,*o):groups.setdefault(n,[]).extend(o)
 joint('root',(0,0,0),None)
 if motif=='salvo':
  joint('body',(0,0,.49),'root');joint('barrel',(0,-.10,1.31));joint('drum',(0,.02,1.19),'barrel')
  attach('body',cyl(c,'Three-point pedestal',(0,0,.21),.52,.38,steel,v=6),
   cyl(c,'Slewing collar',(0,0,.52),.31,.31,copper),cyl(c,'Elevator yoke',(0,.08,.78),.14,.36,steel),box(c,'Angular gun pod',(0,.08,1.16),(.69,.65,.59),paint,b=.10),
   box(c,'Range lens',(0,-.271,1.38),(.33,.04,.095),glow,b=.018))
  for q in range(3):
   angle=math.tau*q/3
   attach('body',box(c,'Outrigger',(math.sin(angle)*.44,math.cos(angle)*.44,.13),(.25,.62,.23),rubber,rotation=-angle))
  for x in (-.18,0,.18):
   attach('barrel',cyl(c,'Pulse tube',(x,-.44,1.20),.081,.65,bright,'Y',10),
    cyl(c,'Pulse aperture',(x,-.78,1.20),.056,.035,warm,'Y',10))
  attach('drum',cyl(c,'External ratchet drum',(.34,.10,1.16),.26,.35,copper,'X'))
  sockets={'weak':((0,-.30,1.38),'body'),'attack':((0,-.80,1.20),'barrel')}
 elif motif=='lunge':
  joint('body',(0,0,.95),'root');joint('blade',(.43,-.06,1.47));joint('visor',(0,-.17,1.79))
  for x,key in [(-.26,'leg_L'),(.26,'leg_R')]:
   joint(key,(x,0,.98));attach(key,rod(c,'Hock strut',(x,0,1.00),(x,.17,.51),.087,bright),
    rod(c,'Shin',(x,.17,.53),(x,-.10,.17),.105,steel),
    box(c,'Rail shoe',(x,-.17,.14),(.26,.60,.22),rubber,b=.045))
  attach('body',box(c,'Tall armored jacket',(0,.02,1.34),(.65,.47,.69),paint,b=.10),
    box(c,'Counter-arm',(-.46,.05,1.26),(.23,.29,.65),steel,b=.055))
  attach('visor',orb(c,'Inspector helmet',(0,0,1.88),(.32,.24,.31),steel),
    box(c,'Red slit',(0,-.235,1.88),(.36,.037,.091),warm,b=.015))
  attach('blade',rod(c,'Outstretched elbow',(.44,-.02,1.54),(.52,-.28,1.18),.12,steel),
    box(c,'Railblade edge',(.52,-.53,1.16),(.12,1.19,.24),bright,b=.055),
    box(c,'Heat seam',(.523,-.55,1.29),(.064,.95,.044),warm,b=.012))
  sockets={'weak':((0,-.27,1.88),'visor'),'attack':((.52,-1.13,1.15),'blade')}
 elif motif=='mortar':
  joint('body',(0,0,.49),'root');joint('tube',(0,-.06,1.00));joint('hatch',(0,.32,.77))
  attach('body',box(c,'Split wheeled crab frame',(0,.07,.35),(1.10,.98,.44),paint,b=.105),
    box(c,'Fire computer',(0,-.49,.49),(.48,.19,.28),steel,b=.041),
    box(c,'Counterweight lamp',(0,-.60,.49),(.31,.04,.066),glow,b=.013))
  for x in (-.56,.56):
   for y in (-.29,.32):attach('body',cyl(c,'Oversized wheel',(x,y,.27),.27,.22,rubber,'X',14),
    cyl(c,'Six-lug hub',(x+math.copysign(.126,x),y,.27),.13,.04,copper,'X',6))
  attach('tube',rod(c,'Tilted launcher',(0,.23,.77),(0,-.40,1.64),.205,steel),
    rod(c,'Hot muzzle',(0,-.37,1.59),(0,-.47,1.72),.228,copper),
    rod(c,'Ignition plane',(0,-.468,1.717),(0,-.486,1.743),.169,warm))
  attach('hatch',box(c,'Ammunition rack',(0,.35,.77),(.65,.39,.23),paint,b=.045))
  for x in (-.19,0,.19):attach('hatch',cyl(c,'Shell casing',(x,.36,.948),.07,.20,bright))
  sockets={'weak':((0,-.63,.49),'body'),'attack':((0,-.49,1.75),'tube')}
 else:
  joint('body',(0,0,.81),'root');joint('reel',(0,0,.97));joint('arm_L',(-.51,0,.97),'reel');joint('arm_R',(.51,0,.97),'reel')
  attach('body',cyl(c,'Turnstile base',(0,0,.20),.42,.31,steel,v=8),
    cyl(c,'Tall column',(0,0,.58),.20,.73,paint),orb(c,'Head drum',(0,0,1.34),(.37,.33,.31),paint),
    box(c,'Status slot',(0,-.32,1.37),(.36,.055,.093),glow,b=.015))
  attach('reel',cyl(c,'Grooved outer reel',(0,0,.95),.36,.29,copper,v=20))
  for q,n in [(-1,'arm_L'),(1,'arm_R')]:
   attach(n,rod(c,'Barrier spindle',(q*.27,0,.97),(q*1.03,0,.97),.065,bright),
    box(c,'Paddle counterweight',(q*.94,0,.97),(.34,.28,.23),paint,b=.050),
    box(c,'Paddle warning strip',(q*.95,-.151,.97),(.24,.024,.07),warm,b=.015))
  sockets={'weak':((0,-.36,1.37),'body'),'attack':((.98,0,.97),'arm_R')}
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
 sig={'salvo':('barrel','drum'),'lunge':('blade','visor'),'mortar':('tube','hatch'),'crosscut':('reel','arm_R')}[motif]
 def pose(kind,strength):
  f={k:[0.,0.,0.,0.,0.,0.] for k in defs};x=strength;P,Q=sig
  if kind=='idle':f['body'][4]=x*.027;f[Q][2]=x*.09
  if kind=='move':
   if motif=='lunge':f['leg_L'][0]=x*.56;f['leg_R'][0]=-x*.56
   else:f['body'][0]=x*.084;f[P][1]=x*.14
  if kind=='turn':f['root'][1]=x*.83;f[P][1]=x*.15
  if kind=='windup':
   f[P][0]=x*({'salvo':-.15,'lunge':-.68,'mortar':-.67,'crosscut':.08}[motif])
   f[Q][2]=x*.21
   if motif=='crosscut':f[P][1]=x*.89;f['arm_L'][0]=x*.44
  if kind in ('attack','special'):
   k=1.58 if kind=='special' else 1
   if motif=='salvo':f[P][5]=-x*.24*k;f[Q][0]=x*1.15*k
   elif motif=='lunge':f[P][0]=x*.88*k;f[P][5]=x*.46*k;f['body'][0]=x*.38*k
   elif motif=='mortar':f[P][0]=x*.48*k;f['body'][4]=-x*.13*k;f[Q][0]=x*.38*k
   else:f[P][1]=-x*1.90*k;f['arm_L'][2]=x*.58*k;f[Q][2]=-x*.58*k
  if kind=='recover':f[P][0]=x*.24;f[Q][2]=-x*.18
  if kind=='hit':f['body'][2]=x*.35;f[P][0]=x*.27
  if kind=='defeat':
   f['body'][2]=x*(1.31 if motif=='lunge' else .97);f['body'][4]=-x*.41;f[P][0]=x*.58
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
 S.frame_set(1);rig.location.x=(i-10.5)*2.30
 font=bpy.data.curves.new(label,'FONT');font.body=label;font.size=.13;font.align_x='CENTER';font.materials.append(words)
 q=bpy.data.objects.new(label+' placard',font);S.collection.objects.link(q);q.location=(rig.location.x,-.94,.006);q.rotation_euler.x=math.radians(68)
bpy.ops.mesh.primitive_plane_add(size=24);bpy.context.object.data.materials.append(mat('Display stone',(.023,.048,.056),.12,.53))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,energy,col,z in [('Cyan key',(-4,-6,6),1600,(.65,.86,1),5),('Forge rim',(4,2,4),1450,(1,.49,.23),3)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.color=col;l.size=z
 o=bpy.data.objects.new(n,l);S.collection.objects.link(o);o.location=p;aim(o,(0,0,.8))
w=bpy.data.worlds.new('Slate sky');S.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
a=bpy.data.cameras.new('Roster plate');cam=bpy.data.objects.new('Roster plate',a);S.collection.objects.link(cam);S.camera=cam
cam.location=(-3.8,-10.8,4.40);aim(cam,(0,0,.89));a.type='ORTHO';a.ortho_scale=10.15
S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=False
S.render.resolution_x=1260;S.render.resolution_y=680;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(TMP/'dock-ordnance.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'dock-ordnance.blend'),compress=True)
bpy.ops.render.render(write_still=True)
