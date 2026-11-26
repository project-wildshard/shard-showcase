import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {AnimationMixer,Box3,Group,LoopOnce,Raycaster,Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {asset,center,door,durations,receipt,sha,splitGlb} from './pack.mjs';

const output=process.argv[2];
const raw=readFileSync(output?join(output,door):asset(door));
const donor=readFileSync(asset('e5b-alarm-gate-leaf.glb'));
assert.equal(sha(donor),receipt.assets['e5b-alarm-gate-leaf'].sha256);
const [expected,expectedBin]=splitGlb(donor);
const [actual,bin]=splitGlb(raw);
assert.deepEqual(actual.meshes,expected.meshes);
assert.deepEqual(actual.materials,expected.materials);
assert(bin.subarray(0,expectedBin.length).equals(expectedBin));
assert.equal(actual.nodes.filter(n=>n.mesh!==undefined).length,40);
assert(!actual.images && !actual.skins);
const tris=actual.meshes.flatMap(m=>m.primitives).reduce((s,p)=>s+actual.accessors[p.indices].count/3,0);
assert.equal(tris,736);

const loader=new GLTFLoader();
const sample=()=>loader.parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'');
const checkpoints={};
for (const [gate,origin] of Object.entries(receipt.origins_world_xyz)) {
  const yaw=receipt[gate+'_yaw_degrees']*Math.PI/180;
  const host=new Group();
  host.position.fromArray(origin);
  host.rotation.y=yaw;
  const {scene,animations}=await sample();
  host.add(scene);
  host.updateMatrixWorld(true);
  const left=host.getObjectByName('AlarmLeafLeft'), right=host.getObjectByName('AlarmLeafRight');
  assert(left&&right);
  assert.equal(left.children.length,20);
  assert.deepEqual(left.children.map(o=>o.geometry),right.children.map(o=>o.geometry));
  const rightX=new Vector3(1,0,0).applyQuaternion(right.quaternion);
  assert(rightX.distanceTo(new Vector3(-1,0,0))<1e-7);
  const axis=new Vector3(1,0,0).applyQuaternion(host.quaternion);
  const forward=new Vector3(0,0,1).applyQuaternion(host.quaternion);
  const aperture=()=>{
    const l=new Box3().setFromObject(left,true);
    const r=new Box3().setFromObject(right,true);
    const extent=b=>{
      const a=b.min.clone().sub(host.position).dot(axis);
      const z=b.max.clone().sub(host.position).dot(axis);
      return [Math.min(a,z),Math.max(a,z)];
    };
    assert(Math.abs(l.min.y-.015)<1e-5 && Math.abs(r.min.y-.015)<1e-5);
    const [outerL,edgeL]=extent(l),[edgeR,outerR]=extent(r);
    assert(outerL>=-16.1001 && outerR<=16.1001);
    assert(Math.abs(edgeL+edgeR)<1e-5);
    return edgeR-edgeL;
  };
  const ray=new Raycaster();
  function hit(x,y) {
    ray.set(host.localToWorld(new Vector3(x,y,-3)),forward);
    ray.far=6;
    return ray.intersectObject(scene,true).length>0;
  }

  checkpoints[gate]={pose:origin,yawDegrees:receipt[gate+'_yaw_degrees']};
  for (const [state,seconds] of Object.entries(durations)) {
    const clip=animations.find(a=>a.name==='Alarm_gate_'+state.toLowerCase());
    assert(clip&&Math.abs(clip.duration-seconds)<1e-6);
    assert.equal(clip.tracks.length,2);
    const mixer=new AnimationMixer(scene);
    const action=mixer.clipAction(clip);
    action.setLoop(LoopOnce,1);
    action.clampWhenFinished=true;
    action.play();
    let prior=null, rayCount=0, maxError=0;
    const n=Math.round(seconds*120), checkpointsM=[];
    for (let i=0;i<=n;i++) {
      const t=i/120;
      mixer.setTime(t);
      host.updateMatrixWorld(true);
      const gap=aperture(), intended=2*(center(state,t)-3.99);
      const error=Math.abs(gap-intended);
      assert(error<.0025, [gate,state,t,gap,intended,error]);
      maxError=Math.max(maxError,error);
      assert(gap>=-1e-5, [gate,state,t,gap]);
      if (prior!==null) assert(state==='Open' ? gap>=prior-1e-6 : gap<=prior+1e-6);
      prior=gap;
      if (i%12===0 || i===n) {
        const edge=gap/2;
        for (const y of [.25,1.4,2.88,3.68]) {
          if (edge>.06) {
            for (const side of [-1,1]) {
              assert(!hit(side*Math.min(7.78,edge-.035),y), [gate,state,t,y]);
              rayCount++;
            }
          }
          if (edge<7.75) {
            for (const side of [-1,1]) {
              assert(hit(side*(edge+.045),y), [gate,state,t,y]);
              rayCount++;
            }
          }
        }
      }
      if (i===0 || i===n/2 || i===n) checkpointsM.push(+gap.toFixed(5)+0);
    }
    action.stop();
    checkpoints[gate][state.toLowerCase()]={seconds,sampledPoses:n+1,
      apertureStartMidEndM:checkpointsM,faceRays:rayCount,maxCurveErrorMm:+(maxError*1000).toFixed(3)};
  }
}

const result={scope:'Animated visual gate pair only; no collision, trigger, hold time, signal switch, or phone test',
  slice:'E5b',catalogId:'WSC-KIT-006',
  asset:{file:door,bytes:raw.length,sha256:sha(raw),sourceSha256:sha(donor),
    trianglesUnique:tris,trianglesVisiblePair:tris*2},
  travelPerLeafM:receipt.travel_per_leaf_m,samplesHz:120,checks:checkpoints,
  pocket:'Original authored pocket requirement only; no new world collision or pockets'};
if(output) writeFileSync(join(output,'e5b-alarm-gate-motion-proof.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
