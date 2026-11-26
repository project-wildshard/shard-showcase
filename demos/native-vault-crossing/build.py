"""Extract existing E10c room art and inspect the bridge-to-lift crossing."""
import json
import os
from pathlib import Path
import runpy
import sys
import bpy

repo=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:]
out=Path(args[0]).resolve()
lift='--lift' in args
out.mkdir(parents=True,exist_ok=True)
receipt=out/('lift-walk.json' if lift else 'walk.json')
os.environ['WSC_METADATA_ONLY']='1'
sys.argv[sys.argv.index('--')+1:]=[str(out)]
try:
    runpy.run_path(str(repo/'scripts/blender/showcase-studies/vault_climb_room.py'))
except SystemExit as e:
    if e.code not in (0,None):
        raise

def role(name):
    if lift and name.startswith(('Last-door landing','Last-door tread')):
        return 'upper'
    for prefix,key in (
        ('Scramble step C / bridge apron','west'),
        ('03 original bridge','bridge'),('Winch approach','east'),
        ('04 fixed shaft mouth','frame'),('Deck at lower mark','deck'),
        ('Vault invert','bottom')):
        if name.startswith(prefix):
            return key
    return None

deps=bpy.context.evaluated_depsgraph_get()
parts=[]
for ob in sorted(bpy.context.scene.objects,key=lambda a:a.name):
    k=role(ob.name)
    if not k or ob.type!='MESH':
        continue
    ev=ob.evaluated_get(deps)
    m=ev.to_mesh()
    try:
        p=[ev.matrix_world@v.co for v in m.vertices]
        m.calc_loop_triangles()
        coords=[round(w,7) for x,y,z in p for w in (186+x,-50+z,-64-y)]
        faces=[i for tri in m.loop_triangles for i in tri.vertices]
        if faces:
            parts.append(dict(role=k,name=ob.name,vertices=coords,triangles=faces))
    finally:
        ev.to_mesh_clear()
assert {p['role'] for p in parts}==({'west','bridge','east','frame','deck','bottom'}|({'upper'} if lift else set()))
(out/('lift-collision.json' if lift else 'collision.json')).write_text(json.dumps(parts,separators=(',',':'))+'\n')
print([(x['role'],x['name'],len(x['triangles'])//3) for x in parts])

if not receipt.exists():
    sys.exit(0)
record=json.loads(receipt.read_text())
import hashlib
assert hashlib.sha256((out/('lift-collision.json' if lift else 'collision.json')).read_bytes()).hexdigest()==record['collisionHash']
from mathutils import Vector
V=Vector
scene=bpy.context.scene
lower=[o for o in scene.objects if o.name.startswith('Deck at lower mark')]
upper=[o for o in scene.objects if o.name.startswith('Deck at upper mark')]
for o in scene.objects:
    if o.name.startswith(('Deck at upper mark','Section label plaque','Landing label plaque','Landing plane dash','01   ','02   ','03   ','04   ','05   ','LOW  ','HIGH  ')):
        o.hide_render=True

def path(name,rgb,frames):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Emission Color'].default_value=(*rgb,1)
    p.inputs['Emission Strength'].default_value=1.1
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.042;c.bevel_resolution=2
    p=c.splines.new('POLY');p.points.add(len(frames)-1)
    for q,r in zip(p.points,frames):
        x,y,z=r['feet'];q.co=(x-186,-64-z,y+50+.11,1)
    c.materials.append(m)
    o=bpy.data.objects.new(name,c);scene.collection.objects.link(o)
    return o

if lift:
    traces=[
        path('Real boarding trace',(.06,.62,.58),record['center']['boardFrames']+[record['center']['boarded']]),
        path('Real lift trace',(.20,.70,.95),[record['center']['boarded']]+record['center']['ascFrames']),
        path('Real exit trace',(.06,.62,.58),[record['center']['afterRide']]+record['center']['exitFrames']+[record['center']['final']])]
else:
    path('Measured grounded boarding',(.06,.62,.58),record['centerCompact']['frames'])
    fall=path('Measured test without the bridge',(.98,.24,.055),[r for r in record['control']['frames'] if not r['grounded']])
scene.world=bpy.data.worlds.new('Cool concrete ambient');scene.world.use_nodes=True
p=scene.world.node_tree.nodes['Background'];p.inputs[0].default_value=(.16,.30,.40,1);p.inputs[1].default_value=.26
def aim(o,target):
    o.rotation_euler=(V(target)-o.location).to_track_quat('-Z','Y').to_euler()
for name,eye,target,energy,size,rgb in [
    ('Warm bridge key',(-3,-3.5,10),(-2,0,5),850,3,(1,.67,.39)),
    ('Cold landing key',(5,3.1,9),(4,0,5),880,4,(.43,.79,1)),
    ('Warm lift key',(11,-2.9,9),(9,0,5),940,3,(1,.76,.55)),
    ('Cool front fill',(3,-10,8),(2,0,5),1050,7,(.65,.81,1))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=rgb
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=eye;aim(o,target)
c=bpy.data.cameras.new('Proof camera');o=bpy.data.objects.new('Proof camera',c);scene.collection.objects.link(o);scene.camera=o
scene.render.engine='CYCLES';scene.cycles.samples=34;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.052
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
settings=[
    ('bridge-lift-wide',(1,-18,10.6),(1.9,0,5.0),(1260,865),19),
    ('bridge-lift-eye',(-3.65,-.18,7.18),(5.2,0,5.53),(760,1000),None)]
if lift:
    settings=[
        ('vault-lift-boarding',(1,-18,10.6),(1.9,0,5.0),(1260,865),19),
        ('vault-lift-top',(7.8,-12,13.1),(10.6,0,8.10),(1260,865),14.6)]
for i,(name,eye,target,wh,scale) in enumerate(settings):
    if lift:
        for ob in lower:ob.hide_render=bool(i)
        for ob in upper:ob.hide_render=not bool(i)
        traces[0].hide_render=bool(i)
        traces[1].hide_render=not bool(i)
        traces[2].hide_render=not bool(i)
    else:
        fall.hide_render=scale is None
    c.type='ORTHO' if scale else 'PERSP'
    if scale:c.ortho_scale=scale
    else:c.lens=24
    o.location=eye;aim(o,target)
    scene.render.resolution_x,scene.render.resolution_y=wh
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
