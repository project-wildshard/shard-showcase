"""Validate sockets, clip timings, silhouette uniqueness and budget."""
import argparse, json, math, struct
from pathlib import Path

cli=argparse.ArgumentParser()
cli.add_argument("directory",type=Path)
p=cli.parse_args().directory
results=[];bounds=set()
for f in sorted(p.glob("*.glb")):
    b=f.read_bytes()
    assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    n,k=struct.unpack_from("<II",b,12)
    assert k==0x4e4f534a
    g=json.loads(b[20:20+n]); start=20+n+8
    def read(i,components):
        a=g["accessors"][i];v=g["bufferViews"][a["bufferView"]]
        assert a["componentType"]==5126
        off=start+v.get("byteOffset",0)+a.get("byteOffset",0)
        return [struct.unpack_from("<"+"f"*components,b,off+j*v.get("byteStride",4*components)) for j in range(a["count"])]
    nodes=g["nodes"]
    ns={v["name"]:v for v in nodes}
    assert {"grip","head","grip_socket","tip_socket"}<=ns.keys()
    assert nodes[ns["grip"]["children"][-1]]  # nonempty hierarchy
    assert max(map(abs,ns["grip_socket"].get("translation",[0,0,0])))<.00001
    assert not g.get("cameras") and not g.get("images")
    clips={}
    for clip in g["animations"]:
        moved=set(); d=0
        for ch in clip["channels"]:
            t=ch["target"]; sa=clip["samplers"][ch["sampler"]]
            times=read(sa["input"],1); d=max(d,times[-1][0]-times[0][0])
            k={'rotation':4,'translation':3,'scale':3}[t["path"]]
            v=read(sa["output"],k)
            assert len(v)==len(times)
            assert all(math.isfinite(x) for row in v for x in row)
            if any(max(abs(q-r) for q,r in zip(v[0],row))>.01 for row in v[1:]):
                moved.add(nodes[t["node"]]["name"])
        assert {"grip","head"}<=moved and d>.6
        clips[clip["name"]]=round(d,3)
    assert len(clips)==2 and "Ready" in clips
    assert any(k in clips for k in ("Attack_chop","Attack_sweep","Attack_thrust"))
    tris=sum(g["accessors"][x["indices"]]["count"]//3 for m in g["meshes"] for x in m["primitives"])
    assert 0<tris<4200
    head=next(v for v in nodes if "Forged profile" in v["name"])
    mesh=g["meshes"][head["mesh"]]
    geo=g["accessors"][mesh["primitives"][0]["attributes"]["POSITION"]]
    bound=tuple(round(b-a,4) for a,b in zip(geo["min"],geo["max"]))
    assert bound not in bounds,bound
    bounds.add(bound)
    label=next(x["name"] for x in nodes if x["name"].startswith(f.stem+" "))
    results.append({"id":"WSC-WPN-"+f.stem,"name":label.split(" ",1)[1],"file":f.name,"triangles":tris,
                    "bytes":len(b),"clips":clips,"head_bounds":bound})
assert len(results)==11 and len(bounds)==11
print(json.dumps({"weapons":results,"unique_head_bounds":len(bounds),"weapon_styles":3,
                  "role":"rigged runtime assets, not equipped in a playable fight"},indent=2))
