"""Optional East seam direction signs, with two eye-level fits to the W0a study."""
import bpy, hashlib, json, math, struct, sys
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index("--")+1]);out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[3]
assets=root/"public/assets/wildshard-art"
pins=json.loads((root/"project/layouts/w0a-east-gate-boundary-donors.json").read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene

def mat(n,c,metal=0,rough=.59):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    node=m.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value=(*c,1);node.inputs["Metallic"].default_value=metal
    node.inputs["Roughness"].default_value=rough
    return m

def box(n,p,d,m,b=.008):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        q=o.modifiers.new("Edge break","BEVEL");q.width=b;q.segments=1
        bpy.ops.object.modifier_apply(modifier=q.name)
    return o

def text(n,body,x,z,size,m):
    d=bpy.data.curves.new(n,"FONT");d.body=body;d.align_x="CENTER";d.align_y="CENTER"
    d.size=size;d.resolution_u=3;d.extrude=0;d.materials.append(m)
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=(x,-.084,z)
    o.rotation_euler.x=math.pi/2;bpy.context.view_layer.update();return o

def select(obs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]

def flatten(n,obs):
    select(obs);bpy.ops.object.convert(target="MESH");bpy.ops.object.join()
    o=bpy.context.object;o.name=n;bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return o

petrol=mat("Oil-dark iron",(.031,.078,.080),.52)
bronze=mat("Weathered brass",(.31,.173,.062),.58,.41)
cream=mat("Cream enamel",(.76,.62,.39),.05,.42)
gray=mat("Chalk inlay",(.80,.78,.63),.06,.44)
teal=mat("Brasswick blue enamel",(.026,.165,.171),.12,.46)
ochre=mat("Yard ochre enamel",(.72,.32,.057),.08,.46)
oak=mat("End grain oak",(.196,.102,.042),0,.85)
asphalt=mat("East approach paving",(.11,.105,.097),0,.91)
clay=mat("East approach shoulder",(.23,.132,.072),0,.94)
paving=mat("Limestone approach",(.34,.264,.169),0,.91)
variants=[
    ("yard","EAST YARD","CHARGE LANES",ochre,petrol),
    ("return","BRASSWICK","BACK TO TOWN",teal,gray),
]
exports={}
for key,title,subtitle,accent,ink in variants:
    old=set(s.objects)
    frame=[box("Stone shoe",(0,0,.046),(.62,.34,.092),bronze,.022),
           box("Oak upright",(0,.052,.84),(.14,.13,1.60),oak,.013),
           box("Base shoe",(0,.05,.19),(.212,.186,.245),petrol,.013),
           box("Enamel frame",(0,0,1.63),(1.56,.126,.57),petrol,.022),
           box("Inset panel",(0,-.068,1.63),(1.485,.023,.505),cream,.014),
           box("Route crest",(-.568,-.081,1.63),(.275,.018,.443),accent,.011),
           box("Subheading underline",(.14,-.081,1.591),(1.02,.012,.009),bronze,.002)]
    me=bpy.data.meshes.new("Direction chevron")
    q=[(-.662,1.648),(-.568,1.762),(-.474,1.648),(-.512,1.648),(-.568,1.715),(-.624,1.648)]
    me.from_pydata([(x,-.093,z) for x,z in q],[],[tuple(reversed(range(len(q))))])
    me.materials.append(ink);arr=bpy.data.objects.new("Route arrow",me);s.collection.objects.link(arr)
    details=[arr,text("Main enamel lettering",title,.147,1.702,.178,petrol),
             text("Secondary enamel lettering",subtitle,.147,1.500,.083,petrol)]
    assert details[1].dimensions.x<1.06 and details[2].dimensions.x<1.04
    for x in (-.718,.718):
        for z in (1.428,1.832):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.018,depth=.014,location=(x,-.086,z),rotation=(math.pi/2,0,0))
            o=bpy.context.object;o.name="Panel pin";o.data.materials.append(bronze);frame.append(o)
    o=flatten("ThresholdDirection_"+key,frame+details)
    select([o]);p=out/f"w0a-east-direction-{key}.glb"
    bpy.ops.export_scene.gltf(filepath=str(p),export_format="GLB",use_selection=True,export_animations=False)
    b=p.read_bytes();j=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    tris=sum(j["accessors"][q["indices"]]["count"]//3 for m in j["meshes"] for q in m["primitives"])
    assert not j.get("textures") and tris<3000 and len(b)<160000
    exports[key]=dict(file=p.name,bytes=len(b),triangles=tris,sha256=hashlib.sha256(b).hexdigest())
    for o in list(set(s.objects)-old):bpy.data.objects.remove(o,do_unlink=True)

def import_mesh(p):
    before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    items=sorted(set(s.objects)-before,key=lambda o:o.name)
    data=[(o.data,o.matrix_world.copy()) for o in items if o.type=="MESH"]
    for o in items:bpy.data.objects.remove(o,do_unlink=True)
    return data

def yaw(p,z=0,scale=1):
    return Matrix.Translation(p)@Matrix.Rotation(z,4,"Z")@Matrix.Scale(scale,4)

def place(mesh,n,tr):
    ans=[]
    for d,tf in mesh:
        o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.matrix_world=tr@tf;ans.append(o)
    return ans

def loadpin(k):
    pin=pins[k];p=assets/pin["file"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==pin["sha256"]
    return import_mesh(p)

data={k:loadpin(k) for k in ("span","tower","bay","post","leaf","banner","planter","lantern","cone")}
def remodel(p,d,w,h):
    return Matrix(((0,-d,0,p[0]),(w,0,0,p[1]),(0,0,h,p[2]),(0,0,0,1)))
host=place(data["span"],"Existing lintel",remodel((-8,0,6.245),.67,1.78,.236))
for side in (-1,1):
    host+=place(data["tower"],"Existing masonry tower",remodel((-8,side*7.84,0),.65,.94,7.19/5.275))
    for j in range(4):
        host+=place(data["bay"],"Existing industrial bay",yaw((0,side*(8.12+j*3.595),0),math.pi/2))
    host+=place(data["post"],"Existing seam post",yaw((0,side*6.73,0),math.pi/2))
    host+=place(data["leaf"],"Existing open seam leaf",yaw((1.42,side*6.73,0),0 if side>0 else math.pi))
    place(data["banner"],"Heraldry",yaw((-9.75,side*8.36,2.13),-math.pi/2,.74))
    place(data["planter"],"Planter",yaw((-12.2,side*8.1,0),math.pi/2,.84))
    place(data["lantern"],"Masonry lamp",yaw((-9.94,side*6.61,3.14),-math.pi/2,.62))
# Exact threshold in Blender study coordinates. Ground and decorative lines are context.
box("Ground",(0,0,-.18),(90,54,.28),clay,0)
box("West paving",(-25.5,0,-.045),(51,20,.09),paving,0)
box("East asphalt",(25,0,-.045),(50,12.5,.09),asphalt,0)
for i in range(12):
    for side in (-1,1):
        box("West pale floor accents",(-1.75-1.48*i,side*3.55,.004),(1.23,.24,.008),cream,0)
for i in range(12):box("Center stripe",(2.5+2.8*i,0,.004),(1.16,.095,.008),cream,0)
for side in (-1,1):
    box("East edge",(24,side*5.95,.004),(44,.095,.008),ochre,0)
    for x in (9,17):place(data["cone"],"Safety cone",yaw((x,side*5.2,0),x,.80))

def tree(obs):
    vertices=[];faces=[]
    for o in obs:
        off=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vertices,faces,all_triangles=False)
# One board on each side of the seam; their fronts face the approaching player.
fits=[
    ("yard",(-3.2,-6.82,0),-math.pi/2),
    ("return",(4.4,-6.82,0),math.pi/2),
]
host_bvh=tree(host)
proof={}
boards=[]
for key,p,r in fits:
    mesh=import_mesh(out/exports[key]["file"]);tr=yaw(p,r)
    obs=place(mesh,"Direction board "+key,tr);boards+=obs
    bvh=tree(obs)
    assert not bvh.overlap(host_bvh),key
    heights=[.25,.8,1.7,2.4]
    # Sample central passage at the same width as W0a; no dressing intrusions.
    points=0
    for z in heights:
        for k in range(-12,13):
            assert bvh.ray_cast(Vector((-20,k*.49,z)),Vector((1,0,0)),40)[0] is None
            points+=1
    candidates=0
    safe=0
    for dist in (6,9,11):
        for y in (-2,-1,0,1,2):
            for h in (1.48,1.7,1.83):
                pos=Vector((p[0]+dist*(-1 if key=="yard" else 1),y,h))
                for lx in (-.52,0,.58):
                    dst=tr@Vector((lx,-.093,1.70));delta=dst-pos
                    candidates+=1
                    if host_bvh.ray_cast(pos,delta.normalized(),delta.length-.001)[0] is None:safe+=1
    proof[key]=dict(stage_three_xyz=[p[0],p[2],-p[1]],yaw_degrees=math.degrees(r),
        samples_clear=safe,samples_total=candidates,passage_samples_clear=points,
        nearest_centerline_m=round(min(abs((o.matrix_world@v.co).y) for o in obs for v in o.data.vertices),4))
    assert safe==candidates,(key,safe,candidates)
    assert proof[key]["nearest_centerline_m"]>5.8
(out/"w0a-east-threshold-direction-proof.json").write_text(json.dumps(dict(
    scope="Optional W0a art fit; no installation, final map coordinates, collision or quest behavior.",
    pinned_donors={k:pins[k] for k in data},exports=exports,review=proof,
),indent=2)+"\n")
if "--no-render" in sys.argv:raise SystemExit(0)
world=bpy.data.worlds.new("Hazy morning");world.use_nodes=True
nodes=world.node_tree.nodes;links=world.node_tree.links
sky=nodes.new("ShaderNodeTexSky");sky.sky_type="NISHITA"
sky.sun_elevation=math.radians(38);sky.sun_rotation=math.radians(236);sky.sun_size=math.radians(2.3)
links.new(sky.outputs[0],nodes["Background"].inputs[0]);nodes["Background"].inputs[1].default_value=.24
s.world=world;s.render.engine="CYCLES";s.cycles.samples=22;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
c=bpy.data.cameras.new("Portrait review");cam=bpy.data.objects.new("Portrait review",c);s.collection.objects.link(cam);s.camera=cam
s.render.resolution_x=810;s.render.resolution_y=1120;s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
for key,p,r in fits:
    eye=(p[0]+(-5.6 if key=="yard" else 5.6),-3.20,1.70)
    at=(p[0]+(.85 if key=="yard" else -.85),-5.95,1.98)
    cam.location=eye;cam.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat("-Z","Y").to_euler()
    c.lens=31
    s.render.filepath=str(out/("nov26-east-threshold-"+key+".png"));bpy.ops.render.render(write_still=True)
