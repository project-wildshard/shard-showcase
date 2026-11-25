"""Rebuild the exact Sword recolors and render matched inventory frames."""
import itertools
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
from sword_finish_materials import build

out=output_directory()
paths, proof=build(out)
clear_scene()
s=bpy.context.scene

def link(name,d):
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);return o

def aim(o,p,q):
    o.location=p;o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()

parts={}
for label,path in paths.items():
    prior=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    ob,=[o for o in set(s.objects)-prior if o.type=='MESH']
    assert len(ob.data.materials)==7
    ob.rotation_mode='XYZ'
    ob.rotation_euler=(0,-.24,.29)
    parts[label]=ob
bpy.context.view_layer.update()
base=[parts['base'].matrix_world@v.co for v in parts['base'].data.vertices]
for o in parts.values():
    assert [o.matrix_world@v.co for v in o.data.vertices]==base

cam=link('Matched inventory lens',bpy.data.cameras.new('Matched inventory lens'))
cam.data.type='ORTHO';s.camera=cam
aim(cam,(.022,-6.5,.40),(-.035,0,.373))

def area(n,p,q,e,sz,color):
    d=bpy.data.lights.new(n,'AREA');d.energy=e;d.shape='DISK';d.size=sz;d.color=color
    aim(link(n,d),p,q)
area('Neutral key',(-1.48,-2.07,2.15),(0,0,.47),164,2.5,(1,.94,.88))
area('Neutral bounce',(.94,-1.77,.76),(0,0,.43),87,1.71,(.91,.95,1))
area('Narrow white edge',(1.27,.08,1.63),(0,0,.42),37,1.05,(1,1,1))
area('Wrap fill',(-.75,-.98,-.27),(0,0,.07),28,1.27,(1,.95,.91))
s.world=bpy.data.worlds.new('Slate ambience')
s.world.color=(.11,.115,.13)
s.render.engine='CYCLES';s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.065
s.render.film_transparent=True
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.view_settings.exposure=-.45
s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
masks={}
for key,ob in parts.items():
    for o in parts.values():o.hide_render=o!=ob
    for w,h,zoom,samples,tag in [(440,640,1.42,28,'large'),(64,64,1.38,42,'64')]:
        s.render.resolution_x=w;s.render.resolution_y=h
        cam.data.ortho_scale=zoom
        s.cycles.samples=samples
        dest=out/f'{key}-{tag}.png'
        s.render.filepath=str(dest)
        bpy.ops.render.render(write_still=True)
        if tag=='64':
            pic=bpy.data.images.load(str(dest),check_existing=False)
            masks[key]={i for i,a in enumerate(pic.pixels[:][3::4]) if a>=.5}
            bpy.data.images.remove(pic)
pairs={a+'/'+b:len(ma&mb)/len(ma|mb) for (a,ma),(b,mb) in itertools.combinations(masks.items(),2)}
assert min(pairs.values())>=.99 and all(200<len(m)<900 for m in masks.values()),pairs
proof['BlenderReimport']=True
proof['mask64']={'occupancy':{n:len(m) for n,m in masks.items()},'sameSilhouetteIou':pairs}
(out/'validation.json').write_text(json.dumps(proof,indent=2)+'\n')
