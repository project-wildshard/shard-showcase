"""E7b reusable night-shift visual pieces. No species, spawn or light behavior."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out = output_directory()
scene = bpy.context.scene
clear_scene()


def material(name, rgb, metallic=0.0, rough=.53):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value=(*rgb,1)
    p.inputs["Metallic"].default_value=metallic;p.inputs["Roughness"].default_value=rough
    return m


def box(name,pos,dim,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new("Readable bevel","BEVEL");m.width=bevel;m.segments=1
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def mesh(name,v,f,m):
    data=bpy.data.meshes.new(name);data.from_pydata(v,[],f);data.update()
    data.materials.append(m);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o)
    return o


def inspect(path):
    raw=path.read_bytes()
    magic,version,size=struct.unpack_from("<4sII",raw)
    assert (magic,version,size)==(b"glTF",2,len(raw))
    d=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    assert not any(k in d for k in ("animations","skins","images"))
    t=sum(d["accessors"][x["indices"]]["count"]//3 for m in d["meshes"] for x in m["primitives"])
    return {"triangles":t,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()},d


# Two cards share the centreline. Leave the opening and end unloaded; both
# the edge and far falloff carry alpha in COLOR_0. In glTF the light faces -Z.
beam_path=out/"e7b-headlamp-beam.glb"
rings=[(0,.075,.0),(.12,.096,.25),(.56,.139,.19),(1.34,.244,.10),
       (2.14,.352,.034),(2.72,.409,0)]
vertices=[]; rgba=[]; idx=[]
for a in (0,math.pi/2):
    off=len(vertices)
    for distance,width,alpha in rings:
        for k in (-1,-.47,0,.47,1):
            vertices.append((k*width*math.cos(a),k*width*math.sin(a),-distance))
            rgba.append((1.0,.54,.112,alpha*(1-abs(k))**1.33))
    for j in range(len(rings)-1):
        for k in range(4):
            p=off+j*5+k
            idx.extend((p,p+1,p+6,p,p+6,p+5))
positions=b"".join(struct.pack("<3f",*v) for v in vertices)
colors=b"".join(struct.pack("<4f",*c) for c in rgba)
indexes=struct.pack("<"+"H"*len(idx),*idx)
binary=positions+colors+indexes
sections=[positions,colors,indexes]
views=[];p=0
for content,target in zip(sections,(34962,34962,34963),strict=True):
    views.append({"buffer":0,"byteOffset":p,"byteLength":len(content),"target":target})
    p+=len(content)
doc={
    "asset":{"version":"2.0","generator":"Wildshard E7b recipe"},
    "extensionsUsed":["KHR_materials_unlit"],
    "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0,"name":"E7b beam | forward -Z"}],
    "meshes":[{"primitives":[{"attributes":{"POSITION":0,"COLOR_0":1},"indices":2,"material":0}]}],
    "materials":[{"name":"Amber coverage | additive at Three runtime",
                  "alphaMode":"BLEND","doubleSided":True,"extensions":{"KHR_materials_unlit":{}}}],
    "bufferViews":views,
    "accessors":[
        {"bufferView":0,"componentType":5126,"count":len(vertices),"type":"VEC3",
         "min":[min(v[i] for v in vertices) for i in range(3)],
         "max":[max(v[i] for v in vertices) for i in range(3)]},
        {"bufferView":1,"componentType":5126,"count":len(rgba),"type":"VEC4"},
        {"bufferView":2,"componentType":5123,"count":len(idx),"type":"SCALAR"}],
    "buffers":[{"byteLength":len(binary)}],
}
raw=json.dumps(doc,separators=(",",":")).encode()
raw+=b" "*(-len(raw)%4)
assert len(binary)%4==0
beam_path.write_bytes(struct.pack("<4sIIII",b"glTF",2,28+len(raw)+len(binary),len(raw),0x4e4f534a)
                      +raw+struct.pack("<II",len(binary),0x004e4942)+binary)
beam_proof,d=inspect(beam_path)
assert beam_proof["triangles"]==80 and beam_proof["bytes"]<8192
assert d["materials"][0]["alphaMode"]=="BLEND"
assert max(x[3] for x in rgba)==.25 and all(x[3]==0 for x in rgba[-5:])

iron=material("Cold enamel",(.052,.078,.091),.38)
brass=material("Oxide edge",(.303,.139,.048),.56)
black=material("Non reflective graphite",(.014,.025,.031),.12)
yellow=material("Amber safety enamel",(.57,.278,.042),.16,.43)
badge=[box("Night chevron mount",(0,0,0),(.42,.06,.25),iron,.022),
       box("Brass gasket",(0,-.03,0),(.382,.028,.213),brass,.018),
       box("Graphite inset",(0,-.047,0),(.346,.021,.175),black,.012)]
for x in (-.088,0,.088):
    path=[(-.034,-.055),(-.006,-.055),(.029,0),(-.006,.055),(-.034,.055),(.001,0)]
    v=[(u+x,-.059,z) for u,z in path]
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(path,path[1:]+path[:1]))
    if area<0:v.reverse()
    badge.append(mesh("Enamel chevron",v,[tuple(range(len(v)))],yellow))
bpy.ops.object.select_all(action="DESELECT")
for o in badge:o.select_set(True)
bpy.context.view_layer.objects.active=badge[0]
bpy.ops.object.join()
obj=bpy.context.object;obj.name=obj.data.name="Night shift chevrons | cosmetic"
badge_path=out/"e7b-hi-vis-chevron.glb"
bpy.ops.export_scene.gltf(filepath=str(badge_path),export_format="GLB",
                         use_selection=True,export_texcoords=False,export_animations=False)
badge_proof,_=inspect(badge_path)
assert badge_proof["bytes"]<16384
clear_scene()
for path in (beam_path,badge_path):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported,=[o for o in scene.objects if o not in prior and o.type=="MESH"]
    imported.data.calc_loop_triangles()
    assert len(imported.data.loop_triangles)==inspect(path)[0]["triangles"]
    if path==beam_path:beam=imported
    else:panel=imported
assert beam.data.color_attributes.active_color is not None
assert beam.location.length<.0001 and panel.location.length<.0001
assert abs(beam.dimensions.y-2.72)<.0001
(out/"e7b-night-shift-vfx.json").write_text(json.dumps({
    "scope":"visual components only; not a new enemy, native lighting or behavior",
    "source":"E7b night-shift look and E1a cosmetic palette slots",
    "beam":{**beam_proof,"length_m":2.72,"gltf_forward":"-Z","gltf_alpha":"BLEND",
            "Three_material_override":"AdditiveBlending with depthWrite false and depthTest true"},
    "chevron":badge_proof,
},indent=2)+"\n")

if os.getenv("WILDSHARD_VALIDATE_ONLY") != "1":
    beam.location=(0,-.312,.83)
    bpy.context.view_layer.update()
    def beam_y():
        return [(beam.matrix_world @ Vector(v)).y for v in beam.bound_box]
    if max(beam_y()) > beam.location.y + 1:
        pivot = beam.location.copy()
        beam.matrix_world = (Matrix.Translation(pivot) @ Matrix.Rotation(math.pi, 4, "Z")
                             @ Matrix.Translation(-pivot) @ beam.matrix_world)
        bpy.context.view_layer.update()
    assert min(beam_y()) < -3.0 and max(beam_y()) < -.30, beam_y()
    panel.location=(0,-.277,.50)
    # The Blender poster is a visibility proof, with beam emission gated to
    # camera rays. It adds no lighting or shadow to the props or ground.
    bm=material("Camera-only beam",(.9,.46,.08))
    ns=bm.node_tree.nodes; wires=bm.node_tree.links;ns.clear()
    surface=ns.new("ShaderNodeOutputMaterial");light_path=ns.new("ShaderNodeLightPath")
    vertex=ns.new("ShaderNodeVertexColor")
    vertex.layer_name=beam.data.color_attributes.active_color.name
    transparent=ns.new("ShaderNodeBsdfTransparent")
    glow=ns.new("ShaderNodeEmission");glow.inputs["Strength"].default_value=1.65
    mask=ns.new("ShaderNodeMath");mask.operation="MULTIPLY"
    mix=ns.new("ShaderNodeMixShader")
    wires.new(vertex.outputs["Color"],glow.inputs["Color"])
    wires.new(vertex.outputs["Alpha"],mask.inputs[0]);wires.new(light_path.outputs["Is Camera Ray"],mask.inputs[1])
    wires.new(mask.outputs[0],mix.inputs[0]);wires.new(transparent.outputs[0],mix.inputs[1]);wires.new(glow.outputs[0],mix.inputs[2])
    wires.new(mix.outputs[0],surface.inputs["Surface"])
    beam.data.materials.clear();beam.data.materials.append(bm)
    slate=material("Test stand slate",(.049,.078,.09),.15)
    base=material("Pale slate witness cards",(.105,.149,.158),.02,.71)
    box("Studio ground",(0,0,-.105),(150,150,.21),slate)
    box("Neutral fixture holder",(0,0,.64),(.62,.5,1.28),slate,.038)
    box("Witness card before fade",(.27,-2.25,.36),(.54,.10,.74),base,.01)
    box("Witness card beyond fade",(.27,-3.24,.36),(.54,.10,.74),base,.01)
    for z in (.02,.03):
        box("Witness alignment rail",(0,-1.75,z),(.038,3.1,.004),black)
    box("Lamp socket surrogate",(0,-.265,.83),(.16,.065,.11),brass,.014)
    box("Amber socket lens",(0,-.301,.83),(.115,.014,.069),
        material("Socket lens",(.64,.32,.08)),.010)

    def aim(o,p):
        o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()

    for n,p,t,e,s,c in [
        ("Frost fill",(-2.2,-3.6,3.2),(0,-1.3,.7),255,3.1,(.41,.68,1)),
        ("Fixture amber rim",(2.25,.25,3.7),(0,0,.65),300,2.2,(1,.69,.40)),
        ("Slate witness soft box",(2.8,-2.7,3.1),(.2,-2.4,.4),140,2.9,(.63,.77,.94)),
    ]:
        d=bpy.data.lights.new(n,"AREA");o=bpy.data.objects.new(n,d)
        d.energy,d.size,d.color=e,s,c;scene.collection.objects.link(o);o.location=p;aim(o,t)
    scene.world=bpy.data.worlds.new("Fixture winter sky")
    scene.world.color=(.035,.059,.106)
    d=bpy.data.cameras.new("Night shift proof")
    c=bpy.data.objects.new(d.name,d);scene.collection.objects.link(c);scene.camera=c
    d.type="ORTHO";scene.render.engine="CYCLES"
    scene.cycles.samples=44;scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=91
    for tag,at,to,scale,w,h in [
        ("beam",(4.9,-4.55,2.9),(0,-1.64,.61),4.65,1440,905),
        ("badge",(1.6,-3.9,1.52),(0,-.272,.58),1.05,1140,850),
    ]:
        c.location=at;aim(c,to);d.ortho_scale=scale
        beam.hide_render=tag=="badge"
        scene.render.resolution_x=w;scene.render.resolution_y=h
        scene.render.filepath=str(out/f"nov24-e7b-night-{tag}.jpg")
        bpy.ops.render.render(write_still=True)
