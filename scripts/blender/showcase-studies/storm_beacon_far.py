"""Verify a compact beacon tower with the original charged insert."""
import hashlib
import json
from math import cos, sin, tau, hypot, radians
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
tower="wsc-kit-007-storm-beacon.glb"
lamp="wsc-kit-007-storm-beacon-charged-lamp.glb"
far=out/"far/wsc-kit-007-storm-beacon-far.glb"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(assets/tower)=="3a525f2637d5150a1e5a85c04640d6a57772c842731f063aa429142810239833"
assert sha(assets/lamp)=="ab7445a6977c9af5cea7a31618a9c660f539e1026e23e61b1bbc2b3426b77a5d"
def clear():
    for o in tuple(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
def bring(path, offset=(0,0,0)):
    old=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    new=sorted(set(bpy.context.scene.objects)-old,key=lambda q:q.name)
    for o in new:
        if o.parent not in new:o.location+=Vector(offset)
    bpy.context.view_layer.update()
    return new
def mesh(path):
    clear()
    v,f=[],[]
    for o in bring(path):
        if o.type!="MESH":continue
        i=len(v);v.extend(o.matrix_world@p.co for p in o.data.vertices)
        f.extend(tuple(i+j for j in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(v,f),v,f
nb,nv,nf=mesh(assets/tower)
fb,fv,ff=mesh(far)
_,lv,_=mesh(assets/lamp)
box=lambda v:[[round(f(p[d] for p in v),6) for f in (min,max)] for d in range(3)]
b0,b1=box(nv),box(fv)
assert b0[2][0]==b1[2][0]==0 and max(abs(a-b) for aa,bb in zip(b0,b1) for a,b in zip(aa,bb))<.008,(b0,b1)
def projected_clear(ps):
    xy=[(p.x,p.y) for p in ps]
    edges=list(zip(xy,xy[1:]+xy[:1]))
    signs=[x*u2-y*u1 for (x,y),(u1,u2) in edges]
    if min(signs)>1e-8 or max(signs)<-1e-8:return 0
    best=100
    for (x,y),(xx,yy) in edges:
        dx,dy=xx-x,yy-y;l=dx*dx+dy*dy
        t=min(1,max(0,-(x*dx+y*dy)/l)) if l>1e-12 else 0
        best=min(best,hypot(x+t*dx,y+t*dy))
    return best
lamp_r=max(hypot(p.x,p.y) for p in lv)
gap=min(projected_clear([fv[i] for i in t]) for t in ff if max(fv[i].z for i in t)>4.671)-lamp_r
assert gap>.055,gap
# Orthographic masks, eight azimuths at two elevations, unlit geometry.
# Each A/B pair uses exactly the same grid, no origin or bounds normalization.
def scores(az,up):
    gaze=Vector((cos(az)*cos(up),sin(az)*cos(up),sin(up)))
    right=Vector((-sin(az),cos(az),0))
    vertical=gaze.cross(right)
    center=Vector((0,0,2.74))+gaze*12
    union=inter=0
    for j in range(144):
        start=center+vertical*((j+.5)*6.1/144-3.05)
        for i in range(76):
            p=start+right*((i+.5)*3.25/76-1.625)
            a=nb.ray_cast(p,-gaze,24)[0] is not None
            b=fb.ray_cast(p,-gaze,24)[0] is not None
            union+=a or b;inter+=a and b
    return round(inter/union,5)
masks=[scores(tau*i/8,radians(y)) for y in (0,8) for i in range(8)]
assert min(masks)>.96,masks
def stats(path):
    b=path.read_bytes();n=struct.unpack_from("<I",b,12)[0];d=json.loads(b[20:20+n])
    assert not any(d.get(k) for k in ("images","animations","skins","textures"))
    assert not any(m.get("emissiveFactor") for m in d["materials"])
    assert all("translation" not in o and "matrix" not in o for o in d["nodes"])
    p=[v for m in d["meshes"] for v in m["primitives"]]
    return dict(bytes=len(b),triangles=sum(d["accessors"][v["indices"]]["count"]//3 for v in p),
                primitives=len(p),sha256=sha(path))
full,reduced=stats(assets/tower),stats(far)
assert reduced["bytes"]<full["bytes"]*.55 and reduced["triangles"]<full["triangles"]*.52
proof=dict(full=full,far=reduced,originalLampSHA256=sha(assets/lamp),
           towerBoundsBlender={"original":b0,"far":b1},
           conservativeLampRadialGapM=round(gap,6),maskGrid=[76,144],
           pitchDegrees=[0,8],azimuthStepDegrees=45,maskIoU=masks,
           automaticLOD=False,nativePlacement=False)
(out/"e9-storm-beacon-far-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print(proof,flush=True)
if "--no-render" in sys.argv:sys.exit(0)
clear()
scene=bpy.context.scene
sizes=(-1.88,1.88)
for x,p in zip(sizes,(assets/tower,far)):
    bring(p,(x,0,14.533658));bring(assets/lamp,(x,0,14.533658))
def slab(name,p,d,col):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    o.data.materials.append(m)
    return o
slab("Band paving",(0,0,-.08),(240,240,.16),(.11,.14,.15))
# Two identical narrower stands for the A/B stand-in; not a map proposal.
for x in sizes:
    slab("Graphite test stand",(x,0,7.2668),(2.80,2.80,14.5336),(.073,.091,.10))
scene.world.color=(.08,.10,.16)
scene.render.engine="CYCLES";scene.cycles.samples=28;scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.light_add(type="SUN",location=(4,-8,25))
sun=bpy.context.object;sun.data.energy=1.80;sun.data.color=(.62,.75,1);sun.data.angle=.26;aim(sun,(0,0,14))
bpy.ops.object.light_add(type="AREA",location=(-5,-3,21))
ob=bpy.context.object;ob.data.energy=660;ob.data.color=(1,.65,.38);ob.data.size=7;aim(ob,(0,0,17))
for n,p,t,typ,scale,dim in [
    ("detail",(0,-34,22),(0,0,17.0),"ORTHO",9.8,(1300,870)),
    ("distance",(0,-104,1.70),(0,0,11.3),"PERSP",20.0,(804,1748)),
]:
    bpy.ops.object.camera_add(location=p)
    cam=bpy.context.object;cam.data.type=typ;aim(cam,t);scene.camera=cam
    if typ=="ORTHO":cam.data.ortho_scale=scale
    else:cam.data.lens=scale
    scene.render.resolution_x,scene.render.resolution_y=dim;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="WEBP";scene.render.image_settings.quality=90
    scene.render.filepath=str(out/f"nov25-e9-beacon-far-{n}.webp")
    bpy.ops.render.render(write_still=True)
