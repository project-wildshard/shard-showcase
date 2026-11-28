"""Four original specialist enemy rigs. World forward -Y, ground +Z."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'art/actors/dock-specialists'
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

spec=[('hook','Hook Crane',(.63,.34,.082),'hook'),('kiln','Kiln Warden',(.58,.18,.07),'guard'),
      ('snare','Breakwater Snare',(.12,.43,.42),'burrow'),('buoy','Spark Buoy',(.34,.23,.49),'burst')]
for i,(slug,label,tint,motif) in enumerate(spec,5):
 c=bpy.data.collections.new(label);S.collection.children.link(c)
 paint=mat(label+' baked enamel',tint,.44,.36);defs={};groups={}
 def joint(n,p,par='body'):defs[n]=(p,par)
 def attach(n,*o):groups.setdefault(n,[]).extend(o)
 joint('root',(0,0,0),None)
 if motif=='hook':
  joint('body',(0,0,.37),'root');joint('arm',(0,.12,1.64));joint('chain',(0,-.61,2.04),'arm')
  attach('body',box(c,'Track deck',(0,0,.39),(1.18,.94,.30),steel),
         box(c,'Upper tower',(0,.16,1.18),(.52,.55,1.59),paint,b=.075),
         box(c,'Amber switch',(0,-.136,1.00),(.31,.032,.17),warm,b=.018))
  for sign in (-1,1):
   x=sign*.52
   attach('body',box(c,'Raillink track',(x,0,.22),(.31,1.19,.43),rubber,b=.10))
   for y in (-.37,0,.37):attach('body',cyl(c,'Track pin',(sign*.69,y,.22),.115,.034,copper,'X'))
  attach('arm',rod(c,'Hoist boom',(0,.13,1.67),(0,-.64,2.12),.103,bright),
         box(c,'Drive motor',(0,.12,1.82),(.51,.37,.31),paint))
  attach('chain',rod(c,'Rigid magnetic leader',(0,-.63,2.10),(0,-.65,1.26),.044,steel),
          orb(c,'Magnetic head',(0,-.66,1.17),(.20,.17,.17),copper),cyl(c,'Hook force lip',(0,-.67,1.04),.19,.10,glow))
  sockets={'weak':((0,-.15,1),'body'),'attack':((0,-.67,1.0),'chain')}
 elif motif=='guard':
  joint('body',(0,0,.93),'root');joint('shield',(0,-.34,1.02));joint('boot_L',(-.25,0,.69));joint('boot_R',(.25,0,.69))
  attach('body',box(c,'Kiln body',(0,.04,1.28),(.84,.64,.66),steel,b=.095),
         box(c,'Hot aperture',(0,-.288,1.32),(.48,.034,.29),warm,b=.04),
         box(c,'Cradle',(0,.07,.89),(.66,.47,.19),paint))
  attach('shield',box(c,'Cast shield',(0,-.46,1.18),(1.06,.19,1.22),paint,b=.105),
         box(c,'Shield rib',(0,-.574,1.18),(.22,.065,1.03),bright,b=.032))
  for x in (-.38,.38):
   for z in (.80,1.55):attach('shield',cyl(c,'Hot fastener',(x,-.56,z),.064,.038,copper,'Y'))
  for x,n in [(-.246,'boot_L'),(.246,'boot_R')]:
   attach(n,rod(c,'Weight strut',(x,0,.74),(x,0,.24),.109,bright),
    box(c,'Forged sneaker',(x,-.13,.19),(.36,.54,.29),rubber,b=.061))
  sockets={'weak':((0,-.32,1.32),'body'),'attack':((0,-.62,1.12),'shield')}
 elif motif=='burrow':
  joint('body',(0,.06,.37),'root');joint('nose',(0,-.46,.30));joint('tail',(0,.49,.30));joint('blade_L',(-.33,-.53,.33),'nose');joint('blade_R',(.33,-.53,.33),'nose')
  for y,r,n in [(-.37,.45,'nose'),(0,.40,'body'),(.39,.36,'tail'),(.76,.26,'tail')]:
   attach(n,orb(c,'Segmented shell',(0,y,.36),(r,.31,.32),paint),
          box(c,'Straked plate',(0,y,.67),(r*.68,.31,.14),bright,b=.035))
  attach('nose',box(c,'Sensor grille',(0,-.676,.33),(.55,.12,.25),steel,b=.053),
         box(c,'Sensor scan',(0,-.75,.36),(.32,.038,.085),glow,b=.012))
  for x,n in [(-.43,'blade_L'),(.43,'blade_R')]:
   attach(n,box(c,'Outboard cutter',(x,-.57,.26),(.18,.59,.12),copper,b=.034,rotation=x*.9))
  sockets={'weak':((0,-.77,.36),'nose'),'attack':((0,-.85,.24),'nose')}
 else:
  joint('body',(0,0,1.14),'root');joint('cage',(0,0,1.23));joint('fin_L',(-.39,0,1.26));joint('fin_R',(.39,0,1.26))
  attach('body',orb(c,'Warning buoy',(0,0,1.25),(.38,.38,.51),paint),
     cyl(c,'Lower collar',(0,0,.80),.26,.19,copper),
     cyl(c,'Jet aperture',(0,0,.681),.172,.044,glow),
     cyl(c,'Charge eye',(0,-.334,1.22),.183,.15,steel,'Y'),
     cyl(c,'Charge eye emitter',(0,-.428,1.22),.121,.028,warm,'Y'))
  for j in range(8):
   a=j*math.tau/8;x,y=math.cos(a)*.30,math.sin(a)*.30
   attach('cage',rod(c,'Cage rod',(x,y,.83),(x*1.43,y*1.43,1.54),.033,bright))
  for sign,n in [(-1,'fin_L'),(1,'fin_R')]:
   attach(n,box(c,'Pivot antenna',(sign*.45,0,1.19),(.37,.13,.34),paint,b=.038),
       box(c,'Antenna indicator',(sign*.55,-.075,1.21),(.17,.032,.06),glow,b=.012))
  sockets={'weak':((0,-.445,1.22),'body'),'attack':((0,-.45,1.2),'body')}
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
 sig={'hook':('arm','chain'),'guard':('shield','boot_R'),'burrow':('nose','tail'),'burst':('cage','fin_R')}[motif]
 def pose(kind,strength):
  f={k:[0.,0.,0.,0.,0.,0.] for k in defs};x=strength;P,Q=sig
  if kind=='idle':
   f['body'][4]=x*(.10 if motif=='burst' else .028);f[Q][2]=x*.08
  if kind=='move':
   if motif=='guard':f['boot_R'][0]=x*.52;f['boot_L'][0]=-x*.52
   elif motif=='burrow':f['nose'][1]=x*.25;f['tail'][1]=-x*.38
   elif motif=='burst':f['body'][4]=x*.16;f['fin_L'][2]=x*.48;f['fin_R'][2]=-x*.48
   else:f['arm'][0]=x*.06;f['chain'][0]=x*.19
  if kind=='turn':
   f['root'][1]=x*.88;f[P][1]=x*.19
  if kind=='windup':
   if motif=='hook':f['arm'][0]=-x*.60;f['chain'][2]=x*1.02
   elif motif=='guard':f['shield'][1]=-x*.92;f['body'][0]=-x*.18
   elif motif=='burrow':f['body'][4]=-x*.23;f['tail'][0]=-x*.40
   else:f['cage'][1]=x*1.61;f['fin_L'][2]=x*1.18;f['fin_R'][2]=-x*1.18
  if kind in ('attack','special'):
   bonus=1.55 if kind=='special' else 1
   if motif=='hook':f['chain'][2]=-x*.95*bonus;f['arm'][0]=x*.48*bonus
   elif motif=='guard':f['shield'][5]=x*.32*bonus;f['body'][0]=x*.27*bonus
   elif motif=='burrow':f['nose'][4]=x*.38*bonus;f['blade_L'][1]=x*.61*bonus;f['blade_R'][1]=-x*.61*bonus
   else:f['cage'][1]=-x*1.65*bonus;f['body'][4]=x*.24*bonus;f['fin_R'][2]=x*bonus
  if kind=='recover':f[P][0]=x*.23;f[Q][2]=-x*.17
  if kind=='hit':f['body'][2]=x*.34;f[P][0]=-x*.35
  if kind=='defeat':
   f['body'][2]=x*(1.15 if motif=='hook' else 1.38);f['body'][4]=-x*(.84 if motif=='burst' else .39)
   f[P][0]=x*.54;f[Q][2]=-x*.61
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
 S.frame_set(1);rig.location.x=(i-6.5)*2.08
 font=bpy.data.curves.new(label,'FONT');font.body=label;font.size=.13;font.align_x='CENTER';font.materials.append(words)
 q=bpy.data.objects.new(label+' placard',font);S.collection.objects.link(q);q.location=(rig.location.x,-.94,.006);q.rotation_euler.x=math.radians(68)
bpy.ops.mesh.primitive_plane_add(size=24);bpy.context.object.data.materials.append(mat('Display stone',(.023,.048,.056),.12,.53))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,energy,col,z in [('Cyan key',(-4,-6,6),1600,(.65,.86,1),5),('Forge rim',(4,2,4),1450,(1,.49,.23),3)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.color=col;l.size=z
 o=bpy.data.objects.new(n,l);S.collection.objects.link(o);o.location=p;aim(o,(0,0,.8))
w=bpy.data.worlds.new('Slate sky');S.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
a=bpy.data.cameras.new('Roster plate');cam=bpy.data.objects.new('Roster plate',a);S.collection.objects.link(cam);S.camera=cam
cam.location=(0,-9.5,4.55);aim(cam,(0,0,.89));a.type='ORTHO';a.ortho_scale=9.1
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=False
S.render.resolution_x=1260;S.render.resolution_y=680;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(TMP/'dock-specialists.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'dock-specialists.blend'),compress=True)
bpy.ops.render.render(write_still=True)
