import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;S=bpy.context.scene;R=REPO/'public/assets/wildshard-art'
C=bpy.data.collections.new('W07 | connected Hover Park static art');S.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new('HOVER '+n);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=.82;return m
M={k:mat(k,c) for k,c in {'earth':(.40,.34,.21),'light':(.50,.43,.32),'slate':(.31,.30,.257),'shadow':(.235,.244,.20),'moss':(.30,.37,.24),'cliff':(.38,.345,.282),'dark':(.034,.049,.047),'timber':(.26,.128,.059),'cedar':(.39,.206,.090),'amber':(.50,.28,.12),'hemp':(.58,.413,.228),'steel':(.075,.11,.112),'teal':(.063,.30,.29),'sand':(.49,.43,.32),'orange':(.64,.26,.068),'darkorange':(.31,.143,.065),'lightorange':(.79,.42,.15),'cyan':(.06,.54,.64),'floor':(.39,.40,.34),'line':(.66,.63,.50)}.items()}
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
  o=bpy.data.objects.new('HOVER | '+n,d);C.objects.link(o);return o
def height(x):return x
g=Group();g.box((-122,-188,-.35),(250,120,.7),'moss');o=g.mesh('ground extension y -128 to -248');o.data.materials[0]=bpy.data.objects['WIP precinct ground'].data.materials[0]
g=Group();g.box((-167,-173,.0025),(134,122,.005),'floor')
# Park Gate path is an inferred visible band aligned to source waypoints.
def path(a,b,w,z):
 a=Vector((*a,z));b=Vector((*b,z));u=(b-a).normalized();v=Vector((-u.y,u.x,0));g.box((a+b)/2,((a-b).length,w,.02),'sand',u,v)
path((-95,-60),(-103,-119),6.8,.02);path((-103,-119),(-106,-141),6.8,.022)
for x in [-230,-104]:
 for y in range(-229,-115,6):g.box((x,y,.015),(.095,2.7,.018),'line')
g.mesh('zone paving precise footprint and Park Gate route')
sources=[]
def proto(key):
 assert key+'.glb' in PINS;f=R/(key+'.glb');before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(f));obs=set(S.objects)-before
 a=[(o.name,o.data,o.matrix_world.copy()) for o in sorted(obs,key=lambda o:o.name) if o.type=='MESH']
 v=[m@u.co for _,d,m in a for u in d.vertices];bounds=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]]
 sources.append({'asset':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bounds_local_blender':bounds})
 for o in obs:bpy.data.objects.remove(o,do_unlink=True)
 return a,bounds
def put(a,n,xyz,rot=0):
 T=Matrix.Translation(xyz)@Matrix.Rotation(rot,4,'Z')
 for i,(label,d,m) in enumerate(a):
  o=bpy.data.objects.new('HOVER | '+n+' %02d'%i,d);C.objects.link(o);o.matrix_world=T@m
strip,sb=proto('wsc-prop-031-hover-run-up-strip');lanes=[]
for y,h,suffix in [(-132,2.4,''),(-143,3.6,'-36'),(-154,4.8,'-48')]:
 r,b=proto('wsc-module-007-hover-kicker'+suffix);x=-157+b[0][1]
 put(r,'ramp %.1f'%h,(x,y,0),math.pi/2);put(strip,'run-up %.1f'%h,(-134.5,y,0),math.pi/2)
 lanes.append({'height_m':h,'map_lane_z':-y,'toe_x':-157,'kicker_center_x':x,'strip_span_x':[-157,-112],'strip_width_m':3.9})
def wall(g,x0,y0,y1,direction,fun,wide,k):
 for i in range(len(fun)-1):
  a0,z0=fun[i];a1,z1=fun[i+1];x=x0+direction*a0;xx=x0+direction*a1
  v=[(x,y0,z0),(xx,y0,z1),(xx,y1,z1),(x,y1,z0),(x,y0,0),(xx,y0,0),(xx,y1,0),(x,y1,0)]
  fs=[(0,1,2,3),(0,4,5,1),(3,2,6,7)]
  if i==len(fun)-2:fs.append((1,5,6,2))
  if direction<0:fs=[tuple(reversed(f)) for f in fs]
  g.add(v,fs,k[i%len(k)])
 g.rod((x0+direction*fun[-1][0],y0,fun[-1][1]),(x0+direction*fun[-1][0],y1,fun[-1][1]),.055,'steel',6)
# D7 two nonvertical opposed 45m launch walls, not a true halfpipe. Source center -220; 8m flat center retained.
# To retain a 4.5m crest and a maximum 45° slope with curved lead-in, each wall needs 9m visual width.
for sign in [-1,1]:
 g=Group();wall(g,-220+sign*4,-165,-120,sign,[(i*.75,4.5*(i/12)**2) for i in range(13)],9,['orange','orange','lightorange'])
 for y in [-164.86,-157.5,-150,-142.5,-135,-127.5,-120.14]:
  for i in range(12):
   a=i*.75;b=(i+1)*.75;x=-220+sign*(4+a);xx=-220+sign*(4+b);z=4.5*(a/9)**2;zz=4.5*(b/9)**2
   g.rod((x,y,z+.016),(xx,y,zz+.016),.017,'darkorange',5)
 g.mesh('launch wall '+('west' if sign<0 else 'east')+' 45m')
g=Group();g.box((-220,-142.5,.013),(8,45,.021),'darkorange');g.mesh('launch channel flat center')
# Facing quarter pipes at exact historical centres; profiles interpreted as launchable visual geometry only.
for x,sg in [(-122,1),(-168,-1)]:
 g=Group();wall(g,x,-213,-199,sg,[(i*.5,5.0*(i/12)**2) for i in range(13)],6,['orange','lightorange','orange']);g.mesh('quarter pipe '+str(x))
g=Group()
# Batched funbox; place four ramp cells around exact 10×10m central platform.
g.box((-145,-206,.90),(10,10,1.8),'darkorange')
for a in range(4):
 u=Vector((math.cos(a*math.pi/2),math.sin(a*math.pi/2),0));v=Vector((-u.y,u.x,0));p=Vector((-145,-206,0))+u*5
 vs=[tuple(p+u*i+v*j+Vector((0,0,z))) for i,j,z in [(0,-5,1.8),(0,5,1.8),(5,5,.008),(5,-5,.008),(0,-5,0),(0,5,0)]]
 g.add(vs,[(0,3,2,1),(0,4,3),(1,2,5)],'orange')
g.mesh('four-ramp funbox')
g=Group()
for y in [-184,-192,-200]:
 g.rod((-208,y,.70),(-188,y,.70),.080,'steel')
 for x in [-207,-198,-189]:g.rod((x,y,.015),(x,y,.68),.060,'steel');g.box((x,y,.03),(.45,.39,.06),'cliff')
g.mesh('three 20m rails')
g=Group();cx,cy=-212,-216
rings=[(0,.02),(8,.02),(8.5,.085),(9,.24),(9.5,.57),(10,1.02),(10.5,1.59),(11,2.20),(11.5,2.86),(12,3.5),(12.45,3.5),(12.45,.005)]
def bp(r,z,i):a=math.tau*i/64;return (cx+r*math.cos(a),cy+r*math.sin(a),z)
for j,((r,z),(q,w)) in enumerate(zip(rings,rings[1:])):
 for i in range(64):g.add([bp(r,z,i),bp(q,w,i),bp(q,w,i+1),bp(r,z,i+1)],[(0,1,2,3)],'floor' if j<2 else 'orange' if j<9 else 'lightorange' if j==9 else 'darkorange')
g.mesh('24m bowl lip centered on source')
g=Group()
for r,z,k in [(3,.061,'cyan'),(2.58,.066,'teal')]:
 vs=[(-106,-143,z)]+[(-106+r*math.cos(i*math.tau/64),-143+r*math.sin(i*math.tau/64),z) for i in range(64)]
 g.add(vs,[(0,i+1,(i+1)%64+1) for i in range(64)],k)
for x in [-107.6,-104.4]:g.box((x,-152,1.27),(.24,.32,2.54),'steel')
g.box((-106,-152,2.36),(4.2,.37,1.52),'steel');g.box((-106,-151.79,2.38),(3.90,.08,1.25),'teal')
g.mesh('source trick start pad and PB board blank static')
def label(n,txt,p,size,angle=0):
 d=bpy.data.curves.new(n,'FONT');d.body=txt;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.008;d.materials.append(M['line']);o=bpy.data.objects.new('HOVER | '+n,d);C.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,angle);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
label('PB board lettering','TRICK SCORE',(-106,-151.73,2.66),.32,math.pi)
label('PB board secondary','PERSONAL BEST',(-106,-151.73,2.20),.21,math.pi)
# Three scene-only markers rank the exact native ramps without inventing catalogue ids.
for y,h in [(-132,2.4),(-143,3.6),(-154,4.8)]:
 g=Group();g.box((-155.5,y+3.55,.55),(.16,1.38,1.0),'steel');g.mesh('lane marker '+str(h))
 label('lane height '+str(h),str(h)+' m',(-155.39,y+3.55,.73),.27,math.pi/2)
(P/'integration.json').write_text(json.dumps({'baseline':'verified Climb/Rock static assembly','source_zone_map_xz':[-234,-100,112,234],'decision':'D7 launch walls + 2.4/3.6/4.8m kickers supersede Round4 blockout heights','lanes':lanes,'launch_wall_length_m':45,'launch_wall_max_design_slope':1,'launch_wall_each_visual_width_m':9,'crest_height_m':4.5,'visual_width_inference':'26m total with 8m center; enlarged versus historic vert section to retain height at <=45°','historical_eye_map':[[-114,1.7,147],[-200,3,140]],'inputs':sources,'scope':'static art only; no runtime, physics, moves, scoring or performance qualification'},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'hover-park-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'hover-park-editable.blend'))
