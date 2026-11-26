"""Author two independently placeable, non-colliding WSC-FX Band 3 cues."""
import hashlib
import json
from math import cos,sin,tau
from pathlib import Path
import struct
import sys

import bpy

O=Path(sys.argv[sys.argv.index('--')+1])
O.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene
S.render.fps=60
for o in tuple(S.objects):bpy.data.objects.remove(o,do_unlink=True)

def flat(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    n=m.node_tree.nodes
    n.clear()
    image=n.new('ShaderNodeEmission')
    image.inputs['Color'].default_value=(*rgb,1)
    m.node_tree.links.new(image.outputs[0],n.new('ShaderNodeOutputMaterial').inputs['Surface'])
    return m
yellow=flat('Plumb | amber warning',(.98,.37,.045))
ivory=flat('Plumb | warm core',(1,.79,.31))
dark=flat('Plumb | iron outline',(.085,.037,.019))
burn=flat('Plumb | dark amber',(.55,.14,.022))

class Mesh:
    def __init__(self,materials):
        self.vertices,self.faces,self.slots=[],[],[]
        self.materials=materials

    def append(self,vertices,faces,slot):
        k=len(self.vertices)
        self.vertices.extend(vertices);self.faces.extend(tuple(k+i for i in row) for row in faces)
        self.slots.extend([slot]*len(faces))

    def strip(self,coords,slot,z=0):
        self.append([(x,y,z) for x,y in coords],[(0,1,2,3)],slot)

    def frustum(self,a,b,r,r2,slot,n=6):
        self.append([(x,radius*cos(tau*i/n),radius*sin(tau*i/n))
          for x,radius in ((a,r),(b,r2)) for i in range(n)],
          [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],slot)

    def save(self,stem,clip,small,fold):
        d=bpy.data.meshes.new(stem)
        d.from_pydata(self.vertices,[],self.faces)
        for m in self.materials:d.materials.append(m)
        for p,i in zip(d.polygons,self.slots):p.material_index=i
        d.update();d.calc_loop_triangles()
        o=bpy.data.objects.new(stem,d);S.collection.objects.link(o)
        o.shape_key_add(name='Basis')
        key=o.shape_key_add(name='Collapse at end')
        for v,p in zip(key.data,self.vertices):v.co=fold(*p)
        # Clamp a glTF mixer action to this 700 ms end if not removing it immediately.
        # The locked cue widens smoothly; a one-tick fold removes it at the end.
        for f,w in ((0,1-small),(14,1-small),(26,.15),(35,0),(41,0),(42,1)):
            key.value=w;key.keyframe_insert('value',frame=f)
        act=d.shape_keys.animation_data.action;act.name=clip
        for fc in act.fcurves:
            for p in fc.keyframe_points:p.interpolation='LINEAR'
        S.frame_set(0)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        f=O/(stem+'.glb')
        bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,
            export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=False)
        raw=f.read_bytes()
        size=struct.unpack_from('<I',raw,12)[0]
        g=json.loads(raw[20:20+size])
        # Blender writes pure Emission as lit PBR. These are display colors, not lamps.
        # Preserve the authored RGB in glTF's portable unlit form.
        g.setdefault('extensionsUsed',[]).append('KHR_materials_unlit')
        for material in g['materials']:
            color=material.pop('emissiveFactor')
            material['pbrMetallicRoughness']={'baseColorFactor':[*color,1]}
            material['extensions']={'KHR_materials_unlit':{}}
        content=json.dumps(g,separators=(',',':')).encode()
        content+=b' '*(-len(content)%4)
        remaining=raw[20+size:]
        raw=struct.pack('<4sIII4s',b'glTF',2,20+len(content)+len(remaining),len(content),b'JSON')+content+remaining
        f.write_bytes(raw)
        assert len(g['meshes'])==len(g['animations'])==1 and not g.get('images')
        assert g['animations'][0]['name']==clip
        p=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
            triangles=len(d.loop_triangles),primitives=len(g['meshes'][0]['primitives']))
        bpy.data.objects.remove(o,do_unlink=True)
        return p

# Exactly 1 m long; scale +X by segment length, preserving world widths.
# Broken casing nodes help distinguish the warning from an always-on sight or rail.
beam=Mesh([ivory,yellow,burn])
beam.frustum(0,1,.035,.035,0)
for i in (0,2,4,6,8,10,12):
    x=i/13
    end=min(1,x+.025)
    beam.frustum(x,end,.061,.050,1)
    beam.frustum(end,min(1,end+.012),.050,.039,2)
p=beam.save('e3-plumb-beam','Plumb beam - 700ms',.54,lambda x,y,z:(x,0,0))

# Ground part has a dark halo under the amber lane edges. Two nested caps stop short of
# the existing screen and make direction visible in grayscale. No fill obscures floor details.
lane=Mesh([dark,yellow,ivory])
for sign in (-1,1):
    for i in range(8):
        x=.07+i*.103
        def quad(a,b,near,far,skew):
            return [(a,sign*near),(b,sign*near),(b+skew,sign*far),(a+skew,sign*far)]
        lane.strip(quad(x,x+.050,.435,.615,.012),0)
        lane.strip(quad(x+.004,x+.046,.475,.579,.010),1,.00125)
for x in (.77,.86,.95):
    for sign in (-1,1):
        lane.strip([(x-.020,0),(x,0),(x-.033,sign*.28),(x-.053,sign*.28)],0)
        lane.strip([(x-.016,0),(x-.005,0),(x-.037,sign*.23),(x-.048,sign*.23)],2,.00125)
# Keep exact x endpoints while including two small end caps, not an oversized filled disk.
for a,b in ((0,.014),(.986,1)):
    lane.strip([(a,-.30),(b,-.30),(b,.30),(a,.30)],0)
    lane.strip([(a+.002,-.257),(b-.002,-.257),(b-.002,.257),(a+.002,.257)],1,.00125)
q=lane.save('e3-plumb-lane','Plumb lane - 700ms',.82,lambda x,y,z:(x,0,z))
proof=dict(duration_s=.7,frequency_hz=60,root_axis='local +X',version='optional 0.7 s warning art only',
    beam=p,lane=q,lane_floor_bias_m=.006,beam_max_radius_m=.061,lane_max_width_m=1.23,
    no_combat_or_runtime=True)
(O/'plumb-export.json').write_text(json.dumps(proof,indent=2)+'\n')
