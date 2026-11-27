// Only the two local contexts are checked in, not the archive itself.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const root = resolve(process.argv[2])
const band = Number(process.argv[3] ?? 1)
if (![1, 2].includes(band)) throw new Error('supported bands: 1, 2')
const pins = {
  'layout.js': '5d019a020361c47187ec889f2bc947f82cd9f98a',
  'placement.js': '6a067ec22a8e07f1d99a9d495d23063d2863ab10',
}
for (const [name, want] of Object.entries(pins)) {
  const data = readFileSync(resolve(root, name))
  const got = createHash('sha1').update(`blob ${data.length}\0`).update(data).digest('hex')
  if (got !== want) throw new Error(`${name} was not the Round 5 donor`)
}
const { place } = await import(pathToFileURL(resolve(root, 'placement.js')))
const world = place()
const close = (rows, p) => rows.filter(q => Math.hypot(q.x - p.x, q.z - p.z) < 16)
const anchors = world.chests.filter(c => c.band === band).map((p, i) => ({
  index: i + 1, three_xz: [p.x, p.z], cover: close(world.cover, p),
  crates: close(world.crates, p), packs: close(world.packs, p),
}))
if (anchors.length !== 2) throw new Error(`expected two Band ${band} anchors`)
console.log(JSON.stringify({
  archive: 'Raynos/project-wildshard-singleplayer@ce1cf050b3',
  source: 'art/showcase-template/round-5-blockout', pins,
  lab_blob: '51a3b4bef1f2d4891172164d10893d98d450a3b9',
  note: 'Round 5 geometry context; cover, crate and creature proxies are not final game geometry.',
  anchors,
}, null, 2))
