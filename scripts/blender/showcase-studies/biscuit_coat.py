"""WSC-ACTOR-019 look board; pin the Nalati donor, never rewrite a joint or vertex."""
import hashlib
import io
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image, ImageFilter

DONOR_SHA = "7885a70507ef1ce6b6f4a87c72f9706b0a53785e934bc0803a964d3c75528bc2"
PALETTES = {
    "amber-bay": [(28, 18, 19), (77, 33, 33), (147, 61, 37), (218, 125, 62), (247, 203, 132)],
    "winter-dun": [(24, 22, 23), (64, 44, 45), (132, 102, 80), (191, 154, 99), (247, 218, 164)],
}


def smooth(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def recolor(im, palette):
    src = np.asarray(im, dtype=np.float32)
    base = np.asarray(im.filter(ImageFilter.GaussianBlur(.72)), dtype=np.float32)
    r, g, b = np.moveaxis(base, -1, 0)
    luma = base @ np.array([.33, .53, .14])
    # Roll paint into broad color bands. Keep dark points, pale embroidery and neutral metal.
    bands = (smooth(29, 47, luma) + smooth(52, 68, luma)
             + smooth(76, 91, luma) + smooth(112, 160, luma))
    mapped = np.stack([np.interp(bands, range(5), c) for c in np.array(palette).T], -1)
    warm = smooth(11, 31, r-b) * smooth(3, 21, r-g)
    protect = smooth(122, 178, luma) * (1 - smooth(11, 44, r-b))
    blend = (.23 + .64 * warm) * (1 - protect)
    target = base * (1 - blend[..., None]) + mapped * blend[..., None]
    target += (src-base) * .78  # Keep seam edges and small eye/bridle details.
    return Image.fromarray(np.uint8(np.rint(np.clip(target, 0, 255))))


def pack(doc, payload):
    j = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    j += b" " * (-len(j) % 4)
    payload += b"\0" * (-len(payload) % 4)
    return struct.pack("<4sII", b"glTF", 2, 28+len(j)+len(payload)) + struct.pack(
        "<I4s", len(j), b"JSON") + j + struct.pack("<I4s", len(payload), b"BIN\0") + payload


def build(path, out):
    file = path.read_bytes()
    assert hashlib.sha256(file).hexdigest() == DONOR_SHA, "Unexpected Nalati donor"
    n = int.from_bytes(file[12:16], "little")
    j, bin_data = json.loads(file[20:20+n]), file[28+n:]
    view = j["bufferViews"][j["images"][0]["bufferView"]]
    cut = (view["byteLength"]+3)//4*4
    assert view["byteOffset"] == 0
    tail = bin_data[cut:]
    src = Image.open(io.BytesIO(bin_data[:view["byteLength"]])).convert("RGB")
    for look, palette in PALETTES.items():
        image = recolor(src, palette)
        compressed = io.BytesIO()
        image.save(compressed, "WEBP", quality=88, method=6, exact=True)
        coat = compressed.getvalue()
        start = len(coat) + (-len(coat) % 4)
        doc = json.loads(json.dumps(j))
        doc["bufferViews"][0]["byteLength"] = len(coat)
        doc["buffers"][0]["byteLength"] = start + len(tail)
        for a,b in zip(j["bufferViews"][1:], doc["bufferViews"][1:]):
            a = a["extensions"]["EXT_meshopt_compression"]
            b = b["extensions"]["EXT_meshopt_compression"]
            b["byteOffset"] += start-cut
            assert a["buffer"] == b["buffer"] == 0
            assert a["byteOffset"]-cut == b["byteOffset"]-start
        assert all(doc[k] == j[k] for k in ("skins","nodes","accessors","meshes","materials"))
        payload = coat.ljust(start,b"\0") + tail
        assert payload[start:] == bin_data[cut:]
        # Variants are for internal review. Do not commit the donor or duplicate its binary.
        image.save(out / f"biscuit-{look}.png")
        derived = pack(doc, payload)
        (out / f"biscuit-{look}.glb").write_bytes(derived)
        print(f"{look}: texture={len(coat)} bytes; derived GLB={len(derived)} bytes; unchanged geometry payload={len(tail)} bytes")


if __name__ == "__main__":
    donor, out = map(Path, sys.argv[1:])
    out.mkdir(parents=True, exist_ok=True)
    build(donor, out)
