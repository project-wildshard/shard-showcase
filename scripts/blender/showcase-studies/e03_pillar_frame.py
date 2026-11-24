"""Rebuild one Round 5 Band 3 pillar frame; static placement review only."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene,export,output_directory

out=output_directory()
s=bpy.context.scene
clear_scene()


def mat(name,color,metal=0,rough=.5,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    p.inputs["Emission Color"].default_value=(*color,1)
    p.inputs["Emission Strength"].default_value=emission
    return m


cast=mat("Dock gray | precast ash",(.285,.31,.311),.03,.72)
joint=mat("Dock gray | darker cover bands",(.148,.172,.180),.17,.59)
cap=mat("Upper beam | worn ochre",(.49,.205,.042),.43,.45)
pale=mat("Screen | raised gray steel",(.103,.141,.147),.58,.42)
dark=mat("Screen | graphite bedding",(.042,.061,.064),.38,.61)
steel=mat("Fasteners | brushed zinc",(.321,.362,.347),.66,.41)
oxide=mat("Inlaid orange signal marks",(.66,.241,.033),.20,.58)
cyan=mat("Inlaid desaturated cyan",(.053,.532,.512),.28,.36,.15)
slate=mat("Dark porcelain marker",(.031,.049,.056),.12,.66)


class Batch:
    def __init__(self):
        self.p,self.f,self.mi,self.m=[],[],[],[]

    def add(self,p,f,m):
        a=len(self.p)
        self.p.extend(p)
        self.f.extend(tuple(a+j for j in row) for row in f)
        if m not in self.m:
            self.m.append(m)
        self.mi.extend([self.m.index(m)]*len(f))

    def box(self, at, dim, m, chamfer=0, angle=0):
        x,y,z=at
        a,b,c=[q*.5 for q in dim]
        k=min(chamfer,a*.7,b*.7)
        rect=[(a,-b),(a,b),(-a,b),(-a,-b)]
        if k:
            rect=[(a,-b+k),(a,b-k),(a-k,b),(-a+k,b),
                  (-a,b-k),(-a,-b+k),(-a+k,-b),(a-k,-b)]
        n=len(rect)
        ca,sa=math.cos(angle),math.sin(angle)
        p=[(x+u*ca-w*sa,y+v,z+u*sa+w*ca)
           for w in (-c,c) for u,v in rect]
        f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
        f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
        self.add(p,f,m)

    def obj(self,name):
        d=bpy.data.meshes.new(name)
        d.from_pydata(self.p,[],self.f)
        d.update()
        for m in self.m:
            d.materials.append(m)
        for p,mi in zip(d.polygons,self.mi):
            p.material_index=mi
        o=bpy.data.objects.new(name,d)
        s.collection.objects.link(o)
        return o


parts=[]
for x in (-4,4):
    g=Batch()
    # Preserve the archive footprint and top. The face hardware is set
    # into the post rather than changing the original 1.6 m envelope.
    g.box((x,0,3.59),(1.50,1.50,6.82),cast,.066)
    for z,h,material in ((.09,.18,joint),(.37,.18,cast),
                         (2.18,.23,joint),(5.95,.26,joint),
                         (6.80,.27,joint)):
        g.box((x,0,z),(1.60,1.60,h),material,.108)
    for y in (-.758,.758):
        g.box((x,y,1.25),(.54,.037,.95),slate,.011)
        for j in (-1,1):
            for k in range(3):
                g.box((x+j*.114,y+math.copysign(.022,y),1.31+k*.17),
                      (.081,.017,.145),oxide,angle=j*.33)
        g.box((x,y,5.47),(.93,.042,.26),joint,.014)
        for i in range(5):
            g.box((x+(i-2)*.148,y+math.copysign(.026,y),5.47),
                  (.074,.011,.057),cyan,.002)
    parts.append(g.obj(f"Post {x:+.0f}"))

g=Batch()
g.box((0,0,6.70),(9.60,.80,.60),cap,.076)
for side in (-1,1):
    for x in [-2.55,-1.80,1.80,2.55]:
        g.box((x,side*.384,6.70),(.093,.029,.31),oxide,
              angle=-.41 if x<0 else .41)
    g.box((0,side*.389,6.70),(1.12,.023,.44),dark,.005)
    # Block stencil on both sides. Geometry, not a font dependency.
    for dx, pattern in [(-.21,"abcdef"),(.21,"abcdg")]:
        seg={"a":(0,.155,.168,.033),"b":(.09,.08,.033,.126),
             "c":(.09,-.08,.033,.126),"d":(0,-.155,.168,.033),
             "e":(-.09,-.08,.033,.126),"f":(-.09,.08,.033,.126),
             "g":(0,0,.168,.033)}
        for a in pattern:
            px,pz,w,h=seg[a]
            g.box((-side*(dx+px),side*.399,6.70+pz),(w,.010,h),cyan)
parts.append(g.obj("Copper ochre head rail"))

g=Batch()
g.box((0,0,4.2),(7.60,.154,4.0),dark)
for x in [(i-4)*.729 for i in range(9)]:
    g.box((x,0,4.21),(.633,.198,3.75),pale)
    for z in (2.43,5.98):
        g.box((x,0,z),(.37,.199,.083),steel)
for z in (2.24,6.16):
    g.box((0,0,z),(7.60,.200,.080),dark,.019)
parts.append(g.obj("Suspended opaque screen"))

file=out/"e03-pillar-frame.glb"
export(parts,file)
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(file))
module=sorted((o for o in s.objects if o.type=="MESH"),key=lambda o:o.name)
assert len(module)==4
bpy.context.view_layer.update()


def bounds(objs):
    p=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
    return [tuple(round(f(v[i] for v in p),4) for i in range(3))
            for f in (min,max)]


mn,mx=bounds(module)
assert mn==(-4.8,-.8,0) and mx==(4.8,.8,7),(mn,mx)
screen=next(o for o in module if o.name.startswith("Suspended"))
beam=next(o for o in module if o.name.startswith("Copper"))
sb,bb=bounds([screen]),bounds([beam])
assert sb[0][2]==2.2 and sb[1][2]==6.2 and bb[0][2]==6.4,(sb,bb)
ps,fs=[],[]
for o in module:
    c=len(ps)
    ps.extend(o.matrix_world@v.co for v in o.data.vertices)
    fs.extend(tuple(c+i for i in p.vertices) for p in o.data.polygons)
tree=BVHTree.FromPolygons(ps,fs)
for x in (-3.16,-2,0,2,3.16):
    for z,obstructs in ((1.7,False),(2.195,False),(2.205,True),
                        (3.95,True),(6.28,False),(6.45,True)):
        hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
        assert (hit is not None)==obstructs,(x,z,hit)
assert tree.ray_cast(Vector((4,-2,1.7)),Vector((0,1,0)),4)[0] is not None

origin=Vector((138.638,221.816,0))
entrance=Vector((122,224,1.7))
yaw=3.28656
pose=Matrix.Translation(origin)@Matrix.Rotation(yaw,4,"Z")
for o in module:
    o.matrix_world=pose@o.matrix_world
dist=(origin.xy-entrance.xy).length
assert 16.77<dist<16.79
assert file.stat().st_size<120000
receipt={
    "archive":"Raynos/project-wildshard-singleplayer@ce1cf050b3, Round 5",
    "cover_kind":"pillars", "band":3,
    "archive_origin_xz":[138.638,-221.816],
    "archive_entry_xz":[122,-224],
    "yaw_radians":yaw, "ground_distance_m":round(dist,4),
    "module_bounds_m":[mn,mx],
    "screen_bounds_m":sb, "cap_bounds_m":bb,
    "screen_floor_clearance_m":2.2, "screen_cap_slot_m":.2,
    "test":"GLB reimport, clear/block visual rays, static staging only",
    "triangles":sum(len(p.vertices)-2 for o in module for p in o.data.polygons),
    "bytes":file.stat().st_size, "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
}
(out/"e03-pillar-frame.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("PILLAR_RECEIPT",json.dumps(receipt),flush=True)

# Editorial context only. Borrow the E03 pale dock paving colors, not
# an imagined reconstruction of surrounding Round 5 placements.
stage=[
    mat("Pale apron | fogged limestone",(.356,.313,.227),.01,.88),
    mat("Pale apron | darker stone",(.306,.268,.197),.01,.85),
    mat("Pale apron | sun-worn stone",(.397,.346,.258),.01,.90),
    mat("Pale apron | fourth stone",(.344,.290,.219),.01,.85),
]
sand=mat("Flat dusty surround",(.258,.228,.176),.0,.92)
paint=mat("Faded cream apron lines",(.676,.583,.410),.07,.81)
g=Batch()
g.box((0,0,-.143),(160,160,.19),sand)
rng=random.Random(3)
for i in range(-11,12):
    for j in range(-12,8):
        z=-.016
        g.box((i*2.00+(j%2)*.994,j*1.0,z),
              (1.985,.983,.032),rng.choice(stage),.025)
for k in range(-14,9):
    if k%3!=0:
        g.box((-2.85,k+.5,.005),(.055,.48,.01),paint)
        g.box((2.85,k+.5,.005),(.055,.48,.01),paint)
g.obj("Provisional limestone review apron").matrix_world=pose
assets=HERE.parents[2]/"public/assets/wildshard-art"
donors={
    "wsc-prop-053-robot-dock.glb":"24550d532c55a98de78abd2df3c1adde9885554242e2be7ecff625ecb9ddafac",
    "wsc-prop-056-plant-pot.glb":"17ecd61ec7a0169370fc708f4879df210bcec4eeeb2a57ad0b73c821234e8c09",
}
for name,digest in donors.items():
    assert hashlib.sha256((assets/name).read_bytes()).hexdigest()==digest
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/name))
    bpy.context.view_layer.update()
    objs=set(s.objects)-before
    mn,mx=bounds(objs)
    x,y=(-7.5,4.5) if "dock" in name else (6.6,2.6)
    xf=pose@Matrix.Translation((x-(mn[0]+mx[0])/2,y-(mn[1]+mx[1])/2,-mn[2]))
    for o in sorted(objs,key=lambda o:o.name):
        if o.parent not in objs:
            o.matrix_world=xf@o.matrix_world
receipt["editorial_donors_sha256"]=donors
(out/"e03-pillar-frame.json").write_text(json.dumps(receipt,indent=2)+"\n")


def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()


world=bpy.data.worlds.new("Pale inland sky")
s.world=world
world.use_nodes=True
nd=world.node_tree.nodes
sky=nd.new("ShaderNodeTexSky")
sky.sky_type="HOSEK_WILKIE"
sky.sun_direction=Vector((-.52,-.42,.743)).normalized()
sky.turbidity=2.45
sky.ground_albedo=.35
world.node_tree.links.new(sky.outputs["Color"],nd["Background"].inputs["Color"])
nd["Background"].inputs["Strength"].default_value=.35
light=bpy.data.lights.new("Late dock daylight","SUN")
light.energy=2.45
light.color=(1,.83,.64)
light.angle=.034
key=bpy.data.objects.new(light.name,light)
s.collection.objects.link(key)
key.location=pose@Vector((4,-6,6))
aim(key,origin)
cd=bpy.data.cameras.new("E03")
camera=bpy.data.objects.new("E03",cd)
s.collection.objects.link(camera)
s.camera=camera
s.render.engine="CYCLES"
s.cycles.samples=50
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.045
s.view_settings.view_transform="AgX"
s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG"
s.render.image_settings.quality=91


def render(name,p,at,res,angle):
    camera.location=p
    aim(camera,at)
    cd.sensor_fit="VERTICAL"
    cd.lens=cd.sensor_height/(2*math.tan(math.radians(angle)/2))
    s.render.resolution_x,s.render.resolution_y=res
    bpy.context.view_layer.update()
    projected=[world_to_camera_view(s,camera,o.matrix_world@v.co)
               for o in module for v in o.data.vertices]
    pb=[[round(f(q[i] for q in projected),4) for i in (0,1)] for f in (min,max)]
    assert min(pb[0])>.015 and max(pb[1])<.985,(name,pb)
    receipt[name]={"projection_fraction":pb,"width_height_px":res,"vertical_fov_deg":angle}
    s.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)


render("nov24-e03-pillar-entry",entrance,pose@Vector((0,0,2.95)),(810,1296),55)
render("nov24-e03-pillar-context",pose@Vector((7,-13,3.0)),
       pose@Vector((0,0,3.14)),(1430,895),40)
(out/"e03-pillar-frame.json").write_text(json.dumps(receipt,indent=2)+"\n")
