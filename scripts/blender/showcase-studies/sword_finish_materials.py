"""E8e inventory materials. Only the materials dictionary in the GLB may change."""
import copy
import hashlib
import json
from pathlib import Path
from struct import pack, unpack_from

ROOT=Path(__file__).resolve().parents[3]
DONOR=ROOT/'public/assets/wildshard-art/wsc-gear-001-sword.glb'
PIN='64d9cf3926a58752233d9a40a467d87dfa9489b2270b83f95d577afa53295d62'
PAL={
    'warden':{
        'Bright perimeter catch':((.24,.66,.78),.63,.28,(.009,.053,.062)),
        'Satin silver, light facet':((.089,.232,.301),.71,.34,None),
        'Satin silver, shadow facet':((.027,.069,.104),.66,.39,None),
        'Silver worn stipple':((.138,.363,.420),.54,.49,(.015,.112,.146)),
        'Graphite hardware':((.066,.091,.127),.64,.39,None),
    },
    'hot-mess':{
        'Bright perimeter catch':((.63,.264,.085),.70,.33,(.044,.012,.002)),
        'Satin silver, light facet':((.265,.099,.036),.64,.44,None),
        'Satin silver, shadow facet':((.078,.026,.019),.61,.51,None),
        'Silver worn stipple':((.91,.235,.034),.51,.46,(.344,.053,.004)),
        'Graphite hardware':((.106,.068,.057),.68,.46,None),
    },
}
LABELS={'base':('COMMON SWORD','ORIGINAL INVENTORY MODEL'),
        'warden':('WARDEN FINISH','VAULT WARDEN CHEST'),
        'hot-mess':('HOT MESS FINISH','NIGHT ELITE REWARD')}

def digest(x):
    return hashlib.sha256(x).hexdigest()

def parse(raw):
    assert unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    n,t=unpack_from('<I4s',raw,12)
    assert t==b'JSON' and n%4==0
    doc=json.loads(raw[20:20+n])
    length,t=unpack_from('<I4s',raw,20+n)
    binary=raw[28+n:]
    assert t==b'BIN\0' and len(binary)==length and length%4==0
    return doc,binary

def encode(doc,binary):
    encoded=json.dumps(doc,separators=(',',':')).encode()
    encoded+=b' '*(-len(encoded)%4)
    return pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))+pack('<I4s',len(encoded),b'JSON')+encoded+pack('<I4s',len(binary),b'BIN\0')+binary

def build(out):
    raw=DONOR.read_bytes()
    assert digest(raw)==PIN
    base,binary=parse(raw)
    assert len(binary)==34488 and len(base['nodes'])==len(base['meshes'])==1
    assert base['nodes']==[{'mesh':0,'name':'WSC-GEAR-001 Sword | Inventory pivot'}]
    assert not any(base.get(n) for n in ('images','animations','extensionsRequired','skins'))
    original={k:v for k,v in base.items() if k!='materials'}
    tri=sum(base['accessors'][p['indices']]['count']//3 for p in base['meshes'][0]['primitives'])
    assert tri==660
    paths={'base':DONOR}
    proof={}
    for key,recipe in PAL.items():
        draft=copy.deepcopy(base)
        for mat in draft['materials']:
            n=mat['name']
            if n not in recipe:continue
            rgb,metal,rough,em=recipe[n]
            pbr=mat['pbrMetallicRoughness']
            pbr.update(baseColorFactor=[*rgb,1],metallicFactor=metal,roughnessFactor=rough)
            if em:mat['emissiveFactor']=em
        result=encode(draft,binary)
        file=out/f'e8e-sword-{key}-finish.glb'
        file.write_bytes(result)
        check,buf=parse(file.read_bytes())
        assert buf==binary and {k:v for k,v in check.items() if k!='materials'}==original
        assert [m['name'] for m in check['materials']]==[m['name'] for m in base['materials']]
        assert [n['name'] for n,m in zip(check['materials'],base['materials']) if n!=m]==list(recipe)
        assert len(result)<41000
        proof[key]={'sha256':digest(result),'bytes':len(result),'materialsChanged':list(recipe)}
        paths[key]=file
    return paths,{'donorSha256':PIN,'BINBytes':len(binary),'BINSha256':digest(binary),
          'trianglesEach':tri,'inventoryPivotUnchanged':True,
          'unchangedOtherGLTFFields':True,'variants':proof}
