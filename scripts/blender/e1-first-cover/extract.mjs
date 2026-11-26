import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const root=resolve(process.argv[2])
const pins={'layout.js':'5d019a020361c47187ec889f2bc947f82cd9f98a','placement.js':'6a067ec22a8e07f1d99a9d495d23063d2863ab10'}
for(const [file,expected] of Object.entries(pins)){
 const b=readFileSync(resolve(root,file))
 assert.equal(createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'),expected,file)
}
const {place}=await import(pathToFileURL(resolve(root,'placement.js')))
const {ROAD}=await import(pathToFileURL(resolve(root,'layout.js')))
const {cover,packs}=place()
const rows=cover.filter(r=>r.band===1&&r.kind==='crates'&&r.x<45&&r.z>-20).sort((a,b)=>a.x-b.x)
assert.equal(rows.length,3)
console.log(JSON.stringify({archive:'Raynos/project-wildshard-singleplayer@ce1cf050b3',pins,ROAD,rows,
  dayPacks:packs.filter(r=>r.band===1&&!r.night)},null,2))
