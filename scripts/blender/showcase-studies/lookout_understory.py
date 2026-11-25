"""Two lightweight foliage studies; stand-alone dressing of the W11 rock path."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

S=bpy.context.scene
O=output_directory()
asset=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
pins={
    "wsc-prop-036-landscape-boulder.glb":"d03ed70f69d230fa82c474770eb65a991189cbf4848db4fc750ec1cb6f812750",
    "wsc-prop-012-deciduous-tree-far.glb":"33f381e232b215c9fa21e81ceb020212f092b8ca669b2fe76d9f1627a910ada9",
    "wsc-prop-046-conifer-tree-far.glb":"43362bfe9c1673367c0065eef2eb88759564a69df379feb2f27dc140e9a699a6",
    "wsc-prop-047-wildflower-clump-far.glb":"e67cfc6fd4d86d239929e0ba36239a8abbc0387410b0265b6fb1a635286c9d98",
}
for name,digest in pins.items():
    assert hashlib.sha256((asset/name).read_bytes()).hexdigest()==digest


def mat(name,c,rough=.75):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Roughness"].default_value=rough
    return m


def mulch_material():
    m=mat("Rock trail · layered dirt",(.14,.098,.05))
    nt=m.node_tree
    n=nt.nodes["Principled BSDF"]
    coords=nt.nodes.new("ShaderNodeTexCoord")
    tex=nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=6.6
    tex.inputs["Detail"].default_value=3
    nt.links.new(coords.outputs["Object"],tex.inputs["Vector"])
    ramp=nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.16
    ramp.color_ramp.elements[0].color=(.082,.052,.027,1)
    ramp.color_ramp.elements[1].position=.81
    ramp.color_ramp.elements[1].color=(.235,.165,.089,1)
    nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],n.inputs["Base Color"])
    bump=nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.24
    bump.inputs["Distance"].default_value=.065
    nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bump.outputs[0],n.inputs["Normal"])
    return m


foliage=mat("West foliage · vertex tones",(.15,.24,.056),.63)
nodes=foliage.node_tree.nodes
attr=nodes.new("ShaderNodeVertexColor")
attr.layer_name="Tints"
foliage.node_tree.links.new(attr.outputs["Color"],nodes["Principled BSDF"].inputs["Base Color"])


class Foliage:
    def __init__(self):
        self.v,self.f,self.rgb=[],[],[]
    def add(self,v,f,c):
        start=len(self.v)
        self.v.extend(v)
        self.f.extend(tuple(start+i for i in face) for face in f)
        self.rgb.extend((*x,1) for x in c)
    def mesh(self,name):
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(self.v,[],self.f)
        mesh.update()
        tint=mesh.color_attributes.new(name="Tints",type="BYTE_COLOR",domain="POINT")
        for dst,color in zip(tint.data,self.rgb):
            dst.color=color
        mesh.color_attributes.active_color=tint
        ob=bpy.data.objects.new(name,mesh)
        S.collection.objects.link(ob)
        ob.data.materials.append(foliage)
        return ob


def scaled(c,n):
    return tuple(min(1,x*n) for x in c)


def fern():
    P=Foliage()
    rng=random.Random(365)
    for i in range(8):
        a=i*math.tau/8+rng.uniform(-.24,.24)
        d=Vector((math.cos(a),math.sin(a),0))
        cross=Vector((-math.sin(a),math.cos(a),0))
        L=rng.uniform(.36,.56)
        h=rng.uniform(.37,.56)
        color=rng.choice(((.076,.24,.041),(.090,.29,.064),(.155,.36,.074),(.19,.40,.077)))
        def axis(t):
            return d*(L*(.08*t+.92*t**1.38))+cross*(.04*t*t)+Vector((0,0,h*(2.60*t-1.70*t*t)))
        spine=[axis(j/8) for j in range(9)]
        P.add([q+cross*(.005*(1-.7*j/8))*b for j,q in enumerate(spine) for b in (-1,1)],
              [(2*i,2*i+1,2*i+3,2*i+2) for i in range(8)],[(.24,.34,.07)]*18)
        for j in range(7):
            t=.23+j*.105
            base=axis(t)
            broad=.094*math.sin(math.pi*(t-.10)/.98)*rng.uniform(.92,1.15)
            length=max(.013,1.25*broad+.022*(1-t))
            for sign in (-1,1):
                tip=base+sign*length*cross+d*(.040+(1-t)*.021)
                tip.z+=rng.uniform(-.021,.019)
                center=base.lerp(tip,.49)
                center.z+=.010
                p0=center+d*.036*(1-.64*t)
                p1=center-d*.031*(1-.65*t)
                P.add([base,p0,center,p1,tip],[(0,1,2),(0,2,3),(1,4,2),(2,4,3)],
                      [scaled(color,.73),color,scaled(color,1.13),scaled(color,.82),scaled(color,.78)])
    return P


def verge():
    P=Foliage()
    rng=random.Random(7421)
    root=(.070,.091,.021)
    for i in range(44):
        a=rng.random()*math.tau
        r=.19*math.sqrt(rng.random())
        d=Vector((math.cos(a),math.sin(a),0))
        cross=Vector((-math.sin(a),math.cos(a),0))
        base=r*d
        z=rng.uniform(.18,.50)
        reach=rng.uniform(.10,.33)
        w=rng.uniform(.011,.028)
        tone=rng.choice(((.22,.32,.061),(.33,.40,.085),(.41,.41,.108),(.18,.33,.057),(.23,.34,.097)))
        v,c=[],[]
        for t,k in ((0,1),(.37,.88),(.73,.58),(1,.045)):
            p=base+d*(reach*t**1.7)+Vector((0,0,z*(1.65*t-.65*t*t)))
            # A folded ribbon makes the blade readable from oblique angles.
            v.extend([p-cross*w*k,p+d*.13*w*k,p+cross*w*k])
            group=tuple(x+(y-x)*t**.65 for x,y in zip(root,tone))
            c.extend((scaled(group,.86),scaled(group,1.15),group))
        P.add(v,[(i*3+j,i*3+j+1,(i+1)*3+j+1,(i+1)*3+j)
                 for i in range(3) for j in range(2)],c)
    return P


def loaded(path):
    old=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return tuple(sorted((o for o in set(S.objects)-old if o.type=="MESH"),key=lambda o:o.name))


def proof(p):
    b=p.read_bytes()
    assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    d=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    assert not any(d.get(k) for k in ("images","animations","skins","extensionsRequired"))
    p0,=d["meshes"][0]["primitives"]
    assert "COLOR_0" in p0["attributes"]
    tri=d["accessors"][p0["indices"]]["count"]//3
    assert len(b)<50000 and tri<800,(len(b),tri)
    clear_scene()
    o,=loaded(p)
    o.data.calc_loop_triangles()
    assert len(o.data.loop_triangles)==tri
    v=[o.matrix_world @ t.co for t in o.data.vertices]
    radial_extent=max(math.hypot(p.x,p.y) for p in v)
    assert min(p.z for p in v)>-.001
    return dict(bytes=len(b),triangles=tri,radius_m=round(radial_extent,5),height_m=round(max(p.z for p in v),5))


# Optional W11 animated review only; default invocation still emits the static studies.
breeze_dir=os.environ.get("WSC_LOOKOUT_BREEZE_DIR")
breeze_slots=[]
out_paths={}
stats={}
for name,fn in (("fern",fern),("verge",verge)):
    if breeze_dir:
        out_paths[name]=Path(breeze_dir)/f"w11-lookout-{name}-breeze.glb"
        stats[name]=dict(radius_m={"fern":.561,"verge":.47401}[name])
        continue
    clear_scene()
    ob=fn().mesh("Lookout understory | "+name)
    p=O/f"w11-lookout-{name}.glb"
    export([ob],p)
    out_paths[name]=p
    stats[name]=proof(p)


def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()


def sun(dir,power,color):
    n=bpy.data.lights.new("Late trail sun","SUN")
    n.energy,n.color,n.angle=power,color,.095
    o=bpy.data.objects.new(n.name,n)
    S.collection.objects.link(o)
    o.rotation_euler=Vector(dir).to_track_quat("-Z","Y").to_euler()


def camera(pos,target,lens=None,ortho=None):
    n=bpy.data.cameras.new("Trail review")
    o=bpy.data.objects.new(n.name,n)
    S.collection.objects.link(o)
    o.location=pos
    aim(o,target)
    if ortho:
        n.type="ORTHO"
        n.ortho_scale=ortho
    if lens:
        n.lens=lens
    S.camera=o


def render(name,w,h):
    S.render.engine="CYCLES"
    S.cycles.samples=36
    S.cycles.use_denoising=False
    S.render.resolution_x,S.render.resolution_y=w,h
    S.render.resolution_percentage=100
    S.render.image_settings.file_format="JPEG"
    S.render.image_settings.quality=91
    S.view_settings.view_transform="AgX"
    S.view_settings.look="AgX - Medium High Contrast"
    S.render.filepath=str(O/f"nov24-lookout-{name}.jpg")
    bpy.ops.render.render(write_still=True)


def plate(name,p,scale,yaw=0):
    for ob in loaded(out_paths[name]):
        ob.matrix_world=Matrix.Translation(p)@Matrix.Rotation(yaw,4,"Z")@Matrix.Scale(scale,4)@ob.matrix_world


clear_scene()
plate("fern",(-.66,0,0),1,-.26)
plate("verge",(.60,0,0),1,.6)
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.003))
bpy.context.object.data.materials.append(mat("Deep loam studio",(.080,.065,.047)))
S.world=bpy.data.worlds.new("Warm gray gallery")
S.world.color=(.46,.42,.36)
sun((.45,.48,-1),2.40,(1,.88,.71))
camera((.18,-3.8,1.48),(0,0,.24),ortho=2.8)
if not breeze_dir and os.environ.get("WSC_UNDERSTORY_TRAIL_ONLY")!="1":
    render("understory-pair",1390,925)

clear_scene()
bpy.ops.mesh.primitive_plane_add(size=130,location=(0,0,-.01))
bpy.context.object.data.materials.append(mulch_material())


def cache(p):
    templates=loaded(p)
    t=[(o.data,o.matrix_world.copy()) for o in templates]
    for o in templates:
        bpy.data.objects.remove(o,do_unlink=True)
    return t


def instance(template,label,xyz,rotation,scale,unique=False):
    trans=Matrix.Translation(xyz)@Matrix.Rotation(rotation,4,"Z")@Matrix.Scale(scale,4)
    for d,m in template:
        ob=bpy.data.objects.new(label,d.copy() if unique else d)
        S.collection.objects.link(ob)
        ob.matrix_world=trans@m
        if unique:
            ob.data.shape_keys.animation_data_clear()
            breeze_slots.append((label,ob,tuple(xyz),rotation,scale))


rock=cache(asset/"wsc-prop-036-landscape-boulder.glb")
flwr=cache(asset/"wsc-prop-047-wildflower-clump-far.glb")
new={n:cache(p) for n,p in out_paths.items()}
dec=cache(asset/"wsc-prop-012-deciduous-tree-far.glb")
pine=cache(asset/"wsc-prop-046-conifer-tree-far.glb")
def hills(x,y):
    t=max(0,y-8.2)
    bend=.9*math.sin(t*.19)
    side=1-math.exp(-max(0,abs(x-bend)-1.65)**2/16)
    sweep=min(1,t/11)
    return .078*t + side*(1.8+.79*math.sin(x*.31+y*.13))*sweep

for template,x,y,yaw,q in ((dec,-4.9,9.0,.49,.74),(pine,4.9,11,-.4,.69),
                            (pine,-3.8,18,1.1,.78),(dec,6.3,18,.94,.82),
                            (pine,1.80,26,2.1,.89),(pine,-7.1,13,1.4,.88),
                            (pine,-2.8,32,-.42,1.1),(dec,6.8,30,1.64,.95),
                            (pine,-6.7,25,.19,1.0)):
    instance(template,"Pinned distance tree",(x,y,hills(x,y)-.04),yaw,q)
# Behind the measured stretch, an uphill stage masks the flat horizon.
# This terrain exists only in the rendered composition.
cols,rows=37,61
v=[(x,y,hills(x,y)-.008) for r in range(rows) for c in range(cols)
   for x,y in ((c-18,8.2+r*.64),)]
f=[(r*cols+c,r*cols+c+1,(r+1)*cols+c+1,(r+1)*cols+c)
   for r in range(rows-1) for c in range(cols-1)]
d=bpy.data.meshes.new("Presentation hillside")
d.from_pydata(v,[],f)
d.update()
o=bpy.data.objects.new("Presentation hillside",d)
S.collection.objects.link(o)
d.materials.append(bpy.data.materials["Rock trail · layered dirt"])
for rgb in ((.13,.155,.064),(.117,.142,.054),(.15,.169,.072)):
    d.materials.append(mat("Distant moss and soil",rgb,.83))
for poly in d.polygons:
    x,y,z=poly.center
    t=max(0,y-8.2)
    if abs(x-.9*math.sin(t*.19))>2.5+.45*math.cos(y*.81):
        poly.material_index=1+(poly.index*19)%3
    poly.use_smooth=True
instance(rock,"Pinned boulder",(-2.42,1.54,0),.29,.73)
instance(rock,"Pinned boulder",(2.44,2.8,0),.84,.57)
instance(rock,"Pinned boulder",(-3.55,6.2,-.06),-2.3,1.08)
instance(rock,"Pinned boulder",(3.05,7.6,-.06),-1.1,.99)
for x,y,z,a,q in ((-1.75,.12,0,1,.77),(2.05,.90,0,-1,.55),(-2.25,4.8,0,1.9,.65)):
    instance(flwr,"Pinned flower donor",(x,y,z),a,q)
rng=random.Random(27)
clearances=[]
for name,fits in {"fern":[(-1.72,-.9,.92),(-2.28,2.8,.87),(1.72,.34,1.05),
                          (1.97,4.6,.78),(-1.75,5.2,.69),(-2.62,6.8,1.16)],
                  "verge":[(-1.38,-1.3,.71),(1.45,-1.5,.79),(-1.57,-.08,.63),
                           (-1.64,1.7,.74),(1.45,1.6,.68),(2.30,3.7,.82),
                           (1.84,5.09,.91),(-1.81,3.6,.82),(-1.53,7.6,.68)]}.items():
    for x,y,q in fits:
        instance(new[name],name,(x,y,0),rng.random()*math.tau,q,unique=bool(breeze_dir))
        clearances.append(abs(x)-stats[name]["radius_m"]*q-1)
assert min(clearances)>.02

# Thin path margin scatter is review composition, not an asset.
r=mat("Biscuit stone fines",(.30,.203,.105),.87)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
d=bpy.context.object.data
d.materials.append(r)
bpy.data.objects.remove(bpy.context.object,do_unlink=True)
for i in range(55):
    x=rng.choice((-1,1))*rng.uniform(.95,2.8)
    o=bpy.data.objects.new("Presentation gravel",d)
    S.collection.objects.link(o)
    o.location=(x,rng.uniform(-2.5,8),rng.uniform(-.022,.025))
    o.rotation_euler.z=rng.random()*math.tau
    o.scale=(rng.uniform(.04,.15),rng.uniform(.06,.16),rng.uniform(.017,.062))
S.world=bpy.data.worlds.new("Lookout clouds")
S.world.use_nodes=True
n=S.world.node_tree.nodes
sky=n.new("ShaderNodeTexSky")
sky.sky_type="NISHITA"
sky.sun_disc=False
sky.sun_elevation=.40
sky.sun_rotation=2
S.world.node_tree.links.new(sky.outputs[0],n["Background"].inputs[0])
n["Background"].inputs[1].default_value=.21
sun((.69,.46,-.74),2.8,(1,.88,.63))
camera((-.20,-3.45,1.18),(.15,2.65,.46),lens=34)
if breeze_dir:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"lookout-breeze"))
    from staging import render_breeze
    render_breeze(S,O,breeze_slots,camera)
    raise SystemExit(0)
render("understory-trail",1540,1040)

(O/"lookout-understory-proof.json").write_text(json.dumps({
    "scope":"Optional understory studies, not native placements, physics or flora approval.",
    "donors":pins,"exports":stats,"new_prototype_instances":len(clearances),
    "staged_path_clear_width_m":2,"conservative_minimum_new_plant_margin_m":round(min(clearances),5),
    "clearance_scope":"Radial extent and recorded scale of new foliage only; not collision.",
},indent=2)+"\n")
