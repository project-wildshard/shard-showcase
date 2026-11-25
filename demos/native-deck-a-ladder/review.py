"""Render the exact canonical deck with sampled player feet; no game actor."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

base, trace, out = (Path(a).resolve() for a in sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True, exist_ok=True)
root=Path(__file__).resolve().parents[2]
expected=json.loads((root/'scripts/blender/west-climb-rock/expected.json').read_text())
parity=json.loads((base/'parity.json').read_text())['matched_signature']
assert parity in (expected['semantic_signature'],expected['normalized_semantic_signature'])
trace=json.loads(trace.read_text())
measurement=trace['explicitStockInstaller']
bpy.ops.wm.open_mainfile(filepath=str(base/'climb-rock-editable.blend'))
s=bpy.context.scene
s.render.use_compositing=False

def take(prefix):
    oo=[o for o in s.objects if o.type=='MESH' and o.name.startswith(prefix)]
    assert len(oo)==1,(prefix,len(oo))
    return oo[0]

def bvh(o):
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                                [tuple(p.vertices) for p in o.data.polygons])

ground=take('CLIMB | source yard footprint')
deck=take('CLIMB | deck A and ladder')
for o in list(s.objects):
    if o.type=='LIGHT':
        bpy.data.objects.remove(o,do_unlink=True)
    elif o.type in {'MESH','CURVE','FONT'}:
        if o not in {ground,deck} and not any(label in o.name for label in
          ('crag mesh','scramble wall','trimmed crown','yard corner')):
            o.hide_render=True

gt,dt=bvh(ground),bvh(deck)
x,y=-166,-28
ys=[y-3.20,y-3.18,y-3.13,y-3.04,y-2.99]
assert all(dt.ray_cast((x+dx, yy,6.3),(0,0,-1),.36)[0] is not None
           for dx in [-.5,0,.5] for yy in ys)
assert dt.ray_cast((x,y-3.26,6.3),(0,0,-1),.36)[0] is None
assert abs(dt.ray_cast((x,y-3.18,6.3),(0,0,-1),.36)[0].z-6)<.00002
g=[gt.ray_cast((x+dx,-31.78+dy,.15),(0,0,-1),.20)[0].z
   for dx in [-.5,-.25,0,.25,.5] for dy in [-.50,-.25,0,.25,.50]]
assert max(abs(v-.0275) for v in g)<.00002
opening=[]
for z in [6.44,6.55,6.68,6.91,7.02,7.13]:
    for dx in [-.62,-.31,0,.31,.62]:
        # The separate ladder rails end 0.20 m in front of this guard.
        opening.append(dt.ray_cast((x+dx,-31.29,z),(0,1,0),.19)[0] is None)
assert all(opening)
end=measurement['landed']['feet']
assert dt.ray_cast((end[0],-end[2],6.3),(0,0,-1),.36)[0] is not None
(out/'art-fit.json').write_text(json.dumps({
  'canonicalFingerprint':parity,'groundSamples':len(g),'sixMetrePlankHits':15,'guardGapClearRays':len(opening),
  'guardOpeningMeters':1.5,'renderedPoses':['mid','landed']},indent=2)+'\n')

def mat(n,color,em=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.37
    p.inputs['Emission Color'].default_value=(*color,1)
    p.inputs['Emission Strength'].default_value=em
    return m

# Dark studio base keeps the isolated terrain from reading as a hole in the scene.
bpy.ops.mesh.primitive_plane_add(size=130,location=(-166,-29,-.035))
bpy.context.object.name='Review base, not playable geometry'
bpy.context.object.data.materials.append(mat('Review slate',(.075,.094,.115)))
amber=mat('Review amber',(.93,.34,.065),.50)
ink=mat('Marker frame',(.053,.076,.087),.04)
pale=mat('Line marks',(.26,.78,.86),.72)

def sphere(n,p,r,ma,scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=p)
    o=bpy.context.object
    o.name,o.scale=n,scale
    for a in o.data.polygons:a.use_smooth=True
    o.data.materials.append(ma)
    return o

def disc(n,p,r,h,ma):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=h,location=p)
    o=bpy.context.object
    o.name=n;o.data.materials.append(ma)
    return o

def ring(n,p,r,minor,ma):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=p,
        major_radius=r,minor_radius=minor)
    o=bpy.context.object;o.name=n;o.data.materials.append(ma)
    return o

# Tick indicators chosen by test samples (not baked animation).
for f in trace['samples'][2::2]:
    xx,yy,zz=f['feet']
    if .24<yy<5.95:
        sphere('Measured path tick',(xx,-zz,yy),.029,pale)
for t in [.20,.4,.60,.80]:
    sphere('Upper landing path',(x,-31.78+.85*t,6.035),.025,pale)

marker=[]
for pose in ['mid','landed']:
    tx,ty,tz=measurement[pose]['feet']
    p=Vector((tx,-tz,ty))
    group=[ring('Foot reference',p+Vector((0,0,.025)),.234,.023,amber),
           disc('Foot center',p+Vector((0,0,.041)),.091,.023,amber),
           sphere('Review capsule',p+Vector((0,0,.81)),.265,amber,(1,1,2.68))]
    group.append(ring('Capsule guide',p+Vector((0,0,.81)),.259,.031,ink))
    marker.append(group)

def aim(o, a, b):
    o.location=a;o.rotation_euler=(Vector(b)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Ladder review',bpy.data.cameras.new('Ladder review'))
s.collection.objects.link(cam)
s.camera=cam
cam.data.lens=53
s.world=bpy.data.worlds.new('Blue-grey open air')
s.world.use_nodes=True
env=s.world.node_tree.nodes['Background']
env.inputs['Color'].default_value=(.24,.34,.42,1)
env.inputs['Strength'].default_value=.24
def light(n,p,q,color,value,size=None):
    d=bpy.data.lights.new(n,'SUN' if size is None else 'AREA')
    d.energy,d.color=value,color
    if size is None:d.angle=.16
    else:d.shape='DISK';d.size=size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);aim(o,p,q)
light('Low late afternoon',(-155,-41,19),(-166,-28,0),(1,.79,.55),2.65)
light('Soft cool fill',(-172,-28,11),(-166,-31,4),(.54,.78,1),570,9)
s.render.engine='CYCLES'
s.cycles.samples=32
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.065
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.film_transparent=False
s.render.resolution_percentage=100
s.render.resolution_x,s.render.resolution_y=1480,1140
s.render.image_settings.file_format='JPEG'
s.render.image_settings.color_mode='RGB'
s.render.image_settings.quality=94
for i,(name,camera,look,lens) in enumerate([
    ('climb',(-156.5,-44.7,7.15),(-166,-29.95,3.25),52),
    ('landing',(-159.3,-37.5,10.75),(-166,-30.15,6.25),54),
]):
    for j, group in enumerate(marker):
        for o in group:o.hide_render=i!=j
    aim(cam,camera,look);cam.data.lens=lens
    s.render.filepath=str(out/f'nov25-deck-a-ladder-{name}.jpg')
    bpy.ops.render.render(write_still=True)
