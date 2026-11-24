"""E4 ground cue from East surface palette, static and bloom-free."""
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from mathutils.geometry import tessellate_polygon

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory

out=output_directory()
clear_scene()
s=bpy.context.scene
rng=random.Random(404)
cfg=json.loads((ROOT/'project/layouts/wsc-scene-005-east-material-key.json').read_text())
brick,slate=cfg['cards'][3:5]
assert brick['ref']=='e04.jpg' and slate['ref']=='e05.jpg'


def mat(name,rgb,e=0,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*rgb,1)
    q.inputs['Metallic'].default_value=metal
    q.inputs['Roughness'].default_value=.64
    q.inputs['Emission Color'].default_value=(*rgb,1)
    q.inputs['Emission Strength'].default_value=e
    return m


patch_palette=[
    mat('Slag cooled soot',(.011,.015,.016)),
    mat('Slag black glass crust',(.038,.031,.023),0,.11),
    mat('Slag warm iron crust',(.14,.040,.008),0,.12),
    mat('Slag orange fracture',(.87,.104,.008),1.0),
    mat('Slag gold heat rim',(.99,.265,.030),2.3),
    mat('Slag hot yellow flecks',(1.00,.51,.088),2.9)]
v,f,mids=[],[],[]
N=68
radius=[.453+.021*math.sin(i*math.tau/N*5)+.013*math.sin(i*math.tau/N*11)
        +rng.uniform(-.012,.011) for i in range(N)]


def layer(frac,z):
    return [(radius[i]*frac*math.cos(i*math.tau/N),
             radius[i]*frac*math.sin(i*math.tau/N),z) for i in range(N)]


def poly(coords,m):
    ids=tuple(range(len(v),len(v)+len(coords)))
    v.extend(coords);f.append(ids);mids.append(m)


layers=[layer(k,z) for k,z in ((1.025,0),(.96,.0002),(.85,.0004),(.75,.0006),(.50,.0007))]
gaps={1,2,14,15,16,27,28,43,44,56,57,58,65}
for row in range(len(layers)-1):
    for i in range(N):
        j=(i+1)%N
        if row==0:m=0 if i%4 else 1
        elif row==1:m=2 if i in gaps else (4 if i%12<4 else 3)
        elif row==2:m=3 if i%8==0 and i not in gaps else 2
        else:m=1 if i%4 else 2
        poly([layers[row][i],layers[row][j],layers[row+1][j],layers[row+1][i]],m)
poly(layers[-1],1)
# Fractured streaks and detached cinders make the silhouette asymmetric.
def shard(x,y,a,length,width,m,z=.0010):
    u=Vector((math.cos(a),math.sin(a),0));w=Vector((-u.y,u.x,0))
    p=Vector((x,y,z))
    poly([tuple(p+du*length*u+dv*width*w) for du,dv in
           [(-.51,-.25),(.16,-.62),(.51,.02),(.11,.46),(-.38,.33)]],m)
for x,y,a,l,w in [(-.07,-.19,.7,.21,.028),(.04,-.13,1.1,.18,.023),
                  (-.125,.08,.3,.16,.025),(.16,.05,1.86,.13,.024),
                  (.041,.13,-.4,.16,.024),(.21,-.15,1.26,.12,.019)]:
    shard(x,y,a,l,w,3)
    shard(x+.02,y+.005,a,l*.59,w*.53,5,.0013)
for k in range(19):
    a=rng.uniform(0,math.tau);r=rng.uniform(.465,.542)
    shard(r*math.cos(a),r*math.sin(a),a+rng.uniform(-1.3,1.3),
          rng.uniform(.023,.08),rng.uniform(.007,.028),2+(k%3==0))
mesh=bpy.data.meshes.new('E4 slag silhouette')
mesh.from_pydata(v,[],f)
for m in patch_palette:mesh.materials.append(m)
for p,i in zip(mesh.polygons,mids):p.material_index=i
patch=bpy.data.objects.new('E4 Ground slag decal',mesh)
s.collection.objects.link(patch)
path=out/'e4-ground-slag-decal.glb'
export([patch],path)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(doc['nodes'])==len(doc['meshes'])==1
assert not any(k in doc for k in ('images','animations','skins','cameras'))
assert sum(1 for a in doc['materials'] if a.get('emissiveFactor'))==3
tris=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
bpy.data.objects.remove(patch,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(path))
patch=next(o for o in s.objects if o.type=='MESH')
# Offline stills use emission to camera only, never to the ground or donor.
for m in patch.data.materials:
    n=m.node_tree.nodes
    q=n.get('Principled BSDF')
    socket=q.inputs['Emission Strength']
    if socket.default_value<=0:continue
    lp=n.new('ShaderNodeLightPath')
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY'
    mul.inputs[1].default_value=socket.default_value
    s0=m.node_tree.links
    s0.new(lp.outputs['Is Camera Ray'],mul.inputs[0])
    s0.new(mul.outputs[0],socket)


def box(name,p,d,ma):
    x,y,z=p;a,b,c=[q*.5 for q in d]
    d=bpy.data.meshes.new(name)
    d.from_pydata([(x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
        [],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
    d.materials.append(ma)
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
    return o


def stage_surface(name,tone,nx,ny,x=0):
    pal=[mat(name+' '+str(i),tuple(c*m for c in tone))
         for i,m in enumerate((.78,.88,.99,1.04,1.10,1.18))]
    obs=[box(name+' grout',(x,-1.9,-.11),(9.10,12.6,.18),pal[0])]
    w,d=9.10/nx,12.60/ny
    for j in range(ny):
        edges=[-4.55]+[-4.55+(k+.48*(j%2))*w for k in range(1,nx)]+[4.55]
        for l,r in zip(edges,edges[1:]):
            obs.append(box(name,(x+(r+l)*.5,-8.2+(j+.5)*d,-.06),
                           (r-l-.018,d-.018,.123),rng.choice(pal)))
    return obs


brick_bits=stage_surface('E04 foundry brick',brick['tone'],22,34)
slate_bits=stage_surface('E05 gray slate',slate['tone'],6,12,x=18)


def tree(items):
    vs,fs=[],[]
    for o in items:
        n=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(n+j for j in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)


def fit(floor,x):
    t=tree(floor)
    heights=[]
    for i in range(-7,8):
        for j in range(-7,8):
            xx,yy=i*.076,j*.076
            if xx*xx+yy*yy>.55**2:continue
            p=t.ray_cast(Vector((x+xx,yy,.2)),Vector((0,0,-1)),.40)[0]
            assert p is not None
            heights.append(p.z)
    return max(heights)+.003, len(heights)


furnace_name,pin=brick['donor']
src=ROOT/'public/assets/wildshard-art'/furnace_name
assert hashlib.sha256(src.read_bytes()).hexdigest()==pin
before=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(src))
new=sorted(set(s.objects)-before,key=lambda o:o.name)
coords=[o.matrix_world@v.co for o in new if o.type=='MESH' for v in o.data.vertices]
lo,hi=[Vector(tuple(fn(p[k] for p in coords) for k in range(3))) for fn in (min,max)]
origin=Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,lo.z))
T=Matrix.Translation((.85,2.55,.003))@Matrix.Translation(-origin)
for o in new:
    if o.parent not in new:o.matrix_world=T@o.matrix_world
patch_z,count=fit(brick_bits,0)
slate_z,count_slate=fit(slate_bits,18)

world=bpy.data.worlds.new('E04 studio ambience')
world.use_nodes=True
q=world.node_tree.nodes['Background']
q.inputs['Color'].default_value=(.25,.34,.52,1)
s.world=world


def area(n,p,target,col,size):
    d=bpy.data.lights.new(n,'AREA');d.color,d.size=col,size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o


key=area('Existing studio key',(-3,-2,6),(0,0,0),(1,.79,.61),8.5)
fill=area('Existing skylight',(4,3,5),(0,0,0),(.64,.79,1),7)
cam=bpy.data.objects.new('Fixed portrait crop',bpy.data.cameras.new('Fixed portrait crop'))
s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.063
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=92;s.view_settings.view_transform='AgX';s.render.use_compositing=False


def shot(n,x,p,target,fov,dims,energy):
    patch.location=(x,0,patch_z if not x else slate_z)
    key.location.x=x-3;fill.location.x=x+4
    for o in (key,fill):
        o.rotation_euler=(Vector((x,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
    key.data.energy,fill.data.energy,q.inputs['Strength'].default_value=energy
    cam.location=p;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36
    cam.data.lens=36/(2*math.tan(math.radians(fov)/2))
    s.render.resolution_x,s.render.resolution_y=dims
    s.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)


day=(1900,1500,.50);dim=(140,160,.10)
frames=(804,1748)
for label,light in [('portrait-day',day),('portrait-dim',dim)]:
    shot(label,0,(0,-6,1.70),(0,0,patch_z),55,frames,light)
coords=[world_to_camera_view(s,cam,patch.matrix_world@v.co) for v in patch.data.vertices]
span=[round((max(v[k] for v in coords)-min(v[k] for v in coords))*pixels,2)
      for k,pixels in enumerate((402,874))]
assert 27<span[1]<46
shot('slate-detail',18,(18.63,-1.35,.97),(18,0,.01),46,(1120,850),dim)
proof={'scope':'E4 static decal geometry study only; no damage, timing, status, placement or actor.',
       'references':['E04 brick','E05 slate alternate','E4-band4-welder-units.md'],
       'furnace_unchanged_sha256':pin,'asset':{'bytes':len(raw),'triangles':tris,'sha256':hashlib.sha256(raw).hexdigest()},
       'portrait_reference_px':[402,874],'portrait_oversample':2,'degrees_vertical_fov':55,
       'eye_height_m':1.70,'distance_m':6,'projection_bbox_px':span,
       'floor_probes':[count,count_slate],'floor_lift_over_highest_mm':3,
       'preview':'Matched portrait camera/exposure. No bloom and no extra light from the material; camera-only emission in Blender preview.'}
(out/'e4-slag-decal.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
