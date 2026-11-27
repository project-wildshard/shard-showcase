"""Fit two archived W9b finds, reusing the exact original Gold GLB and W08."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index('--') + 1])
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[3]
gold = ROOT/'public/assets/wildshard-art/w9b-gold-find-cube.glb'
SHA = '3dfd3a95e261b340911f5b93ffce91a8840a91a0464b915336567aa2f3b6bce0'
assert hashlib.sha256(gold.read_bytes()).hexdigest() == SHA
S = bpy.context.scene
DG = bpy.context.evaluated_depsgraph_get()

def to_world(v):
    return [round(v[0],5),round(v[2],5),round(-v[1],5)]

def tree(meshes):
    verts, polys = [], []
    for obj in sorted(meshes, key=lambda o:o.name):
        e = obj.evaluated_get(DG)
        m = e.to_mesh()
        n = len(verts)
        verts.extend(e.matrix_world @ v.co for v in m.vertices)
        polys.extend(tuple(n+i for i in p.vertices) for p in m.polygons)
        e.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)

def bounds(obj):
    p=[obj.matrix_world@Vector(v) for v in obj.bound_box]
    return [(min(v[i] for v in p),max(v[i] for v in p)) for i in range(3)]

def in_box(obj, x, y, z, radius):
    return all(b>=q-r and a<=q+r for (a,b),q,r in
        zip(bounds(obj),(x,y,z),(radius,radius,3.5)))

def solid(x,y,z,r,h):
    v=[(x+i*r,y+j*r,z+k*h) for k in (0,1) for j in (-1,1) for i in (-1,1)]
    return BVHTree.FromPolygons(v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])

def sample_floor(b,x,y,h):
    hit, normal, _, _=b.ray_cast(Vector((x,y,h+.30)),Vector((0,0,-1)),1.9)
    return None if hit is None or abs(normal.z)<.97 else hit.z

def clear_ray(b,a,c):
    d=c-a
    hit=b.ray_cast(a,d.normalized(),d.length-.04)[0]
    return hit is None

meshes=[o for o in S.objects if o.type=='MESH']
placed=[]
for name,raw,radius,prefix in [
    ('tower-deck-4',(-212,36.6,-34),10.5,'MODULE-001'),
    ('zip-house-roof',(-110,12.5,-12),5.4,'ZIP | Zip House rooftop plane'),
]:
    x,h,z=raw
    y=-z
    m=[o for o in meshes if in_box(o,x,y,h,radius+2)]
    assert any(o.name.startswith(prefix) for o in m)
    b=tree(m)
    offsets=sorted(itertools.product(range(-round(radius*4),round(radius*4)+1),repeat=2),
                   key=lambda d:(d[0]**2+d[1]**2,abs(d[1]),d))
    checks=[(i*.185,j*.185) for i,j in itertools.product(range(-3,4),repeat=2)]
    selected=None
    for ix,iy in offsets:
        if math.hypot(ix/4,iy/4)>radius:continue
        xx,yy=x+ix/4,y+iy/4
        base=sample_floor(b,xx,yy,h)
        # Only accept the intended deck tier, with a broad flat seat and half-metre hover.
        if base is None or abs(base-(h-.5))>.33:continue
        probes=[sample_floor(b,xx+dx,yy+dy,h) for dx,dy in checks]
        if any(p is None or abs(p-base)>.015 for p in probes):continue
        height=h if .36<=h-base<=.65 else base+.5
        if b.overlap(solid(xx,yy,height,.52,1.04)):continue
        eye,target=None,Vector((xx,yy,height+.52))
        for angle in range(0,360,45):
            a=math.radians(angle)
            p=Vector((xx+1.85*math.cos(a),yy+1.85*math.sin(a),base+1.7))
            floor=[sample_floor(b,p.x+i*.26,p.y+j*.26,h)
                   for i,j in itertools.product((-1,0,1),repeat=2)]
            if any(f is None or abs(f-base)>.04 for f in floor):continue
            if b.overlap(solid(p.x,p.y,base+.06,.32,1.74)):continue
            if not clear_ray(b,p,target):continue
            eye=p
            break
        if eye is not None:
            selected=(xx,yy,height,base,eye,probes)
            break
    assert selected, name
    xx,yy,height,base,eye,probes=selected
    p=Vector((xx,yy,height))
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(gold))
    group=set(S.objects)-before
    for o in group:
        if o.parent not in group:o.matrix_world=Matrix.Translation(p)@o.matrix_world
    bpy.context.view_layer.update()
    gold_meshes=[o for o in group if o.type=='MESH']
    assert gold_meshes and not b.overlap(tree(gold_meshes))
    dim=[bounds(o) for o in gold_meshes]
    assert abs(min(v[2][0] for v in dim)-height)<.002
    assert abs(max(v[2][1] for v in dim)-height-1)<.03
    source=Vector((x,y,h))
    placed.append((name,p,eye,dict(id=name,archive_xyz=raw,fit_xyz=to_world(p),
        offset_m=round((p-source).length,5),roof_y=round(base,5),hover_m=round(height-base,5),
        sampled_floor_points=len(probes),floor_spread_mm=round((max(probes)-min(probes))*1000,4),
        exact_GLB_intersects_W08=False,camera_eye_xyz=to_world(eye),visible_from_sampled_eye=True,
        archive_center_surface_y=(round(f,5) if (f:=sample_floor(b,x,y,h)) is not None else None))))

parity=json.loads((Path(bpy.data.filepath).parent/'parity.json').read_text())
assert parity['matched_signature']==['6e6b1692565a314162d3861223ab3454e9475e23bb1a2e01a88a14e76be6722f',2580]
receipt=dict(scope='Static Gold placement on the exact authored W08 tower deck tier and roof, not a pickup or traversal test.',
    gold_sha256=SHA,w08_semantic_signature=parity['matched_signature'],
    round5_ref='ce1cf050b3:art/showcase-template/round-5-blockout/layout.js',
    placements=[r[3] for r in placed])
(OUT/'rooftop-gold-proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
if '--proof-only' in sys.argv:raise SystemExit(0)

S.render.engine='CYCLES';S.cycles.samples=24
S.cycles.use_denoising=True
S.render.resolution_percentage=100
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=94
S.render.resolution_x,S.render.resolution_y=1200,840
S.view_settings.view_transform='AgX'
for obj in S.objects:
    if obj.type=='LIGHT':obj.hide_render=True
world=bpy.data.worlds.new('Clear west evening');world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs[0].default_value=(.34,.48,.70,1);bg.inputs[1].default_value=.41
S.world=world
sun=bpy.data.lights.new('Late exterior key','SUN')
sun.energy=2.25;sun.color=(1,.91,.75);sun.angle=.12
lamp=bpy.data.objects.new('Late exterior key',sun);S.collection.objects.link(lamp)
lamp.rotation_euler=(.47,-.83,-.60)
cam=bpy.data.cameras.new('Rooftop Gold evidence');cam.lens=34;cam.clip_end=390
o=bpy.data.objects.new(cam.name,cam);S.collection.objects.link(o);S.camera=o
for name,p,eye,_ in placed:
    o.location=eye
    o.rotation_euler=(p+Vector((0,0,.60))-eye).to_track_quat('-Z','Y').to_euler()
    S.render.filepath=str(OUT/f'{name}.jpg')
    bpy.ops.render.render(write_still=True)
