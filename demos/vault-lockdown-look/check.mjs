import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {activeFrames,endFrame,frameAt,hz,phaseAt,pitch,rowOrder,slots,stepFrames,warningFrames} from './sweep.mjs';

const tile = new URL('../../public/assets/wildshard-art/vault-r4-tile.glb', import.meta.url);
const sha256 = createHash('sha256').update(readFileSync(tile)).digest('hex');
assert.equal(sha256,'5e72a76df5ebf3d39304b4b5ced156a1968baaf2268215e2c6a4f54ddc840440');
assert.equal(slots.length,29);
assert.equal(new Set(slots.map(s => String(s.xyz))).size,29);
assert.deepEqual(rowOrder.map(row => slots.filter(s => s.row === row).length),[1,5,5,7,5,5,1]);
assert.equal(warningFrames / hz, 1);
assert.throws(() => frameAt(2.1), RangeError);
for (const [idx,row] of rowOrder.entries()) {
    const phases = Array.from({length: endFrame+2},(_,i) => phaseAt(i-1,row));
    const beat = idx*stepFrames;
    assert.equal(phases.indexOf('warning')-1,beat);
    assert.equal(phases.indexOf('active')-1,beat+warningFrames);
    assert.equal(phases.filter(s => s==='warning').length,30);
    assert.equal(phases.filter(s => s==='active').length,activeFrames);
    assert.equal(phases.at(-1),'idle');
}
const counts = states => Object.fromEntries(['idle','warning','active'].map(p => [p,states.filter(s => s.state === p).length]));
assert.equal(counts(frameAt(-1)).idle,29);
assert.equal(counts(frameAt(endFrame)).idle,29);
const preview = [24,50,79].map(frame => ({frame, seconds:frame/hz, counts:counts(frameAt(frame)), states:frameAt(frame)}));
assert.deepEqual(preview.map(p => Object.values(p.counts)), [[18,11,0],[7,17,5],[11,6,12]]);
const output = {scope:'Visual preview only. 30 Hz timebase, not measured fps or a gameplay hazard.',
    tile_sha256:sha256, pitch, hz, warningFrames, activeFrames, stepFrames, endFrame, rowOrder,
    slots, preview};
writeFileSync(process.argv[2],JSON.stringify(output,null,2)+'\n');
console.log(preview.map(({frame,counts})=>({frame,...counts})));
