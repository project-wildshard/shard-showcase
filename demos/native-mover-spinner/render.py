"""Render the unchanged donor under measured deck/feet poses (no gameplay UI)."""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

src, dest = map(Path, sys.argv[sys.argv.index('--')+1:])
spec = json.loads(src.read_text())
asset = Path(__file__).resolve().parents[2] / 'public/assets/wildshard-art/wsc-kit-002-station4-spinner.glb'
assert hashlib.sha256(asset.read_bytes()).hexdigest() == spec['sha']
dest.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(asset))
disc = bpy.data.objects.get('Movers_DiscYaw')
assert disc and bpy.data.objects.get('Movers_ArmYaw')
ox, _, oz = spec['origin']

def coords(q, add=.034):
    return (q[0]-ox, oz-q[2], q[1]+add)

def mat(name, color, metallic=0, bright=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Roughness'].default_value=.56
    n.inputs['Metallic'].default_value=metallic
    n.inputs['Emission Color'].default_value=(*color,1)
    n.inputs['Emission Strength'].default_value=bright
    return m

slate=mat('Cool concrete',(.113,.155,.172))
deck=mat('Charcoal landing',(.128,.166,.172),.24)
rail=mat('Muted brass stage trim',(.55,.26,.053),.4)
teal=mat('Measured stance',(.021,.67,.51),.22,.42)
yellow=mat('Airborne scripted control',(.83,.315,.065),.13,.34)
blue=mat('Original arrival marker',(.12,.38,.64),.19,.2)

def block(label, pos, dims, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    b=bpy.context.object;b.name=label;b.dimensions=dims
    b.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=b.modifiers.new('Preview bevel','BEVEL');m.width=bevel;m.segments=2
        b.modifiers.new('Face normals','WEIGHTED_NORMAL')
    return b

def dot(label, pos, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=radius,location=pos)
    o=bpy.context.object;o.name=label;o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(label, points, material, width=.025):
    c=bpy.data.curves.new(label,'CURVE');c.dimensions='3D'
    c.bevel_depth=width;c.bevel_resolution=2
    sp=c.splines.new('POLY');sp.points.add(len(points)-1)
    for p,xyz in zip(sp.points,points):p.co=(*xyz,1)
    o=bpy.data.objects.new(label,c);s.collection.objects.link(o);c.materials.append(material)
    return o

block('Exact archived Station 3 arrival extent',(6,0,5.75),(2,8,.5),deck,.025)
for q in (-2.8,2.8):
    block('Illustrative landing support',(6.1,q,2.75),(.52,.52,5.52),deck,.018)
block('Ground staging',(0,0,-.135),(100,100,.27),slate)
for i in (-3.2,3.2):
    block('Review landing edge paint',(5.2,i,6.003),(.22,.84,.004),rail)
w=bpy.data.worlds.new('Cool industrial sky');s.world=w;w.use_nodes=True
bg=w.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.47,.64,.83,1);bg.inputs['Strength'].default_value=.48
l=bpy.data.lights.new('Low warm sun','SUN');l.energy=3.1;l.angle=.09;l.color=(1,.807,.59)
o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o)
o.rotation_euler=Vector((-.36,.69,-1)).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=38;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.064
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'

def snap(label, pos, target, dims, focal):
    bpy.ops.object.camera_add(location=pos);c=bpy.context.object
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    c.data.lens=focal;s.camera=c
    s.render.resolution_x,s.render.resolution_y=dims;s.render.resolution_percentage=100
    s.render.filepath=str(dest/(label+'.png'));bpy.ops.render.render(write_still=True)

if 'trials' in spec:
    _,lx,ly,lz,hx,hy,hz=spec['lip']
    probe=json.loads((src.parent/'lip-proof.json').read_text())
    path=src.parent/'w6a-spinner-lift-lip.glb'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==probe['glb_sha256']
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    lip=set(bpy.context.scene.objects)-before
    for o in lip:
        if o.parent is None:o.location+=Vector(coords((lx,ly+hy,lz),0))
    block('Station 5 bottom cage envelope',(-10,0,5.8),(5.5,6.2,.4),deck,.025)
    for t in (-2.65,2.65):
        block('Illustrative cage rail',(-10,t,6.72),(4.9,.10,.095),rail,.017)
        for u in (-12.3,-7.6):
            block('Illustrative cage rail terminal',(u,t,6.36),(.12,.12,.72),rail,.016)
    s.cycles.samples=28
    for enabled in (False,True):
        q=next(q for q in spec['trials'] if q['addLip']==enabled and q['dz']==0 and q['hold']==24)
        for o in lip:o.hide_render=not enabled
        disc.rotation_mode='XYZ'
        disc.rotation_euler.z=q['final']['yaw']
        feet=[coords(f['feet'],.073) for f in q['samples'][::4]]
        feet.append(coords(q['final']['feet'],.073))
        c=teal if enabled else yellow
        trail=tube('Measured stock-player trace',feet,c,.058)
        end=dot('Measured end point',feet[-1],.17,c)
        snap('nov26-spinner-lift-'+('lip' if enabled else 'gap'),(-7.9,-19.3,19.2),(-2.9,0,4.15),(1320,900),39)
        for o in (trail,end):bpy.data.objects.remove(o,do_unlink=True)
    sys.exit(0)

entry=next(q for q in spec['entries'] if q['dz']==0 and not q['jump'])
j=next(q for q in spec['entries'] if q['dz']==0 and q['jump'] and q['spinEnabled'])
disc.rotation_mode='XYZ';disc.rotation_euler.z=entry['firstDeck']['yaw']
decor=[]
for q,m,label in ((entry,teal,'Walk'),(j,yellow,'Jump')):
    # Separate equal-world test traces 10 cm in the picture so overlap remains legible.
    points=[(x,y+(.1 if q['jump'] else -.1),z) for x,y,z in map(coords,q['segments'])]
    decor.append(tube(label+' trace',points,m))
    decor.append(dot(label+' first deck contact',points[-1],.085,m))
snap('approach',(8.6,-5.1,9.7),(2.2,0,5.91),(1280,900),47)
for ob in decor:bpy.data.objects.remove(ob,do_unlink=True)

track=next(q for q in spec['spin'] if q['r']==3.3)['shots']
disc.rotation_euler.z=track[2]['yaw']
for i,q in enumerate(track[:8]):
    p=coords(q['feet'])
    dot(f'Native feet after {i} s',p,.136 if i==2 else .079,blue if i==0 else teal)
    if i==2: tube('Measured current position',[(p[0],p[1],p[2]),(p[0],p[1],p[2]+.45)],teal,.032)
snap('carry',(8,-10.3,16.5),(1.15,-.15,4.42),(1280,900),43)
