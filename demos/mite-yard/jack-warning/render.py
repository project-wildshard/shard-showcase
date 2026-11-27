"""Original static Wildshard staging of two measured line-of-sight cases."""
import math,sys
from pathlib import Path
import bpy
from mathutils import Vector

out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(repo/'public/assets/wildshard-art/wsc-actor-002-pallet-jack-study.glb'))
scene=bpy.context.scene
for o in scene.objects:
    if o.parent is None:o.location.y+=12
def m(name,c,metal=0,rough=.58,emit=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=emit
    return mat
deck=m('Slate slab',(.071,.093,.121),.05,.84)
rails=m('Forged rails',(.09,.15,.19),.48)
post=m('Painted structural orange',(.42,.13,.028),.21)
dark=m('Crate enamel',(.11,.21,.24),.46)
frame=m('Crate frame',(.34,.42,.44),.52)
tell=m('Warm charge mark',(.59,.029,.016),.12,emit=.92)
gold=m('Docks lights',(.93,.46,.09),.12,emit=2)
def box(name,at,scale,material,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Edge bevel','BEVEL');b.width=bevel;b.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    o.data.materials.append(material)
    return o
box('Concrete',(.0,5,-.23),(46,48,.46),deck)
for sign in [-1,1]:
    x=sign*4.25
    for y in (1,5,9,13,17,21):
        box('Bay post',(x,y,1.45),(.27,.29,2.9),post)
        box('Post marker',(x-sign*.15,y,1.42),(.09,.13,.34),gold,.019)
    box('Lower sill',(x,9,.17),(.23,26,.34),rails)
    box('Upper rail',(x,9,.99),(.12,26,.11),rails,.035)
    for n in range(23):
        box('Charge boundary',(sign*1.1,11.65-.6*n,.008),(.042,.43,.016),tell,.008)
    for y in range(0,12,2):
        mark=box('Lane direction',(sign*.24,y,.013),(.05,.73,.024),tell,.009)
        mark.rotation_euler.z=-sign*.78
cover=[box('Cargo blocker',(-.85,7.3,1.2),(2.7,1.8,2.4),dark,.045)]
for x in (-2.12,.42):
    cover.append(box('Blocker frame',(x,6.42,1.2),(.12,.07,2.34),frame,.024))
for z in (.14,2.26):
    cover.append(box('Corner band',(-.85,6.42,z),(2.65,.07,.14),frame,.026))
for x in (-1.85,-1.55,-1.25,-.95,-.65,-.35,-.05,.25):
    cover.append(box('Pressed rib',(x,6.405,1.2),(.055,.075,1.97),dark,.021))
def aim(o,at):
    o.rotation_euler=(Vector(at)-o.location).to_track_quat('-Z','Y').to_euler()
for label,power,pos,color,size in [
    ('Overhead sun bay',2400,(-3,5,8),(1,.73,.50),7),
    ('Cool yard fill',3000,(3,9,7),(.35,.68,1),8),
    ('Distant rim',1000,(1,18,6),(.55,.77,1),5)]:
    light=bpy.data.lights.new(label,'AREA');light.energy=power;light.color=color;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new(label,light);scene.collection.objects.link(ob);ob.location=pos;aim(ob,(0,6,0))
scene.world=bpy.data.worlds.new('Clouded docks');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.2,.31,.44,1);bg.inputs[1].default_value=.5
bpy.ops.object.camera_add(location=(0,-5.78,3.08));cam=bpy.context.object;scene.camera=cam
aim(cam,(0,0,1.9));cam.data.sensor_fit='VERTICAL';cam.data.lens=cam.data.sensor_height/(2*math.tan(math.radians(32)))
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.067
scene.render.resolution_x=402;scene.render.resolution_y=874
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=96
for name in ('open','cover'):
    for o in cover:o.hide_render=name=='open'
    scene.render.filepath=str(out/f'{name}.jpg');bpy.ops.render.render(write_still=True)
