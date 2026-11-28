"""Check a runtime GLB without requiring Blender."""
import json
import math
from pathlib import Path
import struct
import sys

path=Path(sys.argv[1])
b=path.read_bytes()
magic,version,total=struct.unpack_from("<4sII",b)
assert (magic,version,total)==(b"glTF",2,len(b))
n,kind=struct.unpack_from("<II",b,12); assert kind==0x4E4F534A
g=json.loads(b[20:20+n]); data=20+n+8
nodes=g["nodes"]; names={o.get("name"):i for i,o in enumerate(nodes)}
for name in ("grip","gate_L","gate_R","grip_socket","tip_socket"):
    assert name in names,name
assert names["grip_socket"] in nodes[names["grip"]]["children"]
assert names["tip_socket"] in nodes[names["grip"]]["children"]
assert max(map(abs,nodes[names["grip_socket"]].get("translation",[0,0,0])))<1e-6
assert not g.get("cameras") and not g.get("images")
assert all("Studio" not in (node.get("name") or "") for node in nodes)
def values(i,components):
    a=g["accessors"][i];v=g["bufferViews"][a["bufferView"]]
    assert a["componentType"]==5126
    off=data+v.get("byteOffset",0)+a.get("byteOffset",0)
    return [struct.unpack_from("<"+"f"*components,b,off+j*v.get("byteStride",4*components)) for j in range(a["count"])]
anim={}
for a in g["animations"]:
    moves={}
    for c in a["channels"]:
        t=c["target"]
        if t["path"]!="rotation":continue
        node=nodes[t["node"]]["name"]; s=a["samplers"][c["sampler"]]
        ts=values(s["input"],1); qs=values(s["output"],4)
        assert len(ts)==len(qs) and all(math.isfinite(x) for q in qs for x in q)
        span=max(2*math.acos(min(1,abs(sum(a*b for a,b in zip(qs[0],q))))) for q in qs)
        moves[node]=round(math.degrees(span),3)
        duration=ts[-1][0]-ts[0][0]
    assert moves["gate_L"]>8 and moves["gate_R"]>8
    anim[a["name"]]={"seconds":round(duration,3),"rotation_degrees":moves}
assert set(anim)=={"Signal_Release","Arc_Cut"}
assert anim["Arc_Cut"]["rotation_degrees"]["grip"]>40
tri=sum(g["accessors"][p["indices"]]["count"]//3 for m in g["meshes"] for p in m["primitives"])
assert 0<tri<8000
print(json.dumps({"asset":"WSC-WPN-014","triangles":tri,"glb_bytes":len(b),"rig":["grip","gate_L","gate_R"],"clips":anim,"sockets":["grip_socket","tip_socket"]},indent=2))
