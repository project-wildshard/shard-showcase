"""Build the reviewed static Pallet Jack mesh from editable geometry."""
from pathlib import Path
import math,bpy,sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory,clear_scene,export
clear_scene()
s=bpy.context.scene
c=bpy.data.collections.new('Band 02 | Pallet Jack study');s.collection.children.link(c);parts=[]
def mat(name,rgb,metal,rough,em=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if em:bs.inputs['Emission Color'].default_value=(*rgb,1);bs.inputs['Emission Strength'].default_value=em
 return m
enamel=mat('PJ | safety orange polyester',(.64,.217,.036),.38,.46)
gold=mat('PJ | baked edge orange',(.82,.407,.088),.37,.41)
steel=mat('PJ | rubbed steel alloy',(.29,.358,.35),.78,.39)
iron=mat('PJ | unpainted graphite',(.057,.076,.077),.63,.48)
tread=mat('PJ | baked rubber soles',(.024,.031,.030),.12,.74)
cyan=mat('PJ | single square cyan eye',(.012,.76,.91),.24,.26,1.95)
gasket=mat('PJ | eye surround',(.025,.31,.325),.50,.34)
amber=mat('PJ | warning cap recycled brass',(.52,.183,.029),.43,.43)
def make(name,verts,faces,mats,ids=None):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);c.objects.link(o);parts.append(o)
 for t in mats:m.materials.append(t)
 if ids:
  for f,i in zip(m.polygons,ids):f.material_index=i
 return o
def prism(name,loc,w,d,h,r,m,a=None,top=1):
 X,Y,Z=w*.5,d*.5,h*.5
 pts=[(-X+r,-Y),(X-r,-Y),(X,-Y+r),(X,Y-r),(X-r,Y),(-X+r,Y),(-X,Y-r),(-X,-Y+r)] if r else [(-X,-Y),(X,-Y),(X,Y),(-X,Y)]
 q=len(pts);vs=[(x*f,y*f,z) for f,z in ((1,-Z),(top,Z)) for x,y in pts]
 fs=[tuple(reversed(range(q))),tuple(range(q,q*2))]+[(i,(i+1)%q,(i+1)%q+q,i+q) for i in range(q)]
 o=make(name,vs,fs,(m,a) if a else (m,),[0,0]+[j%2 for j in range(q)] if a else None);o.location=loc;return o
def cyl(name,a,b,r,material,n=6):
 a,b=Vector(a),Vector(b);l=(b-a).length
 v=[(r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n),z) for z in (-l/2,l/2) for i in range(n)]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 o=make(name,v,f,(material,));o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 return o
prism('Canted main enclosure',(0,0,1.0),1.4,1.8,.80,.19,enamel,gold,.87)
prism('Removable armored lid',(0,.06,1.422),1.27,1.54,.19,.17,enamel,gold,.90)
prism('Gantry chassis sill',(0,0,.596),1.32,1.68,.26,.15,iron,steel)
prism('Trailing underside case',(0,.41,.448),.69,.67,.20,.06,iron)
# Replace a flat orange corner read with shallow cast guards and side ventilation.
for sign in (-1,1):
 for y in (-1,1):
  cap=prism('Four cast corner collars',(sign*.585,y*.675,1.327),.19,.253,.246,0,iron,steel)
  cap.rotation_euler.z=sign*y*.29
  lower=prism('Four bright corner wear plates',(sign*.642,y*.652,.737),.126,.245,.158,0,steel)
  lower.rotation_euler.z=sign*y*.29
 for z in (.92,1.03):
  prism('Shallow side heat vent',(sign*.655,.235,z),.025,.39,.047,0,iron)
for x in (-.41,.41):
 prism('Top steel tie bar',(x,.13,1.526),.074,.90,.036,0,steel)
 prism('Front latch',(x,-.846,1.249),.15,.10,.16,0,iron)
 prism('Rear worklight socket',(x,.832,1.108),.17,.08,.15,0,iron)
for x in (-1,1):
 for y in (-1,1):
  a=(.53*x,.585*y,.614);joint=(.77*x,.681*y,.425);ankle=(.95*x,.805*y,.129)
  cyl('Transverse hinge',(.545*x,.585*y,.57),(.785*x,.585*y,.57),.142,iron)
  cyl('Exposed leg piston',joint,ankle,.062,steel)
  leg=prism('Canted orange sleeve',((joint[0]+ankle[0])/2,(joint[1]+ankle[1])/2,.315),.174,.203,.218,0,enamel,gold)
  leg.rotation_euler=(ankle[1]*-.23,x*.43,0)
  prism('Caster saddle',(.966*x,.826*y,.106),.31,.27,.205,.039,tread,steel,.88)
for x in (-.32,.32):
 prism('Rolled fork heel',(x,-.865,.435),.22,.26,.26,.042,iron)
 stations=((-1.00,.125,.392,.553),(-1.28,.12,.365,.520),(-1.96,.112,.318,.471),(-2.19,.082,.342,.407))
 verts=[(x+dx,y,z) for y,w,l,h in stations for dx,z in ((-w,l),(w,l),(w,h),(-w,h))]
 fs=[(0,1,2,3)];ids=[0]
 for i in range(3):
  k=i*4
  for j in range(4):
   t=(j+1)%4;fs.append((k+j,k+4+j,k+4+t,k+t));ids.append(1 if j==2 else 0)
 fs.append((15,14,13,12));ids.append(1)
 make('Tapered steel fork',verts,[tuple(reversed(f)) for f in fs],(iron,steel),ids)
# Front optics: square opening, dark centered face, one emitter only.
prism('Face plate',(0,-.865,1.002),.577,.095,.54,.056,iron)
prism('Secondary eye recess',(0,-.922,1.002),.348,.052,.345,.038,gasket)
prism('Single square lens',(0,-.952,1.002),.266,.026,.263,.015,cyan)
cyl('Single unlit brass beacon socket',(0,.35,1.506),(0,.35,1.614),.102,amber)
bpy.context.view_layer.update()
tris=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in parts)
assert tris<=900 and len([o for o in parts if o.name.startswith('Tapered steel fork')])==2
allv=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box]
bb=tuple((min(v[i] for v in allv),max(v[i] for v in allv)) for i in range(3));print('PALLET_JACK',len(parts),'PARTS',tris,'TRIS',bb,flush=True)
assert tris==864
export(parts,output_directory()/'wsc-actor-002-pallet-jack-study.glb')
