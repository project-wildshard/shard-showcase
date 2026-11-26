"""Render exact solver poses in the original authored West Physics Yard."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

trace, out = map(Path, sys.argv[sys.argv.index('--')+1:])
r = json.loads(trace.read_text())
scene = bpy.context.scene
assets = Path(__file__).resolve().parents[2] / 'public/assets/wildshard-art'
pins = {
    'wsc-plan-003-hinged-seesaw': '4810b216338fb4da46115884945a2a52c89776ce9d87c585508d6b95bd27df07',
    'haul-crate': 'd7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44',
}
for key, expected in pins.items():
    assert hashlib.sha256((assets / (key+'.glb')).read_bytes()).hexdigest() == expected

old = [o for o in scene.objects if 'see-saw instance' in o.name]
assert len(old) == 2
for o in old:
    o.hide_render = True  # Replace meshes in these photos, not the actual yard source.

def import_roots(key):
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/(key+'.glb')))
    return {o.name.split('.')[0]: o for o in set(scene.objects)-before if o.parent is None}

def setup(run):
    donor = import_roots('wsc-plan-003-hinged-seesaw')
    assert set(donor) == {'Fixed_Base', 'Hinged_Deck'}
    x, z = run['base']
    donor['Fixed_Base'].location = (x, -z, r['floor'])
    crates = [import_roots('haul-crate')['haul-crate'] for i in range(2)]
    return (donor['Hinged_Deck'], *crates)

def pose(run, objs, tick):
    frame = run['frames'][tick]
    assert tick == frame['tick']
    for ob, key, scale in zip(objs, ('deck','rider','weight'), (1,1,1.35)):
        b = frame[key]
        ob.hide_render = b is None
        if b:
            p,q = b['p'],b['q']
            loc = Matrix.Translation((p['x'],-p['z'],p['y']))
            rot = Quaternion((q['w'],q['x'],-q['z'],q['y'])).to_matrix().to_4x4()
            ob.matrix_world = loc @ rot @ Matrix.Scale(scale, 4)

first, second = r['run'], r['second']
art1, art2 = setup(first), setup(second)
scene.render.engine = 'CYCLES'
scene.cycles.samples = 42
scene.cycles.adaptive_threshold = .045
scene.cycles.use_denoising = False
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'WEBP'
scene.render.image_settings.quality = 90
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
world = bpy.data.worlds.new('Low afternoon skylight')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (.42,.59,.75,1)
bg.inputs[1].default_value = .59
for o in scene.objects:
    if o.type == 'LIGHT':
        o.hide_render = True
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.object
sun.rotation_euler = Vector((.63,.47,-.6)).to_track_quat('-Z','Y').to_euler()
sun.data.color = (1,.84,.65)
sun.data.energy = 3.2
sun.data.angle = .10
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam

def shot(name, eye, target, lens, resolution):
    cam.location = eye
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens = lens
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(out/(name+'.webp'))
    bpy.ops.render.render(write_still=True)

pose(first,art1,first['peakTick'])
pose(second,art2,second['peakTick'])
shot('nov26-w4b-seesaw-apex',(-70.4,-202.8,10.2),(-71.2,-224,2.25),22,(1580,940))
pose(first,art1,first['landed'])
pose(second,art2,second['landed'])
shot('nov26-w4b-seesaw-return',(-88,-218.0,3.9),(-82.0,-224.1,1.95),39,(1300,900))
