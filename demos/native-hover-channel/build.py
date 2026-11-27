"""W5a channel release inlays. Dimensions and wall pins come from the stock replay."""
import bpy,hashlib,json,math,struct,sys
from pathlib import Path
from mathutils import Matrix,Vector
proof,out=map(Path,sys.argv[sys.argv.index('--')+1:][:2]);out.mkdir(exist_ok=True,parents=True)
d=json.loads(proof.read_text())
assets=Path(__file__).resolve().parents[2]/'public/assets/wildshard-art'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(assets/d['file'])==d['sha']
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def mat(n,col,metal=0,rough=.75):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m

chalk=[mat('Board park pale ochre',(.58,.39,.126)),mat('Glazed terracotta inlay',(.28,.072,.019))]
teal=[mat('Aged cyan enamel',(.076,.427,.408)),mat('Dark stained iron',(.035,.109,.122))]
palette=chalk+teal
mesh=bpy.data.meshes.new('Paired release inlays')
verts=[];faces=[];mats=[]
def quad(xy,z,index):
 j=len(verts);verts.extend((x,y,z) for x,y in xy)
 faces.append((j,j+1,j+2,j+3));mats.append(index)
# Short transverse pairs rather than arrows that might imply a speed boost.
# The two indicators are nearby design cues, not an input trigger.
for side in (-1,1):
 edge=2*side
 for j in range(-6,7):
  cy=j*3.4
  for k in range(2):
   x=edge+side*(-.20+.22*k)
   for v in (-1,1):
    pts=[(x-.085*side,cy+v*.055),(x+.08*side,cy+v*.055),(x+.055*side,cy+v*.48),(x-.085*side,cy+v*.48)]
    if ((pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])-(pts[1][1]-pts[0][1])*(pts[2][0]-pts[0][0]))<0:pts.reverse()
    quad(pts,.0244,2 if k==0 else 0)
  x=edge-side*.61
  quad([(x-.045,cy-.28),(x+.045,cy-.28),(x+.045,cy+.28),(x-.045,cy+.28)],.0244,3)
mesh.from_pydata(verts,[],faces);mesh.update()
for m in palette:mesh.materials.append(m)
for f,i in zip(mesh.polygons,mats):f.material_index=i
cue=bpy.data.objects.new('D7 Release Inlays',mesh);s.collection.objects.link(cue);cue.select_set(True)
bpy.context.view_layer.objects.active=cue
dest=out/'w5a-channel-release-inlays.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_texcoords=False,export_animations=False)
raw=dest.read_bytes();g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tris=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
assert tris==260 and len(raw)<21000 and not g.get('textures')
bpy.data.objects.remove(cue,do_unlink=True)
def load(p,center=(0,0,0),yaw=0):
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(p));new=set(s.objects)-old
 m=Matrix.Translation(center)@Matrix.Rotation(yaw,4,'Z')
 for o in new:
  if o.parent not in new:o.matrix_world=m@o.matrix_world
 bpy.context.view_layer.update()
 return new
objects=load(dest)
wave=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
assert max(abs(p.z-d['floor']['top']-.0009) for p in wave)<1e-6
assert max(abs(p.x) for p in wave)<2.5 and max(abs(p.y) for p in wave)<22.5
(out/'inlay.json').write_text(json.dumps({'file':dest.name,'bytes':len(raw),'triangles':tris,'sha256':sha(dest),
 'max_above_floor_m':.0009,'mount':d['guide']['origin'],'collider':False},indent=2)+'\n')
if '--no-render' in sys.argv:sys.exit(0)
for row in d['rows']:
 load(assets/d['file'],(row['x']+220,0,0),row['yaw'])
def cube(n,c,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=n;o.dimensions=size;o.data.materials.append(m)
 return o
outer=mat('Dark fair-weather park paving',(.102,.145,.157));floor=mat('Baked ochre center',(.30,.133,.065))
seam=mat('Paving seams and edge trims',(.07,.082,.096))
cube('Separate original flat channel',(0,0,.013),(8,45,.021),floor)
cube('Surrounding staged paving',(0,0,-.19),(61,73,.38),outer)
for i in range(12):
 for j in range(2):
  cube('Offset joint',((1 if j else -1)*(15.6+(i%2)*2),(i-5.5)*4,-.006),(5.1,.047,.014),seam)
# Imported scale reference, not a moving actor.
board=assets/'wsc-prop-032-hoverboard.glb'
assert sha(board)=='b52b733aecf641b084e9d2729aa5dcd9849b993553cc687fd4bb0fd1c77730b3'
load(board,(-.33,-4.8,.075),.34)
s.world=bpy.data.worlds.new('Storm-clear afternoon');s.world.use_nodes=True
n=s.world.node_tree.nodes['Background'];n.inputs[0].default_value=(.30,.44,.66,1);n.inputs[1].default_value=.56
bpy.ops.object.light_add(type='SUN');o=bpy.context.object;o.data.energy=2.6;o.data.angle=.08;o.data.color=(1,.82,.66)
o.rotation_euler=Vector((.44,.65,-.68)).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=26;s.cycles.adaptive_threshold=.03;s.cycles.use_denoising=False
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=88
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
for name,eye,target,lens,w,h in [
 ('floor',(-.4,-8.9,1.70),(1.7,-1.7,1.05),24,960,1200),
 ('overview',(23,-35,28),(0,.4,.68),31,1300,940),
]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.resolution_x=w;s.render.resolution_y=h
 s.render.filepath=str(out/f'nov27-hover-channel-{name}.webp');bpy.ops.render.render(write_still=True)
