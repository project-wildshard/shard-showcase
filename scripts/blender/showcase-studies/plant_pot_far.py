"""WSC-PROP-056: an authored distance model with one vertex-colored draw primitive."""
import hashlib
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
src=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art/wsc-prop-056-plant-pot.glb"
clear_scene()
points=[];faces=[];colors=[]
rng=random.Random(29)
def ring_profile(profile,n,base,variation=.10):
    a=len(points)
    for r,z in profile:
        points.extend([(r*math.cos(math.tau*j/n),r*math.sin(math.tau*j/n),z) for j in range(n)])
    for i in range(len(profile)-1):
        for j in range(n):
            k=(j+1)%n
            faces.append((a+i*n+j,a+i*n+k,a+(i+1)*n+k,a+(i+1)*n+j))
            shade=1+variation*(math.cos(j*1.7)+.23*math.cos(i*2.3))
            colors.append(tuple(min(1,c*shade) for c in base))
def disc(z,r,n,col):
    a=len(points)
    points.append((0,0,z))
    for j in range(n):
        theta=math.tau*j/n
        points.append((r*math.cos(theta),r*math.sin(theta),z))
    for j in range(n):
        faces.append((a,a+j+1,a+((j+1)%n)+1));colors.append(col)

ring_profile([(.357,.012),(.377,.027),(.387,.065),(.391,.224),(.396,.448),(.397,.559),
              (.384,.580),(.363,.551),(.349,.524)],10,(.061,.083,.077),.24)
ring_profile([(.375,.541),(.413,.552),(.413,.578),(.398,.591),(.373,.583),(.371,.557)],10,
             (.233,.268,.251),.19)
ring_profile([(.356,.012),(.390,.015),(.394,.032),(.384,.051),(.372,.048)],10,
             (.19,.218,.195),.19)
disc(.523,.350,10,(.068,.043,.022))
disc(.012,.357,10,(.039,.054,.050))
for j in range(10):faces[-1-j]=tuple(reversed(faces[-1-j]))

def lance(theta,length,height,width,palette,angle_mod):
    # Center profile and upturned center fold, open tip and low tessellation.
    direction=Vector((math.cos(theta),math.sin(theta),0))
    lateral=Vector((-direction.y,direction.x,0))
    root=Vector((0,0,.522))+direction*(.070+rng.random()*.060)
    sections=[(0,0,.003),(.20,.34,.027),(.44,.76,width*.86),(.66,.99,width),(.86,1,width*.62),(1,.84,.002)]
    a=len(points)
    for u,v,w in sections:
        c=root+direction*length*u+Vector((0,0,height*v))+lateral*(angle_mod*u*u)
        v1=c-lateral*w; v2=c+lateral*w; ridge=c+Vector((0,0,max(.004,w)*.26))
        points.extend([v1,ridge,v2])
    for i in range(len(sections)-1):
        for j in range(2):
            h=a+i*3+j
            faces.append((h,h+3,h+4,h+1))
            tint=1.0+(.11 if j==1 else -.09)+.024*i
            colors.append(tuple(c*tint for c in palette))
    # same geometry material is two-sided, no duplicate rear draw
for i in range(16):
    angle=math.tau*i/16+.16*rng.uniform(-1,1);outer=i%3!=1
    length=rng.uniform(.33,.43) if outer else rng.uniform(.21,.30)
    height=rng.uniform(.18,.30) if outer else rng.uniform(.33,.45)
    green=((.099,.185,.032),(.148,.237,.038),(.067,.142,.024),(.194,.283,.051))[i%4]
    lance(angle,length,height,rng.uniform(.079,.122),green,rng.uniform(-.064,.064))
mesh=bpy.data.meshes.new("Plant pot distance mesh")
mesh.from_pydata(points,[],faces);mesh.update()
ob=bpy.data.objects.new("WSC-PROP-056 Plant pot distant",mesh);bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new("Pot and leaf colors");mat.use_nodes=True;mat.use_backface_culling=False
bs=mat.node_tree.nodes.get("Principled BSDF");bs.inputs["Roughness"].default_value=.67
layer=mesh.color_attributes.new(name="Tint",type='BYTE_COLOR',domain='CORNER')
mesh.color_attributes.active_color=layer
color=mat.node_tree.nodes.new("ShaderNodeVertexColor");color.layer_name=layer.name
mat.node_tree.links.new(color.outputs["Color"],bs.inputs["Base Color"])
ob.data.materials.append(mat)
for polygon, tint in zip(mesh.polygons,colors):
    for loop in polygon.loop_indices:layer.data[loop].color=(*tint,1)
lod=out/"wsc-prop-056-plant-pot-distance.glb"
export([ob],lod)
bpy.data.objects.remove(ob,do_unlink=True)
print(f"LOD bytes: {lod.stat().st_size}")

def bring(path,x):
    seen=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    added=set(bpy.context.scene.objects)-seen
    meshes=[o for o in added if o.type=="MESH"]
    for o in meshes:o.data.calc_loop_triangles()
    num=sum(len(o.data.loop_triangles) for o in meshes)
    bpy.context.view_layer.update()
    co=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    b=[tuple(round(fn(v[k] for v in co),3) for k in range(3)) for fn in (min,max)]
    for o in added:
        if o.parent not in added:o.matrix_world=Matrix.Translation((x,0,-b[0][2]))@o.matrix_world
    return meshes,num,b
near, near_tris, near_bounds=bring(src,-.92)
far, far_tris, far_bounds=bring(lod,.92)
assert len(far)==1 and len(far[0].data.materials)==1 and far[0].data.color_attributes
assert far_tris<710 and lod.stat().st_size<65536
assert .000<=far_bounds[0][2]<=.02 and .9<far_bounds[1][2]<1.04
for axis in range(3):
    a=near_bounds[1][axis]-near_bounds[0][axis]; b=far_bounds[1][axis]-far_bounds[0][axis]
    assert abs(a-b)/a < .13,(axis,a,b)
print("near",src.stat().st_size,near_tris,near_bounds,hashlib.sha256(src.read_bytes()).hexdigest())
print("far",lod.stat().st_size,far_tris,far_bounds,hashlib.sha256(lod.read_bytes()).hexdigest())

def simple(n,c,e=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Emission Color"].default_value=(*c,1);q.inputs["Emission Strength"].default_value=e
    q.inputs["Roughness"].default_value=.73
    return m
slate=simple("Promenade slate",(.073,.094,.102))
stage=simple("Green studio floor",(.045,.063,.055))
ink=simple("Ivory captions",(.83,.78,.63),.24)
def label(word,size,p):
    c=bpy.data.curves.new(word,"FONT");c.body=word;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(word,c);bpy.context.collection.objects.link(o);o.location=p
    o.rotation_euler.x=.56;c.materials.append(ink)
for x,st in [(-.92,"NEAR   /   ORIGINAL"),(.92,"DISTANCE   /   SINGLE MESH")]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,0,-.052))
    o=bpy.context.object;o.dimensions=(1.66,1.47,.102)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(slate)
    b=o.modifiers.new("Chamfer","BEVEL");b.width=.022;b.segments=2
    label(st,.085,(x,-.69,.020))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.112))
bpy.context.object.data.materials.append(stage)
label("EAST PLANT POT   /   WSC-PROP-056",.151,(0,.62,1.28))
s=bpy.context.scene;s.world.color=(.24,.26,.27)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for p,pow,rad,color in [((-2.4,-3.1,4.9),420,3,(1,.86,.69)),((2.6,-1,3.1),270,3,(.70,.89,1)),((0,2.9,3.7),440,3,(.81,1,.72))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=pow;o.data.size=rad;o.data.color=color;aim(o,(0,0,.35))
bpy.ops.object.camera_add(location=(0,-4.75,4.2))
s.camera=bpy.context.object;aim(s.camera,(0,0,.47));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=3.85
s.render.engine="CYCLES";s.cycles.samples=44;s.cycles.use_denoising=False
s.render.resolution_x=1420;s.render.resolution_y=985;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-east-plant-pot-lods.jpg")
bpy.ops.render.render(write_still=True)
