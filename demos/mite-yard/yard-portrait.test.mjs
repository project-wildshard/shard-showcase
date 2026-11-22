import test from 'node:test'
import assert from 'node:assert/strict'
import {PerspectiveCamera,Vector3} from 'three'
import {cameraPose,createGame,step,VIEW_FOV} from './combat.mjs'
import {GANTRY,GANTRY_PLAQUE as sign} from './yard-layout.mjs'

test('yard ID clears portrait HUD at opening and first bite without changing aim',()=>{
 const w=402,h=874,camera=new PerspectiveCamera(VIEW_FOV,w/h,.04,55),g=createGame()
 const bounds=()=>{
  const p=g.player,pose=cameraPose(p)
  camera.position.set(p.x,pose.height,p.z)
  camera.rotation.set(pose.pitch,-p.yaw,pose.roll,'YXZ')
  camera.updateMatrixWorld()
  const toPixel=(x,y)=>{
   const v=new Vector3(x,y,GANTRY.z+sign.front).project(camera)
   return {x:(v.x+1)*w/2,y:(1-v.y)*h/2}
  }
  return [toPixel(-sign.width/2,sign.height+sign.faceHeight/2),toPixel(sign.width/2,sign.height-sign.faceHeight/2)]
 }
 for(const phase of ['opening','windup','closing windup']){
  if(phase==='windup'){
   for(let i=0;i<150&&g.mite.phase!=='windup';i++)step(g,{forward:1,aspect:w/h})
   assert.equal(g.mite.phase,'windup')
  }
  if(phase==='closing windup')for(let i=0;i<18;i++)step(g,{forward:1,aspect:w/h})
  const [tl,br]=bounds()
  assert(tl.x>125&&br.x<277,phase+' avoids flanking buttons')
  assert(tl.y>51&&br.y<240,phase+' fully visible below the HUD '+JSON.stringify([tl,br]))
  assert(br.x-tl.x>62,phase+' occupies a readable width')
 }
})
