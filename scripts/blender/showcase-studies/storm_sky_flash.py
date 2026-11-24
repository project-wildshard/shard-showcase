"""W11a/E9 atmosphere art: one distant lightning asset and preview cue."""
import hashlib
import json
import math
from pathlib import Path
import random
import os
import struct
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

S=bpy.context.scene
O=output_directory()
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
pins={
 "wsc-kit-007-storm-beacon.glb":"3a525f2637d5150a1e5a85c04640d6a57772c842731f063aa429142810239833",
 "wsc-kit-007-storm-beacon-charged-lamp.glb":"ab7445a6977c9af5cea7a31618a9c660f539e1026e23e61b1bbc2b3426b77a5d",
}
for name,sha in pins.items():
    assert hashlib.sha256((assets/name).read_bytes()).hexdigest()==sha

clear_scene()


def mat(name,c,rough=.5,metal=0,emit=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Roughness"].default_value=rough
    n.inputs["Metallic"].default_value=metal
    n.inputs["Emission Color"].default_value=(*c,1)
    n.inputs["Emission Strength"].default_value=emit
    return m


core=mat("Distant lightning core",(.56,.73,1),.78,0,5.4)
verts,faces=[],[]


def stroke(points,base,tip):
    # Vary the large silhouette with smaller irregular cuts. The seed
    # comes from the broad branch anchors, so identical input is stable.
    seed=sum(round(sum(abs(q) for q in pos)*1000) for pos in points)
    rng=random.Random(seed)
    path=[Vector(points[0])]
    for a,b in zip(points,points[1:]):
        a,b=Vector(a),Vector(b)
        span=(b-a).length
        for t in (.35,.68):
            q=a.lerp(b,t)
            q.x+=rng.uniform(-.072,.073)*span
            q.y+=rng.uniform(-.037,.033)*span
            q.z+=rng.uniform(-.030,.029)*span
            path.append(q)
        path.append(b)
    for i,(a,b) in enumerate(zip(path,path[1:])):
        n=(b-a).normalized()
        side=n.cross(Vector((0,1,0))).normalized()
        cross=n.cross(side).normalized()
        for s in (side,cross):
            width0=base+(tip-base)*i/(len(path)-1)
            width1=base+(tip-base)*(i+1)/(len(path)-1)
            if i==0 and points[0]==(0,0,0):
                width0*=.30
            start=len(verts)
            verts.extend([a-s*.5*width0,a+s*.5*width0,b+s*.5*width1,b-s*.5*width1])
            faces.append(tuple(range(start,start+4)))

main=[(0,0,0),(-.70,.19,-2.05),(-.41,.41,-3.01),
      (-1.77,.26,-4.67),(-1.58,-.23,-5.92),(-2.66,-.30,-7.56),
      (-2.28,-.36,-9.21),(-3.46,-.14,-10.59),(-3.37,-.02,-12.18)]
stroke(main,.153,.033)
stroke([main[2],(.70,.27,-4.32),(.55,.14,-5.31),(1.75,.15,-6.55),
        (2.07,.35,-7.40)],.088,.009)
stroke([main[4],(-3.08,-.08,-6.53),(-3.46,.12,-7.10),(-4.66,.35,-7.85)],
       .061,.007)
stroke([main[6],(-1.11,-.27,-9.93),(-.79,-.20,-10.78),(.01,.03,-11.51)],.053,.005)
stroke([main[1],(-1.86,.33,-2.75),(-2.33,.44,-3.61)],.051,.008)
mesh=bpy.data.meshes.new("Branched lightning · reusable visual")
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new(mesh.name,mesh)
S.collection.objects.link(obj)
mesh.materials.append(core)
glb=O/"e9-distant-lightning.glb"
export([obj],glb)
raw=glb.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert len(doc["meshes"])==len(doc["nodes"])==len(doc["materials"])==1
assert not set(doc)&{"images","animations","skins","extensionsRequired"}
pr=doc["meshes"][0]["primitives"][0]
tris=doc["accessors"][pr["indices"]]["count"]//3
assert tris==240 and len(raw)<18000,(tris,len(raw))


def load(p):
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    return sorted((o for o in set(S.objects)-before if o.type=="MESH"),key=lambda o:o.name)


clear_scene()
bolt,=load(glb)
bolt.data.calc_loop_triangles()
assert len(bolt.data.loop_triangles)==tris and bolt.location.length<.001
bolt.location=(7.5,32,15.0)
bolt.rotation_mode="XYZ"
bolt.rotation_euler.z=-.108
bolt.scale=(.77,.77,.77)

for name in pins:
    for o in load(assets/name):
        o.matrix_world=Matrix.Translation((-2.26,-.32,0))@o.matrix_world


def box(name,pos,dims,m,b=.07):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object
    o.name=name
    o.dimensions=dims
    o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        bv=o.modifiers.new("Chamfer","BEVEL")
        bv.width=b
        bv.segments=2
    return o


boundary=mat("Evening silhouette steel",(.019,.031,.051),.76,.22)
steel=mat("Night fence ribs",(.037,.064,.091),.57,.49)
white=mat("Wet concrete",(.066,.085,.109),.30,.16)
paint=mat("Wet ochre curb",(.42,.23,.052),.48,.14)
warm=mat("Distant signal amber",(.88,.36,.039),.38,0,.61)
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-.015))
bpy.context.object.data.materials.append(white)
n=white.node_tree.nodes
links=white.node_tree.links
noise=n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=4.6
noise.inputs["Detail"].default_value=3.3
coords=n.new("ShaderNodeTexCoord")
links.new(coords.outputs["Object"],noise.inputs["Vector"])
bump=n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.25
bump.inputs["Distance"].default_value=.026
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs[0],n["Principled BSDF"].inputs["Normal"])
for i in range(13):
    box("Apron stripe",(-.10,-5+i*1.04,.006),(.086,.56,.01),paint,.003)
for i,x in enumerate((-15,-9.7,-5.9,3.1,8.3,13.5,19)):
    h=(3.3,4.3,2.9,2.6,3.8,3.4,4.3)[i]
    y=12+math.sin(i*1.5)*2.6
    box("Distant industrial shelf",(x,y,h*.5),(4.78,1.2,h),boundary,.07)
    for dx in (-1.9,1.9):
        box("Back rail",(x+dx,y-.65,h*.49),(.13,.16,h*.99),steel,.025)
    box("Amber yard marker",(x+1.90,y-.742,h*.77),(.26,.04,.12),warm,.018)

# Procedural cloud card dressing is not exported. The matched test
# changes a single art cue: bolt visibility, cloud glow, cool light.
cloud=bpy.data.materials.new("Cloud bank · preview only")
cloud.use_nodes=True
n=cloud.node_tree.nodes
links=cloud.node_tree.links
n.clear()
out=n.new("ShaderNodeOutputMaterial")
nc=n.new("ShaderNodeTexCoord")
scale=n.new("ShaderNodeVectorMath")
scale.operation="MULTIPLY"
scale.inputs[1].default_value=(6,.95,12)
ns=n.new("ShaderNodeTexNoise")
ns.inputs["Scale"].default_value=1.16
ns.inputs["Detail"].default_value=4.6
ns.inputs["Roughness"].default_value=.61
links.new(nc.outputs["Generated"],scale.inputs[0])
links.new(scale.outputs[0],ns.inputs["Vector"])
r=n.new("ShaderNodeValToRGB")
r.color_ramp.elements[0].position=.15
r.color_ramp.elements[0].color=(.0035,.0068,.018,1)
r.color_ramp.elements[1].position=.78
r.color_ramp.elements[1].color=(.049,.073,.139,1)
links.new(ns.outputs["Fac"],r.inputs[0])
em=n.new("ShaderNodeEmission")
links.new(r.outputs[0],em.inputs["Color"])
# Feather the glow around the origin instead of brightening the entire sky.
delta=n.new("ShaderNodeVectorMath")
delta.operation="SUBTRACT"
delta.inputs[1].default_value=(.590,.0,.56)
links.new(nc.outputs["Generated"],delta.inputs[0])
spread=n.new("ShaderNodeVectorMath")
spread.operation="MULTIPLY"
spread.inputs[1].default_value=(5.7,0,4.4)
links.new(delta.outputs[0],spread.inputs[0])
radius=n.new("ShaderNodeVectorMath")
radius.operation="LENGTH"
links.new(spread.outputs[0],radius.inputs[0])
decay=n.new("ShaderNodeMath")
decay.operation="MULTIPLY"
links.new(radius.outputs["Value"],decay.inputs[0])
links.new(radius.outputs["Value"],decay.inputs[1])
gauss=n.new("ShaderNodeMath")
gauss.operation="POWER"
gauss.inputs[0].default_value=.035
links.new(decay.outputs[0],gauss.inputs[1])
response=n.new("ShaderNodeMath")
response.operation="MULTIPLY_ADD"
links.new(gauss.outputs[0],response.inputs[0])
response.inputs[2].default_value=1.04
links.new(response.outputs[0],em.inputs["Strength"])
links.new(em.outputs[0],out.inputs["Surface"])
# Generated coordinates on a cube with a thin dimension remain stable.
box("Cloud back card",(0,58,17),(110,.13,46),cloud,0)


def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()


def light(name,pos,target,power,c,size):
    d=bpy.data.lights.new(name,"AREA")
    d.energy,d.color,d.size,d.shape=power,c,size,"DISK"
    o=bpy.data.objects.new(name,d)
    S.collection.objects.link(o)
    o.location=pos
    aim(o,target)
    return o

light("Cold low ambient",(-5.2,2.5,8),(0,0,2),710,(.49,.64,1),7.7)
light("Amber beacon reflection",(-2.26,-.44,4.81),(-2.3,-3.4,.28),
      170,(1,.62,.29),1.3)
light("Cold perimeter edge",(8.9,6.8,3.8),(0,0,1.8),480,(.58,.70,1),5.2)
flash=light("One diffuse fill pulse",(4.0,6.0,12.6),(0,-2,1),0,(.57,.72,1),9)
S.world=bpy.data.worlds.new("Blue storm ambient")
S.world.color=(.054,.068,.104)
bpy.ops.object.camera_add(location=(2.25,-11.8,2.35))
S.camera=bpy.context.object
aim(S.camera,(.11,4.4,3.0))
S.camera.data.lens=44
S.render.engine="CYCLES"
S.cycles.samples=42
S.cycles.use_denoising=False
S.render.resolution_x,S.render.resolution_y=1500,980
S.render.resolution_percentage=100
S.render.image_settings.file_format="JPEG"
S.render.image_settings.quality=92
S.view_settings.view_transform="AgX"
S.view_settings.look="AgX - Medium High Contrast"
S.use_nodes=True
comp=S.node_tree
layer=comp.nodes.get("Render Layers")
dst=comp.nodes.get("Composite")
glow=comp.nodes.new("CompositorNodeGlare")
glow.glare_type="FOG_GLOW"
glow.quality="HIGH"
glow.threshold=1.6
comp.links.new(layer.outputs["Image"],glow.inputs["Image"])
comp.links.new(glow.outputs["Image"],dst.inputs["Image"])

cue=((0,0),(.10,0),(.16,1),(.24,.36),(.43,.08),(.69,0))
assert all(a[0]<b[0] for a,b in zip(cue,cue[1:]))
assert max(x[1] for x in cue)==1 and sum(x[1]==1 for x in cue)==1
for slug,intensity in (("rest",0),("peak",1)):
    bolt.hide_render=intensity==0
    flash.data.energy=1460*intensity
    response.inputs[1].default_value=intensity*1.75
    S.render.filepath=str(O/f"nov24-storm-sky-{slug}.jpg")
    if not (slug=="rest" and os.environ.get("WSC_STORM_PEAK_ONLY")=="1"):
        bpy.ops.render.render(write_still=True)

(O/"storm-sky-flash-proof.json").write_text(json.dumps({
 "scope":"Static distant art and suggested single-pulse review cue; no player-facing runtime or sound.",
 "bytes":len(raw),"triangles":tris,"materials":1,"bolt_anchor":"seed origin at upper end",
 "flash_cue_time_s_normalized":cue,
 "donors":pins,"preview_effects":"Non-exported cloud card, lighting, backdrop and bloom.",
},indent=2)+"\n")
