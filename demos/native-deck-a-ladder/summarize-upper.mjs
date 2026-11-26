import assert from 'node:assert/strict'
import {readFileSync, writeFileSync} from 'node:fs'
import {join} from 'node:path'

const [dir, output] = process.argv.slice(2)
assert(dir && output, 'Pass the trace/review directory and output JSON path')
const read = path => JSON.parse(readFileSync(join(dir, path), 'utf8'))
const decks = {}
for (const id of ['B','C']) {
  const {versions,route,deckRim,normalRoom,explicitStockInstaller:t,selectedApproachInput,approachTrials} = read(id+'.json')
  const artFit = read(id+'-review/art-fit.json')
  assert.equal(artFit.deck,id)
  assert.deepEqual(versions,{engine:'0.1.44',format:'0.43.0'})
  assert.equal(artFit.guardGapClearRays,30)
  assert.equal(artFit.treadHits,15)
  assert.equal(artFit.groundSamples,25)
  assert.equal(selectedApproachInput,.7)
  assert(t.landed.ground && t.landed.feet[2]<deckRim-.05)
  assert(t.low.ground && t.low.feet[1]<.09)
  assert.equal(t.maxRestoreErrorMeters,0)
  assert(!normalRoom.installedLadder && normalRoom.maxFeetY < .05)
  assert.deepEqual(approachTrials.map(x=>x.input),[.4,.55,.7,.85,1])
  const best=approachTrials.find(x=>x.input===.7)
  const control=approachTrials.find(x=>x.input===1)
  assert(best.peakDropMetersPerTick < .065 && control.peakDropMetersPerTick > .084)
  assert(approachTrials.every(x=>x.peakDropMetersPerTick>=best.peakDropMetersPerTick))
  const riseSeconds=(t.landed.tick-t.bottom.tick)/60
  decks[id]={route,deckRim,normalRoom,artFit,selectedApproachInput,approachTrials,
    riseSeconds,landed:t.landed,returned:t.low,restoredTicks:t.restoredTicks,
    maxRestoreErrorMeters:t.maxRestoreErrorMeters,
    alignedPeakMetersPerTick:t.alignedPeakMetersPerTick}
}
const evidence={versions:{engine:'0.1.44',format:'0.43.0'},slice:'W8a',
  scope:'Separate stock installer benches; normal native room does not attach. No new geometry, control binding or live changes.',
  exactReplay:'Each approach comparison restores the same landed state; same measured point, no position overwrite during ascent/descent.',
  decks}
writeFileSync(output,JSON.stringify(evidence,null,2)+'\n')
