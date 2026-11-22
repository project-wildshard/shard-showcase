import test from 'node:test'
import assert from 'node:assert/strict'
import { PerspectiveCamera, Vector3 } from 'three'
import { createViewmodel, poseViewmodel, swordPose } from './viewmodel.mjs'
import { createGame, step, SWORD_SWING } from './combat.mjs'

test('sword viewmodel is bounded, textured by materials alone, with no ready-pose overlap of the aim point',()=>{
 const root=createViewmodel()
 let tris=0
 root.traverse(node=>{
  if(!node.isMesh)return
  tris+=(node.geometry.index?.count??node.geometry.attributes.position.count)/3
  for(const mat of [node.material].flat())assert.equal(mat.map,null)
 })
 assert(tris>1000&&tris<4100)
 for(const aspect of [402/874,1280/720]){
  const camera=new PerspectiveCamera(65,aspect,.04,55)
  camera.add(root);poseViewmodel(root,0,0,false,aspect);camera.updateMatrixWorld(true)
  const blade=root.getObjectByName('Forged stepped fuller and steel cutting bevel')
  const p=blade.geometry.attributes.position
  const uv=new Vector3()
  for(let i=0;i<p.count;i++){
   uv.fromBufferAttribute(p,i).applyMatrix4(blade.matrixWorld).project(camera)
   assert(uv.x>.17&&uv.x<1.0&&Math.abs(uv.y)<.92,'Ready blade must stay on screen and to the right')
  }
 }
})
test('blade uses authored steel finishes without changing the silhouette scale',()=>{
 const root=createViewmodel()
 const blade=root.getObjectByName('Forged stepped fuller and steel cutting bevel')
 assert.equal(blade.material.length,7)
 assert.equal(blade.geometry.groups.length,7,'One draw group per finish')
 assert.deepEqual(new Set(blade.geometry.groups.map(g=>g.materialIndex)),new Set([0,1,2,3,4,5,6]))
 assert(blade.material[0].roughness<blade.material[6].roughness,'Polished edge, dull nicks')
 assert(blade.material.every(m=>m.metalness>.5&&!m.map))
 blade.geometry.computeBoundingBox()
 const {max,min}=blade.geometry.boundingBox
 assert(Math.abs(max.y-.64)<.0001)
 assert(min.x>-.052&&max.x<.052)
})
test('windup, impact and follow-through align with the damage tick',()=>{
 const g=createGame();Object.assign(g.mite,{x:0,z:0,phase:'wake',hp:70})
 Object.assign(g.player,{x:0,z:1.65,yaw:0})
 const {impact,end}=SWORD_SWING
 assert(swordPose(.072)[0]>swordPose(0)[0])
 assert(swordPose(impact)[0]<swordPose(0)[0]&&swordPose(impact+.085)[0]<0)
 assert.deepEqual(swordPose(0),swordPose(end))
 step(g,{attack:true},.001)
 for(let i=0;i<14;i++)step(g,{},.01)
 assert.equal(g.mite.hp,70)
 step(g,{},.01);assert.equal(g.mite.hp,46)
 for(let i=0;i<20;i++)step(g,{},.01)
 assert.equal(g.mite.hp,46)
})
