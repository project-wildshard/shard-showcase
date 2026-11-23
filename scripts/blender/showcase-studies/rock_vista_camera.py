"""W9b visual framing on the rebuilt Rock summit; does not save the source scene."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory
out=output_directory()
s=bpy.context.scene
# Input is the generated climb-rock-editable.blend from west-climb-rock/build.py.
benches=[o for o in s.objects if o.type=="MESH" and o.name.startswith("CLIMB | native lookout bench")]
assert len(benches)==10
floor=Vector((-210,-40,16))
co=[o.matrix_world@p.co for o in benches for p in o.data.vertices]
bounds=[[round(fn(v[k] for v in co),3) for k in range(3)] for fn in (min,max)]
assert bounds[0][2]==16 and bounds[1][2]==16.605
mid=(Vector(bounds[0])+Vector(bounds[1]))/2
assert (Vector((mid.x,mid.y,16))-floor).length<.025
# Remove acquisition rigs, not source art. Reuse the bench, crag and near horizon.
for o in tuple(s.objects):
    if o.type in {"LIGHT","CAMERA"}:bpy.data.objects.remove(o,do_unlink=True)
zs=[o for o in s.objects if o.name.startswith("CLIMB |")]
assert len(zs)>12
# Only the in-memory crown skin used in these pictures; never edit or save the base.
crag=next(o for o in zs if "crag mesh" in o.name)
ridge_material=next(m for m in crag.data.materials if m.name.startswith("CLIMB moss"))
m=ridge_material.copy();m.name="Vista composition mossy stone"
n=m.node_tree.nodes;links=m.node_tree.links
tc=n.new("ShaderNodeTexCoord");noise=n.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=.84
links.new(tc.outputs["Object"],noise.inputs["Vector"])
remap=n.new("ShaderNodeValToRGB")
remap.color_ramp.elements[0].position=.29;remap.color_ramp.elements[0].color=(.067,.100,.045,1)
remap.color_ramp.elements[1].position=.76;remap.color_ramp.elements[1].color=(.196,.229,.093,1)
rmid=remap.color_ramp.elements.new(.53);rmid.color=(.123,.160,.067,1)
links.new(noise.outputs["Fac"],remap.inputs["Fac"])
bs=n.get("Principled BSDF");links.new(remap.outputs["Color"],bs.inputs["Base Color"])
grit=n.new("ShaderNodeTexNoise");grit.inputs["Scale"].default_value=56
links.new(tc.outputs["Object"],grit.inputs["Vector"])
bump=n.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.27;bump.inputs["Distance"].default_value=.075
links.new(grit.outputs["Fac"],bump.inputs["Height"]);links.new(bump.outputs["Normal"],bs.inputs["Normal"])
crag.data.materials[list(crag.data.materials).index(ridge_material)]=m
root=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
donors={
    "guardrail":"wsc-prop-045-lookout-timber-guardrail.glb",
    "conifer":"wsc-prop-046-conifer-tree.glb","flowers":"wsc-prop-047-wildflower-clump.glb"
}
models={}
from mathutils import Matrix
for k,f in donors.items():
    before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(root/f));bpy.context.view_layer.update()
    new=set(s.objects)-before
    models[k]=[(o.data,o.matrix_world.copy()) for o in sorted(new,key=lambda a:a.name) if o.type=="MESH"]
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
placement=[
 ("conifer",(-201.70,-45.8,16),18,.85),
 ("conifer",(-200.8,-34.85,16),-31,.57),
 ("conifer",(-205.65,-48,16),12,.49),
 ("guardrail",(-198.7,-42.09,16),90,1),
 ("guardrail",(-198.5,-44.38,16),90,1),
 ("guardrail",(-198.7,-37.36,16),90,1),
 ("guardrail",(-198.75,-35.07,16),90,1),
]
for i,(x,y,z) in enumerate([(-208.8,-41.2,16),(-206.7,-41.0,16),(-204.1,-39.2,16),(-202.5,-40.74,16),
                            (-200.8,-38.18,16),(-202.5,-38.1,16),(-201.5,-42.1,16),(-204,-44,16),
                            (-202.35,-44,16),(-199.72,-35.6,16),(-207.3,-37.7,16),(-211.2,-38.29,16)]):
    placement.append(("flowers",(x,y,z),i*47,.64+(i%3)*.13))
for k,p,yaw,scale in placement:
    T=Matrix.Translation(p)@Matrix.Rotation(math.radians(yaw),4,"Z")@Matrix.Scale(scale,4)
    for mesh,matx in models[k]:
        o=bpy.data.objects.new("VISTA staging | "+k,mesh);bpy.context.collection.objects.link(o);o.matrix_world=T@matx
# Broken slab path, a scene dressing motif, not a new asset/download.
stone=bpy.data.materials.new("Vista framing stones");stone.use_nodes=True
q=stone.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(.315,.262,.187,1);q.inputs["Roughness"].default_value=.86
for i in range(8):
    p=(-208.8+i*1.30,-40+.31*math.sin(i*.49)+.07*i,16.020+.002*(i%3))
    bpy.ops.mesh.primitive_cylinder_add(vertices=7,radius=.55,depth=.058,location=p)
    o=bpy.context.object;o.name="VISTA staging | stepping slab";o.scale.y=1.18
    o.rotation_euler.z=.28*i+.16;o.data.materials.append(stone)
    b=o.modifiers.new("Slab edges","BEVEL");b.width=.017;b.segments=2

# Deliberately off-map, layered silhouette cards for the studio framing only.
for level,(x0,base_h,amp,tint) in enumerate([
    (148,9.5,14,(.265,.294,.317)),(196,14,21,(.308,.338,.362)),(255,16,28,(.366,.397,.422))]):
    v=[];faces=[]
    for i in range(177):
        y=-650+i*7.4
        x=x0+3.1*math.sin(.06*y)+2*math.sin(.12*y)
        h=base_h+amp*(.32+.24*math.sin(y*.019+level*1.3)+.14*math.sin(y*.058+level*.8)+.10*math.sin(y*.113))
        v.extend(((x,y,-12),(x,y,h)))
        if i:faces.append((2*i-2,2*i,2*i+1,2*i-1))
    m=bpy.data.meshes.new(f"Vista atmosphere ridge {level}");m.from_pydata(v,[],faces);m.update()
    o=bpy.data.objects.new(m.name,m);bpy.context.collection.objects.link(o)
    ma=bpy.data.materials.new(m.name);ma.use_nodes=True
    nt=ma.node_tree;em=nt.nodes.new("ShaderNodeEmission");em.inputs[0].default_value=(*tint,1)
    em.inputs[1].default_value=.74;nt.links.new(em.outputs[0],nt.nodes.get("Material Output").inputs["Surface"])
    o.data.materials.append(ma);o.visible_shadow=False
# Calm warm afternoon; both views use this same custom lighting.
s.world=bpy.data.worlds.new("W9b dusk edge")
s.world.use_nodes=True
nodes=s.world.node_tree.nodes
bg=nodes.get("Background")
sky=nodes.new("ShaderNodeTexSky");sky.sky_type='NISHITA'
sky.sun_rotation=math.radians(122)
sky.sun_elevation=math.radians(24)
sky.sun_intensity=.75;sky.altitude=.15;sky.air_density=1;sky.dust_density=1.25
s.world.node_tree.links.new(sky.outputs["Color"],bg.inputs[0]);bg.inputs[1].default_value=.22
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(29),math.radians(-30),math.radians(33)))
sun=bpy.context.object;sun.data.energy=1.25;sun.data.color=(1.0,.87,.67);sun.data.angle=.14
s.render.engine="CYCLES";s.cycles.samples=40;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.073
s.render.resolution_x=1440;s.render.resolution_y=890;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
def render(n,eye,target,vertical_shift,lens):
    eye,target=Vector(eye),Vector(target)
    bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object
    s.camera.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler()
    s.camera.data.lens=lens;s.camera.data.shift_y=vertical_shift;s.camera.data.clip_end=800
    s.render.filepath=str(out/n);bpy.ops.render.render(write_still=True)
    return dict(eye_blender_m=list(eye),target_blender_m=list(target),lens_mm=lens,
                horizontal_fov_deg=round(math.degrees(s.camera.data.angle_x),3),frame_shift_y=vertical_shift)
manifest=dict(scope="Candidate Blender camera only; no bench prompt, player snap, discovered flag or runtime camera.",
              source="west-climb-rock/build.py generated climb-rock-editable.blend",bench_glb="WSC-PROP-044",
              bench_bounds_blender_m=bounds,bench_pose_blender_m=list(floor),
              studio_context={k:dict(file=f,sha256=hashlib.sha256((root/f).read_bytes()).hexdigest()) for k,f in donors.items()},
              studio_instance_positions=placement,horizon="Off-map atmosphere silhouettes for render only")
manifest["seated"]=render("nov23-rock-vista-seated.jpg",(-209.84,-40,17.48),(-124,-27,15.7),0,30)
manifest["behind_bench"]=render("nov23-rock-vista-behind.jpg",(-215.5,-42.5,18.75),(-167,-32,15.45),-.105,30)
def world(v):return [v[0],v[2],-v[1]]
for id in ("seated","behind_bench"):
    c=manifest[id]
    for s0 in ("eye","target"):c[s0+"_world_xyz_m"]=world(c[s0+"_blender_m"])
(out/"w9b-rock-vista-camera.json").write_text(json.dumps(manifest,indent=2)+"\n")
