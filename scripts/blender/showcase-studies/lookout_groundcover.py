"""W9b native-scale bearberry and rock-edge heather. Rebuild with Blender 4.3+."""
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

OUT = output_directory()
rng = random.Random(463921)
TAU = math.tau
clear_scene()


def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = .87
    return m


greens = [material("Bearberry | " + n, c) for n, c in [
    ("evergreen", (.046, .119, .047)), ("sage", (.122, .207, .079)),
    ("backlit edge", (.232, .315, .102)), ("stem", (.185, .188, .051)), ("berry", (.285,.012,.014))
]]
shrubs = [material("Heather | " + n, c) for n, c in [
    ("needle", (.083, .127, .057)), ("new shoot", (.164, .213, .093)),
    ("wine", (.306, .055, .122)), ("mauve bud", (.58, .181, .279)),
    ("old wood", (.118, .073, .053))
]]


class Builder:
    def __init__(self):
        self.v, self.f, self.mat = [], [], []

    def patch(self, vertices, faces, mat):
        i = len(self.v)
        self.v.extend(vertices)
        self.f.extend(tuple(i+j for j in face) for face in faces)
        self.mat.extend([mat] * len(faces))

    def twig(self, a, b, r0, r1, mat):
        d = (b-a).normalized()
        u = d.cross(Vector((0, 1, 0))).normalized()
        if u.length < .01:
            u = d.cross(Vector((1, 0, 0))).normalized()
        v = d.cross(u)
        ring = [u*math.cos(q*TAU/3)+v*math.sin(q*TAU/3) for q in range(3)]
        self.patch([a+r0*w for w in ring]+[b+r1*w for w in ring],
                   [(i, (i+1)%3, (i+1)%3+3, i+3) for i in range(3)], mat)

    def leaf(self, a, b, width, mat, oval=False):
        side = (b-a).cross(Vector((0, 0, 1))).normalized()
        mid = a.lerp(b, .47)
        if oval:
            rim = [a, a.lerp(b,.29)+side*width*.84, a.lerp(b,.68)+side*width,
                   b, a.lerp(b,.66)-side*width, a.lerp(b,.29)-side*width*.84]
            self.patch(rim+[mid+Vector((0,0,width*.35))],
                       [(i,(i+1)%6,6) for i in range(6)], mat)
            return
        self.patch([a, mid+side*width, b, mid-side*width, mid+Vector((0,0,width*.28))],
                   [(0,1,4), (1,2,4), (2,3,4), (3,0,4)], mat)

    def bud(self, p, r, mat, rounded=False):
        if rounded:
            rings = [p+Vector((math.cos(i*TAU/6)*r*f,math.sin(i*TAU/6)*r*f,r*z))
                     for f,z in ((.67,-.68),(1,.04),(.76,.66)) for i in range(6)]
            self.patch(rings, [(k+i,k+(i+1)%6,k+(i+1)%6+6,k+i+6) for k in (0,6) for i in range(6)]
                       + [tuple(reversed(range(6))), tuple(range(12,18))], mat)
            return
        vecs = [Vector(q)*r for q in ((1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,-.7),(0,0,1.3))]
        self.patch([p+d for d in vecs], [(i,(i+1)%4,5) for i in range(4)]
                   + [((i+1)%4,i,4) for i in range(4)], mat)

    def object(self, name, materials):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.v, [], self.f)
        mesh.update()
        assert not mesh.validate() and all(p.area > 1e-9 for p in mesh.polygons)
        for m in materials:
            mesh.materials.append(m)
        for p, n in zip(mesh.polygons, self.mat):
            p.material_index = n
        ob = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(ob)
        return ob


def bearberry(near):
    b = Builder()
    for i in range(9):
        a = TAU*i/9 + rng.uniform(-.18,.18)
        radius = rng.uniform(.37,.58)
        h = rng.uniform(.20,.31)
        d = Vector((math.cos(a),math.sin(a),0))
        side = Vector((-math.sin(a),math.cos(a),0))
        start = d*.035
        joint = d*radius*.38+Vector((0,0,h*.42))
        tip = d*radius+Vector((0,0,h*.8))
        b.twig(start,joint,.008,.006,3)
        b.twig(joint,tip,.006,.002,3)
        for j in range(0,7):
            if not near and j in (0,1,3,5):
                continue
            t = j/6
            p = joint.lerp(tip,t)
            q = p + side*(-1)**j*(.11-.035*t)+d*.056+Vector((0,0,.054))
            b.leaf(p,q,(.046 if near else .064)*(.78+.22*t), 1 if (i+j)%5 else 0, near)
            if j in (2,4) and i%3!=0:
                b.bud(p+d*.025+Vector((0,0,.050)),.023 if near else .026,4,near)
        b.leaf(tip,tip+d*.078+Vector((0,0,.065)),.032,1)
    return b.object("Rock lookout trailing bearberry", greens)


def heather(near):
    b = Builder()
    for i in range(13):
        a = TAU*i/13*1.618
        r = rng.uniform(.18,.47)
        h = rng.uniform(.17,.38)
        d = Vector((math.cos(a), math.sin(a), 0))
        start = d*r*.13
        knee = d*r*.70 + Vector((0,0,h*.40))
        tip = d*r + Vector((0,0,h))
        b.twig(start, knee, .009, .005, 4)
        for j in range(1, 5 if near else 3):
            t = j/(5 if near else 3)
            p = start.lerp(knee,t)
            e = Vector((math.cos(a+j*2.4),math.sin(a+j*2.4),.51))
            b.leaf(p,p+e*.12,.017 if near else .026,j%2)
        b.twig(knee, tip, .005, .002, 4)
        for j in range(1, 6):
            if not near and j in (1,3,5):
                continue
            t = j/6
            p = knee.lerp(tip,t)
            side = Vector((math.cos(a+j*2.4),math.sin(a+j*2.4),.6))
            q = p+side*(.087-.039*t)
            b.leaf(p, q, .014 if near else .028, (i+j)%2)
            if j >= 2:
                b.bud(q+Vector((0,0,.010)), (.012 if near else .018)*(1+.26*t), 2+(i+j)%2, near and j%2==0)
                if near and j%2==1:
                    b.bud(q+side*.020,.01,3)
        b.bud(tip, .018 if near else .025, 3)
    return b.object("Rock lookout heather", shrubs)


near = []
for name, make in (("bearberry", bearberry), ("heather", heather)):
    for close in (True, False):
        rng.seed(463921 if name == "bearberry" else 463922)
        ob = make(close)
        suffix = "" if close else "-far"
        mesh = ob.data
        mesh.calc_loop_triangles()
        n = len(mesh.loop_triangles)
        limits = [(min(v.co[i] for v in mesh.vertices), max(v.co[i] for v in mesh.vertices)) for i in range(3)]
        assert limits[2][0] >= -.02 and .20 < limits[2][1] < .50
        dest = OUT/f"w9b-lookout-{name}{suffix}.glb"
        export([ob], dest)
        print(name, suffix or "near", n, limits, dest.stat().st_size, flush=True)
        if close:
            near.append(ob)
        else:
            bpy.data.objects.remove(ob, do_unlink=True)

# Private studio renders use repeat instances on a hillside patch; not a new runtime placement.
stone = material("Shale", (.123,.111,.102))
dirt = material("Alpine soil", (.085,.057,.027))
s = bpy.context.scene
s.render.engine = "CYCLES"
s.cycles.samples = 42
s.cycles.use_denoising = False
s.render.resolution_x, s.render.resolution_y = 1250, 790
s.render.resolution_percentage = 100
s.render.image_settings.file_format = "JPEG"
s.render.image_settings.quality = 92
s.world.color = (.10,.10,.10)
s.view_settings.view_transform = "AgX"
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.017))
bpy.context.object.data.materials.append(dirt)
nt = dirt.node_tree
tex = nt.nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 19
tex.inputs["Detail"].default_value = 4
tex.inputs["Roughness"].default_value = .74
coord = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(coord.outputs["Object"],tex.inputs["Vector"])
grain = nt.nodes.new("ShaderNodeTexNoise")
grain.inputs["Scale"].default_value = 157
nt.links.new(coord.outputs["Object"],grain.inputs["Vector"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .32
bump.inputs["Distance"].default_value = .027
nt.links.new(grain.outputs["Fac"],bump.inputs["Height"])
bs = nt.nodes.get("Principled BSDF")
nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (.033,.022,.012,1)
ramp.color_ramp.elements[1].color = (.18,.122,.066,1)
nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
for i in range(52):
    a = rng.uniform(0,TAU)
    x, y = rng.uniform(-4,4), rng.uniform(-2,4)
    if abs(x)<.57 and abs(y)<.49:
        continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(x,y,.005))
    o = bpy.context.object
    z = rng.uniform(.055,.265)
    o.scale = (z*1.7,z*.96,z*.45)
    o.rotation_euler.z = a
    o.data.materials.append(stone)
for name, loc, energy, size, col in [
    ("Late sun", (-4,-2,5), 1300, 2.7, (1,.86,.64)),
    ("Cool rim", (3,2,4), 680, 4.0, (.68,.78,1))
]:
    bpy.ops.object.light_add(type="AREA", location=loc)
    o=bpy.context.object
    o.name, o.data.energy, o.data.shape, o.data.size, o.data.color = name,energy,"DISK",size,col
    o.rotation_euler=(-o.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(1.32,-2.35,1.28))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.19))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.lens = 48
s.camera = cam
for ob, other, name in ((near[0],near[1],"bearberry"),(near[1],near[0],"heather")):
    other.hide_render=True
    repeats=[]
    for j,(x,y) in enumerate([(-1.1,.38),(.65,.66),(-.53,.73),(.13,1.13),(1.39,1.27),(-.35,.23),(.31,.26),(-.86,.45),(.65,.13)]):
        o=ob.copy()
        bpy.context.collection.objects.link(o)
        o.location=(x,y,0)
        o.rotation_euler.z=.71*j+.32
        o.scale=(.62+.08*j,)*3
        repeats.append(o)
    s.render.filepath=str(OUT/f"{name}.jpg")
    bpy.ops.render.render(write_still=True)
    for o in repeats:
        bpy.data.objects.remove(o, do_unlink=True)
    other.hide_render=False
