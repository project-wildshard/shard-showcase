import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;S=bpy.context.scene
C=bpy.data.collections.new('W12 | Range Gate pedestrian landscape');S.collection.children.link(C)
def mat(n,col):
 m=bpy.data.materials.new('RANGE LAND '+n);m.diffuse_color=(*col,1);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*col,1);q.inputs['Roughness'].default_value=.82;return m
M={k:mat(k,c) for k,c in {'earth':(.40,.34,.21),'light':(.50,.43,.32),'slate':(.31,.30,.257),'shadow':(.235,.244,.20),'moss':(.30,.37,.24),'cliff':(.38,.345,.282),'dark':(.034,.049,.047),'timber':(.26,.128,.059),'cedar':(.39,.206,.090),'amber':(.50,.28,.12),'hemp':(.58,.413,.228),'steel':(.075,.11,.112),'teal':(.063,.30,.29),'sand':(.49,.43,.32),'orange':(.64,.26,.068),'darkorange':(.31,.143,.065),'lightorange':(.79,.42,.15),'cyan':(.06,.54,.64),'floor':(.205,.265,.25),'grass':(.28,.36,.20),'palegrass':(.36,.43,.25),'pathstone':(.49,.45,.34),'blueteal':(.09,.32,.31),'verdigris':(.136,.35,.255),'ochre':(.60,.36,.14),'shrub':(.25,.337,.17),'olive':(.32,.40,.18),'line':(.66,.63,.50)}.items()}
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
  o=bpy.data.objects.new('RANGE LAND | '+n,d);C.objects.link(o);return o
def label(n,txt,p,size,angle=0):
 bpy.ops.object.select_all(action='DESELECT')
 d=bpy.data.curves.new(n,'FONT');d.body=txt;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.009;d.materials.append(M['line']);o=bpy.data.objects.new('RANGE LAND | '+n,d);C.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,angle);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
# All additions are scenery only, nonfunctional.
p=Group()
p.box((-53,-119,.006),(78,102,.012),'grass')
p.box((-36,-64,.031),(7.0,8,.02),'pathstone')
p.box((-36,-73,.020),(10,10,.015),'pathstone')
p.box((-53,-80,.020),(66,4,.015),'sand')
p.box((-83,-115,.021),(3.6,68,.022),'sand')
p.box((-50,-148,.020),(69.5,4,.016),'sand')
p.box((-23,-113,.020),(3.6,66,.016),'sand')
# These paths are scenic rather than the historical lanes and remain clear of the retained x=-11 walk.
for x in [-41.25,-30.75]:
 for y in [-76.7,-74.7,-72.7,-70.7]:p.box((x,y,.10),(.37,1.84,.18),'light')
for x in range(-83,-23,3):
 for y in [-82.18,-77.82,-150.17,-145.83]:p.box((x,y,.095),(2.72,.44,.17),'light' if x%2 else 'pathstone')
for x in [-86,-80,-26,-20]:
 for y in range(-144,-85,3):p.box((x,y,.094),(.38,2.72,.16),'light')
p.mesh('green footprint with pedestrian square and curbs')
# Berm is a fictional visual landmark, not a backstop specification. Measured source ground box and 10m peak.
g=Group()
xs=[-92,-90,-86,-81,-75,-67,-60,-52,-44,-36,-28,-21,-17,-14]
heights=[.68,2.0,6.4,8.45,9.35,9.85,10,10,9.9,9.45,8.8,7.15,3.1,.70]
rs=[]
for k,(x,h) in enumerate(zip(xs,heights)):
 wob=.22*math.sin(k*1.71);supp=.16*math.sin(k*.82)
 rs.append([(x,-156,.012),(x,-157.3+wob,h*.22),(x,-158.45+supp,h*.44),(x,-160.55+wob,h*.71),(x,-161.6+supp,h),(x,-163.35+wob,h),(x,-164.45+supp,h*.70),(x,-166.27+wob,h*.36),(x,-168,.012)])
palette=['grass','palegrass','cliff','palegrass','grass','moss','cliff','grass']
for i in range(len(rs)-1):
 for j in range(8):
  a,b=rs[i][j:j+2];c,d=rs[i+1][j:j+2]
  ma=palette[j] if (i*11+j*7)%13>2 else ('moss' if j not in [2,6] else 'shadow')
  g.add([a,b,d,c],[(0,1,2),(0,2,3)],ma)
for k in [0,-1]:
 a=rs[k];g.add(a,[tuple(range(len(a))) if k==0 else tuple(reversed(range(len(a))))],'grass')
g.mesh('south landscape berm measured 78 by 12m crown 10m')
# Low-poly ornamental planting clumps; repeated forms vary in rotation/heights, away from corridor and crest.
g=Group()
def clump(x,y,r,h,idx):
 n=7;v=[]
 for j,(rr,z) in enumerate([(r*.71,.016),(r,h*.43),(r*.65,h*.84),(r*.28,h)]):
  for k in range(n):
   a=k*math.tau/n+idx*.72+j*.15;rad=rr*(.96+.13*math.sin(idx+k*2.1))
   v.append((x+rad*math.cos(a),y+rad*math.sin(a),z))
 for j in range(3):
  for k in range(n):
   q=(k+1)%n;g.add([v[j*n+k],v[j*n+q],v[(j+1)*n+q],v[(j+1)*n+k]],[(0,1,2),(0,2,3)],['olive','shrub','verdigris'][(j+k+idx)%3])
 g.add(v[-n:],[tuple(range(n))],'olive')
for i,(x,y,r,h) in enumerate([(-90,-81,1.2,1.25),(-88,-76,1.2,.85),(-73,-76,1.1,.86),(-64,-86,1.3,1.32),(-57,-87,1.4,1.09),(-44,-86,1.2,1.32),(-29,-85,1.38,1.19),(-18,-83,1.1,.9),(-90,-146,1.36,1.42),(-87,-152,1.11,.85),(-78,-152,1.3,1.05),(-72,-153,1.2,1.1),(-55,-152,1.4,1.2),(-43,-154,1.3,1.27),(-38,-153,1.07,1.15),(-26,-152,1.18,1.16),(-17,-154,1.1,1.06),(-89,-171,1.48,1.12),(-75,-172,1.21,1.33),(-60,-171,1.41,1.25),(-45,-172,1.31,1.24),(-26,-173,1.19,1.09)]):
 clump(x,y,r,h,i)
g.mesh('low profile ornamental planting outside footpaths')
# Inferred quiet garden loops and shaded meadow islands; no historical equipment reconstructed.
g=Group()
def ell(x,y,rx,ry,z,k,n=28):
 v=[(x,y,z)]+[(x+rx*math.cos(math.tau*i/n),y+ry*math.sin(math.tau*i/n),z) for i in range(n)]
 g.add(v,[(0,1+i,(i+1)%n+1) for i in range(n)],k)
for x,y,a,b in [(-65,-113,10.2,7.8),(-40,-129,8.7,6.8),(-43,-102,6.9,5.8)]:
 ell(x,y,a,b,.016,'palegrass');ell(x,y,a*.89,b*.88,.02,'moss')
for a,b in [((-36,-80),(-42,-96)),((-42,-107),(-55,-115)),((-63,-122),(-65,-146)),((-22,-119),(-33,-127)),((-47,-134),(-60,-143))]:
 p=Vector((*a,.028));q=Vector((*b,.028));u=(q-p).normalized();v=Vector((-u.y,u.x,0))
 g.box((p+q)/2,((q-p).length,2.12,.016),'pathstone',u,v)
g.mesh('inferred garden loop and three planted meadow islands')
g=Group()
def canopy(x,y,h,r,idx):
 g.rod((x,y,.016),(x+.21,y-.11,h*.73),.16+idx*.011,'timber',7)
 for j,(dx,dy,z,rr) in enumerate([(-.48,-.08,h*.72,.66),(0,.27,h*.83,1.0),(.67,.17,h*.72,.74),(.16,-.47,h*.94,.55)]):
  v=[];n=8
  for k,(rel,rad) in enumerate([(-.46,.53),(-.16,.96),(.25,1),(.52,.57)]):
   for l in range(n):
    a=l*math.tau/n+.25*k+.71*j;sc=rr*r*rad*(.925+.15*math.sin(l*2.67+j+k*.7))
    v.append((x+dx+sc*math.cos(a),y+dy+sc*math.sin(a),z+rr*r*rel))
  for k in range(3):
   for l in range(n):
    b=(l+1)%n;g.add([v[k*n+l],v[k*n+b],v[(k+1)*n+b],v[(k+1)*n+l]],[(0,1,2),(0,2,3)],['shrub','olive','palegrass'][(k+idx+j+l)%3])
  g.add(v[-n:],[tuple(range(n))],'olive')
for i,(x,y,h,r) in enumerate([(-67,-112,5.1,1.93),(-62,-115,4.7,1.64),(-40,-129.5,5.7,2.11),(-36,-131,4.6,1.65),(-42.8,-102,4.9,1.86)]):
 canopy(x,y,h,r,i)
for x,y in [(-70,-115),(-58,-112),(-42,-134),(-45,-106)]:
 g.box((x,y,.29),(2.08,.53,.56),'light');g.box((x,y,.59),(1.81,.47,.13),'cedar')
g.mesh('five sculpted shade trees and seat blocks')
# Garden wayfinding and modest timber/stone accents; no target or equipment objects.
g=Group()
for x,y in [(-44,-69.2),(-26,-69.2),(-86,-79.6),(-21,-147.8)]:
 for dx in [-1.02,1.02]:g.box((x+dx,y,1.11),(.18,.21,2.22),'timber')
 g.box((x,y,1.74),(2.78,.23,.73),'blueteal')
for x,y in [(-75,-83.6),(-60,-83.6),(-47,-83.6),(-34,-83.6),(-78,-152),(-48,-152)]:
 for dx in [-.77,.77]:g.box((x+dx,y,.23),(.18,.48,.46),'steel')
 g.box((x,y,.5),(1.92,.51,.17),'cedar')
g.mesh('wood and stone pedestrian furnishings')
label('gate path study lettering','SOUTH WALK',(-44,-69.33,1.75),.27)
label('garden study lettering','GARDEN PATH',(-26,-69.33,1.75),.25)
label('edge path study lettering','WEST WALK',(-86,-79.47,1.75),.25,math.pi)
label('yard wayfinding lettering','YARD WALK',(-21,-147.67,1.75),.25,math.pi)
(P/'integration.json').write_text(json.dumps({'baseline':'verified Physics Yard editable static scene','source':'Round 5 layout and Round 4 lab camera/terrain height, commit ce1cf050b3','district_map_xz':[-92,-14,68,170],'landscape_berm_map_xz':[-92,-14,156,168],'berm_visual_crown_m':10,'preserve_east_walk_center_x':-11,'pinned_eye_map_xyz':[-37,1.7,72],'pinned_target_map_xyz':[-80,1.2,125],'vfov':80,'scope':'fictional pedestrian scenery only; no equipment, range functional design or gameplay','donors':'none; all geometry procedural static additions'},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'range-landscape-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'range-landscape-editable.blend'))
