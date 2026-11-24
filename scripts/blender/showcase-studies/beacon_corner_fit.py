"""E9 placement study: reproduce with Blender 4.3, -- /absolute/output."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
assets = Path(__file__).resolve().parents[3] / 'public/assets/wildshard-art'
tower = 'wsc-kit-007-storm-beacon.glb'
lamp = 'wsc-kit-007-storm-beacon-charged-lamp.glb'
module = 'wsc-kit-007-storm-beacon-seat.glb'
pins = {
    tower: '3a525f2637d5150a1e5a85c04640d6a57772c842731f063aa429142810239833',
    lamp: 'ab7445a6977c9af5cea7a31618a9c660f539e1026e23e61b1bbc2b3426b77a5d',
}
for f, pin in pins.items():
    assert hashlib.sha256((assets/f).read_bytes()).hexdigest() == pin

# Round 5 layout.js, lab.js: map X/Z; Blender uses X/-Z.
corners = [(126,14), (232,14), (232,118), (126,118)]
walls = [(126,14,140,14), (156,14,232,14), (232,14,232,118),
         (126,118,232,118), (126,14,126,58), (126,74,126,118)]
assert [(math.dist(a,b)) for a,b in zip(corners,corners[1:]+corners[:1])] == [106,104,106,104]

def load(path, offset=(0,0,0)):
    prior = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    parts = sorted(set(bpy.context.scene.objects)-prior, key=lambda o:o.name)
    for o in parts:
        if o.parent is None:
            o.location += Vector(offset)
    bpy.context.view_layer.update()
    return parts

def points(parts):
    return [o.matrix_world @ v.co for o in parts if o.type == 'MESH' for v in o.data.vertices]

clear_scene()
p = points(load(assets/tower))
q = points(load(assets/lamp))
foot = [v for v in p if abs(v.z) < 1e-5]
crown = max(v.z for v in p)
seat = 20-crown
foot_span = [max(v[i] for v in foot)-min(v[i] for v in foot) for i in (0,1)]
lamp_min, lamp_max = min(v.z for v in q), max(v.z for v in q)
assert abs(min(v.z for v in p)) < 1e-5 and 14.53 < seat < 14.55
assert all(2.17 < width < 2.20 for width in foot_span)
assert seat+lamp_max < 20
clear_scene()

def mat(name, rgb, rough=.65, metal=0, emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    for k,v in {'Base Color':(*rgb,1),'Metallic':metal,'Roughness':rough,
                'Emission Color':(*rgb,1),'Emission Strength':emission}.items():
        n.inputs[k].default_value=v
    return m

concrete=mat('Precast graphite',(.22,.26,.28),.72)
dark=mat('Cast iron',(.064,.085,.108),.38,.52)
amber=mat('Service ochre',(.54,.215,.049),.44,.38)
flange=mat('Zinc steel',(.25,.32,.34),.41,.55)
panel=mat('Boundary concrete',(.13,.165,.184),.58)
ground=mat('Wet blue gravel',(.055,.069,.076),.22)
lit=mat('Amber wayfinding',(.94,.32,.063),.40,.18,1.4)

def box(name, xyz, dims, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=bpy.context.object
    o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Cast edge','BEVEL')
        b.width=bevel
        b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    o.data.materials.append(material)
    return o

# Origin at the existing 4 m pedestal's top; the seat mates at 20 − donor crown.
h=seat-12
mount = [
    box('Foundation flange',(0,0,.11),(3.78,3.78,.22),dark,.04),
    box('Upper pedestal',(0,0,(h-.30)/2),(3.24,3.24,h-.30),concrete,.105),
    box('Warning seam',(0,0,h-.36),(3.32,3.32,.13),amber,.02),
    box('Square metal seat',(0,0,h-.15),(2.94,2.94,.30),dark),
]
for k in [-1,1]:
    for j in [-1,1]:
        mount.append(box('Seat bolt',(1.26*k,1.26*j,h+.041),(.15,.15,.082),flange,.015))
        mount.append(box('Buttress',(1.54*k,1.54*j,.99),(.27,.27,1.52),dark,.04))
export(mount,out/module)
clear_scene()
reloaded=load(out/module)
deck=[o for o in reloaded if o.name.startswith('Square metal seat')]
dp=points(deck)
assert len(deck)==1 and abs(max(v.z for v in dp)-h)<1e-5
assert all(max(abs(v[i]) for v in dp)>width/2+.36 for i,width in enumerate(foot_span))
clear_scene()

for i,(x,z) in enumerate(corners,1):
    placed=points(load(assets/tower,(x,-z,seat)))
    load(assets/lamp,(x,-z,seat))
    load(out/module,(x,-z,12))
    assert abs(max(v.z for v in placed)-20)<1e-5
    assert abs(min(v.z for v in placed)-seat)<1e-5
    box(f'Archived 4 m pedestal {i}',(x,-z,6),(4,4,12),concrete,.035)
    for a in (-1,1):
        box('Expansion seam',(x+2.009*a,-z,7.0),(.04,3.8,.12),dark,.01)
        box('Expansion seam',(x,-z+2.009*a,7.0),(3.8,.04,.12),dark,.01)
        box('High visibility corner stripe',(x+1.75*a,-z+2.013,10.65),(.13,.035,1.10),amber,.01)
        box('High visibility corner stripe',(x-2.013,-z+1.75*a,10.65),(.035,.13,1.10),amber,.01)

for x,z,u,v in walls:
    dx,dz=u-x,v-z
    span=math.hypot(dx,dz)
    box('Round 5 wall',((x+u)/2,-(z+v)/2,1.3),(max(.6,dx),max(.6,dz),2.6),panel)
    # Panel seam and cap dressing only; no extra collision proxy implied.
    box('Wall cap',((x+u)/2,-(z+v)/2,2.542),(max(.6,dx),max(.6,dz),.115),dark,.02)
    for j in range(1,math.ceil(span/4)):
        t=j*4/span
        box('Cast wall joint',(x+dx*t,-z-dz*t,1.245),
            (.035 if dx else .61,.035 if dz else .61,2.49),concrete)

height=seat+(lamp_min+lamp_max)/2
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
for a,b in zip(corners,corners[1:]+corners[:1]):
    start=Vector((a[0],-a[1],height))
    end=Vector((b[0],-b[1],height))
    d=(end-start).normalized()
    # Test in both directions outside the two endpoint cages; no fog/weather logic.
    for s,t,heading in ((start,end,d),(end,start,-d)):
        hit,*_=bpy.context.scene.ray_cast(deps,s+heading*1.1,heading,distance=(t-s).length-2.2)
        assert not hit, (a,b)
metrics={'place_map_x_z':corners,'pedestal_height_m':12,'archived_walls_xz':walls,
         'foot_span_m':foot_span,'seat_y_m':seat,'crown_y_m':20,
         'lamp_y_m':[seat+lamp_min,seat+lamp_max],'lamp_ray_y_m':height,
         'clear_directional_rays':8,'gold_base_witness_xyz':[232,20,118],
         'gold_surface_or_gameplay_claim':False}
(out/'beacon-corners.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(metrics)
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

# Non-authoritative ground and lighting. Do not export world placement or Gold.
box('Wet ground',(179,-66,-.127),(360,350,.25),ground)
nt=ground.node_tree
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=1.8
coords=nt.nodes.new('ShaderNodeTexCoord')
nt.links.new(coords.outputs['Object'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.022,.031,.038,1)
ramp.color_ramp.elements[1].position=.8
ramp.color_ramp.elements[1].color=(.108,.138,.143,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
# Low-contrast apron and light neutral dashes reveal perspective without claiming routes.
apron=mat('Apron asphalt',(.063,.076,.077),.38)
dash=mat('Faded yellow layout paint',(.37,.24,.104),.7)
for x,z,w,d in [(179,-17,104,4),(179,-115,104,4),(129,-66,4,96),(229,-66,4,96)]:
    box('Review apron',(x,z,-.005),(w,d,.012),apron)
    for t in range(-42,43,6):
        box('Apron spacing mark',(x+(t if w>d else 0),z+(t if d>w else 0),.0025),
            (2,.09,.003) if w>d else (.09,2,.003),dash)

for x,z in corners:
    bpy.ops.object.light_add(type='POINT',location=(x,-z,height+.07))
    o=bpy.context.object
    o.data.energy=68
    o.data.shadow_soft_size=.38
    o.data.color=(1,.57,.15)
    for k in (-1,1):
        box('Wayfinding strip',(x+k*1.60,-z+2.038,2.16),(.16,.055,.56),lit,.015)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

s=bpy.context.scene
w=s.world
w.use_nodes=True
bg=w.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(.265,.385,.55,1)
bg.inputs['Strength'].default_value=.44
bpy.ops.object.light_add(type='SUN',location=(118,19,60))
o=bpy.context.object
aim(o,(171,-71,0))
o.data.energy=1.25
o.data.angle=.20
o.data.color=(.68,.79,1)
s.render.engine='CYCLES'
s.cycles.samples=36
s.cycles.use_denoising=False
s.render.resolution_x=1400
s.render.resolution_y=900
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=91
s.view_settings.view_transform='AgX'
# Frame-detail fill keeps the black foot visibly separate from the support.
bpy.ops.object.light_add(type='AREA',location=(129,-19,21.8))
fill=bpy.context.object
aim(fill,(126,-14,15.7))
fill.data.energy=1200
fill.data.shape='DISK'
fill.data.size=5
fill.data.color=(1,.77,.54)
bpy.ops.object.camera_add()
s.camera=bpy.context.object
for name,look,at,lens in [
    ('beacon-seat-detail',(135.5,-23,20.5),(126,-14,15.78),38),
    ('beacon-yard-overview',(113,95,76),(179,-66,5),34),
]:
    s.camera.location=look
    aim(s.camera,at)
    s.camera.data.lens=lens
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
