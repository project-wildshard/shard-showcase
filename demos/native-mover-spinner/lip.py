"""One detachable fixed bridge cassette matching the spinner handoff fixture."""
import hashlib,json,struct,sys
from pathlib import Path
import bpy

out=Path(sys.argv[sys.argv.index('--')+1])
scope=json.loads((out/'handoff.json').read_text())
_,xx,yy,zz,hx,hy,hz=scope['lip']
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def mat(name,c,metal=.35):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*c,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=.54
    return m
iron=mat('Oil-blue structural iron',(.079,.120,.132),.55)
grip=mat('Soot grey pressed tread',(.135,.164,.154))
edge=mat('Burnt-orange endplate',(.55,.184,.048))
bronze=mat('Brass fastener recesses',(.35,.26,.139),.62)
def box(name,pos,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rolled iron edge','BEVEL');b.width=bevel;b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    return o
# Pivot is the bottom cage landing plane at centre of the insert.
box('Steel bridge cassette',(0,0,-.166),(2*hx,2*hz,.268),iron,.025)
box('Continuous pressed deck',(0,0,-.020),(2*hx-.232,2*hz,.040),grip)
for sign in (-1,1):
    box('Orange end plate',(sign*(hx-.058),0,-.035),(.116,2*hz,.07),edge)
    for j in (-2.45,2.45):
        for k in (.24,.62,.98):
            box('Flush fastener', (sign*k,j,-.046),(.078,.078,.012),bronze,.010)
p=out/'w6a-spinner-lift-lip.glb'
# Aggregate into one mesh, retain material slots.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.join()
bpy.context.object.name='Fixed spinner to bottom-lift approach'
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',export_animations=False)
raw=p.read_bytes()
g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(g['meshes'])==1 and not any(k in g for k in ('animations','images','textures'))
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(p))
objs=list(s.objects)
pts=[o.matrix_world@v.co for o in objs if o.type=='MESH' for v in o.data.vertices]
dims=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
assert all(abs(a-b)<1e-5 for got,expected in zip(dims,[[-hx,hx],[-hz,hz],[-2*hy,0]]) for a,b in zip(got,expected))
tris=sum(g['accessors'][q['indices']]['count']//3 for q in g['meshes'][0]['primitives'])
(out/'lip-proof.json').write_text(json.dumps({'glb_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'triangles':tris,
 'bounds_blender_local':[[round(v,4) for v in axis] for axis in dims],
 'three_origin':[xx,yy+hy,zz],'lift_side_visual_seam_m':.010,
 'scope':'Fit-only GLB; stationary lift cage in bench. No installed collider, moving lift or arm collision.'},indent=2)+'\n')
