"""E8d display only: Warden's Plate and Titan's Core, staged in the existing frames."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory

out=output_directory()
clear_scene()
scene=bpy.context.scene
donor=HERE.parents[2]/"public/assets/wildshard-art/west-plaza-empty-mounts.glb"
donor_sha="3e7e28863742ebcdd2f494d97d98574d263d876dac01f03e21a2b0fd5b4a54c7"
assert hashlib.sha256(donor.read_bytes()).hexdigest()==donor_sha


def mat(name,c,m=0,r=.43,e=0):
    a=bpy.data.materials.new(name)
    a.diffuse_color=(*c,1);a.use_nodes=True
    bs=a.node_tree.nodes.get("Principled BSDF")
    for key,val in {"Base Color":(*c,1),"Metallic":m,"Roughness":r,
                    "Emission Color":(*c,1),"Emission Strength":e}.items():
        bs.inputs[key].default_value=val
    return a


steel=mat("Heat-blued Warden plate",(.051,.078,.091),.68)
brush=mat("Forged raised latches",(.171,.196,.212),.70,.33)
edge=mat("Bronze bolt and seam",(.45,.229,.093),.64)
deep=mat("Stamped recess",(.019,.031,.036),.4,.52)
signal=mat("Small Warden tell",(.026,.411,.48),.2,.38,.45)
orange=mat("Titan cargo enamel",(.68,.181,.030),.31)
gray=mat("Titan cargo iron",(.13,.164,.167),.55)
rim=mat("Titan core retaining lip",(.039,.318,.315),.49,.32)
light=mat("Titan exposed cyan core",(.019,.69,.82),.1,.28,1.30)
cool=mat("Titan inner glass facet",(.175,.80,.83),.11,.27,.80)
shadow=mat("Locked display silhouette",(.034,.044,.046),.03,.88)
plaster=mat("West gallery warm stone",(.37,.281,.182),0,.78)


def rect(x,z,w,h,c):
    a,b=w*.5,h*.5
    return [(x-a+c,z-b),(x+a-c,z-b),(x+a,z-b+c),(x+a,z+b-c),
            (x+a-c,z+b),(x-a+c,z+b),(x-a,z+b-c),(x-a,z-b+c)]


def radial(n,r,x=0,z=0,phase=0):
    return [(x+r*math.cos(phase+i*math.tau/n),z+r*math.sin(phase+i*math.tau/n)) for i in range(n)]


class Relief:
    def __init__(self):
        self.v,self.f,self.ms,self.palette=[],[],[],[]

    def part(self,vertices,faces,paint):
        if paint not in self.palette:
            self.palette.append(paint)
        i=len(self.v)
        self.v.extend(vertices)
        self.f.extend(tuple(i+k for k in f) for f in faces)
        self.ms.extend([self.palette.index(paint)]*len(faces))

    def prism(self,p,y0,y1,paint):
        n=len(p)
        self.part([(x,y,z) for y in (y0,y1) for x,z in p],
                  [tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
                  +[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)],paint)

    def ring(self,n,r0,r1,y0,y1,paint,phase=0):
        pts=[*radial(n,r1,phase=phase),*radial(n,r0,phase=phase)]
        f=[]
        for i in range(n):
            j=(i+1)%n
            f.extend([(i,j,j+n,i+n),(i+2*n,i+3*n,j+3*n,j+2*n),
                      (j,i,i+2*n,j+2*n),(i+n,j+n,j+3*n,i+3*n)])
        self.part([(x,y,z) for y in (y0,y1) for x,z in pts],f,paint)

    def mesh(self,name):
        m=bpy.data.meshes.new(name)
        m.from_pydata(self.v,[],self.f)
        m.update()
        assert not m.validate()
        for a in self.palette:
            m.materials.append(a)
        for p,i in zip(m.polygons,self.ms):
            assert p.area>1e-9
            p.material_index=i
        o=bpy.data.objects.new(name,m)
        scene.collection.objects.link(o)
        return o


outer_w=[(-.204,-.108),(-.171,-.151),(.171,-.151),(.204,-.108),
         (.204,.101),(.160,.151),(-.160,.151),(-.204,.101)]
phase=math.pi/6
outer_t=radial(6,.201,phase=phase)
w=Relief()
w.prism(outer_w,0,.028,edge)
w.prism([(x*.966,z*.947) for x,z in outer_w],.018,.055,steel)
w.prism(rect(0,0,.305,.187,.034),.046,.067,deep)
w.ring(16,.064,.090,.062,.084,brush,phase=math.pi/16)
w.prism(radial(12,.066),.056,.075,steel)
w.prism(rect(0,0,.025,.072,.006),.073,.092,signal)
for side in (-1,1):
    w.prism(rect(side*.120,.040,.092,.049,.011),.062,.103,brush)
    w.prism(rect(side*.120,-.041,.069,.024,.004),.061,.077,edge)
    w.prism(radial(8,.016,side*.16,.112),.046,.071,edge)
    w.prism(radial(8,.016,side*.16,-.113),.047,.071,edge)
warden=w.mesh("Warden's Plate · broad latch relief")

t=Relief()
t.prism(outer_t,0,.028,gray)
t.ring(6,.127,.194,.020,.054,deep,phase)
t.ring(12,.096,.137,.040,.066,gray,math.pi/12)
t.ring(12,.084,.106,.059,.083,rim,math.pi/12)
for i in range(6):
    a=phase+i*math.tau/6
    x,z=.150*math.cos(a),.150*math.sin(a)
    pts=[(x+p*math.cos(a)-q*math.sin(a),z+p*math.sin(a)+q*math.cos(a))
         for p,q in rect(0,0,.089,.072,.013)]
    t.prism(pts,.034,.078,orange if i in (0,1,3,4) else gray)
    t.prism(radial(8,.013,x,z),.074,.087,edge)
gems=radial(8,.080,phase=math.pi/8)
lens=[(x,.085,z) for x,z in gems]+[(0,.116,0)]
for i in range(8):
    t.part(lens,[(i,(i+1)%8,8)],light if i%2 else cool)
titan=t.mesh("Titan's Core · hex cargo relief")

records=[]
for o,slug in [(warden,"wardens-plate"),(titan,"titans-core")]:
    path=out/f"e8d-{slug}-relief.glb"
    export([o],path)
    bpy.data.objects.remove(o,do_unlink=True)
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    (n,)=set(scene.objects)-before
    assert n.type=="MESH"
    n.data.calc_loop_triangles()
    assert all(p.area>1e-9 for p in n.data.polygons)
    records.append((n,{"slug":slug,"bytes":path.stat().st_size,
                       "triangles":len(n.data.loop_triangles),
                       "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}))

before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(donor))
frames=sorted(set(scene.objects)-before,key=lambda o:o.name)
assert len(frames)==12 and len({o.data for o in frames})==1
for f in frames[2:]:
    bpy.data.objects.remove(f,do_unlink=True)
def hull(mesh):
    points=sorted({(round(v.co.x,7),round(v.co.z,7)) for v in mesh.vertices})
    def side(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def half(items):
        h=[]
        for p in items:
            while len(h)>1 and side(h[-2],h[-1],p)<=1e-10:
                h.pop()
            h.append(p)
        return h[:-1]
    return half(points)+half(reversed(points))

locked=[]
for index,((o,r),frame) in enumerate(zip(records,frames)):
    center=(index-.5)*1.25
    frame.matrix_world=Matrix.Translation((center,0,1.42))
    o.matrix_world=Matrix.Translation((center,.040,1.42))
    b=Relief()
    b.prism(hull(o.data),0,.005,shadow)
    s=b.mesh("Locked placeholder")
    s.matrix_world=o.matrix_world.copy()
    locked.append(s)
    bpy.context.view_layer.update()
    v=[o.matrix_world@p.co for p in o.data.vertices]
    f=[frame.matrix_world@p.co for p in frame.data.vertices]
    gap=min(p.y for p in v)-max(p.y for p in f)
    margin=[.259-max(abs(z) for z in coord) for coord in ([p.x-center for p in v],[p.z-1.42 for p in v])]
    assert gap>.007 and min(margin)>.050,(gap,margin)
    r["forward_gap_m"]=round(gap,5)
    r["edge_margins_m"]=[round(m,5) for m in margin]

(out/"receipt.json").write_text(json.dumps({
    "frame_sha256":donor_sha,"frame_instances":12,"slot_mapping":"illustrative only; final slot census unresolved",
    "grant_or_actor":False,"assets":[r for _,r in records]},indent=2)+"\n")
print("Reward fit",[(r) for _,r in records],flush=True)
stage=Relief()
stage.prism(rect(0,1.35,4.5,2.5,.02),-.16,-.030,plaster)
for x in (-1.59,1.59):
    stage.prism(rect(x,1.35,.12,2.12,.02),-.125,.08,edge)
stage.mesh("Existing wall palette staging")


def lamp(name,p,t,power,color,size):
    d=bpy.data.lights.new(name,"AREA")
    d.energy,d.size,d.color=power,size,color
    o=bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location=p
    o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()


lamp("Warm gallery source",(-2,2.8,3.23),(0,0,1.35),230,(1,.77,.56),3.0)
lamp("Plaza sky fill",(1.7,2.9,2.2),(0,0,1.45),138,(.72,.86,1),2.6)
bpy.ops.object.camera_add(location=(.10,3.8,1.89))
cam=bpy.context.object
scene.camera=cam
cam.rotation_euler=(Vector((0,0,1.36))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=49
scene.render.engine="CYCLES"
scene.cycles.samples=38
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.075
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x,scene.render.resolution_y=1320,840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=92
for state in ("locked","earned"):
    for o,_ in records:
        o.hide_render=state=="locked"
    for o in locked:
        o.hide_render=state=="earned"
    scene.render.filepath=str(out/f"{state}.jpg")
    bpy.ops.render.render(write_still=True)
