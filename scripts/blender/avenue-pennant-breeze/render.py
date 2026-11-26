"""Render two phases of the exported clip from the same oblique camera."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/"showcase-studies"))
from common import clear_scene,output_directory
O=output_directory();clear_scene();S=bpy.context.scene
S.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(O/"wsc-prop-015-pennant-breeze.glb"))
for o in S.objects:
    if o.parent is None:o.location.z+=2.85

def material(name,color,metal=.09,rough=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value=(*color,1)
    q.inputs["Metallic"].default_value=metal
    q.inputs["Roughness"].default_value=rough
    return m
stone=material("Stage | warm limestone",(.28,.259,.211))
steel=material("Stage | dark architectural iron",(.045,.072,.089),.52)
dye=material("Stage | oxblood bronze",(.29,.104,.039),.48)
ground=material("Stage | navy cyclorama",(.043,.065,.083))
def box(p,d,m,w=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if w:
        b=o.modifiers.new("Cut arris","BEVEL");b.width=w;b.segments=3
        o.modifiers.new("Face weights","WEIGHTED_NORMAL")
for x in (-3.61,3.61):
    box((x,0,3.42),(.23,.24,2.13),steel,.023)
    box((x,0,2.22),(.42,.42,.35),stone)
    box((x,0,4.44),(.32,.32,.15),dye)
    box((x,0,4.15),(.34,.287,.12),dye)
    box((x,0,2.79),(.28,.30,.14),dye)
    box((x,0,1.0),(.35,.35,2.1),stone)
    for z in (3.08,3.66,4.08):
        box((x,-.14,z),(.085,.06,.085),dye,.014)
box((0,0,-.075),(120,120,.15),ground,0)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
if not S.world:S.world=bpy.data.worlds.new("Soft blue")
S.world.use_nodes=True
S.world.node_tree.nodes.get("Background").inputs[0].default_value=(.077,.125,.18,1)
S.world.node_tree.nodes.get("Background").inputs[1].default_value=.35
for name,p,power,r,c in [("Soft amber key",(-3,-5,8),1350,5,(1,.81,.60)),
                         ("Blue fill",(4,-3,4.2),730,4,(.61,.76,1)),
                         ("Rim channel",(1,3,6.4),1550,4,(.76,.88,1))]:
    lamp=bpy.data.lights.new(name,"AREA");lamp.energy=power;lamp.size=r;lamp.color=c
    o=bpy.data.objects.new(name,lamp);S.collection.objects.link(o);o.location=p;aim(o,(0,0,3.45))
cm=bpy.data.cameras.new("Pennant eye line");o=bpy.data.objects.new(cm.name,cm)
S.collection.objects.link(o);S.camera=o;cm.type="ORTHO";cm.ortho_scale=8.35
o.location=(4.1,-10.8,4.48);aim(o,(0,0,3.29))
S.render.engine="CYCLES";S.cycles.samples=26;S.cycles.use_denoising=False
S.view_settings.view_transform="AgX"
S.render.resolution_x=1460;S.render.resolution_y=830;S.render.resolution_percentage=100
S.render.image_settings.file_format="WEBP";S.render.image_settings.quality=89
for frame,label in ((5,"crosswind"),(41,"return")):
    S.frame_set(frame);bpy.context.view_layer.update()
    S.render.filepath=str(O/f"nov26-avenue-pennants-{label}.webp")
    bpy.ops.render.render(write_still=True)
