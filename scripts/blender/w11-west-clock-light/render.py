"""Render the fixture's selected light positions, not a native frame or photometric calibration."""
import bpy,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
data,check,out=map(Path,sys.argv[sys.argv.index('--')+1:])
proof=json.loads(check.read_text()); d=json.loads(data.read_text())
assert hashlib.sha256(data.read_bytes()).hexdigest()==proof['fixtureSHA256']
out.mkdir(exist_ok=True,parents=True)
root=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
pins={
 'w11a-obelisk-uplight.glb':'fe50e1b36bafe31bccfef93cd97ad333033c097212a150e4b7cd9cb802318dcf',
 'w11a-record-board-light.glb':'332b05613fd49f57a8887d61e8b5d9e64cad695125e4848366538f63ed1f0860',
 'w6d-movers-record-board.glb':'b2f95b7f313e8be33e50898e5f2a739e2a5b8beed4fdaf04e37b01c6f5191097',
 'wsc-arch-004-obelisk.glb':'19ac342e2615609121bf69a2e3fa4c43dfa5932775e0004f43aafaa3a8e7dc6d',
 'wsc-prop-018-basin.glb':'5ccebdba563d8b507ac556972477888aa83709a986b68cb86805170e0bbb08f5',
}
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def xyz(p):return Vector((p[0],-p[2],p[1]))
def place(name,p,yaw=0):
 from mathutils import Matrix
 doc=root/name;assert hashlib.sha256(doc.read_bytes()).hexdigest()==pins[name]
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(doc))
 new=set(s.objects)-old
 transform=Matrix.Translation(xyz(p))@Matrix.Rotation(yaw,4,'Z')
 for o in new:
  if o.parent not in new:o.matrix_world=transform@o.matrix_world
 return new

def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 node=m.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*c,1)
 node.inputs['Roughness'].default_value=.79
 return m
pave=[mat('Paving'+str(i),c) for i,c in enumerate(((.25,.243,.213),(.28,.266,.224),(.32,.30,.254),(.218,.224,.207)))]
back=mat('Dark industrial background',(.09,.109,.129))
seal=mat('Accent iron',(.085,.092,.096))
path=mat('Joint backing',(.128,.144,.141))
def cube(n,loc,dim,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=n;o.dimensions=dim;o.data.materials.append(m)
 return o
place('wsc-arch-004-obelisk.glb',(-34,0,0))
place('wsc-prop-018-basin.glb',(-34,.082,0))
lenses=[]
for id,m in d['artMounts'].items():
 if m['kind']=='obelisk':place('w11a-obelisk-uplight.glb',m['at'],m['yaw'])
 if m['kind']=='movers':
  place('w6d-movers-record-board.glb',m['board'],m['yaw'])
  for o in place('w11a-record-board-light.glb',m['at'],m['yaw']):
   if o.type!='MESH':continue
   for a in o.data.materials:
    if a and a.use_nodes and 'Frosted amber lens' in a.name:
     n=a.node_tree.nodes.get('Principled BSDF')
     if n not in lenses:lenses.append(n)
assert lenses
for x,y in ((-34,0),(-66,96)):
 cube('Staged slab',(x,y,-.185),(48,51,.36),path)
 for i in range(-9,10):
  for j in range(-9,10):
   cube('Staged flagstone',(x+i*1.6,y+j*1.6,-.019),(1.58,1.58,.042),pave[(i*i+j*19+i*j)%4])
 for i in range(7):
  dx=i*5-15
  cube('Staged service wall',(x+dx,y+13,1.6),(4.98,.48,3.3),back)
  cube('Staged parapet',(x+dx,y+12.97,3.24),(4.99,.73,.18),seal)
# Identical blue ambient, floor and camera in each matched pair.
s.world=bpy.data.worlds.new('Overcast blue hour');s.world.use_nodes=True
n=s.world.node_tree.nodes['Background'];n.inputs[0].default_value=(.25,.38,.58,1);n.inputs[1].default_value=.17
for px,py in [(-34,0),(-66,96)]:
 bpy.ops.object.light_add(type='AREA',location=(px-6,py+1,14))
 l=bpy.context.object;l.data.energy=1350;l.data.color=(.48,.65,1);l.data.size=22
 l.rotation_euler=(Vector((px,py-2,0))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=27;s.cycles.adaptive_threshold=.035;s.cycles.use_denoising=False
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=89
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
fixtures=[]
for k,row in proof['review'].items():
 for o in fixtures:bpy.data.objects.remove(o,do_unlink=True)
 fixtures=[]
 eye=xyz(row['eye']);cam.location=eye
 at=Vector((-34,-.1,7.4)) if k=='obelisk' else Vector((-66,96,1.59))
 cam.data.lens=28 if k=='obelisk' else 30
 cam.rotation_euler=(at-eye).to_track_quat('-Z','Y').to_euler()
 s.render.resolution_x,s.render.resolution_y=((900,1100) if k=='obelisk' else (1180,900))
 for p in row['night']:
  here=xyz(p['position'])
  if (here-at).length>18:continue
  bpy.ops.object.light_add(type='POINT',location=here)
  o=bpy.context.object;o.data.color=(1,.53,.24);o.data.shadow_soft_size=.15
  fixtures.append(o)
  o['preview_watts']=p['intensity']*(12 if k=='obelisk' else 5)
 for state in ('off','on'):
  for o in fixtures:o.data.energy=o['preview_watts'] if state=='on' else 0
  for n in lenses:
   n.inputs['Emission Color'].default_value=(1,.42,.105,1)
   n.inputs['Emission Strength'].default_value=2.8 if state=='on' and k=='movers' else 0
  s.render.filepath=str(out/f'nov27-west-clock-{k}-{state}.webp')
  bpy.ops.render.render(write_still=True)
