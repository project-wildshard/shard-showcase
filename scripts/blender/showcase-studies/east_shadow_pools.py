"""E5b art readability study; a vertex-alpha decal, not a stealth rule or scene release."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory
out=output_directory()
asset_dir=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
clear_scene()
scene=bpy.context.scene
def import_glb(path):
    old=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
    return sorted(set(scene.objects)-old,key=lambda o:o.name)

# A compact local floor decal. The darkest edge hugs the source wall at y=0.
verts=[];alpha=[];faces=[]
xs=(-3.00,-2.72,-2.30,-1.93,-1.20,0,1.20,1.93,2.30,2.72,3.00)
ys=(0,.07,.17,.31,.53,.82,1.18,1.58,2.01,2.45,2.83,3.10)
for j,y in enumerate(ys):
    t=y/ys[-1]
    for i,x in enumerate(xs):
        width=1-.26*t
        xa=x*width+.38*t
        side=max(0,1-(abs(x)/3)**5)
        fall=(1-t)**.87
        ramp=0 if j==0 else min(1,y/.18)
        value=.83*side*fall*ramp
        verts.append((xa,y,.008));alpha.append(value)
        if i and j:
            n=len(xs);k=j*n+i
            faces.append((k-n-1,k-n,k,k-1))
mesh=bpy.data.meshes.new("Directional shadow | 6 x 3.1 m")
mesh.from_pydata(verts,[],faces);mesh.update()
shadow=bpy.data.objects.new("ShadowPool_WallFloor",mesh);bpy.context.collection.objects.link(shadow)
m=bpy.data.materials.new("Shadow pool | vertex alpha");m.use_nodes=True;m.surface_render_method='BLENDED'
p=m.node_tree.nodes.get("Principled BSDF");p.inputs["Roughness"].default_value=1.0
p.inputs["Specular IOR Level"].default_value=0
p.inputs["Metallic"].default_value=0
col=mesh.color_attributes.new(name="Shade",type='FLOAT_COLOR',domain='CORNER')
mesh.color_attributes.active_color=col
for i,loop in enumerate(mesh.loops): col.data[i].color=(.017,.044,.068,alpha[loop.vertex_index])
v=m.node_tree.nodes.new("ShaderNodeVertexColor");v.layer_name=col.name
m.node_tree.links.new(v.outputs["Color"],p.inputs["Base Color"])
m.node_tree.links.new(v.outputs["Alpha"],p.inputs["Alpha"])
mesh.materials.append(m)
path=out/"wsc-kit-006-shadow-pool-decal.glb"
export([shadow],path)
bpy.data.objects.remove(shadow,do_unlink=True)
shadow,=import_glb(path)
shadow.data.calc_loop_triangles()
assert len(shadow.data.loop_triangles)==220
alphas=[c.color[3] for c in shadow.data.color_attributes.active_color.data]
assert min(alphas)<1e-6 and .71<max(alphas)<.84

refs={
 "container":("WSC-PROP-058","wsc-prop-058-shipping-container.glb"),
 "cover":("WSC-PROP-066","wsc-prop-066-orange-cover-barrier.glb"),
 "fence":("WSC-MODULE-023","wsc-module-023-corrugated-yard-fence.glb"),
 "floodlight":("WSC-MODULE-024","wsc-module-024-floodlight-tower.glb"),
 "hut":("WSC-PROP-065","wsc-prop-065-keycard-shed.glb"),
}
models={}
report={}
for key,(aid,filename) in refs.items():
    f=asset_dir/filename
    ob=import_glb(f)
    models[key]=[(o.data,o.matrix_world.copy()) for o in ob if o.type=='MESH']
    points=[t@v.co for mesh,t in models[key] for v in mesh.vertices]
    for mesh,_ in models[key]:mesh.calc_loop_triangles()
    extent=[round(max(v[j] for v in points)-min(v[j] for v in points),3) for j in range(3)]
    report[key]=dict(id=aid,file=filename,dimensions_blender_m=extent,bytes=f.stat().st_size,
                     triangles=sum(len(mesh.loop_triangles) for mesh,t in models[key]),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
    for o in ob:bpy.data.objects.remove(o,do_unlink=True)

placement=[]
def use(key,n,p,yaw=0,scale=(1,1,1)):
    mat=Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Diagonal(Vector((*scale,1)))
    for mesh,local in models[key]:
        o=bpy.data.objects.new(n+" | "+mesh.name,mesh);bpy.context.collection.objects.link(o)
        o.matrix_world=mat@local
        o.visible_shadow=False # No physical shadows in this comparison rig.
    placement.append(dict(asset=key,name=n,center_m=p,rotation_z=yaw,scale=scale))

use("container","A · entry row",(-5.10,-.7,0),0)
use("container","B · long yard row",(-5.10,4.10,0),180)
use("container","C · blocked rear turn",(5.6,3.9,0),-90)
use("cover","Short cover ahead",(-.72,-.9,0),-13)
use("cover","Second cover", (3.8,1.8,0),31)
for k in range(4):
    use("fence",f"Rear fence bay {k+1}",(-5.13+k*3.42,7.13,0),0)
use("floodlight","Existing eight-lens tower",(-7.65,4.5,0),-18)
use("hut","Foreman exterior background",(5.78,7.40,0),0)

decal_rows=[
 ("Row A long pool",(-3.82,-.70,0),-90,(.84,.96,1)),
 ("Row B long pool",(-3.82,4.10,0),-90,(.80,1.08,1)),
 ("Turn recess pool",(3.04,2.71,0),0,(.86,.70,1)),
 ("Short cover pool",(-.72,-.55,0),-13,(.37,.48,1)),
 ("Far cover pool",(3.7,2.14,0),31,(.37,.43,1)),
]
decals=[]
for name,p,yaw,s in decal_rows:
    o=bpy.data.objects.new(name,shadow.data);bpy.context.collection.objects.link(o)
    mat=Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Diagonal(Vector((*s,1)))
    o.matrix_world=mat@shadow.matrix_world
    o.visible_shadow=False;decals.append(o)
bpy.data.objects.remove(shadow,do_unlink=True)

def mat(n,c,rough=.64,met=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Roughness"].default_value=rough;q.inputs["Metallic"].default_value=met
    return m
dark=mat("Stone ground core",(.065,.089,.106))
floor=mat("Industrial pale aggregate",(.27,.292,.285),.78)
line=mat("Sunwashed factory paint",(.75,.62,.339),.77)
post=mat("Graphite shoulders",(.098,.129,.142),.59)
warning=mat("Terminal amber",(.62,.245,.045),.58)
def box(n,p,d,mat,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if b:
        e=o.modifiers.new("Fine factory edge","BEVEL");e.width=b;e.segments=2
    o.visible_shadow=False
    return o
box("Dark full base",(0,.1,-.19),(260,240,.20),dark)
for i in range(-8,9):
    for j in range(-5,7):
        box("Lane concrete slabs",(i*1.5,j*1.5,-.054),(1.488,1.488,.108),floor,.006)
for j in range(-5,7):
    box("Narrow line guide",(1.32,j*1.03,.002),(.052,.64,.003),line)
for x in [-.8,-.53,-.26,0,.26,.53,.8]:
    q=box("Near painted datum stripe",(x,-4.3,.002),(.102,.59,.003),line)
    q.rotation_euler.z=-math.pi*.25
for x in (-8.8,8.8):
    box("Service rail line",(x,-.82,.39),(.25,13.2,.18),post,.025)
    for y in (-5.5,-2,1.5,5):
        box("Guard stub",(x,y,.38),(.16,.17,.76),warning,.024)
nt=floor.node_tree;bs=nt.nodes.get("Principled BSDF")
tex=nt.nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=47;tex.inputs["Roughness"].default_value=.74
tc=nt.nodes.new("ShaderNodeTexCoord");nt.links.new(tc.outputs["Object"],tex.inputs["Vector"])
b=nt.nodes.new("ShaderNodeBump");b.inputs["Strength"].default_value=.19;b.inputs["Distance"].default_value=.018
nt.links.new(tex.outputs["Fac"],b.inputs["Height"]);nt.links.new(b.outputs["Normal"],bs.inputs["Normal"])
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.36,.53,.70,1);bg.inputs["Strength"].default_value=.46
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,at,w,r,c in [((-9,-6,13),(0,3,1),3900,9,(1,.88,.72)),((7,-2,11),(0,2,1),1550,10,(.74,.86,1)),((0,10,12),(0,0,1),2000,11,(.77,.89,1))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=w;o.data.size=r;o.data.color=c;aim(o,at)
bpy.ops.object.camera_add(location=(6.8,-11.9,9.2));scene.camera=bpy.context.object;aim(scene.camera,(0,2.1,2.98))
scene.camera.data.type="ORTHO";scene.camera.data.ortho_scale=23.3
scene.render.engine="CYCLES";scene.cycles.samples=42;scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.044
scene.render.resolution_x=1440;scene.render.resolution_y=1040;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=91
if os.environ.get("WSC_SHADOW_SKIP_RENDER")!="1":
    scene.render.filepath=str(out/"nov23-east-shadow-pools-on.jpg")
    bpy.ops.render.render(write_still=True)
    for o in decals:o.hide_render=True
    scene.render.filepath=str(out/"nov23-east-shadow-pools-off.jpg")
    bpy.ops.render.render(write_still=True)
(out/"e5b-shadow-study.json").write_text(json.dumps(dict(
    scope="Illustrative E5b art layout. The decal does not set hidden state or claim collision or phone performance.",
    decal=dict(bytes=path.stat().st_size,triangles=220,alpha_max=round(max(alphas),4),width_m=6,deep_m=3.1),
    source_assets=report,placements=placement,pools=decal_rows),indent=2)+"\n")
