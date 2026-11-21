import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector, Matrix
P=OUT;P.mkdir(parents=True,exist_ok=True)
W=COMPONENTS
S=bpy.context.scene;base={o.name for o in S.objects if o.type=='MESH'}
prefixes=('MODULE-001','MODULE-008','PROP-035','PROP-033','Illustrative roof tie-down','W08 illustrative cable')
with bpy.data.libraries.load(str(W),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith(prefixes)]
C=bpy.data.collections.new('West zip / retained W08 and inferred context');S.collection.children.link(C)
bpy.ops.object.select_all(action='DESELECT')
for o in dst.objects:C.objects.link(o)
bpy.context.view_layer.update()
for o in dst.objects:
 if o.name.startswith('MODULE-008'):
  origin=Vector((-115,16.5,11.6));yaw=-.17849229276180267
  T=Matrix.Translation(origin)@Matrix.Rotation(yaw,4,'Z')
  o.matrix_world=T@Matrix.Diagonal((1/1.55,1/1.7,1,1))@T.inverted()@o.matrix_world
 if o.type=='CURVE':
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
def material(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);return m
M=[material('ZIP limestone',(.57,.47,.32)),material('ZIP lintel stone',(.71,.63,.44)),material('ZIP graphite',(.09,.14,.15)),material('ZIP town path',(.52,.45,.32)),material('ZIP painted cyan',(.05,.48,.57)),material('ZIP timber',(.24,.12,.065)),material('ZIP muted terracotta',(.39,.16,.08))]
ground=bpy.data.objects.get('WIP precinct ground');assert ground
def mesh(n,vs,fs,mat):
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.materials.append(mat);o=bpy.data.objects.new('ZIP | '+n,d);C.objects.link(o);return o
def box(n,p,d,m):
 x,y,z=p;a,b,c=[i/2 for i in d];vs=[(x+i*a,y+j*b,z+k*c) for k in [-1,1] for j in [-1,1] for i in [-1,1]]
 return mesh(n,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
def beam(n,a,b,d,m):
 a,b=Vector(a),Vector(b);o=box(n,(0,0,0),(d,d,(b-a).length),m);o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def hook(n,x,y,z):
 bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=6,location=(x,y,z),major_radius=.48,minor_radius=.08,rotation=(math.pi/2,0,math.pi/4));o=bpy.context.object;o.name='ZIP | '+n;o.data.materials.append(M[4])
box('West ground extension (seam y15)',(-122,-22.5,-.35),(250,75,.7),ground.data.materials[0])
# North-wall lower endpoint is unchanged. Exact x=-128, split around West Gate at Z=0.
for a,b in [(-60,-6),(6,59.35)]:
 box('West curtain wall',(-128,(a+b)/2,2.5),(1.3,b-a,5),M[0]);box('West curtain coping',(-128,(a+b)/2,5.12),(1.5,b-a,.24),M[1])
for y in [-6.8,6.8]:
 box('West Gate pier',(-128,y,3),(2.3,1.6,6),M[0]);box('West Gate cap',(-128,y,6.13),(2.5,1.85,.26),M[1])
box('West Gate beam',(-128,0,5.83),(1.6,12,.65),M[5])
# Main Street reference x[-127,-56], y[-6,6]; approach abuts at x=-127.
box('Main Street measured section',(-91.5,0,.028),(71,12,.056),M[3]);box('West Gate exterior approach',(-138.5,0,.028),(23,12,.056),M[3])
# Authoritative lot[-124,-106]x[7,26], nominal roof12. Local cap rests within rooftop.
box('Zip House full measured mass',(-115,16.5,5.85),(18,19,11.7),M[0]);box('Zip House rooftop plane',(-115,16.5,11.85),(18,19,.3),M[1])
# W08 cyan cap bottom at11.6; shift +.42 to put its local deck just above nominal roof.
for o in dst.objects:
 if o and o.name.startswith('MODULE-008'):o.location.z+=.42
 if o and o.name.startswith('PROP-035'):o.location.z+=.42
for z in [1.3,4.15,7.65,11.4]: box('Zip House street cornice',(-115,7.04,z),(18.22,.24,.24),M[1])
for x in [-121,-117,-113,-109]:
 for z in [3,6.1,9.15]:
  box('Zip House framed window',(x,6.91,z),(1.6,.18,1.9),M[5]);box('Zip House recessed glass',(x,6.80,z),(1.24,.09,1.52),M[4]);box('Zip House sill',(x,6.74,z-.92),(1.8,.39,.13),M[1])
box('Zip House street doorway',(-115,6.78,1.46),(2.65,.4,2.92),M[5]);box('Zip House lintel',(-115,6.59,3.18),(4.0,.5,.40),M[4])
# Existing northern context remains; low-mesh indicative frontage only, no full town claim.
for x,y,w in [(-111,-12,13),(-81,-12,12),(-81,12,12),(-64,13,13),(-64,-13,13)]:
 box('Main Street adjacent frontage WIP',(x,y,3.9),(w,11,7.8),M[0]);box('Main Street adjacent roof WIP',(x,y,7.93),(w+.6,11.6,.26),M[6]);f=y-math.copysign(5.54,y)
 for dx in [-3,0,3]:box('Main Street window rhythm',(x+dx,f,5.15),(1.5,.18,1.7),M[5])
# Two entry poles and 28m mast per GRAPPLE source; tank is existing hook3, tower hook5.
for x,y,h,n in [(-150,44,12,'Hook 1 pole'),(-170,68,16,'Hook 2 pole'),(-200,68,28,'Hook 4 mast')]:
 box(n+' base',(x,y,.22),(2.9,2.9,.44),M[1]);box(n+' stem',(x,y,(h-.5)/2),(.42,.42,h-.5),M[2]);hook(n,x,y,h)
 for dx in [-1.1,1.1]:beam(n+' base brace',(x+dx,y,.4),(x,y,min(5,h-2)),.16,M[2])
hook('Hook 5 tower proxy',-214.5,34,45.8)
# Tank ladder on west face (inferred), preserve bridge and roof entry.
for yy in [103.55,104.45]:box('Tank ladder stringer',(-222.30,yy,9.2),(.12,.12,18.4),M[2])
for k in range(50):box('Tank ladder rung',(-222.30,104,.36+k*.36),(.10,.96,.08),M[2])
# Static visual tie near launch, without moving cable's snap coordinate.
box('Summit launch terminal bracket',(-212.26,34.04,44.70),(.55,.5,.43),M[2])
# Capture exact curve endpoint/wall point analytically; existing W08 curve authored to this rule.
A=Vector((-212,34,45));B=Vector((-115,16.5,14));t=84/97
cross=A.lerp(B,t);cross.z-=4*1.2*t*(1-t)
(P/'manifest.json').write_text(json.dumps({'baseline':'verified shared-roof junction','generated_components_sha256':hashlib.sha256(W.read_bytes()).hexdigest(),'anchors_map':[[-212,45,-34],[-115,14,-16.5]],'span_plan_m':math.hypot(97,17.5),'straight_span_m':(B-A).length,'wall_crossing_blender':list(cross),'wall_coping_top_m':5.24,'zip_house_footprint_map':[-124,-106,-26,-7],'nominal_roof_m':12,'tower_source_center_map':[-212,-34],'tower_authored_assembly_offset_m':6.05,'tower_decoration_max_z_m':50.42,'inferred':['tower retained W08 launch alignment offset','West wall/gate dressing','tank ladder','roof/civic dressing','1.2 m cable sag','hook art proxies'],'scope':'static art; no physics/collision/gameplay/performance claims'},indent=2))
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-zip-route-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-zip-route-editable.blend'))
