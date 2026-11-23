"""W9b cosmetic finish proposals; keep the exact hoverboard BIN payload."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys

SOURCE = "b52b733aecf641b084e9d2729aa5dcd9849b993553cc687fd4bb0fd1c77730b3"
EXT = "KHR_materials_variants"
FINISHES = [
    dict(tag="oval-ochre", name="Oval Ochre", deck=0xA77634, grip=0x3C2A25, lamp=0xFFC675, pod=0x543221, rough=.48, metal=.29),
    dict(tag="rock-jade", name="Rock Jade", deck=0x2F6C58, grip=0x1E3632, lamp=0x8AF2AB, pod=0x1D4739, rough=.57, metal=.26),
    dict(tag="alley-violet", name="Alley Violet", deck=0x6345A5, grip=0x281F45, lamp=0xF28FD9, pod=0x3D244F, rough=.39, metal=.43),
    dict(tag="north-frost", name="North Frost", deck=0x85ACC3, grip=0x263B50, lamp=0xB8F4FF, pod=0x33516B, rough=.59, metal=.22),
]
def linear(c):
    vs=((c>>16&255)/255, (c>>8&255)/255, (c&255)/255)
    return [round(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4,8) for x in vs]

def unpack(glb):
    n=struct.unpack_from("<I",glb,12)[0]
    return json.loads(glb[20:20+n]),glb[28+n:]
def pack(j,blob):
    js=json.dumps(j,separators=(",",":"),ensure_ascii=False).encode()
    js+=b" "*(-len(js)%4)
    assert len(blob)%4==0
    return (struct.pack("<4sII",b"glTF",2,28+len(js)+len(blob))+
            struct.pack("<I4s",len(js),b"JSON")+js+
            struct.pack("<I4s",len(blob),b"BIN\0")+blob)

def colorway(source, style):
    materials=copy.deepcopy(source)
    part_names=("Deck paint","Rubber grip","Rim, nose and inlay","Repulsor cap")
    for i,(which,name) in enumerate(zip(("deck","grip","pod","pod"),part_names)):
        m=materials[i];m["name"]=style["name"]+" · "+name
        p=m["pbrMetallicRoughness"]
        p["baseColorFactor"]=[*linear(style[which]),1]
        if i==0:p.update(roughnessFactor=style["rough"],metallicFactor=style["metal"])
        if i>=2:
            m["emissiveFactor"]=linear(style["lamp"])
            m["extensions"]["KHR_materials_emissive_strength"]["emissiveStrength"]=1.45 if i==2 else 2.10
    return materials

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    donor=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art/wsc-prop-032-hoverboard.glb"
    glb=donor.read_bytes()
    assert hashlib.sha256(glb).hexdigest()==SOURCE
    doc,binary=unpack(glb)
    var=copy.deepcopy(doc)
    var.setdefault("extensionsUsed",[]).append(EXT)
    var.setdefault("extensions",{})[EXT]={"variants":[{"name":f["name"]} for f in FINISHES]}
    for style in FINISHES:var["materials"].extend(colorway(doc["materials"],style))
    for i,p in enumerate(var["meshes"][0]["primitives"]):
        assert p["material"]==i
        p.setdefault("extensions",{})[EXT]={"mappings":[{"material":4+4*v+i,"variants":[v]} for v in range(len(FINISHES))]}
    path=out/"wsc-prop-032-hoverboard-cache-finishes.glb"
    path.write_bytes(pack(var,binary))
    re,again=unpack(path.read_bytes())
    assert again==binary
    for k in ("nodes","accessors","bufferViews","scenes","buffers"):assert doc[k]==re[k]
    for a,b in zip(doc["meshes"][0]["primitives"],re["meshes"][0]["primitives"]):
        assert all(a.get(k)==b.get(k) for k in ("attributes","indices","mode","material"))
    # Blender proof applies each mapping from the packed asset, not a parallel palette.
    for i,style in enumerate(FINISHES):
        temp=copy.deepcopy(re)
        temp["extensions"].pop(EXT)
        if not temp["extensions"]:temp.pop("extensions")
        temp["extensionsUsed"].remove(EXT)
        for p in temp["meshes"][0]["primitives"]:
            mapping=p["extensions"].pop(EXT)["mappings"]
            if not p["extensions"]:p.pop("extensions")
            p["material"]=next(m["material"] for m in mapping if i in m["variants"])
        (out/f'{style["tag"]}-preview.glb').write_bytes(pack(temp,again))
    report=dict(source_sha256=SOURCE,geometry_bytes=len(binary),triangles=1232,variant_bytes=path.stat().st_size,
                bytes_over_default=path.stat().st_size-len(glb),finishes=FINISHES,
                scope="Cosmetic palette proposals; no cache assignment, unlock, physics or runtime shader changes.")
    (out/"cache-finishes-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))

if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
