"""Compare exact stock horse feet samples at the R02 near-side saddle rail."""
import bpy
from pathlib import Path
import json
from math import pi
from mathutils import Matrix, Vector

def review(out):
    out=Path(out)
    S=bpy.context.scene
    runs={r["id"]:r["frames"] for r in json.loads((out/"replays.json").read_text())}
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/"w10b-riding-rail-apron.glb"))
    fitted=[o for o in set(S.objects)-before if o.type=="MESH"]
    assert len(fitted)==1
    trans=Matrix.Translation((-125,148,.025))@Matrix.Rotation(pi/2,4,"Z")
    for o in fitted:o.matrix_world=trans@o.matrix_world
    dots={}
    for key,col in (("auto",(.048,.8,.52)),("under",(.95,.45,.09))):
        mat=bpy.data.materials.new("Reviewed horse feet · "+key)
        mat.use_nodes=True
        n=mat.node_tree.nodes["Principled BSDF"]
        n.inputs["Base Color"].default_value=(*col,1)
        n.inputs["Emission Color"].default_value=(*col,1)
        n.inputs["Emission Strength"].default_value=.38
        dots[key]=[]
        for k in runs[key][::4]:
            if not -131.9<=k["x"]<=-117.3:continue
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.064,location=(k["x"],-k["z"],k["y"]+.064))
            o=bpy.context.object
            o.data.materials.append(mat)
            dots[key].append(o)
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    S.camera=cam
    S.cycles.samples=26
    S.cycles.seed=27
    S.cycles.use_animated_seed=False
    def shot(name,eye,target,lens,width,height):
        cam.location=eye
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
        cam.data.lens=lens
        cam.data.clip_end=950
        S.render.resolution_x,S.render.resolution_y=width,height
        S.render.filepath=str(out/(name+".jpg"))
        bpy.ops.render.render(write_still=True)
    for key in ("under","auto"):
        for o in fitted:o.hide_render=key=="under"
        for st,parts in dots.items():
            for o in parts:o.hide_render=st!=key
        shot("nov25-w10b-rail-"+key,(-121.3,138.8,3.5),(-125,148,1),40,1020,770)
    shot("nov25-w10b-apron-detail",(-121.75,144.5,2.04),(-125.0,148,0.83),46,1240,900)
