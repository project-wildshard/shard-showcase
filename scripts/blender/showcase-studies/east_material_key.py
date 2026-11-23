"""Six East surface swatches assembled from existing GLBs. Not level geometry."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

root=Path(__file__).resolve().parents[3]
cfg=json.loads((root/"project/layouts/wsc-scene-005-east-material-key.json").read_text())
s=bpy.context.scene
out=output_directory()
clear_scene()
rng=random.Random(51)
buckets={}
cached={}

def mat(name,c,metal=.06,rough=.76):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*c,1)
    n=mat.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=rough
    return mat

border=mat("Ink framed substrate",(.055,.074,.084),.43)
metal=mat("Zinc corner details",(.18,.22,.24),.50)
ochre=mat("Ochre inlay",(.79,.46,.052),.14)
pale=mat("Pale inlay",(.68,.63,.46))
aqua=mat("Blue enamel reading line",(.039,.321,.366),.28)
ink=mat("Proof labels",(.73,.81,.74),.1)

def poly(g,m,vertices,faces):
    p,f=buckets.setdefault((g,m),([],[]));i=len(p);p.extend(vertices)
    f.extend(tuple(i+j for j in face) for face in faces)

def box(g,m,p,d):
    x,y,z=p;a,b,c=(v/2 for v in d)
    poly(g,m,[(x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
         ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)))

def load(spec):
    name,sha=spec
    if name in cached:return cached[name]
    p=root/"public/assets/wildshard-art"/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,p
    prev=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    got=sorted(set(s.objects)-prev,key=lambda x:x.name)
    mesh=[(o.data,o.matrix_world.copy()) for o in got if o.type=="MESH"]
    points=[w@v.co for m,w in mesh for v in m.vertices]
    lo,hi=[Vector([fn(v[k] for v in points) for k in range(3)]) for fn in (min,max)]
    for o in got:bpy.data.objects.remove(o,do_unlink=True)
    cached[name]=(mesh,lo,hi)
    return cached[name]

def instance(spec,p,maxsize):
    mesh,lo,hi=load(spec)
    span=hi-lo
    sc=min(maxsize[k]/max(.01,span[k]) for k in range(3))
    anchor=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    matrix=Matrix.Translation(Vector(p))@Matrix.Scale(sc,4)@Matrix.Translation(-anchor)
    for i,(m,w) in enumerate(mesh):
        o=bpy.data.objects.new(f"{spec[0]} | {i+1}",m);s.collection.objects.link(o);o.matrix_world=matrix@w
    return sc,tuple(round(x*sc,3) for x in span)

def text(n,x,y,size,material):
    cu=bpy.data.curves.new(n,"FONT");cu.body=n;cu.align_x="CENTER";cu.size=size;cu.materials.append(material)
    o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);o.location=(x,y,.014)

def tile_rows(g,pal,x,y,n,m):
    for j in range(m):
        depth=3.6/m
        w=4.64/n
        spans=[-2.32]+[-2.32+(i+.48*(j%2))*w for i in range(1,n)]+[2.32]
        for l,r in zip(spans,spans[1:]):
            box(g,rng.choice(pal),(x+(l+r)/2,y-1.8+(j+.5)*depth,-.06),(r-l-.018,depth-.018,.123))

metrics=[]
for i,c in enumerate(cfg["cards"]):
    x=((i%3)-1)*5.21;y=(1.0-2*(i//3))*2.23
    g=f"E{i+1:02d} | "+c["name"]
    pal=[mat(f"{g} | tone {j}",tuple(a*f for a in c["tone"])) for j,f in enumerate((.78,.88,.99,1.04,1.10,1.18))]
    box(g,border,(x,y-.23,-.205),(4.85,4.10,.34))
    box(g,pal[2],(x,y,-.073),(4.64,3.60,.146))
    if c["pattern"]=="limestone":tile_rows(g,pal,x,y,8,7)
    if c["pattern"]=="brick":tile_rows(g,pal,x,y,11,10)
    if c["pattern"]=="slab":tile_rows(g,pal,x,y,3,3)
    if c["pattern"]=="earth":
        for j in range(29):
            xx=rng.uniform(-2.17,2.17);yy=rng.uniform(-1.59,1.57)
            box(g,rng.choice(pal),(x+xx,y+yy,.003),(rng.uniform(.06,.24),rng.uniform(.035,.092),.008))
    if c["marks"] in ("ochre","pale"):
        mark=ochre if c["marks"]=="ochre" else pale
        for j in range(8):
            box(g,mark,(x-1.67,y-1.51+.43*j,.006),(.073,.27,.010))
        box(g,mark,(x-.70,y-1.56,.006),(1.84,.06,.01))
    if c["marks"]=="curve":
        vv=[]
        for j in range(24):
            a=math.radians(8+2.9*j)
            vv.extend((x+r*math.sin(a)-1.82,y-1.79+r*(1-math.cos(a)),.008) for r in (2.10,2.17))
        poly(g,pale,vv,[(2*j,2*j+2,2*j+3,2*j+1) for j in range(23)])
        box(g,aqua,(x-1.88,y-.6,.007),(.07,1.93,.009))
    deco_p=(x+.90,y+.88,.005)
    zcap=(1.48,1.49,1.55,1.66,1.34,.57)[i]
    scale,ds=instance(c["donor"],deco_p,(2.42,1.53,zcap))
    _,cs=instance(cfg["common_dock"],(x+.12,y-.61,.008),(1.62,1.32,.61))
    # Fixed fit prevents overhang and keeps the two visual cues distinct.
    assert ds[0]<=2.421 and ds[1]<=1.531 and cs[1]<1.33
    assert deco_p[1]-ds[1]/2>y-.61+cs[1]/2
    box(g,aqua,(x-2.22,y-1.89,.008),(.10,.25,.058))
    box(g,metal,(x+2.22,y-1.89,.008),(.11,.25,.058))
    text(f"E{i+1:02d}   /   {c['name'].upper()}",x,y-2.02,.225,ink)
    metrics.append({"reference":c["ref"],"donor":c["donor"][0],"uniform_studio_scale":round(scale,5)})
for (g,m),(v,f) in buckets.items():
    mesh=bpy.data.meshes.new(g);mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(g+" | "+m.name,mesh);o.data.materials.append(m);s.collection.objects.link(o)
(out/"validation.json").write_text(json.dumps({"id":cfg["asset_id"],"swatches":metrics,
    "distinct_donor_models":len(cached),"originals_unchanged":True,"runtime":False},indent=2)+"\n")

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(name,p,q,power,col,sz):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.color=col;d.shape="DISK";d.size=sz
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new("Slate atlas ambiance");s.world.color=(.18,.22,.26)
area("Warm directional light",(-6,-7,12),(0,0,0),4950,(1,.77,.51),12)
area("Soft skylight",(4,7,10),(0,0,0),4250,(.48,.71,1),11)
area("Neutral fill",(6,-7,9),(0,0,0),1500,(.69,.84,1),8)
base=mat("Slate canvas",(.042,.069,.091))
bpy.ops.mesh.primitive_plane_add(size=300,location=(0,0,-.385))
bpy.context.object.data.materials.append(base)
cam=bpy.data.cameras.new("Art swatches")
s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
cam.type="ORTHO"
s.render.engine="CYCLES";s.cycles.samples=58;s.cycles.use_denoising=False
s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=92
for name,pos,target,scale,res in (
 ("nov23-east-material-key",(0,-13,23),(0,.13,0),16.66,(1800,1050)),
 ("nov23-east-material-foundry",(-3,-8,5),(-5.21,-2.23,0),5.65,(1000,850)),
):
    s.camera.location=pos;aim(s.camera,target);cam.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=res
    s.render.filepath=str(out/(name+".jpg"));bpy.ops.render.render(write_still=True)
