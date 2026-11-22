import assert from 'node:assert/strict'
import test from 'node:test'
import {BoxGeometry,Color,Group,Mesh,MeshBasicMaterial,PerspectiveCamera,Scene} from 'three'
import {canvasRenderer} from './canvas_fallback.mjs'

function renderer(sceneryCull){
 const painted=[]
 const ctx={fillRect(){painted.length=0},beginPath(){this.path=[]},
  moveTo(...p){this.path.push(p)},lineTo(...p){this.path.push(p)},closePath(){},
  fill(){painted.push([this.fillStyle,...this.path])},stroke(){}}
 const canvas={getContext:()=>ctx,ownerDocument:{createElement:()=>({getContext:()=>null})}}
 const r=canvasRenderer(canvas,{sceneryCull})
 return {painted,r}
}

test('rigid scenery never changes the painter output as the camera sweeps or resizes',()=>{
 const enabled=renderer(true),baseline=renderer(false)
 const scene=new Scene();scene.background=new Color('#051813')
 const camera=new PerspectiveCamera(65,402/874,.06,10)
 camera.position.set(0,1,0)
 scene.add(camera)
 const mat=new MeshBasicMaterial({color:0xefaf42})
 const objects=new Group();objects.rotation.y=.16;objects.scale.set(1.13,.8,1.14);scene.add(objects)
 function box(size,position,group=objects,eligible=true){
  const mesh=new Mesh(new BoxGeometry(...size),mat)
  mesh.position.set(...position);mesh.userData.canvasScenery=eligible;group.add(mesh)
 }
 box([1,1,1],[5,1,-4]);box([1,1,1],[-5,1,-4])
 box([40,.1,.1],[0,1,-7]) // Spans the viewport even with all vertices offscreen.
 box([1,.04,.12],[0,1,-.06],scene) // Crosses the painter's near plane.
 box([1,1,1],[0,1,-14],scene) // Painter does not use the camera far plane.
 box([1,1,1],[40,1,-4],scene,false)
 let skipped=0
 for(const [width,height] of [[402,874],[874,402]]){
  camera.aspect=width/height;camera.updateProjectionMatrix()
  for(let i=-12;i<=12;i++){
   camera.rotation.set(i*.006,i*.07,.07)
   for(const {r} of [baseline,enabled]){r.setSize(width,height);r.render(scene,camera)}
   assert.deepEqual(enabled.painted,baseline.painted)
   assert.equal(enabled.r.stats.visitedTriangles+enabled.r.stats.skippedTriangles,baseline.r.stats.visitedTriangles)
   assert(enabled.r.stats.visitedTriangles>=12,'unmarked mesh remains')
   skipped+=enabled.r.stats.skippedTriangles
  }
 }
 assert(skipped>0)
})
