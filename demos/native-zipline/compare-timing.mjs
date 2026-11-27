import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {join} from 'node:path'

const dir=process.argv[2]
assert(dir, 'Pass the experiment output directory')
const read=(name,file)=>JSON.parse(readFileSync(join(dir,name,file+'.json'),'utf8'))
const round=(n,d=4)=>Number(n.toFixed(d))
const cases=['baseline','short','capped'].map(profile=>{
  const ride=read(profile,'ride'), fit=read(profile,'fit'), handoff=read(profile,'handoff')
  assert.equal(ride.engine,'0.1.44')
  assert.equal(fit.seconds,round(ride.seconds))
  assert.equal(fit.ride_ticks,ride.final.tick)
  assert.deepEqual(fit.row,ride.row)
  assert(ride.restoredExactly&&fit.midpoint_restore_exact&&fit.visual_minimum_m>.025)
  assert(handoff.center.pass&&handoff.cases.length===15&&handoff.cases.every(x=>x.pass))
  assert(!handoff.closed.pass&&handoff.closed.arrival>.70)
  const {gravity,drag,maxSpeed,...geometry}=ride.row
  const share={geometry,donor:fit.donor_sha256,terminal:handoff.meshSha}
  const top1=Math.max(...ride.frames.map((f,i)=>(f.speed-(ride.frames[i-1]?.speed??ride.initial.v))*60))
  return {share,metrics:{
    profile,gravity,quadraticDrag:drag,speedCapMps:maxSpeed,rideTicks:ride.final.tick,
    cableSeconds:round(ride.seconds),releaseVelocityMps:ride.row.profile.landing.velocity,
    peakMps:round(ride.maxSpeed_mps),peakDriveAccelerationMps2:round(top1),
    visualSamples:fit.samples,minimumSampledClearanceM:fit.visual_minimum_m,
    wallSampledClearanceM:fit.wall_visual_minimum_m,
    stockReleaseJumpM:round(handoff.stockDismountStep),
    handoffMaximumStepM:round(Math.max(...handoff.cases.map(x=>x.maxStep))),
    handoffStepCount:handoff.approachTicks+handoff.groundTicks,
    successfulMotorStarts:handoff.cases.length,
    blockedControlMissM:round(handoff.closed.arrival)
  }}
})
for(const c of cases)assert.deepEqual(c.share,cases[0].share)
assert.equal(cases[1].metrics.cableSeconds,4.7)
assert.equal(cases[2].metrics.speedCapMps,22)
const receipt={
  scope:'Three local stock-driver calibrations and separate swept handoffs on original W08 art. Not a product or a continuous native carry, clock or phone test.',
  engine:'0.1.44',donorSha256:cases[0].share.donor,terminalSha256:cases[0].share.terminal,
  unchangedGeometry:cases[0].share.geometry, profiles:cases.map(x=>x.metrics),
}
writeFileSync(join(dir,'comparison.json'),JSON.stringify(receipt,null,2)+'\n')
