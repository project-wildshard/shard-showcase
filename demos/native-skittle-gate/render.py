"""Photograph the original ramp with reimported GLBs at recorded gate/ball transforms."""
from pathlib import Path
import hashlib
import json
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

trace,out=map(Path,sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
model=trace.parent
r=json.loads(trace.read_text())
scene=bpy.context.scene
assets=Path(__file__).resolve().parents[2]/'public/assets/wildshard-art'
ballfile=assets/'wsc-plan-004-rolling-ball.glb'
assert hashlib.sha256(ballfile.read_bytes()).hexdigest()=='c04881c87359049db80b6f17772628543628688dd6fee3c58e1bf6f7f3ebe171'

def pos(p):
    return p['x'],-p['z'],p['y']

def transform(roots,p,q=None):
    new=Matrix.Translation(pos(p))
    if q:
        new=new@Quaternion((q['w'],q['x'],-q['z'],q['y'])).to_matrix().to_4x4()
    for ob,base in roots:ob.matrix_world=new@base

def load(path):
    old=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [(ob,ob.matrix_world.copy()) for ob in set(scene.objects)-old if ob.parent is None]

# Hide scene-only balls; the original ramp and rails remain visible.
for ob in tuple(scene.objects):
    if 'shared scene-only study' in ob.name and 'ball ' in ob.name:ob.hide_render=True
yy=load(model/'w4b-ball-gate-yoke.glb')
transform(yy,r['blocked']['frames'][0]['bar'])
bar=load(model/'w4b-ball-gate-bar.glb')
balls=[load(ballfile) for _ in range(4)]

def pose(frame):
    transform(bar,frame['bar'])
    for body,roots in zip(frame['bodies'],balls):
        transform(roots,body['p'],body['q'])
    bpy.context.view_layer.update()

scene.render.engine='CYCLES'
scene.cycles.samples=29
scene.cycles.adaptive_threshold=.045
scene.cycles.use_denoising=False
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.quality=89
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Physics Yard clear day')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.62,.74,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.62
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object
sun.rotation_euler=Vector((-.58,-.32,-1)).to_track_quat('-Z','Y').to_euler()
sun.data.color=(1,.86,.69)
sun.data.energy=2.8
sun.data.angle=.14
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam

def render(n,eye,target,lens,res):
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/(n+'.webp'))
    bpy.ops.render.render(write_still=True)

pose(r['blocked']['frames'][0])
render('nov26-w4b-gate-held',(-17.6,-189.2,10.8),(-25.0,-196,5.15),38,(1360,900))
pose(next(f for f in r['released']['frames'] if f['tick']==144))
render('nov26-w4b-gate-raised',(-32.0,-192.1,6.7),(-25.9,-196,5.55),33,(804,1748))
