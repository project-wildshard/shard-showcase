"""Check the four exported GLBs from scratch or a clean art checkout."""
import json
import math
from pathlib import Path
import struct
import sys

out = Path(sys.argv[1])
spec = {
    'wsc-plan-003-hinged-seesaw': (125_000, 1400, {'Fixed_Base': 0, 'Hinged_Deck': 1.47}, (13.985, 1.869, 2.96), 0),
    'wsc-plan-004-rolling-ball': (28_000, 500, {'Ball_Center_Pivot': 0}, (1.6, 1.6, 1.6), -.8),
    'wsc-plan-005-skittle-pin': (16_000, 270, {'Skittle_Floor_Pivot': 0}, (.58, 1.29, .566), 0),
    'wsc-plan-006-pressure-plate': (72_000, 720, {'Fixed_Frame': 0, 'Moving_Tread': .28}, (4, .3425, 4), 0),
}
for asset, (byte_cap, tri_cap, pivots, dimensions, floor) in spec.items():
    b = (out / (asset + '.glb')).read_bytes()
    assert len(b) < byte_cap and struct.unpack_from('<4sII', b) == (b'glTF', 2, len(b))
    length, chunk = struct.unpack_from('<I4s',b,12)
    assert chunk == b'JSON'
    doc = json.loads(b[20:20+length])
    assert not doc.get('images') and not doc.get('animations') and not doc.get('skins')
    low, high = [math.inf]*3, [-math.inf]*3
    tris = 0
    assert set(doc['scenes'][doc.get('scene', 0)]['nodes']) == set(range(len(doc['nodes'])))
    assert set(pivots) == {n['name'] for n in doc['nodes']}
    for node in doc['nodes']:
        t = node.get('translation', [0, 0, 0])
        assert 'rotation' not in node and 'scale' not in node and 'matrix' not in node
        assert math.isclose(t[1], pivots[node['name']], abs_tol=1e-5) and abs(t[0])+abs(t[2])<1e-5, node
        for part in doc['meshes'][node['mesh']]['primitives']:
            assert part.get('mode',4)==4
            position = doc['accessors'][part['attributes']['POSITION']]
            idx = doc['accessors'][part['indices']]
            assert idx['count']%3==0 and ('max' not in idx or idx['max'][0]<position['count'])
            tris += idx['count']//3
            for i in range(3):
                low[i] = min(low[i], position['min'][i]+t[i])
                high[i] = max(high[i], position['max'][i]+t[i])
    actual = tuple(h-l for l,h in zip(low,high))
    assert 0<tris<=tri_cap and abs(low[1]-floor)<.018, (asset, tris, low)
    assert all(abs(a-b)<.022 for a,b in zip(actual,dimensions)), (asset,actual)
    print(f'{asset} {len(b):,} bytes, {tris:,} triangles, {tuple(round(v,3) for v in actual)} m')
