import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;S=bpy.context.scene
C=bpy.data.collections.new('W0a | West arrival and perimeter static orientation');S.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new('WEST ORIENT '+n);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=.82;return m
M={k:mat(k,c) for k,c in {'earth':(.40,.34,.21),'light':(.50,.43,.32),'slate':(.31,.30,.257),'shadow':(.235,.244,.20),'moss':(.30,.37,.24),'cliff':(.38,.345,.282),'dark':(.034,.049,.047),'timber':(.26,.128,.059),'cedar':(.39,.206,.090),'amber':(.50,.28,.12),'hemp':(.58,.413,.228),'steel':(.075,.11,.112),'teal':(.063,.30,.29),'sand':(.49,.43,.32),'orange':(.64,.26,.068),'darkorange':(.31,.143,.065),'lightorange':(.79,.42,.15),'cyan':(.06,.54,.64),'floor':(.205,.265,.25),'grass':(.28,.36,.20),'palegrass':(.36,.43,.25),'pathstone':(.49,.45,.34),'blueteal':(.09,.32,.31),'verdigris':(.136,.35,.255),'ochre':(.60,.36,.14),'asphalt':(.295,.319,.307),'asphaltlight':(.337,.350,.326),'yellow':(.64,.45,.19),'orangebrick':(.53,.263,.147),'stonecap':(.638,.503,.328),'shrub':(.25,.337,.17),'olive':(.32,.40,.18),'line':(.66,.63,.50)}.items()}
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
  o=bpy.data.objects.new('WEST ORIENT | '+n,d);C.objects.link(o);return o
def label(n,txt,p,size,angle=0):
 bpy.ops.object.select_all(action='DESELECT')
 d=bpy.data.curves.new(n,'FONT');d.body=txt;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.009;d.materials.append(M['line']);o=bpy.data.objects.new('WEST ORIENT | '+n,d);C.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,angle);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
# No inherited mesh edits. Fill precisely at the retained ground tile limits.
p=Group()
p.box((-248.5,0,-.35),(3,500,.7),'grass')
p.box((-123.5,247.5,-.35),(247,5,.7),'grass')
p.box((-123.5,-249,-.35),(247,2,.7),'grass')
o=p.mesh('cell edge ground stitch only');o.data.materials[0]=bpy.data.objects['WIP precinct ground'].data.materials[0]
# West Avenue: source 12m, tapers into an 8m edge throat inside the cell.
g=Group()
def slab(x0,x1,y0,y1,z,k):g.box(((x0+x1)/2,(y0+y1)/2,z*.5),(x1-x0,y1-y0,z),k)
def trapezoid(x0,x1,a,b,z,k):
 g.add([(x0,-a,z),(x1,-b,z),(x1,b,z),(x0,a,z)],[(0,1,2,3)],k)
for sign in [-1,1]:
 y0,y1=sorted([237*sign,247*sign])
 slab(-247,-8,y0,y1,.028,'asphalt')
# Orthogonal ring stops at edge of top/bottom band; junction remains walkable scene art.
for a,b in [(-237,-6),(6,237)]:slab(-247,-237,a,b,.028,'asphalt')
trapezoid(-250,-247,4,4,.042,'asphaltlight')
trapezoid(-247,-237,4,6,.042,'asphalt')
slab(-237,-150,-6,6,.048,'asphalt')
slab(-150,-128,-6,6,.043,'asphaltlight') # under inherited 0.056m apron; no coplanarity
for y in [-6.74,6.74]:
 for x in range(-233,-152,4):
  g.box((x,y,.089),(3.65,.46,.14),'stonecap' if x%3 else 'asphaltlight')
for y in [-5.62,5.62]:
 for x in range(-231,-153,5):g.box((x,y,.053),(2.75,.065,.009),'yellow')
for x in range(-229,-152,9):g.box((x,0,.053),(2.75,.09,.009),'yellow')
# Asphalt fades into the pre-existing lighter Town-facing apron through a narrow tonal transition.
for i in range(6):
 x=-154.15+i*.62;g.box((x,0,.049+i*.0004),(.59,11.83,.009),['asphalt','asphaltlight'][1 if i>=3 else 0])
# Understated verge edges define the scale, outside the 12m arrival.
for x in range(-232,-157,7):
 for y in [-7.5,7.5]:g.box((x,y,.009),(6.50,1.10,.017),'grass' if x%2 else 'palegrass')
g.mesh('west avenue and in-cell perimeter asphalt')
# West wall and West portions of north/south walls only, no East side or seam work.
g=Group()
def wall(x,y,L,vertical):
 d=(1,L,4.84) if vertical else (L,1,4.84)
 g.box((x,y,2.42),d,'orangebrick')
 for z in [.32,2.38,4.70]:
  if vertical:g.box((x+.041,y,z),(.98,L-.05,.15),'stonecap' if z>2 else 'darkorange')
  else:g.box((x,y-math.copysign(.043,y),z),(L-.05,.98,.15),'stonecap' if z>2 else 'darkorange')
for a,b in [(-249,-4),(4,249)]:wall(-249.5,(a+b)/2,b-a,True)
for y in [-249.5,249.5]:wall(-126.5,y,245,False)
# 3m square pylons with inner faces at +/-4; decorative coursing remains inside cell and clear of the aperture.
for y in [-5.5,5.5]:
 g.box((-248.5,y,4.5),(3,3,9),'darkorange')
 for z in [.5,2.9,5.65,8.87]:g.box((-248.47,y,z),(2.99,2.98,.21),'stonecap')
 g.box((-247.87,y,7.1),(1.1,1.98,1.45),'blueteal')
# Low exterior benches at the exact two vista coordinates, not pickups or runtime points.
for y in [-229,229]:
 g.box((-229,y,.042),(5.6,5.6,.035),'sand')
 for dy in [-1.5,1.5]:g.box((-231,y+dy,.30),(.63,.75,.51),'stonecap')
 g.box((-231,y,.62),(.52,3.1,.15),'cedar')
 g.box((-228.0,y+2.1,.57),(.54,.58,1.1),'stonecap')
g.mesh('west perimeter walls 8m throat and two vista corners')
# Nearby paving and landscape marker posts in safe verges; nothing across established routes.
g=Group()
for x,y in [(-238,8.6),(-171,7.8),(-165,-7.8)]:
 for yy in [y-.72,y+.72]:g.box((x,yy,1.52),(.19,.19,3.04),'timber')
 g.box((x,y,2.14),(.23,2.28,.91),'blueteal')
for i,(x,y) in enumerate([(-242,-13),(-240,14),(-235,-15),(-235,15),(-210,-11),(-209,11),(-183,-11),(-177,11),(-161,-11),(-239,-221),(-238,221),(-228,222),(-230,-222)]):
 for j in range(5):
  a=j*math.tau/5.; r=.43+(i%3)*.09;z=.40+(i%4)*.13
  g.rod((x+.17*math.cos(a),y+.17*math.sin(a),.018),(x+r*math.cos(a),y+r*math.sin(a),z),.07,'olive',5)
g.mesh('inferred restrained west-verge wayfinding')
label('west avenue wayfinding','WEST AVENUE',(-238.13,8.6,2.17),.25,-math.pi/2)
label('town direction wayfinding','TOWN',(-171.13,7.8,2.17),.43,-math.pi/2)
label('town lower landscape landmark','WEST GATE',(-165.13,-7.8,2.17),.32,-math.pi/2)
(P/'integration.json').write_text(json.dumps({'baseline':'exact Range Gate pedestrian landscape','source':'Round5 layout.js + lab.js buildGround() at ce1cf050b3; W0a west entry and W9b west corner vistas','west_avenue_map_xz':[-250,-128,-6,6],'throat_x_m':-248.5,'clear_throat_width_m':8,'west_perimeter_asphalt_x':[-247,-237],'west_vista_map_xz':[[-229,-229],[-229,229]],'baseline_apron_overlap_policy':'new road surface only below retained portion x[-150,-128]; preserved apron masks it','partial_perimeter':'north and south western spans only; no east seam additions','viable_footprint_labels':['Town','Range landscape only','Physics Yard','Riding Course','Paddock','Movers','Grapple','Climb','Rock','Hover'],'static_only':True},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-orientation-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-orientation-editable.blend'))
