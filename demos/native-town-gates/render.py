"""Render actual native traces plus the pinned archival plaza/street camera poses."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:]
receipt=json.loads(Path(args[0]).read_text())
out=Path(args[1]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene

def material(name,rgb):
    m=bpy.data.materials.new(name);m.use_nodes=True
    q=m.node_tree.nodes['Principled BSDF']
    q.inputs['Base Color'].default_value=(*rgb,1)
    q.inputs['Emission Color'].default_value=(*rgb,1)
    q.inputs['Emission Strength'].default_value=.45
    return m

def world(p):
    return Vector((p[0],-p[2],p[1]))

scene.render.engine='CYCLES';scene.cycles.samples=27;scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.06
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=91
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new('Gate route warm daylight');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value=(.44,.57,.71,1);bg.inputs[1].default_value=.60
bpy.ops.object.light_add(type='SUN',location=(-82,18,24))
sun=bpy.context.object
sun.rotation_euler=Vector((.57,-.38,-.76)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.7;sun.data.angle=.061;sun.data.color=(1,.88,.73)
bpy.ops.object.camera_add()
cam=bpy.context.object;scene.camera=cam

def render(name,eye,look,width,height,vfov=None):
    cam.location=eye;cam.rotation_euler=(look-eye).to_track_quat('-Z','Y').to_euler()
    if vfov:
        cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL'
        cam.data.lens=cam.data.sensor_height/(2*math.tan(math.radians(vfov)/2))
    else:
        cam.data.type='ORTHO';cam.data.ortho_scale=143
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)

# Exact Three.js camera vectors/FOV from the archived R5 gate() and street() shots.
render('plaza-05',world((-16,1.70,10)),world((-46,5,-20)),740,1000,80)
render('street-06',world((-104,1.70,1.5)),world((-40,4,0)),740,1000,66)

good=material('Completed center route',(.017,.82,.66))
short=material('Center route ends before exterior landing',(.98,.19,.035))
for r in receipt['samples']:
    if r['offset']!=0:
        continue
    pts=[world((r['route'][0][0],.12,r['route'][0][1]))]
    pts.extend(world(s['feet']) for s in r['frames'] if s['grounded'])
    if r['completed']:pts.append(world(r['last']))
    for p in pts:p.z+=.22
    tag=bpy.data.curves.new('Native path | '+r['name'],'CURVE');tag.dimensions='3D';tag.bevel_depth=.19
    curve=tag.splines.new('POLY');curve.points.add(len(pts)-1)
    for point,p in zip(curve.points,pts):point.co=(*p,1)
    o=bpy.data.objects.new(tag.name,tag);scene.collection.objects.link(o)
    m=good if r['completed'] else short
    tag.materials.append(m)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.79,location=pts[-1])
    bpy.context.object.data.materials.append(m)
    caption=bpy.data.curves.new(r['name']+' Gate map label','FONT')
    caption.body=r['name'].upper();caption.align_x='CENTER';caption.size=2.65
    caption.materials.append(m)
    label=bpy.data.objects.new(caption.name,caption);scene.collection.objects.link(label)
    side={'West':(-4.8,2.5),'East':(4.8,2.5),'Stable':(0,3),'Movers':(0,3),
          'Park':(0,-5),'Range':(0,-5)}[r['name']]
    label.location=pts[-1]+Vector((*side,1.7))
render('town-routes',Vector((-68,22,155)),Vector((-68,0,0)),1150,1080)
