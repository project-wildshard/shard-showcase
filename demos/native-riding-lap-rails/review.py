"""Matched flush and receiver renders at the previously tight rail."""
import json
from pathlib import Path
from math import pi
import bpy
from mathutils import Matrix, Vector

def review(out):
    out=Path(out)
    s=bpy.context.scene
    parts=Path(__file__).resolve().parents[2]/'public/assets/wildshard-art'
    replay=json.loads((out/'replays.json').read_text())
    cases={}
    def load(name,loc):
        before=set(s.objects)
        bpy.ops.import_scene.gltf(filepath=str(parts/name))
        bpy.context.view_layer.update()
        obs=sorted([o for o in set(s.objects)-before if o.type=='MESH'],key=lambda o:o.name)
        tr=Matrix.Translation(loc)@Matrix.Rotation(-pi/2,4,'Z')
        for o in obs:o.matrix_world=tr@o.matrix_world
        return obs
    def marker_mat(name,c):
        m=bpy.data.materials.new(name)
        m.use_nodes=True
        shader=m.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value=(*c,1)
        shader.inputs['Emission Color'].default_value=(*c,1)
        shader.inputs['Emission Strength'].default_value=.48
        return m
    for fit,shift,col in [('flush',0,(.95,.36,.05)),('receiver',.8,(.058,.7,.46))]:
        cases[fit]=load('w10b-riding-rail-apron.glb',(-160+shift,224,.025))
        if shift:
            cases[fit]+=load('w10b-riding-apron-stands.glb',(-160+shift,224,.025))
        pose=next(q for q in replay if q['fit']==fit)
        source=next(q for q in pose['samples'] if q['rail']==4)
        m=marker_mat('Measured horse feet · '+fit,col)
        for x,y,z in source['points']:
            if abs(x+160)>7.45:continue
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.073,location=(x,-z,y+.073))
            ob=bpy.context.object;ob.data.materials.append(m)
            cases[fit].append(ob)
    bpy.ops.object.camera_add(location=(-156.2,232,3.25));cam=bpy.context.object
    cam.rotation_euler=(Vector((-160.1,224,1.01))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=43;s.camera=cam
    s.cycles.samples=32;s.cycles.seed=28
    s.render.resolution_x=1280;s.render.resolution_y=900
    for fit,obs in cases.items():
        for key,parts in cases.items():
            for o in parts:o.hide_render=key!=fit
        s.render.filepath=str(out/('rail4-'+fit+'.jpg'))
        bpy.ops.render.render(write_still=True)
