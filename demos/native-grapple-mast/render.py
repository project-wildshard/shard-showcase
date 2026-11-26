"""Show the exact third-to-fourth hop at the tank rim and freestanding mast deck."""
import json
import bpy
from mathutils import Vector,Matrix

m=json.loads(proof.read_text())
assert m['receiverSha']==mesh_sha and len(m['centre'])==4
def xyz(p):return Vector((p[0],-p[2],p[1]))
def load_at(f,pos):
    previous=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(O/f))
    for o in set(S.objects)-previous:o.matrix_world=Matrix.Translation(pos)@o.matrix_world
load_at('w7a-pole-one-perch.glb',(-151,46.62,0))
load_at('w7a-pole-two-tower.glb',(-172,70.2,0))
load_at('w7a-tank-rim-hook.glb',(-193.2,91.2,21.35))
def signal(n,rgb):
    m=matte(n,rgb,0,.55)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(*rgb,1)
    bs.inputs['Emission Strength'].default_value=1.5
    return m
hopColor=[signal('Proof | previous hop',(.19,.76,.47)),signal('Proof | mast hop',(.23,.76,1))]
for n,r in enumerate(m['centre'][2:]):
    source=[r['start']]+[row[1] for row in r['frames'][::3]]+[r['end']]
    pts=[xyz(p)+Vector((0,0,.18)) for p in source]
    d=bpy.data.curves.new(f'Observed hop {n+3}','CURVE')
    d.dimensions='3D';d.bevel_depth=.070;d.bevel_resolution=2
    p=d.splines.new('POLY');p.points.add(len(pts)-1)
    for a,v in zip(p.points,pts):a.co=(*v,1)
    o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o);d.materials.append(hopColor[n])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.24,location=pts[-1])
    bpy.context.object.data.materials.append(hopColor[n])

walk=m['centre'][3]['roofWalk']
walk_color=signal('Proof | roof reposition',(.98,.59,.12))
for p in [walk['start']]+walk['frames'][::4]+[walk['end']]:
    if not isinstance(p,list):continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.075,location=xyz(p)+Vector((0,0,.11)))
    bpy.context.object.data.materials.append(walk_color)

world=bpy.data.worlds.new('Soft afternoon');world.use_nodes=True
bg=world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.27,.40,.58,1)
bg.inputs[1].default_value=.41;S.world=world
l=bpy.data.lights.new('Warm sun','SUN');l.energy=2.5;l.angle=.13;l.color=(1,.931,.846)
sun=bpy.data.objects.new('Warm sun',l);S.collection.objects.link(sun);sun.rotation_euler=(.45,-.56,-.67)
cam=bpy.data.cameras.new('Review camera')
o=bpy.data.objects.new('Review camera',cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=420
S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=90
for name,pos,pivot,lens,w,h in (
 ('route',(-168,77,33),(-199.5,78.1,18),36,1400,960),
 ('deck',(-195.2,72.2,29.1),(-202,64.95,25.53),43,1120,980),
):
    o.location=pos;o.rotation_euler=(Vector(pivot)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;S.render.resolution_x=w;S.render.resolution_y=h
    S.render.filepath=str(O/f'nov26-w7a-mast-{name}.webp')
    bpy.ops.render.render(write_still=True)
