"""Optional walkable E5b shed variant cut from the unchanged donor's front."""
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out = Path(sys.argv[sys.argv.index('--')+1])
out.mkdir(parents=True,exist_ok=True)
assets = Path(__file__).resolve().parents[2]/'public/assets/wildshard-art'
pins = {
 'wsc-prop-065-keycard-shed':'1702aa6968159d7b35b319bcbae4112c89b123fb885113c4e3cfb94aab39c966',
 'wsc-kit-006-foreman-desk':'bcaa8a98a7c2522f7d8553fcd60d70d14582d440ad79855cfedd63ce50ff7ff7',
 'wsc-kit-006-vault-keycard':'53258729cc9e8ec16ea0d7bb08a14c80d9696be1f91374c4fa51e6e9062382cc',
}
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def load(path):
    old = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted(set(scene.objects)-old,key=lambda o:o.name)


def donor(name):
    file=assets/(name+'.glb')
    assert hashlib.sha256(file.read_bytes()).hexdigest()==pins[name]
    return load(file)


old = donor('wsc-prop-065-keycard-shed')
# Cut only the closed right-hand front panel. Leave the original floor,
# back, roof and left window intact. Axes are Blender X/front -Y/up Z.
cut = ((.12,1.38),(-1.42,-.91),(.215,2.24))
planes = [(i,b,s) for i,(lo,hi) in enumerate(cut) for b,s in ((lo,1),(hi,-1))]


def subtract(poly):
    """Partition a face against six planes; keep only the outside fragments."""
    if any(max(v[0][i] for v in poly)<=lo or min(v[0][i] for v in poly)>=hi
           for i,(lo,hi) in enumerate(cut)):
        return [poly]
    kept=[]
    for i,edge,sign in planes:
        inside,outside=[],[]
        a=poly[-1]; da=(a[0][i]-edge)*sign
        for b in poly:
            db=(b[0][i]-edge)*sign
            if (da>=0)!=(db>=0):
                u=da/(da-db)
                hit=tuple(x.lerp(y,u) for x,y in zip(a,b))
                inside.append(hit);outside.append(hit)
            (inside if db>=0 else outside).append(b)
            a,da=b,db
        if len(outside)>=3:kept.append(outside)
        if len(inside)<3:break
        poly=inside
    return kept


def clipped(o):
    src=o.data
    src.calc_loop_triangles()
    tex=src.uv_layers.active
    vertices,indices,normals,uvs=[],[],[],[]
    pool={}
    for tri in src.loop_triangles:
        poly=[(o.matrix_world@src.vertices[src.loops[i].vertex_index].co,
               (o.matrix_world.to_3x3()@src.corner_normals[i].vector).normalized(),
               tex.data[i].uv.copy() if tex else Vector((0,0))) for i in tri.loops]
        for piece in subtract(poly):
            for k in range(1,len(piece)-1):
                w=[piece[j] for j in (0,k,k+1)]
                a,b,c=(v[0] for v in w)
                if (b-a).cross(c-a).length<1e-9:continue
                face=[]
                for q,n,t in w:
                    key=tuple(round(x,7) for x in q)
                    if key not in pool:
                        pool[key]=len(vertices);vertices.append(tuple(q))
                    face.append(pool[key])
                if len(set(face))!=3:continue
                indices.append(face)
                normals.extend(tuple(n.normalized()) for _,n,_ in w)
                uvs.extend(tuple(t) for _,_,t in w)
    if not indices:return None
    m=bpy.data.meshes.new(src.name+' doorway')
    m.from_pydata(vertices,[],indices);m.update()
    assert not m.validate()
    assert len(src.materials)==1
    m.materials.append(src.materials[0])
    uv=m.uv_layers.new()
    for p in m.polygons:p.use_smooth=True
    for slot,t in zip(uv.data,uvs,strict=True):slot.uv=t
    m.normals_split_custom_set(normals)
    ob=bpy.data.objects.new(o.name+' doorway',m);scene.collection.objects.link(ob)
    return ob


variant=[n for o in old if (n:=clipped(o)) is not None]
for o in old:bpy.data.objects.remove(o,do_unlink=True)


def material(name,rgb,metal):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*rgb,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=.48
    return m


steel=material('Jamb | oiled steel',(.092,.143,.149),.50)
orange=material('Door casing | burnt orange',(.58,.19,.053),.39)
grip=material('Sill | graphite tread',(.122,.137,.129),.57)


def shape(name,v,f,m):
    data=bpy.data.meshes.new(name)
    data.from_pydata(v,[],f);data.update()
    assert not data.validate()
    data.materials.append(m)
    o=bpy.data.objects.new(name,data)
    scene.collection.objects.link(o)
    return o


def box(name,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    return o


for x in (.095,1.405):
    variant.append(box('Steel inset jamb',(x,-1.08,1.238),(.052,.34,2.046),steel))
    variant.append(box('Orange edge casing',(x,-1.256,1.238),(.056,.045,2.05),orange))
variant.append(box('Steel lintel',(.75,-1.084,2.272),(1.366,.34,.065),steel))
variant.append(box('Orange edge lintel',(.75,-1.256,2.272),(1.366,.045,.075),orange))
# Flush top overlap with the surviving sill at Y=-1.05.
lo,hi=.10,1.4
variant.append(shape('Folded approach ramp',[
    (lo,-2.01,0),(hi,-2.01,0),(hi,-1.07,0),(lo,-1.07,0),
    (lo,-2.01,.006),(hi,-2.01,.006),(hi,-1.07,.2145),(lo,-1.07,.2145),
],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],grip))
bpy.ops.object.select_all(action='DESELECT')
for o in variant:o.select_set(True)
bpy.context.view_layer.objects.active=variant[0]
mesh=out/'e5b-keycard-shed-open.glb'
bpy.ops.export_scene.gltf(filepath=str(mesh),export_format='GLB',use_selection=True,export_animations=False)


def move(objects,delta):
    for o in objects:
        if not o.parent:o.location+=Vector(delta)


def hash_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()


for o in variant:bpy.data.objects.remove(o,do_unlink=True)
variant=load(mesh)
desk_xyz=(-.70,.46,.2145)
card_xyz=(-.38,.36,1.1280)
desk=donor('wsc-kit-006-foreman-desk');move(desk,desk_xyz)
card=donor('wsc-kit-006-vault-keycard');move(card,card_xyz)
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()


def trace(objects, origin, direction, max_length):
    h=[]
    for o in objects:
        inv=o.matrix_world.inverted()
        q,n,i,_=bvh[o].ray_cast(inv@Vector(origin),inv.to_3x3()@Vector(direction),max_length)
        if q is not None:h.append((o.matrix_world@q,o))
    return min(h,key=lambda p:(p[0]-Vector(origin)).length) if h else (None,None)


closed=donor('wsc-prop-065-keycard-shed')
bpy.context.view_layer.update()
bvh={o:BVHTree.FromObject(o,graph) for o in variant+desk+card+closed}
# Sample the usable portal above its sill; same rays on the original
# must hit a front face. Do not count hits on the rear panel.
rays=0
for i in range(13):
    for j in range(15):
        p=(.17+.096*i,-2.1,.254+.134*j)
        assert trace(variant,p,(0,1,0),1.24)[0] is None,p
        assert trace(closed,p,(0,1,0),1.24)[0] is not None,p
        rays+=1
q,_=trace(desk,(-.38,.36,1.30),(0,0,-1),.35)
assert q and abs(q.z-card_xyz[2])<.002,(q,card_xyz)
# Prove the art sits on the original base slab, not on the ground under it.
q,_=trace(variant,(-.70,.46,1.25),(0,0,-1),1.1)
assert q and abs(q.z-desk_xyz[2])<.001,q
for o in closed:bpy.data.objects.remove(o,do_unlink=True)
triangle_count=0
for o in variant:
    o.data.calc_loop_triangles()
    triangle_count+=len(o.data.loop_triangles)
report={
 'scope':'Optional replacement for the original static shed at the same origin; desk and keycard remain separately reusable.',
 'source_sha256':pins,'bytes':mesh.stat().st_size,'triangles':triangle_count,'sha256':hash_file(mesh),
 'doorway_rays_blocked_before_and_clear_after':rays,'cut_blender_m':cut,
 'model_axis':'glTF X right, Y up, Z faces door',
 'desk_gltf_translation_m':[desk_xyz[0],desk_xyz[2],-desk_xyz[1]],
 'card_gltf_translation_m':[card_xyz[0],card_xyz[2],-card_xyz[1]],
 'sill_m':.2145,'walkable_clear_width_m':1.25,
}
(out/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print('PROOF',report,flush=True)

if os.environ.get('WSC_SHED_RENDER') == '1':
    replay=json.loads((out/'trace.json').read_text())['run']
    floor=material('Yard paving',(.16,.18,.19),.10)
    line=material('Measured player path',(.028,.48,.35),.30)
    bs=line.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(.025,.56,.40,1)
    bs.inputs['Emission Strength'].default_value=.55
    box('Temporary yard ground',(0,0,-.10),(24,24,.20),floor)
    def light(name,xyz,aim,power,colour,size):
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=colour;data.size=size
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
        ob.location=xyz;ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler()
        return ob
    light('Outdoor ambient',(-2,-4.3,6),(0,0,1),780,(.61,.78,1),5.0)
    light('Soft jamb edge',(4,-3,3),(.75,-1,1.1),525,(1,.73,.49),3.6)
    light('Temporary desk lamp look',(-.47,.15,1.58),(-.40,.36,1.08),19,(1,.70,.38),.28)
    light('Interior bounce',(1,-.56,1.83),(-.40,.3,1.3),24,(.58,.78,1),.8)
    world=bpy.data.worlds.new('Yard dusk');scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.34,.47,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
    points=replay['frames']
    n=min(range(len(points)),key=lambda i:points[i][2])
    c=bpy.data.curves.new('Measured inward path','CURVE');c.dimensions='3D';c.bevel_depth=.019;c.bevel_resolution=2
    sp=c.splines.new('POLY');sp.points.add(n)
    for p,(x,y,z) in zip(sp.points,points[:n+1],strict=True):p.co=(x,-z,y+.025,1)
    trail=bpy.data.objects.new(c.name,c);scene.collection.objects.link(trail);c.materials.append(line)
    cam=bpy.data.cameras.new('Shed review camera')
    ob=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(ob);scene.camera=ob
    scene.render.engine='CYCLES';scene.cycles.samples=34;scene.cycles.use_denoising=False
    scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.072
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.resolution_x=1320;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=92
    for slug,pos,target,lens in [
        ('entry',(4.75,-6.65,3.03),(.19,-.65,1.35),47),
        ('card',(.81,-.09,1.78),(-.46,.40,1.20),36),
    ]:
        trail.hide_render=slug=='card'
        ob.location=pos;cam.lens=lens
        ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(slug+'.jpg'))
        bpy.ops.render.render(write_still=True)
