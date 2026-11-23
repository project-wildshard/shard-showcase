"""Reduce the W11 wildflower geometry; preserve the exact close donor and colors."""
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

root = Path(__file__).resolve().parents[3] / 'public/assets/wildshard-art'
out = output_directory()
s = bpy.context.scene
source = root / 'wsc-prop-047-wildflower-clump.glb'
target = out / 'wsc-prop-047-wildflower-clump-far.glb'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'cb0c801b26ec3cb24412cbcffdd5950cb3cce629a8dd667c3bb0f5855717f696'

def load(path):
    prev = set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted((o for o in set(s.objects) - prev if o.type == 'MESH'),key=lambda o:o.name)

def mesh_stats(path):
    b = path.read_bytes()
    assert struct.unpack_from('<4sII', b) == (b'glTF',2,len(b))
    d = json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    assert not any(d.get(k) for k in ('images','animations','skins'))
    ps = [p for m in d['meshes'] for p in m['primitives']]
    assert all('COLOR_0' in p['attributes'] for p in ps)
    return {'bytes':len(b),'triangles':sum(d['accessors'][p['indices']]['count']//3 for p in ps),
            'primitives':len(ps)}

def world(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]

def tree(objects):
    vv, ff = [], []
    for o in objects:
        ff.extend(tuple(len(vv)+i for i in f.vertices) for f in o.data.polygons)
        vv.extend(world(o))
    return BVHTree.FromPolygons(vv,ff)

def bounds(objects):
    vs=[p for o in objects for p in world(o)]
    return [tuple(fn(v[i] for v in vs) for i in range(3)) for fn in (min,max)]

def measure(before,after):
    old,new=map(tree,(before,after))
    scores=[]
    for n,elev in product(range(8),(.08,.27)):
        theta = n * math.tau / 8
        ray = Vector((math.cos(theta),math.sin(theta),elev)).normalized()
        right=Vector((-math.sin(theta),math.cos(theta),0))
        up=ray.cross(right)
        base=Vector((0,0,.36))+ray*3
        both=union=0
        for x,y in product(range(100),range(70)):
            p=base+right*((x+.5-50)*.014)+up*((y+.5-35)*.014)
            a,b=(bvh.ray_cast(p,-ray,6)[0] is not None for bvh in (old,new))
            both+=a and b
            union+=a or b
        scores.append(both/union)
    return min(scores),sum(scores)/len(scores)

clear_scene()
near=load(source)
assert len(near)==2 and 'Meadow' in near[0].name and 'Lupine' in near[1].name
reduced=[]
for o,ratio in zip(near,(.44,.25)):
    q=o.copy()
    q.data=o.data.copy()
    q.name='Far · '+o.name
    s.collection.objects.link(q)
    bpy.context.view_layer.objects.active=q
    dec=q.modifiers.new('Distance geometry','DECIMATE')
    dec.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=dec.name)
    q.data.validate(verbose=False, clean_customdata=False)
    q.data.update()
    assert q.data.color_attributes
    reduced.append(q)
export(reduced,target)
again=load(target)
a,b=bounds(near),bounds(again)
worst,mean=measure(near,again)
before,after=map(mesh_stats,(source,target))
metrics={'asset_id':'WSC-PROP-047','near':before,'far':after,
         'near_bounds_m':a,'far_bounds_m':b,
         'mask_iou_min_16_angles':round(worst,4),'mask_iou_mean_16_angles':round(mean,4),
         'runtime_switch':False}
print(metrics,flush=True)
assert after['bytes'] < before['bytes']*.49 and after['triangles'] < before['triangles']*.35
assert after['primitives']==before['primitives']==2
assert worst >= .80 and mean >= .84
assert abs(a[0][2]-b[0][2])<.004 and abs(a[1][2]-b[1][2])<.025
(out/'validation.json').write_text(json.dumps(metrics,indent=2)+'\n')

def put(objects, move, scale=1, yaw=0):
    transform = (Matrix.Translation(move) @ Matrix.Rotation(math.radians(yaw),4,'Z')
                 @ Matrix.Scale(scale,4))
    for src in objects:
        o = bpy.data.objects.new(src.name + ' instance', src.data)
        s.collection.objects.link(o)
        o.matrix_world = transform @ src.matrix_world

def material(name,c):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes['Principled BSDF']
    n.inputs['Base Color'].default_value=(*c,1)
    n.inputs['Roughness'].default_value=.82
    return m

def ground(name,z,m):
    bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,z))
    o=bpy.context.object
    o.name=name
    o.data.materials.append(m)

def title(name, x, y, caption, ink):
    cu=bpy.data.curves.new(name,'FONT')
    cu.body=caption
    cu.align_x='CENTER'
    cu.size=.044
    cu.materials.append(ink)
    o=bpy.data.objects.new(name,cu)
    s.collection.objects.link(o)
    o.location=(x,y,.004)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def lamp(name,p,q,power,col,sz):
    l=bpy.data.lights.new(name,'AREA')
    l.energy=power
    l.color=col
    l.shape='DISK'
    l.size=sz
    o=bpy.data.objects.new(name,l)
    s.collection.objects.link(o)
    o.location=p
    aim(o,q)

def render(name,pos,q,scale,wh):
    c=bpy.data.cameras.new(name)
    s.camera=bpy.data.objects.new(name,c)
    s.collection.objects.link(s.camera)
    c.type='ORTHO'
    c.ortho_scale=scale
    s.camera.location=pos
    aim(s.camera,q)
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)

s.render.engine='CYCLES'
s.cycles.samples=52
s.cycles.use_denoising=False
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=90
s.world=bpy.data.worlds.new('Late morning bounce')
s.world.color=(.24,.27,.29)

# Identical sunlight, size, yaw and straight-on camera for the two editions.
clear_scene()
for x,asset in ((-.68,source),(.68,target)):
    os=load(asset)
    for o in os:
        o.location.x+=x
ground('Sea-green slate comparison stage',-.002,material('Slate',(.063,.107,.115)))
ink=material('Ivory lettering',(.74,.79,.67))
title('Near label',-.68,-.58,'ORIGINAL  /  20,622 TRI',ink)
title('Far label',.68,-.58,'DISTANT  /  5,556 TRI',ink)
lamp('Amber morning key',(-1.5,-2.7,3.5),(0,0,.3),380,(1,.83,.65),2.3)
lamp('Blue fill',(1,-.1,3),(0,0,.35),205,(.68,.84,1),1.9)
lamp('Light behind petals',(0,2,2),(0,0,.35),170,(1,.91,.70),2)
render('nov23-lookout-flowers-compare',(0,-4,2.25),(0,0,.33),2.72,(1500,790))

# W11-inspired dressing strip only. Exact donors are pinned, not duplicated.
clear_scene()
names=[
  ('wsc-prop-036-landscape-boulder','d03ed70f69d230fa82c474770eb65a991189cbf4848db4fc750ec1cb6f812750'),
  ('wsc-module-013-lookout-deck-bay','a4389e3c54174ddfab242953db8d12320980cb3b093443ea99c8aebeca4c0e75'),
  ('wsc-prop-044-lookout-bench','9109111c13a27c81981839237b9f1880c9e964930f5888e24c1054ac819bfeb1'),
  ('wsc-prop-045-lookout-timber-guardrail','5d3b70e33595a470e07595546dc6320369e0d125544e138e9941d4c2c6cbedb1'),
]
donors=[]
for name,sha in names:
    path=root/(name+'.glb')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
    donors.append(load(path))
flat,full=load(target),load(source)
boulder,bay,bench,rail=donors
for o in [o for os in donors+[flat,full] for o in os]:
    o.hide_render=True
for x,y,k,r in ((-1.74,-1.38,.66,22),(-2.25,.67,.63,-13),
                (-1.82,2.6,.53,8),(-2.7,3.88,.92,-3),(1.98,4.02,.58,35)):
    put(boulder,(x,y,-.19),k,r)
for y in (-1.40,1.40,4.20):
    put(bay,(.33,y,-.08))
put(bench,(.4,.51,.08),.93,90)
put(rail,(.32,3.13,.09),1.39,0)
for i,(x,y,k) in enumerate(((-1.46,-.9,.87),(-1.84,-.67,.68),(-1.24,-.21,.50),
    (-1.69,.01,.74),(-1.52,.57,.85),(-2.14,1.21,.57),(-1.56,1.75,.91),
    (-1.43,2.26,.73),(-1.33,2.52,.48),(-1.62,2.90,.70),(-1.28,3.28,.61),
    (-.68,3.75,.56),(.83,3.93,.74),(1.61,3.47,.53),(1.95,2.60,.72))):
    put(full if i<3 else flat,(x,y,-.095),k,(i*63)%360)
soil=material('Sandstone ochre soil',(.225,.213,.09))
n=soil.node_tree.nodes
link=soil.node_tree.links.new
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6.5
tex=n.new('ShaderNodeTexCoord');link(tex.outputs['Object'],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=(.089,.105,.038,1)
ramp.color_ramp.elements[1].color=(.30,.23,.079,1)
link(noise.outputs['Fac'],ramp.inputs[0])
link(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
bump=n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.36
bump.inputs['Distance'].default_value=.085
link(noise.outputs['Fac'],bump.inputs['Height'])
link(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
ground('W11 warm terrain',-.10,soil)
lamp('Warm West-facing sun',(-4,-1,7),(0,1,0),1900,(1,.78,.57),3)
lamp('Open sky',(2,5,6),(-.5,1,0),1250,(.69,.83,1),6)
render('nov23-lookout-flowers-border',(3.7,-6.2,4.38),(-.31,.89,.22),6.7,(1360,1000))
