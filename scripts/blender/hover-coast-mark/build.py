"""W5a: thin coasting cue on the verified high receiver. No collider."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

out=Path(sys.argv[sys.argv.index('--')+1])
out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[3]
path=root/'public/assets/wildshard-art/w5a-high-kicker-receiver.glb'
pin='287034facd39d323ee6e9af95912c053a3506d6fe3f788e012c4f58158f3be7f'
assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(path))
deck=set(S.objects)
surf,=[ob for ob in deck if 'Riding Surface' in ob.name]
bpy.context.view_layer.update()

def vertices(ob):
    return [ob.matrix_world@p.co for p in ob.data.vertices]
def tree(obs):
    vs=[]; fs=[]
    for ob in obs:
        n=len(vs)
        vs.extend(vertices(ob))
        fs.extend(tuple(n+i for i in p.vertices) for p in ob.data.polygons)
    return BVHTree.FromPolygons(vs,fs)

support=tree([surf])
def floor(x,y):
    hit= support.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),15)[0]
    assert hit is not None,(x,y)
    return hit.z

def mat(name,rgb):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    q=m.node_tree.nodes['Principled BSDF']
    q.inputs['Base Color'].default_value=(*rgb,1)
    q.inputs['Roughness'].default_value=.88
    return m
cream=mat('Warm chalk mineral pigment',(.91,.80,.55))
amber=mat('Amber inset paint',(.73,.28,.08))
center=-170.08+167.39
z=floor(center,0)+.002
bpy.ops.object.text_add(location=(0,0,z))
text=bpy.context.object
text.data.body='EASE OFF'
text.data.align_x='CENTER'
text.data.align_y='CENTER'
text.data.space_character=1.08
text.data.resolution_u=3
bpy.ops.object.convert(target='MESH')
ob=bpy.context.object
width=ob.dimensions.x
ob.scale=(3.15/width,1.14/ob.dimensions.y,1)
ob.rotation_euler.z=math.pi/2
ob.location.x=center
ob.name='Direction-facing mineral lettering'
ob.data.materials.append(cream)

def marks():
    vs=[];fs=[]
    for side in (-1,1):
        for f in (0,.20,.40):
            x=center-.63+f
            y=side*1.88
            n=len(vs)
            vs.extend([(x-.047,y-.105,z),(x+.047,y-.105,z),(x+.047,y+.105,z),(x-.047,y+.105,z)])
            fs.append(tuple(range(n,n+4)))
    m=bpy.data.meshes.new('Six paint flecks')
    m.from_pydata(vs,[],fs);m.update()
    o=bpy.data.objects.new('Narrow shoulder marks',m)
    S.collection.objects.link(o)
    m.materials.append(amber)
    return o
accent=marks()
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for o in (ob,accent):o.select_set(True)
p=out/'w5a-high-receiver-ease-off.glb'
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_animations=False)
for o in (ob,accent):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(p))
bpy.context.view_layer.update()
overlay=set(S.objects)-deck
vs=[v for o in overlay for v in vertices(o)]
gaps=[v.z-floor(v.x,v.y) for v in vs]
assert min(gaps)>.0018 and max(gaps)<.0022
x=[v.x-167.39 for v in vs]
assert min(x)>-171 and max(x)<-169
marg=2.3-max(abs(v.y) for v in vs)
assert marg>.29
proof=json.loads((root/'project/layouts/w5a-launch-wall-contact-proof.json').read_text())
early=[a for a in proof['runs'] if a['releaseX']==-171 and a['installed']]
early_clear=min(a['minX']-proof['wallX'] for a in early)
assert len(early)==3 and early_clear>3.17
b=p.read_bytes()
j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert 'images' not in j and 'animations' not in j
tris=sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])
S.render.engine='CYCLES'
S.cycles.samples=24
S.cycles.use_denoising=False
S.render.image_settings.file_format='WEBP'
S.render.image_settings.quality=88
S.world=bpy.data.worlds.new('Clear afternoon')
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.49,.61,.74,1)
S.world.node_tree.nodes['Background'].inputs[1].default_value=.63
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler=Vector((-.7,.40,-1)).to_track_quat('-Z','Y').to_euler()
bpy.context.object.data.energy=2.15
bpy.context.object.data.color=(1,.89,.73)
bpy.ops.mesh.primitive_plane_add(size=160,location=(-15,0,.025))
bpy.context.object.data.materials.append(mat('Review paving',(.26,.30,.31)))
bpy.ops.object.camera_add()
C=bpy.context.object
S.camera=C
views={}
lettering=[v for o in overlay if 'lettering' in o.name for v in vertices(o)]
for key,eye,dst,lens,dims in (
    ('rider',(2.4,0,6.55),(-5.5,0,4.6),29,(840,1440)),
    ('deck',(-.1,-6.7,10.2),(-5.0,0,4.6),30,(1240,840)),
):
    C.location=eye
    C.rotation_euler=(Vector(dst)-C.location).to_track_quat('-Z','Y').to_euler()
    C.data.lens=lens
    S.render.resolution_x,S.render.resolution_y=dims
    bpy.context.view_layer.update()
    box=[world_to_camera_view(S,C,v) for v in lettering]
    assert box and all(.02<v.x<.98 and .02<v.y<.98 and v.z>0 for v in box),key
    views[key]={'glyph_width_px':round((max(v.x for v in box)-min(v.x for v in box))*dims[0]),
                'glyph_height_px':round((max(v.y for v in box)-min(v.y for v in box))*dims[1])}
    if os.environ.get('WSC_COAST_RENDER')=='1':
        S.render.filepath=str(out/f'nov26-hover-ease-off-{key}.webp')
        bpy.ops.render.render(write_still=True)
(out/'w5a-high-receiver-ease-off-proof.json').write_text(json.dumps({
 'scope':'Art only, no collider, input behavior or live install. Earlier straight-line bench reused for placement reference.',
 'receiver_sha256':pin,'cue_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'triangles':tris,
 'three_origin':[-167.39,0,154], 'world_x_fit':[round(min(x),3),round(max(x),3)],
 'deck_offset_mm':[round(min(gaps)*1000,3),round(max(gaps)*1000,3)],'min_outer_edge_margin_m':round(marg,3),
 'prior_exact_wall_early_release_at_x':-171,'prior_min_stopped_short_m':round(early_clear,3),
 'views':views,
},indent=2)+'\n')
