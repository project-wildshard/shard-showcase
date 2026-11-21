import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;S=bpy.context.scene;R=REPO/'public/assets/wildshard-art'
C=bpy.data.collections.new('W4b | connected Physics Yard static art');S.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new('PHYS '+n);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=.82;return m
M={k:mat(k,c) for k,c in {'earth':(.40,.34,.21),'light':(.50,.43,.32),'slate':(.31,.30,.257),'shadow':(.235,.244,.20),'moss':(.30,.37,.24),'cliff':(.38,.345,.282),'dark':(.034,.049,.047),'timber':(.26,.128,.059),'cedar':(.39,.206,.090),'amber':(.50,.28,.12),'hemp':(.58,.413,.228),'steel':(.075,.11,.112),'teal':(.063,.30,.29),'sand':(.49,.43,.32),'orange':(.64,.26,.068),'darkorange':(.31,.143,.065),'lightorange':(.79,.42,.15),'cyan':(.06,.54,.64),'floor':(.205,.265,.25),'line':(.66,.63,.50)}.items()}
class Group:
 def __init__(self):self.v=[];self.f=[];self.ms=[]
 def add(self,vs,fs,k):
  i=len(self.v);self.v.extend(vs);self.f.extend(tuple(i+x for x in f) for f in fs);self.ms.extend([k]*len(fs))
 def box(self,p,d,k,u=(1,0,0),v=(0,1,0)):
  p=Vector(p);u=Vector(u);v=Vector(v);w=u.cross(v)
  self.add([tuple(p+i*d[0]/2*u+j*d[1]/2*v+z*d[2]/2*w) for z in [-1,1] for j in [-1,1] for i in [-1,1]],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],k)
 def rod(self,a,b,r,k,N=7):
  a=Vector(a);b=Vector(b);d=(b-a).normalized();v=d.cross(Vector((0,0,1))) if abs(d.z)<.99 else d.cross(Vector((1,0,0)));v.normalize();w=d.cross(v)
  self.add([tuple(p+r*(math.cos(i*math.tau/N)*v+math.sin(i*math.tau/N)*w)) for p in [a,b] for i in range(N)],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],k)
 def mesh(self,n):
  d=bpy.data.meshes.new(n);d.from_pydata(self.v,[],self.f);keys=list(dict.fromkeys(self.ms))
  for k in keys:d.materials.append(M[k])
  for f,k in zip(d.polygons,self.ms):f.material_index=keys.index(k)
  o=bpy.data.objects.new('PHYS | '+n,d);C.objects.link(o);return o
def label(n,txt,p,size,angle=0):
 bpy.ops.object.select_all(action='DESELECT')
 d=bpy.data.curves.new(n,'FONT');d.body=txt;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.009;d.materials.append(M['line']);o=bpy.data.objects.new('PHYS | '+n,d);C.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,angle);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
def instance(o,n,p):
 q=bpy.data.objects.new('PHYS | '+n,o.data);C.objects.link(q);q.location=p;return q
g=Group()
# Exact asphalt and 8 m alley between old park edge x=-100 and Physics x=-92.
g.box((-53,-207,.010),(78,54,.020),'floor');g.box((-96,-207,.010),(8,54,.020),'sand')
# Park-east openings are achieved without modifying any retained geometry.
def path(a,b,w,z):
 a=Vector((*a,z));b=Vector((*b,z));u=(b-a).normalized();v=Vector((-u.y,u.x,0));g.box((a+b)/2,((a-b).length,w,.021),'sand',u,v)
for i,(a,b) in enumerate(zip([(-36,-60),(-11,-64),(-11,-176),(-22,-188)],[(-11,-64),(-11,-176),(-22,-188),(-23,-192)])):path(a,b,5.4,.024+i*.003)
path((-96,-173),(-96,-180),5.2,.024)
for i in range(10):
 z=-182.5-i*5
 g.box((-99.68,z,.024),(.13,3.4,.012),'line');g.box((-92.32,z,.024),(.13,3.4,.012),'line')
# W9b cache anchor is just a flush navigation stitch; no cache object or behavior.
g.box((-96,-232,.023),(1.35,1.35,.010),'teal')
# Low perimeter wall only INSIDE yard, leave crossable West gaps and east approach clear.
for a,b in [(-233.3,-229),(-218,-212),(-193,-181)]:
 g.box((-91.62,(a+b)/2,.61),(.40,b-a,1.20),'steel');g.box((-91.62,(a+b)/2,1.22),(.50,b-a,.21),'darkorange')
for a,b in [(-91.35,-75),(-65,-46),(-37,-16)]:
 g.box(((a+b)/2,-233.6,.61),(b-a,.42,1.2),'steel');g.box(((a+b)/2,-233.6,1.22),(b-a,.52,.21),'darkorange')
# Ground island markings communicate the separate activity bays.
for x0,x1,y0,y1 in [(-88,-53,-232,-217),(-56,-16,-203,-189),(-88,-57,-199,-185)]:
 for y in [y0,y1]:g.box(((x0+x1)/2,y,.029),(x1-x0,.11,.011),'line')
 for x in [x0,x1]:g.box((x,(y0+y1)/2,.032),(.11,y1-y0,.011),'line')
# Brick work aisle blazes, no geometry outside exact range corridor.
for i in range(11):g.box((-11,-70-i*9.5,.037),(.13,2.7,.01),'line')
g.mesh('yard 78x54m - open 8m alley - Range Gate approach')
# One shared fixed-position see-saw study, 14m plan plank style and source centers.
g=Group()
for yy in [-1.08,1.08]:
 g.rod((-1.30,yy,.15),(0,yy,1.44),.14,'darkorange');g.rod((1.30,yy,.15),(0,yy,1.44),.14,'darkorange');g.box((0,yy,.13),(3.10,.56,.26),'steel')
g.rod((0,-1.44,1.48),(0,1.44,1.48),.22,'steel',12)
u=Vector((math.cos(.12),0,math.sin(.12)));v=Vector((0,1,0));p=Vector((0,0,1.57))
g.box(p,(14,2.6,.31),'darkorange',u,v)
for i in range(14):
 pp=p+u*(i-6.5)+Vector((0,0,.15));g.box(pp,(.982,2.46,.16),['orange','amber','cedar'][i%3],u,v)
for d in [-1,1]:g.box(p+u*d*6.77+Vector((0,0,.17)),(.40,2.56,.17),'steel',u,v)
g.rod((0,-1.41,1.48),(0,1.41,1.48),.30,'steel',12)
see=g.mesh('see-saw instance 1 original scene-only study');see.location=(-80,-224,0)
instance(see,'see-saw instance 2 shared scene-only study',(-62,-224,0))
# Exact 24 x 4 x 6m continuous ramp, high at east and running west toward target bank.
g=Group();x0=-42;x1=-18;y=-196
for i in range(12):
 a=x0+i*2;b=a+2;za=(a-x0)*.25;zb=(b-x0)*.25
 v=[(a,y-2,za),(b,y-2,zb),(b,y+2,zb),(a,y+2,za),(a,y-2,0),(b,y-2,0),(b,y+2,0),(a,y+2,0)]
 g.add(v,[(0,1,2,3)],'teal')
 for f in [(0,4,5,1),(2,6,7,3)]:g.add(v,[f],'darkorange' if i%2 else 'orange')
 if i==11:g.add(v,[(1,5,6,2)],'darkorange')
for yy in [y-1.92,y+1.92]:
 g.rod((-42,yy,.045),(-18,yy,6.045),.045,'steel')
 for i in range(8):
  xx=-40.7+i*3
  g.box((xx,yy+(.09 if yy>y else -.09),.16),(.36,.34,.3),'steel')
g.mesh('ball ramp core exactly 24m by 4m by 6m')
g=Group()
# Static release lever and clear apron are art-only. No active body/collider rows.
g.box((-17.24,-193.25,.12),(1.50,1.15,.24),'steel')
g.rod((-17.24,-193.25,.25),(-17.24,-193.25,5.72),.13,'steel')
g.rod((-17.24,-193.25,5.72),(-17.85,-193.25,6.15),.075,'orange')
g.box((-48.9,-196,.029),(13.6,4.3,.018),'teal')
for i in range(4):g.box((-43.4-i*3.5,-196,.043),(.14,4.16,.014),'line')
g.mesh('release lever and pin approach static arts')
# Shared color-panel ball proxy, 1.6m diameter.
g=Group();N=24
def sph(i,j):
 t=math.pi*j/16;p=math.tau*i/N;return (.8*math.sin(t)*math.cos(p),.8*math.sin(t)*math.sin(p),.8*math.cos(t))
for j in range(16):
 for i in range(N):
  g.add([sph(i,j),sph(i,j+1),sph(i+1,j+1),sph(i+1,j)],[(0,1,2,3)],'steel' if j in [5,10] or i%6==0 else 'orange' if (i//6+j//5)%2 else 'lightorange')
ball=g.mesh('ball 1 shared scene-only study')
for i in range(4):
 x=-19.5-i*1.8;z=(x+42)*.25+.8
 if i==0:ball.location=(x,-196,z)
 else:instance(ball,f'ball {i+1} shared scene-only study',(x,-196,z))
# Ten pins in the source triangular formation; one shared ivory model.
g=Group();N=16
rings=[(.3,0),(.3,.10),(.29,.17),(.266,.85),(.24,1.03),(.23,1.18),(.20,1.26),(.13,1.3),(0,1.30)]
for j,((a,z),(b,h)) in enumerate(zip(rings,rings[1:])):
 for i in range(N):
  c=math.tau*i/N;d=math.tau*(i+1)/N
  g.add([(a*math.cos(c),a*math.sin(c),z),(a*math.cos(d),a*math.sin(d),z),(b*math.cos(d),b*math.sin(d),h),(b*math.cos(c),b*math.sin(c),h)],[(0,1,2,3)],'orange' if j==4 else 'steel' if j==0 else 'line')
pin=g.mesh('pin 01 shared scene-only study');n=0
for r in range(4):
 for i in range(r+1):
  n+=1;p=(-50-r*1.2,-196-(i-r/2)*1.1,.04)
  if n==1:pin.location=p
  else:instance(pin,'pin %02d shared scene-only study'%n,p)
# W4a context is fixed, greybox positions only.
g=Group()
for x in [-82,-72,-62]:
 g.box((x,-192,.14),(4,4,.24),'steel');g.box((x,-192,.273),(3.54,3.54,.053),'cyan')
 for y in [-193.45,-190.55]:g.box((x,y,.306),(2.96,.12,.014),'line')
for y in [-202,-182]:g.box((-52,y,2.04),(.59,.55,4.08),'darkorange')
g.box((-52,-192,4.08),(.62,20.55,.56),'steel')
for y in range(-200,-183,3):g.box((-52,y,4.4),(.56,1.4,.10),'orange')
g.mesh('static plate court and open-frame gate')
f=R/'haul-crate.glb';before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(f));obs=set(S.objects)-before
proto=[(o.data,o.matrix_world.copy()) for o in sorted(obs,key=lambda o:o.name) if o.type=='MESH'];vs=[m@v.co for d,m in proto for v in d.vertices];sz=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3)];bottom=min(v.z for v in vs)
for o in obs:bpy.data.objects.remove(o,do_unlink=True)
assert all(v<3.2 for v in sz)
for i,(x,y) in enumerate([(-86,-204),(-83.8,-204),(-83.8,-206.2),(-30,-226),(-32.2,-226),(-44,-228),(-44,-230.2)]):
 for j,(d,m) in enumerate(proto):
  o=bpy.data.objects.new(f'PHYS | native cargo crate {i+1} component {j}',d);C.objects.link(o);o.matrix_world=Matrix.Translation((x,y,.022-bottom))@m
# Counter board and entry placard: labels face lane approach, no score claims.
g=Group()
for x,y,w in [(-59,-198.4,4.5),(-87,-216,4.7)]:
 for i in [-1,1]:g.box((x+i*w*.36,y,1.32),(.22,.23,2.64),'steel')
 g.box((x,y,2.3),(w,.25,1.05),'steel')
g.mesh('static scoreboard and district labels')
label('Pin board','SKITTLES',(-59,-198.25,2.45),.42,math.pi)
label('Yard board','PHYSICS YARD',(-87,-215.85,2.45),.49,math.pi)
(P/'integration.json').write_text(json.dumps({'baseline':'reviewed hover native','source':'Round5 layout/lab at ce1cf050b3; W4b switches static only; W9b cache alley marker','yard_map_xz':[-92,-14,180,234],'alley_map_xz':[-100,-92,180,234],'alley_anchor':[-96,232],'seesaws_map_xz':[[-80,224],[-62,224]],'ramp_xz':[-42,-18,196],'ramp_width_height_m':[4,6],'ball_count':4,'pin_count':10,'art_only_plan_concepts':['WSC-PLAN-003','WSC-PLAN-004','WSC-PLAN-005'],'native_crate':{'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':sz}},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'physics-yard-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'physics-yard-editable.blend'))
