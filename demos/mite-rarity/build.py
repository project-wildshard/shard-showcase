"""Build an optional KHR_materials_variants view without touching the donor BIN."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DONOR=ROOT/'public/assets/wildshard-art/wsc-actor-001-crate-mite-rig-yard.glb'
EXT='KHR_materials_variants'

def read_glb(raw):
    magic,v,total=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and v==2 and total==len(raw)
    size,kind=struct.unpack_from('<I4s',raw,12)
    assert kind==b'JSON'
    binary=raw[20+size:]
    n,kind=struct.unpack_from('<I4s',binary)
    assert kind==b'BIN\0' and n+8==len(binary)
    return json.loads(raw[20:20+size]),binary

def pack(document,binary):
    j=json.dumps(document,ensure_ascii=False,separators=(',',':')).encode()
    j+=b' '*((-len(j))%4)
    return struct.pack('<4sIII4s',b'glTF',2,20+len(j)+len(binary),len(j),b'JSON')+j+binary

def build(raw,palette):
    assert hashlib.sha256(raw).hexdigest()==palette['sourceSha256']
    donor,binchunk=read_glb(raw)
    d=deepcopy(donor)
    assert EXT not in d.get('extensionsUsed',[]) and not d.get('extensionsRequired')
    labels=list(palette['variants'])
    d.setdefault('extensionsUsed',[]).append(EXT)
    d.setdefault('extensions',{})[EXT]={'variants':[{'name':n} for n in labels]}
    matIDs={m['name']:i for i,m in enumerate(d['materials'])}
    mapIDs={i:[] for i in matIDs.values()}
    changed=[]
    for ix,(name,swatches) in enumerate(palette['variants'].items()):
        for key,(col,metal,rough) in swatches.items():
            assert 'lens' not in key and key in matIDs
            assert len(col)==4 and col[3]==1 and all(0<=x<=1 for x in [*col,metal,rough])
            j=matIDs[key]
            m=deepcopy(d['materials'][j])
            m['name']=m['name']+' · '+name
            m['pbrMetallicRoughness'].update(baseColorFactor=col,metallicFactor=metal,roughnessFactor=rough)
            mapIDs[j].append({'material':len(d['materials']),'variants':[ix]})
            d['materials'].append(m)
            changed.append((name,key))
    for mesh in d['meshes']:
        for p in mesh['primitives']:
            if mapIDs[p['material']]:
                p.setdefault('extensions',{})[EXT]={'mappings':mapIDs[p['material']]}
    out=pack(d,binchunk)
    check,b=read_glb(out)
    assert b==binchunk
    assert check['materials'][:len(donor['materials'])]==donor['materials']
    base=deepcopy(check)
    del base['extensions'][EXT]
    if 'extensions' not in donor:del base['extensions']
    base['extensionsUsed'].remove(EXT)
    base['materials']=base['materials'][:len(donor['materials'])]
    for mesh in base['meshes']:
        for p in mesh['primitives']:
            x=p.get('extensions')
            if x and EXT in x:
                del x[EXT]
                if not x:del p['extensions']
    assert base==donor, 'No non-palette metadata may change'
    stock=d['skins'][0]['joints']
    proof={'originalBytes':len(raw),'variantBytes':len(out),'addedJsonBytes':len(out)-len(raw),
           'variantSha256':hashlib.sha256(out).hexdigest(),'binaryChunkSha256':hashlib.sha256(b).hexdigest(),
           'sourceSha256':palette['sourceSha256'],'joints':len(stock),'clipNames':[a['name'] for a in d['animations']],
           'alteredSlots':changed,'binaryChunkExact':True,'baseJsonExactAfterRemovingExtension':True}
    return out,proof

if __name__=='__main__':
    arg=argparse.ArgumentParser();arg.add_argument('output',type=Path);a=arg.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    b,p=build(DONOR.read_bytes(),json.loads((HERE/'palette.json').read_text()))
    (a.output/'e7a-mite-rarity.glb').write_bytes(b)
    (a.output/'e7a-build-proof.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps(p))
