"""Reimport one tracked GLB at both exact Band 1 Round 5 chest anchors."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
layout = json.loads((root / 'project/layouts/e1d-band1-scrip-anchors.json').read_text())
glb = root / 'public/assets/wildshard-art/e1d-band1-scrip-opening.glb'
pin = '33ffea4a64ab2caf50f6b89b37f6996d152f313c6b7247f69f9768db70add144'
assert hashlib.sha256(glb.read_bytes()).hexdigest() == pin
args = sys.argv[sys.argv.index('--') + 1:]
out = Path(args[0]).resolve()
out.mkdir(parents=True, exist_ok=True)

def material(name, color, metal=0, rough=.65):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = rough
    return m

def box(name, dims, center, mat, transform=None, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if transform is not None:
        o.matrix_world = transform @ o.matrix_world
    if bevel:
        b = o.modifiers.new('Review bevel', 'BEVEL')
        b.width, b.segments = bevel, 2
        o.modifiers.new('Review normals', 'WEIGHTED_NORMAL')
    return o

def mesh_view(obs):
    deps = bpy.context.evaluated_depsgraph_get()
    verts, tris = [], []
    for ob in obs:
        ob = ob.evaluated_get(deps)
        me = ob.to_mesh()
        me.calc_loop_triangles()
        n = len(verts)
        verts.extend(ob.matrix_world @ v.co for v in me.vertices)
        tris.extend(tuple(i+n for i in t.vertices) for t in me.loop_triangles)
        ob.to_mesh_clear()
    return verts, BVHTree.FromPolygons(verts, tris, all_triangles=True)

def minimum_horizontal_separation(chest_vertices, blockers):
    # Each blocker AABB (world axes) is conservative for the rotated donor.
    # Axis gap is a lower bound on physical separation, not a nearest distance.
    ax = [(min(v[i] for v in chest_vertices), max(v[i] for v in chest_vertices)) for i in range(2)]
    def gap(vs):
        bx = [(min(v[i] for v in vs), max(v[i] for v in vs)) for i in range(2)]
        return max(0, *(max(b[0]-a[1], a[0]-b[1]) for a,b in zip(ax,bx)))
    return min(map(gap, blockers))

results = []
for anchor in layout['anchors']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.fps = 30
    x,z = anchor['three_xz']
    def local(px,pz):
        return (px-x, z-pz, 0)
    def pose(c):
        return Matrix.Translation(local(c['x'],c['z'])) @ Matrix.Rotation(c.get('ry',0),4,'Z')
    bpy.ops.import_scene.gltf(filepath=str(glb))
    chest = [o for o in s.objects if o.type=='MESH']
    actions = list(bpy.data.actions)
    assert len(actions)==1
    f0, f1 = actions[0].frame_range
    assert abs((f1-f0)/s.render.fps-.9) < 1e-5, (f0, f1)
    crate = material('Faded copper enamel',(.29,.13,.057),.32)
    crate2 = material('Oxidised brown enamel',(.165,.085,.043),.27)
    metal = material('Weathered gunmetal rib',(.075,.097,.101),.6)
    rock = material('Slate screed',(.125,.15,.147))
    mat_floor = rock.node_tree.nodes.get('Principled BSDF')
    noise = rock.node_tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 31
    bump = rock.node_tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .22
    bump.inputs['Distance'].default_value = .024
    rock.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
    rock.node_tree.links.new(bump.outputs['Normal'],mat_floor.inputs['Normal'])
    blockers = []
    def cover(c,dims,center,i,styled=True):
        t = pose(c)
        ob = box('Archive cover volume',dims,center,crate if i%2==0 else crate2,t,.042)
        blockers.append(ob)
        if styled:
            # Inset panels stay inside the cover's exact bounding footprint.
            a,b,h = dims
            cx,cy,cz = center
            for side in (-1,1):
                for offs in (-.31,.31):
                    box('Review cargo rib',(.08,.035,h*.78),(cx+offs*a,cy+side*(b/2-.0175),cz),metal,t,.012)
                box('Review cargo header',(a*.84,.039,.085),(cx,cy+side*(b/2-.0195),cz+.32*h),metal,t,.01)
    for c in anchor['cover']:
        if c['kind']=='crates':
            n = 2+math.floor(c['h']*3)
            for i in range(n):
                cover(c,(1.6,1.6,1.6),((i%3)*1.7-1.7,0 if i>=3 else -(i%2)*.4,2.4 if i>=3 else .8),i)
            if n>2:
                cover(c,(1.6,1.6,1.6),(0,0,2.4),2)
        elif c['kind']=='half':
            cover(c,(5,.8,1.1),(0,0,.55),0,False)
            cover(c,(.8,3,1.1),(2.9,-1.1,.55),1,False)
        else:
            raise ValueError(c['kind'])
    # Round 5 shows breakable crate proxies as 1 m cubes (see lab.js).
    for c in anchor['crates']:
        cover(c,(1,1,1),(0,0,.5),1)
        cover(c,(1.02,1.02,.2),(0,0,.5),0,False)
    # Creature envelopes are conservative 1.04 m squares, not rig/aggro proof.
    for pack in anchor['packs']:
        for k in range(pack['size']):
            a=k*2.4+1
            p=local(pack['x']+3.2*math.cos(a),pack['z']+3.2*math.sin(a))
            ob=box('Archived Mite spawn envelope', (1.04,1.04,1.07),(p[0],p[1],.535),metal,None,0)
            ob.hide_render=True
            blockers.append(ob)
    bpy.context.view_layer.update()
    block_vertices = [mesh_view([ob])[0] for ob in blockers]
    block_tree = mesh_view(blockers)[1]
    # Constant-width sampled section is backed by a continuous AABB at the front.
    corridor = box('Front approach, 0.9 m clear width',(.9,2.02,1.7),(0,-1.99,.85),metal)
    cv,ct = mesh_view([corridor])
    assert not ct.overlap(block_tree)
    corridor_sep = minimum_horizontal_separation(cv,block_vertices)
    assert corridor_sep > 0
    bpy.data.objects.remove(corridor,do_unlink=True)
    gaps=[]
    for k in range(109):
        f=f0+(f1-f0)*k/108
        s.frame_set(math.floor(f),subframe=f%1)
        vv,bt=mesh_view(chest)
        assert not bt.overlap(block_tree), (anchor['index'],k)
        assert .0001 > abs(min(v.z for v in vv)), (anchor['index'],k)
        assert not bt.overlap(ct), (anchor['index'],k)
        gaps.append(minimum_horizontal_separation(vv,block_vertices))
    assert min(gaps)>0
    results.append(dict(anchor=anchor['index'],three_xz=anchor['three_xz'],yaw_degrees=0,
                        continuous_approach_clear_width_m=.9,
                        approach_front_z_offsets_m=[.98,3.0],
                        nearby_blocker_count=len(blockers), lid_samples=109,
                        minimum_lid_horizontal_aabb_gap_m=round(min(gaps),6),
                        minimum_approach_horizontal_aabb_gap_m=round(corridor_sep,6),
                        intersecting_sample_count=0))
    print(results[-1],flush=True)
    if '--proof-only' in args:
        continue
    box('Review screed', (76,76,.24),(0,0,-.12),rock)
    world = bpy.data.worlds.new('Muted blue sky')
    world.use_nodes=True
    bg=world.node_tree.nodes.get('Background')
    bg.inputs[0].default_value=(.42,.58,.75,1)
    bg.inputs[1].default_value=.58
    s.world=world
    light=bpy.data.lights.new('Warm East sun','SUN')
    light.energy=2.8
    light.color=(1,.865,.69)
    light.angle=math.radians(5)
    sun=bpy.data.objects.new(light.name,light)
    s.collection.objects.link(sun)
    sun.rotation_euler=Vector((.62,.37,-1)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(1.68,-3.25,1.70))
    cam=bpy.context.object
    cam.data.lens=34
    cam.rotation_euler=(Vector((-.30,.18,.72))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.camera=cam
    s.render.engine='CYCLES'
    s.cycles.samples=36
    s.cycles.use_adaptive_sampling=True
    s.cycles.adaptive_threshold=.07
    s.cycles.use_denoising=False
    s.view_settings.view_transform='AgX'
    s.view_settings.look='AgX - Medium High Contrast'
    s.render.resolution_x,s.render.resolution_y=1000,1030
    s.render.resolution_percentage=100
    f=f0 if anchor['index']==1 else f1
    s.frame_set(math.floor(f),subframe=f%1)
    s.render.filepath=str(out / f'anchor-{anchor["index"]}.png')
    bpy.ops.render.render(write_still=True)
(out/'proof.json').write_text(json.dumps(dict(glb_sha256=pin,sites=results,
    scope='Round 5 blockout only; no runtime geometry, enemies, currency, claim state, or touch validation.'),indent=2)+'\n')
