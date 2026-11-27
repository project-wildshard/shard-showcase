import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const req = createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT), 'package.json') : import.meta.url)
const enginePackage = req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(enginePackage, 'utf8')).version, '0.1.44')
await import(pathToFileURL(join(dirname(enginePackage), 'scripts/sim-node-loader.mjs')).href)
const { ZiplineDriver, ZiplineTrolley } = await import(
  pathToFileURL(req.resolve('@wildshard/engine/sim/cableTraversal')).href)
const { Vector3, Object3D } = await import(pathToFileURL(join(dirname(req.resolve('three')), 'three.module.js')).href)

export const row = {
  kind: 'zipline', id: 'showcase.zipline.calibration',
  top: { x: -212, y: 45, z: -34 },
  bottom: { x: -115, y: 14, z: -16.5 },
  // The positions are W08's wire anchors, not its deck tops. Offset from the deck is explicit.
  // Match the illustrative wire's absolute 1.2 m midspan sag; the driver takes metres per 100 m.
  sag: 120 / Math.hypot(97, 31, 17.5), hang: 1.55, gravity: 9.8, drag: .012, maxSpeed: 22,
  profile: { anchors: 'direct', start: 1.05, release: 1.86, landing: { back: .66, deck: .035, velocity: 2.5 } },
  landing: { x: -115, y: 12.746, z: -16.5 },
}
const profileName = process.argv[3] ?? 'baseline'
assert(['baseline','short','capped'].includes(profileName), 'Choose baseline, short or capped')
if (profileName === 'short') Object.assign(row, { gravity:48, maxSpeed:26 })
if (profileName === 'capped') Object.assign(row, { gravity:64 })
const driver = new ZiplineDriver(row)
const player = { position: new Vector3(), velocity: new Vector3() }
const t = new Object3D()
const parked = new ZiplineTrolley(driver, row.profile.start, t,
  { position: new Vector3(row.top.x, row.top.y, row.top.z), radius: 2, label: 'Ride zipline' },
  () => driver.isRiding, () => driver.start())
assert.equal(parked.prompt.radius, 2)
parked.prompt.onInteract()
assert.equal(parked.prompt.radius, 0)
const initial = driver.snapshot()
const dt = 1/60
const pose = () => ({ rider: player.position.toArray(), trolley: t.position.toArray(),
  s: driver.distance, speed: driver.speed, rotationY: t.rotation.y, roll: t.rotation.z })
const sample = [], key = []
let clone, clonePlayer
for (let tick=1; tick<=1800 && driver.isRiding; tick++) {
  const before = driver.distance
  const carried = driver.update(dt, player)
  assert(driver.distance > before && driver.speed <= row.maxSpeed)
  if (clone) {
    assert.equal(clone.update(dt, clonePlayer), carried)
    assert.deepEqual(clone.snapshot(), driver.snapshot())
    assert.deepEqual(clonePlayer.position.toArray(), player.position.toArray())
    assert.deepEqual(clonePlayer.velocity.toArray(), player.velocity.toArray())
  } else if (driver.distance >= driver.len*.5) {
    clone = new ZiplineDriver(row)
    clonePlayer = { position: new Vector3(), velocity: new Vector3() }
    clone.restore(driver.snapshot())
    assert.deepEqual(clone.snapshot(), driver.snapshot())
  }
  parked.follow(driver.distance)
  sample.push({ tick, carried, ...pose() })
  if (tick===1 || tick%60===0 || !carried) key.push(sample.at(-1))
}
assert(!driver.isRiding && clone, 'Ride must complete after restoring')
assert.equal(parked.prompt.radius, 2)
const final = sample.at(-1)
assert.equal(final.tick, { baseline:562, short:282, capped:302 }[profileName])
assert.equal(final.carried, false)
const landing = new Vector3(row.landing.x, row.landing.y, row.landing.z)
assert(Math.hypot(player.position.x-landing.x,player.position.z-landing.z) < row.profile.landing.back + .001)
assert(player.position.y >= landing.y+row.profile.landing.deck)
assert(Math.abs(player.velocity.length()-row.profile.landing.velocity)<1e-10)
const maxSpeed=Math.max(...sample.map(p=>p.speed))
const receipt = { scope:'Pinned engine cable driver and visual trolley only; not a native product/player integration',
  engine:'0.1.44', row, length_m:driver.len, plan_span_m:Math.hypot(97,17.5), seconds:final.tick*dt,
  maxSpeed_mps:maxSpeed, initial, final, restoredExactly:true, key }
console.log(JSON.stringify(receipt,null,2))
if (process.argv[2]) writeFileSync(process.argv[2],JSON.stringify({ ...receipt, frames:sample })+'\n')
