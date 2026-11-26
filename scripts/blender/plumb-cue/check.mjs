import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const root=dirname(dirname(req.resolve('three')))
const {AnimationMixer,Vector3,LoopOnce,Quaternion,PerspectiveCamera}=await import(pathToFileURL(join(root,'build/three.module.js')).href)
const {GLTFLoader}=await import(pathToFileURL(join(root,'examples/jsm/loaders/GLTFLoader.js')).href)
const out=process.argv[2]
async function load(name){
  const data=readFileSync(join(out,name+'.glb'))
  const r=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'')
  assert.equal(r.animations.length,1)
  const [clip]=r.animations
  assert(Math.abs(clip.duration-.70)<1e-5)
  const meshes=[]
  r.scene.traverse(n=>{if(n.isMesh)meshes.push(n)})
  assert.equal(meshes.length,3)
  assert(meshes.every(n=>n.material.isMeshBasicMaterial))
  const mix=new AnimationMixer(r.scene), action=mix.clipAction(clip)
  action.setLoop(LoopOnce,1).play();action.clampWhenFinished=true
  const verts=()=>meshes.flatMap(o=>Array.from({length:o.geometry.attributes.position.count},(_,i)=>
    o.getVertexPosition(i,new Vector3())))
  const sizes=[]
  for(const frame of [0,14,26,35,41,42.1]){
    mix.setTime(frame/60)
    const v=verts()
    assert(Math.abs(Math.min(...v.map(p=>p.x)))<1e-7)
    assert(Math.abs(Math.max(...v.map(p=>p.x))-1)<1e-7)
    sizes.push(Math.max(...v.map(p=>Math.hypot(p.y,p.z))))
  }
  assert(sizes[0]>.02&&sizes[2]>sizes[1]&&sizes[3]>sizes[2]&&Math.abs(sizes[5])<.002)
  for(const mesh of meshes){
    const index=mesh.geometry.index
    const stride=index?index.count:mesh.geometry.attributes.position.count
    for(let i=0;i<stride;i+=3){
      const p=[i,i+1,i+2].map(j=>mesh.getVertexPosition(index?index.getX(j):j,new Vector3()))
      assert(p[1].sub(p[0]).cross(p[2].sub(p[0])).lengthSq()<1e-12)
    }
  }
  action.reset().setLoop(LoopOnce,1).play();mix.setTime(35/60)
  return {r,meshes,verts,sizes}
}
const beam=await load('e3-plumb-beam')
const lane=await load('e3-plumb-lane')
assert(Math.abs(beam.sizes[3]-.061)<1e-6)
assert(Math.abs(lane.sizes[3]-.615)<.00001)
const newv=(x,y,z)=>new Vector3(x,y,z)
const origin=newv(0,.006,0),xAxis=newv(1,0,0)
function place(a,from,to){
  const delta=to.clone().sub(from)
  a.r.scene.position.copy(from)
  a.r.scene.scale.set(delta.length(),1,1)
  a.r.scene.quaternion.copy(new Quaternion().setFromUnitVectors(xAxis,delta.normalize()))
  a.r.scene.updateMatrixWorld(true)
}
function endpoint(a,end){
  const p=a.verts().filter(v=>Math.abs(v.x-1)<1e-6).map(v=>a.r.scene.localToWorld(v))
  const center=p.reduce((acc,v)=>acc.add(v),newv(0,0,0)).divideScalar(p.length)
  assert(center.distanceTo(end)<1e-6)
  return center.toArray()
}
const proof=[]
for(const h of [3,4,5])for(const distance of [12,15,18]){
  const target=newv(distance,.006,0), from=newv(0,h,0)
  place(beam,from,target);place(lane,origin,target)
  const b=endpoint(beam,target)
  const l=endpoint(lane,target)
  // The 0.07 m continuous core and 1.23 m maximum floor outline at their midpoint.
  // Screen widths reported as geometry evidence, not human/device acceptance.
  const mid=from.clone().lerp(target,.5), floor=origin.clone().lerp(target,.5)
  const sampled=[]
  for(const camPos of [newv(distance+2,1.72,2.4),newv(distance-2,1.72,6),newv(distance+4,1.72,-3.1)]){
    const cam=new PerspectiveCamera(58,402/874,.05,100)
    cam.position.copy(camPos)
    cam.lookAt(mid.clone().lerp(floor,.48))
    cam.updateMatrixWorld(true)
    const pixels=v=>{const p=v.clone().project(cam);return [p.x*201,p.y*437,p.z]}
    const spread=points=>{
      const p=points.map(pixels)
      assert(p.every(v=>Math.abs(v[0])<201&&Math.abs(v[1])<437&&Math.abs(v[2])<1))
      return Math.max(...p.flatMap(a=>p.map(b=>Math.hypot(a[0]-b[0],a[1]-b[1]))))
    }
    const width=spread([mid.clone().add(newv(0,0,.035)),mid.clone().add(newv(0,0,-.035))])
    const groundWidth=spread([floor.clone().add(newv(0,0,.615)),floor.clone().add(newv(0,0,-.615))])
    assert(width>3&&groundWidth>45)
    sampled.push([+width.toFixed(2),+groundWidth.toFixed(2)])
  }
  proof.push({h,distance,beamEndpoint:b,laneEndpoint:l,estimatedProjectedWidthsPx:sampled})
}
const result={frames:[0,14,26,35,41,42.1],beamRadii:beam.sizes,laneHalfWidths:lane.sizes,
  finalFolded:true,viewport:[402,874],threePlayback:true,placementCases:proof}
writeFileSync(join(out,'plumb-three.json'),JSON.stringify(result,null,2)+'\n')
console.log(JSON.stringify({placementCases:proof.length,cameraCases:proof.length*3,
  minNominalPx:Math.min(...proof.flatMap(d=>d.estimatedProjectedWidthsPx.map(x=>x[0])))}))
