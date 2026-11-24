"""Matched Blender material study on exact WSC-PROP-020/021; no GLB changes."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

out=output_directory()
assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
pairs=[
    ('Spool','wsc-prop-020-cable-spool.glb','f6aee08b1e445990bf6b5334c62966567f59008f8298b9db11bd9ab2fdcb2210',(-.75,.04,0),.33),
    ('Barrel','wsc-prop-021-timber-barrel.glb','29a14a74d50ebd5c7b05a23fae9b85e762193681cebcb2d8da85ac14ca17664f',(.68,.17,0),.31),
]
for _,f,h,*_ in pairs:
    assert hashlib.sha256((assets/f).read_bytes()).hexdigest()==h
clear_scene()
s=bpy.context.scene
objects={}
origin={}
for key,f,_,loc,angle in pairs:
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/f))
    new=sorted(set(s.objects)-old,key=lambda o:o.name)
    tf=Matrix.Translation(loc)@Matrix.Rotation(angle,4,'Z')
    for o in new:
        if o.parent is None:o.matrix_world=tf@o.matrix_world
    objects[key]=[o for o in new if o.type=='MESH']
    coord=bpy.data.objects.new(key+' shared material frame',None)
    s.collection.objects.link(coord);coord.matrix_world=tf;origin[key]=coord
bpy.context.view_layer.update()

def fingerprint():
    # World-space geometry and exact placement invariant, not just vertex count.
    h=hashlib.sha256()
    for group in objects.values():
        for o in group:
            h.update(o.name.encode())
            for v in o.data.vertices:
                h.update(repr(tuple(o.matrix_world@v.co)).encode())
            for p in o.data.polygons:
                h.update(repr(tuple(p.vertices)).encode())
    return h.hexdigest()
before=fingerprint()

def get_nt(m):
    m.use_nodes=True
    nt=m.node_tree
    return nt,nt.nodes.get('Principled BSDF')
def tex(nt,obj,vec,scale,detail):
    t=nt.nodes.new('ShaderNodeTexCoord');t.object=obj
    z=nt.nodes.new('ShaderNodeVectorMath');z.operation='MULTIPLY';z.inputs[1].default_value=vec
    nt.links.new(t.outputs['Object'],z.inputs[0])
    n=nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value=scale
    n.inputs['Detail'].default_value=detail
    n.inputs['Roughness'].default_value=.61
    nt.links.new(z.outputs['Vector'],n.inputs['Vector'])
    return n
def ramp(nt,n,stops):
    cr=nt.nodes.new('ShaderNodeValToRGB')
    r=cr.color_ramp
    r.elements[0].position,r.elements[0].color=stops[0]
    r.elements[1].position,r.elements[1].color=stops[-1]
    for (p,c) in stops[1:-1]:
        e=r.elements.new(p);e.color=c
    nt.links.new(n.outputs['Fac'],cr.inputs['Fac'])
    return cr
def bump(nt,p,n,depth,strength):
    b=nt.nodes.new('ShaderNodeBump')
    b.inputs['Distance'].default_value=depth;b.inputs['Strength'].default_value=strength
    nt.links.new(n.outputs['Fac'],b.inputs['Height'])
    nt.links.new(b.outputs['Normal'],p.inputs['Normal'])

def wood(orig,obj,key):
    m=orig.copy();m.name=key+' fibre and abrasion'
    nt,p=get_nt(m)
    color=tuple(p.inputs['Base Color'].default_value)
    # Short-radius, long-axis fibre; object frame is shared across disconnected boards.
    axis=(1.9,58,29) if key=='Spool' else (47,47,1.6)
    grain=tex(nt,obj,axis,2.9,3.4)
    values=[(.15,.39),(.38,.69),(.56,1.02),(.79,1.42)]
    cr=ramp(nt,grain,[(pos,tuple(min(1,v*k) for v in color[:3])+(1,)) for pos,k in values])
    nt.links.new(cr.outputs['Color'],p.inputs['Base Color'])
    rr=ramp(nt,grain,[(.21,(.56,.56,.56,1)),(.78,(.84,.84,.84,1))])
    nt.links.new(rr.outputs['Color'],p.inputs['Roughness'])
    bump(nt,p,grain,.0014,.48)
    return m

def metal(orig,obj,key):
    m=orig.copy();m.name=key+' oxide and galvanized patches'
    nt,p=get_nt(m)
    rust=tex(nt,obj,(7.4,7.4,14),2.55,3.1)
    c=tuple(p.inputs['Base Color'].default_value)
    cc=ramp(nt,rust,[
        (.14,(.103,.039,.024,1)),(.37,(.155,.065,.035,1)),
        (.49,tuple(v*.73 for v in c[:3])+(1,)),(.82,tuple(min(v*1.55,1) for v in c[:3])+(1,))])
    nt.links.new(cc.outputs['Color'],p.inputs['Base Color'])
    rr=ramp(nt,rust,[(.25,(.83,.83,.83,1)),(.80,(.39,.39,.39,1))])
    nt.links.new(rr.outputs['Color'],p.inputs['Roughness'])
    mtl=ramp(nt,rust,[(.24,(.19,.19,.19,1)),(.68,(.67,.67,.67,1))])
    nt.links.new(mtl.outputs['Color'],p.inputs['Metallic'])
    bump(nt,p,tex(nt,obj,(89,89,55),2.5,2.8),.0009,.35)
    return m

edits=[]
for key,group in objects.items():
    cache={}
    for o in group:
        for slot in o.material_slots:
            src=slot.material
            n=src.name.lower().split('.')[0]
            construct=(wood if n.startswith('wood') else metal if n in ['iron','iron_dark'] else None)
            if not construct:continue
            if src not in cache:cache[src]=construct(src,origin[key],key)
            edits.append((slot,src,cache[src],key,n))
assert all(any(e[3]==key and e[4].startswith('wood') for e in edits) and any(
    e[3]==key and e[4]=='iron' for e in edits) for key in objects)
assert before==fingerprint()
proof={'donor_ids':['WSC-PROP-020','WSC-PROP-021'],
       'geometry_placement_signature':before,'altered_slots':[(key,n) for *_,key,n in edits],
       'native_shaders_or_glbs_changed':False}
(out/'timber-hardware-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006))
o=bpy.context.object;o.name='Wet charcoal floor | staged only'
m=bpy.data.materials.new('Review ground')
nt,p=get_nt(m);p.inputs['Base Color'].default_value=(.066,.086,.095,1)
p.inputs['Roughness'].default_value=.66;o.data.materials.append(m)
s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.22,.30,.41,1);bg.inputs[1].default_value=.43
for pos,pow,sz,col in [
    ((-2.6,-3.25,3.68),570,3.0,(1,.83,.65)),
    ((2.8,.6,3),685,2.4,(.66,.84,1)),
    ((.45,3.3,3.6),580,2.8,(1,.68,.38))
]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    o=bpy.context.object;o.data.energy=pow;o.data.size=sz;o.data.color=col;aim(o,(0,0,.46))
bpy.ops.object.camera_add(location=(2.8,-5.6,2.47))
s.camera=bpy.context.object;aim(s.camera,(0,0,.54))
s.camera.data.lens=56
s.render.engine='CYCLES';s.cycles.samples=42;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.042
s.render.resolution_x=1440;s.render.resolution_y=940;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=93
s.view_settings.view_transform='AgX'
for label,on in [('timber-original',False),('timber-worn',True)]:
    for slot,orig,new,*_ in edits:slot.material=new if on else orig
    assert fingerprint()==before
    s.render.filepath=str(out/(label+'.jpg'))
    bpy.ops.render.render(write_still=True)

if os.getenv('WILDSHARD_SAVE_BLEND')=='1':
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'timber-hardware-editable.blend'))
