"""Dress measured server poses with the original boards. Review render, not a client."""
import json
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

root = Path(__file__).resolve().parents[2]
source, trace, out = map(Path, sys.argv[sys.argv.index('--') + 1:])
out.mkdir(parents=True, exist_ok=True)
sign = runpy.run_path(str(root/'scripts/blender/west-scene-r02/semantic_glb.py'))['signature']
expected = json.loads((root/'scripts/blender/west-movers-roof/expected.json').read_text())['junction']['semantic_signature']
assert list(sign(source)) == expected
data = json.loads(trace.read_text())
links = data['summary']['N']
round_trip = 'cases' in data
assert links in (18, 27)
if round_trip:
    assert links == 18 and len(data['cases']) == 10
else:
    assert data['summary']['legacyRebuiltBodies'] == links
# Format/Three Y-up to Blender Z-up; same basis used by Blender GLB reimport.
F = Matrix(((1,0,0),(0,0,-1),(0,1,0)))
def xyz(p):
    return F @ Vector(tuple(p[k] for k in 'xyz'))
def rot(q):
    return F @ Quaternion(tuple(q[k] for k in 'wxyz')).to_matrix() @ F.transposed()

s = bpy.context.scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(source))
bpy.context.view_layer.update()
A,B = (xyz(data['summary'][i]) for i in ('a','b'))
D = (B-A).normalized()
side = Vector((-D.y,D.x,0))
boards = sorted((o for o in s.objects if o.type=='MESH' and 'individual cedar plank' in o.name),
                key=lambda o:(o.matrix_world.translation-A).dot(D))
assert len(boards)==54 and len(boards) % links == 0
boards_per_link = len(boards) // links
original = [o.matrix_world.copy() for o in boards]
for o in s.objects:
    if o.type=='MESH':
        o.hide_render = (not(o.name.startswith('JUNCTION |') or 'Station6' in o.name)
                         or any(k in o.name for k in ('continuous hand rope','rope hanger')))
row = data['rows']['stages'][0]['site']['spans'][0]['segments']
mid = min((f for f in data['frames'] if f['ground'] and 8 < f['travel'] < 15
           and (not round_trip or (f['reverse'] and f['waiting']))),key=lambda f:f['feet'][1])
assert mid['ground']
for i, obj in enumerate(boards):
    before, after = row[i//boards_per_link], mid['poses'][i//boards_per_link]
    rest = xyz(before)
    now = xyz(after['p'])
    delta = rot(after['q']) @ rot(before['rot']).transposed()
    obj.matrix_world = Matrix.Translation(now) @ delta.to_4x4() @ Matrix.Translation(-rest) @ original[i]

def mat(name, rgb, emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=.51
    p.inputs['Emission Color'].default_value=(*rgb,1)
    p.inputs['Emission Strength'].default_value=emission
    return m

rope = mat('Review hemp cords', (.37,.229,.097))
track = mat('Review tick marker', (.023,.68,.77),1.6)
feet = mat('Review midpoint feet', (1,.32,.029),1.2)
return_track = mat('Review return samples',(.98,.45,.085),1.2)

def cable(n, vertices, radius):
    c=bpy.data.curves.new(n,'CURVE')
    c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2
    a=c.splines.new('POLY')
    a.points.add(len(vertices)-1)
    for p,v in zip(a.points,vertices): p.co=(*v,1)
    obj=bpy.data.objects.new(n,c)
    s.collection.objects.link(obj)
    c.materials.append(rope)

# For the review only, connect the original handrail height to the recorded
# link transforms. This is not proof an actual client uses that binding.
for d in (-1,1):
    def at(link, offset, lift):
        p=mid['poses'][link]
        return xyz(p['p']) + rot(p['q']) @ Vector((d*.87,-offset,lift))
    cable('Swaying hand rope',
          [A+side*d*.87+Vector((0,0,1.08))]+[at(k,0,1.155) for k in range(links)]
          +[B+side*d*.87+Vector((0,0,1.08))],.043)
    for k in range(1,links):
        cable('Reconstructed hanger',[at(k,0,.03),at(k,0,1.155)],.022)

for f in data['frames'][::3]:
    # Markers are actual sampled feet; return markers stay smaller.
    if -1 < f['travel'] < data['summary']['len']+.8:
        p=xyz(dict(zip('xyz',f['feet'])))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=(.048 if f.get('reverse') else .065) if round_trip else .054,location=p+Vector((0,0,.16)))
        bpy.context.object.data.materials.append(return_track if f.get('reverse') else track)
p=xyz(dict(zip('xyz',mid['feet'])))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.106,location=p+Vector((0,0,.16)))
bpy.context.object.data.materials.append(feet)

def aim(o,q):
    o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()

s.world=bpy.data.worlds.new('Cool elevated daylight')
s.world.use_nodes=True
back=s.world.node_tree.nodes['Background']
back.inputs['Color'].default_value=(.29,.395,.49,1)
back.inputs['Strength'].default_value=.53

def light(n,kind,loc,target,watts,col,size):
    d=bpy.data.lights.new(n,kind);d.energy=watts;d.color=col
    if kind=='SUN':d.angle=size
    else:d.size=size
    obj=bpy.data.objects.new(n,d);s.collection.objects.link(obj)
    obj.location=loc;aim(obj,target)

light('Copper sky edge','SUN',(-156,67,48),p,2.2,(1,.76,.57),.14)
light('Cold gully bounce','AREA',(-179,107,23),p,2300,(.66,.84,1),11)
c=bpy.data.cameras.new('Native bridge evidence')
s.camera=bpy.data.objects.new(c.name,c);s.collection.objects.link(s.camera)
c.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=52;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.068
s.view_settings.view_transform='AgX'
s.render.resolution_x,s.render.resolution_y=1440,900
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=93
for name, loc, target, scale in [
    ('crossing',(-167,82,32),(-178.6,104,17.9),31.5),
    ('midpoint',p+Vector((3,-6,3.25)),p-Vector((.28,-.18,.03)),9.2)
]:
    c.ortho_scale=scale
    s.camera.location=loc;aim(s.camera,target)
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
