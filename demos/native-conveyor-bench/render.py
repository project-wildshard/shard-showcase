"""Reimport the unchanged WSC-PROP-037 and plot the two independent bench trials."""
import bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector

args=sys.argv[sys.argv.index("--")+1:]
trace=json.loads(Path(args[0]).read_text())
out=Path(args[1])
repo=Path(__file__).resolve().parents[2]
assets=repo/"public/assets/wildshard-art"
belt=assets/"wsc-prop-037-conveyor-module.glb"
arrow=assets/"wsc-prop-037-conveyor-direction.glb"
assert hashlib.sha256(belt.read_bytes()).hexdigest()=="1d0d5e0ac6fb0fd201daef538ed3e277824a2a0f6b9677968fe2f8dbb18debdb"
transforms=json.loads((repo/"project/layouts/w6b-conveyor-direction-proof.json").read_text())["course_poses"]
assert [p[0] for p in transforms]==[t["belt"]["x"] for t in trace["trials"]]
scene=bpy.context.scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
def load(path,pose):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    roots=[o for o in set(scene.objects)-before if o.parent is None]
    assert roots
    transform=Matrix.Translation((pose[0]+90,pose[1]-103,pose[2]))@Matrix.Rotation(pose[3],4,"Z")
    for o in roots:o.matrix_world=transform@o.matrix_world
for pose in transforms:
    for asset in (belt,arrow):load(asset,pose)

def mat(n,c,rough=.5,metal=0,emit=0):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Emission Color"].default_value=(*c,1)
    p.inputs["Emission Strength"].default_value=emit
    return m
road=mat("Old roadway",(.143,.122,.099),.83)
slab=mat("Cast dark concrete",(.25,.24,.21),.79)
oxide=mat("Warm engineering enamel",(.68,.316,.04),.51,.22)
mint=mat("Player sample mint",(.095,.61,.56),.32,.14,.36)
navy=mat("Contour framing",(.027,.085,.094),.53,.5)
peach=mat("Cargo sample ochre",(.78,.33,.058),.43,.08,.18)
def box(name,loc,d,m,bevel=.026):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new("Soft corners","BEVEL")
        b.width=min(bevel,min(d)*.35);b.segments=2
        o.modifiers.new("Weighted normal","WEIGHTED_NORMAL")
    return o
box("Studio ground", (0,0,-.19),(100,100,.36),road,0)
box("Station 1 base, archived dimensions",(0,0,.045),(20,5,.09),slab,.02)
for x in (-6,0,6):
    for y in (-1.25,1.25):
        end=box("Non-exported review floor paint",(x,y,.091),(4.76,.035,.003),oxide,0)
def point(p):return (p[0]+90,-p[2]-103,p[1])
def ball(p,r,m,geo="ICO"):
    if geo=="ICO":bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=p)
    else:bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=r,location=p)
    o=bpy.context.object;o.data.materials.append(m)
    for f in o.data.polygons:f.use_smooth=True
    return o
def player(p):
    x,y,z=point(p)
    # Proxy for the actual radius .38 and stock approx 1.8 m total height.
    o=ball((x,y,z+.916),.38,mint,"UV")
    o.scale.z=2.34
    out_parts=[o]
    for zz in (z+.54,z+.98,z+1.33):
        bpy.ops.mesh.primitive_torus_add(major_radius=.284,minor_radius=.022,major_segments=24,minor_segments=6,location=(x,y,zz))
        ob=bpy.context.object;ob.data.materials.append(navy);out_parts.append(ob)
    return out_parts
def crate(p):
    x,y,z=point(p)
    return [box("Dynamic crate visual proxy",(x,y,z),(.488,.488,.488),peach,.026)]+[
        box("Proxy strap",(x+i,y,z),(.038,.503,.495),navy,.008) for i in (-.16,.16)]
def group(which,m,make):
    objects=[]
    for t in trace["trials"]:
        f=t[which]
        for i in (2,6,10,14,18):
            p=point(f[i]["pos"])
            px,py,pz=p
            objects.append(ball((px,py,pz+(.059 if which=="player" else -.158)),.045 if i<18 else .061,m))
        objects+=make(f[20]["pos"])
    return objects
walk=group("player",mint,player)
cargo=group("cargo",peach,crate)

def illuminate(kind,loc,to,power,size,color):
    bpy.ops.object.light_add(type=kind,location=loc)
    o=bpy.context.object;o.data.energy=power
    o.data.color=color
    o.rotation_euler=(Vector(to)-o.location).to_track_quat('-Z','Y').to_euler()
    if kind=="SUN":o.data.angle=size
    else:o.data.shape="DISK";o.data.size=size
illuminate("SUN",(-8,-4,14),(1,0,0),2.7,.13,(1,.87,.74))
illuminate("AREA",(3,4,10),(0,0,1),1800,9,(.55,.78,1))
scene.world=bpy.data.worlds.new("West movers review")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.31,.43,.54,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.55
scene.render.engine="CYCLES"
scene.cycles.samples=30
scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.044
scene.render.resolution_percentage=100
scene.render.resolution_x=1330
scene.render.resolution_y=800
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=92
scene.view_settings.view_transform="AgX"
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
def photo(name,show,hide,eye,to,lens):
    for o in show:o.hide_render=False
    for o in hide:o.hide_render=True
    cam.location=eye;cam.rotation_euler=(Vector(to)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)
photo("nov25-w6b-belt-foot",walk,cargo,(7,-14,9),(.6,0,.25),33)
photo("nov25-w6b-belt-crate",cargo,walk,(3,-11,12),(.35,0,.0),33)
