"""Original static Wildshard set viewed through the two measured camera transforms."""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion, Matrix

out=Path(sys.argv[sys.argv.index('--')+1]); out.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[3]
proof=json.loads((repo/'project/layouts/wsc-jack-retreat-camera-proof.json').read_text())
frames=proof['samples']['backstep']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(repo/'public/assets/wildshard-art/wsc-actor-002-pallet-jack-study.glb'))
s=bpy.context.scene
for o in s.objects:
    if o.parent is None: o.location.y+=6
def mat(name,color,metal=0,rough=.59,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*color,1)
    p.inputs['Emission Strength'].default_value=emission
    return m
deck=mat('Basalt concrete',(.072,.088,.10),.04,.77)
steel=mat('Blue oxidised steel',(.059,.11,.132),.45)
orange=mat('Safety enamel',(.48,.14,.026),.3)
line=mat('Charge study bars',(.52,.026,.009),.16,emission=.95)
marker=mat('Scripted position marker',(.082,.43,.63),.42,emission=.35)
def box(name,loc,size,m,bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Edge wear','BEVEL');b.width=bevel;b.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    o.data.materials.append(m)
    return o
box('Slab',(0,2,-.21),(42,50,.42),deck)
for side in [-1,1]:
    xx=side*5.8
    for i in range(-4,5):
        yy=i*3.8
        box('Loading bay beam',(xx,yy,1.25),(.27,.31,2.5),orange)
        box('Bay cladding',(xx+side*.21,yy,1.0),(.27,3.78,2.03),steel)
        for j in range(9):
            box('Rib',(xx-side*.08,yy+(.42*j-1.68),.95),(.12,.07,1.78),steel,.016)
    for i in range(20):
        box('Charge boundary',(side*1.1,5.5-.68*i,.009),(.046,.46,.015),line,.006)
for yy in range(6,-9,-2):
    for side in [-1,1]:
        o=box('Charge marking',(side*.25,yy,.014),(.055,.76,.023),line,.008)
        o.rotation_euler.z=-side*.78
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.41,depth=.026)
hero=bpy.context.object;hero.name='Cyan scripted-player foot marker, not a character';hero.data.materials.append(marker)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for name,power,loc,colour,size in [
 ('Warm loading ramp',1400,(3,-2,6),(1,.65,.38),6),
 ('Cool bay roof',2500,(-3,6,7),(.34,.66,1),7),
 ('Face fill',500,(1,2,4),(.65,.82,1),4),
 ('Exit wash',900,(-4,-8,5),(.35,.55,1),6)]:
    l=bpy.data.lights.new(name,'AREA');l.energy=power;l.color=colour;l.shape='DISK';l.size=size
    obj=bpy.data.objects.new(name,l);s.collection.objects.link(obj);obj.location=loc;aim(obj,(0,2,0))
s.world=bpy.data.worlds.new('Overcast yard');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.26,.38,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.46
bpy.ops.object.camera_add()
cam=bpy.context.object;s.camera=cam;cam.data.sensor_fit='VERTICAL'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.cycles.adaptive_threshold=.07
s.render.resolution_x=402;s.render.resolution_y=874
s.render.image_settings.file_format='PNG'
basis=Matrix(((1,0,0),(0,0,-1),(0,1,0))).to_quaternion()
def bl(p):return (p[0],-p[2],p[1])
for name in ['baseline','candidate']:
    f=next(f for f in frames[name] if f['ms']==750)
    cam.location=bl(f['camera'])
    x,y,z,w=f['rotation'];cam.rotation_mode='QUATERNION'
    cam.rotation_quaternion=basis@Quaternion((w,x,y,z))
    cam.data.lens=cam.data.sensor_height/(2*math.tan(math.radians(f['fov'])/2))
    hero.location=bl(f['hero']);hero.location.z=.022
    s.render.filepath=str(out/f'{name}.png')
    bpy.ops.render.render(write_still=True)
