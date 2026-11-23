"""Measure and render the existing full-size Station 6 junction, without new geometry."""
from pathlib import Path
import json
import runpy
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
args=sys.argv[sys.argv.index('--')+1:]
assert len(args)==2 or len(args)==3 and args[2]=='--measure-only', 'Pass junction GLB, output directory, and optionally --measure-only.'
source,out=map(Path,args[:2])
out.mkdir(parents=True,exist_ok=True)
sig=runpy.run_path(str(root/'scripts/blender/west-scene-r02/semantic_glb.py'))['signature']
expected=json.loads((root/'scripts/blender/west-movers-roof/expected.json').read_text())['junction']['semantic_signature']
assert list(sig(source))==expected
s=bpy.context.scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(source))
bpy.context.view_layer.update()
def match(txt):
    return sorted((o for o in s.objects if o.type=='MESH' and txt in o.name),key=lambda o:o.name)
def tree(objects):
    verts,faces=[],[]
    for o in objects:
        faces.extend(tuple(len(verts)+i for i in f.vertices) for f in o.data.polygons)
        verts.extend(o.matrix_world@p.co for p in o.data.vertices)
    return BVHTree.FromPolygons(verts,faces)
A=Vector((-168,103,18))
B=Vector((-190,104,18))
axis=(B-A).normalized()
side=Vector((-axis.y,axis.x,0))
parts={
  'deck':match('Station6 top deck'),
  'roof':match('continuous landable roof'),
  'threshold_a':match('deck flush threshold'),
  'threshold_b':match('roof flush threshold'),
  'planks':match('individual cedar plank'),
}
assert [len(parts[n]) for n in parts]==[1,1,1,1,54]
trees={k:tree(v) for k,v in parts.items()}
def height(k,p):
    v=trees[k].ray_cast(p+Vector((0,0,4)),(0,0,-1),8)[0]
    return None if v is None else v.z
def row(anchor,forward,k,t):
    # Outward from solid land towards middle. The ray resolves actual skin,
    # separately by object family so the overlaid threshold stays measurable.
    offsets=(-.50,-.15,0,.15,.30,.40,.50,.65,.80)
    widths=(-.65,0,.65)
    result=[]
    for q in offsets:
        for w in widths:
            p=anchor+forward*q+side*w
            hits={}
            for label in (k,t,'planks'):
                h=height(label,p)
                if h is not None:hits[label]=round(h,5)
            result.append({'into_bridge_m':q,'cross_m':w,'surface_m':hits})
    return result
lanes={'station6':row(A,axis,'deck','threshold_a'),
       'tank':row(B,-axis,'roof','threshold_b')}
numbers={}
for key,anchor,dir,k,t in (
  ('station6',A,axis,'deck','threshold_a'),('tank',B,-axis,'roof','threshold_b')):
    center_plank=height('planks',anchor+dir*((B-A).length/108))
    assert center_plank is not None and abs(center_plank-17.97615)<.002
    land=height(k,anchor-dir*.5)
    cap=height(t,anchor)
    assert abs(land-18)<.001 and abs(cap-18.012)<.001
    numbers[key]={'walking_surface_m':round(land,5),'threshold_m':round(cap,5),
       'first_plank_center_m':round(center_plank,5),'threshold_above_land_mm':round((cap-land)*1e3,2),
       'first_plank_below_threshold_mm':round((cap-center_plank)*1e3,2)}
# Locate the first open seam on each of the three sampled lanes to sub-mm
# resolution. Searching only the known first seam interval avoids a claim
# about continuous contact, the corners of each board, or native collision.
def width_at(anchor,direction,offset):
    def hit(t):
        return height('planks',anchor+direction*t+side*offset) is not None
    assert hit(.36) and not hit(.4) and hit(.44)
    def border(lo,hi,left):
        for _ in range(12):
            mid=(lo+hi)/2
            if hit(mid)==left:
                lo=mid
            else:
                hi=mid
        return (lo+hi)/2
    a=border(.36,.4,True)
    b=border(.4,.44,False)
    return round((b-a)*1000,2)
for label,anchor,heading in (('station6',A,axis),('tank',B,-axis)):
    gaps=[width_at(anchor,heading,w) for w in (-.65,0,.65)]
    assert all(abs(x-25)<.3 for x in gaps),gaps
    numbers[label]['first_plank_gap_mm_at_three_lanes']=gaps
mid=height('planks',(A+B)/2+axis*.10)
assert mid is not None and abs(mid-17.35)<.002
print(numbers,flush=True)
(out/'validation.json').write_text(json.dumps({'span_m':round((B-A).length,6),'plank_count':54,
    'anchor_map':[-168,18,-103,-190,18,-104],'samples':lanes,'center_height_m':round(mid,5),
    'measurements':numbers,'geometry_changed':False,'native_runtime':False},indent=2)+'\n')

if len(args)==3:
    sys.exit(0)

# Show only existing exported Station 6 and junction geometry. The backdrop
# and lights are not assets; no original mesh or object placement is changed.
for o in s.objects:
    if o.type=='MESH':
        o.hide_render=not (o.name.startswith('JUNCTION |') or 'Station6' in o.name)

def aim(o,q):
    o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,p,q,power,c,size):
    d=bpy.data.lights.new(n,'AREA')
    d.energy=power;d.color=c;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new('High steel blue')
s.world.color=(.25,.29,.34)
area('Wide key',(-173,96,27),(-178,105,18),4800,(1,.79,.55),9)
area('Wide roof bounce',(-192,96,24),(-188,105,18),4500,(.59,.83,1),10)
area('Warm rim',(-183,114,27),(-179,103,18),4100,(1,.88,.68),13)
c=bpy.data.cameras.new('Existing landing inspection')
s.camera=bpy.data.objects.new(c.name,c);s.collection.objects.link(s.camera)
c.type='ORTHO';c.ortho_scale=7.2
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_x,s.render.resolution_y=1320,900
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=91
for name,p,q in (
    ('nov23-station6-deck-threshold',A-axis*1.2-side*5+Vector((0,0,4.1)),A+axis*.60),
    ('nov23-station6-tank-threshold',B+axis*1.2+side*5+Vector((0,0,4.1)),B-axis*.60)):
    s.camera.location=p;aim(s.camera,q)
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
