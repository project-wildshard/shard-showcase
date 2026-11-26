"""Render two proof views of the unchanged W08 tank and the installed example."""
import hashlib
import json

motion=json.loads(open(args[1]).read())
assert motion['saddleSha']==hashlib.sha256((out/'saddle.json').read_bytes()).hexdigest()
def xyz(p):return Vector((p[0],-p[2],p[1]))
def import_at(file,pos):
    before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(out/file))
    for o in set(S.objects)-before:o.matrix_world=Matrix.Translation(pos)@o.matrix_world
import_at('w7a-pole-one-perch.glb',(-151,46.62,0))
import_at('w7a-pole-two-tower.glb',(-172,70.2,0))
def ribbon(name,points,rgb):
    m=mat('Readback | '+name,rgb,0,.5)
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Emission Color'].default_value=(*rgb,1);n.inputs['Emission Strength'].default_value=2
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=.077;d.bevel_resolution=2
    s=d.splines.new('POLY');s.points.add(len(points)-1)
    for q,v in zip(s.points,points):q.co=(*v,1)
    o=bpy.data.objects.new(name,d);S.collection.objects.link(o);d.materials.append(m)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.265,location=points[-1])
    bpy.context.object.data.materials.append(m)
for i,(r,rgb) in enumerate(zip(motion['centre'],[(.09,.74,1),(1,.51,.065),(.22,1,.38)]),1):
    pts=[r['start']]+[f[1] for f in r['frames'][::3]]+[r['end']]
    ribbon(f'Proof only | hop {i}',[xyz(p)+Vector((0,0,.22)) for p in pts],rgb)
world=bpy.data.worlds.new('West exterior daylight');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.29,.42,.62,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.39;S.world=world
l=bpy.data.lights.new('Sun break','SUN');l.energy=2.45;l.angle=.13
light=bpy.data.objects.new('Sun break',l);S.collection.objects.link(light);light.rotation_euler=(.67,-.52,-.66)
cam=bpy.data.cameras.new('Evidence camera')
o=bpy.data.objects.new('Evidence camera',cam);S.collection.objects.link(o);S.camera=o;cam.clip_end=500
S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=89
for name,pos,pivot,lens,w,h in (
  ('approach',(-155,99,31),(-182,82,12),38,1360,920),
  ('landing',(-184.4,91.5,25.6),(-194.5,92.5,19.65),38,1140,920),
):
    o.location=pos;o.rotation_euler=(Vector(pivot)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;S.render.resolution_x=w;S.render.resolution_y=h
    S.render.filepath=str(out/f'nov26-w7a-tank-{name}.webp')
    bpy.ops.render.render(write_still=True)
