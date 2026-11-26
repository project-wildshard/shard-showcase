"""Render the fitted floor and original sectors with the actual recorded walk."""
import json
import bpy
from mathutils import Vector
p=json.loads(motion.read_text())
assert p['geometrySha']==receipt['meshSha']
def xyz(u):
    return Vector((u[0]-146,186-u[2],u[1]))
trail=bpy.data.materials.new('Bench only | walk path');trail.use_nodes=True
pr=trail.node_tree.nodes.get('Principled BSDF')
pr.inputs['Base Color'].default_value=(.05,.68,.94,1)
pr.inputs['Emission Color'].default_value=(.05,.68,.94,1);pr.inputs['Emission Strength'].default_value=1.7
points=[xyz(r['feet'])+Vector((0,0,.11)) for r in p['centre']['frames'] if r['leg']<=6]
c=bpy.data.curves.new('Recorded C3 outbound walk','CURVE');c.dimensions='3D';c.bevel_depth=.051;c.bevel_resolution=2
s=c.splines.new('POLY');s.points.add(len(points)-1)
for a,b in zip(s.points,points):a.co=(*b,1)
o=bpy.data.objects.new(c.name,c);S.collection.objects.link(o);c.materials.append(trail)
for q in (points[0],points[-1]):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.19,location=q)
    bpy.context.object.data.materials.append(trail)
w=bpy.data.worlds.new('Copper dust sky');w.use_nodes=True
b=w.node_tree.nodes['Background'];b.inputs[0].default_value=(.26,.39,.59,1)
b.inputs[1].default_value=.40;S.world=w
l=bpy.data.lights.new('Raking sun','SUN');l.color=(1,.91,.80);l.energy=2.52;l.angle=.13
o=bpy.data.objects.new('Raking sun',l);S.collection.objects.link(o);o.rotation_euler=(.58,-.45,-.57)
cam=bpy.data.cameras.new('C3 audit')
o=bpy.data.objects.new(cam.name,cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=300
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=89
for name,where,target,(w,h),focal in (
 ('join',(145.5,1.72,187.5),(176,4.3,156),(804,1748),44),
 ('plan',(100,69,155),(145,0,186),(1400,960),103),
):
    o.location=xyz(where);o.rotation_euler=(xyz(target)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.type='ORTHO' if name=='plan' else 'PERSP'
    if name=='plan':cam.ortho_scale=focal
    else:cam.lens=focal;cam.sensor_fit='VERTICAL'
    S.render.resolution_x,S.render.resolution_y=w,h
    S.render.filepath=str(O/f'nov26-c3-floor-{name}.webp')
    bpy.ops.render.render(write_still=True)
