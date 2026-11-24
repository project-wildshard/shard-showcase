"""E11c visual dock shutter and indicator, reimported in exact C1 D1/D2."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

out=output_directory()
repo=Path(__file__).resolve().parents[3]
c1=repo/"public/assets/wildshard-art/wsc-scene-007-c1-loading-yard.glb"
layout=json.loads((repo/"project/layouts/wsc-scene-007-c1-loading.json").read_text())
world_x,_,world_z=layout["origin_world_x_y_z"]
scene=bpy.context.scene
clear_scene()


def mat(name,color,metal=.45,rough=.52,emit=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    n=m.node_tree.nodes["Principled BSDF"]
    for k,v in {"Base Color":(*color,1),"Metallic":metal,"Roughness":rough,
                "Emission Color":(*color,1),"Emission Strength":emit}.items():
        n.inputs[k].default_value=v
    return m


slate=mat("Pressed slate steel",(.065,.106,.119))
rib=mat("Warm grey rib",(.128,.163,.174))
rust=mat("Oxide bumper",(.44,.142,.036))
bronze=mat("Warm enamel bars",(.58,.302,.046))
ink=mat("Graphite shield",(.022,.042,.044),.18)
glass=mat("Blue indicator glass",(.027,.44,.52),.13,.36,.25)


def box(name,pos,dim,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new("Silhouette bevel","BEVEL");m.width=bevel;m.segments=1
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def fastener(x,y,z):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.045,depth=.033,location=(x,y,z),
                                      rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name="Enamel dock screw";o.data.materials.append(bronze)
    return o


def asset(name,make):
    objs=make()
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=o.data.name=name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    f=out/(name+".glb")
    bpy.ops.export_scene.gltf(filepath=str(f),export_format="GLB",use_selection=True,
                             export_animations=False,export_texcoords=False)
    b=f.read_bytes()
    assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    d=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    assert len(b)<65536 and "images" not in d
    n=sum(d["accessors"][x["indices"]]["count"]//3 for m in d["meshes"] for x in m["primitives"])
    clear_scene()
    return f,{"bytes":len(b),"triangles":n,"sha256":hashlib.sha256(b).hexdigest()}


def shutter():
    # One universal cosmetic leaf. Reuse twice rather than duplicate.
    objs=[box("Press steel plate",(0,0,1.872),(2.41,.19,3.70),slate,.022)]
    for z in (.24,.82,1.39,1.96,2.53,3.10,3.55):
        objs.append(box("Stamp reinforcement",(0,-.096,z),(2.38,.13,.15),rib,.015))
    for x in (-1.06,1.06):
        objs.append(box("Orange leading strip",(x,-.145,1.87),(.135,.065,3.56),rust,.014))
        for z in (.38,3.34):objs.append(fastener(x,-.180,z))
    objs.append(box("Bottom bumper",(0,-.109,.13),(2.36,.15,.18),ink,.022))
    for x in (-.85,-.46,-.07,.32,.71):
        ob=box("Enamel warning slash",(x,-.190,1.80),(.14,.012,.38),bronze)
        ob.rotation_euler.y=-.39
        objs.append(ob)
    return objs


def relay():
    objs=[
       box("Low-profile relay strip",(0,0,0),(1.82,.102,.228),ink,.016),
       box("Center glass insert",(0,-.052,0),(1.47,.044,.112),glass,.018),
    ]
    for x in (-.58,-.29,0,.29,.58):
        objs.append(box("Black septum",(x,-.077,0),(.044,.014,.124),slate))
    for x in (-.827,.827):
        objs.append(fastener(x,-.054,0))
    return objs


leaf=asset("e11c-c1-dock-shutter-leaf",shutter)
light=asset("e11c-c1-dock-relay-strip",relay)


def load(path,loc=(0,0,0),yaw=0):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    oo=[o for o in scene.objects if o not in prior]
    for o in oo:
        if o.parent not in oo:
            o.location+=Vector(loc)
            if yaw:
                q=o.rotation_euler.to_quaternion() if o.rotation_mode!="QUATERNION" else o.rotation_quaternion
                o.rotation_mode="QUATERNION";o.rotation_quaternion=Quaternion((0,0,1),yaw)@q
    bpy.context.view_layer.update()
    return oo


def bvh(objects):
    verts=[];tris=[]
    for o in objects:
        if o.type!="MESH":continue
        start=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
        o.data.calc_loop_triangles()
        tris.extend(tuple(start+i for i in tri.vertices) for tri in o.data.loop_triangles)
    return BVHTree.FromPolygons(verts,tris,all_triangles=True)


donor=load(c1)
host=bvh(donor)
states={}
groups={}
for name in ("D1","D2"):
    sign=1 if name=="D1" else -1
    x,z=layout["door_x_z"][name]
    x,z=x-world_x,world_z-z
    # Leaves are within the closet and away from the original jamb and wall.
    yaw=sign*math.pi/2
    open_objs=[];closed_objs=[]
    for side in (-1,1):
        open_objs+=load(leaf[0],(x-sign*.98,z+side*3.71,0),yaw)
        closed_objs+=load(leaf[0],(x-sign*.98,z+side*1.207,0),yaw)
    relay_objs=load(light[0],(x+sign*.916,z,4.21),yaw)
    for objs in (open_objs,closed_objs):
        assert len(host.overlap(bvh(objs)))==0,(name,len(host.overlap(bvh(objs))))
    # The two poses differ intentionally. Check the same aperture lines
    # from the court side across the model plane and existing jamb only.
    test=[]
    for off in (-2.22,-1.22,-.12,.12,1.22,2.22):
        for h in (.28,1.05,1.85,2.65,3.48):
            o=Vector((x+sign*1.44,z+off,h));k=Vector((-sign,0,0))
            test.append((o,k))
    open_tree=bvh(open_objs)
    closed_tree=bvh(closed_objs)
    assert all(open_tree.ray_cast(o,k,3.1)[0] is None and host.ray_cast(o,k,3.1)[0] is None for o,k in test)
    assert all(closed_tree.ray_cast(o,k,3.1)[0] is not None for o,k in test)
    groups[name]=(open_objs,closed_objs,relay_objs)
    states[name]={"opening_rays_in_open_pose":len(test),"occluded_rays_in_closed_pose":len(test),
                  "leaf_donor_mesh_overlaps":0,"world_center_xz":layout["door_x_z"][name]}
(out/"e11c-c1-dock-shutters.json").write_text(json.dumps({
    "scope":"Static E11c pose study, not authored wave/spawn/seal logic, collider or runtime path test",
    "c1_sha256":hashlib.sha256(c1.read_bytes()).hexdigest(),"door_checks":states,
    "leaf":{"closed_local_half_offset_m":1.207,"open_local_half_offset_m":3.71,**leaf[1]},
    "relay":light[1],
},indent=2)+"\n")

if os.getenv("WILDSHARD_VALIDATE_ONLY")!="1":
    scene.world=bpy.data.worlds.new("Dusty Loading Yard")
    scene.world.color=(.19,.25,.28)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    x,z=layout["door_x_z"]["D1"];x,z=x-world_x,world_z-z
    for n,p,t,power,size,col in [
        ("Warm yard lantern",(x+4,z-4,7),(x,z,1.9),1800,5.5,(1,.81,.62)),
        ("Cold sky fill",(x+6,z+3,6),(x,z,2),1480,5.0,(.57,.79,1)),
        ("Recessed room spill",(x-3,z,3.35),(x,z,1.1),150,2.0,(1,.66,.32)),
    ]:
        d=bpy.data.lights.new(n,"AREA");o=bpy.data.objects.new(n,d)
        d.energy,d.size,d.color=power,size,col;scene.collection.objects.link(o);o.location=p;aim(o,t)
    d=bpy.data.cameras.new("Matched dock poses")
    cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
    cam.location=(x+10.2,z-4.2,4.95);aim(cam,(x-.25,z,1.98));d.type="ORTHO";d.ortho_scale=8.65
    scene.render.engine="CYCLES";scene.cycles.samples=40;scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.render.resolution_x=1420;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=90
    for state in ("open","closed"):
        for a,b,_ in groups.values():
            for o in a:o.hide_render=state!="open"
            for o in b:o.hide_render=state!="closed"
        scene.render.filepath=str(out/f"nov24-e11c-dock-{state}.jpg")
        bpy.ops.render.render(write_still=True)
