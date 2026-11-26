"""Matched W6a screenshots using the archived Movers art and measured feet."""
import hashlib
import json
import runpy
from pathlib import Path
import sys

import bpy
from mathutils import Vector

trace_path, output = map(Path, sys.argv[sys.argv.index('--')+1:])
trace = json.loads(trace_path.read_text())
repo = Path(__file__).resolve().parents[2]
donor = repo/'scripts/blender/west-movers-roof/movers.py'
assert hashlib.sha256(donor.read_bytes()).hexdigest() == trace['sourceSha']
bpy.ops.wm.read_factory_settings(use_empty=True)
stage = runpy.run_path(str(donor), init_globals={'REPO':repo,'OUT':output/'scratch'})
scene = bpy.context.scene

prefix = 'MOVERS | '
arm = bpy.data.objects[prefix+'Station4 sweep arm STATIC']
arm.hide_render = True  # Not part of the physics bench.
cage = [o for o in scene.objects if o.name.startswith(prefix+'Station5 lift cage floor STATIC at6m') or
        o.name.startswith(prefix+'Station5 lift safety rail')]
base_z = {o:o.location.z for o in cage}
assert len(cage)>1
head = bpy.data.objects[prefix+'Station5 lift head beam']
assert abs(head.location.z-trace['archivedBeam'][2])<1e-6
assert abs(head.dimensions.z-2*trace['archivedBeam'][5])<1e-6
landing = bpy.data.objects[prefix+'Station6 top deck']
assert abs(landing.location.z+landing.dimensions.z/2-18)<1e-5
for o in scene.objects:
    if not o.name.startswith(tuple(prefix+n for n in ('Station3 far landing','Station4','Station5','Station6'))):
        o.hide_render = True

guides = []
for _,gx,gy,gz,hx,hy,hz in trace['guideExtensions']:
    guides.append(stage['box']('Guide top extension',(gx,-gz,gy),(2*hx,2*hz,2*hy),'steel',.035))

mesh = repo/'public/assets/wildshard-art/w6a-spinner-lift-lip.glb'
assert hashlib.sha256(mesh.read_bytes()).hexdigest() == trace['lipSha']
old = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(mesh))
_,x,y,z,_,hy,_ = trace['lip']
for o in set(scene.objects)-old:
    if o.parent is None:o.location += Vector((x,-z,y+hy))

stage['box']('Review ground',(-151,104,-.19),(70,70,.28),'concrete',0)
world = bpy.data.worlds.new('Blue-gray backdrop');scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(.32,.48,.61,1)
bg.inputs['Strength'].default_value=.36
def light(kind,name,point,target,energy,color):
    d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=color
    if kind=='AREA':d.size=9
    else:d.angle=.10
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=point
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('SUN','Grazing light',(-137,80,36),(-156,103,12),2.0,(1,.80,.60))
light('AREA','Sky fill',(-167,85,28),(-154,103,14),2900,(.60,.78,1))

def trail_mat(name,rgba):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=n.inputs['Emission Color'].default_value=(*rgba,1)
    n.inputs['Emission Strength'].default_value=.62
    return m

def path(points,m):
    c=bpy.data.curves.new('Measured player-foot path',type='CURVE');c.dimensions='3D'
    c.bevel_depth=.077;c.bevel_resolution=2
    spl=c.splines.new('POLY');spl.points.add(len(points)-1)
    for p,(x,y,z) in zip(spl.points,points):p.co=(x,-z,y+.095,1)
    o=bpy.data.objects.new(c.name,c);scene.collection.objects.link(o);c.materials.append(m)
    fx,fy,fz=points[-1]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.172,location=(fx,-fz,fy+.095))
    end=bpy.context.object;end.data.materials.append(m);end.name='Recorded endpoint'
    return o,end

cam=bpy.data.cameras.new('Matched lift view')
camera=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(camera)
scene.camera=camera;camera.location=(-141,68,27)
camera.rotation_euler=(Vector((-152.9,103,11.3))-camera.location).to_track_quat('-Z','Y').to_euler()
cam.type='ORTHO';cam.ortho_scale=37.0
scene.render.engine='CYCLES';scene.cycles.samples=29
scene.cycles.use_denoising=False;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.078
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.render.resolution_x=1360;scene.render.resolution_y=1020;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=92

for label,key,beam,c in (
    ('low-beam','control',trace['archivedBeam'],(.92,.34,.058)),
    ('raised-beam','show',trace['raisedBeam'],(.032,.73,.53)),
):
    q=trace[key]
    head.location.z=beam[2]
    for o in guides:o.hide_render=key=='control'
    for o in cage:o.location.z=base_z[o]+q['atTop']['cageY']-6
    overlay=path([s['feet'] for s in q['frames']]+[q['final']['feet']],trail_mat(label,c))
    scene.render.filepath=str(output/(label+'.jpg'))
    bpy.ops.render.render(write_still=True)
    for o in overlay:bpy.data.objects.remove(o,do_unlink=True)
