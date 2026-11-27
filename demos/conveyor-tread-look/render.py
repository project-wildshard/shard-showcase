"""Matched Blender evidence. The tile comes from the tested Three.js adapter."""
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'scripts/blender/showcase-studies'))
from common import clear_scene
root=HERE.parents[1]
A=root/'public/assets/wildshard-art'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(exist_ok=True,parents=True)
payload=(out/'tile.rgba').read_bytes();assert len(payload)==512
pattern=bpy.data.images.new('Exact Three 128 x 1 tread tile',width=128,height=1)
pattern.colorspace_settings.name='Non-Color'
pattern.pixels[:]=[i/255 for i in payload]
clear_scene()
s=bpy.context.scene
period=1.32
def load(file):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(A/file))
    return sorted(set(s.objects)-before,key=lambda o:o.name)
group=[]
for x,v,turn in [(-84,-3,0),(-90,-4,3.141592653589793),(-96,-5,0)]:
    T=Matrix.Translation((x,103,.10))@Matrix.Rotation(turn,4,'Z')
    belt=load('wsc-prop-037-conveyor-module.glb')
    donors=load('wsc-prop-037-conveyor-direction.glb')
    maps=[]
    for o in belt:
        if o.type!='MESH':continue
        d=o.data
        uv=d.uv_layers.new(name='Belt repeat')
        for f in d.polygons:
            for i in f.loop_indices:
                q=d.vertices[d.loops[i].vertex_index].co
                uv.data[i].uv=(q.x/period,.5)
        for i,m in enumerate(d.materials):
            if not m.name.startswith('Rubber tread'):continue
            m=m.copy();d.materials[i]=m
            n=m.node_tree.nodes;links=m.node_tree.links
            bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
            base=tuple(bs.inputs['Base Color'].default_value)
            tex=n.new('ShaderNodeTexImage');tex.image=pattern;tex.extension='REPEAT'
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY'
            mix.inputs['Fac'].default_value=1;mix.inputs[1].default_value=base
            map=n.new('ShaderNodeMapping');tc=n.new('ShaderNodeUVMap');tc.uv_map=uv.name
            links.new(tc.outputs['UV'],map.inputs['Vector'])
            links.new(map.outputs['Vector'],tex.inputs['Vector'])
            links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs['Color'],bs.inputs['Base Color'])
            maps.append(map)
    assert len(maps)==3
    for o in belt+donors:
        if o.parent not in belt+donors:o.matrix_world=T@o.matrix_world
    group.append((v,maps))
def box(name,p,d,rgb):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d
    b=bpy.data.materials.new(name);b.use_nodes=True
    q=b.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*rgb,1)
    q.inputs['Roughness'].default_value=.86
    o.data.materials.append(b)
box('Rebuilt station slab',(-90,103,.045),(20,5,.09),(.23,.255,.238))
box('Presentation ground',(-90,103,-.13),(150,140,.25),(.068,.092,.095))
for y in (101.07,104.93):
    for x in range(-98,-80,2):
        box('Slab safety line', (x,y,.091),(.8,.049,.002),(.58,.33,.067))
s.world=bpy.data.worlds.new('West daylight')
s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.34,.50,.63,1);bg.inputs[1].default_value=.53
def lamp(name,kind,p,target,energy,color,size):
    d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=color
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
lamp('West afternoon','SUN',(-82,94,10),(-91,103,0),2.9,(1,.86,.67),.24)
lamp('Tread fill','AREA',(-90,106,5),(-90,103,.48),840,(.65,.87,1),8)
c=bpy.data.cameras.new('Tread Review')
obj=bpy.data.objects.new(c.name,c);s.collection.objects.link(obj);s.camera=obj
s.render.engine='CYCLES';s.cycles.samples=28;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.034
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=92
s.view_settings.view_transform='AgX';s.view_settings.exposure=.8
for stem,t,p,q,scale,w,h in [
    ('overview',.233,(-83.75,95.7,10),(-90,103,.33),21.4,1380,840),
    ('phase-a',0,(-84.3,100,6.3),(-84,103,.45),5.8,1160,850),
    ('phase-b',.137,(-84.3,100,6.3),(-84,103,.45),5.8,1160,850),
]:
    for v,maps in group:
        for m in maps:m.inputs['Location'].default_value[0]=(-v*t/period)%1
    obj.location=p;obj.rotation_euler=(Vector(q)-obj.location).to_track_quat('-Z','Y').to_euler()
    c.type='ORTHO';c.ortho_scale=scale
    s.render.resolution_x=w;s.render.resolution_y=h
    s.render.filepath=str(out/(stem+'.jpg'));bpy.ops.render.render(write_still=True)
