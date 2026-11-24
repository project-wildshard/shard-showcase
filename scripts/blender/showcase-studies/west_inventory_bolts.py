"""Three deliberately oversized, nonfunctional W3b fantasy inventory props."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
s = bpy.context.scene
clear_scene()


def mat(name, color, metal=.0, rough=.45, glow=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["Emission Color"].default_value = (*color, 1)
    p.inputs["Emission Strength"].default_value = glow
    return m


ash = mat("Honey ash", (.308,.145,.058), .06,.49)
wood = mat("Sienna shaft facets", (.245,.097,.040), .03,.55)
wood_light = mat("Light honey grain", (.395,.19,.072), .03,.53)
aged = mat("Ochre shaft grain", (.16,.061,.026), .03,.57)
gun = mat("Pewter iron", (.325,.358,.403), .58,.37)
cool = mat("Blue iron", (.205,.326,.414), .65,.34)
bright = mat("Polished ribs", (.568,.633,.635), .72,.25)
rust = mat("Warm graphite", (.104,.107,.120), .58,.46)
grey = mat("Slate vanes", (.29,.313,.374), .28,.53)
silver = mat("Silver ribbed vanes", (.45,.478,.525), .30,.48)
jade = mat("Jade enamel vanes", (.045,.246,.242), .29,.44)
foam = mat("Patina ridge", (.103,.400,.39), .31,.36)
bronze = mat("Dark cast bronze", (.252,.109,.048), .62,.45)
gold = mat("Burnished brass", (.593,.321,.104), .60,.34)
umber = mat("Russet decorative wrap", (.225,.079,.036), .04,.60)
honey = mat("Amber gem honey planes", (.89,.238,.009), .23,.30,.22)
hot = mat("Amber gem bright planes", (1,.478,.023), .15,.28,.42)
smoke = mat("Amber gem burnt planes", (.66,.098,.009), .30,.39,.09)


class Mesh:
    def __init__(self):
        self.v, self.f, self.ids, self.mats = [], [], [], []

    def add(self, v, f, mats):
        n = len(self.v)
        self.v.extend(v)
        self.f.extend(tuple(n+i for i in face) for face in f)
        for m in mats if isinstance(mats,list) else [mats]*len(f):
            if m not in self.mats:
                self.mats.append(m)
            self.ids.append(self.mats.index(m))

    def rings(self, profile, n, side, ellipse=1, phase=0, turn=0):
        v = [(r*math.cos(phase+j*turn+i*math.tau/n),
              r*ellipse*math.sin(phase+j*turn+i*math.tau/n), z)
             for j,(z,r) in enumerate(profile) for i in range(n)]
        f = [tuple(range(n-1,-1,-1))]
        for j in range(len(profile)-1):
            for i in range(n):
                a,b=j*n+i,j*n+(i+1)%n
                f.append((a,b,b+n,a+n))
        f += [tuple(range(len(v)-n,len(v)))]
        mats = [side[(i-1)%len(side)] for i in range(len(f))] if isinstance(side,list) else side
        self.add(v,f,mats)

    def plaque(self, outline, depth, front, edges, angle=0):
        a = len(outline)
        ca,sa = math.cos(angle),math.sin(angle)
        v = [(x*ca-y*sa,x*sa+y*ca,z) for y in (-depth,depth) for x,z in outline]
        f = [tuple(range(a)),tuple(range(2*a-1,a-1,-1))]
        f += [(i,i+a,(i+1)%a+a,(i+1)%a) for i in range(a)]
        self.add(v,f,[front,front]+[edges]*a)

    def object(self, name):
        g = bpy.data.meshes.new(name)
        g.from_pydata(self.v,[],self.f)
        g.update()
        for m in self.mats:
            g.materials.append(m)
        assert len(self.ids)==len(g.polygons)
        for p,i in zip(g.polygons,self.ids):
            p.material_index=i
        o=bpy.data.objects.new(name,g)
        s.collection.objects.link(o)
        return o


def shaft(g, begin, top, mode):
    palette = [umber,wood,wood,aged] if mode=="pitch" else [ash,wood,wood_light,ash,aged]
    g.rings([(0,.018),(.009,.024),(begin,.026),(.39,.026),
             (top-.04,.023),(top,.027)], 12, palette, .86, .1, .035)
    for z in (.015,begin,top-.025):
        base, rim=(bronze,gold) if mode=="pitch" else (rust,gun)
        g.rings([(z-.007,.025),(z-.003,.031),(z+.003,.031),(z+.007,.026)],
                10,[base,rim,base],.88,.13)
    # Wide closed, faceted end cap; no interface to launching hardware.
    g.rings([(0,.024),(.006,.028),(.017,.029),(.023,.026)],8,bronze if mode=="pitch" else rust,.82,.25)


def vanes(g, body, ridge, mode):
    for angle in (0,math.pi,math.pi/2):
        outline = [( .023,.079),(.101,.039),(.086,.184),(.047,.240),(.024,.271)]
        if mode=="pitch":
            outline=[(.023,.078),(.106,.045),(.091,.190),(.026,.268)]
        g.plaque(outline,.004,body,ridge,angle)
        for j in range(4 if mode!="pitch" else 2):
            z=.100+j*.026
            off=.013+j*.003
            verts=[(.026,z+.062),(.089-off,z),(.086-off,z+.012),(.026,z+.073)]
            g.plaque(verts,.0061,ridge,body,angle)


def iron():
    g=Mesh()
    shaft(g,.070,.740,"iron")
    vanes(g,grey,silver,"iron")
    g.rings([(.692,.025),(.72,.029),(.752,.035),(.768,.035)],10,[rust,gun,gun], .84)
    g.rings([(.744,.031),(.785,.060),(.806,.093),(.839,.082),
             (.975,.014),(.984,.010)], 6,[gun,rust,bright,gun,rust,gun],.40,.03)
    return g


def broad():
    g=Mesh()
    shaft(g,.069,.68,"broad")
    vanes(g,jade,foam,"broad")
    g.rings([(.622,.028),(.650,.042),(.702,.042),(.724,.036)],8,[cool,bright,rust,cool],.71,.12)
    g.rings([(.694,.034),(.769,.050),(.938,.022),(.975,.009)],
            8,[cool,rust,bright,cool],.49)
    # Two decorative pierced stone-like wings. Closed rim caps keep real
    # holes in the mesh; the top silhouettes intentionally end blunt.
    outer=[(.027,.697),(.152,.666),(.105,.777),(.013,.961)]
    inner=[(.042,.730),(.101,.714),(.074,.777),(.038,.821)]
    for sign in (-1,1):
        v=[(sign*x,side*(.008 if j<4 else .013),z)
           for side in (-1,1) for j,(x,z) in enumerate(outer+inner)]
        f=[];mm=[]
        for i in range(4):
            j=(i+1)%4
            f.extend([(i,j,j+4,i+4),(8+i,12+i,12+j,8+j),
                      (i,8+i,8+j,j),(4+i,4+j,12+j,12+i)])
            mm.extend([cool,cool,bright,rust])
        g.add(v,[q if sign>0 else tuple(reversed(q)) for q in f],mm)
    return g


def pitch():
    g=Mesh()
    shaft(g,.063,.624,"pitch")
    vanes(g,bronze,gold,"pitch")
    g.rings([(.544,.030),(.583,.040),(.608,.043),(.639,.068),(.662,.071),
            (.678,.066)],10,[bronze,gold,bronze],.89,.14)
    crystal=[(.646,.056),(.701,.077),(.792,.087),(.881,.073),(.945,.044),(.956,.028)]
    g.rings(crystal,9,[honey,hot,smoke,honey,hot,honey,honey,smoke],.82,.05,.25)
    for sign in (-1,1):
        v=[]
        for i in range(37):
            t=i/36
            a=t*math.tau+sign*.8
            h=.782+sign*.068*math.cos(a)
            za,ra,zb,rb=next((a0,r0,b0,r1) for (a0,r0),(b0,r1) in zip(crystal,crystal[1:]) if a0<=h<=b0)
            radius=ra+(rb-ra)*(h-za)/(zb-za)+.002
            for dz,dr in ((-.012,.0),(0,.003),(.012,0)):
                v.append(((radius+dr)*math.cos(a),.88*(radius+dr)*math.sin(a),h+dz))
        g.add(v,[(3*i+j,3*(i+1)+j,3*(i+1)+j+1,3*i+j+1)
                 for i in range(36) for j in range(2)], [umber,bronze]*36)
    g.plaque([(-.031,.642),(0,.601),(.031,.642),(0,.682)],
             .058,bronze,gold)
    g.plaque([(-.012,.642),(0,.623),(.012,.642),(0,.661)],
             .061,gold,bronze)
    return g


recipes = [("007","Iron",iron),("008","Broadhead",broad),("009","Pitch",pitch)]
rows=[]
for ident, label, make in recipes:
    clear_scene()
    o=make().object("WSC-GEAR-"+ident+" | "+label+" display proxy")
    # Correct closed shells independently; no external raster textures.
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    path=out/f"wsc-gear-{ident}-{label.lower()}-bolt.glb"
    export([o],path)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes=[o for o in s.objects if o.type=="MESH"]
    assert len(meshes)==1 and meshes[0].location.length<.0001
    vs=[v.co for v in meshes[0].data.vertices]
    size=[max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3)]
    assert abs(min(v.z for v in vs))<.0001
    assert .93<size[2]<1 and path.stat().st_size<=65536
    rows.append(dict(id="WSC-GEAR-"+ident,label=label,file=path.name,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     bytes=path.stat().st_size,
                     triangles=sum(len(p.vertices)-2 for p in meshes[0].data.polygons),
                     normalized_display_bounds=[round(x,5) for x in size]))
(out/"west-inventory-bolts.json").write_text(json.dumps(rows,indent=2)+"\n")
print("BOLT_RECEIPT",json.dumps(rows),flush=True)

# Review stage only: the works sit above individually lit dark backing plates.
clear_scene()
for i,row in enumerate(rows):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/row["file"]))
    o=next(o for o in set(s.objects)-before if o.type=="MESH")
    o.location.x=(i-1)*.56
    o.rotation_euler.z=(-.19,.11,.12)[i]

plate = mat("Studio anodized backplate", (.034,.072,.088), .29,.52)
inset = mat("Studio chamfer", (.100,.166,.169), .40,.45)
floor = mat("Studio void", (.022,.042,.051), .08,.7)
text = mat("Studio frosted lettering", (.76,.80,.70), .09,.65,.11)
for i,row in enumerate(rows):
    x=(i-1)*.56
    g=Mesh()
    g.plaque([(x-.23,-.145),(x+.23,-.145),(x+.248,-.112),
              (x+.248,1.034),(x+.227,1.069),(x-.227,1.069),
              (x-.248,1.034),(x-.248,-.112)],.013,plate,inset)
    o=g.object("Studio backing "+row["label"])
    o.location.y=.122
    def label(body,z,size,m):
        d=bpy.data.curves.new(body,"FONT")
        d.body=body
        d.align_x="CENTER"
        d.size=size
        d.materials.append(m)
        a=bpy.data.objects.new(body,d)
        s.collection.objects.link(a)
        a.location=(x,.102,z)
        a.rotation_euler.x=math.pi/2
    label(row["label"].upper(),-.073,.041,text)
    label(row["id"],-.109,.024,inset)
g=Mesh()
g.plaque([(-6,-6),(6,-6),(6,6),(-6,6)],.025,floor,floor)
g.object("Graphite cyclorama").location.y=.260


def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()


def area(name,at,to,power,size,tint):
    d=bpy.data.lights.new(name,"AREA")
    d.energy=power
    d.size=size
    d.color=tint
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o)
    o.location=at
    aim(o,to)


area("Soft gold key",(-1.4,-2.4,2.3),(0,0,.48),90,1.75,(1,.86,.68))
area("Soft ice edge",(1.4,-1.8,1.6),(0,0,.53),62,1.45,(.61,.78,1))
area("Grazing strip",(-.4,-.7,.18),(0,0,.44),18,1.10,(.72,.90,1))
s.world=bpy.data.worlds.new("Workshop ambience")
s.world.color=(.11,.143,.175)
cd=bpy.data.cameras.new("Catalogue lens")
cam=bpy.data.objects.new("Catalogue lens",cd)
s.collection.objects.link(cam)
s.camera=cam
cd.type="ORTHO"
s.render.engine="CYCLES"
s.cycles.samples=64
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.037
s.view_settings.view_transform="AgX"
s.view_settings.look="AgX - Medium High Contrast"
s.render.image_settings.file_format="JPEG"
s.render.image_settings.quality=92
s.render.resolution_percentage=100


def render(name,loc,at,scale,wh):
    cam.location=loc
    aim(cam,at)
    cd.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)


render("nov24-west-inventory-bolts",(.23,-4,.65),(0,.02,.466),
       1.92,(1450,1050))
render("nov24-west-inventory-bolt-details",(.8,-3,.93),(0,.015,.813),
       1.92,(1450,450))
