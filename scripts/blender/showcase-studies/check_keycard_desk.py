"""Check standalone desk and pickup GLBs, not the in-game quest."""
import json
import math
import struct
import sys
from pathlib import Path

out = Path(sys.argv[1])
for file, nodes, lower, upper, tris, limit in [
    ("foreman-desk", ["Foreman_Desk_Geometry", "Analog_Lamp_And_Ledger"],
     [-.89,0,-.385], [.89,1.405,.385], 1936, 116_000),
    ("vault-keycard", ["Vault_Keycard_Quest_Prop"],
     [-.0715,0,-.0435], [.0715,.0114,.0435], 440, 30_000),
]:
    p = out/f"wsc-kit-006-{file}.glb"
    blob = p.read_bytes()
    assert struct.unpack_from("<4sII",blob)==(b"glTF",2,len(blob))
    length=struct.unpack_from("<I",blob,12)[0]
    d=json.loads(blob[20:20+length])
    assert all(set(n)=={"mesh","name"} for n in d["nodes"])
    assert [n["name"] for n in d["nodes"]]==nodes
    assert not {"animations","images","skins"} & d.keys()
    primitives=[p for m in d["meshes"] for p in m["primitives"]]
    assert sum(d["accessors"][p["indices"]]["count"] for p in primitives)==tris*3
    points=[]
    for prim in primitives:
        a=d["accessors"][prim["attributes"]["POSITION"]]
        v=d["bufferViews"][a["bufferView"]]
        assert a["type"]=="VEC3" and a["componentType"]==5126
        start=28+length+v.get("byteOffset",0)+a.get("byteOffset",0)
        points.extend(struct.unpack_from("<fff",blob,start+i*v.get("byteStride",12))
                      for i in range(a["count"]))
    for axis in range(3):
        assert math.isclose(min(v[axis] for v in points),lower[axis],abs_tol=1e-5)
        assert math.isclose(max(v[axis] for v in points),upper[axis],abs_tol=1e-5)
    names={m["name"] for m in d["materials"]}
    assert ("Vault copper polymer" in names)==(file=="vault-keycard")
    assert len(blob)<limit
    print(f"{p.name}: {len(blob):,} bytes, {tris:,} triangles, standalone local pivot")
