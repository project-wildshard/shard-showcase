"""WSC-PROP-025: original painted face, fewer triangles in its metal surround."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export

root = Path(__file__).resolve().parents[3]
source = root / 'public/assets/wildshard-art/wsc-prop-025-bullseye-target.glb'
pin = 'a55a951a51dd6ab46f9f0e9cc4b879d1df74d5609cb02e25ae8095a6bcc36c0a'
assert hashlib.sha256(source.read_bytes()).hexdigest() == pin
args = sys.argv[sys.argv.index('--') + 1:]
out = Path(args[0]).resolve()
out.mkdir(parents=True, exist_ok=True)
clear_scene()
s = bpy.context.scene

def load(path):
    old = set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted((o for o in set(s.objects)-old if o.type == 'MESH'), key=lambda o:o.name)

def glb_info(path):
    raw = path.read_bytes()
    n = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+n])
    parts = {doc['materials'][p['material']]['name']:doc['accessors'][p['indices']]['count']//3
             for m in doc['meshes'] for p in m['primitives']}
    blob = raw[28+n:]
    tex = []
    for m in doc['materials']:
        t = m.get('pbrMetallicRoughness',{}).get('baseColorTexture')
        if t is not None:
            i = doc['images'][doc['textures'][t['index']]['source']]
            v = doc['bufferViews'][i['bufferView']]
            start = v.get('byteOffset',0)
            tex.append((m['name'], hashlib.sha256(blob[start:start+v['byteLength']]).hexdigest()))
    return dict(file=path.name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                triangles=sum(parts.values()), parts=parts, images=len(doc.get('images',[])), face_textures=dict(tex))

near, = load(source)
base = glb_info(source)
hardware = {'Rubbed pewter', 'Graphite hardware'}
face_names = set(base['parts']) - hardware
face_slots = {i for i,m in enumerate(near.data.materials) if m.name in face_names}
assert len(face_slots) == 3
assert base['triangles'] == 7688
bpy.ops.object.select_all(action='DESELECT')

def isolate(name, slots, simplify=False):
    ob = near.copy()
    ob.data = near.data.copy()
    ob.name = name
    s.collection.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in slots], context='FACES')
    if simplify:
        # No paint or UV seams are involved. Weld split export vertices first.
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bm.to_mesh(ob.data)
    bm.free()
    if simplify:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        mod = ob.modifiers.new('Hardware distance trim', 'DECIMATE')
        mod.ratio = .30
        bpy.ops.object.modifier_apply(modifier=mod.name)
        ob.select_set(False)
    return ob

paint = isolate('Paint and rim (unchanged)',face_slots)
metal = [isolate(near.data.materials[i].name+' (trimmed)',{i},True)
         for i in range(len(near.data.materials)) if i not in face_slots]
for o in metal:
    o.select_set(True)
paint.select_set(True)
bpy.context.view_layer.objects.active = paint
bpy.ops.object.join()
paint.name = 'WSC-PROP-025 | Distance'
file = out / 'wsc-prop-025-bullseye-distance.glb'
export([paint],file)
bpy.data.objects.remove(paint,do_unlink=True)
far, = load(file)
dist = glb_info(file)
assert set(dist['parts']) == set(base['parts'])
assert dist['triangles'] < base['triangles']*.45 and dist['bytes'] < base['bytes']*.8,dist
assert dist['images'] == base['images'] == 2
assert dist['face_textures'] == base['face_textures']

def surface_signature(ob):
    m = ob.data
    uv = m.uv_layers.active.data
    m.calc_loop_triangles()
    return Counter((m.materials[t.material_index].name.split('.00')[0],
                    tuple(sorted(tuple(round(x,6) for x in (*tuple(ob.matrix_world @ m.vertices[m.loops[i].vertex_index].co),*uv[i].uv))
                          for i in t.loops)))
                   for t in m.loop_triangles if m.materials[t.material_index].name.split('.00')[0] in face_names)

assert surface_signature(near) == surface_signature(far), 'paint position or UV changed'

def geometry(ob):
    m = ob.data
    m.calc_loop_triangles()
    w = [ob.matrix_world @ v.co for v in m.vertices]
    return w,BVHTree.FromPolygons(w,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)

npts, nt = geometry(near)
fpts, ft = geometry(far)
def bounds(v):
    return [[round(fn(x[i] for x in v),6) for i in range(3)] for fn in (min,max)]
nb, fb = bounds(npts),bounds(fpts)
err = max(abs(a-b) for row1,row2 in zip(nb,fb) for a,b in zip(row1,row2))
assert err < .002
view_meta=[]
for angle in (0,30,60,90,135,180):
    th=math.radians(angle)
    eye=Vector((math.sin(th),-math.cos(th),0))
    right=Vector((math.cos(th),math.sin(th),0))
    total=shared=0
    for u in range(120):
        for v in range(192):
            p=eye*3+right*((u+.5)/120*1.26-.63)+Vector((0,0,(v+.5)/192*1.94))
            a=nt.ray_cast(p,-eye,7)[0] is not None
            b=ft.ray_cast(p,-eye,7)[0] is not None
            total+=a or b
            shared+=a and b
    view_meta.append(dict(yaw_deg=angle,intersection_over_union=round(shared/total,6)))
print(view_meta,flush=True)
assert min(x['intersection_over_union'] for x in view_meta)>=.970
(out/'proof.json').write_text(json.dumps(dict(
    scope='Static phone-distance art option; no runtime LOD, interaction, scoring or device benchmark.',
    original=base,distance=dist,original_bounds_blender_m=nb,distance_bounds_blender_m=fb,
    max_bound_delta_m=round(err,6),paint_rim_triangles_uv_match=sum(surface_signature(near).values()),
    rays_per_view=120*192,views=view_meta),indent=2)+'\n')
if '--proof-only' in args:
    raise SystemExit(0)

def material(name,color,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*color,1)
    q.inputs['Roughness'].default_value=roughness
    return m

ground_mat=material('Review sandy screed',(.202,.167,.107),.88)
q=ground_mat.node_tree.nodes.get('Principled BSDF')
noise=ground_mat.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=37
bump=ground_mat.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25
bump.inputs['Distance'].default_value=.023
ground_mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
ground_mat.node_tree.links.new(bump.outputs['Normal'],q.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=130,location=(0,-24,-.002))
bpy.context.object.data.materials.append(ground_mat)
s.world=bpy.data.worlds.new('Soft blue sky');s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.39,.56,.72,1);bg.inputs[1].default_value=.56
light=bpy.data.lights.new('Afternoon light','SUN');light.energy=2.6;light.color=(1,.85,.68);light.angle=.12
sun=bpy.data.objects.new(light.name,light);s.collection.objects.link(sun)
sun.rotation_euler=Vector((.40,.58,-1)).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
cam=bpy.context.object;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.085;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_x=520;s.render.resolution_y=740
s.render.resolution_percentage=100

def render(label,A,B,place,focus=False):
    A.hide_render=False;B.hide_render=True
    cam.location=place
    cam.data.lens=43 if focus else 32
    target=Vector((0,0,1.22))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(out/(label+'.png'))
    bpy.ops.render.render(write_still=True)

for mode,a,b in [('original',near,far),('distance',far,near)]:
    render(mode+'-front',a,b,(0,-2.9,1.52),True)
    for d in (10,30,50):
        render(f'{mode}-{d}m',a,b,(0,-d,1.70))
