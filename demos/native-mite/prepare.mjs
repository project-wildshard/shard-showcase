import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here=dirname(fileURLToPath(import.meta.url))
const output=resolve(process.argv[2]??'')
assert(process.argv[2],'Pass a new output directory under an installed Wildshard project')
assert.equal(basename(output),'mite-calibration','The native folder must match the fixed shard slug')
const resolveFrom=createRequire(process.env.WSC_NODE_PROJECT
 ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const pkgroot=name=>dirname(resolveFrom.resolve(name+'/package.json'))
const loadModule=name=>import(pathToFileURL(resolveFrom.resolve(name)).href)
const sha=bytes=>createHash('sha256').update(bytes).digest('hex')
const load=async p=>JSON.parse(await readFile(p,'utf8'))
const write=(p,j)=>writeFile(p,JSON.stringify(j,null,2)+'\n')
const sdk=pkgroot('@wildshard/sdk'),format=resolve(dirname(resolveFrom.resolve('@wildshard/format/glbCost')),'..','..')
assert.equal((await load(join(sdk,'package.json'))).version,'0.4.12')
assert.equal((await load(join(format,'package.json'))).version,'0.43.0')

await import(pathToFileURL(join(sdk,'src/sharddev/bake/format-hook.mjs')).href)
const {parseGlbData}=await loadModule('@wildshard/format/glbCost')
const {parseSkinFile,validateSkinAssets,skinLookRules}=await loadModule('@wildshard/format/skinAssets')
const glb=await readFile(join(here,'../../public/assets/wildshard-art/wsc-actor-001-crate-mite-rig.glb'))
const rig=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)))
const node=rig.nodes.find(n=>n.skin!==undefined&&n.mesh!==undefined)
assert(node&&rig.meshes[node.mesh].primitives.length===7)
const file=sha(glb), costs=parseGlbData(glb)
const cost={decoded:costs.decoded,gpu:costs.gpu,triangles:costs.triangles,draws:costs.draws}
assert.equal(cost.triangles,386)
const row={id:'crate-mite',file,family:'pbr',rig:{skeleton:'wsc.crateMite',
  joints:[rig.skins[node.skin].joints.map(j=>rig.nodes[j].name)],
  clips:rig.animations.map(a=>a.name),sockets:['body','head']},cost}
const materials={},mapping={}
for(const [i,m] of rig.materials.entries()){
 const id='mite.part-'+i
 const pbr=m.pbrMetallicRoughness??{}
 const base={family:'pbr',colour:(pbr.baseColorFactor??[1,1,1]).slice(0,3),
   metalness:pbr.metallicFactor??0,roughness:pbr.roughnessFactor??.7}
 materials[id]=m.name==='Mite | day cyan lens'
  ? {family:'emissive',colour:m.emissiveFactor??[.012,.76,.91],intensity:1.95}
  : base
 mapping[m.name]=id
}
assert.equal(Object.keys(mapping).length,7)
assert.equal(materials[mapping['Mite | day cyan lens']].family,'emissive')
const binding={skin:row.id,material:{family:'pbr',colour:[.53,.18,.04]},
  materials:mapping,loops:['idle','walk','run','sleep']}
const blob=Buffer.from(JSON.stringify({row,binding})),skin=sha(blob)
const look={id:'template.look.crateMite',species:'crate-mite',recipe:'platform.skin',
  material:null,parameters:{skin},animation:{recipe:'platform.clips',parameters:{attackSpan:1.2},
    clipMap:{states:{idle:'idle',walk:'walk',attack:'attack.bite',hit:'hit',die:'die'},
      abilities:{'crate-mite.bite':'attack.bite','crate-mite.overclock':'attack.overclock'}}}}
const files=[
 {hash:skin,kind:'json',compressed:blob.length,decoded:blob.length*2,gpu:0,triangles:0,draws:0,dependencies:[file],critical:false},
 {hash:file,kind:'glb',compressed:glb.length,...cost,dependencies:[],critical:false}]
const stub={rows:{looks:[look]},files,library:[skin],look:{materials}}
assert.deepEqual(skinLookRules(stub),[])
assert.equal(parseSkinFile(blob).row.rig.clips.length,11)
validateSkinAssets(stub,new Map([[file,glb],[skin,blob]]))
await mkdir(output,{recursive:true})
assert.deepEqual(await readdir(output),[],'Output must be empty, never patch an existing checkout')
await cp(join(sdk,'src/shards/_template'),output,{recursive:true})
const d=n=>join(output,'data',n+'.json')
const identity=await load(d('identity'))
await write(d('identity'),{...identity,slug:'mite-calibration',name:'Mite calibration',revision:1})
const card=await load(d('card'))
for(const key of Object.keys(card.card))card.card[key]=card.card[key].replace('/src/shards/_template/','/src/shards/mite-calibration/')
await write(d('card'),{...card,slug:'mite-calibration',name:'Mite calibration',status:'hidden',
 blurb:'Private native skin and sword calibration; not a showcase release.'})
// The stock art receipt describes the unmodified upstream product, not this draft.
await rm(join(output,'hero.json'),{force:true})
const items=await load(d('items'));assert(items.rows.find(r=>r.id==='weapon.sword-iron')?.view.recipe==='kit.sword')
items.loadout.primary='weapon.sword-iron';await write(d('items'),items)
const spawns=await load(d('creatures'))
const base=spawns.spawns.find(s=>s.id==='grey-blob:1');assert(base)
const brain=spawns.brains.find(b=>b.id===base.brain);assert(brain.kind==='pursue')
spawns.brains.push({...brain,id:'mite-pursuit',awareRadius:18,leashRadius:30,speed:2,stopDistance:1.35})
Object.assign(base,{id:'crate-mite:1',species:'crate-mite',variant:'yard',brain:'mite-pursuit',strike:'crate-mite.bite',respawn:90})
// Keep the nearby proof corridor free of unrelated grey-blob attacks.
spawns.spawns=spawns.spawns.filter(s=>s.id!=='grey-blob:2'&&s.id!=='grey-blob:3')
await write(d('creatures'),spawns)
const species=await load(d('rows/species')),grey=species.find(s=>s.id==='grey-blob');assert(grey)
species.push({...grey,id:'crate-mite',label:'Crate Mite',
 dims:{...grey.dims,bodyY:.32,bodyHalfLen:.28,bodyRadius:.29,headRadius:.13,legLen:.24,halfWidth:.36},
 temperament:{brain:'mite-pursuit',reaction:'aggressive',leash:30,assist:0,home:{speed:2,stop:1.35}},
 senses:{notice:18},
 presentation:{blood:false,sounds:{}},
 abilities:[
  {use:'crate-mite.bite',range:[0,2.35],cooldown:1.2,weight:2,clip:'attack.bite',tell:'lane'},
  {use:'crate-mite.overclock',range:[1.3,3.1],cooldown:3,weight:1,clip:'attack.overclock',tell:'lane'}
 ],
 variants:[{...grey.variants[0],id:'yard',label:'Crate Mite',hp:70}]})
await write(d('rows/species'),species)
const strikes=await load(d('rows/strikes'))
const lane=strikes.find(s=>s.id==='template.blob.lane');assert(lane)
strikes.push({...lane,id:'crate-mite.bite',shape:{kind:'lane',length:3,width:1.05},
 tags:['creature.crateMite'],windup:.6,active:.22,recover:.38,cooldown:1,range:2.7,damage:14,speed:8})
strikes.push({...lane,id:'crate-mite.overclock',shape:{kind:'lane',length:3.55,width:1.18},
 tags:['creature.crateMite'],windup:23/30,active:.22,recover:.48,cooldown:2,range:3.1,damage:22,speed:10})
await write(d('rows/strikes'),strikes)
const oldlook=await load(d('look'));Object.assign(oldlook.materials,materials);await write(d('look'),oldlook)
const skins=await load(d('skins'));skins.push({species:row.id,look:look.id,skin,glb:file,files})
await write(d('skins'),skins)
await writeFile(join(output,'assets',file),glb);await writeFile(join(output,'assets',skin),blob)
const product=join(output,'generators/product.ts'),source=await readFile(product,'utf8')
const needle="animation: { recipe: 'platform.clips', parameters: { attackSpan: 1 } }"
assert.equal(source.split(needle).length,2,'Pinned template skin generation changed')
const animation=JSON.stringify(look.animation)
await writeFile(product,source.replace(needle,`animation: entry.species === 'crate-mite' ? ${animation} : { recipe: 'platform.clips', parameters: { attackSpan: 1 } }`))
console.log(JSON.stringify({output,file,skin,glbBytes:glb.length,cost,joints:row.rig.joints,clips:row.rig.clips,validated:'pinned native skin byte admission'}))
