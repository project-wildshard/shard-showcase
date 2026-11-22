import test from 'node:test'
import assert from 'node:assert/strict'
import {readFile} from 'node:fs/promises'

async function rig(suffix){
 const data=await readFile(new URL('../../public/assets/wildshard-art/wsc-actor-001-crate-mite-rig'+suffix+'.glb',import.meta.url))
 const j=JSON.parse(data.subarray(20,20+data.readUInt32LE(12)))
 const skinned=j.nodes.find(n=>n.skin!==undefined&&n.mesh!==undefined)
 return {j,skinned,bytes:data.length,
  triangles:j.meshes[skinned.mesh].primitives.reduce((n,p)=>n+j.accessors[p.indices].count/3,0),
  joints:j.skins[skinned.skin].joints.map(i=>j.nodes[i].name),
  clips:j.animations.map(a=>a.name)}
}
test('yard Mite upgrades geometry without changing the native rig contract',async()=>{
 const stock=await rig(''), far=await rig('-far'), hero=await rig('-yard')
 assert.equal(stock.triangles,386);assert.equal(far.triangles,138)
 assert.equal(hero.triangles,1734)
 assert(hero.bytes<275000);assert.equal(hero.j.textures?.length??0,0)
 assert.deepEqual(hero.joints,stock.joints);assert.deepEqual(hero.clips,stock.clips)
 assert.equal(hero.joints.length,7);assert.equal(hero.clips.length,11)
 for(const clip of hero.j.animations)for(const s of clip.samplers)assert.equal(s.interpolation??'LINEAR','LINEAR')
})
