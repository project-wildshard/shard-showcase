"""W06 Sword and Spear catalogue silhouettes, static fictional inventory art."""
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
scene = bpy.context.scene
clear_scene()


def material(name, rgb, metal=0, roughness=.48):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = roughness
    return m


steel = material("Satin silver, light facet", (.52, .56, .61), .72, .31)
steel_dark = material("Satin silver, shadow facet", (.26, .30, .36), .71, .38)
edge = material("Bright perimeter catch", (.78, .80, .79), .79, .26)
scuff = material("Silver worn stipple", (.405, .43, .46), .67, .49)
oxide = material("Graphite hardware", (.084, .104, .129), .54, .42)
leather = material("Burnt orange leather", (.50, .145, .035), .04, .54)
seam = material("Russet leather binding", (.208, .053, .022), .03, .51)
wood = material("Oiled brown shaft", (.26, .111, .05), .03, .5)
wood_alt = material("Oiled brown shaft, light facet", (.31, .146, .074), .03, .52)
slate = material("Blue iron, light facet", (.24, .33, .42), .65, .35)
slate_dark = material("Blue iron, shadow facet", (.099, .157, .221), .56, .43)
red = material("Garnet pennant fabric", (.33, .037, .051), .01, .71)
red_fold = material("Garnet pennant fabric, fold", (.184, .015, .029), .01, .79)
red_tip = material("Faded garnet fold", (.44, .059, .068), 0, .76)

# A single mesh is assembled directly. Its material primitives are inspectable
# by ordinary glTF readers without textures, scripts, or decoder extensions.
vertices, faces, indices, palette = [], [], [], []


def add(v, f, m):
    start = len(vertices)
    vertices.extend(v)
    faces.extend([tuple(start + i for i in p) for p in f])
    per_face = [m] * len(f) if not isinstance(m, list) else m
    assert len(per_face) == len(f)
    for mat in per_face:
        if mat not in palette:
            palette.append(mat)
        indices.append(palette.index(mat))


def stack(rings, sections, mat):
    coords = [p for ring in rings for p in ring]
    f = [tuple(range(sections-1, -1, -1))]
    for j in range(len(rings)-1):
        for i in range(sections):
            a, b = j*sections+i, j*sections+(i+1) % sections
            f.append((a, b, b+sections, a+sections))
    f.append(tuple(range(len(coords)-sections, len(coords))))
    add(coords, f, mat if not callable(mat) else [mat(i) for i in range(len(f))])


def radial(zr, n, mat, phase=0, squash=1):
    stack([[(r*math.cos(t*math.tau/n+phase), squash*r*math.sin(t*math.tau/n+phase), z)
            for t in range(n)] for z,r in zr], n, mat)


def octagon(x, y, z, trim=.25):
    a,b=x*(1-trim),y*(1-trim)
    return [(u,v,z) for u,v in [(x,-b),(x,b),(a,y),(-a,y),(-x,b),(-x,-b),(-a,-y),(a,-y)]]


def stone_profile(rows, cool=False):
    # Broad graphic planes with shallow perimeter strips.
    m1,m2=(slate,slate_dark) if cool else (steel,steel_dark)
    rings=[]
    for z,w,d in rows:
        rings.append([(w,0,z),(.91*w,.40*d,z),(0,d,z),(-.91*w,.40*d,z),
                      (-w,0,z),(-.91*w,-.40*d,z),(0,-d,z),(.91*w,-.40*d,z)])
    stack(rings,8,lambda i:[edge,m1,m2,edge,edge,m1,m2,edge][(i-1)%8])


def wrap(zstart,zend,r,turns,color,squash=1):
    n=16*turns
    vv=[]
    for i in range(n+1):
        t=i/n; a=t*math.tau*turns
        for dz,dr in ((-.004,0),(0,.003),(.004,0)):
            vv.append(((r+dr)*math.cos(a),squash*(r+dr)*math.sin(a),
                       zstart+(zend-zstart)*t+dz))
    add(vv,[(3*i+j,3*i+j+1,3*(i+1)+j+1,3*(i+1)+j)
             for i in range(n) for j in range(2)],color)


def sword():
    blade=[(.11,.076,.021),(.20,.079,.022),(.77,.075,.021),
           (.83,.068,.019),(.94,.001,.001)]
    stone_profile(blade)
    # A handful of shallow graphic wear marks on the broad panels.
    def silver_face(x,z):
        a,b=next((a,b) for a,b in zip(blade,blade[1:]) if a[0]<=z<=b[0])
        t=(z-a[0])/(b[0]-a[0])
        w,d=(a[i]+t*(b[i]-a[i]) for i in (1,2))
        return d*(1-.60*abs(x)/(.91*w))
    for side in (-1,1):
        for x,z,w,l in ((-.027,.29,.019,.022),(.036,.46,.020,-.017),
                        (-.040,.65,.019,-.025),(.028,.726,.013,.013)):
            poly=[(x-w,z-l),(x-w*.7,z-l*.6),(x+w,z+l),(x+w*.38,z+l*.80)]
            v=[(u,side*(silver_face(u,h)+.00065),h) for u,h in poly]
            add(v, [(0,1,2,3) if side<0 else (3,2,1,0)], scuff)
    stack([octagon(x,y,z) for z,x,y in
           ((.084,.092,.027),(.097,.107,.034),(.134,.107,.034),(.148,.091,.027))],8,steel)
    stack([octagon(x,y,z) for z,x,y in
           ((-.162,.040,.029),(-.150,.048,.035),(-.105,.048,.035),(-.097,.039,.027))],8,oxide)
    radial([(-.102,.038),(-.077,.043),(.062,.041),(.096,.039)],16,leather, squash=.78)
    wrap(-.086,.077,.0405,5,seam,.78)
    # Small graphic maker's stamps, not structural geometry.
    for side in (-1,1):
        z=.114; y=.0342*side
        poly=[(-.013,y,z),(0,y,z+.010),(.013,y,z),(0,y,z-.010)]
        add(poly,[tuple(range(4)) if side<0 else (3,2,1,0)],oxide)


def pennant(angle,length,flare,offset):
    direction=Vector((math.cos(angle),math.sin(angle),0))
    across=Vector((-math.sin(angle),math.cos(angle),0))
    zz=.768+offset
    v=[]
    for t,w,rd in ((0,.010,.033),(.27,.023,.040),(.58,.028,flare*.77),
                   (.84,.016,flare), (1,.001,flare*.94)):
        center=direction*rd + across*(.016*t*t) + Vector((0,0,zz-length*t))
        v.extend([tuple(center+w*across),tuple(center+direction*.007),tuple(center-w*across)])
    ff=[(3*j+i,3*j+i+1,3*j+4+i,3*j+3+i) for j in range(4) for i in range(2)]
    add(v,ff,[red_fold,red_tip,red_fold,red,red,red,red_fold,red_fold])


def spear():
    radial([(-1.016,.026),(-.982,.028),(-.61,.024),(-.04,.026),
            (.24,.026),(.62,.024),(.805,.027)],12,
           lambda i: wood_alt if i%12 in (1,2,3,4,5) else wood)
    stone_profile([(.817,.019,.014),(.851,.026,.017),(.923,.058,.029),
                   (1.008,.072,.032),(1.089,.060,.026),(1.159,.034,.015),
                   (1.234,.001,.001)],True)
    radial([(.747,.028),(.757,.036),(.825,.035),(.841,.023)],12,seam)
    wrap(.759,.830,.0355,4,leather)
    radial([(-1.030,.024),(-1.019,.032),(-.907,.030),(-.892,.027)],12,seam)
    wrap(-1.016,-.907,.030,5,leather)
    r=random.Random(86)
    for i in range(8):
        pennant(i*math.tau/8+r.uniform(-.16,.16),r.uniform(.263,.38),
                r.uniform(.072,.114),r.uniform(-.012,.006))


def create(slug, label, build):
    clear_scene()
    for x in (vertices, faces, indices, palette):
        x.clear()
    build()
    mesh=bpy.data.meshes.new(label)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    for m in palette:
        mesh.materials.append(m)
    for p,i in zip(mesh.polygons,indices):
        p.material_index=i
    assert all(p.area>1e-9 for p in mesh.polygons)
    obj=bpy.data.objects.new(label+" | Inventory pivot",mesh)
    scene.collection.objects.link(obj)
    p=out/(slug+".glb")
    export([obj],p)
    raw=p.read_bytes()
    assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
    doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    assert len(doc["meshes"])==len(doc["nodes"])==1
    assert not set(doc)&{"animations","images","skins","extensionsRequired"}
    primitives=doc["meshes"][0]["primitives"]
    tris=sum(doc["accessors"][p["indices"]]["count"]//3 for p in primitives)
    assert len(raw)<84000 and tris<1600, (len(raw),tris)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(p))
    re,=[o for o in scene.objects if o.type=="MESH"]
    assert re.location.length<1e-6
    assert len(re.data.materials)==len(primitives)
    re.data.calc_loop_triangles()
    assert len(re.data.loop_triangles)==tris
    bounds=[[round(fn(c[i] for c in re.bound_box),5) for i in range(3)]
            for fn in (min,max)]
    return p,dict(bytes=len(raw),triangles=tris,primitive_count=len(primitives),
                  bounds_blender=bounds,inventory_pivot=[0,0,0])


sword_glb,sword_proof=create("wsc-gear-001-sword","WSC-GEAR-001 Sword",sword)
spear_glb,spear_proof=create("wsc-gear-002-spear","WSC-GEAR-002 Spear",spear)
(out/"west-inventory-pair-proof.json").write_text(json.dumps({
    "scope":"Static fictional inventory visuals, no native gameplay, grip fit, skins or animation.",
    "WSC-GEAR-001":sword_proof,"WSC-GEAR-002":spear_proof,
},indent=2)+"\n")


def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()


def light(label,location,target,energy,tint,size,shape="DISK"):
    data=bpy.data.lights.new(label,"AREA")
    data.energy,data.color,data.size,data.shape=energy,tint,size,shape
    obj=bpy.data.objects.new(label,data)
    scene.collection.objects.link(obj)
    obj.location=location
    aim(obj,target)


def place(path,x,y,z,tilt,yaw):
    old=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    o,=[o for o in set(scene.objects)-old if o.type=="MESH"]
    o.location=(x,y,z)
    o.rotation_mode="XYZ"
    o.rotation_euler=(0,tilt,yaw)


def studio(filename, detail=False):
    clear_scene()
    if detail:
        place(sword_glb,-.27,0,-.07,-.24,.44)
        place(spear_glb,.24,0,-.76,.19,-.38)
    else:
        place(sword_glb,-.34,0,-.18,-.25,.41)
        place(spear_glb,.44,.04,0,.23,-.28)
    panel=material("Deep indigo wall",(.014,.024,.039),.05,.8)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,.56,0),rotation=(math.pi/2,0,0))
    bpy.context.object.data.materials.append(panel)
    world=bpy.data.worlds.new("Studio neutral")
    world.color=(.095,.101,.118)
    scene.world=world
    light("Soft warm key",(-2,-3,2.3),(0,0,.15),225,(1,.89,.78),3.0)
    light("Silver reflection",(1.7,-2.4,1.8),(0,0,.25),90,(.79,.90,1),1.7)
    light("Cyan edge",(1.5,-.29,1.24),(.31,0,.35),24,(.41,.71,1),.72)
    light("Warm fabric fill",(-.7,-1.7,-.64),(0,0,0),32,(1,.71,.59),1.9)
    cd=bpy.data.cameras.new("Inventory review")
    co=bpy.data.objects.new(cd.name,cd)
    scene.collection.objects.link(co)
    scene.camera=co
    co.location=(.04,-7.2,.08 if detail else .1)
    aim(co,(.035,0,.08 if detail else .10))
    cd.type="ORTHO"
    cd.ortho_scale=1.55 if detail else 2.71
    scene.render.engine="CYCLES"
    scene.cycles.samples=48
    scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.render.resolution_x=1500 if detail else 1400
    scene.render.resolution_y=1120 if detail else 1320
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG"
    scene.render.image_settings.quality=91
    scene.render.filepath=str(out/filename)
    bpy.ops.render.render(write_still=True)


studio("nov24-west-inventory-pair.jpg")
studio("nov24-west-inventory-materials.jpg",True)
