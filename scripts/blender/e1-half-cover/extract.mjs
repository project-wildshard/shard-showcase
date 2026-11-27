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
const rows=cover.filter(r=>r.band===1&&r.kind==='half').sort((a,b)=>a.x-b.x)
const review=rows.filter(r=>r.x>50&&r.x<75)
const context=cover.filter(r=>r.band===1&&r.kind==='crates'&&r.x>37&&r.x<89&&r.z> -47)
assert.equal(rows.length,9)
assert.equal(review.length,3)
console.log(JSON.stringify({archive:'Raynos/project-wildshard-singleplayer@ce1cf050b3',pins,ROAD,rows,review,context,
  dayPacks:packs.filter(r=>r.band===1&&!r.night).map(p=>({x:p.x,z:p.z}))},null,2))
