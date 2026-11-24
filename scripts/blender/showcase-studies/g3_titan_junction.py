"""Round 5 G3 art-only junction, local origin at archived gate (198,0,186)."""
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

OUT=output_directory()
FILE=OUT/'g3-titan-lane-junction.glb'
ORIGIN=(198,0,186)
def at(x,z,h):
    return (x-ORIGIN[0],ORIGIN[2]-z,h)

def material(n,rgb,rough=.65,metal=0,glow=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*rgb,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*rgb,1)),('Emission Strength',glow)]:
        p.inputs[k].default_value=v
    return m

clear_scene()
concrete=material('Concrete · charcoal',(.20,.23,.235),.83)
fire=material('Weathered orange cladding',(.48,.133,.037),.67,.22)
dark=material('Steel · blackened',(.043,.071,.077),.5,.43)
zinc=material('Steel · pickled',(.147,.182,.193),.58,.5)
clay=material('Compacted court graphite',(.127,.101,.081),.91)
floor=material('Passage cast deck',(.259,.276,.256),.83)
lane=material('Titan lane surfacing',(.13,.177,.178),.78)
base=material('Yard slab',(.161,.187,.188),.81)
opal=material('Warm guard lamp',(.93,.48,.095),.41,.20,2.8)
cyan=material('Route light',(.14,.78,.72),.40,.20,1.6)
Type=material('Stencil enamel',(.91,.81,.61),.73,.03,.16)
line=material('Worn route stripe',(.72,.46,.134),.83,.02)

def mesh(n,p,f,m):
    d=bpy.data.meshes.new(n);d.from_pydata(p,[],f);d.update()
    o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o)
    d.materials.append(m);return o

def box(n,x,z,h,w,d,t,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at(x,z,h))
    o=bpy.context.object;o.name=n;o.dimensions=(w,d,t)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Built edges','BEVEL');mod.width=b;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def flat(n,x0,x1,z0,z1,h,m):
    return mesh(n,[at(x0,z1,h),at(x1,z1,h),at(x1,z0,h),at(x0,z0,h)],[(0,1,2,3)],m)

# Finished floor clipped only at the west edge of this bounded scene.
ar=math.acos((164-146)/28)
p=[at(146+28*math.cos(a),186-28*math.sin(a),.05)
   for a in [-ar+2*ar*i/64 for i in range(65)]]
mesh('C3 exact eastern fight floor',p,[tuple(range(len(p)))],clay)
flat('Yard base at original zero datum',164,224,169,203,0,base)
# The radial cut is open all the way through the stepped profile.
profile=[(28,0),(28,1.5),(34,1.5),(34,3),(40,3),(40,6),(42,6),(42,0)]
for sign in (-1,1):
    a0,a1=sorted((sign*.11,sign*.395))
    p=[]
    for j in range(19):
        a=a0+(a1-a0)*j/18
        p.extend(at(146+r*math.cos(a),186-r*math.sin(a),h) for r,h in profile)
    n=len(profile)
    f=[(i*n+j,(i+1)*n+j,(i+1)*n+(j+1)%n,i*n+(j+1)%n)
       for i in range(18) for j in range(n)]
    f += [tuple(reversed(range(n))),tuple(18*n+j for j in range(n))]
    o=mesh('C3 stepped terrace with 0.22 rad cut',p,f,fire)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    for a in [sign*q for q in [.145,.20,.26,.32,.38]]:
        r=40.045
        o=box('Shadow pilaster',146+r*math.cos(a),186-r*math.sin(a),
              4.47,.11,.32,2.94,dark,.025)
        o.rotation_euler.z=a

flat('G3 passage slab',188,208,182,190,.05,floor)
flat('Titan lane slab',208,222,169,197,.045,lane)
flat('Plaza only · cropped threshold',196,224,197,203,.045,lane)
for z in (182,190):
    box('G3 passage side wall',198,z,2,20,.8,4,fire,.045)
    box('G3 passage top flashing',198,z,3.92,20,.81,.16,dark,.025)
    for x in (190,193,196,200,203,206):
        box('Passage deep vertical rib',x,z,2,.16,.81,3.78,zinc,.026)

# Archived lane walls are 1.5 m thick. West-wall clear notch z182..190.
for x,z0,z1 in [(208,169,182),(208,190,197),(222,169,197)]:
    box('Titan lane wall',x,(z0+z1)/2,2,1.5,z1-z0,4,fire,.04)
    box('Titan lane wall cap',x,(z0+z1)/2,3.97,1.51,z1-z0,.075,dark,.02)
    for z in range(math.ceil(z0+1),math.floor(z1-1),3):
        box('Titan lane folded panel',x,z,2,1.50,.11,3.78,zinc,.028)

# Frame preserves the archive's 8 m opening and 7 m portal crown.
for s in (-1,1):
    z=186+s*4.7
    box('G3 portal column',198,z,3.5,1.4,1.4,7,dark,.065)
    box('G3 column cladding',197.27,z,4,.17,.93,5.55,fire,.02)
    box('G3 column lamp',197.164,z,4.3,.065,.35,1.58,opal,.016)
    box('G3 exposed foot',198,z,.13,1.69,1.39,.26,zinc,.03)
box('G3 crown',198,186,7,1.4,10.8,1.2,dark,.083)
box('G3 lintel fascia',197.255,186,7.08,.10,7.98,.73,fire,.025)
box('G3 lintel route light',197.22,186,6.65,.082,5.90,.065,cyan,.016)
# Floor paint avoids the clear geometry audit rays; proposed art only.
for x in (167,170,173,176,179,182,185,189,192,195,198,201,204,207,210,213):
    h=.052 if x<=173 or 188<=x<=208 else (.047 if x>208 else .002)
    for z in (184.1,187.7):
        box('Paired route dashes',x,z,h,.96,.052,.001,line)
for z in (175,178,181,184,187,190,193,196,199,202):
    for x in (212.55,218.85):
        box('Lane guide dash',x,z,.047,.06,1.05,.001,line)

def sign(label,where,size,m,west=True):
    bpy.ops.object.text_add(location=where)
    o=bpy.context.object;o.name=label;o.data.body=label
    o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size
    # local XY face; normal to West, baseline reads towards +Z(world).
    o.rotation_euler=(math.pi/2,0,-math.pi/2) if west else (0,0,0)
    o.data.materials.append(m)
    bpy.ops.object.convert(target='MESH')

sign('G3    /    TITAN LANE',at(197.19,186,7.09),.49,Type)
box('Lane turn wayfinding',221.16,186,2.46,.12,5.30,1.18,dark,.07)
sign('TITAN    >',at(221.088,186,2.49),.67,Type)
sign('TITAN',at(215.5,188.3,.047),.75,Type,False)
sign('COURT  03',at(168.35,186,.052),.62,Type,False)

# Keep major floors and both terrace cuts named, batch repeated static trim by material.
groups={}
def repeat(o):
    return o.name.startswith(('Shadow pilaster','Passage deep vertical rib',
        'Titan lane folded panel','Paired route dashes','Lane guide dash'))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and repeat(o):
        groups.setdefault(o.data.materials[0].name,[]).append(o)
for name,group in sorted(groups.items()):
    group.sort(key=lambda o:o.name)
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    ob=group[0]
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.join()
    ob.name='Batched trim | '+name
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
prep=sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name)
export(prep,FILE)
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(FILE))
bpy.context.view_layer.update()
s=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get()
def rr(a,b):
    av,bv=Vector(a),Vector(b); d=bv-av
    return s.ray_cast(dg,av,d.normalized(),distance=d.length)

heights=[]
path=[(164.5+i*.125,186) for i in range(405)]+[(215,186+i*.125) for i in range(1,133)]
for x,z in path:
    hit,p,_,_,obj,_=rr(at(x,z,1.32),at(x,z,-.1))
    assert hit and -.001<p.z<.054,(x,z,p,obj)
    heights.append(p.z)
# Direct line through both gate and lane opening at player height.
assert not rr(at(164.5,186,1.4),at(221,186,1.4))[0]
assert not rr(at(215,186,1.4),at(215,202.5,1.4))[0]
assert rr(at(206,181.96,1.4),at(210,181.96,1.4))[0]
assert rr(at(206,190.04,1.4),at(210,190.04,1.4))[0]
for z in (182.41,189.59):
    assert not rr(at(188.03,z,1.4),at(208.9,z,1.4))[0]
for radius,height in [(31,1.5),(37,3),(41,6)]:
    for sign in (-1,1):
        for theta,wanted in [(.109,0),(.112,height)]:
            a=theta*sign
            x,z=146+radius*math.cos(a),186-radius*math.sin(a)
            hit,pt,*_=rr(at(x,z,7),at(x,z,-.1))
            assert hit and abs(pt.z-wanted)<.01,(radius,sign,theta,pt.z)
proof={
    'map_origin_xyz':ORIGIN,'proof_floor_samples':len(path),
    'largest_sampled_step_m':max(abs(a-b) for a,b in zip(heights,heights[1:])),
    'passage_xz':[188,208,182,190],'apron_centerline_m':14,
    'arch_design_opening_m':8,'passage_clear_between_walls_m':7.2,
    'lane_wall_gap_m':8,'lane_gross_width_m':14,
    'taper_chords_m':[2*r*math.sin(.11) for r in (28,34,40,42)],
    'separate_northern_shortcut_off_scene':True,'native_gameplay':False,
}
assert .046<proof['largest_sampled_step_m']<.055
print(proof)
(OUT/'g3-junction-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

staging=material('Background ground',(.045,.072,.086),.86)
box('Backdrop slab',193,185,-.111,280,280,.20,staging)
w=s.world;w.use_nodes=True
bg=w.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.20,.34,.48,1);bg.inputs[1].default_value=.40
for location,target,power,color,r in [
    (at(173,194,15),at(180,181,0),4200,(.63,.81,1),10),
    (at(212,175,13),at(198,188,2),4900,(1,.62,.32),13),
    (at(197,186,6.2),at(190,186,0),350,(.59,1,.87),4),
]:
    bpy.ops.object.light_add(type='AREA',location=location)
    o=bpy.context.object;o.data.energy=power;o.data.color=color;o.data.size=r;aim(o,target)
bpy.ops.object.light_add(type='SUN',location=at(180,162,40))
o=bpy.context.object;aim(o,at(200,186,1));o.data.energy=1.65;o.data.color=(1,.83,.62);o.data.angle=.12
bpy.ops.object.camera_add()
s.camera=bpy.context.object
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=False
s.render.resolution_x=1440;s.render.resolution_y=920;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
for n,eye,target,lens in [
    ('g3-approach',at(173.4,186.0,1.64),at(198,186,3.8),36),
    ('g3-elevated',at(177,223,39),at(196,187,1.8),37),
]:
    s.camera.location=eye;aim(s.camera,target);s.camera.data.lens=lens
    s.render.filepath=str(OUT/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)
