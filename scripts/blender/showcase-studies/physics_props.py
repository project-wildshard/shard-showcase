"""Rebuild four standalone West Physics Yard GLBs; no dependency on a .blend."""
from pathlib import Path
import math
import sys

import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

OUT = output_directory()
TAU = math.tau

def finish(name, hex_srgb, roughness, metal=0):
    def linear(n):
        s = n / 255
        return s / 12.92 if s <= .04045 else ((s + .055) / 1.055) ** 2.4
    color = tuple(linear((hex_srgb >> n) & 255) for n in (16, 8, 0)) + (1,)
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Metallic'].default_value = metal
    shader.inputs['Roughness'].default_value = roughness
    return mat

steel = finish('Charcoal forged steel', 0x37494b, .54, .62)
zinc = finish('Brushed zinc', 0x98a09b, .34, .72)
orange = finish('Safety orange enamel', 0xc96c28, .53, .35)
dark = finish('Rubber gasket', 0x202b2b, .86)
cream = finish('Ivory pin enamel', 0xe9d6a9, .49)
teal = finish('Verdigris tread', 0x418482, .70, .54)
wood = [finish('Treated timber ' + str(i), c, .79) for i, c in enumerate((0xa45d2b, 0xb4763a, 0xb16530, 0x995427))]
mark = finish('Painted ID stripe', 0xe3ae52, .75)

def box(n, center, dims, mat, bevel=.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = n
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(mat)
    return o

def rod(n, a, b, radius, mat, sides=10):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = n
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    return o

def group(name, objects, origin=(0,0,0)):
    # One mesh per movable part. Bake its transform, then restore its authored pivot.
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    bpy.context.scene.cursor.location = origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return o

def seesaw():
    a = []
    for y in (-1, 1):
        a += [box('Sill', (0,y,.12), (3.1,.54,.24), steel, .04)]
        for x in (-1.32, 1.32):
            a += [rod('A-frame brace', (x,y,.20), (0,y,1.43), .16, orange),
                  rod('Foot bolt', (x,y,.24), (x,y,.28), .083, zinc, 8)]
        a += [rod('Axle boss', (0,y-.22,1.47), (0,y+.22,1.47), .29, steel, 12)]
    a += [rod('Hinge axle', (0,-1.48,1.47), (0,1.48,1.47), .17, zinc, 12)]
    b = [box('Beam', (0,0,1.52), (13.9,1.9,.22), steel, .04)]
    for i in range(14):
        b += [box('Deck board', (i-6.5,0,1.72), (.985,2.6,.19), wood[i%4], .028)]
    for x in (-6.77, 6.77):
        b += [box('End tread', (x,0,1.835), (.42,2.53,.045), orange, .017)]
        for y in (-.88,0,.88):
            b += [box('Grip stripe', (x,y,1.865), (.30,.09,.008), mark)]
    return [group('Fixed_Base',a),group('Hinged_Deck',b,(0,0,1.47))]

def ball():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=.8, location=(0,0,0))
    o=bpy.context.object
    o.name='Ball_Center_Pivot'
    for m in (orange,steel,zinc):
        o.data.materials.append(m)
    for f in o.data.polygons:
        z=f.center.z
        if abs(z)<.12:
            f.material_index=1
        elif .45<abs(z)<.61:
            f.material_index=2
        else:
            f.material_index=0
        f.use_smooth=True
    return [o]

def pin():
    profile=[(.24,0),(.29,.04),(.29,.11),(.275,.19),(.243,.68),(.209,.98),(.193,1.10),(.165,1.23),(.10,1.29)]
    n=14
    vs=[(radius*math.cos(i*TAU/n),radius*math.sin(i*TAU/n),z) for radius,z in profile for i in range(n)]
    faces=[tuple(reversed(range(n)))]
    bands=[0]
    for j in range(len(profile)-1):
        for i in range(n):
            q=(i+1)%n
            faces.append((j*n+i,j*n+q,(j+1)*n+q,(j+1)*n+i))
            bands.append(0 if j<2 else 2 if j in (5,6) else 1)
    faces.append(tuple(range(len(vs)-n,len(vs))))
    bands.append(1)
    m=bpy.data.meshes.new('Skittle lathed profile')
    m.from_pydata(vs,[],faces)
    m.update()
    o=bpy.data.objects.new('Skittle_Floor_Pivot',m)
    bpy.context.collection.objects.link(o)
    for f in (dark,cream,orange):
        m.materials.append(f)
    for f,i in zip(m.polygons,bands):
        f.material_index=i
        f.use_smooth=len(f.vertices)==4
    return [o]

def plate():
    a=[box('Inset frame',(0,0,.10),(4,4,.20),steel,.09)]
    a += [box('Bed seal',(0,0,.21),(3.76,3.76,.061),dark,.029)]
    for x in (-1.83,1.83):
        for y in (-1.83,1.83):
            a += [rod('Anchor',(x,y,.20),(x,y,.225),.078,zinc,8)]
    b=[box('Depressible tread',(0,0,.28),(3.54,3.54,.09),teal,.048)]
    for j in range(-4,5):
        b += [box('Raised traction rib',(0,j*.25,.331),(2.63,.077,.023),steel,.009)]
    for y in (-1.53,1.53):
        b += [box('Approach stripe',(0,y,.33),(2.93,.093,.013),mark)]
    return [group('Fixed_Frame',a),group('Moving_Tread',b,(0,0,.28))]

MODELS = {
    'wsc-plan-003-hinged-seesaw':seesaw,
    'wsc-plan-004-rolling-ball':ball,
    'wsc-plan-005-skittle-pin':pin,
    'wsc-plan-006-pressure-plate':plate,
}
for name, build in MODELS.items():
    clear_scene()
    export(build(), OUT / (name + '.glb'))

# Optional visual QA and a single repro-ready contact sheet, not a shipped asset.
if __import__('os').environ.get('WSC_PHYSICS_RENDER') == '1':
    clear_scene()
    positions=[(-3.8,3.3,0),(2.15,-2.4,.8),(3.9,-2.4,0),(-1.75,-2,0)]
    for name,pos in zip(MODELS,positions):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT / (name+'.glb')))
        for o in set(bpy.context.scene.objects)-before:
            if o.parent is None:
                o.location += Vector(pos)
    ground=finish('Studio blue gray',0x344757,.9)
    box('Studio ground',(0,0,-.095),(200,200,.15),ground)
    scene=bpy.context.scene
    scene.world.color=(.32,.32,.32)
    def aim(o,p):
        o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
    for n,p,power,size,c in [('Key',(-7,-8,15),2900,7,(1,.85,.70)),('Fill',(7,-2,11),1400,8,(.68,.83,1)),('Rim',(2,8,14),2250,6,(1,.93,.8))]:
        bpy.ops.object.light_add(type='AREA',location=p)
        o=bpy.context.object
        o.name=n
        o.data.energy=power
        o.data.size=size
        o.data.color=c
        aim(o,(0,1,0))
    bpy.ops.object.camera_add(location=(7,-19,16))
    scene.camera=bpy.context.object
    aim(scene.camera,(-2.2,.6,.3))
    scene.camera.data.type='ORTHO'
    scene.camera.data.ortho_scale=19
    scene.render.engine='CYCLES'
    scene.cycles.samples=48
    scene.cycles.use_denoising=False
    scene.render.resolution_x=1280
    scene.render.resolution_y=880
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='JPEG'
    scene.render.image_settings.quality=90
    scene.render.filepath=str(OUT/'west-physics-props.jpg')
    bpy.ops.render.render(write_still=True)
