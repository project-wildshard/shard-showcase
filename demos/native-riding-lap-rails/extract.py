"""Export test geometry only: exact rail + apron imports at all four R02 picks."""
import bpy
import hashlib
import json
import math
from mathutils import Matrix
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[2]
assets=root/'public/assets/wildshard-art'
out=Path(sys.argv[sys.argv.index('--')+1])
layout=root/'project/layouts/w10b-riding-course-study.json'
raw=layout.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='2e5470d81f6a525194da2c143720c5d245cfb871dcc609a46e747ae2403c868f'
jumps=json.loads(raw)['jumps']['r02_wip_blender_xy_m']
assert jumps==[[-165,148],[-125,148],[-110,224],[-160,224]]
pins={
    'w10b-reusable-riding-jump-wip.glb':'0881ec693a68897ff8eadc60cd648237ec8bd969c4d05c7fd6faef09445c3680',
    'w10b-riding-rail-apron.glb':'8b815991a362c592f7717bb9a26faba8826877984d050ece94bcdbdaa6e64f6c',
    'w10b-riding-apron-stands.glb':'7a78a5c46c7656efac6112533e13a72cb6251206e6fab4005ba91e956495c6dd',
}
for name in pins:
    sha=hashlib.sha256((assets/name).read_bytes()).hexdigest()
    assert pins[name]==sha

def load(name):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/name))
    bpy.context.view_layer.update()
    return sorted([o for o in set(bpy.context.scene.objects)-before if o.type=='MESH'],key=lambda o:o.name)

def pack(o,mat):
    o.data.calc_loop_triangles()
    p=[mat@o.matrix_world@v.co for v in o.data.vertices]
    return dict(name=o.name,v=[round(a,7) for x,y,z in p for a in (x,z,-y)],
                t=[i for tri in o.data.loop_triangles for i in tri.vertices])

bpy.ops.wm.read_factory_settings(use_empty=True)
rail,apron,stands=[load(name) for name in pins]
assert len(rail)==32 and len(apron)==1 and len(stands)==2
rows=[]
for i,(x,z) in enumerate(jumps,1):
    a=math.pi/2 if z==148 else -math.pi/2
    m=Matrix.Translation((x,z,.025))@Matrix.Rotation(a,4,'Z')
    parts=[pack(o,m) for o in rail]
    av=pack(apron[0],m)['v']
    mm=[(min(av[j::3]),max(av[j::3])) for j in range(3)]
    center=[round((a+b)/2,6) for a,b in mm]
    half=[round((b-a)/2,6) for a,b in mm]
    assert center==[x,.697,-z] and all(abs(a-b)<1e-5 for a,b in zip(half,[.061,.341,2.047]))
    row=dict(id=i,x=x,z=-z,threeYawDeg=round(math.degrees(a)),
             direction=-1 if z==148 else 1,parts=parts,apron=dict(center=center,half=half))
    if i==4:
        receiver_m=Matrix.Translation((.80,0,0))@m
        extents=[]
        for o in stands:
            v=pack(o,receiver_m)['v']
            axes=[(min(v[j::3]),max(v[j::3])) for j in range(3)]
            c=[round((a+b)/2,6) for a,b in axes]
            h=[round((b-a)/2,6) for a,b in axes]
            assert abs(c[0]+159.2)<.001 and abs(c[2]+224)-h[2]>1.78
            assert abs(c[1]-h[1]-.025)<1e-6
            extents.append(dict(center=c,half=h))
        row['receiver']=dict(translation=[-159.2,.025,-224],downstream_m=.80,
            panel=dict(center=[x+.8,center[1],center[2]],half=half),stands=extents)
    rows.append(row)
out.write_text(json.dumps(dict(pins=pins,rows=rows),separators=(',',':'))+'\n')
