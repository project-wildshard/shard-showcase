"""Build and reimport a freestanding W7a mast receiver without changing the mast."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector

args=sys.argv[sys.argv.index('--')+1:]
O=Path(args[0])
S=bpy.context.scene
anchor=(-202.6,0,-63.55)
w,d,h,top=3.4,2.8,.22,25.6
def matte(n,c,metal=.3,rough=.46):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
m=[
   matte('Mast | slate galvanized steel',(.095,.153,.170),.66),
   matte('Mast | worn ochre steel',(.66,.235,.043),.43),
   matte('Mast | abrasive graphite tread',(.125,.151,.153),.22,.71),
   matte('Mast | cast stone feet',(.29,.272,.224),.12,.72),
   matte('Mast | sea green glass',(.064,.49,.48),.19,.33)]
vertex,faces,slots=[],[],[]
cube=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def box(p,dim,i,rot=None):
    k=len(vertex);p=Vector(p)
    for z in (-1,1):
        for y in (-1,1):
            for x in (-1,1):
                v=Vector((x*dim[0]/2,y*dim[1]/2,z*dim[2]/2))
                vertex.append(tuple(p+(rot@v if rot is not None else v)))
    faces.extend(tuple(k+n for n in f) for f in cube);slots.extend([i]*6)
def beam(a,b,width,depth,i):
    a,b=Vector(a),Vector(b)
    v=b-a
    box((a+b)/2,(width,depth,v.length),i,v.to_track_quat('Z','Y'))
def obj(n,materials):
    d=bpy.data.meshes.new(n)
    d.from_pydata(vertex,[],faces)
    for a in materials:d.materials.append(a)
    for p,k in zip(d.polygons,slots):p.material_index=k
    o=bpy.data.objects.new(n,d);S.collection.objects.link(o)
    vertex.clear();faces.clear();slots.clear()
    return o
box((0,0,top-h/2),(w,d,h),0)
floor=obj('Mast 4 exact deck floor',[m[2]])
levels=[.46,5.16,9.98,14.80,19.62,24.43]
for sx in (-1,1):
    for sy in (-1,1):
        x,y=sx*1.23,sy*.95
        X,Y=sx*.99,sy*.73
        box((x,y,.19),(.76,.70,.38),3)
        box((x,y,.43),(.46,.41,.12),1)
        beam((x,y,.45),(X,Y,top-h),.22,.22,0)
        for k,z in enumerate(levels[1:]):
            t=min(1,(z-.45)/(top-h-.45))
            box((x+(X-x)*t,y+(Y-y)*t,z),(.34,.32,.23),1)
def coord(side,slot,z):
    t=min(1,max(0,(z-.45)/(top-h-.45)))
    return (side*(1.23-.24*t),slot*(.95-.22*t),z)
levels2=levels+[top-.6]
for i,(a,b) in enumerate(zip(levels2,levels2[1:])):
    for side in (-1,1):
        beam(coord(side,-1,b),coord(side,1,b),.12,.15,1 if i in (2,5) else 0)
        beam(coord(-1,side,b),coord(1,side,b),.12,.15,1 if i in (2,5) else 0)
        beam(coord(side,-1,a),coord(side,1,b),.094,.10,0)
        beam(coord(side,1,a),coord(side,-1,b),.094,.10,0)
        beam(coord(-1,side,a),coord(1,side,b),.094,.10,0)
        beam(coord(1,side,a),coord(-1,side,b),.094,.10,0)
for x in (-1,1):
    box((1.62*x,0,top-.21),(.15,2.59,.28),1)
    for y in (-.73,0,.73):
        box((x*1.704,y,top-.17),(.022,.22,.083),0)
        box((x*1.716,y,top-.17),(.01,.15,.036),4)
for y in (-1,1):
    box((0,y*1.32,top-.22),(3.1,.15,.25),0)
    for x in (-.89,-.56,.56,.89):
        box((x,y*1.40,top-.19),(.19,.021,.075),1)
frame=obj('Mast 4 freestanding braced frame',m)
bpy.ops.object.select_all(action='DESELECT')
for o in (floor,frame):o.select_set(True)
bpy.context.view_layer.objects.active=floor
file=O/'w7a-mast-receiver.glb'
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_animations=False)
for o in (floor,frame):bpy.data.objects.remove(o,do_unlink=True)
before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(file))
fresh=sorted(set(S.objects)-before,key=lambda o:o.name)
assert len(fresh)==2
dress=[];triangles=0
for o in fresh:
    v=[o.matrix_world@q.co for q in o.data.vertices]
    o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
    if o.name=='Mast 4 exact deck floor':
        e=[[f(p[k] for p in v) for k in range(3)] for f in (min,max)]
        for actual,expected in zip(e,[[-w/2,-d/2,top-h],[w/2,d/2,top]]):
            assert all(abs(a-b)<1e-5 for a,b in zip(actual,expected))
        continue
    assert max(q.z for q in v)<top
    dress.append(dict(name=o.name,
        vertices=[round(k,6) for p in v for k in (p.x+anchor[0],p.z,p.y*-1+anchor[2])],
        triangles=[i for t in o.data.loop_triangles for i in t.vertices]))
raw=json.dumps(dress,separators=(',',':'))+'\n'
(O/'mast-receiver-dressing.json').write_text(raw)
(O/'mast-receiver-export.json').write_text(json.dumps(dict(
    sha256=hashlib.sha256(file.read_bytes()).hexdigest(),bytes=file.stat().st_size,triangles=triangles,
    mesh_sha256=hashlib.sha256(raw.encode()).hexdigest(),origin_three=anchor,
    deck=dict(x=anchor[0],z=anchor[2],y=top,w=w,d=d,h=h)
),indent=2)+'\n')
if len(args)==2:
    import runpy
    for o in fresh:o.matrix_world=Matrix.Translation((anchor[0],-anchor[2],0))@o.matrix_world
    runpy.run_path(str(Path(__file__).with_name('render.py')),
        init_globals=dict(S=S,O=O,matte=matte,proof=Path(args[1]),mesh_sha=hashlib.sha256(raw.encode()).hexdigest()))
