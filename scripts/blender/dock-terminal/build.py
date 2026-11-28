"""Four original terminal enemy rigs. World forward -Y, ground +Z."""
import bpy,math,sys
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'art/actors/dock-terminal'
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

spec=[('bailiff','Shutter Bailiff',(.19,.39,.45),'shutter'),
      ('seeder','Porcelain Seeder',(.48,.64,.59),'seed'),('harrow','Copper Harrow',(.54,.24,.096),'harrow'),
      ('keel','Keel Crab',(.26,.23,.43),'flank')]
for i,(slug,label,tint,motif) in enumerate(spec,17):
 c=bpy.data.collections.new(label);S.collection.children.link(c)
 paint=mat(label+' enamel',tint,.50,.37);defs={};groups={}
 def joint(n,p,par='body'):defs[n]=(p,par)
 def attach(n,*o):groups.setdefault(n,[]).extend(o)
 joint('root',(0,0,0),None)
 if motif=='shutter':
  joint('body',(0,0,.84),'root');joint('gate_L',(-.47,-.36,1.20));joint('gate_R',(.47,-.36,1.20));joint('punch',(0,-.28,1.14))
  attach('body',box(c,'Deep cast body',(0,.12,1.27),(1.10,.80,1.02),steel,b=.12),
   box(c,'Rear radiator',(0,.56,1.49),(.65,.19,.43),copper,b=.055),
   cyl(c,'Inner energy cell',(0,-.275,1.36),.242,.15,warm,'Y',12),
   box(c,'Undercarriage',(0,.03,.84),(.65,.56,.18),paint))
  for q,k in [(-1,'L'),(1,'R')]:
   joint('leg_'+k,(q*.28,.12,.82))
   attach('leg_'+k,rod(c,'Hydraulic leg',(q*.31,.11,.84),(q*.41,.10,.27),.137,bright),
    box(c,'Wide damped foot',(q*.42,-.05,.19),(.40,.70,.35),rubber,b=.073))
   attach('gate_'+k,box(c,'Heavy shutter leaf',(q*.258,-.439,1.26),(.508,.21,.84),paint,b=.065),
    rod(c,'External latch rib',(q*.14,-.574,1.59),(q*.38,-.574,.94),.041,bright))
  attach('punch',cyl(c,'Drawn piston',(0,-.37,1.13),.216,.23,bright,'Y',12),
    cyl(c,'Piston face',(0,-.50,1.13),.17,.052,glow,'Y',8))
  sockets={'weak':((0,-.353,1.36),'body'),'attack':((0,-.54,1.13),'punch')}
 elif motif=='seed':
  joint('body',(0,0,.70),'root');joint('hopper',(0,.11,1.32));joint('paddle',(0,-.45,.48))
  attach('body',cyl(c,'Inverted porcelain dome',(0,.12,.87),.52,.36,paint,v=10),
   box(c,'Pressure chassis',(0,.08,.54),(.81,1.02,.31),steel,b=.098),
   cyl(c,'Filter front',(0,-.49,.76),.162,.115,copper,'Y',10))
  for q,k in [(-1,'L'),(1,'R')]:
   joint('leg_'+k,(q*.37,.07,.68))
   for y in (-.38,.43):
    attach('leg_'+k,rod(c,'Curved spring arm',(q*.33,.11,.75),(q*.64,y,.31),.074,bright),
      box(c,'Rocker pad',(q*.64,y,.17),(.29,.47,.23),rubber,b=.066))
   attach('hopper',orb(c,'Ceramic seed pod',(q*.28,.16,1.28),(.224,.22,.37),paint),
    cyl(c,'Copper pod cap',(q*.28,.16,1.54),.162,.093,copper,v=10))
  attach('hopper',orb(c,'Lead pod',(0,-.22,1.26),(.188,.21,.37),paint),
   cyl(c,'Hot lead pod cap',(0,-.22,1.55),.137,.108,warm,v=8))
  attach('paddle',rod(c,'Seed slide',(0,-.43,.52),(0,-.77,.24),.129,bright),
   box(c,'Seed gate lip',(0,-.77,.24),(.39,.13,.08),glow,b=.018))
  sockets={'weak':((0,-.73,1.28),'hopper'),'attack':((0,-.79,.27),'paddle')}
 elif motif=='harrow':
  joint('body',(0,0,.96),'root');joint('iris',(0,0,1.31));joint('nozzle',(0,-.21,1.30),'iris')
  attach('body',cyl(c,'Hexalateral float',(0,0,1.54),.55,.24,paint,v=6),
   cyl(c,'Lower drive cap',(0,0,1.01),.328,.34,steel,v=12),
   cyl(c,'Hover annulus',(0,0,.81),.24,.075,glow),
   box(c,'Front rider plate',(0,-.48,1.55),(.40,.07,.13),bright,b=.025))
  for k in range(6):
   a=k*math.tau/6;x,y=math.sin(a),math.cos(a)
   attach('iris',rod(c,'Radial brass vane',(x*.22,y*.22,1.30),(x*.77,y*.77,1.39),.067,copper),
    box(c,'Vane point',(x*.68,y*.68,1.39),(.20,.28,.12),bright,b=.034,rotation=-a))
  attach('nozzle',cyl(c,'Directed sweep mouth',(0,-.47,1.30),.134,.36,steel,'Y',12),
   cyl(c,'Sweeping eye',(0,-.666,1.30),.095,.042,warm,'Y',12))
  sockets={'weak':((0,-.524,1.55),'body'),'attack':((0,-.70,1.30),'nozzle')}
 else:
  joint('body',(0,.08,.57),'root');joint('claw',(.54,-.09,.69));joint('hinge',(.76,-.56,.68),'claw')
  attach('body',orb(c,'Sloped shell',(0,.12,.71),(.67,.56,.39),paint),
    box(c,'Keel plate',(0,-.43,.61),(.40,.145,.23),copper,b=.051),
    box(c,'Aqua mask slit',(0,-.51,.65),(.29,.034,.069),glow,b=.012))
  for q,k in [(-1,'L'),(1,'R')]:
   joint('leg_'+k,(q*.42,.14,.68))
   for y in (-.24,.27,.64):
    attach('leg_'+k,rod(c,'Outer leg bollard',(q*.43,y,.66),(q*.77,y+.14,.55),.069,bright),
     rod(c,'Short angular knee',(q*.77,y+.14,.55),(q*.89,y-.03,.14),.060,steel),
     box(c,'Pointed pad',(q*.89,y-.03,.095),(.23,.32,.15),rubber,b=.043))
  attach('claw',rod(c,'Offset claw arm',(.52,-.10,.69),(.78,-.53,.71),.118,steel),
   orb(c,'Ram head',(.78,-.60,.73),(.35,.29,.20),paint))
  attach('hinge',rod(c,'Lower pincer',(.60,-.71,.75),(.43,-.93,.75),.072,copper),
   rod(c,'Upper pincer',(.95,-.70,.76),(1.03,-.94,.76),.073,bright),
   box(c,'Pincer tracer',(.74,-.834,.65),(.38,.062,.058),warm,b=.012))
  sockets={'weak':((0,-.538,.65),'body'),'attack':((.77,-.95,.74),'hinge')}
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
 sig={'shutter':('gate_L','gate_R'),'seed':('hopper','paddle'),'harrow':('iris','nozzle'),'flank':('claw','hinge')}[motif]
 def pose(kind,strength):
  f={k:[0.,0.,0.,0.,0.,0.] for k in defs};x=strength;P,Q=sig
  if kind=='idle':f['body'][4]=x*(.085 if motif=='harrow' else .024);f[Q][2]=x*.072
  if kind=='move':
   if motif=='harrow':f[P][1]=x*.84;f['body'][4]=x*.10
   else:f['leg_L'][0]=x*.55;f['leg_R'][0]=-x*.55
  if kind=='turn':f['root'][1]=x*.88;f[P][1]=x*.16
  if kind=='windup':
   if motif=='shutter':f[P][1]=-.98*x;f[Q][1]=.98*x;f['punch'][5]=.09*x
   if motif=='seed':f[P][0]=x*.36;f[Q][0]=x*.64
   if motif=='harrow':f[P][1]=x*.83;f[Q][0]=-x*.11
   if motif=='flank':f[P][1]=-x*.65;f[Q][1]=x*.57;f['body'][2]=x*.20
  if kind in ('attack','special'):
   k=1.55 if kind=='special' else 1
   if motif=='shutter':f[P][1]=-x;f[Q][1]=x;f['punch'][5]=x*.44*k
   elif motif=='seed':f[P][0]=-x*.47*k;f[Q][0]=-x*.76*k
   elif motif=='harrow':f[P][1]=-x*1.61*k;f['body'][4]=x*.13
   else:f[P][1]=x*1.14*k;f[Q][1]=-x*.81*k;f['body'][4]=x*.12
  if kind=='recover':
   if motif=='shutter':f[P][1]=-.98*x;f[Q][1]=.98*x
   else:f[P][0]=x*.21;f[Q][2]=-x*.18
  if kind=='hit':f['body'][2]=x*.35;f[P][0]=x*.23
  if kind=='defeat':f['body'][2]=x*1.36;f['body'][4]=-x*(.74 if motif=='harrow' else .41);f[Q][0]=x*.43
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
 S.frame_set(1);rig.location.x=(i-18.5)*2.45
 font=bpy.data.curves.new(label,'FONT');font.body=label;font.size=.13;font.align_x='CENTER';font.materials.append(words)
 q=bpy.data.objects.new(label+' placard',font);S.collection.objects.link(q);q.location=(rig.location.x,-.94,.006);q.rotation_euler.x=math.radians(68)
bpy.ops.mesh.primitive_plane_add(size=72);bpy.context.object.data.materials.append(mat('Display stone',(.023,.048,.056),.12,.53))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,p,energy,col,z in [('Cyan key',(-4,-6,6),1600,(.65,.86,1),5),('Forge rim',(4,2,4),1450,(1,.49,.23),3)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.color=col;l.size=z
 o=bpy.data.objects.new(n,l);S.collection.objects.link(o);o.location=p;aim(o,(0,0,.8))
w=bpy.data.worlds.new('Slate sky');S.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Strength'].default_value=.33
a=bpy.data.cameras.new('Roster plate');cam=bpy.data.objects.new('Roster plate',a);S.collection.objects.link(cam);S.camera=cam
cam.location=(-3.8,-10.8,4.40);aim(cam,(0,0,.89));a.type='ORTHO';a.ortho_scale=10.78
S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=False
S.render.resolution_x=1260;S.render.resolution_y=680;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.filepath=str(TMP/'dock-terminal.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'dock-terminal.blend'),compress=True)
bpy.ops.render.render(write_still=True)
