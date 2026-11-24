"""W11a art-only shared light with exact Range and Movers board fits."""
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
light=out/'w11a-record-board-light.glb'
donors=[
 ('Movers','w6d-movers-record-board.glb','b2f95b7f313e8be33e50898e5f2a739e2a5b8beed4fdaf04e37b01c6f5191097',2.835,-.196,2.562),
 ('Range','wsc-prop-027-range-timer-display.glb','5e443a0211c4b5806c7f7118cc4a00c7bad19c31522a75d9f2295c3a71a42bc3',1.245,-.320,.945),
]
for k,f,p,*_ in donors:
    assert hashlib.sha256((assets/f).read_bytes()).hexdigest()==p

def load(p,offs=(0,0,0)):
    prior=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    parts=sorted(set(bpy.context.scene.objects)-prior,key=lambda o:o.name)
    for o in parts:
        if o.parent is None:o.location+=Vector(offs)
    bpy.context.view_layer.update()
    return parts

def mat(name,c,rough=.66,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal)]:
        p.inputs[k].default_value=v
    return m

def box(n,p,d,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        q=o.modifiers.new('Satin tooling edge','BEVEL');q.width=bevel;q.segments=1
        bpy.ops.object.modifier_apply(modifier=q.name)
    return o

def ray(a,b):
    s=bpy.context.scene
    v,u=Vector(a),Vector(b);d=u-v
    return s.ray_cast(bpy.context.evaluated_depsgraph_get(),v,d.normalized(),distance=d.length)

clear_scene()
black=mat('Graphite powder coat',(.044,.068,.079),.57,.51)
ochre=mat('Ochre cast end',(.52,.216,.090),.71,.22)
glass=mat('Frosted amber lens | neutral',(.58,.32,.116),.38,.055)
brass=mat('Tool screw brass',(.317,.25,.157),.47,.66)
objects=[
    box('Two-board light shade',(0,-.369,.104),(.88,.154,.102),black,.018),
    box('Frosted lens',(0,-.385,.049),(.68,.091,.020),glass,.008),
]
for x in (-.258,.258):
    objects.extend([box('Mount foot',(x,0,.021),(.10,.048,.042),black,.009),
                    box('Cantilever arm',(x,-.168,.075),(.061,.356,.045),black,.009),
                    box('Fastener cap',(x,.009,.051),(.033,.029,.018),brass,.006)])
for x in (-.397,.397):
    objects.append(box('Ochre end cap',(x,-.369,.103),(.065,.147,.094),ochre,.011))
export(objects,light)
data=[]
scene=bpy.context.scene
mount_y=-.12
for key,f,hsh,seat,front,toptxt in donors:
    clear_scene()
    load(assets/f)
    for x in (-.307,-.258,-.209,.209,.258,.307):
        for y in (mount_y-.023,mount_y,mount_y+.023):
            hit,p,*_=ray((x,y,4),(x,y,0))
            assert hit and abs(p.z-seat)<1e-5,(key,x,y,p.z)
    fixtures=load(light,(0,mount_y,seat))
    assert abs(min((o.matrix_world@v.co).z for o in fixtures if o.type=='MESH' for v in o.data.vertices)-seat)<1e-5
    start=(0,-.513,seat+.035)
    goal=(0,front-.008,toptxt)
    assert not ray(start,goal)[0],key
    assert not ray((0,-7,1.50),goal)[0],key
    data.append({'donor':key,'seat_y_m':seat,'mount_blender_local_y_m':mount_y,
                 'contact_samples':18,'title_lamp_line_clear':True,'title_reader_line_clear':True,
                 'material_only_neutral_export':True})
(out/'record-board-light-proof.json').write_text(json.dumps(data,indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

clear_scene()
ground=mat('Blue yard concrete',(.104,.148,.161),.83)
trim=mat('Worn rail on display stand',(.415,.238,.078),.77,.28)
stage=mat('Display stage',(.102,.127,.126),.81)
box('Studio ground',(0,0,-.149),(200,200,.288),ground)
box('Range timer riser | stage only',(1.83,.1,.515),(2.65,1.2,1.03),stage,.075)
box('Riser stripe',(1.83,-.512,.803),(1.65,.020,.039),trim,.006)
pose=[(-1.62,0,0),(1.83,0,1.03)]
emit=[]
def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for (key,f,hsh,seat,front,toptxt),(x,y,z) in zip(donors,pose):
    load(assets/f,(x,y,z))
    fixture=load(light,(x,mount_y,z+seat))
    nose=next(o for o in fixture if o.name.startswith('Frosted lens'))
    emit.append(nose.data.materials[0].node_tree.nodes.get('Principled BSDF'))
    bpy.ops.object.light_add(type='AREA',location=(x,-.513,z+seat+.035))
    o=bpy.context.object;o.data.shape='RECTANGLE';o.data.size=.58;o.data.size_y=.055
    aim(o,(x,front-.012,z+toptxt-.25))
    o.data.color=(1,.69,.38)
    emit.append(o.data)

w=scene.world
w.use_nodes=True
bg=w.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.153,.273,.40,1);bg.inputs[1].default_value=.24
for p,power,size,color in [((-4,-1,5),145,5,(.43,.59,1)),((4,5,6),340,6,(.49,.74,1))]:
    bpy.ops.object.light_add(type='AREA',location=p)
    o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=color;aim(o,(0,0,1.4))
bpy.ops.object.camera_add(location=(.35,-9.55,3.31))
scene.camera=bpy.context.object
aim(scene.camera,(0,0,1.55))
scene.camera.data.lens=42
scene.render.engine='CYCLES';scene.cycles.samples=38;scene.cycles.use_denoising=False
scene.render.resolution_x=1440;scene.render.resolution_y=880;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=91
scene.view_settings.view_transform='AgX'
for active in (False,True):
    for a in emit:
        if getattr(a,'energy',None) is not None:a.energy=12 if active else 0
        else:
            a.inputs['Emission Color'].default_value=(1,.45,.115,1)
            a.inputs['Emission Strength'].default_value=3.7 if active else 0
    scene.render.filepath=str(out/('record-lights-on.jpg' if active else 'record-lights-off.jpg'))
    bpy.ops.render.render(write_still=True)
