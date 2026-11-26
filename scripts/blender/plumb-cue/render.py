"""Render the same 15 m look at acquire and lock with the exact existing E3 screen."""
import hashlib
from mathutils import Matrix,Vector
from pathlib import Path
import sys

import bpy

O=Path(sys.argv[sys.argv.index('--')+1])
REPO=Path(__file__).resolve().parents[3]
S=bpy.context.scene
for o in tuple(S.objects):bpy.data.objects.remove(o,do_unlink=True)
def load(path):
    before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    return tuple(set(S.objects)-before)
def art(name,hash):
    p=REPO/'public/assets/wildshard-art'/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==hash,p
    return p
screen=art('e3-suspended-pillar-screen.glb','b97aac0a7b80e50f2c2d066e51e89cbf32c1ccbed65b83cfd776c9b03c65f69e')
perch=art('e3-maintenance-perch.glb','4cd6018c7bfe879925e0c198d7ee4d810d28aaf4fa3569b2f4894b5e27defafc')
for o in load(screen):o.matrix_world=Matrix.Translation((3.7,2.6,0))@o.matrix_world
for o in load(perch):o.matrix_world=Matrix.Translation((7.7,2.6,4.02))@o.matrix_world
for o in load(screen):
    o.matrix_world=Matrix.Translation((14.4,6.1,0))@o.matrix_world

def mat(n,rgb,rough):
    m=bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough
    return m
concrete=mat('Proof ground | poured grey - mottled',(.25,.255,.239),.81)
n=concrete.node_tree.nodes;l=concrete.node_tree.links
coord=n.new('ShaderNodeTexCoord')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.4;tex.inputs['Detail'].default_value=3
l.new(coord.outputs['Object'],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.19;ramp.color_ramp.elements[0].color=(.115,.124,.124,1)
ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(.305,.302,.272,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=32
l.new(coord.outputs['Object'],noise.inputs['Vector'])
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.34;b.inputs['Distance'].default_value=.035
l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],n.get('Principled BSDF').inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=78);bpy.context.object.data.materials.append(concrete)
# Orthogonal floor joints are scene dressing only and do not enter either export.
joint=mat('Proof | flat sealed joint',(.078,.086,.087),.82)
for x in (-12,-6,0,6,12,18,24,30):
    bpy.ops.mesh.primitive_plane_add(size=1,location=(x,0,.0004))
    o=bpy.context.object;o.scale=(.025,44,1);o.data.materials.append(joint)
for y in (-12,-6,6,12,18):
    bpy.ops.mesh.primitive_plane_add(size=1,location=(6,y,.0005))
    o=bpy.context.object;o.scale=(44,.025,1);o.data.materials.append(joint)

def place(file,from_,to):
    v=Vector(to)-Vector(from_)
    rot=Vector((1,0,0)).rotation_difference(v.normalized())
    M=Matrix.Translation(from_)@rot.to_matrix().to_4x4()@Matrix.Diagonal((v.length,1,1,1))
    nodes=load(O/file)
    bases=[o for o in nodes if o.parent not in nodes]
    for o in bases:o.matrix_world=M@o.matrix_world
    keys=[]
    for o in nodes:
        if o.type!='MESH' or not o.data.shape_keys:continue
        shape=o.data.shape_keys
        if shape.animation_data:shape.animation_data_clear()
        keys.append(shape.key_blocks[1])
    assert keys
    return keys
beam=place('e3-plumb-beam.glb',(0,0,4),(15,0,.006))
lane=place('e3-plumb-lane.glb',(0,0,.006),(15,0,.006))

world=bpy.data.worlds.new('Industrial sky');world.use_nodes=True
bg=world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.24,.40,.60,1)
bg.inputs[1].default_value=.4;S.world=world
l=bpy.data.lights.new('Side sun','SUN');l.energy=2.4;l.angle=.17;l.color=(1,.888,.757)
sun=bpy.data.objects.new('Side sun',l);S.collection.objects.link(sun);sun.rotation_euler=(.60,-.44,-.68)
cam=bpy.data.cameras.new('402 x 874 view')
o=bpy.data.objects.new('402 x 874 view',cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=110
S.render.engine='CYCLES';S.cycles.samples=20;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=90
for name,pos,pivot,size,lock in (
 ('acquire',(18.2,-3.4,1.72),(6.5,.62,1.76),(804,1748),False),
 ('lock',(18.2,-3.4,1.72),(6.5,.62,1.76),(804,1748),True),
):
    for k in beam:k.value=0 if lock else .46
    for k in lane:k.value=0 if lock else .18
    bpy.context.view_layer.update()
    o.location=pos;o.rotation_euler=(Vector(pivot)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=46
    S.render.resolution_x,S.render.resolution_y=size
    S.render.filepath=str(O/f'nov26-e3-plumb-{name}.webp')
    bpy.ops.render.render(write_still=True)
