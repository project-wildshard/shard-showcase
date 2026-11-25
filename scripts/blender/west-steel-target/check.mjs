import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {AnimationMixer,LoopOnce,Box3,Euler} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const [path,report]=process.argv.slice(2);
const raw=readFileSync(path);
const js=JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString());
assert.ok(raw.length<131072,raw.length);
assert.deepEqual(js.animations[0].channels.map(c=>c.target.path).sort(),['rotation','scale']);
const asset=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.length),'');
const {scene,animations}=asset;
assert.equal(animations.length,1);
const [clip]=animations;
assert.equal(clip.name,'W3C_TargetImpact_1p4s');
assert.ok(Math.abs(clip.duration-1.4)<1e-6,clip.duration);
assert.equal(clip.tracks.length,2);
const pivot=scene.getObjectByName('Target_Swing_Pivot');
const pulse=scene.getObjectByName(clip.tracks.find(tr=>tr.name.endsWith('.scale')).name.split('.')[0]);
assert.ok(pivot&&pulse&&pulse.parent===pivot);
const m=new AnimationMixer(scene);
const a=m.clipAction(clip).setLoop(LoopOnce,0);
a.clampWhenFinished=true;a.play();
const rad=Math.PI/180;
let peak=-Infinity,returnPeak=Infinity,floorSpan=Infinity,lateral=Infinity;
const sample=t=>{
  m.setTime(t);
  scene.updateMatrixWorld(true);
  const extent=new Box3().setFromObject(pivot,true);
  const theta=new Euler().setFromQuaternion(pivot.quaternion).x/rad;
  peak=Math.max(peak,theta);returnPeak=Math.min(returnPeak,theta);
  floorSpan=Math.min(floorSpan,extent.min.y);
  lateral=Math.min(lateral,.755-Math.max(Math.abs(extent.min.x),Math.abs(extent.max.x)));
  return {theta,pulse:pulse.scale.toArray()};
};
const start=sample(0);
for(let k=1;k<=84;k++)sample(k/60);
const end={theta:new Euler().setFromQuaternion(pivot.quaternion).x/rad,pulse:pulse.scale.toArray()};
a.reset().play();
const on=sample(11/60);
assert.ok(Math.abs(on.theta-30)<.02&&on.pulse[0]>.98&&on.pulse[1]>.98,JSON.stringify(on));
assert.ok(Math.abs(start.theta)<.001&&Math.abs(end.theta)<.001);
assert.ok(start.pulse[0]<.002&&end.pulse[0]<.002);
assert.ok(peak>29.9&&returnPeak<-11.9&&floorSpan>.7&&lateral>.03,{peak,returnPeak,floorSpan,lateral});
const triangles=js.meshes.flatMap(m=>m.primitives).reduce((n,p)=>n+js.accessors[p.indices].count/3,0);
const summary={file:'w3c-swing-steel-target.glb',sha256:createHash('sha256').update(raw).digest('hex'),bytes:raw.length,triangles,
  clip:clip.name,durationSec:1.4,angleDegrees:[Math.round(returnPeak),Math.round(peak)],
  minimumClearanceAboveFloorM:+floorSpan.toFixed(4),minimumClearanceToSidePostsM:+lateral.toFixed(4),
  localAxis:'pivot X',reviewDistancesM:[25,50,75],scope:'Standalone game art; no hit handler, sound, scoring or map placement.'};
writeFileSync(report,JSON.stringify(summary,null,2)+'\n');
console.log(summary);
