import bpy,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;P.mkdir(parents=True,exist_ok=True);SRC=REPO/'public/assets/wildshard-art';W10=SRC
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene;random.seed(47);M={};sources=[];placements=[]
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;M[n]=m
for n,c in [('meadow',(.21,.31,.10)),('grasslight',(.29,.38,.14)),('sand',(.59,.44,.25)),('limestone',(.64,.54,.35)),('capstone',(.81,.70,.48)),('wood',(.20,.115,.055)),('roof',(.06,.25,.24)),('gold',(.9,.47,.08)),('path',(.49,.42,.29))]:mat(n,c)
def box(n,x,y,z,dx,dy,dz,ma,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z));o=bpy.context.object;o.name=n;o.dimensions=(dx,dy,dz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[ma]);
 if bev:md=o.modifiers.new('edge','BEVEL');md.width=bev;md.segments=1
 return o
def proto(n,folder=SRC):
 f=folder/(n+'.glb');before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(f));objs=sorted(set(S.objects)-before,key=lambda obj:obj.name);a=[];pts=[]
 for o in objs:
  if o.type=='MESH':
   a.append((o.name,o.data,o.matrix_world.copy()));pts.extend(o.matrix_world@Vector(v) for v in o.bound_box)
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 for o in objs:bpy.data.objects.remove(o,do_unlink=True)
 sources.append({'source':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bounds':[lo,hi]});return (n,a,lo,hi)
def place(pr,n,x,y,yaw=0,z=0):
 nm,a,lo,hi=pr;T=Matrix.Translation((x,y,z-lo[2]))@Matrix.Rotation(yaw,4,'Z')
 for name,mesh,m in a:
  o=bpy.data.objects.new(n+' | '+name,mesh);S.collection.objects.link(o);o.matrix_world=T@m
 placements.append({'asset':nm,'name':n,'blender_xy':[x,y],'map_xz':[x,-y],'yaw':yaw,'ground_z':z})
fence=proto('wsc-module-011-riding-fence');tree=proto('wsc-prop-012-deciduous-tree');fir=proto('wsc-prop-046-conifer-tree');house=proto('town-gate-merchant-house');ring=proto('wsc-prop-043-riding-ring');gantry=proto('wsc-module-010-riding-start-gantry');timer=proto('wsc-prop-042-riding-timer-display');trough=proto('w10a-paddock-trough-wip',W10);jump=proto('w10b-reusable-riding-jump-wip',W10)
# Map x east,z south to Blender x,-z,metres. Full measured precinct, no miniature scaling.
box('WIP precinct ground',-122,130,-.35,250,230,.7,'meadow')
# Town north wall and exact Stable/Movers Gate openings, 5m wall. No fake closure across routes.
for a,b in [(-128,-101),(-89,-42),(-30,-8)]:
 box('Town north wall',.5*(a+b),60,2.5,b-a,1,5,'limestone');box('Wall coping',.5*(a+b),60,5.12,b-a,1.3,.24,'capstone')
for x in (-42,-30,-101,-89):
 box('Gate pier',x,60,3,1.6,2,6,'limestone');box('Pier crown',x,60,6.2,2,2.4,.4,'capstone')
box('Stable Gate beam',-36,60,5.9,12,1.25,.8,'wood')
# Banner uprights are scenic, not new catalogue assets.
for x in (-43.1,-28.9):
 box('Gate teal banner',x,58.9,4.1,1.2,.07,2.4,'roof');box('Gold band',x,58.83,4.5,1.22,.04,.16,'gold')
box('Stable Lane exact 12m',-36,39.5,.025,12,39,.05,'path')
box('Stable to paddock approach',-36,66,.03,12,12,.06,'path')
box('Paddock central route',-38,102,.025,8,60,.05,'path')
box('Paddock to oval chute 12m',-40,140,.025,12,16,.05,'sand')
# Paddock fence repeats source, never stretch entire rail. 12m entry and 12m chute openings.
def fence_line(a,b,label):
 d=Vector((b[0]-a[0],b[1]-a[1]));L=d.length;count=max(1,math.floor(L/3.138));step=L/count
 for i in range(count):
  u=(i+.5)/count;place(fence,label+str(i),a[0]+d.x*u,a[1]+d.y*u,math.atan2(d.y,d.x))
for a,b in [((-62,72),(-42,72)),((-30,72),(-14,72)),((-62,72),(-62,132)),((-14,72),(-14,132)),((-62,132),(-46,132)),((-34,132),(-14,132)),((-46,132),(-46,148)),((-34,132),(-34,148))]:fence_line(a,b,'Paddock/chute fence ')
place(trough,'W10 trough exact plan position',-52,100);place(proto('wsc-plan-008-horse-mounting-block-wip',SRC),'Existing WIP mounting block exact plan position',-36,96)
# Stable occupies authoritative 18x18m interior lot x[-28,-10],z[-56,-38]; barn mass is explicit WIP.
box('Stable WIP barn back',-19,39,3,18,1,6,'limestone')
for x in (-27.5,-10.5):box('Stable WIP side wall',x,47,3,1,18,6,'limestone')
for x in (-27,-21.7,-16.3,-11):box('Stable arcade post',x,55,2.5,.35,.35,5,'wood')
box('Stable arcade header',-19,55,5.2,18,.45,.5,'wood')
for x in (-23.5,-14.5):
 o=box('Stable pitched roof',x,47,6.8,10,20,.3,'roof');o.rotation_euler.y=math.radians(20 if x< -19 else -20)
box('Stable ridge',-19,47,8.45,.3,20,.3,'gold')
# Town block context: existing house mesh, no scale changes, kept west of Stable Lane.
for x,y in [(-53,47),(-72,47),(-114,47),(-53,25),(-76,25),(-114,25)]:place(house,'North town existing house',x,y,math.pi)
# Stadium track centre (-122,-186), r38, halfstraight60: 479m centreline, 12m track, 208x88 outer envelope.
pts=[]
for i in range(49):pts.append((-182+120*i/48,148))
for i in range(1,49):t=-math.pi/2+math.pi*i/48;pts.append((-62+38*math.cos(t),186+38*math.sin(t)))
for i in range(1,49):pts.append((-62-120*i/48,224))
for i in range(1,49):t=math.pi/2+math.pi*i/48;pts.append((-182+38*math.cos(t),186+38*math.sin(t)))
verts=[]
for i,(x,y) in enumerate(pts[:-1]):
 prev=Vector(pts[(i-1)%(len(pts)-1)]);nxt=Vector(pts[(i+1)%(len(pts)-1)]);d=(nxt-prev).normalized();normal=Vector((-d.y,d.x));verts.extend([(x+normal.x*6,y+normal.y*6,.04),(x-normal.x*6,y-normal.y*6,.04)])
N=len(verts)//2;faces=[(i*2,i*2+1,((i+1)%N)*2+1,((i+1)%N)*2) for i in range(N)];me=bpy.data.meshes.new('12m actual ring surface');me.from_pydata(verts,[],faces);me.materials.append(M['sand']);o=bpy.data.objects.new('479m oval actual geometry',me);S.collection.objects.link(o)
# Track equipment at source gantry anchor; other station coordinates are visual-study inferences.
place(gantry,'Source riding gantry',-80,148,math.pi/2);place(timer,'Lap timer display on gantry',-80,148,math.pi/2,5.6)
box('Riding lap PB board PROXY',-80,137,1.65,2,.15,1.2,'wood');box('PB board proxy leg',-80,137,.65,.15,.15,1.3,'wood')
for i,(x,y,yaw) in enumerate([(-145,148,math.pi/2),(-105,148,math.pi/2),(-28,169,0),(-28,203,0),(-100,224,math.pi/2),(-145,224,math.pi/2),(-216,203,0),(-216,169,0)]):place(ring,'Riding ring '+str(i+1),x,y,yaw)
for i,(x,y,yaw) in enumerate([(-165,148,math.pi/2),(-125,148,math.pi/2),(-110,224,math.pi/2),(-160,224,math.pi/2)]):place(jump,'Reusable jump '+str(i+1),x,y,yaw)
# Clearly separated planted verges: keep oval surface and approach routes empty.
for x,y in [(-57,81),(-57,118),(-19,83),(-19,118),(-48,65),(-23,66),(-53,138),(-21,139),(-48,172),(-74,195),(-100,190),(-130,182),(-160,198),(-190,184)]:place(tree,'Existing oak planted verge',x,y)
for i in range(27):
 x=-232+i*8.1;y=239+random.uniform(-2,2);place(fir,'North perimeter windbreak',x,y)
# Visual WIP scale marker, not actor: 1.75m human silhouette beside Stable Gate.
box('1.75m scale marker torso',-32.5,56,1.08,.42,.28,.65,'gold');box('Scale marker legs',-32.5,56,.4,.32,.25,.8,'wood');bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.15,location=(-32.5,56,1.6));bpy.context.object.name='Scale marker head';bpy.context.object.data.materials.append(M['gold'])
# All art exports selected; cameras/lights excluded.
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-linked-precinct-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
(P/'manifest.json').write_text(json.dumps({'status':'private assembled WIP, not gameplay','source_layout_commit':'ce1cf050b3','layout_path':'art/showcase-template/round-5-blockout/layout.js','sources':sources,'placements':placements,'map_transform':'(x,y,z)->(x,-z,y)','inferences':['stable architectural form','tree planting','ring and jump station placement','12m chute width','PB board proxy'],'exact_anchors':{'gate':[-36,-60],'paddock':[-62,-14,-132,-72],'oval':[-122,-186,60,38,12],'stable_lot':[-28,-10,-56,-38]},'horses':0,'rings':8,'jumps':4},indent=2))
# Warm coherent light, daylight; fresh cameras include one true 1.75m player eye.
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=False;S.render.resolution_x=1600;S.render.resolution_y=1000;S.render.resolution_percentage=100
S.world=bpy.data.worlds.new('West daylight');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.60,.78,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.55
bpy.ops.object.light_add(type='SUN',location=(0,0,60));sun=bpy.context.object;sun.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-35));sun.data.energy=2.4;sun.data.angle=.1
for name,pos,target,lens in [('01-linked-precinct-hero',(-4,13,77),(-108,154,0),29),('02-stable-gate-player-eye',(-36,45,1.75),(-39,142,4),22)]:
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.name=name;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1200;S.camera=cam;S.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True) if RENDER else None
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-linked-precinct-WIP.blend'));print('ASSEMBLY COMPLETE')
