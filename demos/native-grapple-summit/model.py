"""Export and reimport the optional W7a outboard summit ring on the exact W08 donor."""
import hashlib
import json
from math import pi
from pathlib import Path
import sys
import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:]
O=Path(args[0])
S=bpy.context.scene
anchor=(-211.4,46.4,-38.9)
def mat(n,c,metal=.4):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=.38
    return m
steel=mat('Summit | blued steel',(.071,.135,.157),.67)
orange=mat('Summit | safety ochre',(.74,.257,.041))
cyan=mat('Summit | turquoise enamel',(.041,.52,.59))
parts=[]
def mark(n,m):
    o=bpy.context.object;o.name=n;parts.append(o);o.data.materials.append(m);return o
def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=mark(n,m);o.scale=d;return o
def rod(n,a,b,r,m,v=8):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,
      location=(a+b)/2,rotation=d.to_track_quat('Z','Y').to_euler())
    return mark(n,m)
# The main platform landing is west of this bracket. Keep hardware on the east side.
base=next(o for o in S.objects if o.type=='MESH' and o.name.endswith('Textured gray deck panels'))
bvh=BVHTree.FromPolygons([base.matrix_world@v.co for v in base.data.vertices],
    [p.vertices[:] for p in base.data.polygons])
for i in range(7):
    for j in range(7):
        x=anchor[0]-.74+i*.46/6;y=-anchor[2]-.44+j*.56/6
        hit,n,_,_=bvh.ray_cast(Vector((x,y,45.5)),Vector((0,0,-1)),.75)
        assert hit and abs(hit.z-45.05)<.002 and n.z>.95,(i,j,hit)
box('Low keeper flange',(-.51,-.16,-1.29),(.46,.56,.14),steel)
for x in (-.653,-.32):
    for y in (-.31,-.01):
        rod('Captured hex head',(x,y,-1.22),(x,y,-1.15),.05,orange,6)
for y in (-.34,.06):
    rod('Offset support',(-.48,y,-1.23),(-.26,y,-.45),.085,steel)
    rod('Short clevis arm',(-.26,y,-.45),(-.04,y,-.40),.087,orange)
rod('Lower clevis axle',(-.04,-.38,-.40),(-.04,.10,-.40),.079,steel)
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=10,major_radius=.42,minor_radius=.076,
    location=(0,0,0),rotation=(pi/2,0,-.39))
ring=mark('Turquoise capture ring',cyan)
for p in ring.data.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
o=bpy.context.object;o.name='W7a summit outboard ring'
S.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
path=O/'w7a-summit-outboard-ring.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False)
bpy.data.objects.remove(o,do_unlink=True)
before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(path))
o,=tuple(set(S.objects)-before)
o.matrix_world=Matrix.Translation((anchor[0],-anchor[2],anchor[1]))@o.matrix_world
bpy.context.view_layer.update()
o.data.calc_loop_triangles()
world=[o.matrix_world@v.co for v in o.data.vertices]
g=dict(name=o.name,vertices=[round(v,6) for p in world for v in (p.x,p.z,-p.y)],
    triangles=[i for t in o.data.loop_triangles for i in t.vertices])
raw=json.dumps([g],separators=(',',':'))+'\n'
(O/'summit-bracket.json').write_text(raw)
receipt=dict(origin_three=anchor,footprintProbes=49,flangeSeatM=.01,bytes=path.stat().st_size,triangles=len(o.data.loop_triangles),
    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),mesh_sha256=hashlib.sha256(raw.encode()).hexdigest())
(O/'summit-bracket-export.json').write_text(json.dumps(receipt,indent=2)+'\n')
if len(args)==2:
    import runpy
    runpy.run_path(str(Path(__file__).with_name('render.py')),init_globals=dict(S=S,O=O,proof=Path(args[1]),mat=mat,receipt=receipt))
