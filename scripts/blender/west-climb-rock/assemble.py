import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;S=bpy.context.scene;R=REPO/'public/assets/wildshard-art'
C=bpy.data.collections.new('W8a W9a | static climb and Rock exterior');S.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new('CLIMB '+n);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=.82;return m
M={k:mat(k,c) for k,c in {'earth':(.40,.34,.21),'light':(.50,.43,.32),'slate':(.31,.30,.257),'shadow':(.235,.244,.20),'moss':(.30,.37,.24),'cliff':(.38,.345,.282),'dark':(.034,.049,.047),'timber':(.26,.128,.059),'cedar':(.39,.206,.090),'amber':(.50,.28,.12),'hemp':(.58,.413,.228),'steel':(.075,.11,.112),'teal':(.063,.30,.29),'sand':(.49,.43,.32)}.items()}
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
  o=bpy.data.objects.new('CLIMB | '+n,d);C.objects.link(o);return o
g=Group();g.box((-122,-94,-.35),(250,68,.7),'moss');ground=g.mesh('southern ground extension y -60 to -128');ground.data.materials[0]=bpy.data.objects['WIP precinct ground'].data.materials[0]
# Source West Gate routes (positive map z becomes negative Blender Y). Straight/gravel detail inferred.
g=Group()
def path(a,b,w,z=.035):
 a=Vector((*a,z));b=Vector((*b,z));u=(b-a).normalized();v=Vector((-u.y,u.x,0));g.box((a+b)/2,((a-b).length,w,.034),'sand',u,v)
path((-150,0),(-200,-10),5.4);path((-200,-10),(-200,-14),4.1,.036);path((-150,0),(-160,-10),3.6,.037);path((-160,-10),(-167,-18),3.6,.038);path((-200,-84),(-200,-74),4.2,.034)
g.box((-156,-42,.014),(40,56,.027),'earth');g.mesh('source yard footprint plus two West Gate branches')
# Existing visual motifs are imported at native scale; the landmark is never a stretched cave prop.
sources=[]
def donor(key,n,xyz,yaw=0):
 f=R/next(n for n in PINS if key in n);sources.append({'asset':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(f));obs=set(S.objects)-before;T=Matrix.Translation(xyz)@Matrix.Rotation(yaw,4,'Z')
 for i,o in enumerate(sorted(obs,key=lambda o:o.name)):
  if o.type!='MESH':continue
  a=bpy.data.objects.new('CLIMB | '+n+' %02d'%i,o.data);C.objects.link(a);a.matrix_world=T@o.matrix_world
 for o in obs:bpy.data.objects.remove(o,do_unlink=True)
# Crag: continuous faceted rings, bevel-like strata, top plane 16 m. Mouth sector cut shallowly from exterior.
CX,CY=-206,-44
N=72
profiles=[(0,22,29.3),(2.7,21.8,28.1),(4.0,21.4,28.7),(7.3,19.1,25.1),(9.4,17.9,24.0),(12.4,15.9,21),(15.0,13.5,18.2),(16.0,12.8,17.2)]
shell=Group();rings=[]
for j,(z,rx,ry) in enumerate(profiles):
 ring=[]
 for i in range(N):
  a=math.tau*i/N+.018*math.sin(i*2.1+j*1.19);f=.952+.040*math.sin(a*5+j*.63)+.016*math.cos(a*11+j*.72);x=CX+rx*math.cos(a)*f;y=CY+ry*math.sin(a)*f
  # Crag brow over each native portal; push only low arc y into shallow decorative recess.
  if j<2 and abs(x+200)<4.8 and abs(y-CY)>19:y-=math.copysign((4.8-abs(x+200))*.86,y-CY)
  zv=z if j in (0,7) else z+.61*math.sin(3*a+j*.55)+.33*math.cos(9*a+j)
  ring.append((x,y,zv))
 rings.append(ring)
for j in range(len(rings)-1):
 for i in range(N):
  k=(i+1)%N;a=rings[j][i];b=rings[j][k];c=rings[j+1][k];d=rings[j+1][i]
  palette=['slate','slate','shadow','cliff','cliff','light','moss'];ma=palette[j]
  if (i*37+j*29)%11<3:ma=['cliff','moss','slate','slate','shadow','cliff','slate'][j]
  shell.add([a,b,c,d],[(0,1,2),(0,2,3)],ma)
top=rings[-1];shell.add([(CX,CY,16),*top],[(0,i+1,((i+1)%N)+1) for i in range(N)],'moss');shell.mesh('crag mesh 44m zone / crown 16m')
for n,y,yaw in [('north',-14,math.pi),('south',-74,0)]:donor('prop-011','native cave mouth '+n,(-200,y,0),yaw)
g=Group()
# Dark stone end stops are shallow facade occlusion, not a modeled tunnel or playable opening.
for y in [-15.6,-72.4]:g.box((-200,y,1.2),(4.6,.34,2.4),'dark')
g.mesh('north and south exterior recess backing')
donor('prop-044','native lookout bench',(-210,-40,16),math.pi/2)
# Site-specific deck frames and planks (one repeated kit). Eye/deck centres are source points.
deck=[('A',-166,-28,6),('B',-146,-44,10),('C',-170,-60,14)]
for n,x,y,h in deck:
 g=Group();g.box((x,y,h-.32),(6.6,6.7,.32),'timber')
 for j in range(12):g.box((x,y+(j-5.5)*.54,h-.085),(6.6,.52,.17),('cedar','amber','timber')[j%3])
 for dx in [-2.7,2.7]:
  for dy in [-2.7,2.7]:
   g.box((x+dx,y+dy,.18),(.91,.91,.36),'cliff');g.box((x+dx,y+dy,h/2),(.44,.44,h),'timber')
 for dx in [-2.7,2.7]:
  g.rod((x+dx,y-2.7,.66),(x+dx,y+2.7,h-.48),.15,'steel')
  g.rod((x+dx,y+2.7,.66),(x+dx,y-2.7,h-.48),.15,'steel')
 # Outer north and south guards skip exact ladder and side bridge entries.
 for dy in [-3.2,3.2]:
  xs=[(x-3.15,x-.75),(x+.75,x+3.15)] if dy<0 else [(x-3.15,x+3.15)]
  for a,b in xs:
   for q in [a,b]:g.rod((q,y+dy,h),(q,y+dy,h+1.08),.07,'timber')
   for z in [.55,1.02]:g.rod((a,y+dy,h+z),(b,y+dy,h+z),.047,'hemp')
 for dx in [-.31,.31]:g.rod((x+dx,y-3.40,.17),(x+dx,y-3.40,h+.78),.061,'steel')
 for j in range(1,math.floor(h/.33)+1):g.rod((x-.31,y-3.40,j*.33),(x+.31,y-3.40,j*.33),.029,'amber')
 g.mesh('deck '+n+' and ladder, walking plane '+str(h)+'m')
# Scramble wall envelope exact; scale-safe ledges illustrative only.
g=Group()
for j,h in enumerate([1.3,2.6,3.9,5.2,6.5]):
 x=-172.6+j*2.8;y=-19-(j%2)*.62;g.box((x,y,h/2),(2.77,5.96,h),('cliff','slate')[j%2]);g.box((x,y,h+.038),(2.71,5.80,.076),'light')
g.mesh('scramble wall inferred surface')
# Native rope-walkway language without stretching an 8.7m donor. Batched by bridge.
bridges=[('AB',(-163,-30,6),(-149,-42,10),1.4,1.4),('BC',(-149,-46,10),(-167,-59,14),1.4,1.4),('C Rock',(-173,-59,14),(-198,-50,16),1.8,1.8)]
records=[]
for n,a,b,w,sag in bridges:
 g=Group();A=Vector(a);B=Vector(b);D=B-A;L=math.hypot(D.x,D.y);U=Vector((D.x/L,D.y/L,0));V=Vector((-U.y,U.x,0));N=round(L/.43)
 def point(t):
  p=A+D*t-Vector((0,0,4*sag*t*(1-t)))
  # Fitted approach rises onto the existing summit plane before its irregular rim.
  # Keep historically exact endpoints, but use an inferred shaped transition rather than pure sag at the join.
  if n=='C Rock' and t>.67:
   if t<=.82:
    q=(t-.67)/.15;f=q*q*(3-2*q);p.z=p.z*(1-f)+16.065*f
   else:p.z=16+.065*(1-t)/.18
  return p
 for i in range(N):
  t=(i+.5)/N;p=point(t);u=(point(min(1,t+.012))-point(max(0,t-.012))).normalized()
  g.box(p-Vector((0,0,.072)),(L/N-.022,w,.14),['cedar','timber','amber'][i%3],u,V)
 for p in [A,B]:
  g.box(p-Vector((0,0,.055)),(.9,w,.132),'cedar',U,V)
  for s in [-1,1]:g.rod(p+V*s*(w*.58),p+V*s*(w*.58)+Vector((0,0,1.27)),.084,'timber')
 for s in [-1,1]:
  v=V*s*(w*.55);z=Vector((0,0,1.05))
  for i in range(N):
   a0=point(i/N)+v;b0=point((i+1)/N)+v;g.rod(a0+z,b0+z,.035,'hemp')
   if i%3==0:g.rod(a0,a0+z,.023,'hemp',5)
 g.mesh('bridge '+n);records.append({'name':n,'anchors_blender':[a,b],'straight_m':D.length,'width_m':w,'illustrative_sag_m':sag,'end_fit':'raised shaped transition into rock crown, source endpoint retained' if n=='C Rock' else None})
g=Group()
# Exterior north chimney, separate from preserved crag body; ladder ends at16 m.
# Massive tapered shoulder takes the chimney from source anchor into the main crag; no floating ledge.
rings2=[(0,-221,-212,-15.3,-35),(5,-220,-212.4,-15.9,-34),(9,-219.4,-213.2,-16.2,-33),(13,-218.2,-213.9,-16.1,-32),(16,-217.6,-214.4,-16.2,-31)]
for k in range(len(rings2)-1):
 z,a,b,front,back=rings2[k];zz,c,d,f,h=rings2[k+1]
 v=[(a,front,z),(b,front,z),(b,back,z),(a,back,z),(c,f,zz),(d,f,zz),(d,h,zz),(c,h,zz)]
 g.add(v,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],['slate','shadow','slate','cliff'][k])
z,a,b,f,h=rings2[-1];g.add([(a,f,z),(b,f,z),(b,h,z),(a,h,z)],[(0,1,2,3)],'cliff')
g.box((-216,-16,7.86),(.40,1.22,15.72),'slate')
# Interlocking talus fins flank the native mouths and visually bring the crag face forward.
for yy,sg in [(-14,-1),(-74,1)]:
 for j,(x,w,h) in enumerate([(-205.2,4.1,5.5),(-207.3,3.7,3.8),(-194.5,4.4,4.9),(-192.6,4.1,3.7)]):
  y=yy+sg*(2.15+(j%2)*.85);a=w/2;d=3.8
  g.add([(x-a,y-d,0),(x+a,y-d,0),(x+a,y+d,0),(x-a,y+d,0),(x-a*.50,y-d*.41,h*.78),(x+a*.41,y-d*.52,h*.92),(x+a*.61,y+d*.57,h),(x-a*.49,y+d*.46,h*.86)],[(0,1,5,4),(1,2,6,5),(2,3,7,6),(0,4,7,3),(4,5,6,7)],['cliff','earth','slate','light'][j])
# Seven south scramble massing steps, source-inspired, not mechanically qualified.
for j in range(7):
 h=1+.726*(j+1)*2.2/1.6;x=-216+(j%2)*2;y=-72+j*2.6
 g.box((x,y,h/2),(3.9,2.90,h),('cliff','slate')[j%2])

for dx in [-.35,.35]:g.rod((-216+dx,-15.23,.10),(-216+dx,-15.23,16.32),.057,'steel')
for j in range(1,47):g.rod((-216.35,-15.23,j*.34),(-215.65,-15.23,j*.34),.032,'amber')
# Decorative chimney connection; short horizontal service ledge only, not a climb fit claim.

g.mesh('north chimney and exterior ladder')
(P/'integration.json').write_text(json.dumps({'baseline':'whole-town-editable.blend','donors':sources,'bridges':records,'geometry_map_anchors':'ce1cf050b3 round4 lab.js and layout.js','source_yard_xz':[-176,-136,14,70],'source_rock_zone_xz':[-228,-184,14,74],'zone_envelope_reconciles_source_radius_discrepancy':True,'crown_m':16,'mouth_centres_map_xz':[[-200,14],[-200,74]],'status':'static art exterior only; no cave interior, traverse, collision, swing or performance validation'},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'climb-rock-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'climb-rock-editable.blend'))
