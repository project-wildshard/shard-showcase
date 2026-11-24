"""W9b NW and SW art-camera studies using pinned GLBs; no map edits."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

OUT=output_directory()
ASSETS=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
FILE='w9b-corner-vista-pad.glb'
FILES={
    'bench':('wsc-prop-044-lookout-bench','9109111c13a27c81981839237b9f1880c9e964930f5888e24c1054ac819bfeb1'),
    'gantry':('wsc-module-010-riding-start-gantry','784738b070cdf0d5b400355249d0b3f12697369064274433857b9793b5786774'),
    'fence':('wsc-module-011-riding-fence','4b080d634287a167eba8cc4690b7fbedd0323244154a7bb96402262b71c4afe0'),
    'funbox':('wsc-kit-003-hover-funbox','8ca1480074d3641c126ea154268de36705c81495d078fd2d3dbb020bf4d57ebf'),
    'bowl':('wsc-kit-003-hover-bowl-24m','bc914064823498a59ab74252ad034378d5cb16d87f3fe3b8e98e8914edb7deb1'),
    'tree':('wsc-prop-046-conifer-tree-far','43362bfe9c1673367c0065eef2eb88759564a69df379feb2f27dc140e9a699a6'),
    'boulder':('wsc-prop-036-landscape-boulder','d03ed70f69d230fa82c474770eb65a991189cbf4848db4fc750ec1cb6f812750'),
    'flower':('wsc-prop-047-wildflower-clump-far','e67cfc6fd4d86d239929e0ba36239a8abbc0387410b0265b6fb1a635286c9d98'),
}
for f,sha in FILES.values():
    assert hashlib.sha256((ASSETS/(f+'.glb')).read_bytes()).hexdigest()==sha

def mat(n,c,rough=.7,metal=0):
    m=bpy.data.materials.get(n)
    if m:return m
    m=bpy.data.materials.new(n)
    m.diffuse_color=(*c,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal)]:
        p.inputs[k].default_value=v
    return m

def mesh(n,vs,fs,m):
    data=bpy.data.meshes.new(n)
    data.from_pydata(vs,[],fs)
    data.update()
    o=bpy.data.objects.new(n,data)
    bpy.context.collection.objects.link(o)
    data.materials.append(m)
    return o

def box(n,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=n
    o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    return o

def load(path, xyz=(0,0,0), angle=0, scale=1):
    prior=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    parts=sorted(set(bpy.context.scene.objects)-prior,key=lambda o:o.name)
    tr=Matrix.Translation(xyz)@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)
    for o in parts:
        if o.parent is None:o.matrix_world=tr@o.matrix_world
    bpy.context.view_layer.update()
    return parts

def donor(key,p,ang=0,scale=1):
    return load(ASSETS/(FILES[key][0]+'.glb'),p,ang,scale)

def verts(parts):
    return [o.matrix_world @ v.co for o in parts if o.type=='MESH' for v in o.data.vertices]

# Textured in the review scene only. The reusable pad exports flat, portable materials.
clear_scene()
paving=mat('Fine blue granite',(.155,.174,.176),.89)
border=mat('Honed outer curb',(.28,.31,.301),.69)
bronze=mat('Inlaid cache-route bronze',(.30,.185,.068),.52,.45)
seal=mat('Recess shadow',(.048,.065,.064))
N=24
pads=[]
def rings(r0,r1,z0,z1,m,name):
    vs=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)
        for r,z in ((r0,z0),(r1,z0),(r1,z1),(r0,z1)) for i in range(N)]
    fs=[]
    for j in range(4):
        for i in range(N):
            nxt=(i+1)%N
            fs.append((j*N+i,j*N+nxt,((j+1)%4)*N+nxt,((j+1)%4)*N+i))
    return mesh(name,vs,fs,m)
vs=[(2.40*math.cos(i*math.tau/N),2.40*math.sin(i*math.tau/N),0) for i in range(N)]
pads.append(mesh('Bench paving surface',vs,[tuple(range(N))],paving))
pads.append(rings(2.40,2.435,-.07,-.006,seal,'Inset seal'))
pads.append(rings(2.435,2.79,-.08,0,border,'Stone collar'))
pads.append(rings(2.535,2.56,-.025,.001,bronze,'Inlaid ribbon'))
for a in (math.pi/4,math.pi*3/4,math.pi*5/4,math.pi*7/4):
    o=box('Quadrant datum',(2.66*math.cos(a),2.66*math.sin(a),.001),(.19,.028,.002),bronze)
    o.rotation_euler.z=a
export(pads,OUT/FILE)
clear_scene()
pp=verts(load(OUT/FILE))
radius=max(math.hypot(v.x,v.y) for v in pp)
assert 2.78<radius<2.80
assert min(v.z for v in pp)<-.07 and max(v.z for v in pp)<.004
clear_scene()

# Round 5 lab.js draws benches +2 m on map Z from their discovery anchors.
records={
    'nw': {'anchor':[-229,0,-229],'bench':[-229,0,-227],'aim_map':[-126,0.85,-178]},
    'sw': {'anchor':[-229,0,229],'bench':[-229,0,231],'aim_map':[-148,1.7,228]},
}
# Round 5 STRIP starts at |x| or |z|=237. Preserve the rim- and course-side gaps.
for row in records.values():
    x,z=row['bench'][::2]
    row['clear_to_rim_m']=237-max(abs(x),abs(z))-radius
    assert row['clear_to_rim_m']>3.2
# Riding capsule: point to center segment [-182,-62] at world z=-186, less outer r=44.
x,z=records['nw']['bench'][::2]
records['nw']['clear_to_subject_m']=math.hypot(x+182,z+186)-44-radius
x,z=records['sw']['bench'][::2]
records['sw']['clear_to_subject_m']=math.hypot(x+212,z-216)-12.45-radius
assert records['nw']['clear_to_subject_m']>15 and records['sw']['clear_to_subject_m']>7

def ground_mat():
    m=mat('Verge grass',(.18,.21,.086),.83)
    nt=m.node_tree
    if nt.nodes.get('Grass tones'):return m
    tc=nt.nodes.new('ShaderNodeTexCoord')
    tex=nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=.21
    tex.inputs['Detail'].default_value=4
    nt.links.new(tc.outputs['Object'],tex.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.name='Grass tones'
    ramp.color_ramp.elements[0].position=.19
    ramp.color_ramp.elements[0].color=(.052,.089,.032,1)
    ramp.color_ramp.elements[1].position=.88
    ramp.color_ramp.elements[1].color=(.245,.28,.115,1)
    nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    return m

def capsule_band(cx,cy,r0,r1,width,m):
    vs=[]
    for r in (r0,r1):
        for sign in [-1,1]:
            for i in range(33):
                a=(.5*math.pi if sign==-1 else -.5*math.pi)+math.pi*i/32
                vs.append((cx+sign*width+r*math.cos(a),cy+r*math.sin(a),-.005))
    fs=[(i,(i+1)%66,(i+1)%66+66,i+66) for i in range(66)]
    return mesh('Measured oval ribbon',vs,[tuple(reversed(f)) for f in fs],m)

def hills():
    r=random.Random(91)
    sky=[(.108,.145,.154),(.156,.204,.214),(.22,.25,.263)]
    for k in range(3):
        vs=[]
        origin=Vector((-229,0,0))
        for i in range(100):
            a=math.radians(-105+210*i/99)
            rad=510+k*100
            x,y=origin.x+math.cos(a)*rad,math.sin(a)*rad
            peak=13+k*5+16*abs(math.sin(a*5+k))*abs(math.cos(a*2.5+k*2))+r.uniform(0,4)
            vs.extend([(x,y,-7),(x,y,peak)])
        m=mat('Painted distant ridge '+str(k),sky[k])
        mesh('Painted horizon',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(99)],m)

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def setup_camera(row):
    x,z=row['bench'][::2]
    bp=Vector((x,-z,0))
    tx,ty,tz=row['aim_map']
    target=Vector((tx,-tz,ty))
    direction=(Vector((target.x,target.y,0))-bp).normalized()
    angle=math.atan2(direction.x,-direction.y)   # original seat faces local -Y.
    bench=verts(donor('bench',bp,angle))
    assert abs(min(v.z for v in bench))<1e-5 and .60<max(v.z for v in bench)<.61
    plate=verts(load(OUT/FILE,bp,angle))
    assert abs(min(v.x for v in plate)-x)<radius+.01
    eye=bp+direction*.16+Vector((0,0,1.48))
    row['eye_world_xyz_m']=[eye.x,eye.z,-eye.y]
    row['yaw_degrees_blender']=math.degrees(angle)
    return eye,target,direction,bp

def glazing(n,m,left,right):
    # Narrow irregular footpath used only for camera composition.
    border_left=left
    border_right=right
    vs=border_left+border_right
    q=len(border_left)
    return mesh(n,vs,[(i,i+q,i+q+1,i+1) for i in range(q-1)],m)

def views(key,row):
    clear_scene()
    s=bpy.context.scene
    eye,target,heading,bp=setup_camera(row)
    g=ground_mat()
    # Off-map context, apron and quarry light are staged only.
    box('Meadow ground',(-82,0,-.070),(620,620,.122),g)
    strip=mat('Dusty perimeter strip',(.30,.238,.140),.89)
    box('West strip',(-242,0,-.046),(10,494,.074),strip)
    box('North/South strip',(0,242 if key=='nw' else -242,-.046),(474,10,.075),strip)
    side=Vector((-heading.y,heading.x,0))
    path=mat('Fine compacted chalk',(.31,.258,.168),.93)
    left=[]
    right=[]
    for i in range(18):
        d=2.6+1.08*i
        arc=.0081*d*d
        h=bp+heading*d+side*arc
        w=.64+math.sin(i*.9)*.10
        for lane,sign in [(left,-1),(right,1)]:
            v=h+side*sign*w
            lane.append((v.x,v.y,-.004))
    glazing('Illustrative vista path',path,left,right)
    if key=='nw':
        capsule_band(-122,186,32,44,60,mat('Amber riding soil',(.28,.126,.047),.91))
        capsule_band(-122,186,44,44.18,60,mat('Pale arena edging',(.43,.32,.185),.88))
        capsule_band(-122,186,31.82,32,60,mat('Pale arena edging',(.43,.32,.185),.88))
        donor('gantry',(-80,148,0))
        for i in range(31):
            a=math.radians(101+i*4.15)
            donor('fence',(-182+44.55*math.cos(a),186+44.55*math.sin(a),0),a+math.pi/2)
        for i in range(14):
            donor('fence',(-180+3.22*i,230.55,0),0)
        # Arena side is left open so the near bend remains visible.
        tree_locs=[(-208,226),(-191,227),(-176,210),(-163,225),(-135,227),(-120,231),(-215,184),(-208,171),(-192,153),(-152,139)]
    else:
        donor('bowl',(-212,-216,0))
        donor('funbox',(-145,-206,0))
        tree_locs=[(-224,-203),(-226,-187),(-193,-209),(-179,-215),(-181,-193),(-165,-182),(-162,-220),(-159,-203),(-150,-189),(-134,-210)]
    r=random.Random(789 if key=='nw' else 887)
    for i,(x,y) in enumerate(tree_locs):
        donor('tree',(x,y,0),r.uniform(0,math.tau),r.uniform(.7,1.34))
    for d,n in [(3.0,-2.4),(3.6,2.15),(6,-3.4),(6.7,4.6),(11,-5.7),(13,6.6)]:
        p=bp+heading*d+side*n
        donor('boulder',p, r.uniform(0,math.tau),r.uniform(.45,.78))
        for j in range(3):
            p2=p+heading*(.43+j*.37)+side*(j*.54*math.copysign(1,n))
            donor('flower',p2,r.uniform(0,math.tau),r.uniform(.66,.91))
    hills()
    w=s.world
    w.use_nodes=True
    nt=w.node_tree
    sky=nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type='NISHITA'
    sky.sun_elevation=math.radians(21 if key=='nw' else 31)
    sky.sun_rotation=math.radians(120 if key=='nw' else 225)
    sky.sun_disc=False
    bg=nt.nodes.get('Background')
    nt.links.new(sky.outputs[0],bg.inputs[0])
    bg.inputs['Strength'].default_value=.17
    bpy.ops.object.light_add(type='SUN',location=(-230,-58,60))
    o=bpy.context.object
    aim(o,(-90,22,0) if key=='nw' else (-170,-160,0))
    o.data.energy=2.1
    o.data.color=(1,.83,.61) if key=='nw' else (.86,.90,1)
    o.data.angle=.065
    bpy.ops.object.camera_add(location=eye)
    s.camera=bpy.context.object
    aim(s.camera,target)
    s.camera.data.lens=31 if key=='nw' else 24
    s.camera.data.clip_end=1100
    s.render.engine='CYCLES'
    s.cycles.samples=32
    s.cycles.use_denoising=False
    s.render.resolution_x=1440
    s.render.resolution_y=900
    s.render.resolution_percentage=100
    s.render.image_settings.file_format='JPEG'
    s.render.image_settings.quality=90
    s.view_settings.view_transform='AgX'
    s.view_settings.look='AgX - Medium High Contrast'
    s.render.filepath=str(OUT/(f'corner-{key}-seated.jpg'))
    bpy.ops.render.render(write_still=True)
    if key=='sw':
        prove_bowl_occlusion(row,eye,target)
        # One three-quarter view explains what the seated images alone cannot: the shared pad.
        s.camera.location=bp-heading*6.2+side*4.0+Vector((0,0,3.7))
        aim(s.camera,bp+heading*1.0+Vector((0,0,.40)))
        s.camera.data.lens=33
        s.render.filepath=str(OUT/'corner-pad-approach.jpg')
        bpy.ops.render.render(write_still=True)

def prove_bowl_occlusion(row, eye, target):
    # Ground-level seat does not see the bowl floor. Test the exact donor.
    s=bpy.context.scene
    bpy.context.view_layer.update()
    target_floor=Vector((-212,-216,.08))
    diff=target_floor-eye
    hit,_,_,_,obj,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),eye,diff.normalized(),distance=diff.length-.02)
    assert hit and obj and ('bowl' in obj.name.lower() or 'lip' in obj.name.lower()), obj
    row['bowl_floor_ray']='occluded in study by '+obj.name
    glance=target-eye
    h,_,_,_,blocker,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),eye,glance.normalized(),distance=glance.length-.03)
    assert not h, blocker
    row['oblique_center_ray_clear']=True

for k,row in records.items():
    if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
        clear_scene()
        eye,target,*_=setup_camera(row)
        if k=='sw':
            donor('bowl',(-212,-216,0))
            prove_bowl_occlusion(row,eye,target)
    else:
        views(k,row)
(OUT/'corner-vista-proof.json').write_text(json.dumps(records,indent=2)+'\n')
