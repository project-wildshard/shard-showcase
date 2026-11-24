"""E5b preview: a lightweight floor cue, not an enemy or its sight volume."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import struct
import sys

import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from common import export, output_directory

out = output_directory()
assets = here.parents[2] / "public/assets/wildshard-art"
donors = {
    "wsc-prop-058-shipping-container": "8bd1c2bca075256315a8bf5a76b5da489b3e42fca0def63d06088031695232af",
    "wsc-prop-066-orange-cover-barrier": "e999ab405f289a1dfdebf307c26ae260eb2392d1c6b75b4a6ec35b3e1e0b6b36",
    "wsc-module-023-corrugated-yard-fence": "7adef24ac76e756865ec8ddc7ab8c054375759334d0861ce93036791f098d020",
    "wsc-module-024-floodlight-tower": "316a77c8fdabebbbc2767fe035b7a24caa749773cffe98f2dcf99791d7ec16b2",
    "wsc-prop-065-keycard-shed": "1702aa6968159d7b35b319bcbae4112c89b123fb885113c4e3cfb94aab39c966",
}
for name,sha in donors.items():
    assert hashlib.sha256((assets/(name+".glb")).read_bytes()).hexdigest() == sha

# Rebuild existing yard and shadow pools from the checked source; no snapshot.
argv = sys.argv
old_skip = os.environ.get("WSC_SHADOW_SKIP_RENDER")
try:
    os.environ["WSC_SHADOW_SKIP_RENDER"] = "1"
    sys.argv = [argv[0],"--",str(out/"yard")]
    runpy.run_path(str(here/"east_shadow_pools.py"), run_name="__main__")
finally:
    sys.argv = argv
    if old_skip is None:
        del os.environ["WSC_SHADOW_SKIP_RENDER"]
    else:
        os.environ["WSC_SHADOW_SKIP_RENDER"] = old_skip
scene = bpy.context.scene
cue_z = .017
length = 5.8
half_angle = math.radians(15)
# A faint fill, narrow bright shoulders and a soft readable curved far edge.
# Continuous vertices prevent blended rings from overlapping each other.
angles = (-1,-.98,-.945,-.89,-.65,-.31,0,.31,.65,.89,.945,.98,1)
distances = (.11,.22,.42,.85,1.45,2.3,3.35,4.48,5.16,5.36,5.51,5.63,5.71,5.8)
n = len(angles)
vs, fs, colors = [], [], []
for r in distances:
    for a in angles:
        t = a*half_angle
        x,y = math.sin(t)*r, math.cos(t)*r
        vs.append((x,y,cue_z))
        fade = min(1,max(0,(r-.11)/.78))
        fill = .22*(.8 + .2*r/length)*(1-.50*abs(a)**1.4)
        shoulders = .48*math.exp(-((abs(a)-.94)/.041)**2)
        lip = .47*math.exp(-((r-5.58)/.115)**2)
        scanline = .13*math.exp(-((r-4.48)/.11)**2)
        alpha = (fill+shoulders+lip+scanline)*fade
        alpha *= min(1,max(0,(1-abs(a))/.035))*min(1,max(0,(length-r)/.09))
        alpha = min(.75,alpha)
        # Warm-gold marker is distinct from the green keycard. Bright rims
        # also retain the shape without relying exclusively on orange hue.
        rim = min(1,(shoulders+lip)*1.65)
        colors.append((.99,.29+.47*rim,.045+.21*rim,alpha))
        i = len(vs)-1
        if i//n and i%n:
            fs.append((i-n-1,i-n,i,i-1))
mesh = bpy.data.meshes.new("Patrol lamp floor sweep")
mesh.from_pydata(vs,[],fs)
mesh.update()
material = bpy.data.materials.new("Warning amber alpha · unlit")
material.use_nodes = True
material.surface_render_method = "BLENDED"
nt = material.node_tree
pbr = nt.nodes.get("Principled BSDF")
color = mesh.color_attributes.new(name="Sweep",type="FLOAT_COLOR",domain="CORNER")
mesh.color_attributes.active_color = color
for i,loop in enumerate(mesh.loops):
    color.data[i].color = colors[loop.vertex_index]
node = nt.nodes.new("ShaderNodeVertexColor")
node.layer_name = color.name
nt.links.new(node.outputs["Color"],pbr.inputs["Base Color"])
nt.links.new(node.outputs["Alpha"],pbr.inputs["Alpha"])
mesh.materials.append(material)
source = bpy.data.objects.new("E5b patrol floor sweep",mesh)
scene.collection.objects.link(source)
file = out/"wsc-kit-006-patrol-floor-sweep.glb"
export([source],file)
bpy.data.objects.remove(source,do_unlink=True)
raw = file.read_bytes()
magic,version,size,head,tag = struct.unpack_from("<4sIII4s",raw)
assert (magic,version,size,tag)==(b"glTF",2,len(raw),b"JSON")
doc=json.loads(raw[20:20+head])
assert len(raw)<55_000 and len(doc["meshes"])==1 and len(doc["materials"])==1
assert doc["materials"][0].get("alphaMode")=="BLEND", doc["materials"]
# This exporter preserves color/alpha via Principled, not through the
# transparent + emission graph. Mark the same RGB/alpha material unlit
# in the standard JSON chunk while leaving the original BIN untouched.
doc.setdefault("extensionsUsed",[]).append("KHR_materials_unlit")
doc["materials"][0].setdefault("extensions",{})["KHR_materials_unlit"] = {}
payload=json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode()
payload+=b" " * (-len(payload)%4)
raw=struct.pack("<4sIII4s",magic,version,20+len(payload)+len(raw[20+head:]),
                len(payload),tag)+payload+raw[20+head:]
file.write_bytes(raw)
assert len(raw)<55_000

assert not any(doc.get(k) for k in ("images","skins","animations"))
assert all("COLOR_0" in p["attributes"] for p in doc["meshes"][0]["primitives"])
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(file))
cue,=set(scene.objects)-before
cue.data.calc_loop_triangles()
triangles = len(cue.data.loop_triangles)
assert triangles == 312
alpha = [v.color[3] for v in cue.data.color_attributes.active_color.data]
assert min(alpha)<1e-6 and .60<max(alpha)<.76, max(alpha)
cue.location=(1.42,4.67,0)
cue.rotation_mode = "XYZ"
cue.rotation_euler.z=math.radians(-174)
cue.visible_shadow = cue.visible_diffuse = cue.visible_glossy = False
cue.hide_set(True)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
gaps=[]
transformed = [cue.matrix_world @ v.co for v in cue.data.vertices]
assert -1.14 < min(p.y for p in transformed) < -1.12
assert 4.55 < max(p.y for p in transformed) < 4.57
for v in cue.data.vertices:
    p = cue.matrix_world @ v.co
    hit,at,_,_,ob,_=scene.ray_cast(dg,(p.x,p.y,2.0),(0,0,-1),distance=2.5)
    assert hit and at.z < p.z-.003,(list(p),list(at),ob.name if ob else None)
    gaps.append(p.z-at.z)
cue.hide_set(False)
# Keep stage readable at dusk without actual light from the cue.
for ob in scene.objects:
    if ob.type=="LIGHT":
        ob.data.energy *= .47
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.30
scene.cycles.samples=40
scene.cycles.adaptive_threshold=.075
scene.view_settings.view_transform="AgX"
scene.render.resolution_x,scene.render.resolution_y=1320,870
cam=scene.camera
cam.data.type="PERSP"
cam.data.lens=28
cam.location=(3.25,-6.2,1.70)
cam.rotation_euler=(Vector((1.0,1.3,1.15))-cam.location).to_track_quat("-Z","Y").to_euler()
for name,hide in [("unmarked",True),("marked",False)]:
    cue.hide_render=hide
    scene.render.filepath=str(out/f"nov24-e5b-sweep-{name}.jpg")
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)
(out/"patrol-sweep-validation.json").write_text(json.dumps({
    "blender_z_up_local": "+Y forward, X span, 17 mm above flat floor",
    "length_m": length, "visual_half_angle_degrees":15,
    "bytes":len(raw),"triangles":triangles,"sha256":hashlib.sha256(raw).hexdigest(),
    "tested_stage_base_xyz_m":list(cue.location),"tested_stage_blender_yaw_degrees":-174,
    "reimport_vertex_gap_min_m":round(min(gaps),5),
    "reimport_vertex_gap_max_m":round(max(gaps),5),
    "vertex_rays":len(gaps), "additive_blending":False,
    "real_light":False,"runtime_behavior":False,"donor_sha256":donors,
},indent=2)+"\n")
