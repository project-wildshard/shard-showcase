"""Validate exported, untransformed W5c art in glTF coordinates (Y up, metres)."""
import json
import math
import struct
import sys
from pathlib import Path


def verify(file, variant, triangles, low, high):
    blob = file.read_bytes()
    assert struct.unpack_from("<4sII", blob) == (b"glTF", 2, len(blob))
    size = struct.unpack_from("<I", blob, 12)[0]
    doc = json.loads(blob[20:20 + size])
    bin_at = 28 + size
    assert not any(k in doc for k in ("animations", "images", "skins"))
    assert doc["scenes"][doc.get("scene", 0)]["nodes"] == [0, 1]
    nodes = {n["name"]: n for n in doc["nodes"]}
    assert set(nodes) == {"Continuous_grind_surface", "Mounts_and_supports"}
    assert all(set(n) == {"name", "mesh"} for n in nodes.values())

    def read_positions(primitive):
        a = doc["accessors"][primitive["attributes"]["POSITION"]]
        v = doc["bufferViews"][a["bufferView"]]
        assert (a["componentType"], a["type"]) == (5126, "VEC3")
        at = bin_at + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return [struct.unpack_from("<fff", blob, at + i*v.get("byteStride", 12))
                for i in range(a["count"])]

    parts = dict()
    total = 0
    for name, node in nodes.items():
        points = parts[name] = []
        for prim in doc["meshes"][node["mesh"]]["primitives"]:
            assert prim.get("mode", 4) == 4
            n = doc["accessors"][prim["indices"]]["count"]
            assert n % 3 == 0 and n
            total += n // 3
            points.extend(read_positions(prim))
    all_pts = sum(parts.values(), [])
    assert total == triangles and len(blob) < 97000
    for axis in range(3):
        values = [p[axis] for p in all_pts]
        assert math.isclose(min(values), low[axis], abs_tol=.002)
        assert math.isclose(max(values), high[axis], abs_tol=.002)

    rail = parts["Continuous_grind_surface"]
    left = [p for p in rail if p[0] < low[0] + .08]
    right = [p for p in rail if p[0] > high[0] - .08]
    lz, rz = max(p[1] for p in left), max(p[1] for p in right)
    if variant == "flat":
        assert math.isclose(high[0]-low[0], 12) and abs(lz-rz) < .001
    elif variant == "down":
        assert lz - rz > 1.28 and max(abs(p[2]) for p in rail) <= .106
    else:
        corner = [p for p in rail if abs(p[0]) < .08 and p[2] > 1.36]
        assert corner and 2.58 < max(p[1] for p in corner) < 2.80
        assert lz - rz > 2.85 and min(p[2] for p in right) < -.82
    print(f"{variant}: {total:,} triangles, {len(blob):,} bytes; checked actual GLB positions")


directory = Path(sys.argv[1])
for suffix, count, mn, mx in (
    ("flat", 1256, (-6, 0, -.255), (6, .82237, .255)),
    ("down", 1256, (-5.10825, 0, -.255), (5.10825, 2.17524, .255)),
    ("kink", 1632, (-4.81367, 0, -.97221), (4.53571, 3.82961, 1.705)),
):
    verify(directory/f"wsc-plan-009-grind-rail-{suffix}.glb", suffix, count, mn, mx)
