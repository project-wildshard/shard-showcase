"""One replaceable maintenance shelf fitted to the archived E3 screen post."""
import hashlib
import json
from math import cos, sin, tau
from pathlib import Path
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
donor=root/"public/assets/wildshard-art/e3-suspended-pillar-screen.glb"
donor_sha="b97aac0a7b80e50f2c2d066e51e89cbf32c1ccbed65b83cfd776c9b03c65f69e"
assert hashlib.sha256(donor.read_bytes()).hexdigest()==donor_sha
out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
out.mkdir(parents=True,exist_ok=True)
def clear():
    for ob in tuple(bpy.context.scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
clear()
parts=[]
def mat(name,rgb,metal=.0,rough=.63,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    for key,value in [("Base Color",(*rgb,1)),("Metallic",metal),("Roughness",rough),
                      ("Emission Color",(*rgb,1)),("Emission Strength",emission)]:
        p.inputs[key].default_value=value
    return m
iron=mat("Graphite enamel",(.056,.077,.086),.58)
zinc=mat("Rolled zinc",(.25,.30,.32),.65,.46)
orange=mat("Foundry ochre",(.64,.239,.052),.24,.50)
rubber=mat("Ribbed landing mat",(.058,.061,.048),.05,.83)
teal=mat("Service ready inlay",(.055,.46,.38),.23,.53,.40)

def mesh(name,v,f,m):
    q=bpy.data.meshes.new(name);q.from_pydata(v,[],f);q.update()
    o=bpy.data.objects.new(name,q);bpy.context.collection.objects.link(o);q.materials.append(m);parts.append(o)
    return o
def box(name,c,d,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=c)
    o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m);parts.append(o)
    if bevel:
        b=o.modifiers.new("Dressed edge","BEVEL");b.width=bevel;b.segments=1
    return o
def beam(name,p,q,m,d):
    u,v=Vector(p),Vector(q);delta=v-u
    o=box(name,(u+v)/2,(*d,delta.length),m,.012)
    o.rotation_mode="QUATERNION";o.rotation_quaternion=delta.to_track_quat("Z","Y")
# Blender stock 12-sided cylinder vertices line up at 30° increments.
# Orient the mating surface to the actual donor angular basis measured below.
def ring(name,phase,z):
    steps=7  # seven vertices along the outward-facing half of each ring
    vv=[(r*cos(phase+tau*i/12),r*sin(phase+tau*i/12),z+h)
        for r,h in ((.557,-.052),(.615,-.052),(.615,.052),(.557,.052)) for i in range(-3,4)]
    ff=[(k*steps+i,k*steps+i+1,((k+1)%4)*steps+i+1,((k+1)%4)*steps+i)
        for k in range(4) for i in range(steps-1)]
    ff.extend([(0,7,14,21),(27,20,13,6)])
    return mesh(name,vv,ff,zinc)

def bring(p):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    return sorted(set(bpy.context.scene.objects)-before,key=lambda x:x.name)
def world_mesh(obs):
    vv,ff=[],[]
    for o in obs:
        if o.type!="MESH":continue
        base=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        ff.extend(tuple(base+i for i in f.vertices) for f in o.data.polygons)
    return vv,ff
from math import atan2
pole=Vector((4,0,4.02))
v,f=world_mesh(bring(donor))
pick=next(q for q in v if abs(((q.x-4)**2+q.y*q.y)**.5-.55)<1e-6 and .43<q.z<.45)
phase=(atan2(pick.y,pick.x-4)+tau/24)%(tau/12)-tau/24
assert abs(phase)<1e-5, phase
screen_bvh=BVHTree.FromPolygons(v,f)
clear()
for z in (-.36,-.011):
    ring("Split collar sleeve",phase,z)
    for y in (-.255,.255):
        box("Collar clamp lug",(.573,y,z),(.14,.125,.075),iron,.01)
        box("Fastener inset",(.653,y,z),(.039,.052,.053),zinc,.005)
for y in (-.435,.435):
    beam("Diagonal shelf brace",(.611,y*.49,-.413),(1.88,y,.034),iron,(.115,.125))
    beam("Longitudinal frame",(.59,y,.015),(2.215,y,.015),iron,(.108,.145))
box("Chamfered perimeter pan",(1.425,0,.082),(1.68,1.302,.145),orange,.040)
box("Raised landing pad",(1.44,0,.157),(1.24,1.02,.053),rubber,.014)
for y in (-.556,.556):
    box("Visible side reveal",(1.527,y,.17),(1.30,.053,.017),zinc,.005)
for x in (.98,1.23,1.48,1.73,1.98):
    for s in (-1,1):
        box("Traction rib",(x,s*.339,.184),(.039,.22,.012),iron,.003)
for y in (-.375,0,.375):
    box("Outboard status inlay",(2.199,y,.145),(.061,.205,.032),teal,.007)
scene=bpy.context.scene
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
o=bpy.context.object;o.name="E3 bolt-on maintenance perch"
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
glb=out/"e3-maintenance-perch.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,export_texcoords=False,export_animations=False)
clear()
perch=bring(glb)
pv,pf=world_mesh(perch)
pb=BVHTree.FromPolygons(pv,pf)
gaps=[]
for z in (-.36,-.011):
    for i in range(24):
        t=phase-tau/4 + tau*(i+.27)/48
        d=Vector((cos(t),sin(t),0))
        dst=screen_bvh.ray_cast(pole+Vector((0,0,z)),d,.600)[3]
        inside=pb.ray_cast((0,0,z),d,.700)[3]
        assert dst is not None and inside is not None
        gap=inside-dst
        assert .005<gap<.009, (z,i,gap)
        gaps.append(gap)
top_checks=[]
for i in range(7):
    x=.99+i*.15
    for y in (-.44,-.22,0,.22,.44):
        h=pb.ray_cast((x,y,.6),(0,0,-1),.6)[0]
        assert h is not None and .179<h.z<.20,(x,y,h)
        top_checks.append(float(h.z))
assert min(q.x for q in pv)>-.00001, "Inboard cloth must not overlap the cradle"
for height in (.85,1.7,2.1):
    for i in range(33):
        x=-3.2+.2*i
        assert not pb.ray_cast(Vector((x,-3,height))-pole,(0,1,0),6)[0]
blob=glb.read_bytes()
g=json.loads(blob[20:20+struct.unpack_from("<I",blob,12)[0]])
pr=g["meshes"][0]["primitives"]
tris=sum(g["accessors"][p["indices"]]["count"]//3 for p in pr)
assert len(g["meshes"])==1 and len(pr)==5 and tris<3000 and len(blob)<120000
assert not any(g.get(k) for k in ("textures","images","skins","animations"))
dims=list(zip(*(tuple(q) for q in pv)))
proof={"donorSHA256":donor_sha,"assetSHA256":hashlib.sha256(blob).hexdigest(),
       "bytes":len(blob),"triangles":tris,"primitives":len(pr),"mountBlenderLocal":tuple(pole),
       "localBoundsBlender":[[round(min(a),6),round(max(a),6)] for a in dims],
       "radialFitSamples":len(gaps),"radialFitGapMm":[round(min(gaps)*1000,3),round(max(gaps)*1000,3)],
       "padPlaneSamples":len(top_checks),"nominalCenteredPadClearXzM":[1.24,1.02],
       "untouchedCentralRays":99,"newActor":False,"nativePlacement":False}
(out/"e3-maintenance-perch-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print(proof,flush=True)
if "--no-render" in sys.argv:sys.exit(0)
for o in perch:
    if o.parent not in perch:o.location+=pole
bring(donor)
floor=mat("Workshop lean concrete",(.125,.149,.162),.08,.84)
bpy.ops.mesh.primitive_plane_add(size=120)
bpy.context.object.data.materials.append(floor)
scene.world.color=(.27,.31,.38)
scene.render.engine="CYCLES";scene.cycles.samples=27;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(loc,p,w,light,s):
    bpy.ops.object.light_add(type="AREA",location=loc)
    ob=bpy.context.object;ob.data.energy=w;ob.data.color=light;ob.data.shape="DISK";ob.data.size=s;aim(ob,p)
area((1,-6,12),(3,0,3.5),2400,(.68,.82,1),8)
area((8,3,9),(4,0,4),3100,(1,.63,.41),6)
for name,pos,target,lens,wh in [
    ("context",(12,-17,7.4),(.7,0,3.4),47,(1300,890)),
    ("detail",(8.4,-5.7,6.2),(4.95,0,4),57,(1120,900)),
]:
    bpy.ops.object.camera_add(location=pos)
    c=bpy.context.object;aim(c,target);c.data.lens=lens;scene.camera=c
    scene.render.resolution_x,scene.render.resolution_y=wh;scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    assert all(.025<p.x<.975 and .025<p.y<.975 for p in (world_to_camera_view(scene,c,pole+q) for q in pv))
    scene.render.image_settings.file_format="WEBP";scene.render.image_settings.quality=90
    scene.render.filepath=str(out/f"nov25-e3-perch-{name}.webp")
    bpy.ops.render.render(write_still=True)
