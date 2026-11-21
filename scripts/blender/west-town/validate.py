import json,runpy,struct,hashlib
f=out/'whole-town-WIP.glb';b=f.read_bytes()
assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b))
g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert not g.get('skins') and not g.get('animations')
assert all('uri' not in x for x in g.get('images',[])+g.get('buffers',[]))
sig=runpy.run_path(str(HERE.parent/'west-scene-r02/semantic_glb.py'))['signature']
actual=sig(f)
strict=actual;changes=0
if list(actual)!=expected['semantic_signature']:
 normalize=runpy.run_path(str(HERE.parent/'west-zip/arm_uv.py'))['normalize']
 temporary=out/'parity-arm-uv.glb'
 try:
  changes=normalize(f,temporary);actual=sig(temporary)
  assert list(actual)==expected['normalized_semantic_signature'],(actual,expected)
 finally:
  temporary.unlink(missing_ok=True)
(out/'parity.json').write_text(json.dumps({'matched_signature':actual,'raw_signature':strict,'inherited_arm_uv_writes':changes,'rebuilt_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},indent=2)+'\n')
print('WHOLE TOWN SEMANTIC PARITY PASS',actual)
