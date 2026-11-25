"""Two drop-in E5a floor effects. Normalized art; no damage or creature logic."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out=output_directory()
clear_scene()
scene=bpy.context.scene
period=2*math.pi

def ring(tag, bands, runs, chords, fraction, pulse):
    positions=[]; colors=[]; indices=[]
    for n in range(runs):
        i0=len(positions)
        for j in range(chords+1):
            f=j/chords
            a=(n+(1-fraction)/2+fraction*f)*period/runs
            for r,rgba in bands:
                positions.append((math.cos(a)*r,0,math.sin(a)*r))
                amp=(min(1,f*chords,(1-f)*chords) if runs>1 else 1)
                colors.append((*rgba[:3], rgba[3]*amp*pulse(a)))
        k=len(bands)
        for j in range(chords):
            for h in range(k-1):
                a=i0+j*k+h
                indices.extend((a,a+k,a+1,a+1,a+k,a+k+1))
    assert len(indices)%6==0
    sections=[b''.join(struct.pack('<3f',*x) for x in positions),
              b''.join(struct.pack('<4f',*x) for x in colors),
              struct.pack('<'+'H'*len(indices),*indices)]
    views=[]; offset=0
    for section,target in zip(sections,(34962,34962,34963),strict=True):
        views.append(dict(buffer=0,byteOffset=offset,byteLength=len(section),target=target))
        offset+=len(section)
    binary=b''.join(sections)
    name='e5a-riveter-'+tag
    doc=dict(asset=dict(version='2.0',generator='Wildshard E5a procedural ring'),
        scene=0, scenes=[dict(nodes=[0])], nodes=[dict(name=name,mesh=0)],
        meshes=[dict(primitives=[dict(attributes=dict(POSITION=0,COLOR_0=1),indices=2,material=0)])],
        materials=[dict(name=tag,alphaMode='BLEND',doubleSided=True,extensions={'KHR_materials_unlit':{}})],
        accessors=[dict(bufferView=0,componentType=5126,count=len(positions),type='VEC3',
                        min=[min(v[i] for v in positions) for i in range(3)],
                        max=[max(v[i] for v in positions) for i in range(3)]),
                   dict(bufferView=1,componentType=5126,count=len(colors),type='VEC4'),
                   dict(bufferView=2,componentType=5123,count=len(indices),type='SCALAR')],
        extensionsUsed=['KHR_materials_unlit'],bufferViews=views,buffers=[dict(byteLength=offset)])
    raw=json.dumps(doc,separators=(',',':')).encode()
    raw+=b' '*(-len(raw)%4)
    path=out/(name+'.glb')
    path.write_bytes(struct.pack('<4sIIII',b'glTF',2,28+len(raw)+len(binary),len(raw),0x4e4f534a)+raw+
                     struct.pack('<II',len(binary),0x004e4942)+binary)
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    obj,=[o for o in scene.objects if o not in prior and o.type=='MESH']
    obj.data.calc_loop_triangles()
    assert len(obj.data.loop_triangles)==len(indices)//3
    assert obj.data.color_attributes.active_color is not None and obj.location.length < 1e-6
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    assert max(abs(p.z) for p in points)<1e-6
    radii=[math.hypot(p.x,p.y) for p in points]
    assert abs(min(radii)-bands[0][0])<1e-6 and abs(max(radii)-bands[-1][0])<1e-6
    receipt=dict(bytes=path.stat().st_size, triangles=len(indices)//3, draws=1,
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 material='unlit RGBA alpha blend',normalized_radii=[bands[0][0],bands[-1][0]],
                 arc_runs=runs, segments_per_run=chords)
    assert receipt['bytes']<26000
    return obj,receipt

warning, w=ring('warning-ring',[
    (.947,(.49,.075,.004,0)),(.970,(.95,.27,.018,.75)),
    (.989,(1,.73,.12,1)),(1.0,(.95,.22,.008,0))],24,4,.70,lambda a:1)
wave, x=ring('travel-front',[
    (.843,(.42,.035,.006,0)),(.895,(.81,.092,.009,.23)),
    (.949,(1,.23,.016,.74)),(.974,(1,.68,.12,.95)),
    (.986,(1,.88,.43,.98)),(1.0,(1,.33,.024,0))],
    1,96,1.0,lambda a:.84+.09*math.cos(11*a)+.07*math.cos(19*a+1.2))
(out/'e5a-riveter-slam-vfx.json').write_text(json.dumps({
    'scope':'Visual preview only; no creature, damage, jump, or native integration',
    'planned_warning_seconds':1.0,'normalized_max_radius':1.0,
    'review_radius_m':3.4,'review_wave_seconds':.46,'wave_review_time_seconds':1.34,
    'warning':w,'wave':x},indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

def camera_fx(o, strength):
    mat=bpy.data.materials.new('Camera-visible VFX '+o.name)
    mat.use_nodes=True
    t=mat.node_tree;t.nodes.clear();n=t.nodes;l=t.links
    attr=n.new('ShaderNodeVertexColor');attr.layer_name=o.data.color_attributes.active_color.name
    em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=strength
    mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY'
    rays=n.new('ShaderNodeLightPath')
    mix=n.new('ShaderNodeMixShader')
    l.new(attr.outputs['Color'],em.inputs[0]);l.new(attr.outputs['Alpha'],mask.inputs[0])
    l.new(rays.outputs['Is Camera Ray'],mask.inputs[1]);l.new(mask.outputs[0],mix.inputs[0])
    l.new(n.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],n.new('ShaderNodeOutputMaterial').inputs[0])
    o.data.materials.clear();o.data.materials.append(mat)
    o.location.z=.019

camera_fx(warning,1.95)
camera_fx(wave,2.65)
def mat(name,c,r=.53,met=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r
    p.inputs['Metallic'].default_value=met
    return m

base=mat('Tar aggregate',(.080,.104,.109),.66)
p=base.node_tree.nodes.get('Principled BSDF')
n=base.node_tree.nodes;l=base.node_tree.links
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=27
l.new(n.new('ShaderNodeTexCoord').outputs['Object'],noise.inputs[0])
cr=n.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].position=.16
cr.color_ramp.elements[0].color=(.034,.054,.059,1)
cr.color_ramp.elements[1].position=.84;cr.color_ramp.elements[1].color=(.144,.153,.156,1)
l.new(noise.outputs['Fac'],cr.inputs[0]);l.new(cr.outputs[0],p.inputs['Base Color'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.062
l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
steel=mat('Flush brushed drain',(.106,.135,.141),.58,.5)
dark=mat('Recessed floor seam',(.026,.038,.041))
old=mat('Aged traffic stripe',(.38,.33,.17),.79)

def block(name,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d;o.data.materials.append(m)
    return o

block('Ground witness', (0,0,-.05),(45,45,.10),base)
for y in (-4.5,4.2):
    block('Inset channel',(0,y,.002),(13,.26,.004),dark)
    for j in range(-18,19):
        block('Drain slots',(j*.33,y,.005),(.06,.23,.006),steel)
for i in (-1,1):
    for j in range(-5,6):
        block('Weathered lane marks',(i*4.53,j*.87,.003),(.08,.32,.004),old)

repo=Path(__file__).resolve().parents[3]
asset=repo/'public/assets/wildshard-art'
def donor(name,xy,yaw=0):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(asset/name))
    obs=set(scene.objects)-prior
    from mathutils import Matrix
    mx=Matrix.Translation((*xy,0))@Matrix.Rotation(yaw,4,'Z')
    bpy.context.view_layer.update()
    for o in obs:
        if o.parent not in obs:o.matrix_world=mx@o.matrix_world

donor('e5b-alarm-gate-leaf.glb',(-3.98,5.2))
donor('e5b-alarm-gate-leaf.glb',(3.98,5.2),math.pi)
donor('haul-crate.glb',(4.8,1.32),.23)
donor('wsc-prop-009-stacked-pallets.glb',(-4.62,3.1),-.22)
scene.world=bpy.data.worlds.new('Cold dusk')
scene.world.color=(.072,.097,.128)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

for name,loc,target,power,size,col in [
    ('Overcast',(-3,-2,6),(0,0,0),1350,6,(.58,.76,1)),
    ('Dock glow',(5,4,5),(1,1,1),1000,4,(1,.63,.34)),
    ('Low bounce',(-4,1,3),(-1,3,1),440,3,(.47,.81,1)),
]:
    lamp=bpy.data.lights.new(name,'AREA');lamp.energy=power;lamp.size=size;lamp.color=col
    o=bpy.data.objects.new(name,lamp);scene.collection.objects.link(o);o.location=loc;aim(o,target)

data=bpy.data.cameras.new('Review photo')
cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.065
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.image_settings.file_format='PNG'
for tag,location,target,lens,width,height in [
    ('warning',(-.2,-5.5,1.7),(.04,.2,.45),24,900,1350),
    ('wave',(5.7,-7.5,5.0),(0,.45,.35),35,1420,930),
]:
    cam.location=location;aim(cam,target);data.lens=lens
    warning.hide_render=tag!='warning'
    transparent_extent=3.4*(.10+.90*.34/.46)
    warning.scale=(3.4,3.4,1)
    wave.scale=(transparent_extent,transparent_extent,1)
    wave.hide_render=tag!='wave'
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/f'nov25-e5a-{tag}.png')
    bpy.ops.render.render(write_still=True)
