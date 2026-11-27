import assert from 'node:assert/strict';
import { realpathSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { registerHooks, createRequire } from 'node:module';
import { join, dirname } from 'node:path';
import { pathToFileURL } from 'node:url';
import { configure, bindAdapter } from './rig-reader.mjs';
import { pickSwordContactPose } from './contact-after-pose.mjs';

const checkout=realpathSync(process.argv[2]);
const depsFile=join(realpathSync(process.argv[3]),'package.json');
const deps=createRequire(depsFile);
const threeDir=dirname(dirname(deps.resolve('three')));
const threeURL=pathToFileURL(join(threeDir,'build/three.module.js')).href;
const load=name=>name==='three'?import(threeURL):import(pathToFileURL(deps.resolve(name)).href);
const root=pathToFileURL(checkout+'/').href;
const adapter=new URL('./rig-reader.mjs',import.meta.url).href;
const names = [
  'src/core/util.ts','src/data/moves.ts','src/gfx/models.ts',
  ...['rig','fit','weapons','anim','types','ik','fpview','shootpose','ribbon','kits'].map(n=>'src/entities/humanoid/'+n+'.ts'),
  'public/models/rook.glb','public/models/swords.glb'
];
const pin={
  "src/core/util.ts": "1737fa575a6bb8c6c684ce2cde5b8541402d27f3",
  "src/data/moves.ts": "c1f32d8674e37613de387dfae8409bfcd2cea127",
  "src/gfx/models.ts": "9aa9413ac093eea4ac0fc39599a90acb97c40c48",
  "src/entities/humanoid/rig.ts": "05af0544e4935182803e3cfa930d4d1fadc15759",
  "src/entities/humanoid/fit.ts": "7608b9713f18cd7ad620a9b6dd5f84ba18692655",
  "src/entities/humanoid/weapons.ts": "6a91651e08a6c06cfc208714075f01e37cec4ca9",
  "src/entities/humanoid/anim.ts": "6036eddeb184202728a1197770be971b5c942d6d",
  "src/entities/humanoid/types.ts": "6288ffc443fda2bb9ab4b5c584441f424773f086",
  "src/entities/humanoid/ik.ts": "03ee709bd94761025d3b0b56a681b9f841223026",
  "src/entities/humanoid/fpview.ts": "842bd6828888c2545c35bbfa77dd756c01e33a02",
  "src/entities/humanoid/shootpose.ts": "eafb0d6c88cd6e57f6d2fe3117c867497270b978",
  "src/entities/humanoid/ribbon.ts": "3e4b38c68ca25ae115d20cc65591f7458d68d8c2",
  "src/entities/humanoid/kits.ts": "8363db2ed4789be46c6cd8ecc224230dac912f8b",
  "public/models/rook.glb": "58a81ae05e6a063f17855b68fcfee24fb21f8706",
  "public/models/swords.glb": "a6e064883bc1d6145c40c2efa64932d1ba793c1f"
};
for(const p of names){
  const b=readFileSync(join(checkout,p));
  assert.equal(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex'),pin[p],p);
}
registerHooks({resolve(s,c,next){
  if(c.parentURL?.startsWith(root)&&s.startsWith('.')&&!s.endsWith('.ts')){
    const url=new URL(s,c.parentURL).href;
    if(/\/gfx\/(models|material|textures)$/.test(url))return next(adapter,c);
    return next(url+'.ts',c);
  }
  if(s==='three'&&(c.parentURL?.startsWith(root)||c.parentURL===adapter))return next(threeURL,c);
  return next(s,c);
}});
const THREE=await load('three');
await configure(checkout,load,THREE,threeDir);
bindAdapter();
const {makeHumanoid}=await import(root+'src/entities/humanoid/rig.ts');
const {makeWeaponModel}=await import(root+'src/entities/humanoid/weapons.ts');
const {SWORD}=await import(root+'src/data/moves.ts');
const p0={locomotion:'ground',time:0,speed:0,vy:0,lookYaw:0,lookPitch:0,landT:99,lean:0,rollT:0,action:null,actionT:0,weapon:'sword',drawn:true,aimPitch:0,moveX:0,moveZ:0,climbPhase:0,fp:0,jumpT:99,settleT:99};
const round=x=>+x.toFixed(5);
const seed = 293;
function run(s,hz,wind,poseLag){
  // Reference animator uses random idle phase, blink and glance. Keep the
  // two replay paths strictly paired; this is an isolated Node process.
  const originalRandom=Math.random;
  let state=seed;
  Math.random=()=>((state=(1664525*state+1013904223)>>>0)/4294967296);
  try { return runPose(s,hz,wind,poseLag); }
  finally { Math.random=originalRandom; }
}
function runPose(s,hz,wind,poseLag){
  const rig=makeHumanoid({kind:'hero'}),blade=makeWeaponModel('shop_blade');
  rig.setWeapon(blade);
  const p={...p0}; let lastT=s.from??0,t=lastT;
  for(let i=0;i<hz/2;i++){p.time+=1/hz;rig.update(1/hz,p);}
  const trace=[];
  for(let i=1;t<1&&i<800;i++){
    lastT=t;
    t+=1/(hz*s.dur)*(lastT<s.hitAt?wind:1);
    p.time+=1/hz;
    p.action=s.anim;
    p.actionT=Math.min(1,poseLag?lastT:t);
    rig.update(1/hz,p);
    const start=blade.base.getWorldPosition(new THREE.Vector3()),tip=blade.tip.getWorldPosition(new THREE.Vector3());
    if(![...start,...tip].every(Number.isFinite))throw new Error('nonfinite');
    trace.push({ms:round(i*1000/hz),actionT:round(p.actionT),hit:lastT<s.hitAt&&t>=s.hitAt,
      start:start.toArray().map(round),tip:tip.toArray().map(round)});
  }
  return trace;
}
const out=[];
for(const s of [SWORD.light[0],SWORD.light[1],SWORD.light[2],SWORD.heavy,SWORD.counter])for(const hz of [30,60,120])for(const wind of [1,.65]){
  const a=run(s,hz,wind,true),b=run(s,hz,wind,false),i=a.findIndex(f=>f.hit),o=a[i],n=b[i];
  assert.equal(a.length,b.length);
  assert.equal(b.findIndex(f=>f.hit),i);
  assert.equal(o.ms,n.ms);
  const hit={id:1,weaponEpoch:1,weapon:'sword',source:'melee',damageDealt:1,tick:i,action:s.anim,actionT:n.actionT};
  const feed=f=>({tick:i,weaponEpoch:1,action:s.anim,actionT:f.actionT,base:f.start,tip:f.tip});
  assert.equal(pickSwordContactPose(hit,feed(o)),null);
  assert.deepEqual(pickSwordContactPose(hit,feed(n)),{id:1,base:n.start,tip:n.tip});
  assert.equal(pickSwordContactPose({...hit,damageDealt:0},feed(n)),null);
  assert.ok(Math.abs(new THREE.Vector3(...n.tip).distanceTo(new THREE.Vector3(...n.start)) - Math.hypot(.83,.029))<.001);
  const d=Math.hypot(...n.tip.map((x,i)=>x-o.tip[i]));
  out.push({move:s.anim,hz,wind,i,ms:o.ms,old:o,new:n,tipDelta:round(d),baseDelta:round(Math.hypot(...n.start.map((x,i)=>x-o.start[i]))),...(hz===60&&wind===1?{arc:b.slice(i-3,i+4)}:{})});
}
assert.equal(out.length,30);
console.log(JSON.stringify({
  revision:'3afcd880b397e9703e906a7e66b42e8447e59519',sourceGitBlobs:pin,threeRevision:THREE.REVISION,seed,
  method:'Pinned Rook rig, animator and Shop Blade base/tip sockets with decoded source bones. Fixed root, deterministic simulated swing phase. Material and weapon visibility adapter; no GPU, render, hitbox, root motion, or combat runtime.',
  cases:out,
},null,2));
