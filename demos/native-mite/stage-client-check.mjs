import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFile, mkdir, readdir, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'

const [output,standard,far]=process.argv.slice(2)
assert(output&&standard&&far&&process.argv.length===5,'Pass a new fixture folder and the standard and far product folders')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const packageFile=req.resolve('@wildshard/engine/package.json')
const json=async p=>JSON.parse(await readFile(p,'utf8'))
assert.equal((await json(packageFile)).version,'0.1.44')
await mkdir(output,{recursive:true})
assert.deepEqual(await readdir(output),[],'Use a fresh fixture directory')
// Stage only the exact cooked look and two hash-checked blobs for each tier.
for(const [tier,product,triangles] of [['standard',standard,386],['far',far,138]]){
 const {rows}=await json(join(product,'sections/look/materials.json'))
 const {look}=await json(join(product,'sections/look/look.json'))
 const {files}=await json(join(product,'shard.json'))
 const mite=rows.looks.find(x=>x.species==='crate-mite')
 assert.equal(mite?.recipe,'platform.skin')
 const skin=files.find(x=>x.hash===mite.parameters.skin),glb=files.find(x=>x.hash===skin?.dependencies[0])
 assert.equal(skin?.kind,'json');assert.equal(glb?.kind,'glb');assert.equal(glb.triangles,triangles)
 const folder=join(output,'public',tier);await mkdir(folder,{recursive:true})
 const stage=async ({kind,hash})=>{
  const bytes=await readFile(join(product,'blobs',kind,`${hash}.${kind}`))
  assert.equal(createHash('sha256').update(bytes).digest('hex'),hash)
  await writeFile(join(folder,hash),bytes)
  return bytes
 }
 const {binding}=JSON.parse(await stage(skin));await stage(glb)
 const materials=Object.fromEntries(Object.values(binding.materials).map(id=>[id,look.materials[id]]))
 assert(Object.values(materials).every(Boolean))
 await writeFile(join(folder,'source.json'),JSON.stringify({rows:{looks:[mite]},files:[skin,glb],look:{materials}}))
}
await writeFile(join(output,'index.html'),`<!DOCTYPE html><html lang="en"><meta charset="UTF-8">
<title>Wildshard native rig loader check</title><main><h1>Wildshard Crate Mite client rig loader check</h1>
<p>Engine 0.1.44 asset loading only. No rendered game scene.</p><output id="receipt">Loading</output></main>
<script type="module" src="./boot.mjs"></script></html>`)
await writeFile(join(output,'boot.mjs'),`
import { MeshStandardMaterial } from 'three'
import { Scope } from '@wildshard/engine/app/scope'
import { loadClientSkins } from ${JSON.stringify(join(dirname(packageFile),'src/client/game/shardfile/clientSkins.ts'))}
const receipt=document.querySelector('#receipt')
const get=async url=>{const r=await fetch(url);if(!r.ok)throw new Error('Asset read failed: '+r.status);return r}
const check=async (tier,expected)=>{
 const root=new URL('./'+tier+'/',document.baseURI)
 const source=await (await get(new URL('source.json',root))).json()
 const assets=new Map(await Promise.all(source.files.map(async file=>[file.hash,new Uint8Array(await (await get(new URL(file.hash,root))).arrayBuffer())])))
 const scope=new Scope()
 try{
  const skins=await loadClientSkins(source,assets,()=>new MeshStandardMaterial(),scope)
  const skin=skins.get(source.rows.looks[0].id),actual=skin.geometry.index.count/3
  if(actual!==expected||skin.bones.length!==7||skin.clips.size!==11)throw new Error('Wrong rig contract: '+actual)
  return tier+': '+actual+' triangles, '+skin.bones.length+' joints, '+skin.clips.size+' sampled clips'
 }finally{scope.dispose()}
}
try{
 const results=[]
 for(const [tier,tris] of [['standard',386],['far',138]]){results.push(await check(tier,tris));receipt.textContent=results.join(' | ')}
 receipt.textContent='PASS: '+results.join(' | ')
}catch(error){receipt.textContent='FAIL: '+String(error);console.error(error)}
`)
