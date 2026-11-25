import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {sampleSlamCue,bindSlamMesh} from './timeline.mjs';
const root=new URL('../../',import.meta.url);
const source=new URL('public/assets/wildshard-art/',root);
const receipt=JSON.parse(readFileSync(new URL('project/layouts/e5a-riveter-slam-vfx.json',root)));
const maxR=receipt.review_radius_m,travel=receipt.review_wave_seconds;
function near(a,b,e=1e-6){assert.ok(Math.abs(a-b)<e,`${a} ≠ ${b}`)}
for (const [id,key] of [['warning-ring','warning'],['travel-front','wave']]){
  const data=readFileSync(new URL('e5a-riveter-'+id+'.glb',source));
  const spec=receipt[key];
  assert.equal(data.length,spec.bytes);
  assert.equal(createHash('sha256').update(data).digest('hex'),spec.sha256);
  const pkg=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'');
  assert.equal(pkg.animations.length,0);
  pkg.scene.traverse(node=>assert.ok(!node.isLight && !node.isSkinnedMesh));
  const ring=bindSlamMesh(pkg.scene);
  assert.equal(ring.geometry.index.count/3,spec.triangles);
  assert.ok(ring.material.depthTest && !ring.material.depthWrite && ring.material.transparent);
  const p=ring.geometry.getAttribute('position'), c=ring.geometry.getAttribute('color');
  const rs=Array.from({length:p.count},(_,i)=>Math.hypot(p.getX(i),p.getZ(i)));
  near(Math.min(...rs),spec.normalized_radii[0]);
  near(Math.max(...rs),1);
  const shapeCount=spec.arc_runs, steps=spec.segments_per_run;
  const rows=p.count/shapeCount/(steps+1);
  for(let i=0;i<p.count;i++){
    assert.equal(p.getY(i),0);
    const radial=i%rows;
    if(radial===0 || radial===rows-1) assert.equal(c.getW(i),0);
    else if(key==='wave') assert.ok(c.getW(i)>0);
  }
  if(key==='warning'){
    let midRays=0;
    for(let i=0;i<shapeCount;i++){
      const from=i*(steps+1)*rows, to=from+steps*rows;
      const angle=(n)=>Math.atan2(p.getZ(n),p.getX(n));
      const step=(a,b)=>((b-a)+2*Math.PI)%(2*Math.PI);
      const arc=step(angle(from),angle(to));
      near(arc/(2*Math.PI/24),.70);
      near(step(angle(to),angle(((i+1)%shapeCount)*(steps+1)*rows))/(2*Math.PI/24),.30);
      if(c.getW(from+2*rows+2)>.99)midRays++;
    }
    assert.equal(midRays,24);
  } else {
    for(let i=0;i<rows;i++){
      const j=p.count-rows+i;
      near(p.getX(i),p.getX(j));near(p.getZ(i),p.getZ(j));near(c.getW(i),c.getW(j));
    }
  }
  console.log(id,spec.triangles,'triangles',spec.bytes,'bytes');
}
assert.equal(sampleSlamCue(-.0001,maxR).state,'off');
assert.equal(sampleSlamCue(0,maxR).state,'warning');
assert.equal(sampleSlamCue(.9999,maxR).state,'warning');
assert.equal(sampleSlamCue(1,maxR).state,'wave');
assert.equal(sampleSlamCue(1+travel,maxR).state,'off');
let prev=0;
for(let i=0;i<241;i++){
  const s=sampleSlamCue(1+i*travel/241,maxR);
  assert.equal(s.state,'wave');
  assert.ok(s.radius>prev && s.radius<maxR && s.opacity>0 && s.opacity<=1);
  prev=s.radius;
}
near(sampleSlamCue(1.34,maxR).radius,2.601739130434782);
assert.throws(()=>sampleSlamCue(.3,NaN));
console.log('241 outward wave samples; exactly 1 s warning; no game logic.');
