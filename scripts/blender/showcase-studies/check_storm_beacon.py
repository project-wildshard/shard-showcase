"""Check exact tower/lamp GLBs, including clear shared mount space."""
import json
import math
import struct
import sys
from pathlib import Path

TOWER="wsc-kit-007-storm-beacon.glb"
LAMP="wsc-kit-007-storm-beacon-charged-lamp.glb"


def read(path, names, triangles, max_bytes):
    blob=path.read_bytes()
    assert struct.unpack_from("<4sII",blob)==(b"glTF",2,len(blob))
    section=struct.unpack_from("<I",blob,12)[0]
    d=json.loads(blob[20:20+section])
    assert not any(k in d for k in ("images","skins","animations"))
    assert {n["name"] for n in d["nodes"]}==set(names)
    assert all(set(n)=={"name","mesh"} for n in d["nodes"])
    def parse(i):
        a=d["accessors"][i]
        v=d["bufferViews"][a["bufferView"]]
        offset=28+section+v.get("byteOffset",0)+a.get("byteOffset",0)
        fmt={5123:"<H",5125:"<I",5126:"<fff"}[a["componentType"]]
        stride=v.get("byteStride",struct.calcsize(fmt))
        return [struct.unpack_from(fmt,blob,offset+j*stride) for j in range(a["count"])]
    ts=[]
    vs=[]
    for m in d["meshes"]:
        for p in m["primitives"]:
            pos=parse(p["attributes"]["POSITION"])
            iv=[i for i, in parse(p["indices"])]
            assert not len(iv)%3
            vs.extend(pos)
            ts.extend(tuple(pos[i] for i in iv[j:j+3]) for j in range(0,len(iv),3))
    assert len(ts)==triangles and len(blob)<max_bytes
    print(f"{path.name}: {len(blob):,} bytes, {len(ts):,} triangles; identity pivot")
    lit={m["name"]:m.get("extensions",{}).get("KHR_materials_emissive_strength",{}).get("emissiveStrength")
         for m in d["materials"] if m.get("emissiveFactor")}
    return vs,ts,lit


def clearance(points):
    # Distance from center to the XZ projection, handling vertical triangles.
    points=[(x,z) for x,_,z in points]
    edges=list(zip(points,points[1:]+points[:1]))
    signs=[x1*z2-z1*x2 for (x1,z1),(x2,z2) in edges]
    if (min(signs)>1e-8 or max(signs)<-1e-8):
        return 0
    result=[]
    for (x,z),(xx,zz) in edges:
        dx,dz=xx-x,zz-z
        square=dx*dx+dz*dz
        t=max(0,min(1,-(x*dx+z*dz)/square)) if square>1e-12 else 0
        result.append(math.hypot(x+t*dx,z+t*dz))
    return min(result)


out=Path(sys.argv[1])
tower,ts,light=read(out/TOWER,["Beacon_Body_and_Socket","Beacon_Cage_and_Hardware"],5164,250_000)
lamp,_,strength=read(out/LAMP,["Beacon_Charged_Lamp_Insert"],260,17_000)
assert not light and set(strength)=={"Charged opal","Bright tungsten"} and min(strength.values())>=4
assert min(y for _,y,_ in tower)==0 and 5.46<max(y for _,y,_ in tower)<5.47
assert 4.669<min(y for _,y,_ in lamp)<4.671 and 5.24<max(y for _,y,_ in lamp)<5.25
rad=max(math.hypot(x,z) for x,_,z in lamp)
gap=min(clearance(t) for t in ts if max(y for _,y,_ in t)>4.671)
assert gap>rad+.055,(gap,rad)
print(f"Shared mount: {gap-rad:.3f} m conservative radial clearance above lamp seat; unlit tower has no emission")
