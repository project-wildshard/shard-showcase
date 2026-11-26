"""Build a reversible, non-colliding confirmation overlay for the original roof pad."""
import hashlib
import json
from math import cos,sin,tau
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index('--')+1])
scene=bpy.context.scene
pad=Vector((-115,16.5,12.754))
mesh_raw=(out/'terminal-mesh.json').read_bytes()
assert hashlib.sha256(mesh_raw).hexdigest()=='a8b955c7f7baa9e95c2b8bcdfdb0e3b7b6a6d5f1b3a3847500b338f46130be55'
geo=json.loads(mesh_raw)
v,f=[],[]
for g in (x for x in geo if x['name'].startswith('PROP-035')):
    i=len(v)
    v.extend(Vector((x,-z,y)) for x,y,z in zip(*[iter(g['vertices'])]*3))
    f.extend(tuple(i+j for j in t) for t in zip(*[iter(g['triangles'])]*3))
bvh=BVHTree.FromPolygons(v,f,all_triangles=True)
vertices,faces,contracted=[],[],[]
gaps=[]
# A narrow green echo just inside the original cyan ring. Three breaks leave the paint visible.
for band in range(3):
    i=len(vertices)
    for j in range(19):
        a=tau*(.14+band/3+j*.78/(18*3))
        taper=max(.10,min(1,j/3,(18-j)/3))
        for r in (.78,.78+.118*taper):
            x,y=cos(a)*r,sin(a)*r
            vertices.append((x,y,0));contracted.append((cos(a)*.78,sin(a)*.78,0))
        if j:
            k=i+2*(j-1);faces.append((k,k+1,k+3,k+2))
# Inspect 5×5 points per quad over the swept width; morph poses are subsets.
for face in faces:
    a,b,c,d=(Vector(vertices[i]) for i in face)
    for i in range(5):
        u=i/4
        for j in range(5):
            v=j/4
            sample=a.lerp(b,u).lerp(d.lerp(c,u),v)
            hit,n,idx,dist=bvh.ray_cast(pad+sample+Vector((0,0,1)),Vector((0,0,-1)),1.1)
            assert hit and .005 < pad.z-hit.z < .023,(tuple(sample),hit,n)
            gaps.append(pad.z-hit.z)
m=bpy.data.materials.new('Confirmation enamel | jade')
m.diffuse_color=(.11,.88,.39,1);m.use_nodes=True
p=m.node_tree.nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value=m.diffuse_color
p.inputs['Roughness'].default_value=.46
p.inputs['Emission Color'].default_value=m.diffuse_color
p.inputs['Emission Strength'].default_value=.65
mesh=bpy.data.meshes.new('Revealed arc strips')
mesh.from_pydata(vertices,[],faces);mesh.materials.append(m)
o=bpy.data.objects.new('W7b finish confirmation',mesh);scene.collection.objects.link(o)
o.shape_key_add(name='Basis')
morph=o.shape_key_add(name='Contract')
for a,b in zip(morph.data,contracted):a.co=b
scene.render.fps=60
for frame,w in ((0,1),(5,0),(18,.18),(24,0),(42,1)):
    morph.value=w;morph.keyframe_insert('value',frame=frame)
act=o.data.shape_keys.animation_data.action;act.name='Roof finish - acknowledge'
for fc in act.fcurves:
    for pt in fc.keyframe_points:pt.interpolation='LINEAR'
scene.frame_set(0)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
path=out/'w7b-finish-ack.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
    export_animation_mode='ACTIONS',export_animations=True,export_force_sampling=False)
raw=path.read_bytes()
g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(g['animations'])==len(g['meshes'])==1 and not g.get('images')
assert g['animations'][0]['name']==act.name
(out/'pad-ack.json').write_text(json.dumps(dict(
    bytes=len(raw),triangles=len(faces)*2,sha256=hashlib.sha256(raw).hexdigest(),
    overlay_origin_three=[-115,12.754,-16.5],fit_probes=len(gaps),duration_s=.70,
    material_primitives=1,radial_support_m=[.78,.898],probed_clearance_mm=[round(min(gaps)*1000,2),round(max(gaps)*1000,2)],
    scope='Optional one-shot visual, not a collider or a course trigger.'),indent=2)+'\n')
