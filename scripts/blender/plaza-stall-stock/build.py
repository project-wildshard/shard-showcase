"""Three vertex-colored, tabletop-only stock options for WSC-PROP-005."""
import hashlib
import json
from math import cos, pi, sin, tau
from pathlib import Path
from random import Random
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
root = here.parents[2]
assets = root / 'public/assets/wildshard-art'
out = Path(sys.argv[sys.argv.index('--') + 1])
out.mkdir(parents=True, exist_ok=True)
stall = assets / 'market-awning-stall.glb'
pin = 'b240fd8056db68d9b1caeaefc61459de4171f1345782726b0da40d0a1c614f04'
assert hashlib.sha256(stall.read_bytes()).hexdigest() == pin
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(stall))
table = next(o for o in s.objects if o.type == 'MESH')
bpy.context.view_layer.update()

def geometry(o):
    m = o.data
    m.calc_loop_triangles()
    return [o.matrix_world @ v.co for v in m.vertices], [tuple(t.vertices) for t in m.loop_triangles]
tbl = BVHTree.FromPolygons(*geometry(table),all_triangles=True)
rng = Random(5792)

mat = bpy.data.materials.new('Stock linear vertex colors')
mat.use_nodes = True
n = mat.node_tree.nodes.get('Principled BSDF')
n.inputs['Roughness'].default_value = .66
a = mat.node_tree.nodes.new('ShaderNodeVertexColor')
a.layer_name = 'StockColor'
mat.node_tree.links.new(a.outputs['Color'],n.inputs['Base Color'])

oak=(.31,.151,.068)
light=(.45,.242,.105)
iron=(.075,.092,.081)
linen=(.61,.49,.29)
brass=(.53,.28,.067)

class Mesh:
    def __init__(self):
        self.v,self.f,self.c=[],[],[]
    def emit(self,verts,faces,c):
        k=len(self.v)
        self.v.extend(verts)
        self.c.extend(c if isinstance(c,list) else [c]*len(verts))
        self.f.extend(tuple(k+i for i in f) for f in faces)
    def box(self,x,y,z,sx,sy,sz,c):
        self.emit([(x+i*sx/2,y+j*sy/2,z+k*sz/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[
            (0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],c)
    def turned(self,x,y,z,rings,sx,sy,c,twist,segments=10,irreg=.035):
        verts,colors=[],[]
        for j,(r,h,tone) in enumerate(rings):
            for i in range(segments):
                p=tau*i/segments+twist
                v=r*(1+rng.uniform(-irreg,irreg))
                verts.append((x+sx*v*cos(p),y+sy*v*sin(p),z+h))
                k=tone*(1+rng.uniform(-.078,.078))
                colors.append(tuple(min(1,u*k) for u in c))
        faces=[tuple(reversed(range(segments))),tuple(range(len(verts)-segments,len(verts)))]
        for j in range(len(rings)-1):
            for i in range(segments):
                a=j*segments+i;b=j*segments+(i+1)%segments
                faces.append((a,b,b+segments,a+segments))
        self.emit(verts,faces,colors)
    def leaf(self,origin,angle,reach,width,rise,c):
        x,y,z=origin
        dx,dy=cos(angle),sin(angle)
        p=[(x,y,z),(x+.43*dx*reach-dy*width,y+.43*dy*reach+dx*width,z+rise*.6),
           (x+dx*reach,y+dy*reach,z+rise),
           (x+.55*dx*reach+dy*width,y+.55*dy*reach-dx*width,z+rise*.52),
           (x+.45*dx*reach,y+.45*dy*reach,z+rise*.69)]
        self.emit(p,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],c)
    def finish(self,name):
        m=bpy.data.meshes.new(name)
        m.from_pydata(self.v,[],self.f)
        m.update()
        col=m.color_attributes.new('StockColor','FLOAT_COLOR','POINT')
        m.color_attributes.active_color=col
        for i,c in enumerate(self.c):
            col.data[i].color=(*c,1)
        # Smooth organic surfaces, but preserve right angles on tray slats.
        m.set_sharp_from_angle(angle=.79)
        for p in m.polygons:
            p.use_smooth=True
        m.materials.append(mat)
        o=bpy.data.objects.new(name,m)
        s.collection.objects.link(o)
        return o

def tray(m,base,trim):
    # Exterior feet on Z=0; the three variants share the same envelope.
    for x in (-.48,.48):
        m.box(x,0,.018,.12,.56,.036,iron)
    for i in range(6):
        m.box(0,-.29+i*.116,.047,1.33,.112,.030,base if i%2 else trim)
    for x in (-.68,.68):
        m.box(x,0,.09,.041,.70,.10,trim)
    for y in (-.333,.333):
        m.box(0,y,.084,1.32,.042,.092,base)
        for x in (-.615,.615):
            m.box(x,y*1.068,.104,.10,.009,.031,brass)

def fruit():
    m=Mesh();tray(m,oak,light)
    for row,y in enumerate((-.18,.018,.208)):
        for i in range(6):
            x=-.532+i*.211+(row%2)*.018
            pear=x>.09
            c=(.69,.43,.055) if pear else ((.58,.075,.038) if (i+row)%2 else (.36,.102,.040))
            rings=[(.44,.0,.67),(.88,.028,.81),(1,.073,.91),(.75 if pear else .935,.122,1.08),(.40 if pear else .51,.171 if pear else .151,1)]
            k=rng.uniform(.083,.098)
            m.turned(x,y,.062,rings,k,k*.93,c,i*.4,9)
            z=.062+rings[-1][1]
            m.box(x,y,z+.012,.013,.016,.025,oak)
            if (i+row)%2==0:
                m.leaf((x,y,z+.013),1.7*i+row,.080,.026,.019,(.13,.27,.057))
    return m

def bread():
    m=Mesh();tray(m,linen,oak)
    for i,x in enumerate((-.44,0,.44)):
        for j,y in enumerate((-.154,.152)):
            c=((.65,.281,.078),(.48,.18,.046),(.80,.422,.123))[(i+j)%3]
            m.turned(x,y,.062,[(.72,0,.67),(1,.051,.87),(.94,.12,.99),(.70,.167,1.12),(.38,.187,1.22)],
                     .167,.121,c,(i+j)*.37,12)
            # Raised flour lines, not cuts into underlying mesh.
            for k in (-1,0,1):
                z=.244-abs(k)*.012
                x1=x+k*.066
                m.emit([(x1-.039,y-.040,z),(x1-.031,y-.051,z),
                        (x1+.031,y+.048,z),(x1+.022,y+.052,z)],[(0,1,2,3)],(.87,.66,.36))
    return m

def herbs():
    m=Mesh();tray(m,(.16,.106,.058),light)
    for j,y in enumerate((-.15,.16)):
        for i,x in enumerate((-.49,-.16,.17,.50)):
            clay = ((.53,.22,.095),(.24,.28,.177),(.59,.42,.17))[(i+j)%3]
            m.turned(x,y,.062,[(.84,0,.72),(.97,.023,.86),(1,.126,1),(.88,.148,.99),(.9,.172,1.13)],
                     .116,.106,clay,i*.4,10)
            m.turned(x,y,.234,[(.93,0,.7),(1,.014,1),(.84,.023,1.15)],.112,.102,linen,i*.4,10)
            m.box(x,y-.098,.157,.087,.011,.043,linen)
            for k in range(5):
                green=((.087,.24,.072),(.27,.42,.092),(.12,.33,.22))[(i+k+j)%3]
                m.leaf((x,y,.252),k*tau/5+i,.128+rng.uniform(0,.032),.031,rng.uniform(.031,.081),green)
    return m

records=[]
stock=[]
for label,make in [('orchard',fruit),('bread',bread),('herbs',herbs)]:
    m=make()
    source=m.finish('Plaza stall tray | '+label)
    bpy.ops.object.select_all(action='DESELECT')
    source.select_set(True)
    name='w0b-plaza-stock-'+label+'.glb'
    p=out/name
    bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_animations=False)
    bpy.data.objects.remove(source,do_unlink=True)
    b=p.read_bytes()
    g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    assert not g.get('textures') and not g.get('images') and len(g['materials'])==1
    tri=sum(g['accessors'][p['indices']]['count']//3 for me in g['meshes'] for p in me['primitives'])
    assert tri<3500 and len(b)<125_000 and g['meshes'][0]['primitives'][0]['attributes']['COLOR_0']>=0,(label,tri,len(b))
    prev=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    o,=set(s.objects)-prev
    stock.append(o)
    bpy.context.view_layer.update()
    points,_=geometry(o)
    assert abs(min(q.z for q in points))<1e-6
    assert max(abs(q.x) for q in points)<.72 and max(abs(q.y) for q in points)<.37
    assert max(q.z for q in points)<.405
    gap=[]
    for q in points:
        hit,*_=tbl.ray_cast(Vector((q.x,q.y,1.8)),Vector((0,0,-1)),1)
        if hit and hit.z>1.08:
            assert hit.z<1.110,(tuple(q),tuple(hit))
            gap.append(1.109+q.z-hit.z)
    assert len(gap)>.70*len(points),(label,len(gap),len(points))
    assert -.0001<min(gap)<.001
    contact=[]
    for x in (-.48,.48):
        feet=[tbl.ray_cast(Vector((x+i*.008,j*.008,1.8)),Vector((0,0,-1)),1)[0]
              for i in range(-6,7) for j in range(-31,32)]
        seated=sum(abs(q.z-1.109)<.001 for q in feet if q is not None)
        assert seated>len(feet)*.74,(seated,len(feet))
        contact.append(seated)
    _, tris=geometry(o)
    lifted=BVHTree.FromPolygons([q+Vector((0,0,1.111)) for q in points],tris,all_triangles=True)
    assert not tbl.overlap(lifted),label
    records.append(dict(file=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),triangles=tri,
        materials=1,textures=0,projectedCounterHits=len(gap),verticalRays=len(points),footContacts=contact,footSamplesPerSide=819,counterIntersectionWith2mmOffset=False,minFootGapM=round(min(gap),6),
        dimensionsM=[round(max(v[i] for v in points)-min(v[i] for v in points),6) for i in range(3)]))
    o.location.z=1.109
result={'scope':'Three interchangeable decorative counter trays on the unchanged stall donor; no inventory, vendor, collision or placement in the map.',
        'catalogueId':'WSC-PROP-005','stallSha256':pin,'sameOriginThree':[0,1.109,0],'assets':records}
(out/'w0b-plaza-stall-stock-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(result,flush=True)
if '--proof-only' in sys.argv:sys.exit(0)

def aim(o,t):
    o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,kind,at,target,energy,color,size):
    d=bpy.data.lights.new(name,kind)
    d.energy,d.color=energy,color
    if kind=='SUN':d.angle=size
    else:d.shape,d.size='DISK',size
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o);o.location=at;aim(o,target)
s.world=bpy.data.worlds.new('Cloudy market sky')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.36,.48,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.53
light('Warm morning', 'SUN',(-4,7,9),(0,0,1),2.6,(1,.79,.57),.14)
light('Counter fill', 'AREA',(2,-4,4),(0,0,1),225,(.69,.82,1),4)
light('Canvas bounce', 'AREA',(-1,3.2,3.5),(0,0,1),150,(1,.82,.64),3.5)
bpy.ops.mesh.primitive_plane_add(size=200)
ground=bpy.context.object
pav=bpy.data.materials.new('Review ground only')
pav.diffuse_color=(.14,.161,.17,1)
ground.data.materials.append(pav)
bpy.ops.object.camera_add(location=(1.35,2.05,1.93))
cam=bpy.context.object
s.camera=cam
aim(cam,(0,0,1.23));cam.data.lens=47
s.render.engine='CYCLES'
s.cycles.samples=30
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.066
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.resolution_x,s.render.resolution_y=1050,810
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=92
for i,tag in enumerate(('orchard','bread','herbs')):
    for k,o in enumerate(stock):
        o.hide_render=i!=k
    s.render.filepath=str(out/(tag+'.jpg'))
    bpy.ops.render.render(write_still=True)
