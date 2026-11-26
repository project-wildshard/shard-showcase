"""Author and reimport the optional tank-rim ring; do not edit W08."""
import hashlib
import json
from math import pi
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

args=sys.argv[sys.argv.index("--")+1:]
out=Path(args[0])
S=bpy.context.scene
anchor=(-193.2,91.2,21.35)
center=Vector(anchor)
U=Vector((1,-1,0)).normalized()
V=Vector((1,1,0)).normalized()
W=Vector((0,0,1))
def at(a,b,c):return a*U+b*V+c*W
def mat(n,rgb,metal,rough):
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
steel=mat('Tank gripped steel',(.07,.15,.17),.64,.35)
brass=mat('Yellow oxide enamel',(.79,.33,.047),.33,.36)
cyan=mat('Claw turquoise enamel',(.039,.49,.57),.41,.33)
iron=mat('Cold iron fasteners',(.08,.09,.10),.76,.36)
parts=[]
def mark(n,m):
    o=bpy.context.object;o.name='Roof hook | '+n;o.data.materials.append(m);parts.append(o);return o
def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at(*p),rotation=(0,0,-pi/4))
    o=mark(n,m);o.scale=d;return o
def bar(n,a,b,r,m,vertices=8):
    a,b=at(*a),at(*b);delta=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=delta.length,location=(a+b)/2,
        rotation=delta.to_track_quat('Z','Y').to_euler())
    return mark(n,m)
# Saddle feet lie within the existing roof radius; clear the approach gap at low height.
for side in (-1,1):
    b=side*1.58
    box('Roof saddle',(-3.05,b,-3.27),(.80,.55,.16),steel)
    for du in (-.26,.26):
        for dv in (-.17,.17):bar('Hex anchor',(-3.05+du,b+dv,-3.19),(-3.05+du,b+dv,-3.12),.055,iron,6)
    bar('Upright',(-3.05,b,-3.22),(-3.05,b,.27),.096,steel)
    bar('Cantilever',(-3.05,b,.27),(-.30,side*.75,.30),.10,steel)
    bar('Knee brace',(-3.05,b,-2.16),(-1.14,side*1.00,.29),.071,steel)
    bar('Enamel signal sleeve',(-3.05,b,-.59),(-3.05,b,.01),.122,brass)
    bar('Clevis cheek',(-.30,side*.75,.30),(-.10,side*.34,.47),.092,brass)
    bar('Clevis cap',(-.10,side*.34,.47),(0,side*.21,.49),.088,steel)
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=10,location=(0,0,0),
    major_radius=.48,minor_radius=.09,rotation=(-pi/2,0,pi/4))
ring=mark('Claw ring centre origin',cyan)
for p in ring.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
o=bpy.context.object;o.name='W7a roof rim grapple saddle'
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
glb=out/'w7a-tank-rim-hook.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_animations=False)
bpy.data.objects.remove(o,do_unlink=True)
before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(glb))
objs=sorted(set(S.objects)-before,key=lambda o:o.name)
assert len(objs)==1 and objs[0].type=='MESH'
for o in objs:o.matrix_world=Matrix.Translation(center)@o.matrix_world
bpy.context.view_layer.update()
def three(v):return (v.x,v.z,-v.y)
geometry=[]
for o in objs:
    o.data.calc_loop_triangles()
    geometry.append(dict(name=o.name,vertices=[round(k,6) for v in o.data.vertices for k in three(o.matrix_world@v.co)],
      triangles=[i for t in o.data.loop_triangles for i in t.vertices]))
raw=json.dumps(geometry,separators=(',',':'))+'\n'
(out/'saddle.json').write_text(raw)
(out/'saddle-export.json').write_text(json.dumps(dict(
    bytes=glb.stat().st_size,triangles=sum(len(g['triangles'])//3 for g in geometry),
    sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),mesh_sha256=hashlib.sha256(raw.encode()).hexdigest(),
    origin_three=[anchor[0],anchor[2],-anchor[1]],rotation_three=[0,0,0]),indent=2)+'\n')
if len(args)==1:raise SystemExit(0)
runpy_args={'S':S,'bpy':bpy,'out':out,'Vector':Vector,'Matrix':Matrix,'mat':mat,'args':args}
import runpy
runpy.run_path(str(Path(__file__).with_name('render.py')),init_globals=runpy_args)
