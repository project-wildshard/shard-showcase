"""Render W08 with the original trolley and the exact verified motor trajectory."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector

out=Path(sys.argv[sys.argv.index('--')+1])
scene=bpy.context.scene
motion=json.loads((out/'handoff.json').read_text())
pad=json.loads((out/'pad-ack.json').read_text())
ride=json.loads((out/'ride.json').read_text())
assert motion['center']['pass'] and not motion['closed']['pass']
assert motion['meshSha']==hashlib.sha256((out/'terminal-mesh.json').read_bytes()).hexdigest()
def xyz(p):return Vector((p[0],-p[2],p[1]))
def load(path):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return tuple(set(scene.objects)-before)
repo=Path(__file__).resolve().parents[2]
trolley,=load(repo/'public/assets/wildshard-art/w7b-ochre-cable-trolley.glb')
t=ride['final']['s']/ride['length_m']
x=Vector((97,-17.5,-31-4*1.2*(1-2*t))).normalized()
y=Vector((-x.y,x.x,0)).normalized()
z=x.cross(y)
trolley.matrix_world=Matrix.Translation(xyz(ride['final']['trolley']))@Matrix((x,y,z)).transposed().to_4x4()
overlay,=load(out/'w7b-finish-ack.glb')
overlay.matrix_world=Matrix.Translation(xyz(pad['overlay_origin_three']))@overlay.matrix_world
def mat(n,rgb):
    m=bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=.8
    return m
sweep=mat('Overlay | motor sweep',(.99,.47,.075))
settle=mat('Overlay | pad contact',(.25,.93,.64))
start=xyz(motion['start'])
c=motion['center']['frames']
p=[start]+[xyz(f['feet']) for f in c if f['stage']=='handoff']
draw=[]
def dot(p,r,m):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=p+Vector((0,0,.055)))
    o=bpy.context.object;o.name='Bench locator';o.data.materials.append(m);draw.append(o)
for point in p:dot(point,.034,sweep)
dot(xyz(motion['center']['last']['feet']),.062,settle)
cv=bpy.data.curves.new('Native motor trace','CURVE');cv.dimensions='3D';cv.bevel_depth=.015
sp=cv.splines.new('POLY');sp.points.add(len(p)-1)
for point,pos in zip(sp.points,p):point.co=(*(pos+Vector((0,0,.055))),1)
line=bpy.data.objects.new('Debug only | eight collision-aware steps',cv);scene.collection.objects.link(line)
cv.materials.append(sweep);draw.append(line)
S=scene
world=bpy.data.worlds.new('Late afternoon');world.use_nodes=True
bg=world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.28,.40,.57,1)
bg.inputs[1].default_value=.41;S.world=world
l=bpy.data.lights.new('Warm sun','SUN');l.energy=2.85;l.angle=.13;l.color=(1,.94,.84)
sun=bpy.data.objects.new('Warm sun',l);S.collection.objects.link(sun);sun.rotation_euler=(.43,-.62,-.48)
cam=bpy.data.cameras.new('Bench camera')
o=bpy.data.objects.new('Bench camera',cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=260
S.render.engine='CYCLES';S.cycles.samples=28;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=89
for name,pos,pivot,lens,w,h,debug in (
  ('sweep',(-119.5,13.6,16.0),(-115.7,16.4,13.1),39,1360,980,True),
  ('ack',(-117.1,13.25,15.4),(-115,16.5,12.85),46,1000,1000,False),
):
    for d in draw:d.hide_render=not debug
    overlay.hide_render=debug
    # The imported preview action is 60 fps when loaded into the 60 fps source scene.
    keys=overlay.data.shape_keys
    if keys.animation_data:keys.animation_data_clear()
    keys.key_blocks[1].value=0
    bpy.context.view_layer.update()
    o.location=pos;o.rotation_euler=(Vector(pivot)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;S.render.resolution_x=w;S.render.resolution_y=h
    S.render.filepath=str(out/f'nov26-w7b-roof-{name}.webp')
    bpy.ops.render.render(write_still=True)
