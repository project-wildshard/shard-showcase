"""W9b Gold find collectible, reimported studio and Station 6 fit previews."""
import json
from pathlib import Path
import runpy
import struct
import sys
import math

import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export

source,out=map(Path,sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[3]
signature=runpy.run_path(str(root/'scripts/blender/west-scene-r02/semantic_glb.py'))['signature']
assert list(signature(source))==json.loads((root/'scripts/blender/west-movers-roof/expected.json').read_text())['junction']['semantic_signature']
s=bpy.context.scene
clear_scene()


def mat(name,color,metal=0,rough=.42,em=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes['Principled BSDF']
    for k,v in [('Base Color',(*color,1)),('Metallic',metal),('Roughness',rough),
                ('Emission Color',(*color,1)),('Emission Strength',em)]:
        bs.inputs[k].default_value=v
    return m


deep=mat('Dark antique brass underlay',(.29,.105,.026),.79,.39)
rim=mat('Polished warm gold',(.92,.431,.072),.80,.24)
face=mat('Brushed satin gold',(.76,.338,.042),.64,.34)
groove=mat('Dark chased lines',(.17,.056,.013),.54,.41)
line=mat('Amber inset',(.85,.246,.022),.24,.37,.38)
bright=mat('Bright gold enamel mark',(.98,.681,.246),.46,.27,.10)


def cube(name, xyz, loc, ma, bevel=0,seg=2):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name
    o.dimensions=xyz
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    if bevel:
        m=o.modifiers.new('Chased edge','BEVEL');m.width=bevel;m.segments=seg
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def section(name,poly,y0,y1,ma):
    n=len(poly)
    vv=[(x,y,z) for y in (y0,y1) for x,z in poly]
    ff=[tuple(range(n)),tuple(reversed(range(n,n*2)))]
    ff.extend((i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n))
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update();me.materials.append(ma)
    o=bpy.data.objects.new(name,me);s.collection.objects.link(o);return o


def diamond(w,h,cx=0,cz=0):
    return [(cx,cz-h),(cx+w,cz),(cx,cz+h),(cx-w,cz)]


def edges(name,r,sx,y0,y1,ma):
    outer=diamond(r,r)
    inner=diamond(r-sx,r-sx)
    return [section(name,[outer[i],outer[(i+1)%4],inner[(i+1)%4],inner[i]],y0,y1,ma) for i in range(4)]


def join(items,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join()
    items[0].name=name;items[0].data.name=name
    return items[0]


body=cube('Gold core',(.934,)*3,(0,0,0),deep,.043,3)
plate=cube('Face lip',(.798,.061,.798),(0,-.465,0),rim,.028)
parts=[plate,cube('Face plate',(.681,.032,.681),(0,-.480,0),face,.016)]
parts+=edges('Recessed lozenge shoulder',.226,.044,-.497,-.491,groove)
parts+=edges('Gold line inset',.216,.014,-.498,-.496,line)
parts+=[
    section('Raised abstract mark',diamond(.105,.105),-.500,-.498,bright),
    section('Recess in the mark',diamond(.043,.043),-.5003,-.50005,groove),
]
for x,z in ((-.278,-.278),(-.278,.278),(.278,-.278),(.278,.278)):
    parts.append(section('Corner stamp',diamond(.028,.028,x,z),-.4975,-.494,groove))
panel=join(parts,'Cast face')
for t in [Matrix.Rotation(i*math.pi/2,4,'Z') for i in range(4)]+[
    Matrix.Rotation(math.pi/2,4,'X'),Matrix.Rotation(-math.pi/2,4,'X')]:
    o=bpy.data.objects.new('Panel',panel.data);s.collection.objects.link(o)
    o.matrix_world=Matrix.Translation((0,0,.5))@t@panel.matrix_world
body.location.z=.5
bpy.data.objects.remove(panel,do_unlink=True)
donor=out/'w9b-gold-find-cube.glb'
export([o for o in s.objects if o.type=='MESH'],donor)
raw=donor.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(doc['meshes'])==2 and len(doc['nodes'])==7 and len(raw)<85000 and tri<1300, (len(raw),tri)
assert not any(doc.get(k) for k in ('images','skins','animations'))
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(donor))
bpy.context.view_layer.update()
gold=list(s.objects)
points=[o.matrix_world@v.co for o in gold for v in o.data.vertices]
mins=[min(v[i] for v in points) for i in range(3)]
maxs=[max(v[i] for v in points) for i in range(3)]
assert max(abs((b-a)-1) for a,b in zip(mins,maxs))<.001, (mins,maxs)


def aim(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()


def area(name,loc,target,w,color,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=w;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target);return o


def obj(name,data):
    o=bpy.data.objects.new(name,data);s.collection.objects.link(o);return o


d=bpy.data.cameras.new('Gold review');cam=obj('Gold review',d);s.camera=cam
s.world=bpy.data.worlds.new('Steel-blue studio')
s.world.color=(.22,.25,.31)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91


def shot(name,eye,t,wh,scale=None,lens=33):
    cam.location=eye;aim(cam,t);d.type='ORTHO' if scale else 'PERSP'
    if scale: d.ortho_scale=scale
    d.lens=lens;s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(name+'.jpg'));bpy.ops.render.render(write_still=True)


plinth=cube('Studio slate only',(200,200,.1),(0,0,-.35),mat('Slate',(.051,.067,.083),.22,.48))
lights=[
    area('Cold window',(-2,-3,4),(0,0,.4),430,(.73,.84,1),2.4),
    area('Warm edge',(1.5,1.7,2.1),(0,0,.46),310,(1,.78,.42),2.0),
    area('Silk fill',(2,-1,1.3),(0,0,.48),170,(.91,.91,1),1.8),
]
shot('nov23-gold-find-studio',(2.7,-3.6,2.4),(0,0,.42),(1140,970),2.30)
for o in [plinth,*lights]:bpy.data.objects.remove(o,do_unlink=True)
existing=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(source))
bpy.context.view_layer.update()
roof=[o for o in set(s.objects)-existing if 'continuous landable roof' in o.name]
assert len(roof)==1
o=roof[0]
M=o.matrix_world.inverted()
archived=Vector((-206,104,18.5))
staged=archived+Vector((0,-2.5,0))
meshes=[o for o in set(s.objects)-existing if o.type=='MESH']

def bounds(o):
    bb=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [(min(v[i] for v in bb),max(v[i] for v in bb)) for i in range(3)]

def overlaps(location):
    region=list(zip(location+Vector(mins),location+Vector(maxs)))
    return sorted(mesh.name for mesh in meshes
                  if all(a < d and c < b for (a,b),(c,d) in zip(region,bounds(mesh))))

blocked=overlaps(archived)
assert any('roof hook pedestal' in n for n in blocked),blocked
assert not overlaps(staged),overlaps(staged)
roof_heights=[]
for x,y in ((0,0),(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)):
    origin=Vector((staged.x+x,staged.y+y,21.5))
    hit,p,*_=o.ray_cast(M@origin,M.to_3x3()@Vector((0,0,-1)))
    assert hit
    roof_heights.append((o.matrix_world@p).z)
roof_z=max(roof_heights)
assert max(abs(z-18) for z in roof_heights)<.002,roof_heights
for g in gold:g.location+=staged
for ob in meshes:ob.hide_render=not (ob.name.startswith('JUNCTION |') or 'Station6' in ob.name)
world=bpy.data.worlds.new('Open air')
world.use_nodes=True
sky=world.node_tree.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA'
sky.sun_elevation=.47;sky.sun_rotation=2.4;sky.sun_size=.024;sky.sun_intensity=.73
world.node_tree.links.new(sky.outputs[0],world.node_tree.nodes['Background'].inputs[0])
world.node_tree.nodes['Background'].inputs[1].default_value=.16
s.world=world
area('Sky bounce',(-204,99,23),(-206,104,19),420,(.72,.82,1),6)
shot('nov23-gold-find-roof',(-193.8,107,19.75),(-204.4,102.65,18.9),(1340,900),lens=27)
lo=world_to_camera_view(s,cam,staged)
hi=world_to_camera_view(s,cam,staged+Vector((0,0,1)))
assert .25<lo.x<.75 and .1<lo.y<.8 and hi.y>lo.y+.04
(out/'validation.json').write_text(json.dumps({
    'bytes':len(raw),'unique_triangles':tri,'unique_meshes':len(doc['meshes']),
    'bounds_blender_m':[mins,maxs], 'roof_m':roof_z,
    'archived_blocking_meshes':blocked,'staged_overlaps':overlaps(staged),
    'staged_bottom_blender_m':list(staged),'clearance_m':staged.z+mins[2]-roof_z,
    'center_screen_height_px':round((hi.y-lo.y)*900,1),'native_pickup':False,
},indent=2)+'\n')
