"""Reimport and test the sky against the pinned Titan bowl and camera proof."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import struct

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

os.environ["WSC_STANDS_RAYS_ONLY"]="1"
base=runpy.run_path(str(Path(__file__).resolve().parent.parent/"showcase-studies/titan_stands_review.py"))
S,O,C,bvh,aim=[base[k] for k in ("S","O","C","bvh","aim")]
base["ground"].hide_render=True
base["sky"].inputs[1].default_value=0
S.cycles.samples=24
p=O/"e12h-titan-interior-sky.glb"
raw=p.read_bytes()
glb=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert len(glb["meshes"])==1 and len(glb["meshes"][0]["primitives"])==1
assert "KHR_materials_unlit" in glb["materials"][0]["extensions"]
assert "images" not in glb and "textures" not in glb
before=set(S.objects)
bpy.ops.import_scene.gltf(filepath=str(p))
bpy.context.view_layer.update()
(obj,)=set(S.objects)-before
assert obj.type=="MESH"
verts=[obj.matrix_world @ v.co for v in obj.data.vertices]
faces=[tuple(q.vertices) for q in obj.data.polygons]
shell=BVHTree.FromPolygons(verts,faces,all_triangles=True)
assert abs(max(v.z for v in verts)-70)<.0001
assert min(math.hypot(v.x,v.y) for v in verts if v.z < 31)>92
# Ensure the background doesn't introduce light, reflections or shadows
# in the comparison. These are Blender preview switches, not runtime props.
for flag in ("visible_shadow","visible_diffuse","visible_glossy","visible_transmission","visible_volume_scatter"):
    setattr(obj,flag,False)

shots={}
for name,pos,target,dims,fov in base["cameras"]:
    C.lens=24/(2*math.tan(math.radians(fov)/2))
    S.camera.location=pos
    aim(S.camera,target)
    S.render.resolution_x,S.render.resolution_y=dims
    bpy.context.view_layer.update()
    frame=C.view_frame(scene=S)
    x0,x1=min(q.x for q in frame),max(q.x for q in frame)
    y0,y1=min(q.y for q in frame),max(q.y for q in frame)
    z=frame[0].z
    rot=S.camera.matrix_world.to_quaternion()
    holes=filled=front=0
    min_gap=math.inf
    for j in range(100):
        for i in range(72):
            ray=(rot@Vector((x0+(x1-x0)*(i+.5)/72,y0+(y1-y0)*(j+.5)/100,z))).normalized()
            donor=bvh.ray_cast(S.camera.location,ray,350)[3]
            _,normal,_,sky=shell.ray_cast(S.camera.location,ray,350)
            if donor is None:
                holes+=1
                if sky is not None:
                    filled+=1
                    assert normal.dot(ray)<0
            elif sky is not None:
                min_gap=min(min_gap,sky-donor)
                front+=sky<donor
    assert filled==holes and front==0,(name,holes,filled,front)
    shots[name]={"rays":7200,"empty_on_bowl_alone":holes,"filled_by_sky":filled,"foreground_rays_replaced":front,
                "min_donor_to_sky_separation_m":round(min_gap,3) if math.isfinite(min_gap) else None}
    if os.environ.get("WSC_SKY_RENDER")=="1" and name in ("north-portrait","angled-portrait"):
        S.render.filepath=str(O/f"nov26-titan-interior-sky-{name}.jpg")
        bpy.ops.render.render(write_still=True)

(O/"e12h-titan-interior-sky-proof.json").write_text(json.dumps({
    "scope":"Optional unlit presentation shell. No actor, cutscene, collision, native placement, lighting or runtime sky changes.",
    "donor_sha256":base["PIN"],"shell_sha256":hashlib.sha256(raw).hexdigest(),"shell_bytes":len(raw),
    "triangles":len(faces),"primitives":1,"top_m":70,"shots":shots,
},indent=2)+"\n")
