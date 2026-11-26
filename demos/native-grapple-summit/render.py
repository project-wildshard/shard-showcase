"""Render the verified fifth pull and original summit with the reimported ring."""
import json
import bpy
from mathutils import Matrix,Vector
p=json.loads(proof.read_text())
assert p['summitRingSha']==receipt['mesh_sha256'] and len(p['centre'])==5
def xyz(v):return Vector((v[0],-v[2],v[1]))
def load_at(f,pos):
    before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(O/f))
    for o in set(S.objects)-before:o.matrix_world=Matrix.Translation(xyz(pos))@o.matrix_world
for f,pos in (
 ('w7a-pole-one-perch.glb',(-151,0,-46.62)),
 ('w7a-pole-two-tower.glb',(-172,0,-70.2)),
 ('w7a-tank-rim-hook.glb',(-193.2,21.35,-91.2)),
 ('w7a-mast-receiver.glb',(-202.6,0,-63.55)),
):load_at(f,pos)
def signal(name,rgb):
    m=mat(name,rgb,0)
    s=m.node_tree.nodes.get('Principled BSDF')
    s.inputs['Emission Color'].default_value=(*rgb,1);s.inputs['Emission Strength'].default_value=1.3
    return m
trail=signal('Proof | stock motor trajectory',(.95,.56,.09))
node=signal('Proof | confirmed summit contact',(.10,.86,.58))
r=p['centre'][-1]
points=[r['start']]+[x[1] for x in r['frames'][::2]]+[r['end']]
pts=[xyz(a)+Vector((0,0,.19)) for a in points]
cv=bpy.data.curves.new('Fifth pull actual motor trace','CURVE');cv.dimensions='3D';cv.bevel_depth=.077;cv.bevel_resolution=2
s=cv.splines.new('POLY');s.points.add(len(pts)-1)
for a,v in zip(s.points,pts):a.co=(*v,1)
g=bpy.data.objects.new(cv.name,cv);S.collection.objects.link(g);cv.materials.append(trail)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.23,location=pts[-1])
bpy.context.object.data.materials.append(node)
world=bpy.data.worlds.new('West twilight blue');world.use_nodes=True
bg=world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.24,.39,.63,1)
bg.inputs[1].default_value=.43;S.world=world
l=bpy.data.lights.new('Low western sun','SUN');l.energy=2.76;l.angle=.14;l.color=(1,.935,.846)
sun=bpy.data.objects.new('Low western sun',l);S.collection.objects.link(sun)
sun.rotation_euler=(.52,-.59,-.62)
cam=bpy.data.cameras.new('Summit review')
o=bpy.data.objects.new('Summit review',cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=440
S.render.engine='CYCLES';S.cycles.samples=22;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=90
for name,pos,target,lens,w,h in (
 ('route',(-176,52,45),(-208,49,33),39,1400,960),
 ('landing',(-206.6,44.6,50.5),(-214.5,38.8,45.6),42,1120,980),
):
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;S.render.resolution_x=w;S.render.resolution_y=h
    S.render.filepath=str(O/f'nov26-w7a-summit-{name}.webp')
    bpy.ops.render.render(write_still=True)
