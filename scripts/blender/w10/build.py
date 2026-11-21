import bpy, math, json, os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
M={}
def mat(n,c,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;M[n]=m;return m
mat('Whitewash',(.78,.77,.65));mat('Cedar warm',(.28,.14,.065));mat('Cedar honey',(.39,.23,.11));mat('Iron',(.07,.095,.10),.7);mat('Galvanized basin',(.28,.38,.39),.55,.3);mat('Water',(.035,.24,.25),.25,.2);mat('Course teal',(.055,.31,.31));mat('Zinc',(.5,.55,.53),.8,.25)
def box(n,loc,scale,m,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[m]);
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=2;mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,a,b,r,m,vertices=16):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(M[m]);return o
def asset(name,fn):
 bpy.ops.object.select_all(action='DESELECT');before=set(bpy.data.objects);fn();objs=[o for o in bpy.data.objects if o not in before];
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0]
 bpy.ops.export_scene.gltf(filepath=str(ROOT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 return objs

def trough():
 # Open, separately modelled interior walls and inset water; not a solid box.
 for x in (-1.15,1.15):box('Trough grounded bearer',(x,0,.1),(.22,1.05,.2),'Iron')
 box('Basin floor',(0,0,.24),(3.3,.91,.1),'Galvanized basin')
 for y in (-.48,.48):box('Basin long wall',(0,y,.52),(3.3,.09,.55),'Galvanized basin')
 for x in (-1.62,1.62):box('Basin end wall',(x,0,.52),(.09,.92,.55),'Galvanized basin')
 for i in range(18):
  x=-1.53+i*.18
  for y in (-.55,.55):box('Cedar vertical stave',(x,y,.48),(.168,.08,.49),'Cedar honey' if i%3==0 else 'Cedar warm',.009)
 for x in (-1.71,1.71):box('Cedar end panel',(x,0,.48),(.08,1.02,.49),'Cedar warm')
 for z in (.3,.65):
  for y in (-.6,.6):box('Iron binding',(0,y,z),(3.5,.035,.055),'Iron',.009)
 for y in (-.49,.49):cyl('Rounded basin rim',(-1.64,y,.81),(1.64,y,.81),.045,'Galvanized basin')
 for x in (-1.64,1.64):cyl('Rounded end rim',(x,-.49,.81),(x,.49,.81),.045,'Galvanized basin')
 box('Inset water surface',(0,0,.665),(3.16,.82,.025),'Water',.035)
 for x in (-1.43,1.43):
  for y in (-.624,.624):
   for z in (.3,.65):cyl('Band rivet',(x,y,z),(x,y+(.012 if y>0 else -.012),z),.022,'Zinc',12)
 # Closed feed pipe, no physics or animation implied.
 cyl('Feed riser',(-1.45,.72,.12),(-1.45,.72,1.02),.035,'Iron')
 cyl('Feed spout',(-1.45,.72,1.02),(-1.45,.25,1.02),.035,'Iron')

def jump():
 for x in (-2.05,2.05):
  box('Grounded cross foot',(x,0,.06),(.65,1.05,.12),'Iron')
  box('Whitewashed upright',(x,0,.78),(.18,.18,1.44),'Whitewash')
  box('Teal post cap',(x,0,1.53),(.23,.23,.1),'Course teal')
  for z in (.58,.8,1.02,1.24):
   cyl('Adjustment pin',(x,-.101,z),(x,-.12,z),.022,'Iron',12)
  box('Rail cup',(x,-.10,1.015),(.23,.22,.08),'Iron')
  for s in (-1,1):
   o=box('Foot diagonal brace',(x,s*.24,.28),(.065,.065,.58),'Whitewash');o.rotation_euler.x=s*math.radians(48)
 # One continuous modular striped pole, authored length 4.1m, crest 1.17m.
 for i in range(10):
  a=-2.05+i*.41;b=a+.41
  cyl('Jump rail stripe %02d'%i,(a,-.12,1.1),(b,-.12,1.1),.07,'Course teal' if i%2==0 else 'Whitewash',20)
 for x in (-2.05,2.05):cyl('Pole end cap',(x,-.12,1.1),(x+(.02 if x>0 else -.02),-.12,1.1),.073,'Iron',20)

T=asset('w10a-paddock-trough-wip',trough)
for o in T:o.hide_render=True;o.hide_set(True)
J=asset('w10b-reusable-riding-jump-wip',jump)
for o in T:o.hide_render=False;o.hide_set(False)
# Native file contains separate editable object groups, at origin by design.
for name,objs in [('W10a trough',T),('W10b reusable jump',J)]:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
 for o in objs:
  for old in list(o.users_collection):old.objects.unlink(o)
  c.objects.link(o)
bpy.data.collections['W10b reusable jump'].hide_viewport=True
bpy.data.collections['W10b reusable jump'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'w10-editable.blend'))
bpy.data.collections['W10b reusable jump'].hide_viewport=False
bpy.data.collections['W10b reusable jump'].hide_render=False
# Render exact exported GLBs in a clean scene, proving actual delivered model pixels.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX'
mat('Backdrop',(.13,.17,.16))
box('Render floor',(0,0,-.09),(200,200,.15),'Backdrop',0)
bpy.ops.object.light_add(type='AREA',location=(1,-4,7));bpy.context.object.data.energy=1700;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.ops.object.light_add(type='AREA',location=(-4,3,5));bpy.context.object.data.energy=1100;bpy.context.object.data.size=5
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=5.5
for name in ['w10a-paddock-trough-wip','w10b-reusable-riding-jump-wip']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/(name+'.glb')));objs=set(bpy.data.objects)-before
 for suffix,pos in [('hero',(4,-6,3.7)),('reverse',(-4,5,3.2))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(ROOT/(name+'-'+suffix+'.png'));bpy.ops.render.render(write_still=True)
 for o in objs:bpy.data.objects.remove(o,do_unlink=True)
print('W10 BUILD AND RENDERS COMPLETE')
