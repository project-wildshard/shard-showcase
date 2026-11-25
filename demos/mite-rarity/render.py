"""Compare the unchanged yard rig and two material presets in matched light."""
from hashlib import sha256
import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2]
base=root/"public/assets/wildshard-art/wsc-actor-001-crate-mite-rig-yard.glb"
palette=json.loads(Path(__file__).with_name("palette.json").read_text())
assert sha256(base.read_bytes()).hexdigest()==palette["sourceSha256"]
out=Path(sys.argv[sys.argv.index("--")+1]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
for x,patch in zip((-1.36,0,1.36),[{},*palette["variants"].values()]):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(base))
    bpy.context.view_layer.update()
    group=sorted(set(scene.objects)-before,key=lambda o:o.name)
    rig=next(o for o in group if o.type=="ARMATURE")
    rig.data.pose_position='REST'
    assert len(rig.data.bones)==7
    touched=set()
    for obj in group:
        if obj.parent not in group:
            obj.matrix_world=Matrix.Translation((x,0,0))@obj.matrix_world
        if obj.type!="MESH": continue
        for slot in obj.material_slots:
            key=slot.material.name.split('.')[0]
            if key not in patch:continue
            m=slot.material.copy()
            node=m.node_tree.nodes.get('Principled BSDF')
            color,metal,rough=patch[key]
            node.inputs['Base Color'].default_value=color
            node.inputs['Metallic'].default_value=metal
            node.inputs['Roughness'].default_value=rough
            m.diffuse_color=color
            slot.material=m
            touched.add(key)
    assert touched==set(patch)
    bpy.context.view_layer.update()

def mat(n,c,r,met=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Roughness"].default_value=r
    q.inputs["Metallic"].default_value=met
    return m
stone=mat("Warm industrial road mesh",(.137,.148,.15),.83)
edge=mat("Steel studio guide",(.24,.246,.234),.61,.49)
def box(n,at,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.data.materials.append(m)
box("Ground for shadow reference",(0,0,-.055),(160,160,.1),stone)
for x in (-2.04,-.68,.68,2.04):
    box("Thin aisle separator",(x,0,.001),(.015,1.48,.002),edge)
scene.world=bpy.data.worlds.new("Shed daylight")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.37,.46,.57,1)
bg.inputs[1].default_value=.67

def panel(kind,p,q,e,size,c):
    bpy.ops.object.light_add(type=kind,location=p)
    o=bpy.context.object
    o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.energy=e;o.data.color=c
    if kind=="SUN":o.data.angle=size
    else:o.data.shape='DISK';o.data.size=size
panel('SUN',(-6,-3,7),(0,0,0),2.65,.15,(1,.85,.69))
panel('AREA',(1.2,2.5,3),(0,0,.42),580,4,(.50,.73,1))
panel('AREA',(-.2,-3.6,2.7),(0,0,.44),95,3,(1,.96,.86))
scene.render.engine='CYCLES';scene.cycles.samples=38;scene.cycles.adaptive_threshold=.034
scene.cycles.use_denoising=False
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=94;scene.view_settings.view_transform='AgX'
bpy.ops.object.camera_add()
cam=bpy.context.object;scene.camera=cam
def shot(name,eye,aim,lens,w,h,fit):
    cam.location=eye;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.sensor_fit=fit;cam.data.sensor_height=24;cam.data.lens=lens
    scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+'.jpg'));bpy.ops.render.render(write_still=True)
shot('nov25-e7a-mite-finishes',(.08,-5.15,2.20),(0,0,.39),44,1480,760,'HORIZONTAL')
shot('nov25-e7a-mite-10m',(0,-10,1.70),(0,0,.43),12/math.tan(math.radians(40)),402,874,'VERTICAL')
