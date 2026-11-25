"""Fit existing West wall lanterns and validate proposed lamp aims. No game edits."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

parser=argparse.ArgumentParser(__doc__)
parser.add_argument("town",type=Path)
parser.add_argument("out",type=Path)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
args.out.mkdir(parents=True,exist_ok=True)
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
pins={"wall-lantern.glb":"bdbdce040eee6e60693e110cdcdb25e1abc93d80ed4f79f7d2e72fc5490ecc09",
      "w0b-town-gate-nameplates.glb":"2daf80f5fa5f5bcdf22aeec26d2113a72d36250c864064fdb403d9a50718e480"}
parity=json.loads((args.town.parent/"parity.json").read_text())
assert parity["matched_signature"]==["e6bbb20e18adbc863c18fd637211e6c8a35ae4a01deed667d071f4850dce7b4f",2692]
for n,h in pins.items():
    assert hashlib.sha256((assets/n).read_bytes()).hexdigest()==h,n
bpy.ops.wm.open_mainfile(filepath=str(args.town.resolve()))
s=bpy.context.scene

def load(n):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/n))
    bpy.context.view_layer.update()
    return sorted(set(s.objects)-before,key=lambda o:o.name)

def vertices(o,T=Matrix.Identity(4)):
    return [T@o.matrix_world@v.co for v in o.data.vertices]

def bounds(vs):
    return [(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]

def tree(obs,inv):
    vs=[];ps=[]
    for o in obs:
        b=len(vs);vs.extend(vertices(o,inv))
        ps.extend(tuple(b+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,ps)

def aim(o,q):
    o.rotation_euler=(Vector(q)-o.location).to_track_quat("-Z","Y").to_euler()

def light(name,kind,loc,target,watts,color):
    d=bpy.data.lights.new(name,kind)
    d.energy=watts;d.color=color
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
    o.location=loc;aim(o,target)
    return o

def as_three(v):
    return [round(v[0],4),round(v[2],4),round(-v[1],4)]

original=tuple(s.objects)
for old in original:
    if old.type=="LIGHT":
        old.hide_render=True
signs=load("w0b-town-gate-nameplates.glb")
proof={}
shots=[]
extra=[]
for label,x,y,yaw,prefix,beam_name in [
    ("Stable",-36,60,0,"New Stable Gate stone pier","Stable Gate sign board"),
    ("West",-128,0,math.pi/2,"ZIP | West Gate pier","ZIP | West Gate beam"),
]:
    G=Matrix.Translation((x,y,0))@Matrix.Rotation(yaw,4,"Z")
    Inv=G.inverted()
    piers=sorted([o for o in original if o.type=="MESH" and o.name.startswith(prefix)],key=lambda o:(Inv@o.matrix_world.translation).x)
    assert len(piers)==2
    beam=s.objects[beam_name]
    beam_box=bounds(vertices(beam,Inv))
    sign=next(o for o in signs if o.name==label+" Gate")
    sign.matrix_world=G@Matrix.Translation((0,beam_box[1][0]-.03,sum(beam_box[2])*.5))
    extra.extend([sign,*sign.children_recursive])
    if label=="Stable":
        for n in ("Stable Gate sign inset","Stable Gate clear lettering"):
            s.objects[n].hide_render=True
    scene_fit=tree([*piers,beam],Inv)
    placements=[]
    omissions=[]
    for idx,pier in enumerate(piers):
        p_box=bounds(vertices(pier,Inv))
        x0=sum(p_box[0])*.5; front=p_box[1][0]
        z0=2.95
        seat=tree([pier],Inv)
        # Hit the actual unmodified pier plane on the rectangular oak bracket footprint.
        for dx in (-.092,0,.092):
            for dz in (.23,.43,.63,.81):
                hit,n,*_=seat.ray_cast(Vector((x0+dx,front-.14,z0+dz)),Vector((0,1,0)),.23)
                assert hit is not None and n.y<-.999 and abs(hit.y-front)<.0002,(label,pier.name,hit)
        objs=load("wall-lantern.glb")
        mesh,=[o for o in objs if o.type=="MESH"]
        for o in objs:
            if o.parent not in objs:o.matrix_world=G@Matrix.Translation((x0,front+.001,z0))@o.matrix_world
        bpy.context.view_layer.update()
        b=bounds(vertices(mesh,Inv))
        assert (b[0][0]>6.50 if idx else b[0][1]<-6.50)
        assert abs(b[1][1]-front-.001)<.0001
        # Reject neighboring map objects, not just the candidate pier.
        close=[]
        for o in original:
            if o.type!="MESH" or o==pier:continue
            a=bounds([Inv@o.matrix_world@Vector(v) for v in o.bound_box])
            if all(a[j][0]<=b[j][1]+.005 and a[j][1]>=b[j][0]-.005 for j in range(3)):
                close.append(o)
        body_tree=tree([mesh],Inv)
        clashes=[o.name for o in close if body_tree.overlap(tree([o],Inv))]
        if label=="Stable" and idx==0:
            assert any("LOT 18" in n for n in clashes),(label,clashes)
            omissions.append({"pier":pier.name,"reason":"Approach lantern intersects adjacent Lot 18 facade","clashes":clashes})
            for o in objs:o.hide_render=True
            continue
        assert not clashes,(label,clashes)
        obj_material=next(m for m in mesh.data.materials if "emissive glass" in m.name)
        # Tune only the review instance's glass, not the source material.
        glass=obj_material.copy()
        i=list(mesh.data.materials).index(obj_material)
        mesh.data.materials[i]=glass
        bs=glass.node_tree.nodes.get("Principled BSDF")
        glass_verts={u for p in mesh.data.polygons if p.material_index==i for u in p.vertices}
        glocal=[Inv@mesh.matrix_world@mesh.data.vertices[v].co for v in glass_verts]
        gl=bounds(glocal)
        origin=Vector((x0,sum(gl[1])*.5-.04,b[2][0]-.045))
        target=Vector((x0*.76,-3.20,.07))
        ray=target-origin
        for d in (scene_fit,body_tree):
            assert d.ray_cast(origin,ray.normalized(),ray.length)[0] is None,(label,idx)
        lamp=light(label+" downlight "+str(idx+1),"SPOT",G@origin,G@target,205,(1,.61,.29))
        lamp.data.spot_size=math.radians(62);lamp.data.spot_blend=.74;lamp.data.shadow_soft_size=.15
        placements.append(dict(pier=pier.name,mount_three_xyz_m=as_three(G@Vector((x0,front+.001,z0))),
            light_three_xyz_m=as_three(G@origin),aim_three_xyz_m=as_three(G@target),
            bracket_contact_rays=12,clear_center_beam_m=round(ray.length,4)))
        extra.extend(objs)
        shots.append((label,lamp,bs))
    proof[label]=dict(gate_three_xz_m=[x,-y],yaw_deg=round(math.degrees(yaw),4),
        donor_outside_corridor_m=round(abs(x0)-.16036-6,4),lanterns=placements,omissions=omissions)

# Remove the unused signs just from this temporary render, not any saved scene.
for o in signs:
    if o not in extra:o.hide_render=True
receipt={"scope":"Exact art fit and scene-light witness; no native emitters or clock",
         "parity_signature":parity["matched_signature"],"pinned_donors":pins,"gates":proof,
         "fixture":{"type":"spot","watts_preview":205,"full_cone_degrees":62,"blend":.74}}
(args.out/"w11a-gate-lanterns-proof.json").write_text(json.dumps(receipt,indent=2)+"\n")
scene_light=bpy.data.worlds.new("W11a evening")
s.world=scene_light;s.world.use_nodes=True
ns=s.world.node_tree.nodes
ns["Background"].inputs["Color"].default_value=(.25,.38,.67,1)
ns["Background"].inputs["Strength"].default_value=.14
rim=light("Blue hour rim","SUN",(-78,-25,100),(-65,35,0),.34,(.49,.64,1))
rim.data.angle=.18
cd=bpy.data.cameras.new("Town gate eye")
cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam
s.render.engine="CYCLES"
s.cycles.samples=26;s.cycles.use_denoising=False;s.cycles.adaptive_threshold=.072
s.view_settings.view_transform="AgX"
s.view_settings.look="AgX - Medium High Contrast"
s.render.resolution_x=1370;s.render.resolution_y=850;s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
cd.lens=30
for label,x,y,yaw in [("Stable",-36,60,0),("West",-128,0,math.pi/2)]:
    G=Matrix.Translation((x,y,0))@Matrix.Rotation(yaw,4,"Z")
    cam.location=G@Vector((.6,-17.2,1.7))
    aim(cam,G@Vector((0,2.85,3.30)))
    for mode in (("off","on") if label=="Stable" else ("on",)):
        for key,l,b in shots:
            l.hide_render=key!=label or mode=="off"
            b.inputs["Emission Strength"].default_value=1.8 if not l.hide_render else 0
        s.render.filepath=str(args.out/f"nov25-w11a-{label.lower()}-lanterns-{mode}.png")
        bpy.ops.render.render(write_still=True)
