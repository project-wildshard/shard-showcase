"""Build three nonfunctional E8c/E8d prize concepts against the original shared frame."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from common import clear_scene, export, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene

def mat(name, color, metallic=.35, rough=.44, signal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    for k,v in {"Base Color":(*color,1),"Metallic":metallic,"Roughness":rough,
                "Emission Color":(*color,1),"Emission Strength":signal}.items():
        p.inputs[k].default_value=v
    return m

kraft=mat("Nibbles | folded corrugation",(.58,.29,.09),.05,.72)
cut=mat("Nibbles | torn brown edges",(.23,.093,.035),.03,.78)
gold=mat("Cast inlaid brass",(.65,.35,.087),.65,.31)
oxide=mat("Hot Mess | red oxide",(.35,.061,.025),.44)
soot=mat("Soot black",(.029,.034,.039),.3,.54)
steel=mat("Rita | brushed gunmetal",(.155,.205,.233),.73)
blue=mat("Rita | ice enamel",(.018,.36,.42),.35,.28,.15)
ember=mat("Hot Mess | vitrified slag",(.79,.125,.015),.23,.36,.28)
shadow=mat("Locked | charcoal sepia",(.051,.046,.043),.13,.79)
wood=mat("Mount rail | stained oak",(.22,.105,.049),.03,.57)
wall=mat("Gallery | mineral plaster",(.26,.18,.12),.02,.82)

def rect(x,z,w,h,c):
    a=w/2;b=h/2
    return [(x-a+c,z-b),(x+a-c,z-b),(x+a,z-b+c),(x+a,z+b-c),
            (x+a-c,z+b),(x-a+c,z+b),(x-a,z+b-c),(x-a,z-b+c)]

def circle(x,z,r,n=12,phase=0):
    return [(x+r*math.cos(phase+i*math.tau/n),z+r*math.sin(phase+i*math.tau/n)) for i in range(n)]

class Form:
    def __init__(self):
        self.verts=[];self.faces=[];self.ids=[];self.palette=[]
    def prism(self, poly,y0,y1,m):
        if m not in self.palette:self.palette.append(m)
        assert len(poly)>=3 and y1>y0
        def orient(a,b,c):
            return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        for i,a in enumerate(poly):
            b=poly[(i+1)%len(poly)]
            for j in range(i+2,len(poly)):
                if i==0 and j==len(poly)-1:continue
                c=poly[j];d=poly[(j+1)%len(poly)]
                assert not (orient(a,b,c)*orient(a,b,d)<-1e-14
                    and orient(c,d,a)*orient(c,d,b)<-1e-14), (poly,i,j)
        o=len(self.verts);n=len(poly)
        area=sum(poly[i][0]*poly[(i+1)%n][1]-poly[(i+1)%n][0]*poly[i][1] for i in range(n))
        assert abs(area)>1e-8
        if area<0:poly=list(reversed(poly))
        self.verts.extend((x,y,z) for y in (y0,y1) for x,z in poly)
        faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
        faces.extend((i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n))
        self.faces.extend(tuple(o+j for j in f) for f in faces)
        self.ids.extend([self.palette.index(m)]*len(faces))
    def bar(self,x,z,w,h,y0,y1,m,a=0):
        c=math.cos(a);s=math.sin(a)
        self.prism([(x+u*c-v*s,z+u*s+v*c) for u,v in rect(0,0,w,h,min(w,h)*.19)],y0,y1,m)
    def make(self,name):
        d=bpy.data.meshes.new(name);d.from_pydata(self.verts,[],self.faces);d.update()
        assert not d.validate()
        for m in self.palette:d.materials.append(m)
        for face,i in zip(d.polygons,self.ids):
            assert face.area>1e-9
            face.material_index=i
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);return o

# Concepts for the planned rewards, not final inventory names. Flat locked cuts reuse the
# primary outline (holes are not baked into the unlock state).
crown=[(-.193,-.081),(-.202,.071),(-.179,.158),(-.108,.076),(-.019,.191),
       (.002,.202),(.087,.086),(.145,.157),(.202,.080),(.184,-.081)]
slag=[(-.147,.166),(-.085,.133),(-.044,.092),(-.048,-.013),(-.023,-.037),
      (.026,-.042),(.060,-.024),(.078,-.015),(.051,.071),(.096,.121),(.158,.153),
      (.197,.085),(.150,.022),(.119,-.026),(.113,-.139),(.041,-.193),(-.066,-.185),
      (-.121,-.119),(-.114,-.032),(-.173,.021),(-.195,.096)]
lamp=[(-.187,-.136),(-.204,-.095),(-.204,.034),(-.151,.084),(-.122,.084),
      (-.123,.136),(-.075,.169),(.078,.169),(.133,.124),(.131,.089),(.183,.068),
      (.204,.022),(.188,-.102),(.140,-.153),(-.135,-.153)]

a=Form();a.prism(crown,0,.014,cut)
a.prism([(x*.949,z*.939+.004) for x,z in crown],.014,.027,kraft)
a.bar(0,-.073,.371,.059,.027,.042,cut)
a.bar(0,-.054,.342,.015,.042,.052,gold)
for i,x in enumerate((-.118,0,.109)):
    a.prism(circle(x,.021,.022,4,math.pi/2),.027,.042,gold)
for x in (-.154,-.126,-.097,.103,.132,.161):
    a.bar(x,-.082,.007,.018,.043,.046,kraft)

b=Form();b.prism(slag,0,.019,soot)
for x,a0 in [(-.105,-.63),(.114,.61)]:
    b.bar(x,.08,.100,.142,.014,.039,oxide,a0)
    b.bar(x*1.28,.128,.078,.042,.039,.062,steel,a0)
    b.bar(x*.76,.029,.042,.091,.025,.044,gold,a0)
b.prism([(-.055,.007),(.038,.043),(.083,-.102),(.034,-.152),(.002,-.188),(-.038,-.149),(-.071,-.065)],.019,.042,oxide)
b.prism([(-.032,-.019),(.023,-.008),(.049,-.095),(.006,-.151),(-.037,-.116)],.042,.056,ember)
for x,z,r in [(-.077,-.086,.010),(.052,-.07,.012),(.029,-.022,.008)]:
    b.prism(circle(x,z,r,6),.042,.055,gold)

c=Form();c.prism(lamp,0,.018,soot)
c.prism([(x*.92,z*.9) for x,z in lamp],.018,.037,steel)
c.bar(0,.124,.22,.045,.037,.049,soot)
c.prism(circle(0,.027,.075,16,math.pi/16),.037,.061,soot)
c.prism(circle(0,.027,.060,16,math.pi/16),.061,.080,blue)
c.prism(circle(0,.027,.038,12,math.pi/12),.080,.084,steel)
for x,z in [(-.145,-.070),(.145,-.070),(-.127,.040),(.127,.040)]:
    c.prism(circle(x,z,.0125,6),.037,.048,gold)
for x in (-.086,-.043,0,.043,.086):
    c.bar(x,-.109,.019,.007,.039,.046,soot)

entries=[("sir-nibbles",a,crown),("hot-mess",b,slag),("riveting-rita",c,lamp)]
models=[];cuts=[]
for slug,shape,outline in entries:
    m=shape.make(slug+"-earned")
    flat=Form();flat.prism(outline,0,.005,shadow);l=flat.make(slug+"-locked")
    models.append(m);cuts.append(l)
artifact=out/"e8d-night-elite-reliefs.glb"
export(models+cuts,artifact)
assert artifact.stat().st_size<350000
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(artifact))
replay=sorted(set(scene.objects)-before,key=lambda o:o.name)
assert len(replay)==6 and all(o.type=="MESH" for o in replay)
def signature(o):
    o.data.calc_loop_triangles()
    bb=[[round(f(v[i] for v in o.bound_box),6) for i in range(3)] for f in (min,max)]
    return bb,len(o.data.loop_triangles)
assert sorted(signature(o) for o in replay)==sorted(signature(o) for o in (models+cuts))
for o in replay:bpy.data.objects.remove(o,do_unlink=True)
frames_path=here.parents[2]/"public/assets/wildshard-art/west-plaza-empty-mounts.glb"
pin="3e7e28863742ebcdd2f494d97d98574d263d876dac01f03e21a2b0fd5b4a54c7"
assert hashlib.sha256(frames_path.read_bytes()).hexdigest()==pin
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(frames_path))
frames=sorted(set(scene.objects)-before,key=lambda o:o.name)
assert len(frames)==12 and len({o.data for o in frames})==1
for f in frames[3:]:bpy.data.objects.remove(f,do_unlink=True)
receipts=[]
for i,(m,l,fr) in enumerate(zip(models,cuts,frames[:3])):
    x=(1-i)*.656
    fr.matrix_world=Matrix.Translation((x,0,1.42))
    for o in (m,l):o.matrix_world=Matrix.Translation((x,.040,1.42))
    bpy.context.view_layer.update()
    fv=[fr.matrix_world@v.co for v in fr.data.vertices]
    mv=[o.matrix_world@v.co for o in (m,l) for v in o.data.vertices]
    gap=min(p.y for p in mv)-max(p.y for p in fv)
    edge=.259-max(max(abs(v.x-x),abs(v.z-1.42)) for v in mv)
    assert gap>=.007 and edge>=.050
    receipts.append(dict(artwork_id=entries[i][0],edge_clearance_m=round(edge,6),
       forward_gap_m=round(gap,6),earned_triangles=signature(m)[1],locked_triangles=signature(l)[1]))
(out/"receipt.json").write_text(json.dumps(dict(frame_sha256=pin,shared_frame_instances=12,assets=receipts,
    sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),bytes=artifact.stat().st_size,
    scope="three provisional reliefs; stage positions are not canonical slots; no grants or actors"),indent=2)+"\n")
g=Form()
g.prism(rect(0,1.48,3.4,1.27,.04),-.125,-.032,wall)
for z in (1.001,2.00):g.bar(0,z,3.4,.076,-.032,.032,wood)
g.make("Gallery staging only")
def light(name,p,t,power,color,size):
    d=bpy.data.lights.new(name,"AREA");d.energy,d.size,d.color=power,size,color
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()
light("Warm raking gallery",(-1.6,1.9,2.8),(0,0,1.44),140,(1,.78,.56),1.4)
light("Cool evening fill",(1.6,2.9,2.15),(0,0,1.42),95,(.67,.83,1),1.75)
bpy.ops.object.camera_add(location=(.18,3.25,1.73))
cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((0,0,1.41))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens=48
scene.render.engine="CYCLES";scene.cycles.samples=42
scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.046
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x=1340;scene.render.resolution_y=670
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=94
for state in ("locked","earned"):
    for o in models:o.hide_render=state=="locked"
    for o in cuts:o.hide_render=state=="earned"
    scene.render.filepath=str(out/("nov25-e8d-night-reliefs-"+state+".jpg"))
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):bpy.ops.render.render(write_still=True)
