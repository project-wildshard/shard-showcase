"""Build the WSC-SCENE-008 optional interior sky shell. Blender + stdlib only."""
from array import array
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector


def field(x, y, z):
    """Fixed lattice and cubic interpolation; no per-process noise seed."""
    k = tuple(map(math.floor, (x, y, z)))
    r = [v-a for v,a in zip((x,y,z),k)]
    u,v,w = [t*t*(3-2*t) for t in r]

    def corner(i,j,k):
        n = ((i*374761393) ^ (j*668265263) ^ (k*1274126177)) & 0xffffffff
        n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
        return ((n ^ (n >> 16)) / 0xffffffff) * 2 - 1

    return sum(corner(k[0]+a,k[1]+b,k[2]+c)
               * (u if a else 1-u) * (v if b else 1-v) * (w if c else 1-w)
               for a in (0,1) for b in (0,1) for c in (0,1))


out = Path(sys.argv[sys.argv.index("--") + 1])
out.mkdir(parents=True, exist_ok=True)
# Blender coordinates; the writer converts them to glTF's X, up-Y, south-Z.
azimuths, bands = 128, 24
radius, top, datum = 114.0, 70.0, -22.0
points, colors, indices = [], [], []
for j in range(bands):
    elev = (math.pi / 2) * j / bands
    for i in range(azimuths):
        t = 2 * math.pi * i / azimuths
        d = Vector((math.cos(t) * math.cos(elev), math.sin(t) * math.cos(elev), math.sin(elev)))
        points.append((radius*d.x, radius*d.y, datum+(top-datum)*d.z))
        # Hand-set storm gradient with low-frequency cloud bands. The north
        # horizon is cool steel; a muted slate violet shelf wraps the south.
        h = d.z
        sky = tuple(a*(1-h)+b*h for a,b in zip((.097,.148,.208),(.011,.026,.052)))
        # Coherent noise in direction space is continuous across the wrap seam.
        broad = field(d.x*4.7+4,d.y*4.7-1,d.z*13.9+2)
        wisps = field(d.x*9.1-4,d.y*9.1+8,d.z*33+5)
        ribbon = math.exp(-((h-(.22+.055*math.sin(2*t)))/.14)**2)
        cloud = max(0,min(.67,(broad*.8 + wisps*.2 + .32)*ribbon))
        glow = .031*(.5+.5*d.y)*math.exp(-((h-.09)/.13)**2)
        c = tuple(s*(1-cloud)+v*cloud+glow*k for s,v,k in zip(sky,(.159,.203,.266),(.60,.88,1)))
        colors.append((*c,1.0))
points.append((0,0,top))
colors.append((.011,.026,.052,1))
pole=len(points)-1
for j in range(bands-1):
    for i in range(azimuths):
        a=j*azimuths+i
        b=j*azimuths+(i+1)%azimuths
        c,d=b+azimuths,a+azimuths
        indices.extend((a,c,b,a,d,c))
for i in range(azimuths):
    a=(bands-1)*azimuths+i
    b=(bands-1)*azimuths+(i+1)%azimuths
    indices.extend((a,pole,b))

p=[(x,z,-y) for x,y,z in points]
chunks=[array("f",(v for row in p for v in row)).tobytes(),
        array("f",(v for row in colors for v in row)).tobytes(),
        array("H",indices).tobytes()]
offsets=[0,len(chunks[0]),len(chunks[0])+len(chunks[1])]
blob=b"".join(chunks)
blob+=b"\0"*((-len(blob))%4)
glb={
    "asset":{"version":"2.0","generator":"Wildshard Titan interior sky"},
    "extensionsUsed":["KHR_materials_unlit"],"extensionsRequired":["KHR_materials_unlit"],
    "scene":0,"scenes":[{"nodes":[0]}],
    "nodes":[{"name":"E12h · North storm shelf","mesh":0}],
    "meshes":[{"primitives":[{"attributes":{"POSITION":0,"COLOR_0":1},"indices":2,"material":0}]}],
    "materials":[{"name":"Interior sky | unlit vertex palette","pbrMetallicRoughness":{"baseColorFactor":[1,1,1,1]},"extensions":{"KHR_materials_unlit":{}}}],
    "buffers":[{"byteLength":len(blob)}],
    "bufferViews":[{"buffer":0,"byteOffset":o,"byteLength":len(c),"target":t} for o,c,t in zip(offsets,chunks,(34962,34962,34963))],
    "accessors":[{"bufferView":0,"componentType":5126,"count":len(p),"type":"VEC3",
                  "min":[min(v) for v in zip(*p)],"max":[max(v) for v in zip(*p)]},
                 {"bufferView":1,"componentType":5126,"count":len(colors),"type":"VEC4"},
                 {"bufferView":2,"componentType":5123,"count":len(indices),"type":"SCALAR"}],
}
assert sys.byteorder=="little" and len(points)<65536
header=json.dumps(glb,separators=(",",":"),ensure_ascii=False).encode()
header+=b" "*((-len(header))%4)
(out/"e12h-titan-interior-sky.glb").write_bytes(struct.pack("<4sIIII",b"glTF",2,28+len(header)+len(blob),len(header),0x4e4f534a)+header+struct.pack("<II",len(blob),0x004e4942)+blob)
