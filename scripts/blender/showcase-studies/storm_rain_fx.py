"""W11a/E9 art study: neutral wind rain tile and animated splash; no runtime wiring."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
clear_scene()
rng=random.Random(932)
def material(n,c,rough=.45,metal=0,emission=0,alpha=1):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,alpha)
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*c,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    p.inputs["Emission Color"].default_value=(*c,1)
    p.inputs["Emission Strength"].default_value=emission
    p.inputs["Alpha"].default_value=alpha
    if alpha<1:
        m.surface_render_method='BLENDED'
        m.use_backface_culling=False
    return m
rain_ink=material("Rain slip | satin atmosphere",(.18,.38,.55),.35,0,.6,.36)
splash_ink=material("Splash lumen | cool shore",(.18,.42,.50),.42,0,.80,.61)

def mesh_object(name,points,polygons,mat):
    m=bpy.data.meshes.new(name)
    m.from_pydata(points,[],polygons);m.update();m.materials.append(mat)
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
    return o

pts=[];faces=[]
def panel(a,b,width,offset):
    i=len(pts);w=offset.normalized()*width
    pts.extend([a-w*.4,a+w*.4,b+w,b-w])
    faces.append((i,i+1,i+2,i+3))
# 6 x 6 x 4 m tile; dry ground at zero. Centered in X/Y with +X wind.
for i in range(76):
    x=rng.uniform(-2.78,2.68);y=rng.uniform(-2.88,2.88);z=rng.uniform(.26,3.52)
    length=rng.uniform(.19,.43);width=rng.uniform(.0023,.0067)
    a=Vector((x,y,z));b=a+Vector((-.25*length,.08*length,length))
    panel(a,b,width,Vector((0,1,0)))
    panel(a,b,width,Vector((1,0,.25)))
rain=mesh_object("Rain_6m_crossed_streaks",pts,faces,rain_ink)
rain_path=out/"wsc-kit-007-storm-rain-tile.glb"
export([rain],rain_path)
bpy.data.objects.remove(rain,do_unlink=True)

pts=[];faces=[]
for k,(r,a0,a1) in enumerate([(.22,.25,4.6),(.24,4.95,6.11),(.37,1.07,4.95)]):
    n=(15,6,15)[k]
    for j in range(n+1):
        t=a0+(a1-a0)*j/n
        s=math.sin(math.pi*j/n)
        thick=.004+.016*s
        pts.extend([(r*math.cos(t),r*math.sin(t),.009+k*.005),((r+thick)*math.cos(t),(r+thick)*math.sin(t),.012+k*.005)])
        if j:
            a=len(pts)-4;faces.append((a,a+1,a+3,a+2))
for i in range(8):
    a=i*math.tau/8+.13;rs=.14+.025*(i%3)
    x=rs*math.cos(a);y=rs*math.sin(a)
    j=len(pts)
    pts.extend([(x-.009,y, .045),(x+.011,y, .044),(x,y+.009,.037),(x*1.22,y*1.22,.12+.013*(i%3))])
    faces.extend([(j,j+2,j+1),(j,j+1,j+3),(j+1,j+2,j+3),(j+2,j,j+3)])
impact=mesh_object("Rain_impact",pts,faces,splash_ink)
s=bpy.context.scene;s.render.fps=24;s.frame_start=0;s.frame_end=20
for frame,scale in [(0,(.045,.045,.015)),(3,(.47,.47,1)),(8,(.83,.83,.48)),(14,(1,1,.11)),(20,(.045,.045,.015))]:
    impact.scale=scale;impact.keyframe_insert("scale",frame=frame)
impact.animation_data.action.name="Rain impact"
bpy.ops.object.select_all(action='DESELECT');impact.select_set(True);bpy.context.view_layer.objects.active=impact
s.frame_set(0)
splash_path=out/"wsc-kit-007-storm-splash.glb"
bpy.ops.export_scene.gltf(filepath=str(splash_path),export_format='GLB',use_selection=True,export_animations=True,
                          export_animation_mode='ACTIONS',export_force_sampling=False)
bpy.data.objects.remove(impact,do_unlink=True)

def imported(path):
    pre=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted(set(s.objects)-pre,key=lambda o:o.name)

tile,=imported(rain_path); splash,=imported(splash_path)
for obj in (tile,splash):obj.data.calc_loop_triangles()
assert len(tile.data.loop_triangles)==304 and len(splash.data.loop_triangles)==104
assert splash.animation_data and splash.animation_data.action
frame_range=splash.animation_data.action.frame_range[:]
assert frame_range[1]-frame_range[0]==20
s.frame_set(3);s0=splash.scale[:]
s.frame_set(14);s1=splash.scale[:]
assert s0[0]<.6 and s0[2]>.8 and s1[0]>.95 and s1[2]<.2,(s0,s1)
tower_path=assets/"wsc-kit-007-storm-beacon.glb"
lamp_path=assets/"wsc-kit-007-storm-beacon-charged-lamp.glb"
tower=imported(tower_path);lamp=imported(lamp_path)
p=Vector((-.10,.73,0))
for ob in tower+lamp:
    if ob.parent not in tower+lamp:ob.matrix_world=Matrix.Translation(p)@ob.matrix_world
# Copy the exact imported geometry to two height layers with a single shared mesh datablock.
scene_rain=[(-3.01,-3,0),(2.98,-3,0),(-3.01,3.01,0),(2.98,3.01,0),(-3.01,3.01,4),(2.98,3.01,4)]
for i,v in enumerate(scene_rain):
    q=bpy.data.objects.new(f"Rain tile {i+1}",tile.data);bpy.context.collection.objects.link(q);q.location=v
    if i==1:q.rotation_euler.z=math.pi*.03
bpy.data.objects.remove(tile,do_unlink=True)
for i in range(53):
    x=rng.uniform(-5.7,5.7);y=rng.uniform(-5.4,3.1)
    if abs(x)<1.1 and abs(y-.73)<1.1:continue
    q=bpy.data.objects.new(f"Staggered impact sprite {i}",splash.data)
    bpy.context.collection.objects.link(q);q.location=(x,y,.023)
    a=rng.uniform(.28,.73);q.scale=(a,a,rng.uniform(.10,.47));q.rotation_euler.z=rng.uniform(0,math.tau)
bpy.data.objects.remove(splash,do_unlink=True)

wet=material("Dark rain-slick concrete",(.054,.079,.101),.22,.16)
nt=wet.node_tree
q=nt.nodes.get("Principled BSDF")
tex=nt.nodes.new("ShaderNodeTexNoise");tex.inputs["Scale"].default_value=9;tex.inputs["Roughness"].default_value=.72
coords=nt.nodes.new("ShaderNodeTexCoord");nt.links.new(coords.outputs["Object"],tex.inputs["Vector"])
mix=nt.nodes.new("ShaderNodeMapRange");mix.inputs["To Min"].default_value=.13;mix.inputs["To Max"].default_value=.37
nt.links.new(tex.outputs["Fac"],mix.inputs["Value"]);nt.links.new(mix.outputs["Result"],q.inputs["Roughness"])
bump=nt.nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.13;bump.inputs["Distance"].default_value=.024
nt.links.new(tex.outputs["Fac"],bump.inputs["Height"]);nt.links.new(bump.outputs["Normal"],q.inputs["Normal"])
black=material("Near-black wet pavement gaps",(.019,.025,.04),.25)
orange=material("Wet enamel shoulders",(.55,.15,.031),.22,.1)
metal=material("Wet cobalt structure",(.048,.091,.133),.30,.26)
concrete=material("Wet raw footing",(.087,.113,.13),.36,.11)
foot=material("Reflective inlay",(.522,.304,.079),.24,.04,.20)
def box(n,where,d,mat,bevel=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=where)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new("Enamel edge","BEVEL");b.width=bevel;b.segments=2
    return o
box("Back of stage",(0,0,-.15),(170,160,.23),black)
for i in range(-9,10):
    for j in range(-5,7):
        box("Wet paving sample",(1.39*i,1.6*j,-.052),(1.374,1.581,.104),wet,.014)
box("Raised beacon pedestal",(-.1,.73,-.021),(2.30,1.91,.088),concrete,.05)
for h in (.53,1.13):
    box("Shoulder barrier core",(0,5.1,h),(17,.26,.48),metal,.06)
for x in range(-7,8):
    box("Amber rim marker",(x*.91,4.958,.74),(.36,.036,.19),orange,.025)
for i in range(10):
    box("Wet leading edge marking",(-1.30+.265*i,-2.25,.008),(.125,.022,.01),foot,.004)
for x in (-6.9,-4.6,4.6,6.9):
    box("Scenic back-wall post",(x,7.4,2.2),(.28,.38,4.4),metal,.04)
box("Scenic wall",(0,7.6,1.7),(33,.26,3.4),black,.04)
distance=material("Distant haze roofs",(.022,.040,.062),.61)
for x,y,z,w in [(-8,14,5.2,4.9),(-5,13,4.4,3),(-1.5,17,5.5,4.3),(9,18,4.7,3.6),(-11.2,12,6.2,2.5)]:
    box("Distant factory silhouette",(x,y,z/2),(w,2,z),distance,.10)
for loc in ((-8,13.3,5.32),(-1.5,16.5,5.63),(9,17.4,4.83)):
    box("Distant warning dot",loc,(.12,.09,.08),orange,.014)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for pos,tar,power,size,c in [((1,-5,7),(0,.5,2.0),1350,7,(.54,.76,1)),
                             ((-4,4,8),(0,0,2.1),1800,5,(.38,.63,1)),
                             ((1,4,6.3),(0,1,3.0),1300,5,(.50,.77,1)),
                             ((-.1,.53,4.91),(-.1,-1,1),125,1,(1,.60,.30))]:
    bpy.ops.object.light_add(type="AREA",location=pos);o=bpy.context.object
    o.data.energy=power;o.data.size=size;o.data.color=c;aim(o,tar)
bpy.ops.object.camera_add(location=(7.7,-10.6,3.6))
s.camera=bpy.context.object;aim(s.camera,(0,.55,2.33));s.camera.data.lens=47
s.world.use_nodes=True
sky=s.world.node_tree.nodes.get("Background")
sky.inputs[0].default_value=(.034,.056,.085,1);sky.inputs[1].default_value=.64
s.use_nodes=True
comp=s.node_tree
rl=comp.nodes.get("Render Layers")
dest=comp.nodes.get("Composite")
glow=comp.nodes.new("CompositorNodeGlare");glow.glare_type="FOG_GLOW";glow.quality="HIGH";glow.threshold=1.8
comp.links.new(rl.outputs["Image"],glow.inputs["Image"]);comp.links.new(glow.outputs["Image"],dest.inputs["Image"])
s.frame_set(12)
s.render.engine="CYCLES";s.cycles.samples=50;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.045
s.render.resolution_x=1360;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(out/"nov23-e9-wind-rain-preview.jpg")
bpy.ops.render.render(write_still=True)
for o,f in [(rain_path,304),(splash_path,104)]:
    print(f'{o.name}: {o.stat().st_size} bytes; {f} triangles; sha256 {hashlib.sha256(o.read_bytes()).hexdigest()}')
