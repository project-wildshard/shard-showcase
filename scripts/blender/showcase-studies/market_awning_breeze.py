"""WSC-PROP-005: a small offline cloth loop extracted from the pinned stall."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

here=Path(__file__).resolve()
sys.path.insert(0,str(here.parent))
from common import clear_scene, output_directory

out=output_directory()
clear_scene()
scene=bpy.context.scene
scene.render.fps=24
scene.frame_start,scene.frame_end=0,72
donor=here.parents[3]/'public/assets/wildshard-art/market-awning-stall.glb'
pin='b240fd8056db68d9b1caeaefc61459de4171f1345782726b0da40d0a1c614f04'
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
bpy.ops.import_scene.gltf(filepath=str(donor))
old=list(scene.objects)
source=next(o for o in old if o.type=='MESH')
assert sum(o.type=='MESH' for o in old)==1
points=[source.matrix_world@v.co for v in source.data.vertices]
faces=[tuple(p.vertices) for p in source.data.polygons]
mids=[p.material_index for p in source.data.polygons]
mats=list(source.data.materials)
cloth_mat={'canvas','saffron','linen'}
cloth_face=[i for i,f in enumerate(faces)
            if mats[mids[i]].name in cloth_mat and min(points[j].z for j in f)>2.30]
static_face=sorted(set(range(len(faces)))-set(cloth_face))
assert len(cloth_face)>3500 and len(static_face)>2000


def partition(name,indices):
    use=sorted({j for i in indices for j in faces[i]})
    mapper={j:k for k,j in enumerate(use)}
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([points[j] for j in use],[],
                     [tuple(mapper[j] for j in faces[i]) for i in indices])
    used_mats=sorted({mids[i] for i in indices})
    for i in used_mats:mesh.materials.append(mats[i])
    for f,i in zip(mesh.polygons,indices):
        f.material_index=used_mats.index(mids[i])
        f.use_smooth=source.data.polygons[i].use_smooth
    for layer in source.data.uv_layers:
        new=mesh.uv_layers.new(name=layer.name,do_init=False)
        for f,i in zip(mesh.polygons,indices):
            old_face=source.data.polygons[i]
            for new_loop,old_loop in zip(f.loop_indices,old_face.loop_indices):
                new.data[new_loop].uv=layer.data[old_loop].uv
    normal_vectors=[source.data.corner_normals[j].vector.copy()
                    for i in indices for j in source.data.polygons[i].loop_indices]
    mesh.normals_split_custom_set(normal_vectors)
    o=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(o)
    return o,[points[j] for j in use]

canopy,verts=partition('MarketAwning_Canvas',cloth_face)
stand,_=partition('Pinned stall, rigid parts',static_face)
for o in old:bpy.data.objects.remove(o,do_unlink=True)
basis=canopy.shape_key_add(name='Donor rest')
positive=canopy.shape_key_add(name='Market lee ripple')
negative=canopy.shape_key_add(name='Market windward ripple')


def envelope(p):
    x,y,z=p
    along=min(1,max(0,(1.43-abs(x))/.29))
    across=min(1,max(0,(abs(y)-.16)/.70))
    hem=min(1,max(0,(2.43-z)/.11))
    # Ridge and eave hardware remain fixed. Scallops below the rigid rod
    # have a separate envelope; fields bow inside the secured rod/ridge.
    field=along*math.sin(math.pi*across)**2
    tail=along*hem*across**2
    return field,tail


for i,p in enumerate(verts):
    a,b=envelope(p)
    wave=math.sin(4.2*p.x+1.1*p.y)
    z=.026*a*wave+.058*b*(.83+.17*wave)
    y=.014*a*wave+math.copysign(.038*b,p.y)
    delta=Vector((0,y,z))
    positive.data[i].co=p+delta
    negative.data[i].co=p-delta*.82
    if abs(p.y)<=.16 or abs(p.x)>=1.43:
        assert delta.length<1e-8

for f,p,n in ((0,0,0),(12,.58,0),(22,1,0),(34,0,0),
              (46,0,1),(58,0,.36),(72,0,0)):
    for k,v in ((positive,p),(negative,n)):
        k.value=v
        k.keyframe_insert('value',frame=f)
canopy.data.shape_keys.animation_data.action.name='Market awning · light breeze'
bpy.ops.object.select_all(action='DESELECT')
canopy.select_set(True)
bpy.context.view_layer.objects.active=canopy
scene.frame_set(0)
path=out/'wsc-prop-005-market-awning-breeze.glb'
bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB',
                         use_selection=True,export_animations=True,
                         export_animation_mode='ACTIONS',export_force_sampling=False,
                         export_morph_normal=False)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(doc['nodes'])==len(doc['meshes'])==len(doc['animations'])==1
assert not any(k in doc for k in ('skins','cameras'))
assert {img['name'] for img in doc['images']}=={'canvas','linen'}
assert all('bufferView' in img and 'uri' not in img for img in doc['images'])
assert all('TEXCOORD_0' in p['attributes'] for p in doc['meshes'][0]['primitives'])
assert len(raw)<310000

bpy.data.objects.remove(canopy,do_unlink=True)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(path))
(canopy,)=(o for o in set(scene.objects)-before if o.type=='MESH')
sk=canopy.data.shape_keys
assert len(sk.key_blocks)==3 and tuple(sk.animation_data.action.frame_range)==(0,72)
actual=[canopy.matrix_world@v.co for v in sk.key_blocks[0].data]
for left,right in [(actual,verts),(verts,actual)]:
    tree=KDTree(len(right))
    for i,p in enumerate(right):tree.insert(p,i)
    tree.balance()
    assert max(tree.find(p)[2] for p in left)<2e-6


def pose(f):
    scene.frame_set(f)
    ev=canopy.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [canopy.matrix_world@v.co for v in ev.data.vertices]


p0,p1,p2,p72=[pose(f) for f in (0,22,46,72)]
loop=max((a-b).length for a,b in zip(p0,p72))
peak=max((a-b).length for a,b in zip(p0,p1))
swing=max((a-b).length for a,b in zip(p1,p2))
pins=[i for i,p in enumerate(p0) if abs(p.y)<=.16 or abs(p.x)>=1.43]
pin_motion=max((p1[i]-p0[i]).length for i in pins)
assert loop<1e-6 and pin_motion<1e-6 and .035<peak<.075 and .07<swing<.13
report={'donor':donor.name,'donor_sha256':pin,'frames':[0,72],'seconds':3,
        'canopy_triangle_count':sum(doc['accessors'][p['indices']]['count']//3
                                    for p in doc['meshes'][0]['primitives']),
        'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
        'rest_to_peak_m':round(peak,5),'peak_to_peak_m':round(swing,5),
        'first_last_max_m':round(loop,7),'fixed_ridge_or_outer_points':len(pins),
        'fixed_points_max_m':round(pin_motion,7),
        'scope':'Canopy replacement only. Omit fixed donor cloth when installing; not a wind or cloth simulation.'}
(out/'awning-breeze.json').write_text(json.dumps(report,indent=2)+'\n')

world=bpy.data.worlds.new('Market afternoon')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.34,.53,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
scene.world=world
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.012))
floor=bpy.data.materials.new('Limestone floor')
floor.diffuse_color=(.43,.32,.206,1)
bpy.context.object.data.materials.append(floor)
for name,pos,target,power,col,size in (
   ('Warm shop sun',(-3,-4,7),(0,0,1.6),1950,(1,.86,.68),5.0),
   ('Soft cool fill',(2,-4,3),(0,0,2.2),670,(.69,.82,1),4.1),
   ('Canopy rim lamp',(0,3,6),(0,0,2.4),940,(1,.84,.65),3.0)):
    d=bpy.data.lights.new(name,'AREA');d.energy,d.color,d.size=power,col,size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Canopy review camera',bpy.data.cameras.new('Canopy review camera'))
scene.collection.objects.link(cam)
scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=46;scene.cycles.use_denoising=False
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=91;scene.view_settings.view_transform='AgX'


def shot(name,f,pos,target,lens,w,h):
    scene.frame_set(f)
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=w,h
    scene.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)


shot('stall',22,(2.94,-4.9,3.65),(0,0,1.49),52,1050,1000)
for name,f in [('lee',22),('windward',46)]:
    shot(name,f,(.72,-4.2,2.62),(0,-.20,2.51),53,1120,620)
