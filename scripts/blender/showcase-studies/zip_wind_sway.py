"""W11a wind art overlay for the exact canonical West zip cable, no gameplay."""
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[3]
stage,out=(Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
parity=json.loads((stage/'parity.json').read_text())['matched_signature']
expected=json.loads((root/'scripts/blender/west-town/expected.json').read_text())
assert parity in [v for v in expected.values() if isinstance(v,list)]
bpy.ops.wm.open_mainfile(filepath=str(stage/'prior/w08-components.blend'))
curve,=[o for o in bpy.context.scene.objects if o.name.startswith('W08 illustrative cable')]
assert curve.type=='CURVE' and len(curve.data.splines)==1
p=[curve.matrix_world@q.co.xyz for q in curve.data.splines[0].points]
assert len(p)==97
assert (p[0]-Vector((-212,34,45))).length<.00001
assert (p[-1]-Vector((-115,16.5,14))).length<.00001
bpy.ops.wm.open_mainfile(filepath=str(stage/'whole-town-editable.blend'))
s=bpy.context.scene
s.render.use_compositing=False
old,=[o for o in s.objects if o.name.startswith('W08 illustrative cable')]
from mathutils.kdtree import KDTree
kdt=KDTree(len(old.data.vertices))
for q in old.data.vertices:kdt.insert(old.matrix_world@q.co,q.index)
kdt.balance()
assert max(kdt.find(v)[2] for v in p)<.067
origin=p[0]
d=(p[-1]-p[0]).normalized()
lateral=Vector((-d.y,d.x,0)).normalized()
A=.38
radius=.065

def matte(name,c,r=.55,metal=0,em=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1)
    b=m.node_tree.nodes['Principled BSDF']
    for key,val in [('Base Color',(*c,1)),('Roughness',r),('Metallic',metal),
                    ('Emission Color',(*c,1)),('Emission Strength',em)]:
        b.inputs[key].default_value=val
    return m

def tube(n,centers,r,ma,radial=8):
    verts=[]
    for j,c in enumerate(centers):
        tangent=(centers[min(j+1,len(centers)-1)]-centers[max(j-1,0)]).normalized()
        across=Vector((0,0,1)).cross(tangent).normalized()
        up=tangent.cross(across).normalized()
        for k in range(radial):
            a=math.tau*k/radial
            verts.append(c+r*(math.cos(a)*across+math.sin(a)*up))
    f=[tuple(reversed(range(radial)))]
    for i in range(len(centers)-1):
        for k in range(radial):
            j=(k+1)%radial
            f.append((i*radial+k,i*radial+j,(i+1)*radial+j,(i+1)*radial+k))
    j=(len(centers)-1)*radial
    f.append(tuple(j+k for k in range(radial)))
    me=bpy.data.meshes.new(n);me.from_pydata(verts,[],f);me.update();me.materials.append(ma)
    for poly in list(me.polygons)[1:-1]:
        poly.use_smooth=True
    o=bpy.data.objects.new(n,me);s.collection.objects.link(o)
    return o

steel=matte('Blackened high-tensile steel',(.039,.053,.067),.36,.74)
ob=tube('W11a visual-only zip cable',[v-origin for v in p],radius,steel)
ob.location=origin
ob.shape_key_add(name='Canonical neutral')
for side,n in [(1,'West gust'),(-1,'East gust')]:
    k=ob.shape_key_add(name=n)
    for j,base in enumerate(k.data):
        ring=j//8
        t=ring/(len(p)-1)
        # sin² keeps both anchors and end tangents still. Flat lead-in
        # protects terminal clamps; the cosmetic cable needs no rig.
        u=(t-.06)/.88
        envelope=math.sin(math.pi*u)**2 if 0<u<1 else 0
        base.co+=lateral*(side*A*envelope)+Vector((0,0,-.076*envelope))
    for frame in range(1,122,3):
        angle=(frame-1)/120*math.tau
        k.value=max(0,math.sin(angle)*side)
        if frame in (1,61,121):k.value=0
        k.keyframe_insert(data_path='value',frame=frame,group='Fixed-anchor sway')
    k.value=0
sk=ob.data.shape_keys
sk.animation_data.action.name='West zip cable · crosswind'
for c in sk.animation_data.action.fcurves:
    for pt in c.keyframe_points:pt.interpolation='LINEAR'
s.render.fps=24
s.frame_start,s.frame_end=1,121
s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True);bpy.context.view_layer.objects.active=ob
dst=out/'w11a-west-zip-sway.glb'
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_anim_slide_to_zero=True,
    export_morph=True,export_morph_normal=False)
raw=dst.read_bytes()
g=json.loads(raw[20:20+int.from_bytes(raw[12:16],'little')])
assert len(g['nodes'])==len(g['meshes'])==len(g['animations'])==1
assert len(g['meshes'][0]['primitives'][0]['targets'])==2
assert len(raw)<100000
bpy.data.objects.remove(ob,do_unlink=True)
before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(dst))
new,=[o for o in set(s.objects)-before if o.type=='MESH']
imported_action=new.data.shape_keys.animation_data.action
assert imported_action and len(imported_action.fcurves)==2
start=round(imported_action.frame_range[0])
assert abs(imported_action.frame_range[1]-start-120)<.0001
s.frame_set(start)
bpy.context.view_layer.update()
# Derive reconstructed contour centres by grouping coincident seam positions
# after glTF splits any vertices. Use the corresponding radial cloud sets.
by_ring=[set() for _ in p]
for v in new.data.vertices:
    w=new.matrix_world@v.co
    i=min(range(len(p)),key=lambda j:(p[j]-w).length_squared)
    assert abs((p[i]-w).length-radius)<.00003
    by_ring[i].add(tuple(round(x,5) for x in w))
assert all(len(x)==8 for x in by_ring)
proof={'scope':'Cosmetic GLB loop only; no change to engine route, sag, collision, rider or weather host.',
    'canonicalScene':parity,'launchWorld':[-212,45,-34],'arrivalWorld':[-115,14,-16.5],
    'sourceRingCount':len(p),'baseRadiusMeters':radius,'planSpanMeters':(p[-1].xy-p[0].xy).length,
    'spatialChordMeters':(p[-1]-p[0]).length,'restSagMeters':1.2,
    'swayPerSideMeters':A,'peakExtraDropMeters':.076,'sleevePerEnd':.06,'periodSeconds':5,
    'bytes':len(raw),'triangles':sum(g['accessors'][t['indices']]['count']//3 for t in g['meshes'][0]['primitives']),
    'blenderReimportCanonicalRadialSamples':sum(len(x) for x in by_ring)}
(out/'validation.json').write_text(json.dumps(proof,indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY'):raise SystemExit(0)

# Matched review images: full geography, then midspan motion reference.
def aim(o,p,t):
    o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
old.hide_render=True
for o in list(s.objects):
    if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
w=bpy.data.worlds.new('West gust clear sky');w.use_nodes=True;s.world=w
nt=w.node_tree;sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA'
sky.sun_elevation=.29;sky.sun_rotation=.62;sky.sun_size=.066;sky.sun_intensity=.72
nt.links.new(sky.outputs[0],nt.nodes.get('Background').inputs['Color'])
nt.nodes.get('Background').inputs['Strength'].default_value=.35
c=bpy.data.cameras.new('West cable review')
cam=bpy.data.objects.new(c.name,c);s.collection.objects.link(cam);s.camera=cam
c.clip_end=760
s.render.engine='CYCLES'
s.cycles.samples=36;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.071
s.cycles.use_denoising=False
s.render.resolution_x,s.render.resolution_y=1580,1010
s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.0
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=94
mid=p[48]
cyan=matte('Reference only: still-air centre',(.016,.59,.77),.42,.06,.65)
gold=matte('Reference only: animated cable tint',(.95,.37,.033),.38,.15,.38)
# The warm tint in the diagnostic frame is a renderer annotation only.
c.type='ORTHO';c.ortho_scale=128
aim(cam,mid+Vector((12,-88,87)),mid+Vector((3,4,-8)))
s.frame_set(start)
s.render.filepath=str(out/'nov25-zip-sway-route.jpg');bpy.ops.render.render(write_still=True)

for i in range(6,91,6):
    tube('Diagnostic calm dash',p[i:i+3],.026,cyan,6)
new.data.materials[0]=gold
c.type='PERSP';c.lens=46
s.render.resolution_y=770
aim(cam,mid+lateral*12+Vector((0,0,13.5)),mid+Vector((3,0,-1.15)))
s.frame_set(start+30)
s.render.filepath=str(out/'nov25-zip-sway-offset.jpg');bpy.ops.render.render(write_still=True)
