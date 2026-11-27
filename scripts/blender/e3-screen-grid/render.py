"""Stage the accepted E03 screen rows for review. Exports photographs only."""
import bpy, hashlib, json, math, random, sys
from pathlib import Path
from mathutils import Vector, Matrix

src,out=map(Path,sys.argv[sys.argv.index('--')+1:]);out.mkdir(parents=True,exist_ok=True)
d=json.loads(src.read_text())
root=Path(__file__).resolve().parents[3]
assets=root/'public/assets/wildshard-art'
model=assets/d['model']['name']
assert hashlib.sha256(model.read_bytes()).hexdigest()==d['model']['sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(model))
donors=[(o.data,o.matrix_world.copy()) for o in s.objects if o.type=='MESH']
assert donors
for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
placed=d['rows']
for row in placed:
 if not row['installedInFixture']:continue
 m=Matrix.Translation((row['x'],-row['z'],0))@Matrix.Rotation(row['ry'],4,'Z')
 for mesh,local in donors:
  ob=bpy.data.objects.new(f"Screen {row['ordinal']:02}",mesh);s.collection.objects.link(ob);ob.matrix_world=m@local

def mat(name,col,rough=.86):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 return m
def slab(name,v,sz,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=v)
 o=bpy.context.object;o.name=name;o.dimensions=sz;o.data.materials.append(m)
 return o
def surface(name,col,other,scale):
 m=mat(name,col); n=m.node_tree.nodes; links=m.node_tree.links
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4
 coords=n.new('ShaderNodeTexCoord');links.new(coords.outputs['Object'],tex.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*col,1)
 ramp.color_ramp.elements[1].position=.83;ramp.color_ramp.elements[1].color=(*other,1)
 p=n.get('Principled BSDF')
 links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.08
 links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
sand=surface('Shallow quarry dust',(.18,.154,.115),(.32,.271,.202),.78)
pad=surface('Brushed limestone apron',(.33,.31,.254),(.46,.418,.336),.29)
infill=surface('Slate access route',(.11,.119,.11),(.19,.20,.178),.85)
yellow=mat('Scuffed ochre trims',(.39,.22,.07))
shadow=mat('Dark seam',(.067,.08,.073))
slab('Ground dressing only',(180,179,-.19),(208,195,.36),sand)
slab('Western review walkway',(125.5,208,-.045),(7.5,40,.105),infill)
slab('Northern service strip',(185,230,-.047),(123,7,.109),infill)
rng=random.Random(42003)
for row in placed:
 if not row['installedInFixture']:continue
 x,y,ry=row['x'],-row['z'],row['ry']
 local=Matrix.Translation((x,y,0))@Matrix.Rotation(ry,4,'Z')
 for i in range(3):
  for j in range(2):
   center=local@Vector((3.66*(i-1),(j-.5)*3.55,.006))
   ob=slab('Review-only slab joint',center,(3.62,3.51,.022),pad)
   ob.rotation_euler.z=ry
 for i in range(8):
  center=local@Vector((-.68+i*.19,-3.46,.021))
  ob=slab('Worn sidestep trim',center,(.096,.12,.011),yellow)
  ob.rotation_euler.z=ry+.25
for i in range(29):
 x=117+i*4.4
 slab('Service drainage',(x,234,.01),(1.2,.21,.033),shadow)
# Batched tufts in the seams, not included in game art.
v=[];f=[]
for i in range(1180):
 x,y=rng.uniform(119,238),rng.uniform(124,239)
 if (x<130 and 185<y<229) or y>226 or any(math.hypot(x-a['x'],y+a['z'])<6 for a in placed if a['installedInFixture']):continue
 for k in range(4):
  dx,dy=rng.uniform(-.3,.3),rng.uniform(-.3,.3)
  a=len(v);g=rng.uniform(.055,.14)
  v.extend([(x+dx-g,y+dy,0),(x+dx+g,y+dy,0),(x+dx+.13,y+dy+.09,rng.uniform(.20,.51))]);f.append((a,a+1,a+2))
m=bpy.data.meshes.new('Dry grass');m.from_pydata(v,[],f);m.update();m.materials.append(mat('Juniper sage',(.18,.207,.095)))
o=bpy.data.objects.new('Review ground scrub',m);s.collection.objects.link(o)
# A low distant edge keeps the frame industrial without implying final walls.
for i in range(13):
 x=119+i*10
 ob=slab('Distant service bank',(x,243,-.01),(9.97,1.50,3.8),pad)
 slab('Service coping',(x,243,1.86),(10.02,1.62,.27),shadow)
for i in range(9):
 x=125+i*14
 slab('Distant rust inset',(x,242.18,.87),(4.5,.11,1.7),yellow)

s.world=bpy.data.worlds.new('Steel morning');s.world.use_nodes=True
n=s.world.node_tree.nodes
n['Background'].inputs[0].default_value=(.34,.43,.57,1);n['Background'].inputs[1].default_value=.53
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object;sun.rotation_euler=Vector((.53,-.74,-.65)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.15;sun.data.angle=.075;sun.data.color=(1,.84,.68)
s.render.engine='CYCLES';s.cycles.samples=28;s.cycles.adaptive_threshold=.025;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.19
s.render.image_settings.file_format='WEBP';s.render.image_settings.quality=87
bpy.ops.object.camera_add()
cam=bpy.context.object;s.camera=cam
r=next(a for a in placed if a['ordinal']==8)
def pose(row,x,y,z):
 a=row['ry'];return Vector((row['x']+x*math.cos(a)-y*math.sin(a),-row['z']+x*math.sin(a)+y*math.cos(a),z))
for k,eye,to,lens,w,h in [
 ('walk',pose(r,-1.45,-10.6,1.72),pose(r,.36,.9,3.05),27,900,1120),
 ('field',Vector((86,101,138)),Vector((180,181,0)),184,1340,920),
]:
 cam.location=eye;cam.rotation_euler=(to-eye).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if k=='field' else 'PERSP'
 if k=='field':cam.data.ortho_scale=lens
 else:cam.data.lens=lens
 s.render.resolution_x=w;s.render.resolution_y=h
 s.render.filepath=str(out/f'nov27-e3-screen-grid-{k}.webp')
 bpy.ops.render.render(write_still=True)
