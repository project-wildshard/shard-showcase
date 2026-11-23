"""Export the three W5c static rail models; optionally render the reimported GLBs."""
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT = output_directory()
BASE = "wsc-plan-009-grind-rail"
# Blender coordinates, in metres. Only the flat length is specified by W5c.
# Ramp crest and bowl lip heights reference the west-hover static assembly.
VARIANTS = {
    "flat": ([(-6, 0, .72), (6, 0, .72)], [(0, .11), (0, .50), (0, .89)]),
    "down": ([(-5.1, 0, 2.08), (5.1, 0, .74)], [(0, .10), (0, .51), (0, .90)]),
    "kink": ([(-4.8, -1.45, 3.74), (0, -1.45, 2.68), (4.5, .90, .82)],
             [(0, .12), (0, .71), (1, .24), (1, .84)]),
}


def finish(name, hex_color, roughness, metallic=0):
    def lin(v):
        return v / 12.92 if v < .04045 else ((v + .055) / 1.055) ** 2.4
    color = tuple(lin((hex_color >> shift & 255) / 255) for shift in (16, 8, 0)) + (1,)
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


class Mesh:
    def __init__(self):
        self.verts, self.faces, self.materials = [], [], []

    def add(self, verts, faces, mat):
        offset = len(self.verts)
        self.verts.extend(verts)
        self.faces.extend(tuple(offset + i for i in f) for f in faces)
        self.materials.extend([mat] * len(faces))

    def sweep(self, points, radii, mat, sides=12, wear=None):
        points = list(map(Vector, points))
        dirs = [(b-a).normalized() for a,b in zip(points, points[1:])]
        tangents = [dirs[0]] + [(a+b).normalized() for a,b in zip(dirs,dirs[1:])] + [dirs[-1]]
        rings = []
        for p,t,rad in zip(points,tangents,radii):
            horizontal = Vector((0,0,1)).cross(t)
            if horizontal.length < .001:
                horizontal = Vector((1,0,0))
            horizontal.normalize()
            up = t.cross(horizontal)
            rings.extend(p+rad*(horizontal*math.cos(a*math.tau/sides)+up*math.sin(a*math.tau/sides))
                         for a in range(sides))
        self.add(rings, [tuple(reversed(range(sides))),
                         tuple(range(len(rings)-sides,len(rings)))],mat)
        base = len(self.verts)-len(rings)
        for row in range(len(points)-1):
            for i in range(sides):
                j = (i+1)%sides
                a = base + row*sides
                self.faces.append((a+i,a+j,a+sides+j,a+sides+i))
                self.materials.append(wear if wear and i in (1,2,3,4) else mat)

    def footing(self, p,w,d,z,mat):
        # Beveled octagonal plates with true flat bottoms at the local datum.
        x,y = p[:2]
        r=.065
        ring=[(-w+r,-d),(w-r,-d),(w,-d+r),(w,d-r),
              (w-r,d),(-w+r,d),(-w,d-r),(-w,-d+r)]
        verts=[(x+u*s,y+v*s,h) for s,h in ((1,z),(1,z+.052),(.93,z+.073)) for u,v in ring]
        self.add(verts,[tuple(reversed(range(8))),tuple(range(16,24))] +
                 [(i+a,j+a,j+a+8,i+a+8) for a in (0,8) for i in range(8) for j in [(i+1)%8]],mat)

    def object(self,name):
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.verts,[],self.faces)
        mats=list(dict.fromkeys(self.materials))
        for m in mats:data.materials.append(m)
        for f,m in zip(data.polygons,self.materials):
            f.material_index=mats.index(m)
            assert f.area > 1e-8, (name,f.index)
        obj=bpy.data.objects.new(name,data)
        bpy.context.collection.objects.link(obj)
        return obj


clear_scene()
pipe=finish("Blue black forged steel",0x26393c,.39,.71)
wear=finish("Exposed crown wear",0x949d98,.30,.76)
foot=finish("Carbon mounting plates",0x343e3c,.65,.49)
brace=finish("Copper oxide orange sleeve",0xba692e,.47,.55)
lug=finish("Galvanized hardware",0x9d9c87,.41,.63)
end=finish("Unlit turquoise end plugs",0x358784,.48,.55)

for variant,(path,stations) in VARIANTS.items():
    clear_scene()
    cap, frame = Mesh(), Mesh()
    ps=list(map(Vector,path))
    start=(ps[1]-ps[0]).normalized()
    finish_dir=(ps[-1]-ps[-2]).normalized()
    # Taper the ends without adding length. A continuous bisector section avoids a gap at the kink.
    cap.sweep([ps[0],ps[0]+start*.048,*ps[1:-1],ps[-1]-finish_dir*.048,ps[-1]],
              [.065,.105]+[.105]*(len(ps)-2)+[.105,.065],pipe,14,wear)
    for p,d in ((ps[0],start),(ps[-1],-finish_dir)):
        cap.sweep([p+d*.002,p+d*.038],[.068,.093],end,14)
    for seg,t in stations:
        p=ps[seg].lerp(ps[seg+1],t)
        x,y,z=p
        top=(x,y,z-.080)
        frame.footing((x,y),.37,.255,0,foot)
        frame.sweep([(x,y,.068),(x,y,.25),(x,y,z*.64),top],[.121,.102,.094,.080],pipe,10)
        frame.sweep([(x,y,.090),(x,y,.168),(x,y,.212)],[.130,.121,.103],brace,10)
        frame.sweep([(x-.245,y,.083),(x-.105,y,z*.49),(x,y,z*.55)],[.042,.037,.037],pipe,8)
        for dx in (-.25,.25):
            for dy in (-.145,.145):
                q=(x+dx,y+dy)
                frame.sweep([(*q,.056),(*q,.089),(*q,.097)],[.052,.052,.039],lug,6)
    cap.object("Continuous_grind_surface")
    frame.object("Mounts_and_supports")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(OUT/f"{BASE}-{variant}.glb"),export_format="GLB",
        use_selection=True,export_texcoords=False,export_animations=False)

if os.getenv("WSC_RAIL_RENDER") == "1":
    clear_scene()
    # Spread the three local-origin models on timbers in a single studio frame.
    for variant,d in zip(VARIANTS,(-4.7,0,5.0)):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT/f"{BASE}-{variant}.glb"))
        for o in set(bpy.context.scene.objects)-before:
            if o.parent is None:o.location.y += d
    floor=finish("Warm studio concrete",0x67665c,.84)
    marker=finish("Dull studio inlay",0x8c8574,.83)
    for name,location,dims,mat in [
        ("Studio floor",(0,0,-.11),(200,200,.20),floor),
        *[(f"Studio divider {y}",(0,y,-.004),(15,.022,.016),marker) for y in (-7.6,-2.5,2.4,8)]
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        o=bpy.context.object;o.name=name;o.dimensions=dims;o.data.materials.append(mat)
    s=bpy.context.scene
    s.world.color=(.30,.30,.30)
    def aim(o, p):
        o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for pos,power,sz,color in [
        ((-6,-8,13),4700,9,(1,.88,.72)),
        ((8,-2,10),3100,8,(.72,.85,1)),
        ((0,11,9),3800,9,(1,.78,.57)),
    ]:
        bpy.ops.object.light_add(type="AREA",location=pos)
        o=bpy.context.object;o.data.energy=power;o.data.size=sz;o.data.color=color
        aim(o,(0,0,1.2))
    bpy.ops.object.camera_add(location=(8.6,-18,19))
    s.camera=bpy.context.object;aim(s.camera,(0,.4,1.4))
    s.camera.data.type="ORTHO";s.camera.data.ortho_scale=18.8
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1040;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(OUT/"west-grind-rail-family-reimport.jpg")
    bpy.ops.render.render(write_still=True)
