import bpy,math,json,hashlib,re
from pathlib import Path
from mathutils import Vector
P=OUT; S=bpy.context.scene
lots=json.loads((P/'town-lots.json').read_text())
def extent(row):
 return row['x0'],row['x1'],-row['z1'],-row['z0']
removed=[]
for o in list(S.objects):
 if o.type!='MESH':continue
 n=o.name
 match=re.search(r'R02 street grove (\d+)',n)
 if match and int(match[1])<6:
  x,y=[(-46,30),(-46,53),(-85,40),(-105,40),(-84,24),(-120,57)][int(match[1])]
  if not any(a-.65<x<b+.65 and c-.65<y<d+.65 for a,b,c,d in map(extent,lots)):match=None
 else:match=None
 if match or n.startswith(('North town existing house','R02 house-to-alley walkway','ZIP | Main Street adjacent','ZIP | Main Street window rhythm')):
  removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
C=bpy.data.collections.new('W0b | whole town scoped static art');S.collection.children.link(C)
def mat(n,c,m=0):
 a=bpy.data.materials.new(n);a.diffuse_color=(*c,1);a.use_nodes=True;q=a.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=(*c,1);q.inputs['Metallic'].default_value=m;q.inputs['Roughness'].default_value=.7;return a
spec={'sand':(.49,.36,.22),'lime':(.65,.51,.35),'clay':(.55,.30,.16),'sage':(.31,.38,.31),'gold':(.67,.42,.15),'trim':(.72,.57,.39),'wood':(.18,.083,.041),'roof':(.28,.105,.046),'roof2':(.095,.21,.21),'glass':(.055,.18,.20),'iron':(.076,.101,.105),'stone':(.42,.42,.35),'path':(.43,.36,.27),'plaza':(.63,.55,.40),'ochre':(.67,.255,.047),'teal':(.042,.36,.38),'ivory':(.85,.74,.53),'cyan':(.075,.56,.61)}
M={k:mat('W0b '+k,v,.22 if k in ['iron','gold'] else 0) for k,v in spec.items()}
class Group:
 def __init__(self):self.v=[];self.f=[];self.ms=[]
 def shape(self,vs,fs,ma):
  i=len(self.v);self.v.extend(vs);self.f.extend(tuple(i+j for j in f) for f in fs);self.ms += [ma]*len(fs)
 def box(self,x,y,z,w,d,h,ma):
  self.shape([(x+i*w/2,y+j*d/2,z+k*h/2) for k in [-1,1] for j in [-1,1] for i in [-1,1]],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],ma)
 def frustum(self,x,y,z0,z1,w0,w1,d0,d1,ma):
  self.shape([(x+i*w/2,y+j*d/2,z) for z,w,d in [(z0,w0,d0),(z1,w1,d1)] for j in [-1,1] for i in [-1,1]],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],ma)
 def gable(self,x,y,z,w,d,h,ma):
  a=w/2;b=d/2
  self.shape([(x-a,y-b,z),(x+a,y-b,z),(x-a,y+b,z),(x+a,y+b,z),(x-a,y,z+h),(x+a,y,z+h)],[(0,1,5,4),(4,5,3,2),(0,4,2),(1,3,5),(0,2,3,1)],ma)
 def mesh(self,name):
  d=bpy.data.meshes.new(name);d.from_pydata(self.v,[],self.f);keys=list(dict.fromkeys(self.ms))
  for ma in keys:d.materials.append(M[ma])
  for f,k in zip(d.polygons,self.ms):f.material_index=keys.index(k)
  o=bpy.data.objects.new('TOWN | '+name,d);C.objects.link(o);return o
def label(n,txt,pos,size,rot):
 d=bpy.data.curves.new(n,'FONT');d.body=txt;d.align_x='CENTER';d.align_y='CENTER';d.size=size;d.extrude=.008;d.materials.append(M['ivory'])
 o=bpy.data.objects.new('TOWN | '+n,d);C.objects.link(o);o.location=pos;o.rotation_euler=rot;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
# Rectangular plans remain exact. Details kept inside lot; window rows and trims repeat one grammar.
def mass(row,i):
 a,b,c,d=extent(row);x=(a+b)/2;y=(c+d)/2;w=b-a;dep=d-c;h=row['h'];k=row['kind'];g=Group()
 body=['lime','sand','clay','sage'][i%4] if k=='house' else ('sage' if k=='tolet' else 'lime')
 g.box(x,y,h/2,w-.8,dep-.8,h,body);g.box(x,y,.32,w-.63,dep-.63,.64,'stone')
 for z in [.64,h-.2]:g.box(x,y,z,w-.62,dep-.62,.17,'trim')
 if row.get('roof',False):g.gable(x,y,h-.01,w-.2,dep-.2,min(2.75,dep*.30),'roof' if i%4 else 'roof2')
 else:
  g.box(x,y,h+.15,w-.22,dep-.22,.3,'roof2' if k=='gatehouse' else 'roof')
  for xx in [a+.22,b-.22]:g.box(xx,y,h+.47,.23,dep-.22,.49,'trim')
  for yy in [c+.22,d-.22]:g.box(x,yy,h+.47,w-.22,.23,.49,'trim')
 # Center all main street shops toward street; gold signs are physical geometry.
 for side in [-1,1]:
  yf=y+side*(dep/2-.40)
  g.box(x,yf+side*.09,h*.50,w-.85,.16,.14,'wood') if k=='house' else None
  for j in range(max(2,round(w/3.5))):
   wx=a+1.4+(w-2.8)*j/max(1,max(2,round(w/3.5))-1)
   for fl in range(1,max(2,round(h/3.1))):
    z=1.37+fl*2.69
    if z>h-1.0:continue
    g.box(wx,yf+side*.068,z,1.28,.20,1.56,'trim');g.box(wx,yf+side*.177,z,.83,.05,1.11,'glass')
    g.box(wx,yf+side*.212,z,.05,.05,1.10,'wood')
    if k=='house':
     for off in [-.7,.7]:g.box(wx+off,yf+side*.13,z,.18,.15,1.29,'roof2')
    g.box(wx,yf+side*.15,z-.81,1.49,.34,.12,'stone')
  if k=='house':
   g.box(x,yf+side*.04,1.11,1.49,.16,2.22,'wood');g.box(x,yf+side*.14,.15,1.8,.35,.3,'stone')
 for side in [-1,1]:
  xx=x+side*(w/2-.4)
  for yy in [c+dep*.30,c+dep*.70]:
   for z in [4.05,6.75,9.45]:
    if z>h-1:continue
    g.box(xx+side*.075,yy,z,.18,1.28,1.54,'trim');g.box(xx+side*.178,yy,z,.05,.83,1.14,'glass')
 if k in ['shop','tolet']:
  sg=-1 if y>0 else 1;f=y+sg*(dep/2-.40)
  g.box(x,f+sg*.05,1.46,w*.59,.18,2.75,'wood');g.box(x,f+sg*.172,1.65,w*.54,.09,1.84,'glass')
  for dx in [-w*.17,0,w*.17]:g.box(x+dx,f+sg*.23,1.63,.11,.07,1.90,'wood')
  # Folded canopy front face is set inside lot, no narrowing of the 12m street.
  g.box(x,f-sg*.41,3.21,w*.81,1.49,.22,'teal' if k=='shop' else 'ochre')
  g.box(x,f+sg*.26,3.06,w*.81,.17,.32,'teal' if k=='shop' else 'ochre')
  g.box(x,f+sg*.21,4.18,w*.76,.19,.75,'wood')
  label(row['label']+' fascia '+str(i),row['label'],(x,f+sg*.32,4.18),.63,(math.pi/2,0,0 if sg==-1 else math.pi))
 return g.mesh(('LOT %02d '%i)+k)
for i,l in enumerate(lots,1):
 if l['kind'] not in ('stable','zip'):mass(l,i)
g=Group()
# Inferred warm district substrate, below existing lanes; separately add missing lengths only.
g.box(-68,0,.004,120,120,.016,'sand')
g.box(-36,0,.045,40,40,.09,'plaza')
# Unchanged north fragment begins at y20, and Main Street occupies y[-6,6].
for a,b in [(-59,-6),(6,20)]:g.box(-95,(a+b)/2,.035,8,b-a,.07,'path')
for a,b in [(-127,-99),(-91,-42)]:g.box((a+b)/2,-34,.036,b-a,4,.072,'path')
g.box(-36,-39.5,.035,12,39,.07,'path');g.box(-12,0,.041,8,12,.082,'plaza')
# Paving paths across plaza visual grid. Tiny lines lie above plaza slab, not coincident.
for yy in [-19,-15,-11,-7,-3,1,5,9,13,17,19]:g.box(-36,yy,.093,39.2,.065,.011,'trim')
for xx in range(-54,-17,4):g.box(xx,0,.094,.045,39.2,.010,'trim')
# Cut-stone lane edges and staggered seams give the historic eye-height frame depth cues.
for side in [-1,1]:
 for i in range(35):
  x=-125.75+2*i
  g.box(x,side*5.55,.072,1.96,.76,.035,('stone','trim','stone')[i%3])
 for i in range(33):
  x=-124.5+2*i+(0.37 if side>0 else 0)
  g.box(x,side*3.88,.059,.045,2.4,.009,'trim')
for i in range(33):
 x=-124.5+2*i
 g.box(x,0,.059,.043,2.7,.009,'trim')
g.mesh('source ground plane and added circulation')
g=Group()
# Preserve existing north/west spans. New East and South curtain walls with 12m gaps.
for a,b in [(-128,-101),(-89,-42),(-30,-8)]:
 g.box((a+b)/2,-60,2.5,b-a,1.2,5,'lime');g.box((a+b)/2,-60,5.11,b-a,1.42,.22,'trim')
for a,b in [(-60,-6),(6,60)]:
 g.box(-8,(a+b)/2,2.5,1.2,b-a,5,'lime');g.box(-8,(a+b)/2,5.11,1.42,b-a,.22,'trim')
for n,x,y,rotate in [('PARK GATE',-95,-60,False),('RANGE GATE',-36,-60,False),('EAST GATE',-8,0,True)]:
 for side in [-1,1]:
  px=x if rotate else x+side*6.9;py=y+side*6.9 if rotate else y
  g.box(px,py,3.52,1.8,1.8,7.04,'lime');g.box(px,py,7.02,2.05,2.05,.34,'trim')
 g.box(x,y,6.62,1.75 if rotate else 12.2,12.2 if rotate else 1.75,.75,'wood')
 if rotate:label(n,n,(x-.89,y,6.60),.60,(math.pi/2,0,-math.pi/2))
 else:label(n,n,(x,y-.89,6.60),.60,(math.pi/2,0,0))
g.mesh('east south walls and three gates')
# Plaza anchors per lab.js; no actor/collision data.
g=Group();g.box(-34,0,.65,5,5,1.3,'stone');g.box(-34,0,1.35,3.2,3.2,.38,'gold');g.frustum(-34,0,1.54,21.3,2.65,.90,2.65,.90,'lime');g.frustum(-34,0,21.3,22,.90,.08,.90,.08,'cyan')
for dx in [-.46,.46]:g.frustum(-34+dx,0,1.55,9.0,.19,.13,2.74,2.25,'gold')
for z,w in [(2,2.85),(8.85,2.08),(15.7,1.46),(21.15,1.06)]:
 g.box(-34,0,z,w,w,.21,'gold' if z>2 else 'ochre')
g.mesh('22m obelisk source landmark')
g=Group()
for x,y,w,title,sg in [(-36,17,6,'QUEST BOARD',-1),(-26,-17,6,'CONTRACTS',1),(-42,-18,10,'TROPHIES',1),(-54,-12,4,'FEATS',1)]:
 for xx in [x-w*.40,x+w*.40]:g.box(xx,y,1.59,.28,.40,3.18,'wood')
 g.box(x,y,2.15,w,.42,2.31,'wood');g.box(x,y+sg*.23,2.18,w-.33,.05,1.97,'ochre' if title=='QUEST BOARD' else 'teal')
 label(title,title,(x,y+sg*.29,2.86),.46,(math.pi/2,0,0 if sg==-1 else math.pi))
 if title=='TROPHIES':
  for j in range(12):g.box(x-3.75+(j%6)*1.5,y+sg*.28,1.58+(.68 if j<6 else 0),.57,.06,.53,'trim')
for i,(x,y) in enumerate([(-24,7),(-24,-7),(-48,-7)]):
 g.box(x,y,.58,3.2,1.8,1.15,'wood');g.box(x,y,1.21,3.45,2,.15,'trim')
 for xx in [x-1.5,x+1.5]:
  for yy in [y-.86,y+.86]:g.box(xx,yy,1.95,.13,.13,1.90,'wood')
 for j in range(7):g.box(x+(j-3)*.53,y,2.92,.53,2.54,.22,('ochre','ivory')[(i+j)%2])
for x,y in [(-54,18),(-18,18),(-54,-18),(-18,-18)]:
 g.box(x,y,2.2,.23,.23,4.4,'iron');g.box(x,y,4.36,.62,.62,.58,'gold');g.box(x,y,4.60,.77,.77,.16,'iron')
g.mesh('plaza four stands three stalls and lamps')
(P/'integration.json').write_text(json.dumps({'removed_placeholder_meshes':removed,'source':'ce1cf050b3 round4 townPlan seed31','new_lots':42,'preserved_lots':['stable','zip'],'town_m':[120,120],'plaza_m':[40,40],'historical_street_nominal_m':72,'placed_existing_street_box_m':71,'status':'Static art WIP; no gameplay, performance, new catalogue IDs, or production claims'},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'whole-town-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'whole-town-editable.blend'))
