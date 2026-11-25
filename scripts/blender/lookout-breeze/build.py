"""Optional W11 breeze GLBs, preserving the donor vertex and index streams."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "public/assets/wildshard-art"
SPEC = {
    "fern": ("b1b0079071ca92d1299431e87ca565bcdae62d4c200901a39c9efe957c90f295", .038, .021, 4.0),
    "verge": ("3bb2020dbf711bfc96b94f6bb7e98fba3c0489cfd19fba427eec88e4c65071b0", .030, .017, 3.2),
}
KEYS = 41
TARGETS = ("along", "against", "cross", "return")


def weights(u):
    theta = u * math.tau
    a = .82 * math.sin(theta) + .18 * math.sin(3 * theta)
    b = .48 * math.sin(theta) + .38 * math.sin(2 * theta) + .07 * (math.cos(theta) - 1)
    return max(0, a), max(0, -a), max(0, b), max(0, -b)


def unpack_glb(raw):
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    n, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    size, kind = struct.unpack_from("<I4s", raw, 20 + n)
    assert kind == b"BIN\0" and len(raw) == 28 + n + size
    return json.loads(raw[20:20+n]), bytearray(raw[28+n:])


def pack_glb(doc, body):
    doc["buffers"][0]["byteLength"] = len(body)
    meta = json.dumps(doc, separators=(",", ":")).encode()
    meta += b" " * (-len(meta) % 4)
    return (struct.pack("<4sIII4s", b"glTF", 2, 28+len(meta)+len(body), len(meta), b"JSON")
            + meta + struct.pack("<I4s", len(body), b"BIN\0") + body)


def build(name):
    digest, along, cross, period = SPEC[name]
    raw = (ASSETS / f"w11-lookout-{name}.glb").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    doc, body = unpack_glb(raw)

    def add(values, kind, bounds=False, target=None):
        cols = len(values[0])
        data = struct.pack(f"<{len(values)*cols}f", *(x for row in values for x in row))
        view = {"buffer": 0, "byteOffset": len(body), "byteLength": len(data)}
        if target:
            view["target"] = target
        acc = {"bufferView": len(doc["bufferViews"]), "componentType": 5126,
               "count": len(values), "type": kind}
        if bounds:
            acc.update(min=list(map(min, zip(*values))), max=list(map(max, zip(*values))))
        doc["bufferViews"].append(view)
        body.extend(data)
        doc["accessors"].append(acc)
        return len(doc["accessors"]) - 1

    mesh, = doc["meshes"]
    prim, = mesh["primitives"]
    assert prim["attributes"] == {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2}

    def vectors(i):
        v = doc["bufferViews"][i]
        a = v["byteOffset"]
        return list(struct.iter_unpack("<3f", body[a:a+v["byteLength"]]))

    pos, normals = vectors(0), vectors(1)
    height = max(p[1] for p in pos)
    directions = ((along, 0), (-along, 0), (0, cross), (0, -cross))
    targets = []
    for dx, dz in directions:
        morph_pos, morph_normal = [], []
        for (_, y, _), (nx, ny, nz) in zip(pos, normals):
            # Quadratic response anchors the entire basal collar and its normals.
            u = max(0, (y - .045) / (height - .045))
            du = 2 * u / (height - .045)
            morph_pos.append((dx*u*u, 0, dz*u*u))
            n = (nx, ny - du * (dx*nx + dz*nz), nz)  # inverse transpose of shear Jacobian
            q = math.sqrt(sum(v*v for v in n))
            morph_normal.append(tuple(v/q - orig for v, orig in zip(n, (nx, ny, nz))))
        targets.append({"POSITION": add(morph_pos, "VEC3", True, 34962),
                        "NORMAL": add(morph_normal, "VEC3", False, 34962)})
    prim["targets"] = targets
    mesh["weights"] = [0] * len(targets)
    mesh["extras"] = {"targetNames": list(TARGETS)}
    times = add([(period * i/(KEYS - 1),) for i in range(KEYS)], "SCALAR", True)
    keys = [weights(i/(KEYS - 1)) for i in range(KEYS - 1)]
    keys.append(keys[0])
    track = add([(x,) for key in keys for x in key], "SCALAR")
    doc["animations"] = [{
        "name": "Lookout_Breeze_" + name,
        "samplers": [{"input": times, "output": track, "interpolation": "LINEAR"}],
        "channels": [{"sampler": 0, "target": {"node": 0, "path": "weights"}}],
    }]
    result = pack_glb(doc, body)
    assert len(result) < 165_000
    p0, b0 = unpack_glb(raw)
    p1, b1 = unpack_glb(result)
    assert b1[:len(b0)] == b0 and p1["accessors"][:4] == p0["accessors"]
    return result, {"donor_sha256": digest, "width_extension_bound_m": math.hypot(along, cross),
                    "anchor_height_m": .045, "period_s": period, "keys": KEYS,
                    "triangles": doc["accessors"][3]["count"]//3, "bytes": len(result)}


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    entries = {}
    for name in SPEC:
        raw, proof = build(name)
        (out / f"w11-lookout-{name}-breeze.glb").write_bytes(raw)
        entries[name] = proof
    (out / "lookout-breeze-assets.json").write_text(json.dumps(entries, indent=2) + "\n")


if __name__ == "__main__":
    main()
