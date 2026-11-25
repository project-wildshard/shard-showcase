import * as T from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {makeSlagBatch} from './slag.mjs'

const loader=new GLTFLoader()
const load=f=>loader.loadAsync('/assets/'+f).then(g=>g.scene)
const [donor,shell,furnace]=await Promise.all([
  load('e4-ground-slag-decal.glb'),load('e4-cover-bay-shell.glb'),load('wsc-prop-057-foundry-furnace.glb')])
const batch=makeSlagBatch(donor)
const renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true})
renderer.setPixelRatio(1)
renderer.setSize(innerWidth,innerHeight)
renderer.toneMapping=T.ACESFilmicToneMapping
renderer.toneMappingExposure=1.1
document.body.append(renderer.domElement)
const scene=new T.Scene(), background=new T.Color(0x0f1320)
scene.background=background
const set=new T.Group();scene.add(set)
set.add(shell,furnace)
furnace.position.set(.52,0,-.56)
const base=new T.HemisphereLight(0xb2d0ff,0x594c40,1.2)
set.add(base)
const moon=new T.DirectionalLight(0x94b7ff,1.13)
moon.position.set(-4,8,4);set.add(moon)
const fill=new T.DirectionalLight(0xffbb8f,.13)
fill.position.set(2,2,-5);set.add(fill)
scene.add(batch.mesh)
const cam=new T.PerspectiveCamera(48,innerWidth/innerHeight,.065,45)
const point={born:0,x:0,y:.003,z:1.2,yaw:Math.PI}
let cameraLabel=''
function look(which){
  if(which==='portrait'){
    // Exact relative archived approach marker z=6 would crop the small surface on a narrow display;
    // this uses a review eye 0.2m to the side, five metres from the patch.
    cam.position.set(.20,1.70,6.20)
    cam.lookAt(0,.52,1.20)
  }else{
    cam.position.set(-2.45,2.25,4.30)
    cam.lookAt(.05,.28,.83)
  }
  cameraLabel=which
}
function snapshot(now, view='detail', count=1, isolated=false){
  if(view!==cameraLabel)look(view)
  set.visible=!isolated
  const entries=Array.from({length:count},(_,i)=>({...point,x:count===1?0:(i%4-1.5)*1.4,z:count===1?1.2:(Math.floor(i/4)-1)*1.4+1.2}))
  const heat=batch.update(now,entries)
  renderer.render(scene,cam)
  return {instances:batch.mesh.count,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,heat}
}
window.slagPreview={snapshot}
snapshot(0,location.search.includes('portrait')?'portrait':'detail')
