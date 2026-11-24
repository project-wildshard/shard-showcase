"""E13 Gold art fit at the archived Titan arch crown; no runtime changes."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory
out=output_directory()
clear_scene()
sc=bpy.context.scene
assets=HERE.parents[2]/'public/assets/wildshard-art'
arch_name='wsc-arch-008-titan-surface-gate.glb'
gold_name='w9b-gold-find-cube.glb'
pins={arch_name:'d52c233e077aa4f8178482b16ea44210464d077b5cb4c28b759ec1e7b2a2c73c',
      gold_name:'3dfd3a95e261b340911f5b93ffce91a8840a91a0464b915336567aa2f3b6bce0'}


def load(path,T=Matrix.Identity(4)):
    previous=set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    new=sorted(set(sc.objects)-previous,key=lambda o:o.name)
    world={o:o.matrix_world.copy() for o in new}
    for o in new:
        if o.parent not in new:o.matrix_world=T@world[o]
    bpy.context.view_layer.update()
    return [o for o in new if o.type=='MESH']


def donor(n,T):
    p=assets/n
    assert hashlib.sha256(p.read_bytes()).hexdigest()==pins[n]
    return load(p,T)


def vertices(obs):
    return [o.matrix_world@v.co for o in obs for v in o.data.vertices]


def tree(obs):
    v,f=[],[]
    for ob in obs:
        base=len(v)
        v.extend(ob.matrix_world@x.co for x in ob.data.vertices)
        f.extend(tuple(base+n for n in p.vertices) for p in ob.data.polygons)
    return BVHTree.FromPolygons(v,f)


arch=donor(arch_name,Matrix.Identity(4))
h=max(v.z for v in vertices(arch))
scale=18/h
T=Matrix.Rotation(math.pi,4,'Z')@Matrix.Scale(scale,4)
for o in arch:
    if o.parent is None:o.matrix_world=T@o.matrix_world
bpy.context.view_layer.update()
assert abs(max(v.z for v in vertices(arch))-18)<2e-5
width=max(v.x for v in vertices(arch))-min(v.x for v in vertices(arch))
A=tree(arch)


def down(t,x,y):
    return t.ray_cast(Vector((x,y,24)),Vector((0,0,-1)),15)[0]


def mat(name,color,metal=0,rough=.57):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*color,1)
    b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
    return m


steel=mat('Crown dark cast collar',(.068,.098,.119),.64)
deep=mat('Crown blued upper plate',(.16,.22,.26),.70)
copper=mat('Crown orange edge inlay',(.57,.204,.048),.48,.44)


def prism(name,rings,ma):
    n=len(rings[0]); k=len(rings)
    f=[tuple(reversed(range(n)))]
    for l in range(k-1):
        for i in range(n):
            a=l*n+i;b=l*n+(i+1)%n
            f.append((a,b,b+n,a+n))
    f.append(tuple(range((k-1)*n,k*n)))
    m=bpy.data.meshes.new(name)
    m.from_pydata([p for ring in rings for p in ring],[],f)
    m.materials.append(ma)
    o=bpy.data.objects.new(name,m);sc.collection.objects.link(o)
    return o


def xy(w,d):
    x=w/2;y=d/2;k=.19
    return [(x-k,-y),(x,-y+k),(x,y-k),(x-k,y),(-x+k,y),(-x,y-k),(-x,-y+k),(-x+k,-y)]


def plane(w,d,z):
    return [(x,y,z-18) for x,y in xy(w,d)]


# Every foot vertex is measured on the scaled donor; the bottom follows crown curvature.
rim=xy(1.72,1.64)
anchored=[down(A,x,y).z for x,y in rim]
assert min(anchored)>17.85 and max(anchored)<18.0001
parts=[
    prism('Seated crown base',[[(x,y,z-18-.010) for (x,y),z in zip(rim,anchored)],
                             plane(1.64,1.56,18.18)],steel),
    prism('Recessed amber welt',[plane(1.61,1.53,18.18),plane(1.46,1.38,18.26)],copper),
    prism('Machined collectible seat',[plane(1.42,1.34,18.26),
                                      plane(1.38,1.30,18.44),
                                      plane(1.26,1.26,18.50)],deep)
]
path=out/'e13-titan-crown-seat.glb'
export(parts,path)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
triangles=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert not any(k in doc for k in ('images','skins','animations','cameras'))
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
seat=load(path,Matrix.Translation((0,0,18)))
t=tree(seat)
xy_samples=[(x,y) for x in (-.445,0,.445) for y in (-.445,0,.445)]
levels=[down(t,x,y).z for x,y in xy_samples]
assert max(abs(z-18.5) for z in levels)<.00005
# Keep the Gold donor unscaled at the archived marker; shift 0.3 mm to remove its geometry epsilon.
gold=donor(gold_name,Matrix.Translation((0,0,18.5003)))
lo=min(v.z for v in vertices(gold))
assert abs(lo-18.5)<.00005

world=bpy.data.worlds.new('Titan plaza blue dusk')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.39,.58,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
sc.world=world


def lamp(n,kind,pos,look,watts,size,color):
    d=bpy.data.lights.new(n,kind);d.energy,d.color=watts,color
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=pos
    o.rotation_euler=(Vector(look)-o.location).to_track_quat('-Z','Y').to_euler()


lamp('Plaza sunlight','SUN',(-13,12,29),(0,0,7),2.45,.12,(1,.72,.46))
lamp('Gold fill','AREA',(1,3.5,22),(0,0,18.5),440,4.1,(.70,.86,1))
lamp('Crown backlight','AREA',(2,-3,22),(0,0,18.5),330,5.1,(1,.77,.44))
lamp('Threshold shadow fill','AREA',(0,12,8),(0,0,7),1750,9.7,(.55,.76,1))
bpy.ops.mesh.primitive_plane_add(size=165,location=(0,0,-.009))
bpy.context.object.data.materials.append(mat('Review plaza warmer concrete',(.27,.21,.14),0,.83))
cam=bpy.data.objects.new('Titan crown review camera',bpy.data.cameras.new('Titan crown review camera'))
sc.collection.objects.link(cam);sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=66;sc.cycles.use_denoising=False
sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.046
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=91;sc.view_settings.view_transform='AgX'


def render(n,p,target,lens,wh):
    cam.location=p
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    sc.render.resolution_x,sc.render.resolution_y=wh
    sc.render.filepath=str(out/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)


render('crown-close',(3.3,4.6,21.5),(0,0,18.7),54,(1120,880))
ground=Vector((-4,25,1.7))
render('plaza-eye',ground,(0,0,10.2),33,(1140,950))
direction=Vector((0,0,19))-ground
ray=A.ray_cast(ground,direction.normalized(),direction.length)[0]
coords=[world_to_camera_view(sc,cam,v) for v in vertices(gold)]
assert min(v.x for v in coords)>0 and max(v.x for v in coords)<1
report={
 'scope':'Art-only restaging of the E13 Gold cue on the modern WSC-ARCH-008 gate; no pickup, path, parkour or gameplay.',
 'archive':'ce1cf050b3 art/showcase-template/round-5-blockout/layout.js and lab.js',
 'map_arch_xz':[216,229],'map_gold_base':[216,18.5,229],'archive_arch_top_m':18,
 'unscaled_crown_height_m':round(h,5),'uniform_art_stage_scale':round(scale,6),
 'scaled_arch_outer_width_m':round(width,4),'archived_lintel_width_m':22,
 'stage_world_from_gltf':'[216+x, y, 229+z] for the full stage only. The small seat GLB uses origin at crown (216,18,229).',
 'sampled_arch_crown_y_m':[round(z,6) for z in anchored],
 'seat_surface_y_m':[round(z,6) for z in levels],
 'gold_actual_base_y_m':round(lo,6),
 'plaza_eye_height_m':1.7,'plaza_eye_to_gold_center_ray_blocked_by_gate':ray is not None,
 'unchanged_donors':pins,'asset':{'bytes':len(raw),'triangles':triangles,'sha256':hashlib.sha256(raw).hexdigest()}}
(out/'titan-crown-gold.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
