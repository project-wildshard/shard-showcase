"""Two textureless leaf-litter inserts fitted to the existing avenue paving."""
import bpy, hashlib, json, math, random, struct, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/"public/assets/wildshard-art"
OUT=Path(sys.argv[sys.argv.index("--")+1]); OUT.mkdir(parents=True,exist_ok=True)
DONORS={
    "wsc-module-004-avenue-paving":"049c6b7e91fa8d05a84178d3280eee72c4221728e535b806b5b4434509936739",
    "wsc-prop-014-planter-bed":"ac39cc51273c0d25c3b5c4cb957b4c71e4d427992b9d219152f89195332da7d7",
    "wsc-prop-012-deciduous-tree":"83685e45bd4ef2af08941de87909aaf0f7078dbecfe784bc06a9fc8fc4d8a355",
}
def clear():
    for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def bring(n):
    src=ASSETS/f"{n}.glb"
    if n in DONORS:assert hashlib.sha256(src.read_bytes()).hexdigest()==DONORS[n],n
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(src))
    return sorted(set(bpy.context.scene.objects)-before,key=lambda o:o.name)
def place(obs,p,angle=0):
    for o in obs:
        if o.parent not in obs:
            o.location+=Vector(p);o.rotation_euler.z+=angle
    bpy.context.view_layer.update()
clear()
pavers=bring("wsc-module-004-avenue-paving")
bpy.context.view_layer.update()
ds=bpy.context.evaluated_depsgraph_get()
vertices,faces=[],[]
for o in pavers:
    if o.type!="MESH":continue
    e=o.evaluated_get(ds); m=e.to_mesh()
    base=len(vertices)
    vertices.extend(e.matrix_world@v.co for v in m.vertices)
    faces.extend(tuple(base+i for i in f.vertices) for f in m.polygons)
    e.to_mesh_clear()
bvh=BVHTree.FromPolygons(vertices,faces)
def stone(x,y):
    hit,n,_,_=bvh.ray_cast((x,y,.20),(0,0,-1),.23)
    if hit is None or n.z<.80:return None
    return float(hit.z)
def srgb(n):
    x=n/255
    return x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4
palette=[tuple(map(srgb,p)) for p in (
    (169,83,29),(193,104,29),(201,126,40),(188,70,34),(126,55,27),(212,151,60),(135,90,44),(187,109,55))]
m=bpy.data.materials.new("Avenue oak litter | vertex color")
m.use_nodes=True
b=m.node_tree.nodes.get("Principled BSDF")
b.inputs["Roughness"].default_value=.79
b.inputs["Specular IOR Level"].default_value=.22
c=m.node_tree.nodes.new("ShaderNodeVertexColor");c.layer_name="LeafColor"
m.node_tree.links.new(c.outputs["Color"],b.inputs["Base Color"])
# A pointed, softly lobed oak-style silhouette and one raised midrib point.
leaf=((-0.56,0),(-.38,-.34),(-.13,-.43),(-.05,-.30),(.19,-.36),(.34,-.21),(.49,0),
      (.33,.19),(.17,.37),(-.06,.31),(-.17,.45),(-.41,.31),(0,0))
def one(label,side,total,seed):
    rng=random.Random(seed)
    vv,ff,cc,centers=[],[],[],[]
    heights=[]
    for _ in range(5000):
        if len(centers)==total:break
        # Keep an irregular center-free stripe, not a line of confetti.
        y=rng.uniform(-3.31,3.31)
        if rng.random()>.45+.45*(.5+.5*math.sin(1.68*y+.8*side)):continue
        edge=rng.betavariate(1.3,3.0)
        x=side*(1.94-.64*edge)
        size=rng.uniform(.085,.178); angle=rng.uniform(0,math.tau)
        ratio=rng.uniform(.59,1.01)
        if any((x-u)**2+(y-v)**2<(.044+.20*(size+t))**2 for u,v,t in centers):continue
        co,si=math.cos(angle),math.sin(angle)
        points=[(x+size*(a*co-b*si*ratio),y+size*(a*si+b*co*ratio)) for a,b in leaf]
        samples=[stone(a,b) for a,b in points]
        if None in samples or max(samples)-min(samples)>.008:continue
        if not all(1.24<abs(a)<2.04 and abs(b)<3.47 for a,b in points):continue
        base_z=max(samples)+.0018
        curl=rng.uniform(.003,.011)
        rise=[curl*(.58*abs(a)+max(.2-abs(b),0)*.3) for a,b in leaf[:-1]]+[curl]
        points3=[(a,b,base_z+z) for (a,b),z in zip(points,rise)]
        # Also test each triangle centroid; reject any interior pierce/overhang.
        deltas=[p[2]-h for p,h in zip(points3,samples)]
        valid=True
        for k in range(12):
            tri=(points3[k],points3[(k+1)%12],points3[-1])
            px,py,pz=(sum(p[i] for p in tri)/3 for i in range(3))
            hit=stone(px,py)
            if hit is None or not .0013<=pz-hit<=.021:
                valid=False;break
            deltas.append(pz-hit)
        if not valid:continue
        centers.append((x,y,size))
        i=len(vv); vv+=points3
        ink=palette[rng.randrange(len(palette))]
        for k in range(12):
            ff.append((i+k,i+(k+1)%12,i+12))
        for k in range(13):
            gain=rng.uniform(.89,1.06) if k<12 else 1.15
            cc.append(tuple(min(1,f*gain) for f in ink)+(1,))
        heights.extend(deltas)
    assert len(centers)==total,(len(centers),total)
    assert min(heights)>.0012 and max(heights)<.021
    mesh=bpy.data.meshes.new(label);mesh.from_pydata(vv,[],ff);mesh.update()
    assert not mesh.validate()
    for face in mesh.polygons:face.use_smooth=True
    colors=mesh.color_attributes.new(name="LeafColor",type="BYTE_COLOR",domain="POINT")
    for color,rgb in zip(colors.data,cc):color.color=rgb
    mesh.materials.append(m)
    obj=bpy.data.objects.new(label,mesh);bpy.context.scene.collection.objects.link(obj)
    dest=OUT/f"{label}.glb"
    bpy.ops.object.select_all(action="DESELECT"); obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format="GLB",use_selection=True,export_animations=False)
    raw=dest.read_bytes()
    doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    assert len(doc["meshes"])==len(doc["materials"])==1
    primitive,=doc["meshes"][0]["primitives"]
    assert "COLOR_0" in primitive["attributes"] and not any(key in doc for key in ("images","textures","skins","animations"))
    assert doc["accessors"][primitive["indices"]]["count"]==36*total and len(raw)<47000
    return obj,dict(asset=dest.name,sha256=hashlib.sha256(raw).hexdigest(),size=len(raw),count=total,
                     triangles=12*total,nearest_center_x=min(abs(x) for x,y,z in vv),clearance_m=[min(heights),max(heights)])

near,a=one("w0b-avenue-litter-windrow",-1,78,2026112501)
far,b=one("w0b-avenue-litter-drift",1,41,2026112502)
(OUT/"proof.json").write_text(json.dumps(dict(paving_sha256=DONORS["wsc-module-004-avenue-paving"],
    scope="optional avenue-edge visual overlays, fit to one exact 4.2 m x 7.2 m donor at identity",
    center_clear_width=2*min(a["nearest_center_x"],b["nearest_center_x"]), checks_per_leaf=25, variants=[a,b]),indent=2)+"\n")
# Reimport exact delivered triangles; all other assets are staging context.
bpy.data.objects.remove(near,do_unlink=True);bpy.data.objects.remove(far,do_unlink=True)
for summary in (a,b):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(OUT/summary["asset"]))
    (leaf_mesh,)=set(bpy.context.scene.objects)-before
    bpy.context.view_layer.update()
    assert leaf_mesh.type=="MESH" and len(leaf_mesh.data.polygons)==summary["triangles"]
    points=[leaf_mesh.matrix_world@v.co for v in leaf_mesh.data.vertices]
    assert len(points)==13*summary["count"]
    assert min(abs(p.x) for p in points)>1.29 and max(abs(p.x) for p in points)<2.04
    for p in points+[sum((points[i] for i in f.vertices),Vector())/3 for f in leaf_mesh.data.polygons]:
        h=stone(p.x,p.y)
        assert h is not None and .0012<p.z-h<.021
if __import__('os').environ.get("WSC_LITTER_ONLY")=="1":raise SystemExit(0)
for y in (-7.2,7.2):place(bring("wsc-module-004-avenue-paving"),(0,y,0))
planter=bring("wsc-prop-014-planter-bed")
place(planter,(-2.99,.20,-.018),math.pi/2)
edge=max((o.matrix_world@Vector(p)).x for o in planter if o.type=="MESH" for p in o.bound_box)
place(planter,(-2.16-edge,0,0))
assert max((o.matrix_world@Vector(p)).x for o in planter if o.type=="MESH" for p in o.bound_box)<-2.15
place(bring("wsc-prop-012-deciduous-tree"),(-4.09,1.17,-.025),.28)
s=bpy.context.scene
floor=bpy.data.materials.new("Compact dry shoulder");floor.diffuse_color=(.151,.106,.066,1)
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.051))
bpy.context.object.data.materials.append(floor)
s.world=bpy.data.worlds.new("Late afternoon warm avenue")
s.world.use_nodes=True
bg=s.world.node_tree.nodes.get("Background")
bg.inputs[0].default_value=(.43,.58,.78,1);bg.inputs[1].default_value=.57
bpy.ops.object.light_add(type="SUN",location=(-8,-4,9))
sun=bpy.context.object
sun.rotation_euler=Vector((.60,.28,-.73)).to_track_quat("-Z","Y").to_euler()
sun.data.energy=2.75;sun.data.color=(1,.86,.66);sun.data.angle=.20
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
s.render.engine="CYCLES";s.cycles.samples=26;s.cycles.use_denoising=False
s.cycles.adaptive_threshold=.058;s.render.resolution_percentage=100
s.render.image_settings.file_format="WEBP";s.render.image_settings.quality=94
s.view_settings.view_transform="AgX"
def shot(name,eye,target,lens,w,h):
    cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens;s.render.resolution_x=w;s.render.resolution_y=h
    s.render.filepath=str(OUT/f"nov25-w0b-avenue-{name}.webp")
    bpy.ops.render.render(write_still=True)
shot("leaf-detail",(-1.00,-2.95,1.22),(-1.60,-.35,.06),37,1260,850)
shot("leaf-pair",(5.8,-7.2,7.4),(-.40,.65,.09),43,1370,895)
