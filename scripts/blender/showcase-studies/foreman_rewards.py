"""E11d independent reward props. This does not create an actor or drops."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene,export,output_directory
D=output_directory()
assets=HERE.parents[2]/"public/assets/wildshard-art"
donor=assets/"west-plaza-empty-mounts.glb"
pin="3e7e28863742ebcdd2f494d97d98574d263d876dac01f03e21a2b0fd5b4a54c7"
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
clear_scene()
s=bpy.context.scene

def mat(name,c,met=0,rough=.46):
    a=bpy.data.materials.new(name);a.use_nodes=True
    bs=a.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*c,1)
    bs.inputs["Metallic"].default_value=met
    bs.inputs["Roughness"].default_value=rough
    return a

gold=mat("Satin ochre brass",(.58,.30,.055),.64,.35)
old=mat("Darkened brass",(.224,.113,.043),.62,.43)
iron=mat("Heat-darkened slot",(.033,.042,.039),.25,.57)
edge=mat("Burnished edges",(.82,.57,.189),.65,.32)
yellow=mat("Safety yellow high impact shell",(.91,.57,.026),.10,.35)
brim=mat("Amber underside",(.67,.35,.022),.10,.46)
liner=mat("Suspension headband",(.050,.071,.076),.04,.73)
cloth=mat("Blue graphite harness webbing",(.082,.13,.145),.05,.71)
steel=mat("Blackened rivets",(.140,.172,.162),.64,.37)
copper=mat("Worn hat ridge",(.77,.399,.023),.12,.47)

def box(name,p,d,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new("Sloped tool edge","BEVEL");b.width=min(bevel,min(d)*.24);b.segments=2
        bpy.ops.object.modifier_apply(modifier=b.name)
        n=o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
        bpy.ops.object.modifier_apply(modifier=n.name)
    return o

def mesh(name,v,f,palette,paint=None,smooth=False):
    d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update()
    assert not d.validate()
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
    for m in palette:d.materials.append(m)
    for i,p in enumerate(d.polygons):
        p.material_index=paint[i] if paint else 0;p.use_smooth=smooth
    return o

def oval_ring(name,p,r,thick,m):
    # Surface of a drilled, oblong retaining loop; its opening passes through Y.
    vertices=[];faces=[]
    for i in range(32):
        a=i*math.tau/32
        for j in range(8):
            z=j*math.tau/8
            vertices.append((p[0]+(r[0]+thick*math.cos(z))*math.cos(a),
                             p[1]+thick*math.sin(z),
                             p[2]+(r[1]+thick*math.cos(z))*math.sin(a)))
    for i in range(32):
        for j in range(8):
            k=(i+1)%32;l=(j+1)%8
            faces.append((i*8+j,i*8+l,k*8+l,k*8+j))
    return mesh(name,vertices,faces,[m],smooth=True)

def cylinder(name,p,r,depth,m,orient=(0,0,0),count=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=count,radius=r,depth=depth,location=p,rotation=orient)
    o=bpy.context.object;o.name=name;o.data.materials.append(m)
    return o

def joined(obs,name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=o.data.name=name
    s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    return o

body=box("Whistle rounded chamber",(-.019,0,.019),(.073,.030,.038),gold,.005)
gap=box("Slot cutter",(-.033,0,.037),(.024,.015,.024),iron,.002)
body.data.materials.append(iron)
b=body.modifiers.new("Cut mouth vent","BOOLEAN");b.operation="DIFFERENCE";b.solver="EXACT";b.object=gap
bpy.context.view_layer.objects.active=body
bpy.ops.object.modifier_apply(modifier=b.name);bpy.data.objects.remove(gap,do_unlink=True)
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.dissolve_degenerate(bm,dist=.00002,edges=list(bm.edges))
bm.to_mesh(body.data);bm.free();body.data.update()
whistle=[body,box("Pressed mouthpiece",(-.059,0,.024),(.027,.026,.022),gold,.004),
    box("Mouth dark insert",(-.073,0,.026),(.002,.015,.005),iron,.001),
    box("Welded lanyard lug",(.020,0,.018),(.016,.019,.020),old,.002),
    oval_ring("Right safety loop",(.042,0,.019),(.017,.011),.0033,edge),
    box("Stamped bracket",(-.014,-.016,.017),(.031,.003,.014),old,.002)]
# Small recessed cast countersinks, read as wear at the display scale.
for x in (-.040,.002):
    whistle.append(cylinder("Recessed end cap", (x,-.0165,.018),.004,.0028,edge,(math.pi/2,0,0)))
W=joined(whistle,"Foremans_Whistle")

def cap_surface():
    # Closed double-wall shell, not a solid ellipsoid: opening faces -Z.
    N=44; radius=(.132,.145); verts=[];faces=[];pa=[]
    rows=[("outer",u) for u in (0,.16,.33,.51,.69,.84,.95,1.02,1.20,1.37,1.51)]
    for _,a in rows:
        for i in range(N):
            t=math.tau*i/N
            verts.append((radius[0]*math.cos(t)*math.cos(a),
                          radius[1]*math.sin(t)*math.cos(a),
                          .015+.152*math.sin(a)))
    for a in reversed([u for _,u in rows]):
        for i in range(N):
            t=math.tau*i/N
            verts.append(((radius[0]-.0046)*math.cos(t)*math.cos(a),
                          (radius[1]-.0048)*math.sin(t)*math.cos(a),
                           .015+.1468*math.sin(a)))
    blocks=len(rows)*2
    for row in range(blocks-1):
        for i in range(N):
            j=(i+1)%N
            faces.append((row*N+i,row*N+j,(row+1)*N+j,(row+1)*N+i))
            pa.append(0 if row<len(rows)-1 else 1)
    for i in range(N):
        j=(i+1)%N
        faces.append(((blocks-1)*N+i,(blocks-1)*N+j,j,i));pa.append(1)
    # Replace the equatorial rim artifact at the poles with separate non-overlapping caps.
    # The two top rings are different radii and heights; surfaces meet at the open rim only.
    # Remove the band bridging outer-to-inner at the top before capping those holes.
    a=(len(rows)-1)*N
    del faces[a:a+N];del pa[a:a+N]
    faces += [tuple(range(a,a+N)),tuple(range(a+2*N-1,a+N-1,-1))]
    pa += [0,1]
    return mesh("Dome and exposed liner",verts,faces,[yellow,brim],pa,True)

def helmet_brim():
    # Extra depth on the forward (-Y) brim; the rear stays short.
    n=44;pts=[];face=[];pm=[]
    for layer in range(4):
        for i in range(n):
            a=math.tau*i/n
            ext=.009+.041*max(0,-math.sin(a))**6 if layer in (1,2) else -.008
            z=(.012 if layer in (0,1) else .004)-.010*max(0,-math.sin(a))**3 if layer in (1,2) else (.015 if layer==0 else .007)
            pts.append(((.131+ext)*math.cos(a),(.144+ext)*math.sin(a),z))
    for k in range(4):
        for i in range(n):
            j=(i+1)%n;l=(k+1)%4
            face.append((k*n+i,l*n+i,l*n+j,k*n+j));pm.append(0 if k in (0,1) else 1)
    return mesh("Vent-free raised safety brim",pts,face,[yellow,brim],pm,True)

def stripe():
    # Soft raised front-to-back crown ridge against the authored shell curve.
    v=[];f=[]
    for i in range(25):
        a=.12+i*(math.pi-.24)/24
        y=.145*math.cos(a);z=.015+.152*math.sin(a)
        w=.014+.003*math.sin(a)
        v.extend([(-w,y,z-.002),(-w*.65,y,z+.007),(0,y,z+.009),
                  (w*.65,y,z+.007),(w,y,z-.002)])
    for i in range(24):
        for j in range(4):
            k=i*5+j;f.append((k,k+5,k+6,k+1))
    return mesh("Formed crown reinforcement",v,f,[copper],smooth=True)

def headband():
    n=44;pts=[];faces=[]
    for rx,ry,z in [(.118,.129,.020),(.118,.129,.043),(.112,.121,.043),(.112,.121,.020)]:
        pts.extend((rx*math.cos(a*math.tau/n),ry*math.sin(a*math.tau/n),z) for a in range(n))
    for k in range(4):
        for i in range(n):
            j=(i+1)%n;l=(k+1)%4
            faces.append((k*n+i,k*n+j,l*n+j,l*n+i))
    return mesh("Replaceable inner head band",pts,faces,[liner],smooth=True)

def webbing(turn):
    vertices=[];faces=[]
    for i in range(15):
        u=(i-7)/7
        for w,t in [(-.009,0),(.009,0),(.009,.004),(-.009,.004)]:
            x,y=(u*.123,w)
            a,b=(x*math.cos(turn)-y*math.sin(turn),x*math.sin(turn)+y*math.cos(turn))
            vertices.append((a,b,.041+(.067 if turn>0 else .075)*(1-u*u)+t))
    for i in range(14):
        for j in range(4):
            k=(j+1)%4
            faces.append((i*4+j,i*4+k,(i+1)*4+k,(i+1)*4+j))
    faces += [(0,1,2,3),(59,58,57,56)]
    return mesh("Inset suspension strap",vertices,faces,[cloth],smooth=True)

chunks=[cap_surface(),helmet_brim(),stripe(),headband(),webbing(math.pi/4),webbing(-math.pi/4)]
for d in (-1,1):
    for y in (-.065,.058):
        chunks.append(cylinder("Side pin",(.119*d,y,.053),.0061,.008,steel,(0,math.pi/2,0)))
chunks.append(box("Adjustment buckle",(0,.124,.031),(.044,.012,.020),steel,.003))
H=joined(chunks,"Foreman_HardHat_WearPlane")

def coords(o):
    return [o.matrix_world@v.co for v in o.data.vertices]

def tree(o):
    return BVHTree.FromPolygons(coords(o),[tuple(p.vertices) for p in o.data.polygons])

def measure(o,name):
    f=D/(name+".glb");export([o],f)
    bpy.data.objects.remove(o,do_unlink=True)
    old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(f))
    m,=[x for x in set(s.objects)-old if x.type=="MESH"]
    bpy.context.view_layer.update()
    assert m.location.length<1e-6
    pts=coords(m);a,b=([k(p[i] for p in pts) for i in range(3)] for k in (min,max))
    m.data.calc_loop_triangles()
    assert all(p.area>1e-12 for p in m.data.polygons),(name, sorted(p.area for p in m.data.polygons)[:6])
    return m,{"name":name,"bytes":f.stat().st_size,"triangles":len(m.data.loop_triangles),
              "dimensions_m":[round(q-p,6) for p,q in zip(a,b)],
              "sha256":hashlib.sha256(f.read_bytes()).hexdigest()}

W,w=measure(W,"e11d-foreman-whistle")
H,h=measure(H,"e11d-foreman-hard-hat")
assert w["bytes"]<75000 and h["bytes"]<160000
whistle_tree=tree(W)
# Negative ray through center of loop and adjacent positive solid control.
assert whistle_tree.ray_cast(Vector((.042,.06,.019)),Vector((0,-1,0)),.12)[0] is None
assert whistle_tree.ray_cast(Vector((.042,.06,.030)),Vector((0,-1,0)),.12)[0] is not None
hat_tree=tree(H)
under=[]
for x,y in ((-.056,0),(.056,0),(0,-.06),(0,.06),(.02,.071),(-.021,-.07)):
    hit,*_=hat_tree.ray_cast(Vector((x,y,-.03)),Vector((0,0,1)),.22)
    assert hit is not None and hit.z>.050,(x,y,hit)
    under.append(round(hit.z,6))
strap_hits=[]
for x,y in ((-.048,-.048),(.048,.048),(-.048,.048),(.048,-.048)):
    point,*_=hat_tree.ray_cast(Vector((x,y,-.03)),Vector((0,0,1)),.18)
    assert point is not None and .083<point.z<.113,(x,y,point)
    strap_hits.append(round(point.z,6))
olds=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(donor))
frames=sorted(set(s.objects)-olds,key=lambda o:o.name)
assert len(frames)==12 and len({o.data for o in frames})==1
F=frames[0];F.matrix_world=Matrix.Translation((0,0,1.42))
for o in frames[1:]:bpy.data.objects.remove(o,do_unlink=True)
scale=2.75
W.matrix_world=Matrix.Translation((-.016,.087,1.365))@Matrix.Rotation(math.pi,4,"Z")@Matrix.Scale(scale,4)
bpy.context.view_layer.update()
ws,fs=coords(W),coords(F)
margin=[.259-max(abs(p[i]-c) for p in ws) for i,c in ((0,0),(2,1.42))]
gap=min(p.y for p in ws)-max(p.y for p in fs)
assert min(margin)>.050 and gap>.007,(margin,gap)
receipt={"scope":"Two independently editable rewards; no actor, equipped or drop state",
  "e12_reference_blob":"03833f41a2c703599fad5373dc01374fd55436a6","assets":[w,h],"frame_donor_sha256":pin,
  "whistle_display_only_scale":scale,"whistle_display_edge_margins_m":[round(x,5) for x in margin],
  "whistle_frame_forward_gap_m":round(gap,5),"loop_open_and_solid_control":True,
  "under_hat_first_hits_m":under,"suspension_hits_m":strap_hits,"hat_wear_origin_provisional_blender_m":[0,0,0]}
(D/"e11d-foreman-rewards-proof.json").write_text(json.dumps(receipt,indent=2)+"\n")
if os.getenv("WILDSHARD_VALIDATE_ONLY")=="1":sys.exit(0)

def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()
def setup():
    s.world=bpy.data.worlds.new("Cool shop ambience");s.world.color=(.10,.12,.15)
    s.render.engine="CYCLES";s.cycles.samples=38;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.067
    s.view_settings.view_transform="AgX";s.view_settings.look="AgX - Medium High Contrast"
    s.render.resolution_x=1360;s.render.resolution_y=910;s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
def lights(items):
    for loc,goal,power,c,size in items:
        n=bpy.data.lights.new("Shop softbox","AREA");n.energy=power;n.color=c;n.size=size
        o=bpy.data.objects.new(n.name,n);s.collection.objects.link(o);o.location=loc;aim(o,goal)
def cam(loc,goal,size):
    n=bpy.data.cameras.new("Reward study");o=bpy.data.objects.new(n.name,n);s.collection.objects.link(o)
    o.location=loc;aim(o,goal);n.type="ORTHO";n.ortho_scale=size;s.camera=o
def render(tag):
    s.render.filepath=str(D/("nov25-foreman-"+tag+".png"));bpy.ops.render.render(write_still=True)

setup()
H.hide_render=True
slate=mat("Warm plasma-cut wall",(.17,.121,.073),.12,.72)
box("Wall witness",(0,-.13,1.4),(2.6,.15,2.1),slate,.012)
lights([((-.55,.94,2.1),(0,0,1.43),37,(1,.79,.57),.78),((.66,.82,1.54),(0,0,1.42),23,(.56,.82,1),.55)])
cam((.20,1.46,1.63),(0,.05,1.42),.81)
if os.getenv("WSC_FOREMAN_LINER_ONLY")!="1":render("whistle")
for o in list(s.objects):
    if o!=H:bpy.data.objects.remove(o,do_unlink=True)
H.hide_render=False
backdrop=mat("Toolroom charcoal",(.041,.071,.076),.03,.80)
setup()
lights([((-.40,-.44,.53),(0,0,.07),21,(1,.84,.61),.50),((.40,.24,.34),(0,0,.08),14,(.55,.78,1),.38)])
box("Toolroom seamless tabletop",(0,0,-.040),(10,10,.05),backdrop,.005)
cam((.31,-.47,.295),(0,0,.07),.46)
if os.getenv("WSC_FOREMAN_LINER_ONLY")!="1":render("hardhat")
H.rotation_mode="XYZ"
H.rotation_euler.y=math.radians(-128)
bpy.context.view_layer.update()
H.location.z=-.013-min(v.z for v in coords(H))
cam((.40,-.26,.32),(0,0,.122),.52)
render("hardhat-liner")
