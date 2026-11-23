"""Extract the exact W5a bowl, funbox and quarter pipe from the reproducible park build."""
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

a=argparse.ArgumentParser()
a.add_argument('--park-build',type=Path,required=True)
a.add_argument('--output',type=Path,required=True)
args=a.parse_args(sys.argv[sys.argv.index('--')+1:])
out=args.output.resolve()
out.mkdir(parents=True,exist_ok=True)
src=args.park_build/'hover-park-editable.blend'
assert src.is_file() and (args.park_build/'parity.json').is_file()
bpy.ops.wm.open_mainfile(filepath=str(src))
S=bpy.context.scene
def get(n):
    o,=[o for o in S.objects if o.name==f'HOVER | {n}' and o.type=='MESH']
    return o

I=Matrix.Identity(4)
def ordered_mesh(ob, transformation=I):
    """Drop genuinely zero-area triangles without changing surviving material assignments."""
    coords=[transformation @ ob.matrix_world @ v.co for v in ob.data.vertices]
    ob.data.calc_loop_triangles()
    rec=[]
    degenerate=0
    for tri in ob.data.loop_triangles:
        pts=[coords[i] for i in tri.vertices]
        if (pts[1]-pts[0]).cross(pts[2]-pts[0]).length_squared<1e-14:
            degenerate+=1
            continue
        rec.append((pts,ob.data.polygons[tri.polygon_index].material_index))
    return rec,degenerate
def canonical(records,mats):
    return Counter((mats[k].name.split('.')[0], tuple(sorted(tuple(round(t,4) for t in p) for p in row))) for row,k in records)

entries=[
    ('bowl','24m bowl lip centered on source',(-212,-216,0),'wsc-kit-003-hover-bowl-24m.glb'),
    ('funbox','four-ramp funbox',(-145,-206,0),'wsc-kit-003-hover-funbox.glb'),
    ('quarter','quarter pipe -122',(-122,-206,0),'wsc-kit-003-hover-quarter-pipe.glb'),
]
reverse=get('quarter pipe -168')
want={};saved={};stats={}
for key,source,center,filename in entries:
    donor=get(source)
    local=Matrix.Translation(-Vector(center))
    rows,drops=ordered_mesh(donor,local)
    # Mesh is local and uses the original static face colors and triangulation.
    V=[];index={};faces=[]
    for row,_ in rows:
        idx=[]
        for p in row:
            t=tuple(p)
            if t not in index:
                index[t]=len(V);V.append(t)
            idx.append(index[t])
        assert len(set(idx))==3
        faces.append(idx)
    md=bpy.data.meshes.new(source)
    md.from_pydata(V,[],faces);md.update()
    for m in donor.data.materials:
        md.materials.append(m)
    for face,(_,i) in zip(md.polygons,rows):
        face.material_index=i
    ob=bpy.data.objects.new(f'W5a | {source}',md)
    S.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    target=out/filename
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,
                              export_animations=False,export_texcoords=False,export_normals=True)
    saved[key]=target
    want[key]=canonical(rows,donor.data.materials)
    stats[key]=dict(source_object=donor.name,file=filename,origin_blender_world_m=center,
                    triangles=len(rows),removed_zero_area_triangles=drops,
                    raw_bytes=target.stat().st_size)
    if key=='quarter':
        # Reversed planar quads can triangulate with the other diagonal.
        # Compare exact authored polygons and materials before triangulation.
        def polygons(ob, transform):
            return [([transform@ob.matrix_world@ob.data.vertices[i].co for i in f.vertices],
                      f.material_index) for f in ob.data.polygons]
        back=Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation(-Vector((-168,-206,0)))
        assert canonical(polygons(reverse,back),reverse.data.materials)==canonical(polygons(donor,local),donor.data.materials)

# The publishable geometry is taken from the reimport, not the intermediate source mesh.
for o in tuple(S.objects):
    bpy.data.objects.remove(o,do_unlink=True)
objs={}
for key,path in saved.items():
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    ob,=[o for o in set(S.objects)-before if o.type=='MESH']
    bpy.context.view_layer.update()
    assert ob.matrix_world.translation.length<1e-7
    r,degen=ordered_mesh(ob)
    assert not degen
    assert canonical(r,ob.data.materials)==want[key]
    points=[p for row,_ in r for p in row]
    stats[key]['local_bounds_blender_m']=[[round(fn(p[i] for p in points),6) for i in range(3)] for fn in (min,max)]
    objs[key]=ob

def surface_height(ob,x,y):
    tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
    q,n,*_=tree.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),11)
    assert q is not None,(ob.name,x,y)
    assert n.z>.2,(ob.name,x,y,n)
    return round(q.z,4)
bowl=objs['bowl']
for r,z in ((.11,.02),(7.5,.02),(9.5,.57),(12.15,3.5)):
    for t in [k*math.tau/8 for k in range(8)]:
        actual=surface_height(bowl,r*math.cos(t),r*math.sin(t))
        assert abs(actual-z)<.008,(r,t,actual,z)
assert stats['bowl']['removed_zero_area_triangles']==64
assert stats['bowl']['local_bounds_blender_m'][1][0] == 12.449997
for x,y,z in [(0,0,1.8),(7.5,0,.904),(-7.5,0,.904),(0,7.5,.904),(0,-7.5,.904)]:
    assert abs(surface_height(objs['funbox'],x,y)-z)<.007
assert abs(surface_height(objs['quarter'],5.90,0)-4.8403)<.003
manifest=dict(catalogue_id='WSC-KIT-003',scene_support_id='WSC-SCENE-003',
              scope='Static W5a reuse proof; no route eligibility, collision, traversal, scoring or performance.',
              source='scripts/blender/west-hover/assemble.py from tracked build',
              coordinates='Blender x,y,z metres. World glTF x,z,-y.',
              assets=stats,
              design_bowl_place=[-212,-216,0],nominal_inner_bowl_lip_diameter_m=24,
              bowl_outer_diameter_m=24.9,bowl_lip_z_m=3.5,bowl_floor_z_m=.02,
              funbox_platform_m=[10,10,1.8],quarter_pipe_count_in_scene=2,
              quarter_second_world_blender_xyz=[-168,-206,0],quarter_second_yaw_deg=180,
              total_geometry_bytes=sum(x['raw_bytes'] for x in stats.values()))
(out/'w5a-secondary-kit.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('W5A_SECONDARY',stats)
if os.getenv('WSC_METADATA_ONLY')=='1':
    sys.exit(0)

# One existing modular bowl, one funbox and one quarter donor; no scene export.
region=Vector((-178,-206,0))
for k,ob in objs.items():
    ob.location=Vector(stats[k]['origin_blender_world_m'])-region
extra=bpy.data.objects.new('W5a | facing quarter reuse',objs['quarter'].data)
S.collection.objects.link(extra)
extra.location=Vector((-168,-206,0))-region
extra.rotation_euler.z=math.pi
bpy.context.view_layer.update()

def mat(n,c,rough=.75):
    x=bpy.data.materials.new(n)
    x.use_nodes=True
    q=x.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*c,1)
    q.inputs['Roughness'].default_value=rough
    return x

floor=mat('Warm fine aggregate',(.243,.267,.210),.86)
q=floor.node_tree.nodes.get('Principled BSDF')
n=floor.node_tree.nodes
links=floor.node_tree.links
co=n.new('ShaderNodeTexCoord')
noise=n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=46
links.new(co.outputs['Object'],noise.inputs['Vector'])
bump=n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.18
bump.inputs['Distance'].default_value=.06
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],q.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-.004))
bpy.context.object.data.materials.append(floor)
edge=mat('Muted lane boundary',(.42,.36,.23))
stripe=mat('Grit tape cream',(.63,.58,.42))
def patch(n,xyz,w,d,m):
    bpy.ops.mesh.primitive_plane_add(size=1,location=xyz)
    ob=bpy.context.object;ob.name=n;ob.scale.x=w;ob.scale.y=d
    ob.data.materials.append(m)
# Off-obstacle ground markings are render staging only.
for x in range(-49,64,4):
    for y in (-25,17):
        patch('Outline dash',(x,y,.005),2.25,.12,stripe)
for x in (-54,65):
    patch('Edge strip',(x,-4,.004),.21,42,edge)

S.world=bpy.data.worlds.new('West blue sky')
S.world.use_nodes=True
n=S.world.node_tree.nodes
bg=n.get('Background')
sky=n.new('ShaderNodeTexSky')
sky.sky_type='NISHITA'
sky.sun_rotation=1.1;sky.sun_elevation=.55;sky.sun_intensity=.54
S.world.node_tree.links.new(sky.outputs['Color'],bg.inputs[0]);bg.inputs[1].default_value=.22
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(36),math.radians(-24),math.radians(31)))
bpy.context.object.data.energy=1.46
bpy.context.object.data.color=(1,.86,.67)
bpy.context.object.data.angle=.12
def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
S.render.engine='CYCLES';S.cycles.samples=38;S.cycles.use_denoising=False
S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.085
S.view_settings.exposure=-.25
S.render.resolution_x=1520;S.render.resolution_y=920;S.render.resolution_percentage=100
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=90
for name,eye,target,lens in [
    ('nov23-hover-secondary-overview',(-13,-78,60),(3,-5,.3),30),
    ('nov23-hover-secondary-bowl',(-48,-27,7),(-18,-5,1),32),
]:
    bpy.ops.object.camera_add(location=eye)
    S.camera=bpy.context.object
    aim(S.camera,target)
    S.camera.data.lens=lens
    S.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
