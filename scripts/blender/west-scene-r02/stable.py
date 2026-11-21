import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
P=OUT;P.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
M={}
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 s=m.node_tree.nodes['Principled BSDF'];s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=.74;s.inputs['Metallic'].default_value=metal;M[n]=m
for n,c in [('plaster',(.72,.66,.51)),('stone',(.39,.36,.28)),('cap',(.64,.58,.44)),('timber',(.19,.10,.045)),('cedar',(.35,.20,.085)),('teal',(.045,.22,.21)),('rooflight',(.06,.28,.26)),('cream',(.88,.81,.62)),('dark',(.035,.055,.055)),('iron',(.09,.105,.10)),('glass',(.10,.18,.19))]:mat(n,c)
def box(n,p,d,m,b=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[m])
 if b:
  mod=o.modifiers.new('Dressed edge','BEVEL');mod.width=b;mod.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def beam(n,a,b,w,h,m='timber'):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(w,h,(b-a).length),m,.018);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(M[m]);return o
def sign(n,txt,p,size,rot):
 bpy.ops.object.text_add(location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.body=txt;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size;o.data.extrude=.008;o.data.bevel_depth=.002;o.data.materials.append(M['cream']);bpy.ops.object.convert(target='MESH');return bpy.context.object
# Source lot exact 18 x 18m. Architecture is an inferred art study, not recovered design.
# Deep open arcade faces the paddock (+Y); western side door faces Stable Lane.
for x in [-27.6,-10.4]:
 for ya,yb in [(38,46.2),(49.8,54.8)] if x< -20 else [(38,54.8)]:
  box('Stable stone plinth',(x,(ya+yb)/2,.48),(.6,yb-ya,.96),'stone')
  box('Stable lime plaster wall',(x,(ya+yb)/2,3.1),(.5,yb-ya,4.3),'plaster')
box('Stable rear plinth',(-19,38.3,.48),(17.4,.6,.96),'stone')
box('Stable rear plaster',(-19,38.3,3.1),(17.4,.5,4.3),'plaster')
# Back wall of sheltered arcade with three deep dark stalls, timber split doors.
box('Arcade rear plaster',(-19,50.4,3.1),(17.2,.35,4.3),'plaster')
for x in [-24.7,-19,-13.3]:
 box('Stall shadow recess',(x,50.65,2.25),(3.8,.18,3.35),'dark')
 box('Stall split lower door',(x,50.82,1.05),(3.5,.13,1.9),'teal')
 for xx in [x-1.85,x+1.85]:box('Stall door jamb',(xx,50.9,2.1),(.16,.2,4.05),'timber')
 box('Stall lintel',(x,50.9,4.1),(3.9,.23,.25),'timber')
 for off in [-1.45,-.73,0,.73,1.45]:box('Door vertical board',(x+off,50.91,1.05),(.025,.035,1.8),'rooflight',.005)
 beam('Split door diagonal',(x-1.6,50.97,.3),(x+1.6,50.97,1.8),.1,.08,'cedar')
 box('Cream stall numeral plaque',(x,50.95,3.65),(.52,.05,.4),'teal')
 sign('Stall number',str([-24.7,-19,-13.3].index(x)+1),(x,51,3.65),.29,(math.pi/2,0,math.pi))
# Major primary timber structure, stone footings and knee braces.
for x in [-27.45,-21.82,-16.18,-10.55]:
 box('Arcade square stone footing',(x,55.15,.35),(.9,.9,.7),'stone')
 box('Arcade stone capital base',(x,55.15,.76),(1,.95,.16),'cap')
 box('Arcade oak post',(x,55.15,3.05),(.42,.42,4.6),'timber')
 for direction in [-1,1]:
  end=x+direction*1.05
  if -27.5<end< -10.5:beam('Structural curved-brace substitute',(x,55.15,4.1),(end,55.15,5.32),.23,.25)
box('Continuous arcade bressumer',(-19,55.15,5.36),(17.5,.5,.55),'timber')
box('Arcade cream fascia',(-19,55.45,5.65),(17.55,.12,.16),'cream')
# Exposed side half timber, continuous sill, articulated corners.
for x in [-27.88,-10.12]:
 for y in [38.4,42.4,46.1,49.9,54.9]:
  box('Side framing post',(x,y,3.05),(.18,.24,4.55),'timber')
 box('Side top plate',(x,46.7,5.35),(.23,17.1,.35),'timber')
 for a,b in [(38.6,42.2),(42.6,45.9),(50.1,54.7)]:
  beam('Side upper diagonal',(x,a,3.2),(x,b,5.2),.17,.17)
# West entrance: no encroachment on lane. Doorway faces x negative.
box('West entry shadow',(-27.75,48,2.25),(.15,3.4,4.3),'dark')
for y in [46.15,49.85]:box('West entry timber jamb',(-27.85,y,2.25),(.25,.25,4.5),'timber')
box('West entry header',(-27.85,48,4.5),(.28,4,.35),'timber')
# Gable roof, fully closed thickness, no roof plane floating through ridge.
for side in [-1,1]:
 x0=-19;x1=-19+side*8.95
 v=[(x0,38,8.35),(x1,38,5.7),(x1,56,5.7),(x0,56,8.35)]
 v += [(x,y,z-.22) for x,y,z in v]
 mesh('Solid teal roof slope',v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'teal')
 # Intentional broad standing seams, calibrated against 18m building, not noise.
 for y in [38.15+i*1.05 for i in range(18)]:
  beam('Roof standing seam',(-19,y,8.39),(x1,y,5.74),.045,.045,'rooflight')
for y in [38.2,55.7]:
 mesh('Cream gable tympanum',[(-27.65,y,5.6),(-10.35,y,5.6),(-19,y,8.1)],[(0,1,2)],'plaster')
 beam('Gable bargeboard',(-27.9,y,5.7),(-19,y,8.36),.22,.22)
 beam('Gable bargeboard',(-19,y,8.36),(-10.1,y,5.7),.22,.22)
 beam('Gable king post',(-19,y,5.65),(-19,y,8.2),.24,.24)
 for x in [-24.4,-13.6]:beam('Gable fan brace',(x,y,5.7),(-19,y,7.9),.16,.16)
beam('Roof ridge cap',(-19,38,8.41),(-19,56,8.41),.3,.3,'rooflight')
# Front signage floats only 0.1m in front of gable structure, with timber frame.
box('North stable sign',(-19,55.82,6.05),(6.9,.13,.9),'teal')
sign('North stable lettering','WEST STABLES',(-19,55.90,6.04),.59,(math.pi/2,0,math.pi))
box('West stable sign',(-27.86,48,4.97),(.1,3.7,.65),'teal')
sign('West entrance lettering','STABLES',(-27.93,48,4.97),.45,(math.pi/2,0,-math.pi/2))
# Replaces existing proxy gate piers: outward faces give true 12m clear at ground.
for x in [-42.8,-29.2]:
 box('New Stable Gate stone pier',(x,60,3),(1.6,2,6),'stone')
 box('New Stable Gate pier crown',(x,60,6.15),(1.6,2.25,.3),'cap')
 box('New Stable Gate pier foot',(x,60,.3),(1.6,2.15,.6),'cap')
box('New gate bressumer',(-36,60,5.92),(15.2,.75,.65),'timber')
for x,dx in [(-42.6,1),(-29.4,-1)]:
 beam('Gate brace',(x,60,4.9),(x+dx*1.05,60,5.77),.28,.28)
# Canopy over gateway, ridge along X, steep modest teal saddle.
for side in [-1,1]:
 v=[(-43.6,60,7.45),(-28.4,60,7.45),(-28.4,60+side*1.1,6.32),(-43.6,60+side*1.1,6.32)]
 v += [(x,y,z-.17) for x,y,z in v]
 mesh('Stable Gate canopy',v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'teal')
beam('Gate ridge',(-43.7,60,7.48),(-28.3,60,7.48),.23,.23,'rooflight')
for x in [-43.58,-28.42]:
 for y in [58.9,61.1]:beam('Gate canopy fascia',(x,y,6.3),(x,60,7.45),.19,.19,'cream')
box('Stable Gate sign board',(-36,59.44,5.83),(7.65,.16,.94),'timber')
box('Stable Gate sign inset',(-36,59.34,5.83),(7.3,.06,.71),'teal')
sign('Stable Gate clear lettering','STABLE GATE',(-36,59.29,5.83),.63,(math.pi/2,0,0))
# Gate route destination sign from outside, north face.
box('Gate return plaque',(-36,60.48,5.83),(7.35,.15,.8),'teal')
sign('Town return lettering','WEST TOWN',(-36,60.58,5.83),.58,(math.pi/2,0,math.pi))
# Stable-side yard lamps grounded on facade, not route.
for x in [-26.5,-11.5]:
 beam('Lantern bracket',(x,55.4,4.25),(x,55.85,4.25),.075,.075,'iron')
 box('Lantern frame',(x,55.85,3.92),(.3,.3,.52),'iron')
 box('Lantern warm glass',(x,55.85,3.94),(.22,.22,.36),'cream')
# Export world-space kit only.
asset=list(bpy.context.scene.objects)
bpy.ops.object.select_all(action='SELECT')
out=P/'stable-gate-frontage-art-WIP.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'stable-gate-frontage-editable.blend'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(out))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
(P/'validation.json').write_text(json.dumps({'status':'art-only inferred architecture, source anchors','map_transform':'map(x,y,z) to Blender(x,-z,y)','world_space':True,'triangles':tri,'mesh_objects':len(meshes),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'reimport_bounds':[lo,hi],'stable_source_lot':[-28,-10,38,56],'gate_source_center':[-36,60],'gate_clear_ground_width_m':12,'gate_pier_center_x':[-42.8,-29.2],'no_gameplay_rider_collision_validation':True,'catalog_id':None},indent=2))
# Save reimport proof before context composition.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'stable-gate-frontage-reimport.blend'))
print('FRONTAGE READY',tri,lo,hi)
