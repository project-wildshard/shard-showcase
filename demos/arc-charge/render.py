"""Review exactly the exported Three vertex snapshots. No compositor glow."""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector

V=Vector
receipt=Path(sys.argv[-1]).resolve()
data=json.loads(receipt.read_text())
out=receipt.parent
repo=Path(__file__).resolve().parents[2]
cover=repo/"public/assets/wildshard-art/e6-low-cover-return.glb"
assert hashlib.sha256(cover.read_bytes()).hexdigest()==data["context"]["cover"]["sha256"]
scene=bpy.context.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj,do_unlink=True)

def material(name,diffuse,metal=.1,rough=.6):
    m=bpy.data.materials.new(name);m.diffuse_color=(*diffuse,1)
    m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*diffuse,1)
    bs.inputs["Metallic"].default_value=metal;bs.inputs["Roughness"].default_value=rough
    return m

mat=[
    material("Ceramic insulation",(.27,.28,.225),.02,.51),
    material("Gunmetal",(.052,.078,.091),.47,.4),
    material("Copper seam",(.36,.145,.042),.47,.4),
    material("Slate ash",(.095,.102,.104),.05,.87),
]
def box(name,x,y,z,s,kind,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z))
    o=bpy.context.object;o.name=name;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=o.modifiers.new("Machined silhouette","BEVEL");m.width=bevel;m.segments=3
        o.modifiers.new("Planar normals","WEIGHTED_NORMAL")
    o.data.materials.append(mat[kind])
    return o

# Review proxy only: no model of an Arc Sentry or its held lance.
def mount(x,y,z):
    solids=[]
    solids.append(box("dark carrier channel",x,y+.060,z-.091,(1.02,.21,.128),1,.025))
    for n,d in enumerate([-1,1]):
        xx=x+d*.428
        solids.append(box("ceramic terminal",xx,y,z,(.137,.21,.221),0,.032))
        solids.append(box("copper shoe",xx-d*.028,y-.048,z,(.085,.20,.114),2,.019))
        solids.append(box("fatigue collar",xx+d*.098,y+.022,z-.069,(.124,.26,.151),1,.025))
    return solids

def geometry(frame,x,y,z):
    p,c=frame["positions"],frame["colors"]
    assert len(p)==len(c)==72*frame["segments"]
    verts=[(x+p[i],y-p[i+2],z+p[i+1]) for i in range(0,len(p),3)]
    faces=[(i,i+1,i+2) for i in range(0,len(verts),3)]
    mesh=bpy.data.meshes.new("Exact sampled VFX "+str(frame["t"]))
    mesh.from_pydata(verts,[],faces)
    attr=mesh.color_attributes.new(name="linear cue color",type="FLOAT_COLOR",domain="POINT")
    for i,k in enumerate(attr.data):
        k.color=(*c[3*i:3*i+3],1)
    m=bpy.data.materials.get("Camera-only cue")
    if m is None:
        m=bpy.data.materials.new("Camera-only cue");m.use_nodes=True
        nt=m.node_tree;nt.nodes.clear()
        a=nt.nodes.new("ShaderNodeVertexColor");a.layer_name="linear cue color"
        e=nt.nodes.new("ShaderNodeEmission");e.inputs["Strength"].default_value=1.85
        t=nt.nodes.new("ShaderNodeBsdfTransparent");p=nt.nodes.new("ShaderNodeLightPath")
        v=nt.nodes.new("ShaderNodeMixShader");o=nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(a.outputs["Color"],e.inputs["Color"])
        nt.links.new(p.outputs["Is Camera Ray"],v.inputs[0]);nt.links.new(t.outputs[0],v.inputs[1])
        nt.links.new(e.outputs[0],v.inputs[2]);nt.links.new(v.outputs[0],o.inputs["Surface"])
    mesh.materials.append(m)
    ob=bpy.data.objects.new("Exact sampled charge",mesh);scene.collection.objects.link(ob)
    return ob

scene.render.engine="CYCLES";scene.cycles.samples=30;scene.cycles.use_denoising=False
scene.world=bpy.data.worlds.new("Slate twilight");scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"];bg.inputs["Color"].default_value=(.25,.37,.58,1)
bg.inputs["Strength"].default_value=.24
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.image_settings.file_format="PNG";scene.render.resolution_percentage=100
def lamp(name,pos,power,size,tint,aim):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.shape="DISK";d.size=size;d.color=tint
    ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=pos
    ob.rotation_euler=(V(aim)-ob.location).to_track_quat("-Z","Y").to_euler()
    return ob
cam=bpy.data.cameras.new("Three-geometry evidence")
ob=bpy.data.objects.new("Review camera",cam);scene.collection.objects.link(ob);scene.camera=ob
def shot(name,size,pos,point,lens,orthographic=False):
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(out/f"{name}.png")
    ob.location=pos;ob.rotation_euler=(V(point)-ob.location).to_track_quat("-Z","Y").to_euler()
    cam.type="ORTHO" if orthographic else "PERSP"
    if orthographic:cam.ortho_scale=lens
    else:
        cam.sensor_fit="VERTICAL";cam.sensor_height=24
        cam.lens=lens
    bpy.ops.render.render(write_still=True)

set_a=[]
for i,frame in enumerate(data["frameData"]):
    x=(i-1)*1.27
    set_a.extend(mount(x,0,1.1))
    set_a.append(geometry(frame,x,0,1.1))
set_a.extend([box("display slab",0,.2,.90,(4.5,.62,.16),3,.032),box("backdrop",0,.9,.65,(16,.15,14),3)])
set_a.extend([lamp("warm key",(-3,-2,5),810,4,(1,.64,.42),(0,0,1)),
             lamp("cool fill",(2,-3,2),325,3,(.42,.63,1),(0,0,1))])
shot("timeline",(1320,610),(0,-6,1.53),(0,0,1.09),4.15,True)
for o in set_a:
    bpy.data.objects.remove(o,do_unlink=True)
# The existing stand-in cover uses its exact archived placement. The mount
# is a proposed viewing prop in front of it, not an authored sentry spawn.
bpy.ops.import_scene.gltf(filepath=str(cover))
x,map_z=data["context"]["cover"]["xz"]
yaw=data["context"]["cover"]["yaw"]
X,Y=x,-map_z
T=Matrix.Translation((X,Y,0)) @ Matrix.Rotation(yaw,4,"Z")
for node in list(scene.objects):
    if node is not ob and node.type not in ("LIGHT","CAMERA") and node.parent is None:
        node.matrix_world=T@node.matrix_world
a,b,z=X+.25,Y-1.81,1.73
box("review ash ground",X,Y,-.085,(34,45,.17),3)
box("proxy only pedestal",a,b+.23,.79,(.36,.39,1.58),1,.052)
mount(a,b,z)
active=geometry(data["frameData"][-1],a,b,z)
lamp("Band 6 dusk key",(X-4,Y-4,7),1400,6,(1,.66,.43),(a,b,1.0))
lamp("blue sky edge",(X+4,Y+3,4.2),1570,5,(.40,.58,1),(a,b,1.45))
shot("phone",(402,874),(a,b-10,z),(a,b,z),12/math.tan(math.radians(62)/2))
active.hide_render=True
shot("phone-off",(402,874),(a,b-10,z),(a,b,z),12/math.tan(math.radians(62)/2))
