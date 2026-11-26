"""W2b: lay the exact starter sword on the actual W1a street counter."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

out = output_directory()
only = os.environ.get('WSC_METADATA_ONLY') == '1'
repo = HERE.parents[2]
assets = repo / 'public/assets/wildshard-art'
slug = 'w2b-gunsmith-sword-tray'
clear_scene()
scene = bpy.context.scene


def material(name, color, roughness, metal=0):
    data = bpy.data.materials.new(name)
    data.diffuse_color = (*color, 1)
    data.use_nodes = True
    p = data.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = roughness
    return data


oak = material('Smoked oak', (.102, .050, .025), .58)
felt = material('Forest green felt', (.028, .108, .071), .88)
brass = material('Brushed champagne brass', (.54, .329, .105), .42, .71)
enamel = material('Warm ivory enamel', (.92, .82, .60), .46)
parts = []


def box(name, p, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = bpy.context.object
    o.name, o.dimensions = name, dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Eased edges', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        o.modifiers.new('Planar normals', 'WEIGHTED_NORMAL')
        bpy.ops.object.convert(target='MESH')
    parts.append(o)


# Feet straddle the original raised countercloth, never replace it.
body_start = len(parts)
box('Shallow oak carrier', (0, 0, .023), (1.44, .451, .046), oak, .009)
box('Felt bed', (0, .018, .0475), (1.320, .317, .007), felt, .003)
for y in (-.191, .192):
    box('Inset brass fillet', (0, y, .048), (1.365, .004, .004), brass)
for sx in (-1, 1):
    x = sx * .690
    for y in (-.160, .160):
        box('Corner straps', (x, y, .047), (.023, .042, .006), brass, .002)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=.004, depth=.003, location=(x,y,.0505))
        o = bpy.context.object
        o.name = 'Recessed fixing'
        o.data.materials.append(oak)
        parts.append(o)
caption = bpy.data.curves.new('Starter sword', 'FONT')
caption.body, caption.align_x, caption.align_y, caption.size = 'STARTER  SWORD', 'CENTER', 'CENTER', .031
caption.resolution_u = 3
caption.materials.append(enamel)
o = bpy.data.objects.new(caption.name, caption)
scene.collection.objects.link(o)
o.location = (0, -.165, .0482)
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.object.convert(target='MESH')
parts.append(o)
for obj in parts[body_start:]:
    obj.location.z += .028
for x in (-.625, .625):
    for y in (-.188, .188):
        box('Four inset feet', (x, y, .014), (.087, .042, .028), oak, .002)
groups = {m: [p for p in parts if p.data.materials[0] == m] for m in (oak, felt, brass, enamel)}
export_parts = []
for mat, group in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:
        o.select_set(True)
    bpy.context.view_layer.objects.active = group[0]
    if len(group) > 1:
        bpy.ops.object.join()
    o = bpy.context.object
    o.name = 'Sword tray | ' + mat.name
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    export_parts.append(o)

tray_path = out / (slug + '.glb')
export(export_parts, tray_path)
raw = tray_path.read_bytes()
doc = json.loads(raw[20:20+struct.unpack_from('<I', raw, 12)[0]])
primitives = [p for m in doc['meshes'] for p in m['primitives']]
tris = sum(doc['accessors'][p['indices']]['count']//3 for p in primitives)
assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
assert len(raw)<100_000 and tris<2000 and len(primitives)==4
assert not any(k in doc for k in ('images','skins','animations','cameras'))

os.environ['WILDSHARD_VALIDATE_ONLY'] = '1'
try:
    runpy.run_path(str(HERE/'keeper_street.py'))
except SystemExit as e:
    if e.code != 0:
        raise
else:
    raise AssertionError('Unexpected staging mode')

old = json.loads((repo/'project/layouts/w1a-keeper-frontage-proof.json').read_text())
recent = json.loads((out/'w1a-keeper-frontage-proof.json').read_text())
for key in ('stage_frame','keeper_world_xz','rook_world_xz','keeper_yaw','rook_yaw'):
    assert old[key] == recent[key], key
for a,b in zip(old['counter_blender_xyz'],recent['counter_blender_xyz']):
    assert abs(a-b)<.002, (a,b)

def load(path):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted(set(scene.objects)-before,key=lambda o:o.name)

def vertices(objs):
    return [o.matrix_world @ v.co for o in objs if o.type=='MESH' for v in o.data.vertices]

def ext(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]

def bvh(obs):
    points, faces = [], []
    for o in obs:
        start = len(points)
        points.extend(o.matrix_world @ v.co for v in o.data.vertices)
        faces.extend([start+i for i in p.vertices] for p in o.data.polygons)
    return BVHTree.FromPolygons(points, faces)

counter = [o for o in scene.objects if o.name.startswith('Oak counter exact part')]
donor = bvh(counter)
x, y = -66.16, -4.70
support = []
for i in range(25):
    for j in range(9):
        p,*_ = donor.ray_cast(Vector((x + 1.44*(i/24-.5),y + .451*(j/8-.5),2.0)), Vector((0,0,-1)),1.1)
        assert p is not None, (i,j)
        support.append(p.z)
feet = []
for xx in (-.625, .625):
    for yy in (-.188, .188):
        for dx in (-.042,0,.042):
            for dy in (-.020,0,.020):
                p,*_ = donor.ray_cast(Vector((x+xx+dx,y+yy+dy,2.0)),Vector((0,0,-1)),1.1)
                assert p is not None
                feet.append(p.z)
assert max(feet)-min(feet)<.001, feet
at = Vector((x,y,max(feet)+.0005))
cloth_gap = at.z + .028 - max(support)
assert cloth_gap > .005, cloth_gap
tray = load(tray_path)
for o in tray:
    assert o.parent is None
    o.location += at
bpy.context.view_layer.update()
tb=ext(vertices(tray))
cb=ext(vertices(counter))
edge=min(tb[0][i]-cb[0][i] for i in (0,1))
edge=min(edge,*(cb[1][i]-tb[1][i] for i in (0,1)))
assert edge>.15 and .0004<tb[0][2]-max(feet)<.0006,(edge,tb)
liner = [o for o in tray if any('Forest green felt' in m.name for m in o.data.materials)]
assert len(liner)==1
ll, lh = ext(vertices(liner))
sword_path = assets/'wsc-gear-001-sword.glb'
sword_hash=hashlib.sha256(sword_path.read_bytes()).hexdigest()
assert sword_hash == '64d9cf3926a58752233d9a40a467d87dfa9489b2270b83f95d577afa53295d62'
sword = load(sword_path)
assert len(sword)==1 and sword[0].parent is None
o = sword[0]
orientation = Matrix.Rotation(.045,4,'Z') @ Matrix.Rotation(-1.5707963267948966,4,'Y') @ Matrix.Rotation(1.5707963267948966,4,'Z')
o.matrix_world = orientation @ o.matrix_world
bpy.context.view_layer.update()
a,b=ext(vertices(sword))
target=Vector((x,y+.020,lh[2]+.0004))
o.location += target - Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,a[2]))
bpy.context.view_layer.update()
sl,sh=ext(vertices(sword))
margin=min(*(sl[i]-ll[i] for i in (0,1)),*(lh[i]-sh[i] for i in (0,1)))
assert margin>.025 and .0003<sl[2]-lh[2]<.0005, (margin,sl,sh,ll,lh)

proof=dict(tray=dict(bytes=len(raw),triangles=tris,primitives=len(primitives),sha256=hashlib.sha256(raw).hexdigest()),
           donor_town_sha256=recent['town_glb_sha256'],sword_sha256=sword_hash,stage_frame=19,
           tray_blender_xyz=list(at),tray_three_xyz=[at.x,at.z,-at.y],
           counter_height_range_m=[min(support),max(support)],counter_ray_count=len(support),foot_ray_count=len(feet),
           min_tray_underside_clearance_m=cloth_gap,
           min_counter_edge_margin_m=edge,sword_liner_edge_margin_m=margin,
           sword_blender_world=[list(r) for r in o.matrix_world],bounds_blender=[sl,sh])
(out/(slug+'.json')).write_text(json.dumps(proof,indent=2)+'\n')
if only:
    sys.exit(0)

world=bpy.data.worlds.new('Brasswick overcast')
scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.46,.59,.75,1)
bg.inputs[1].default_value=.70

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def light(name, kind, at, target, color, power, size):
    data=bpy.data.lights.new(name,kind)
    data.energy,data.color=power,color
    if kind=='AREA': data.size=size
    else: data.angle=size
    o=bpy.data.objects.new(name,data)
    scene.collection.objects.link(o)
    o.location=at
    aim(o,target)

light('Slanting sun','SUN',(-80,9,19),(-66,-5,0),(1,.83,.64),2.15,.12)
light('Counter softbox','AREA',(-65.5,-2.0,3.4),(-66,-4.7,1),(1,.86,.68),310,3.0)
light('Street bounce','AREA',(-68,-5.2,2.6),(-66,-4.7,1),(.63,.78,1),75,2.0)
cam=bpy.data.cameras.new('Street review')
c=bpy.data.objects.new(cam.name,cam)
scene.collection.objects.link(c)
scene.camera=c
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.07
scene.cycles.use_denoising=False
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=93
for name,p,t,lens,w,h in [
    ('detail',(-66.30,-3.48,2.48),(-66.16,-4.71,1.10),47,1200,760),
    ('street',(-68.95,.07,1.75),(-65.5,-4.65,1.71),42,840,1120),
]:
    c.location=p
    aim(c,t)
    cam.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=w,h
    scene.render.filepath=str(out/f'nov26-w2b-sword-tray-{name}.jpg')
    bpy.ops.render.render(write_still=True)
