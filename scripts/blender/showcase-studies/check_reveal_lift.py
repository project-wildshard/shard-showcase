"""Verify +4 m translation clearance from the actual two static GLB buffers."""
import json
import math
import struct
import sys
from pathlib import Path

out=Path(sys.argv[1])


def triangles(part,title,expected,budget):
    blob=(out/f"wsc-kit-009-reveal-lift-{part}.glb").read_bytes()
    assert struct.unpack_from("<4sII",blob)==(b"glTF",2,len(blob))
    n=struct.unpack_from("<I",blob,12)[0]
    doc=json.loads(blob[20:20+n])
    assert doc["nodes"]==[{"mesh":0,"name":title}]
    assert not any(k in doc for k in ("animations","skins","images"))
    def array(i):
        a=doc["accessors"][i]
        v=doc["bufferViews"][a["bufferView"]]
        off=28+n+v.get("byteOffset",0)+a.get("byteOffset",0)
        fmt={5123:"<H",5125:"<I",5126:"<fff"}[a["componentType"]]
        return [struct.unpack_from(fmt,blob,off+j*v.get("byteStride",struct.calcsize(fmt)))
                for j in range(a["count"])]
    ts=[]
    for p in doc["meshes"][0]["primitives"]:
        points=array(p["attributes"]["POSITION"])
        idx=[i for i, in array(p["indices"])]
        ts.extend(tuple(points[i] for i in idx[j:j+3]) for j in range(0,len(idx),3))
    assert len(ts)==expected and len(blob)<budget
    print(f"{part}: {len(blob):,} bytes, {len(ts):,} triangles; identity pivot")
    return ts


frame=triangles("frame","C2_Lift_Fixed_Frame",2144,125_000)
deck=triangles("deck","C2_Lift_Moving_Deck",1584,93_000)
vs=[p for t in deck for p in t]
for axis in (0,2):
    assert min(p[axis] for p in vs)==-3 and max(p[axis] for p in vs)==3
assert max(p[1] for p in vs)==max(p[1] for t in frame for p in t)==0
# Outside the central sleeve, each triangle is beyond one side of the deck's
# aperture. The sleeve is below the thick platform; only the narrow shaft
# can reach it during upward travel. Check those two separations independently.
def side(t):
    return max(min(sign*p[axis] for p in t) for sign in (-1,1) for axis in (0,2))

sleeve=[t for t in frame if max(abs(p[a]) for p in t for a in (0,2))<1.1]
assert len(sleeve)==176
outer=[t for t in frame if t not in sleeve]
gap=min(map(side,outer))
assert math.isclose(gap,3.06,abs_tol=.00002)
shaft_zone=max(p[1] for t in sleeve for p in t)
assert shaft_zone<-.66
rad=max(abs(p[a]) for t in deck if min(p[1] for p in t)<=shaft_zone for p in t for a in (0,2))
shaft_gap=min(map(side,sleeve))-rad
assert shaft_gap>.055
print(f"Shaft-to-sleeve clearance: {shaft_gap:.3f} m")
for pose in (0,2,4):
    assert max(p[1]+pose for p in vs)==pose
print(f"6 m square deck; flush and +4 m top; {gap-3:.3f} m min separation across full vertical art stroke.")
