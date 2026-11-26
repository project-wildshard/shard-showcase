"""Daylight review fixture; the floor and pallet props are render context only."""
import sys
import bpy
from pathlib import Path
from mathutils import Matrix, Vector

out=Path(sys.argv[sys.argv.index('--')+1])
root=Path(__file__).resolve().parents[3]
scene=bpy.context.scene
assets=root/'public/assets/wildshard-art'
for i,(x,y,angle) in enumerate([(3.2,-2.7,.28),(3.5,-3.6,-.15),(-3.9,.8,.13)]):
    old=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/'wsc-prop-009-stacked-pallets.glb'))
    for ob in set(scene.objects)-old:
        if ob.parent is None: ob.matrix_world=Matrix.Translation((x,y,0))@Matrix.Rotation(angle,4,'Z')@ob.matrix_world
bpy.ops.mesh.primitive_plane_add(size=48)
floor=bpy.context.object
floor.location.z=-.008
m=bpy.data.materials.new('Yard concrete | render only')
m.use_nodes=True
p=m.node_tree.nodes.get('Principled BSDF')
p.inputs['Roughness'].default_value=.82
n=m.node_tree.nodes.new('ShaderNodeTexNoise')
n.inputs['Scale'].default_value=270
n.inputs['Detail'].default_value=2.5
r=m.node_tree.nodes.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].position=.24
r.color_ramp.elements[0].color=(.107,.128,.133,1)
r.color_ramp.elements[1].position=.81
r.color_ramp.elements[1].color=(.25,.275,.278,1)
m.node_tree.links.new(n.outputs['Fac'],r.inputs[0])
m.node_tree.links.new(r.outputs[0],p.inputs['Base Color'])
floor.data.materials.append(m)
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object
sun.rotation_euler=Vector((.50,.58,-.76)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=3
sun.data.angle=.16
sun.data.color=(1,.85,.68)
world=bpy.data.worlds.new('Cloud break')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.39,.53,.69,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.58
scene.render.engine='CYCLES'
scene.cycles.samples=30
scene.cycles.adaptive_threshold=.043
scene.cycles.use_denoising=False
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.quality=90
scene.render.resolution_percentage=100
bpy.ops.object.camera_add()
camera=bpy.context.object
scene.camera=camera
def render(name,eye,target,lens,width,height):
    camera.location=eye
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=width,height
    scene.render.filepath=str(out/(name+'.webp'))
    bpy.ops.render.render(write_still=True)

render('nov26-e2-divider-front',(6.4,-9.5,3.2),(.04,-.1,1.45),39,1360,900)
render('nov26-e2-divider-rear',(-4.1,6.1,1.7),(-1.19,0,1.58),34,804,1748)
