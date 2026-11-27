import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const f=resolve(process.argv[2]), b=readFileSync(f)
const sha=createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex')
assert.equal(sha,'5d019a020361c47187ec889f2bc947f82cd9f98a')
const {SECRETS,ZONES,REAL,ROCK}=await import(pathToFileURL(f))
const atRock=process.argv.includes('--rock')
const {x,y,z}=SECRETS.find(s=>s.k==='c'&&s.at===(atRock?'behind the Rock':'behind the oval'))
const {x:ox,z:oz,r,halfLen}=ZONES.find(a=>a.id==='04')
console.log(JSON.stringify({archive:'Raynos/project-wildshard-singleplayer@ce1cf050b3:art/showcase-template/round-5-blockout/layout.js',archiveBlob:sha,at:[x,y,z],...(atRock?{rock:ROCK}:{oval:{x:ox,z:oz,r,halfLen,runRadius:REAL.oval.radius}})},null,2))
