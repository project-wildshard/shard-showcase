"""Matched West paving finish and an optional irregular pool overlay."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene,export,output_directory
out=output_directory()
s=bpy.context.scene
root=HERE.parents[2]/"public/assets/wildshard-art"
clear_scene()
pins={
 "wsc-arch-005-plaza-paving-kit.glb":"85b9ddb3f5c13a5168325fd4b6c34ccf0fde319a5c3511d67232ce6d762f97ea",
 "town-gate-merchant-house.glb":"266fc52858b80847add0627c536c1421d1305e3092c846625937d1d6d80017fe",
 "wsc-prop-004-lantern-post.glb":"fbaa76a0606141fcac37d45553b26072025586ac0f53be41d57daaf3beeb405b",
 "wall-lantern.glb":"bdbdce040eee6e60693e110cdcdb25e1abc93d80ed4f79f7d2e72fc5490ecc09",
 "quest-board.glb":"84b82ec701da4529f5d9403e137d10a28ea370b87ada4ba28f837dc0ba1472aa",
}
sources={}
for n,h in pins.items():
    path=root/n
    assert hashlib.sha256(path.read_bytes()).hexdigest()==h
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    added=set(s.objects)-old
    meshes=[(o.name,o.data,o.matrix_world.copy()) for o in sorted(added,key=lambda o:o.name) if o.type=="MESH"]
    vs=[m@v.co for _,d,m in meshes for v in d.vertices]
    bounds=[Vector(tuple(f(v[i] for v in vs) for i in range(3))) for f in (min,max)]
    center=(bounds[0]+bounds[1])/2
    center.z=bounds[0].z
    sources[n]=(meshes,center)
    for o in added:
        bpy.data.objects.remove(o,do_unlink=True)


def pose(p,angle=0,sc=1):
    return Matrix.Translation(p)@Matrix.Rotation(math.radians(angle),4,"Z")@Matrix.Scale(sc,4)


def place(n,xf,center=True):
    meshes,p=sources[n]
    if center:
        xf=xf@Matrix.Translation(-p)
    result=[]
    for name,mesh,m in meshes:
        o=bpy.data.objects.new(name,mesh)
        s.collection.objects.link(o)
        o.matrix_world=xf@m
        result.append(o)
    return result


pavers=[]
for x in (-4.8,0,4.8):
    for y in (-3.56,1.24,6.04):
        pavers+=place("wsc-arch-005-plaza-paving-kit.glb",pose((x,y,-.154)))
place("town-gate-merchant-house.glb",pose((.47,6.05,0),0,.86))
place("quest-board.glb",pose((.54,.33,0),0,.81))
lamps=[]
for xyz,yaw in [((-2.95,-.71,0),20),((3.05,-.21,0),-16),((3.45,3.55,0),-8)]:
    xf=pose(xyz,yaw)
    place("wsc-prop-004-lantern-post.glb",xf,False)
    place("wall-lantern.glb",xf@pose((0,-.182,2.27)),False)
    lamps.append(xf@Vector((0,-.809,2.449)))
bpy.context.view_layer.update()
vs=[];fs=[]
for o in pavers:
    base=len(vs)
    vs += [o.matrix_world@v.co for v in o.data.vertices]
    fs += [tuple(base+i for i in f.vertices) for f in o.data.polygons]
tree=BVHTree.FromPolygons(vs,fs)


def floor_z(x,y):
    hit=tree.ray_cast(Vector((x,y,.4)),Vector((0,0,-1)),1)[0]
    assert hit is not None,(x,y)
    return hit.z


def finish(name,col,rough,metal=0,coat=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*col,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    p.inputs["Coat Weight"].default_value=coat
    p.inputs["Coat Roughness"].default_value=.11
    p.inputs["IOR"].default_value=1.35
    return m


# The overlay is a deliberately opaque reflective art approximation,
# not simulation, displaced water or a new material on the donor.
core=finish("Pool | dark glossy surface",(.047,.055,.064),.095,.12,.46)
skin=finish("Pool | edge water film",(.058,.063,.063),.145,.065,.30)
lip=finish("Pool | sand at wet edge",(.077,.063,.042),.246,.02,.16)
overlay=[]
footprint_checks=[]
for j,(x,y,rx,ry,spin) in enumerate([
        (-.65,-3.65,1.32,.76,.21),(1.06,-2.57,.72,.43,1.15),
        (-1.40,-1.63,.67,.42,-.38),(2.26,-3.75,.45,.24,.6)]):
    n=48
    rims=[]
    for i in range(n):
        a=i*math.tau/n
        wave=1+.13*math.sin(3*a+j)+.09*math.cos(5*a-j)+.041*math.sin(11*a+.3*j)
        u,v=rx*wave*math.cos(a),ry*wave*math.sin(a)
        rims.append((u*math.cos(spin)-v*math.sin(spin),u*math.sin(spin)+v*math.cos(spin)))
    tested=[floor_z(x+u*k,y+v*k) for k in (0,.25,.50,.75,1) for u,v in rims]
    z=max(tested)+.0025
    assert z-min(tested)<.071,(j,z,min(tested),max(tested))
    footprint_checks.append({"puddle":j,"rays":len(tested),"floor_min_z":min(tested),
                   "floor_max_z":max(tested),"pool_z":z})
    p=[(x,y,z)]
    for k in (.925,.979,1):
        p.extend((x+u*k,y+v*k,z) for u,v in rims)
    faces=[(0,1+i,1+(i+1)%n) for i in range(n)]
    for k in range(2):
        for i in range(n):
            a=1+k*n+i;b=1+k*n+(i+1)%n
            faces.append((a,a+n,b+n,b))
    mesh=bpy.data.meshes.new("Irregular pool footprint "+str(j))
    mesh.from_pydata(p,[],faces)
    mesh.update()
    for m in (core,skin,lip):
        mesh.materials.append(m)
    for i,f in enumerate(mesh.polygons):
        f.material_index=i//n
    o=bpy.data.objects.new(mesh.name,mesh)
    s.collection.objects.link(o)
    overlay.append(o)

file=out/"w11a-plaza-pool-overlay.glb"
export(overlay,file)
for o in overlay:
    bpy.data.objects.remove(o,do_unlink=True)
old=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(file))
overlay=set(s.objects)-old
bpy.context.view_layer.update()
assert len([o for o in overlay if o.type=="MESH"])==4
assert file.stat().st_size<70000
wet={}
restore=[]
for o in pavers:
    for slot in o.material_slots:
        base=slot.material
        if base not in wet:
            m=base.copy()
            m.name=base.name+" | wet review"
            p=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
            col=p.inputs["Base Color"]
            assert not col.is_linked
            col.default_value=tuple(v*.68 for v in col.default_value[:3])+(1,)
            p.inputs["Roughness"].default_value=.285
            p.inputs["Coat Weight"].default_value=.47
            p.inputs["Coat Roughness"].default_value=.17
            wet[base]=m
        restore.append((slot,base,wet[base]))
        slot.link="OBJECT"
        slot.material=base


def aim(o,t):
    o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()


def light(name,kind,p,target,power,color,scale):
    d=bpy.data.lights.new(name,kind)
    d.energy=power
    d.color=color
    if kind=="POINT":
        d.shadow_soft_size=scale
    if kind=="SUN":
        d.angle=scale
    if kind=="AREA":
        d.shape="DISK"
        d.size=scale
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o)
    o.location=p
    if target is not None:aim(o,target)


s.world=bpy.data.worlds.new("Fixed wet comparison sky")
s.world.use_nodes=True
b=s.world.node_tree.nodes.get("Background")
b.inputs["Color"].default_value=(.105,.20,.39,1)
b.inputs["Strength"].default_value=.41
light("Cool edge","SUN",(-4,6,8),(0,0,0),.96,(.60,.74,1),.12)
light("Blue evening fill","AREA",(-3,-5,6),(0,0,0),430,(.51,.67,1),8)
light("Amber storefront bounce","AREA",(.3,3.2,2.3),(0,-2,.2),325,(1,.56,.25),2.8)
for j,p in enumerate(lamps):
    light("Pinned lantern emitter","POINT",p,None,(160,177,122)[j],(1,.59,.28),.17)
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.161))
bpy.context.object.data.materials.append(finish("Stone stage underlay",(.21,.154,.102),.8))
cd=bpy.data.cameras.new("W11a fixed paving camera")
cam=bpy.data.objects.new(cd.name,cd)
s.collection.objects.link(cam)
s.camera=cam
cam.location=(.34,-7.45,1.7)
aim(cam,(.27,.83,1.17))
cd.lens=32
s.render.engine="CYCLES"
s.cycles.samples=108
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.036
s.view_settings.view_transform="AgX"
s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1400
s.render.resolution_y=880
s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG"
s.render.image_settings.quality=92
bpy.context.view_layer.update()


def signature():
    return [(o.name,[v for r in o.matrix_world for v in r])
            for o in s.objects if o.type in ("CAMERA","LIGHT","MESH")]


fixed=signature()
for state in ("dry","wet"):
    for o in overlay:o.hide_render=(state=="dry")
    for slot,base,variant in restore:
        slot.material=base if state=="dry" else variant
    assert signature()==fixed
    s.render.filepath=str(out/f"nov24-west-plaza-{state}-finish.jpg")
    bpy.ops.render.render(write_still=True)
receipt={"geometry_camera_lights_matched":True, "donor_sha256":pins,
         "overlay_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
         "overlay_bytes":file.stat().st_size,"puddle_fit":footprint_checks,
         "overlay_triangles":sum(len(f.vertices)-2 for o in overlay if o.type=="MESH"
                                 for f in o.data.polygons),
         "mode":"opaque puddle appearance proxy, offline wet material review"}
(out/"w11a-plaza-wet-proof.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("W11A_WET_RECEIPT",json.dumps(receipt),flush=True)
