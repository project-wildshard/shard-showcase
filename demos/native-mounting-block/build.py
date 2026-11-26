"""Reimport the pinned WSC-PLAN-008 mounting block at the archived pad."""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
A=root/'public/assets/wildshard-art'
T=Path(sys.argv[sys.argv.index('--')+1]);T.mkdir(parents=True,exist_ok=True)
P=A/'wsc-plan-008-horse-mounting-block-wip.glb'
sha=hashlib.sha256(P.read_bytes()).hexdigest()
assert sha=='efc0615bfb51f527545bee0d5b36fff8856559928ddaf87a963955333867bf7a'
scene=bpy.context.scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
def imp(file):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(file))
    bpy.context.view_layer.update()
    return sorted(set(scene.objects)-prior,key=lambda o:o.name)
block=imp(P)
parts=[]
for o in block:
    if o.type!='MESH':continue
    m=o.data
    m.calc_loop_triangles()
    parts.append(dict(name=o.name,vertices=[round(w,7) for v in m.vertices
      for x,y,z in [o.matrix_world@v.co] for w in (x-36,z,-96-y)],
      triangles=[i for t in m.loop_triangles for i in t.vertices]))
assert len(parts)==36 and sum(len(g['triangles'])//3 for g in parts)==5264
p=T/'block-collision.json'
p.write_text(json.dumps(dict(donor=sha,origin=[-36,0,-96],meshes=parts),separators=(',',':'))+'\n')
if not (T/'walk.json').exists():sys.exit(0)
r=json.loads((T/'walk.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['geometrySha256']
def mat(n,c,e=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*c,1)
    q.inputs['Emission Color'].default_value=(*c,1)
    q.inputs['Emission Strength'].default_value=e
    q.inputs['Roughness'].default_value=.68
    return m
def place(path,loc,rotation=0):
    from mathutils import Matrix
    obs=imp(A/path)
    for o in obs:
        if o.parent not in obs:o.matrix_world=Matrix.Translation(loc)@Matrix.Rotation(rotation,4,'Z')@o.matrix_world
    bpy.context.view_layer.update()
plane=mat('Review ground, ochre clay',(.227,.149,.087))
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(plane)
place('wsc-module-011-riding-fence.glb',(0,.95,0))
place('wsc-module-011-riding-fence.glb',(3.0,.95,0))
place('w10a-paddock-trough-wip.glb',(-1.58,1.41,0),.22)
# Traces are annotations of capsule feet. Green = three boxes, amber = no block.
traces=[]
for mode,col in [('treads',(.053,.69,.56)),('nothing',(.84,.37,.10))]:
    row=next(row for row in r['traces'] if row['mode']==mode)
    c=bpy.data.curves.new(mode,'CURVE');c.dimensions='3D';c.bevel_depth=.015;c.bevel_resolution=2
    points=[v['feet'] for v in row['frames']]+[row['end']['feet']]
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for pnt,(x,y,z) in zip(s.points,points):
        pnt.co=(x+36+(.16 if mode=='nothing' else 0),-96-z,y+.03,1)
    c.materials.append(mat(mode,col,.74))
    o=bpy.data.objects.new(mode,c);scene.collection.objects.link(o);traces.append(o)
scene.world=bpy.data.worlds.new('West afternoon');scene.world.use_nodes=True
w=scene.world.node_tree.nodes.get('Background');w.inputs[0].default_value=(.39,.58,.79,1);w.inputs[1].default_value=.55
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object;sun.data.energy=2.6;sun.data.angle=.14;sun.data.color=(1,.85,.69)
sun.rotation_euler=Vector((-.42,.31,-.86)).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=30;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.056
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for i,(name,eye,aim,lens,wh) in enumerate([
        ('paddock-block-walk',(2.85,-3.7,1.72),(-.17,-.25,.34),41,(1240,900)),
        ('paddock-block-treads',(-1.43,-1.93,1.7),(0,-.02,.25),39,(1000,900))]):
    # Amber goes under the planks in the first overlay; hide it for the second close-up.
    traces[1].hide_render=bool(i)
    cam.location=eye;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=wh
    scene.render.filepath=str(T/(name+'.png'));bpy.ops.render.render(write_still=True)
