"""WSC-KIT-005. Stage the reimported R02 hardware without repackaging the donor meshes."""
import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

ROOT = Path(__file__).resolve().parents[3]
OUT = output_directory()
clear_scene()
S = bpy.context.scene
SOURCE = ROOT / "public/assets/wildshard-art"
RNG = random.Random(105)
ASSETS = {
    "ring": ("WSC-PROP-043", "wsc-prop-043-riding-ring.glb"),
    "gantry": ("WSC-MODULE-010", "wsc-module-010-riding-start-gantry.glb"),
    "timer": ("WSC-PROP-042", "wsc-prop-042-riding-timer-display.glb"),
    "jump": ("WSC-PROP-080", "w10b-reusable-riding-jump-wip.glb"),
    "fence": ("WSC-MODULE-011", "wsc-module-011-riding-fence.glb"),
    "conifer": ("WSC-PROP-046", "wsc-prop-046-conifer-tree.glb"),
    "oak": ("WSC-PROP-012", "wsc-prop-012-deciduous-tree.glb"),
}
MODELS = {}
for key, (asset_id, name) in ASSETS.items():
    path = SOURCE / name
    before = set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    loaded = sorted(set(S.objects) - before, key=lambda x: x.name)
    meshes = [(o.name, o.data, o.matrix_world.copy()) for o in loaded if o.type == "MESH"]
    points = [m @ v.co for _, mesh, m in meshes for v in mesh.vertices]
    bounds = [[round(fn(v[i] for v in points), 5) for i in range(3)] for fn in (min, max)]
    asset = dict(id=asset_id, path=str(path.relative_to(ROOT)), bounds_blender_m=bounds,
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if key == "ring":
        center = .5 * (bounds[0][2] + bounds[1][2])
        inner = 2 * min(math.hypot(v.x, v.z - center) for v in points)
        assert abs(center - 1.562) < 1e-6 and abs(inner - 2.636) < 1e-5
    MODELS[key] = (meshes, asset)
    for o in loaded:
        bpy.data.objects.remove(o, do_unlink=True)

def place(key, name, xyz, yaw=0., scale=1.):
    transform = Matrix.Translation(xyz) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Scale(scale, 4)
    for original, mesh, transform_source in MODELS[key][0]:
        o = bpy.data.objects.new(f"{name} | {original}", mesh)
        S.collection.objects.link(o)
        o.matrix_world = transform @ transform_source

def surface(name, light, dark, scale, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    n, k = mat.node_tree.nodes, mat.node_tree.links
    p = n.get('Principled BSDF')
    p.inputs['Roughness'].default_value = roughness
    t = n.new('ShaderNodeTexCoord')
    mix = n.new('ShaderNodeTexNoise')
    mix.inputs['Scale'].default_value = scale
    k.new(t.outputs['Object'], mix.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .23
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = .74
    ramp.color_ramp.elements[1].color = (*light, 1)
    k.new(mix.outputs['Fac'], ramp.inputs[0])
    k.new(ramp.outputs[0], p.inputs['Base Color'])
    grit = n.new('ShaderNodeTexNoise')
    grit.inputs['Scale'].default_value = 30
    k.new(t.outputs['Object'], grit.inputs['Vector'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .21
    bump.inputs['Distance'].default_value = .045
    k.new(grit.outputs['Fac'], bump.inputs['Height'])
    k.new(bump.outputs['Normal'], p.inputs['Normal'])
    return mat

def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    data.materials.append(mat)
    o = bpy.data.objects.new(name, data)
    S.collection.objects.link(o)
    return o

CX, CY, HALF, RADIUS, WIDTH = -122, 186, 60, 38, 12
LAP = 4 * HALF + 2 * math.pi * RADIUS
def course(s, radius=RADIUS):
    s %= LAP
    h = math.pi * RADIUS
    if s < 2 * HALF: return CX - HALF + s, CY - radius, 0.
    s -= 2 * HALF
    if s < h:
        angle = -math.pi / 2 + s / RADIUS
        return CX + HALF + radius * math.cos(angle), CY + radius * math.sin(angle), angle + math.pi / 2
    s -= h
    if s < 2 * HALF: return CX + HALF - s, CY + radius, math.pi
    angle = math.pi / 2 + (s - 2 * HALF) / RADIUS
    return CX - HALF + radius * math.cos(angle), CY + radius * math.sin(angle), angle + math.pi / 2

def strip(name, inner, outer, z, mat):
    n = 256
    verts = [(x, y, z) for i in range(n) for r in (inner, outer)
             for x, y, _ in [course(i * LAP / n, r)]]
    return mesh(name, verts, [(2*i, 2*i+1, 2*((i+1)%n)+1, 2*((i+1)%n)) for i in range(n)], mat)

grass = surface('Meadow | proof setting', (.157, .201, .075), (.028, .063, .026), .39, .83)
sand = surface('Oval | packed clay', (.41, .267, .111), (.207, .110, .049), .79, .72)
shoulder = surface('Oval | worn shoulder', (.31, .224, .115), (.112, .104, .049), .55, .76)
wheel = surface('Oval | worn riding line', (.44, .300, .124), (.273, .171, .073), .91, .67)
mesh("Meadow ground", [(-670,-180,0),(380,-180,0),(380,610,0),(-670,610,0)], [(0,1,2,3)], grass)
strip("Oval shoulder", 30.7, 45.3, .009, shoulder)
strip("R02 true 12 m riding ribbon", 32, 44, .025, sand)
strip("Wear line", 37.0, 39.0, .028, wheel)
# Repeated linked fence sources, fixed mesh width; no duplicate geometry or new export.
for side in (31.45, 44.55):
    n = round((4 * HALF + 2 * math.pi * side) / 3.138)
    for i in range(n):
        x, y, yaw = course(i * LAP/n, side)
        if y < 160 and abs(x + 80) < 3.2:  # Clear the start-frame feet.
            continue
        place('fence', 'Rail', (x, y, .02), yaw)
# R02 has four inferred end slots. Keep their y values and snap x to the
# actual centreline; assign each ring plane perpendicular to travel.
old_rings = [(-145,148),(-105,148),(-28,169),(-28,203),(-100,224),(-145,224),(-216,203),(-216,169)]
jump_xy = [(-165,148),(-125,148),(-110,224),(-160,224)]
scale = 4.56 / inner
center_height = 3.4
ring_records = []
for index, (x, y) in enumerate(old_rings, 1):
    angle = math.pi / 2 if y == 148 else -math.pi / 2
    old_x = x
    if y not in (148,224):
        side = 1 if x > CX else -1
        arc_x = math.sqrt(RADIUS**2 - (y-CY)**2) * side
        x = CX + HALF * side + arc_x
        angle = math.atan2(y-CY, arc_x) + math.pi
    ring_z = center_height - center * scale
    place('ring', f'R{index:02}', (x,y,ring_z), angle, scale)
    ring_records.append(dict(number=index, r02_xy_blender_m=[old_x,y],
                             origin_blender_m=[round(x,5),y,round(ring_z,5)], yaw_deg=round(math.degrees(angle)%360,5)))
for x, y in jump_xy:
    place('jump', 'R02 jump', (x,y,.025), math.pi/2 if y == 148 else -math.pi/2)
# Keep the R02 gantry anchor. Turn the timer's face toward the camera approach.
# The front plane is offset 0.71 m from the gantry frame; this is an art-fit proposal.
place('gantry','Start finish',(-80,148,.025),-math.pi/2)
place('timer','Static display',(-80.71,148,5.25),-math.pi/2)
# Distant dressing is not exported, and nothing is added to the inner track.
for i in range(100):
    x = -255 + i*2.9 + RNG.uniform(-1,1)
    y = 237 + RNG.uniform(2,31)
    place('conifer','Forest backdrop',(x,y,0),RNG.uniform(0,math.tau),RNG.uniform(.64,2.1))
for i in range(114):
    x = RNG.uniform(-13,63)
    y = RNG.uniform(111,246)
    place('conifer','Forest east edge',(x,y,0),RNG.uniform(0,math.tau),RNG.uniform(.55,1.82))
for i in range(34):
    x = -235 + RNG.uniform(0,235)
    y = RNG.choice([RNG.uniform(110,137), RNG.uniform(164,211)])
    if -176 < x < -72 or y < 137:
        place('oak','Meadow grove',(x,y,0),RNG.uniform(0,math.tau),RNG.uniform(.69,1.48))

# A low distant ridge is art framing only; the crown follows the eastern
# woodland outside the route instead of crossing any checkpoint.
ridge = surface('Background | wooded shoulder', (.074,.123,.062), (.029,.076,.046), .082, .92)
verts = []
for i in range(126):
    y = -500 + i * 9.6
    h = 21.0 + 8.8*math.sin(.021*y) + 3.5*math.sin(.056*y) + 2*math.sin(.12*y)
    verts.extend([(93,y,0), (152,y,h), (206,y,.12*h)])
mesh('East ridge | studio backdrop',verts,
     [(3*i+j,3*(i+1)+j,3*(i+1)+j+1,3*i+j+1) for i in range(125) for j in (0,1)],ridge)

views = {
    "mounted-height": dict(eye=[-118.5,148.0,2.6], target=[-74,148,3.89], lens=36),
    "first-gate": dict(eye=[-91.8,141.6,4.9], target=[-80,148.0,4.25], lens=37),
    "course-overview": dict(eye=[-122,186,180], target=[-122,186,0], ortho=230),
}
report = {
    "catalogue_id": "WSC-KIT-005",
    "scope": "Art-only reimport and instance placement. No horse, gate clearance, gameplay, deployment or runtime certification.",
    "coordinates": "Blender metres (X, Y, Z); world glTF (X, Z, -Y).",
    "reference": {"art": "scripts/blender/west-scene-r02/assemble.py and finish.py",
                  "historical_layout_commit": "ce1cf050b3",
                  "historical_layout": "art/showcase-template/round-5-blockout/lab.js"},
    "oval": {"center_blender_xy_m": [CX,CY], "outer_size_m": [208,88], "centreline_m": round(LAP,3),
             "half_straight_m": HALF, "centerline_radius_m": RADIUS, "track_width_m": WIDTH},
    "donor_meshes": {k: v[1] for k,v in MODELS.items()},
    "rings": {"count": len(ring_records), "unscaled_clear_opening_m": round(inner,3),
              "candidate_clear_opening_m": 4.56, "uniform_scale": round(scale,6),
              "ring_center_z_m": center_height, "outer_arc_bottom_m": round(ring_z,3),
              "clear_opening_bottom_m": round(center_height-4.56/2,3),
              "lower_arc": "Full ring retained, suspended in the visual comparison; no collision assigned.",
              "checkpoint_pad_requirement_m": 4, "checkpoint_pad_status": "Separate requirement, not modeled.",
              "placements": ring_records},
    "jumps": {"count": len(jump_xy), "r02_wip_blender_xy_m": jump_xy, "rail_width_m": 4.1,
              "donor_full_width_m": 4.75, "historic_proxy_width_m": 10},
    "timer": {"gantry_blender_xy_m": [-80,148], "timer_blender_xyz_m": [-80.71,148,5.25],
              "status": "Static readability placement; not timed."},
    "camera": views,
}
assert len(ring_records) == 8 and len(jump_xy) == 4 and 478.7 < LAP < 478.8
(OUT/'w10b-riding-course-study.json').write_text(json.dumps(report, indent=2) + '\n')
def diagram():
    # Render the authoritative study points, not a screenshot with guessed positions.
    def pos(x,y): return 95 + (x + 228)*4.7, 55 + (230 - y)*4.7
    def p1(x,y): return ','.join(f'{q:.1f}' for q in pos(x,y))
    trace=' '.join(p1(*course(LAP*i/256)[:2]) for i in range(256))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 550" role="img" aria-labelledby="title desc">',
         '<title id="title">Riding course placement study</title>',
         '<desc id="desc">Top view, eight teal checkpoint rings, four gold jumps, and the start gantry.</desc>',
         '<rect width="1200" height="550" rx="18" fill="#142525"/>',
         f'<polygon points="{trace}" fill="#213933" stroke="#77634b" stroke-width="56"/>',
         f'<polygon points="{trace}" fill="none" stroke="#e1cc92" stroke-opacity=".52" stroke-width="1.3" stroke-dasharray="5 8"/>']
    for r in ring_records:
        x,y,_=r['origin_blender_m']
        px,py=pos(x,y)
        svg += [f'<circle cx="{px:.1f}" cy="{py:.1f}" r="16" fill="#87e0d2" stroke="#144d49" stroke-width="2"/>',
                f'<text x="{px:.1f}" y="{py+5:.1f}" fill="#102e30" text-anchor="middle">{r["number"]}</text>']
    for n,(x,y) in enumerate(jump_xy,1):
        px,py=pos(x,y)
        svg += [f'<rect x="{px-4:.1f}" y="{py-15:.1f}" width="8" height="30" rx="2" fill="#f5bc63"/>',
                f'<text x="{px+10:.1f}" y="{py+5:.1f}" fill="#fff4d8">J{n}</text>']
    px,py=pos(-80,148)
    svg += [f'<rect x="{px-4:.1f}" y="{py-30:.1f}" width="8" height="60" fill="#f38e60"/>',
            f'<text x="{px+12:.1f}" y="{py-14:.1f}" fill="#ffbd98">START / FINISH</text>',
            '<text x="36" y="508" fill="#f2e8d4" font-size="26">WEST OVAL / PLACEMENT STUDY</text>',
            '<text x="36" y="531" fill="#c4d2ca" font-size="14">Teal = visual checkpoint ring · gold = existing jump · dots = centreline · no gameplay triggers</text>']
    svg.insert(3,'<style>text{font: bold 14px system-ui,sans-serif}text[font-size="26"]{font-size:26px}</style>')
    return '\n'.join(svg+['</svg>',''])
(OUT/'nov23-riding-route.svg').write_text(diagram())
if os.environ.get('WSC_METADATA_ONLY') == '1':
    sys.exit(0)

S.world = bpy.data.worlds.new('Riding oval late sun')
S.world.use_nodes = True
n = S.world.node_tree.nodes
bg = n.get('Background')
sky = n.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_rotation = 1.8
sky.sun_elevation = .40
sky.sun_intensity = .66
sky.dust_density = 1.2
S.world.node_tree.links.new(sky.outputs['Color'], bg.inputs[0])
bg.inputs[1].default_value = .20
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(42),math.radians(-27),math.radians(27)))
bpy.context.object.data.energy = 1.25
bpy.context.object.data.angle = .10
bpy.context.object.data.color = (1,.85,.65)
S.view_settings.exposure = -.59
S.render.engine = 'CYCLES'
S.cycles.samples = 44
S.cycles.use_denoising = False
S.cycles.use_adaptive_sampling = True
S.cycles.adaptive_threshold = .095
S.render.resolution_x, S.render.resolution_y = 1400, 820
S.render.resolution_percentage = 100
S.render.image_settings.file_format = 'JPEG'
S.render.image_settings.quality = 88
if lap_review := os.environ.get("WSC_RIDING_LAP_RAIL_REVIEW"):
    import runpy
    helpers=Path(__file__).resolve().parents[3]/"demos/native-riding-lap-rails/review.py"
    runpy.run_path(str(helpers))["review"](lap_review)
    sys.exit(0)
if rail_review := os.environ.get("WSC_RIDING_RAIL_REVIEW"):
    import runpy
    helpers=Path(__file__).resolve().parents[3]/"demos/native-riding-rail/review.py"
    runpy.run_path(str(helpers))["review"](rail_review)
    sys.exit(0)
for name, v in views.items():
    bpy.ops.object.camera_add(location=v['eye'])
    c = bpy.context.object
    c.rotation_euler = (Vector(v['target'])-c.location).to_track_quat('-Z', 'Y').to_euler() if 'ortho' not in v else (0,0,0)
    c.data.clip_end = 950
    if 'ortho' in v:
        c.data.type = 'ORTHO'
        c.data.ortho_scale = v['ortho']
    else:
        c.data.lens = v['lens']
    S.camera = c
    S.render.filepath = str(OUT/f'nov23-riding-{name}.jpg')
    bpy.ops.render.render(write_still=True)
