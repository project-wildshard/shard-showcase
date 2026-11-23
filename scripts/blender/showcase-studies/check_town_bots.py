"""Check the two exact W1a exports, including real animation key and skin buffers."""
import json
import math
import struct
import sys
from pathlib import Path

ORDER = """hips spine chest neck head clavicleR shoulderR twistR elbowR handR
clavicleL shoulderL twistL elbowL handL thighR shinR footR thighL shinL footL""".split()
PARENT = [-1, 0, 1, 2, 3, 2, 5, 6, 7, 8, 2, 10, 11, 12, 13, 0, 15, 16, 0, 18, 19]
SHAPES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
FORMATS = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}


def check(path, target_triangles):
    blob=path.read_bytes()
    assert struct.unpack_from("<4sII",blob)==(b"glTF",2,len(blob))
    size=struct.unpack_from("<I",blob,12)[0]
    doc=json.loads(blob[20:20+size])
    base=28+size

    def values(which):
        a=doc["accessors"][which]
        v=doc["bufferViews"][a["bufferView"]]
        pos=base+v.get("byteOffset",0)+a.get("byteOffset",0)
        fmt="<"+FORMATS[a["componentType"]]*SHAPES[a["type"]]
        stride=v.get("byteStride",struct.calcsize(fmt))
        return [struct.unpack_from(fmt,blob,pos+i*stride) for i in range(a["count"])]

    assert len(doc["meshes"])==len(doc["skins"])==len(doc["materials"])==1
    joints=doc["skins"][0]["joints"]
    nodes=doc["nodes"]
    assert [nodes[j]["name"] for j in joints]==ORDER
    assert len(values(doc["skins"][0]["inverseBindMatrices"]))==21
    assert all(joints[c] in nodes[joints[p]]["children"] for c,p in enumerate(PARENT) if p>=0)
    mesh_node,=[n for n in nodes if "mesh" in n]
    assert mesh_node["skin"]==0 and not ({"matrix","translation","rotation","scale"} & mesh_node.keys())
    p,=doc["meshes"][0]["primitives"]
    a=p["attributes"]
    pos,uv,joints0,weights=[values(a[k]) for k in ("POSITION","TEXCOORD_0","JOINTS_0","WEIGHTS_0")]
    assert len(pos)==len(uv)==len(joints0)==len(weights)
    assert min(v[1] for v in pos)==0 and 1.805<max(v[1] for v in pos)<1.806
    assert len({(round(u,3),round(v,3)) for u,v in uv})>=12
    assert all(all(0<=i<21 for i in v) for v in joints0)
    assert all(all(0<=w<=1 for w in v) and math.isclose(sum(v),1,abs_tol=1e-5) for v in weights)
    assert len({j for js,ws in zip(joints0,weights) for j,w in zip(js,ws) if w>0})>=15
    idx=doc["accessors"][p["indices"]]["count"]
    assert idx==target_triangles*3 and len(blob)<450_000
    clip,=doc["animations"]
    active=set()
    for c in clip["channels"]:
        s=clip["samplers"][c["sampler"]]
        times=[t for t, in values(s["input"])]
        samples=values(s["output"])
        assert all(b>a for a,b in zip(times,times[1:]))
        assert math.isclose(times[-1]-times[0],3,abs_tol=2e-5)
        assert all(abs(x-y)<1e-5 for x,y in zip(samples[0],samples[-1]))
        if c["target"]["path"]=="rotation" and any(math.dist(x,samples[0])>.005 for x in samples):
            active.add(nodes[c["target"]["node"]]["name"])
    assert active=={"chest","head","elbowR","elbowL"},active
    look={}
    for img in doc["images"]:
        view=doc["bufferViews"][img["bufferView"]]
        at=base+view.get("byteOffset",0)
        look[img["name"]]=blob[at:at+view["byteLength"]]
    assert set(look)=={"w1a-albedo","w1a-signal"}
    print(f"{path.name}: {len(blob):,} B, {idx//3:,} triangles; one skinned mesh, 21 ordered joints, 3 s idle")
    return look


directory=Path(sys.argv[1])
assert (check(directory/"wsc-plan-001-stable-hand.glb",3396)==
        check(directory/"wsc-plan-002-weapons-keeper.glb",3512)), "Shared palette did not match"
