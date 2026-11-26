import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'

const load=(path)=>JSON.parse(readFileSync(path))
const [runFile,sceneFile,sightFile,output]=process.argv.slice(2)
assert(output,'usage: summarize-entry.mjs entry-run.json parity.json sight.json receipt.json')
const run=load(runFile), scene=load(sceneFile), sight=load(sightFile)
assert.equal(run.repeatExactly,true)
assert.deepEqual(run.entryRuns.map(r=>r.gateToYard.offset),[-.65,0,.65])
assert.deepEqual(sight.map(r=>r.id),run.fixtures.map(f=>f.id))
assert(sight.every((x,i)=>!x.environment_blocked&&x.fixture_intercept===(i<3)))
assert.deepEqual(run.closedGate.flags,[])
const paths=run.entryRuns.map(r=>{
  assert.deepEqual(r.attempts.at(-1).orderedFlags,run.fixtures.map(f=>'yard.hit.'+f.id))
  assert(r.airTicks===0&&r.maxStalls===0)
  const finalHit=r.attempts.at(-1).landingTick
  assert.equal(finalHit-r.started,r.firstMovementToLastHitTicks)
  assert.equal(finalHit-r.gateToYard.tick,r.drillClockTicks)
  assert(r.finished>finalHit,'timer must stop on the last impact, not recovery')
  return {offset:r.gateToYard.offset,routeMetres:r.routeMetres,
    gateToYard:r.gateToYard,airTicks:r.airTicks,maxStalls:r.maxStalls,
    firstMovementToLastHitTicks:r.firstMovementToLastHitTicks,drillClockTicks:r.drillClockTicks,
    hits:r.attempts.map(a=>[a.name,a.landingTick-r.started])}
})
const receipt={scope:'untouched Range Gate and existing six fixtures; travel, equipped strikes and timing in one headless host only',
  engine:run.engine,format:run.format,ticksPerSecond:60,scenery:scene,
  geometrySha256:run.geometrySha256,colliderMeshes:run.colliderMeshes,triangles:run.triangles,
  fixtures:run.fixtures,paths,closedGate:run.closedGate,sight,negativeControls:run.negativeControls}
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n')
