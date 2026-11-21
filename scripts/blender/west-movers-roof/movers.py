import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;P.mkdir(parents=True,exist_ok=True);R=REPO/'public/assets/wildshard-art';S=bpy.context.scene;old_names={o.name for o in S.objects};sources=[];placements=[]
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes['Principled BSDF'];s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.65;return m
M={'steel':mat('MOVERS steel',(.075,.11,.12),.6),'orange':mat('MOVERS safety orange',(.72,.26,.045),.2),'concrete':mat('MOVERS boardformed concrete',(.39,.42,.38)),'light':mat('MOVERS warm edges',(.75,.70,.53)),'rubber':mat('MOVERS rubber',(.025,.035,.036)),'sand':mat('MOVERS approach gravel',(.48,.42,.29))}
def box(n,xyz,dim,ma,bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.name='MOVERS | '+n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[ma]);
 if bevel:v=o.modifiers.new('Built edge','BEVEL');v.width=bevel;v.segments=1
 return o
def beam(n,a,b,w,ma):
 d=Vector(b)-Vector(a);o=box(n,(Vector(a)+Vector(b))/2,(w,w,d.length),ma,.015);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def cyl(n,xyz,r,depth,ma):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=xyz);o=bpy.context.object;o.name='MOVERS | '+n;o.data.materials.append(M[ma]);return o
def proto(n):
 f=R/(n+'.glb');before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(f));objs=sorted(set(S.objects)-before,key=lambda o:o.name);p=[(o.name,o.data,o.matrix_world.copy()) for o in objs if o.type=='MESH'];sources.append({'path':'public/assets/wildshard-art/'+f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 for o in objs:bpy.data.objects.remove(o,do_unlink=True)
 return n,p
def put(p,label,x,y,z=0,yaw=0):
 T=Matrix.Translation((x,y,z))@Matrix.Rotation(yaw,4,'Z')
 for n,mesh,m in p[1]:o=bpy.data.objects.new('MOVERS | '+label+' | '+n,mesh);S.collection.objects.link(o);o.matrix_world=T@m
 placements.append({'asset':p[0],'label':label,'xyz':[x,y,z],'yaw':yaw})
def text(n,words,pos,size=.7):
 bpy.ops.object.text_add(location=pos,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='MOVERS | '+n;o.data.body=words;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size;o.data.extrude=.008;o.data.materials.append(M['light']);bpy.ops.object.convert(target='MESH')
platform=proto('wsc-module-009-mover-station-platform');belt=proto('wsc-prop-037-conveyor-module');pad=proto('wsc-plan-007-mover-jump-pad-casing');rail=proto('wsc-prop-039-mover-guardrail');ladder=proto('wsc-prop-040-mover-access-ladder')
# Source entry route: north Movers Gate(-95,-60) to course start(-74,-90).
box('gate-to-start gravel threshold',(-95,67,.045),(8,14,.09),'sand',0)
box('eastward entry court',(-85,77,.045),(28,6,.09),'sand',0)
box('course start approach',(-74,87.5,.045),(6,15,.09),'sand',0)
# All stations run east->west along mapz-103. Full reserved98x58m zone remains intact.
for i,x in enumerate([-84,-90,-96]):put(belt,'Station1 static belt '+str(i+1),x,103,.10,0 if i%2==0 else math.pi)
box('Station1 conveyor base',(-90,103,.045),(20,5,.09),'concrete',.02)
# Pad casings at ground, neutral static poses; no implied launch physics.
for i,x in enumerate([-104,-110,-116]):put(pad,'Station2 static jump pad '+str(i+1),x,103,.12)
box('Station2 pad run',(-110,103,.05),(16,7,.10),'concrete',.02)
# First six-metre landing and enclosed pit with open top, floor retained at existing0m ground.
box('Station2 six metre receiving ledge',(-121,103,5.75),(4,8,.5),'concrete')
for x in [-119.5,-122.5]:
 for y in [99.8,106.2]:box('Ledge support',(x,y,2.75),(.5,.5,5.5),'steel')
for y in [98.4,107.6]:box('Station3 pit retaining side',(-132,y,2.8),(16,.5,5.6),'concrete')
box('Station3 shaded pit floor',(-132,103,.08),(16,9,.16),'rubber',0)
for y in [100.5,105.5]:box('Station3 slider guide STATIC',(-132,y,5.6),(16,.18,.24),'steel')
for i,(x,y) in enumerate([(-126,101.8),(-132,104.2),(-138,101.8)]):put(platform,'Station3 slider neutral pose '+str(i+1),x,y,4.888)
box('Station3 far landing',(-141,103,5.75),(2,8,.5),'concrete')
# Station4 disc at nominal6m and offset sweep arm, both static proxies.
cyl('Station4 turntable pedestal',(-147,103,2.7),1.2,5.4,'steel');cyl('Station4 rotating disc STATIC',(-147,103,5.85),4.5,.3,'steel');cyl('Station4 centre axle',(-147,103,6.45),.32,1.2,'orange')
beam('Station4 sweep arm STATIC',(-147,103,6.65),(-143.8,105.5,6.65),.22,'orange')
# Lift starts at6m,18m top. Tall guides and top-deck trusses make the destination legible from gate.
for x in [-159.6,-154.4]:
 for y in [99.5,106.5]:
  box('Station5 lift guide',(x,y,9.1),(.45,.45,18.2),'steel')
  box('Station5 guide foot',(x,y,.18),(1.2,1.2,.36),'concrete')
box('Station5 lift head beam',(-157,103,18.5),(6,8,.6),'orange')
box('Station5 lift cage floor STATIC at6m',(-157,103,5.8),(5.5,6.2,.4),'orange')
for y in [100.2,105.8]:put(rail,'Station5 lift safety rail',-157,y,6)
for x in [-159.6,-154.4]:
 for z in [3,9,15]:beam('Station5 lateral X brace',(x,99.5,z-2.5),(x,106.5,z+2.5),.13,'steel')
# Top-deck18m height, sourcex[-168,-160]. No tank/ropebridge extension.
box('Station6 top deck',(-164,103,17.7),(8,10,.6),'steel');box('Station6 deck nosing',(-164,97.9,17.85),(8,.22,.3),'orange')
for x in [-167.5,-160.5]:
 for y in [98.4,107.6]:box('Station6 column',(x,y,8.7),(.65,.65,17.4),'steel');box('Station6 footing',(x,y,.2),(1,1,.4),'concrete')
for y in [98.4,107.6]:
 for z in [3,9,15]:
  beam('Station6 triangulated truss',(-167.6,y,z-2.5),(-160.4,y,z+2.5),.2,'orange');beam('Station6 return truss',(-160.4,y,z-2.5),(-167.6,y,z+2.5),.2,'steel')
for y in [98.2,107.8]:
 for x in [-166.5,-163.6,-161]:put(rail,'Station6 edge rail',x,y,18)
for y in [99.7,102.6,105.5]:put(rail,'Station6 west return rail',-167.8,y,18,math.pi/2)
# Existing ladders used unscaled only on3.7m maintenance rises; no fake6m climb claim.
put(ladder,'Maintenance ladder specimen STATIC',-120,99,0)
# Large numbered route markers are explicit study signage, not six new IDs or disguised baked01 copies.
for num,x,z,label in [(1,-90,0,'CONVEYORS'),(2,-110,0,'JUMP PADS'),(3,-132,6,'SLIDERS'),(4,-147,6,'SPINNER'),(5,-157,10,'LIFT'),(6,-164,18,'TOP DECK')]:
 box('Station marker '+str(num),(x,97, z+1.4),(3.6,.16,1.5),'orange');text('Route label '+str(num),str(num)+'  '+label,(x,96.9,z+1.4),.43)
# A clear front observation/recovery path connects stations outside play apparatus; inferred art only.
box('Station observation path',(-122.5,92,.03),(91,4,.06),'sand',0)
# Newmesh content must stay inside source zone except defined gate approach.
added=[o for o in S.objects if o.type=='MESH' and o.name not in old_names]
(P/'manifest.json').write_text(json.dumps({'baseline':'retained West r02','baseline_glb_sha256':'92f04d657deaea793bf08066d8a0a8c1ee167190a49c518ca6f655da8ef61b01','source':'Raynos/project-wildshard-singleplayer@ce1cf050b3 art/showcase-template/round-5-blockout/layout.js MOVERS','zone_blender_xy':[-168,-70,74,132],'station_axis_y':103,'source_heights':[0,0,6,6,6,18],'sources':sources,'placements':placements,'proxies':['slider neutral poses','spinner/disc/sweep arm','lift cage/structure','ledges/supports','route markers','observation path'],'excluded':['gameplay','animation','collision','tank','rope bridge'],'new_meshes':len(added)},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-r02-plus-movers-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-r02-plus-movers-editable.blend'))
