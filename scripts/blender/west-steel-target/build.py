"""W3c game prop. A stock scene clip, not a weapon, hit handler or real-world fixture."""
from pathlib import Path
import json
import math
import os
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'showcase-studies'))
from common import clear_scene,output_directory

out=output_directory()
clear_scene()
s=bpy.context.scene

def mat(name,rgb,metal=0,rough=.5,emission=0):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*rgb,1)
    p.inputs['Emission Strength'].default_value=emission
    return m

slate=mat('Blue graphite frame',(.061,.094,.124),.58,.44)
ochre=mat('Baked orange enamel',(.64,.19,.041),.43,.42)
red=mat('Muted oxide backing',(.29,.078,.044),.61,.48)
zinc=mat('Machined lips',(.395,.429,.449),.78,.28)
dark=mat('Patinated blue-grey face',(.122,.183,.207),.72,.37)
cream=mat('Reflective cream split chevron',(.90,.74,.38),.11,.39)
lit=mat('Mint hit pulse',(.029,.83,.52),.04,.27,2.2)
rubber=mat('Graphite floor pads',(.022,.027,.033),.05,.75)

def box(name,loc,dims,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        bev=o.modifiers.new('Broken edge','BEVEL');bev.width=b;bev.segments=1
        bpy.ops.object.modifier_apply(modifier=bev.name)
    o.data.materials.append(m)
    return o

def prism(name,profile,y,depth,m,b=.015):
    vs=[(x,sy,z) for sy in (y-depth/2,y+depth/2) for x,z in profile]
    n=len(profile)
    fs=[list(range(n)),list(range(2*n-1,n-1,-1))]
    fs += [(i+n,(i+1)%n+n,(i+1)%n,i) for i in range(n)]
    mesh=bpy.data.meshes.new(name)
    # profile is CCW in XZ; the near cap normal is -Y.
    mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    if b:
        bev=o.modifiers.new('Silhouette chamfer','BEVEL');bev.width=b;bev.segments=1
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bev.name)
    mesh.materials.append(m)
    return o

def pin(name,loc,r,m,along):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=.12,location=loc)
    o=bpy.context.object;o.name=name
    o.rotation_euler=Vector(along).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(m)
    return o

bx=.96
pivot_z=2.24
for x in (-bx,bx):
    box('Anchor shoe',(x,0,.115),(.47,.9,.23),slate,.042)
    for y in (-.23,.24):
        box('Damped runner',(x,y,.045),(.39,.24,.09),rubber,.024)
    box('Raked visual pylon',(x,0,1.10),(.28,.32,1.94),slate,.035)
    box('Enamel tall panel',(x,-.181,1.14),(.19,.072,1.27),ochre,.021)
    box('Bushed shoulder',(x,0,2.18),(.41,.46,.44),red,.044)
    pin('Bright pivot cap',(x,-.256,2.24),.118,zinc,(0,1,0))
    for z in (.35,.57,1.77):
        pin('Cast pylon plug',(x,-.202,z),.038,zinc,(0,1,0))
box('Bridge casting',(0,.015,2.38),(1.96,.29,.18),slate,.034)
box('Enamel bridge lintel',(0,-.163,2.40),(1.48,.082,.10),ochre,.018)
for x in (-.50,.50):
    box('Pivot cradle',(x,0,2.267),(.20,.37,.20),zinc,.022)

pivot=bpy.data.objects.new('Target_Swing_Pivot',None);bpy.context.collection.objects.link(pivot)
pivot.location=(0,0,pivot_z)
def attach(o):
    o.parent=pivot
    o.location.z-=pivot_z
    return o
for x in (-.43,.43):
    attach(box('Suspended yoke',(x,0,1.98),(.137,.135,.48),slate,.017))
    attach(pin('Yoke face pin',(x,-.061,1.93),.072,zinc,(0,1,0)))

outline=[(-.46,.78),(.46,.78),(.72,1.02),(.72,1.55),(.46,1.86),(-.46,1.86),(-.72,1.55),(-.72,1.02)]
attach(prism('Perimeter strike plate',outline,0,.149,zinc,.029))
profile=[(x*.929,1.32+(z-1.32)*.922) for x,z in outline]
attach(prism('Cold blue strike face',profile,-.082,.038,dark,.016))
attach(prism('Rear patina',[(x*.88,1.32+(z-1.32)*.85) for x,z in outline],.071,.035,red,.016))
# Two separate offset shapes read as one graphic on a small screen.
for ix in (-1,1):
    points=[(.09,1.25),(.46,1.52),(.56,1.40),(.10,1.07)]
    points=[(ix*x,z) for x,z in points]
    # CCW is required for the near face.
    if sum(points[i][0]*points[(i+1)%4][1]-points[(i+1)%4][0]*points[i][1] for i in range(4))<0:
        points.reverse()
    attach(prism('Painted split-chevron',points,-.106,.010,cream,.003))

pulse=attach(box('Mint pulse strip',(0,-.121,.966),(.76,.020,.11),lit,.009))
s.frame_start=0;s.frame_end=84;s.render.fps=60
for f,a in [(0,0),(5,17),(11,30),(20,18),(32,-12),(45,7),(59,-3),(71,1.3),(84,0)]:
    pivot.rotation_euler.x=math.radians(a)
    pivot.keyframe_insert('rotation_euler',frame=f,group='Impact swing')
pulse_keys=[(0,.001),(2,1),(12,1),(24,.5),(38,.001),(84,.001)]
for f,t in pulse_keys:
    pulse.scale=(t,1,t)
    pulse.keyframe_insert('scale',frame=f,group='Mint cue')
for obj in (pivot,pulse):
    for fc in obj.animation_data.action.fcurves:
        for p in fc.keyframe_points:p.interpolation='LINEAR'
s.frame_set(0)
dst=out/'w3c-swing-steel-target.glb'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='SCENE',export_texcoords=False,export_frame_range=True)
raw=dst.read_bytes()
length=struct.unpack_from('<I',raw,12)[0]
g=json.loads(raw[20:20+length])
clip={'name':'W3C_TargetImpact_1p4s','samplers':[],'channels':[]}
for action in g['animations']:
    start=len(clip['samplers'])
    clip['samplers'].extend(action['samplers'])
    clip['channels'].extend({**ch,'sampler':ch['sampler']+start} for ch in action['channels'])
assert len({(c['target']['node'],c['target']['path']) for c in clip['channels']})==len(clip['channels'])
g['animations']=[clip]
tail=raw[20+length:]
bin_length,bin_type=struct.unpack_from('<I4s',tail)
assert bin_type==b'BIN\0' and len(tail)==bin_length+8
payload=bytearray(tail[8:])
node=next(i for i,n in enumerate(g['nodes']) if n['name']=='Mint pulse strip')
if not any(c['target']=={'node':node,'path':'scale'} for c in clip['channels']):
    # Blender's scene exporter can omit scale-only actions on a pivot child.
    # Reattach the exact source curve in standard glTF accessor format.
    def accessor(values,size,kind):
        data=struct.pack('<'+'f'*len(values),*values)
        view=len(g['bufferViews'])
        g['bufferViews'].append({'buffer':0,'byteOffset':len(payload),'byteLength':len(data)})
        payload.extend(data)
        row={'bufferView':view,'componentType':5126,'count':len(values)//size,'type':kind}
        if size==1:row.update(min=[min(values)],max=[max(values)])
        i=len(g['accessors']);g['accessors'].append(row)
        return i
    sampler=len(clip['samplers'])
    clip['samplers'].append({'input':accessor([f/60 for f,_ in pulse_keys],1,'SCALAR'),
        'output':accessor([c for _,t in pulse_keys for c in (t,t,1)],3,'VEC3'),'interpolation':'LINEAR'})
    clip['channels'].append({'sampler':sampler,'target':{'node':node,'path':'scale'}})
g['buffers'][0]['byteLength']=len(payload)
clean=json.dumps(g,separators=(',',':')).encode()
clean+=b' ' * (-len(clean)%4)
tail=struct.pack('<I4s',len(payload),b'BIN\0')+payload
dst.write_bytes(struct.pack('<4sIII4s',b'glTF',2,20+len(clean)+len(tail),len(clean),b'JSON')+clean+tail)

if os.environ.get('W3C_ASSET_ONLY')=='1':
    raise SystemExit(0)

# Standalone art-stage; the intentional distances below are review cameras only.
sand=mat('Compacted slate gravel',(.122,.141,.151),.01,.86)
path=mat('Coarse warm edge',(.195,.174,.136),.03,.83)
floor=box('Review stage',(0,0,-.2),(24,200,.4),sand,.03)
for side in (-1,1):
    box('Review walkway edge',(side*1.90,-38,.02),(.17,82,.06),path,.02)
    for i in range(8):
        box('Pace inset',(side*1.62,-6-i*8,.016),(.095,.56,.026),ochre,.01)
for x in (-9,-6.8,6.8,9):
    box('Far field walls',(x,7,1.4),(2.4,3.4,2.8),slate,.11)
box('Recessed backdrop',(0,8,1.54),(12,1.1,3.08),sand,.13)

def light(name,xyz,target,power,size,col):
    bpy.ops.object.light_add(type='AREA',location=xyz)
    o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col

light('Cool key',(-3,-4,7),(0,0,1),850,5,(.77,.88,1))
light('Honey edge',(3,2,4),(0,0,1),980,4,(1,.66,.37))
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object;sun.rotation_euler=(math.radians(32),math.radians(-23),math.radians(26));sun.data.energy=2.1;sun.data.angle=.10
s.world.color=(.19,.21,.25)
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.065
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add();s.camera=bpy.context.object
def photo(name,loc,aim,size,angle,frame):
    s.frame_set(frame)
    c=s.camera;c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler()
    c.data.sensor_fit='VERTICAL';c.data.angle_y=math.radians(angle)
    s.render.resolution_x,s.render.resolution_y=size
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)

photo('w3c-target-detail',(-3.35,-5.15,2.85),(0,0,1.22),(1040,880),34,0)
for distance in (25,50,75):
    for frame in (0,11):
        photo(f'w3c-target-{distance}m-{frame}',(0,-distance,1.70),(0,0,1.35),(402,874),55,frame)
