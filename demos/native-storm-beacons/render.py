"""Render the pinned Storm Hour kit before and after a fixture tap."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
root = here.parents[1]
assets = root / 'public/assets/wildshard-art'
fit = json.loads((root / 'project/layouts/e9-beacon-ground-control-proof.json').read_text())
spec = json.loads((here / 'states.json').read_text())
out = Path(sys.argv[sys.argv.index('--')+1])
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.fps = 25

def load(file, digest, pos):
    author = assets/file
    assert sha256(author.read_bytes()).hexdigest() == digest
    before = set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(author))
    objects = set(s.objects)-before
    for ob in objects:
        if ob.parent is None:
            ob.location += Vector(pos)
    return objects

def cube(name, pos, size, color, rough, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        edge = o.modifiers.new('Cast edge','BEVEL')
        edge.width = bevel
        edge.segments = 2
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color,1)
    bsdf.inputs['Roughness'].default_value = rough
    o.data.materials.append(m)

def area(name,pos,target,power,color,size):
    ld = bpy.data.lights.new(name,'AREA')
    ld.energy = power
    ld.color = color
    ld.shape = 'DISK'
    ld.size = size
    o = bpy.data.objects.new(name,ld)
    s.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

cube('Archived four-metre pedestal',(-1,2,6),(4,4,12),(.13,.17,.18),.79,.035)
cube('Yard floor',(0,0,-.15),(35,45,.30),(.045,.063,.071),.34,0)
cube('North boundary',(6,2,1.3),(14,.6,2.6),(.105,.158,.175),.65,.02)
cube('West boundary',(-1,-16,1.3),(.6,32,2.6),(.105,.158,.175),.65,.02)
controls = load('wsc-kit-007-storm-beacon-control.glb',fit['sha256'],(0,0,1.32))
lens = next(o for o in controls if o.name == spec['lens'])
pivot = next(o for o in controls if o.name == 'BeaconControlPivot')
clip = pivot.animation_data.action
start,end = map(round,clip.frame_range)
assert end-start == 8
for file,height in [('wsc-kit-007-storm-beacon-seat.glb',12),('wsc-kit-007-storm-beacon.glb',14.533658)]:
    load(file,fit['pins'][file],(-1,2,height))
file = spec['charged_insert']
charged = load(file,fit['pins'][file],(-1,2,14.533658))
world = bpy.data.worlds.new('Cold storm overcast')
s.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.19,.32,.54,1)
world.node_tree.nodes['Background'].inputs[1].default_value = .47
area('Cold overcast',(-4,-3.3,8),(-.5,0,1.4),920,(.52,.71,1),6)
area('Warm spill',(2,-5,3.6),(0,0,1.45),130,(1,.78,.52),4)
bpy.ops.object.camera_add(location=(.60,-1.40,1.72))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,-.22,1.32))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens = 50
s.camera = cam
s.render.resolution_x,s.render.resolution_y = 940,940
s.render.resolution_percentage = 100
s.render.engine = 'CYCLES'
s.cycles.samples = 28
s.cycles.use_denoising = False
s.cycles.adaptive_threshold = .068
s.view_settings.view_transform = 'AgX'
s.view_settings.look = 'AgX - Medium High Contrast'
for state,frame in [('ready',start),('lit',end)]:
    s.frame_set(frame)
    for o in charged:
        o.hide_render = state != 'lit'
    st = spec['states'][state]
    shader = lens.active_material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*st['base_linear'],1)
    shader.inputs['Emission Color'].default_value = (*st['emission_linear'],1)
    shader.inputs['Emission Strength'].default_value = st['strength']
    s.render.filepath = str(out/(state+'.png'))
    bpy.ops.render.render(write_still=True)
