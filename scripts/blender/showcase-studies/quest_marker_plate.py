"""Render 2x phone plate with marker anchors from evaluated head mesh."""
import hashlib
import json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import bpy

def capture(scene,out,root,eye,screen,cam):
    eye.location=(-.06,-6.70,1.70)
    eye.rotation_euler=(Vector((-.06,.10,1.30))-eye.location).to_track_quat("-Z","Y").to_euler()
    eye.data.lens=38
    eye.data.sensor_fit="HORIZONTAL"
    scene.frame_set(19)
    scene.render.resolution_x=804
    scene.render.resolution_y=1748
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.engine="CYCLES"
    scene.cycles.samples=22
    scene.cycles.use_denoising=False
    scene.cycles.adaptive_threshold=.075
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    rigs=[o for o in scene.objects if o.type=="ARMATURE"]
    assert len(rigs)==3,rigs
    positions={}
    for role,p,_ in screen:
        rig=min(rigs,key=lambda o:abs(o.matrix_world.translation.x-p[0]))
        assert abs(rig.matrix_world.translation.x-p[0])<.1
        body,=[o for o in rig.children if o.type=="MESH" and o.vertex_groups]
        mesh=body.evaluated_get(dg)
        vertices=[mesh.matrix_world@v.co for v in mesh.data.vertices]
        pts=[world_to_camera_view(scene,eye,v) for v in vertices]
        top=max(p.y for p in pts)
        crown=[p for p in pts if p.y>top-.011]
        x=(min(v.x for v in crown)+max(v.x for v in crown))/2
        positions[role]={"headX":round(x*402,3),"headY":round((1-top)*874,3),
                         "rigJoints":len(rig.data.bones),
                         "sourceSHA256":hashlib.sha256(next(root.glob(f"wsc-actor-*-{role}.glb")).read_bytes()).hexdigest()}
        assert 52<positions[role]["headX"]<350 and 105<positions[role]["headY"]<545,positions
    (out/"anchors.json").write_text(json.dumps(positions,indent=2)+"\n")
    scene.render.filepath=str(out/"marker-plate.png")
    bpy.ops.render.render(write_still=True)
