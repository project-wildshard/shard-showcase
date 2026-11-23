"""Three actual rig reimports on identical stages; no runtime/animation claims."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out=output_directory()
clear_scene()

def matte(name, c, rough=.73, glow=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Roughness"].default_value=rough
    n.inputs["Emission Color"].default_value=(*c,1)
    n.inputs["Emission Strength"].default_value=glow
    return m

base=matte("Charcoal museum slate",(.060,.070,.066))
room=matte("Deep moss studio",(.023,.030,.025),.88)
key=matte("Linen display ink",(.86,.76,.59),.75,.27)
gold=matte("Brass display ink",(.81,.48,.16),.75,.29)

def aim(o, p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()

def label(value,size,xyz,mat):
    c=bpy.data.curves.new(value,"FONT");c.body=value;c.align_x="CENTER";c.size=size
    ob=bpy.data.objects.new(value,c);bpy.context.collection.objects.link(ob)
    ob.location=xyz;ob.rotation_euler.x=math.radians(37)
    c.materials.append(mat)

reference=None
for x, slug, caption in [
    (-2.95,"donor","01  /  NALATI ORIGINAL"),
    (0,"amber-bay","02  /  AMBER BAY"),
    (2.95,"winter-dun","03  /  WINTER DUN"),
]:
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/f"{slug}-preview.glb"))
    added=set(bpy.context.scene.objects)-before
    arm,=[o for o in added if o.type=="ARMATURE"]
    mesh,=[o for o in added if o.type=="MESH" and o.vertex_groups]
    assert len(arm.data.bones)==24 and len(mesh.vertex_groups)==24
    mesh.data.calc_loop_triangles()
    assert len(mesh.data.loop_triangles)==5000 and not mesh.animation_data
    counts=tuple(sum(any(g.group==v.index and g.weight>0 for g in vertex.groups) for vertex in mesh.data.vertices)
                 for v in mesh.vertex_groups)
    data=(tuple(b.name for b in arm.data.bones), counts)
    if reference is not None: assert data==reference
    reference=data
    bpy.context.view_layer.update()
    coords=[mesh.matrix_world@v.co for v in mesh.data.vertices]
    lo=Vector([min(v[k] for v in coords) for k in range(3)])
    hi=Vector([max(v[k] for v in coords) for k in range(3)])
    cent=(lo+hi)/2;cent.z=lo.z
    placement=Matrix.Translation((x,.19,.013))@Matrix.Rotation(math.radians(-55),4,"Z")@Matrix.Translation(-cent)
    for o in added:
        if o.parent not in added: o.matrix_world=placement@o.matrix_world
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,.02,-.071))
    slab=bpy.context.object;slab.dimensions=(2.72,2.2,.14)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    slab.data.materials.append(base)
    mod=slab.modifiers.new("Rounded slab edge","BEVEL");mod.width=.025;mod.segments=2
    label(caption,.145,(x,-1.04,.052), gold if slug=="amber-bay" else key)
    print(f"{slug}: {len(mesh.data.vertices)} verts, {len(mesh.data.loop_triangles)} tris, 24 bones; dimensions {(hi-lo)[:]}")

label("WEST PADDOCK  /  BISCUIT",.32,(0,2.60,1.29),key)
label("WSC-ACTOR-019      •      COAT LOOK STUDY",.151,(0,2.38,1.07),gold)
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-.145))
bpy.context.object.data.materials.append(room)
s=bpy.context.scene;s.world.color=(.17,.17,.16)
for pos,power,size,color in [((-3,-5,7),1550,6,(1,.84,.66)),((5,-3,6),930,7,(.75,.87,1)),((0,5,6),1520,7,(1,.80,.55))]:
    bpy.ops.object.light_add(type="AREA",location=pos)
    l=bpy.context.object;l.data.energy=power;l.data.shape="DISK";l.data.size=size;l.data.color=color;aim(l,(0,0,.65))
bpy.ops.object.camera_add(location=(0,-8,7.3))
s.camera=bpy.context.object;aim(s.camera,(0,0,.90))
s.camera.data.type="ORTHO";s.camera.data.ortho_scale=9.35
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1640;s.render.resolution_y=825;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=89
s.render.filepath=str(out/"nov23-biscuit-coat-board.jpg")
bpy.ops.render.render(write_still=True)
