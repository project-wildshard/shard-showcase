import {cp,mkdir,readFile,readdir,stat} from 'node:fs/promises'
import {fileURLToPath} from 'node:url'
import {dirname,join,relative,resolve} from 'node:path'
import {createRequire} from 'node:module'
import assert from 'node:assert/strict'
const home=dirname(fileURLToPath(import.meta.url))
const dest=resolve(process.argv[2]||join(home,'dist'))
const get=createRequire(import.meta.url)
const three=resolve(process.env.WSC_THREE_ROOT||join(dirname(get.resolve('three')),'..'))
const pkg=JSON.parse(await readFile(join(three,'package.json'),'utf8'))
assert.equal(pkg.version,'0.186.0')
await mkdir(dest,{recursive:true})
await mkdir(join(dest,'assets'),{recursive:true})
await cp(join(home,'../../public/assets/wildshard-art/wsc-actor-001-crate-mite-rig.glb'),join(dest,'assets/mite.glb'))
for(const name of ['index.html','yard.css','yard.mjs','combat.mjs','canvas_fallback.mjs','viewmodel.mjs'])await cp(join(home,name),join(dest,name))
const deps=new Set()
async function module(name){
 if(deps.has(name))return
 assert(!name.startsWith('..')&&!name.startsWith('/'))
 deps.add(name)
 const source=join(three,name),out=join(dest,'vendor/three',name)
 const text=await readFile(source,'utf8')
 const refs=Array.from(text.matchAll(/\b(?:from\s*|import\s*)(['"])(\.\.?\/[^'"\n]+)\1/g),m=>m[2])
 await mkdir(dirname(out),{recursive:true});await cp(source,out)
 for(const ref of refs)await module(relative(three,resolve(dirname(source),ref)))
}
await module('build/three.module.js')
await module('examples/jsm/loaders/GLTFLoader.js')
await cp(join(three,'LICENSE'),join(dest,'vendor/three/LICENSE'))
async function size(path){
 let n=0;for(const e of await readdir(path,{withFileTypes:true}))n+=e.isDirectory()?await size(join(path,e.name)):(await stat(join(path,e.name))).size
 return n
}
console.log('Static build',deps.size,'Three modules,',await size(dest),'bytes')
