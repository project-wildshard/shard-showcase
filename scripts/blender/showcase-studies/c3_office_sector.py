"""C3 office sector, sourced static geometry; run in Blender 4.3 with -- OUT."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
clear_scene()
sc = bpy.context.scene
turn = math.pi/4
outer = math.radians(24)
r_deck = math.hypot(29, 29)
r_office = math.hypot(35, 35)
r_start = r_deck - 3.5


def shade(n, rgb, metal=0, rough=.63):
    m = bpy.data.materials.new(n)
    m.diffuse_color = (*rgb,1)
    m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1)
    b.inputs['Metallic'].default_value=metal
    b.inputs['Roughness'].default_value=rough
    return m


sand=shade('Tamped copper earth',(.36,.223,.125))
step=shade('Warm cast concrete',(.42,.30,.216))
orange=shade('Oxide orange structural panels',(.44,.119,.035),.29)
edge=shade('Faded orange flashing',(.65,.236,.067),.40,.48)
grey=shade('Factory office graphite',(.102,.136,.149),.34)
trim=shade('Blackened steel',(.048,.071,.084),.58,.48)
light=shade('Honey office glazing',(.63,.26,.052),.25,.29)
rail=shade('Amber side guard',(.86,.39,.048),.44)
chalk=shade('Floor inset paint, worn ochre',(.68,.46,.20),0,.79)


def mesh(name,xyz,faces,mat):
    d=bpy.data.meshes.new(name)
    d.from_pydata(xyz,[],faces)
    d.materials.append(mat)
    o=bpy.data.objects.new(name,d)
    sc.collection.objects.link(o)
    return o


def box(n,px,py,pz,w,d,h,mat,yaw=0, bevel=.035):
    c,s=math.cos(yaw),math.sin(yaw)
    v=[(px+c*x-s*y,py+s*x+c*y,pz+z)
       for z in (-h/2,h/2) for y in (-d/2,d/2) for x in (-w/2,w/2)]
    o=mesh(n,v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat)
    if bevel:
        mod=o.modifiers.new('Flashing edges','BEVEL')
        mod.width,mod.segments=bevel,1
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o


def ring(n, r0, r1, z0, z1, mat, a0=-outer, a1=outer, N=48):
    pts=[]
    for i in range(N+1):
        a=a0+(a1-a0)*i/N
        pts.extend((r*math.cos(a), r*math.sin(a), z)
                   for r,z in [(r0,z0),(r1,z0),(r1,z1),(r0,z1)])
    faces=[(3,2,1,0)]
    for i in range(N):
        b=i*4
        for a in range(4):
            j=(a+1)%4
            faces.append((b+a,b+j,b+j+4,b+a+4))
    faces.append(tuple(range(N*4,N*4+4)))
    return mesh(n,pts,faces,mat)


# Truncated court sector only. No scene collision, gate or spawn geometry.
ring('Visible fight floor cropped at r=16m',16,28,-.25,.05,sand)
ring('Court terrace 01',28,34,0,1.5,step)
ring('Court terrace 02',34,40,0,3,step)
ring('C3 wall',40,42,0,5.7,orange)
ring('Painted wall frieze',40,42,5.7,6,edge)
for j in range(-7,8):
    a=math.radians(3*j)
    box('Set-in wall rib',40.08*math.cos(a),40.08*math.sin(a),4.4,.18,.24,2.78,trim,a)
    box('Reinforced rib head',40.05*math.cos(a),40.05*math.sin(a),5.65,.16,.63,.21,grey,a)


def wedge(n,x0,x1,z0,z1):
    v=[(x,y,z) for y in (-2,2) for x,z in ((x0,z0),(x1,z0),(x1,z1))]
    return mesh(n,v,[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)],step)


wedge('Archived first diagonal ramp',23,28,0,1.5)
wedge('Archived second diagonal ramp',29,34,1.5,3)
# Sparse lane markings are surface art, never a path or movement annotation.
for y in (-2.45,2.45):
    for x in (23,24.1,25.2,26.3,27.4):
        box('Ramp edge stripe',x,y,.052,.51,.072,.004,chalk,bevel=0)

# Local +X is the radial diagonal into the office. Three.js local +Z becomes
# negative section Y. Office remains square in original world X/Z.
box('Office, exact 10 m mass',r_office,0,4,10,10,8,grey,-turn,.054)
box('Office, exact 11 m roof cap',r_office,0,8.25,11,11,.50,orange,-turn,.062)
box('Archived balcony slab',r_deck,0,6.25,7,5,.50,orange)
box('Painted balcony fascia',r_start-.008,0,6.25,.019,4.88,.31,edge)
for x in (r_start+.18,r_deck-1.75,r_deck,r_deck+1.75,r_deck+3.3):
    box('Single side guard post',x,-2.4,7.05,.12,.20,1.10,rail)
box('Single side guard upper',r_deck,-2.4,7.56,7,.20,.08,rail)
box('Single side guard lower',r_deck,-2.4,6.90,7,.12,.07,trim)
# Paired lengths of cosmetic fascia framing; neither crosses the rim nor
# extends beneath the deck into the +3 m terrace.
for y in (-1.68,1.68):
    box('Recessed balcony seam',r_deck-.72,y,6.04,4.9,.16,.08,trim)
for side in (-1,1):
    # Dark factory stripes under the cap, inset from the outer corners.
    a=side*turn
    normal=Vector((-math.cos(a),-math.sin(a),0))
    p=Vector((r_office,0,7.92))+normal*5.037
    box('Office upper accent',*p,.068,8.7,.061,edge,a)

# Decorative windows placed on the two court-facing chamfer edges of the
# square office. Surface dressing only; no opening and no actor marker.
for side in (-1,1):
    a=side*turn
    normal=Vector((-math.cos(a),-math.sin(a),0))
    tangent=Vector((-normal.y,normal.x,0))
    for along in (-2.7,0,2.7):
        p=Vector((r_office,0,7.23))+normal*5.017+tangent*along
        box('Office glazing frame',*p,.12,1.50,.94,trim,a)
        p+=normal*.071
        box('Office glazing',*p,.046,1.28,.70,light,a)
        for off in (-.4,0,.4):
            pos=p+tangent*off+normal*.028
            box('Office glazing mullion',*pos,.024,.037,.701,grey,a)

parts=list(sc.objects)
path=out/'c3-office-sector.glb'
export(parts,path)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tris=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
assert not any(k in d for k in ('images','animations','skins','cameras'))
assert 37.50 < r_start < 37.52 and 42 < math.hypot(30,30) < r_deck+3.5
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(path))
assert any(o.type=='MESH' for o in sc.objects)

world=bpy.data.worlds.new('East afternoon')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.29,.43,.66,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.43
sc.world=world


def lamp(name,kind,xyz,focus,power,color,size):
    d=bpy.data.lights.new(name,kind)
    d.energy,d.color=power,color
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(name,d)
    sc.collection.objects.link(o)
    o.location=xyz
    o.rotation_euler=(Vector(focus)-o.location).to_track_quat('-Z','Y').to_euler()


lamp('Raking late sun','SUN',(18,-10,21),(43,2,1),2.6,(1,.78,.59),.10)
lamp('Cold sky fill','AREA',(31,11,13),(42,0,5),3300,(.65,.79,1),14)
cam=bpy.data.objects.new('C3 review camera',bpy.data.cameras.new('C3 review camera'))
sc.collection.objects.link(cam)
sc.camera=cam
sc.render.engine='CYCLES'
sc.cycles.samples=54
sc.cycles.use_denoising=False
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=91
sc.view_settings.view_transform='AgX'


def render(name, xyz, target, dims, lens, ortho=False):
    cam.location=xyz
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO' if ortho else 'PERSP'
    if ortho:cam.data.ortho_scale=lens
    else:cam.data.lens=lens
    sc.render.resolution_x,sc.render.resolution_y=dims
    sc.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)


render('eye', (20,-4.7,1.75),(39,0,4.1),(1260,800),42)
render('sector', (19,-27,24),(39,0,3.8),(1260,800),38,True)
report={
  'scope':'Static C3 office and partial wall/terrace sector, not a full court or encounter',
  'archive':'Raynos/project-wildshard-singleplayer@ce1cf050b3 art/showcase-template/round-5-blockout',
  'layout_sha':'5d019a020361c47187ec889f2bc947f82cd9f98a',
  'lab_sha':'51a3b4bef1f2d4891172164d10893d98d450a3b9',
  'map_court_xz':[146,186],
  'axes':{'description':'glTF +X radial 45deg toward office, +Z maps tangent near rail',
          'sector_half_deg':24,'floor_cut_r_m':16},
  'court':{'floor_y_m':.05,'floor_outer_r_m':28,'terrace_radius_m':[28,34,40],
           'terrace_top_m':[1.5,3],'wall_r_m':[40,42],'wall_top_m':6,
           'in_axis_ramp_runs_m':[[23,28],[29,34]],'ramp_width_m':4},
  'deck':{'map_center_xz':[175,157],'center_r_m':r_deck,'rims_r_m':[r_start,r_deck+3.5],
          'size_m':[7,5,.5],'bottom_top_m':[6,6.5],'inner_edge_to_fight_floor_m':r_start-28,
          'vertical_drop_to_terrace_m':3.5,'guard_local_section_y_m':-2.4},
  'office':{'map_bounds_xz':[176,186,146,156],'wall_top_m':8,'roof_top_m':8.5,
            'sector_centerline_first_corner_r_m':math.hypot(30,30)},
  'eye_height_above_floor_m':1.7, 'asset':{'bytes':len(raw),'triangles':tris,
       'sha256':hashlib.sha256(raw).hexdigest()},
  'illustrative':'Office glazing, material breaks, wall ribs and partial floor markings'}
(out/'c3-office-sector.json').write_text(json.dumps(report,indent=2)+'\n')

# A true centerline section of archived massing, independent of perspective.
# It follows the original ramps; the side rail is outside this cut.
def sx(r): return 62+(r-20)*29
def sy(z): return 385-z*29
def trace(xz): return ' '.join(f'{sx(x):.2f},{sy(z):.2f}' for x,z in xz)
def shape(xz, fill):
    return f'<polygon points="{trace(xz)}" fill="{fill}" stroke="#8f9aa4" stroke-width="1.2"/>'
def line(x,y,end_x,end_y,color='#cdb081',dash=''):
    return (f'<line x1="{sx(x):.2f}" y1="{sy(y):.2f}" x2="{sx(end_x):.2f}" '
            f'y2="{sy(end_y):.2f}" stroke="{color}" stroke-width="1.4" stroke-dasharray="{dash}"/>')
def label(x,y,caption,color='#f3ece0',size=17):
    return (f'<text x="{sx(x):.2f}" y="{sy(y):.2f}" fill="{color}" '
            f'font-family="sans-serif" font-size="{size}">{caption}</text>')

parts_svg=[
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 470" role="img" aria-label="C3 radial section showing the ramps, wall, balcony and office">',
    '<rect width="1180" height="470" fill="#182128"/>',
    '<text x="62" y="51" font-family="sans-serif" font-size="28" font-weight="bold" fill="#f7ebdc">C3 / FOREMAN OFFICE SECTION</text>',
    '<text x="62" y="78" font-family="sans-serif" font-size="15" fill="#bfccd5">Round 5 diagonal through the two ramps, wall and office. Radius starts at court center.</text>',
    shape([(20,0),(28,0),(28,.05),(20,.05)],'#77553a'),
    shape([(28,0),(34,0),(34,1.5),(28,1.5)],'#69747b'),
    shape([(34,0),(40,0),(40,3),(34,3)],'#79838a'),
    shape([(23,0),(28,0),(28,1.5)],'#9b8c77'),
    shape([(29,1.5),(34,1.5),(34,3)],'#9b8c77'),
    shape([(40,0),(42,0),(42,6),(40,6)],'#a74b23'),
    shape([(math.hypot(30,30),0),(math.hypot(40,40),0),
           (math.hypot(40,40),8),(math.hypot(30,30),8)],'#455765'),
    shape([(r_office-11/math.sqrt(2),8),(r_office+11/math.sqrt(2),8),
           (r_office+11/math.sqrt(2),8.5),(r_office-11/math.sqrt(2),8.5)],'#b44f25'),
    shape([(r_start,6),(r_deck+3.5,6),(r_deck+3.5,6.5),(r_start,6.5)],'#d4783a'),
    line(20,0,57.4,0),
    line(r_start,6.5,r_start,3,'#e7bc79','4 5'),
    line(28,0,28,-1.17),line(r_start,3,r_start,-1.17),
    line(28,-1.0,r_start,-1.0),
    label(28.8,-1.74,'9.51 m to the fight floor radius','#f2c98c',15),
    label(20.05,.39,'Fight floor +0.05 m'),
    label(28.7,1.87,'+1.5 m'),
    label(34.2,3.33,'+3 m'),
    label(34.15,6.85,'Deck top +6.5 m','#f2c98c'),
    label(43.3,8.83,'Office roof +8.5 m','#f2c98c'),
    label(35.9,4.38,'3.5 m','#f2c98c',15),
    label(20,-2.36,'Cut only · side guard is out of plane · dotted line is a vertical reference, not a movement path','#bfccd5',14),
    '</svg>']
(out/'c3-office-section.svg').write_text('\n'.join(parts_svg)+'\n')
