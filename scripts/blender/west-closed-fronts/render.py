"""Review the exact reimported shutters against the unmodified W0b street."""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

out=Path(sys.argv[sys.argv.index("--")+1])
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=28
scene.cycles.adaptive_threshold=.04
scene.cycles.use_denoising=False
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.quality=89
world=bpy.data.worlds.new('Main Street daylight')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.71,.83,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.50
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object
sun.rotation_euler=Vector((-.65,.39,-1)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=3.0
sun.data.angle=.12
sun.data.color=(1,.85,.72)
scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add()
camera=bpy.context.object
scene.camera=camera

def render(name,eye,look,lens,dims):
    camera.location=eye
    camera.rotation_euler=(Vector(look)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=dims
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/f'{name}.webp')
    bpy.ops.render.render(write_still=True)

render('nov25-w0b-closed-front-street',(-103,3.4,2.1),(-112,-6.2,2.45),30,(1360,900))
render('nov25-w0b-closed-front-portrait',(-79,0,1.7),(-82,6,2.6),24,(804,1748))
