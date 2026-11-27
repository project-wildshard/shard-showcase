import assert from 'node:assert/strict';
import { registerHooks, createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { realpathSync, readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { chargeCameraFeed } from './policy.mjs';

// No reference source lives in this repository. Supply a trusted local checkout
// of the pinned reference and a Node package directory with Three/Rapier.
const root = realpathSync(process.argv[2]);
const deps = createRequire(pathToFileURL(realpathSync(process.argv[3])+'/package.json'));
const threeURL = pathToFileURL(deps.resolve('three').replace(/three\.cjs$/, 'three.module.js')).href;
const pinned = {
  'src/core/camera.ts':'89632998089f21d16314e3246cfc3944e959ff79',
  'src/core/util.ts':'1737fa575a6bb8c6c684ce2cde5b8541402d27f3',
  'src/core/physics.ts':'2efb28822086e54d6ed951b8a479e341fd09658f',
  'src/systems/engage.ts':'9ba9403d3b4b0058ecc852d93464d81a1e15dfb5',
  'src/data/enemies.ts':'345d524891aa9d022a8c51bddc8c802ad05cc251'
};
for (const [rel, hash] of Object.entries(pinned)) {
  const b = readFileSync(root+'/'+rel);
  assert.equal(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex'),hash,rel);
}
const prefix = pathToFileURL(root+'/').href;
registerHooks({resolve(spec, context, next) {
  if (context.parentURL?.startsWith(prefix)) {
    if (spec === 'three') return next(threeURL,context);
    if (spec === '@dimforge/rapier3d-compat') return next(pathToFileURL(deps.resolve(spec)).href,context);
    if (spec.startsWith('.') && !spec.endsWith('.ts')) return next(spec+'.ts',context);
  }
  return next(spec,context);
}});
const THREE = await import(threeURL);
const { CameraRig } = await import(prefix+'src/core/camera.ts');
const { Engagement } = await import(prefix+'src/systems/engage.ts');
const referenceRevision = '3afcd880b397e9703e906a7e66b42e8447e59519';
const dt = 1 / 60;
const cases = [
  {id:'backstep', end:57, run:110},
  {id:'side-backstep', end:57, run:110, x:.44},
  {id:'short-backstep', end:24, run:110},
  {id:'escape', end:240, run:240},
  {id:'sprint', end:57, run:110, sprint:true},
  {id:'drag', end:57, run:110, drag:true},
  {id:'manual-clear', end:57, run:110, clear:true},
  {id:'no-tell', end:57, run:110, noTell:true},
  {id:'third-person-follow-off', end:57, run:110, autoFollow:false}
];
const rounded = n => +n.toFixed(4);
function run(s, protectedTell) {
 const cam = new THREE.PerspectiveCamera(64,402/874,.1,1000);
 const rig = new CameraRig(cam,{spherecast:()=>null,raycast:()=>null});
 rig.setAspect(402/874);
 rig.autoFollow = s.autoFollow ?? true;
 const target = {alive:true,aggro:true,pos:new THREE.Vector3(0,0,-6),height:1.8};
 const g={combat:{target,busy:false,aiming:false,stance:'melee'},mobs:{inCombat:1,list:[target]},player:{pos:new THREE.Vector3(), speed2d:0, moveHeading:null, rolling:false, sprinting:false},cameraRig:rig};
 const engage = new Engagement(g);
 const trace=[];
 let preframed=false, manual=false;
 for(let i=-30;i<s.run;i++){
  const active=i>=0&&i<s.end;
  if (s.clear && i===18) engage.clearTarget();
  const sprint=!!(s.sprint && active);
  const x=active?(s.x??0):0, y=active?-Math.sqrt(1-x*x):0;
  rig.setStick(x,y);
  const heading=active?rig.moveYaw+Math.atan2(-x,y)+Math.PI:null;
  const sp=active?(sprint?6.2:3.6):0;
  if(active){g.player.pos.x+=Math.sin(heading)*sp*dt;g.player.pos.z+=Math.cos(heading)*sp*dt;}
  Object.assign(g.player,{speed2d:sp,moveHeading:heading,sprinting:sprint});
  engage.update(dt);
  if(i===-1) preframed=engage.framed===target;
  const lookX=s.drag&&i>=30&&i<48?.06:0;
  if (lookX) manual=true;
  const aim=engage.framed;
  const normal={aimTarget:aim?.pos??null,aimHeight:aim?.height??0,flee:engage.flee};
  const feed=protectedTell ? chargeCameraFeed({
    target:g.combat.target,armedTarget:preframed?target:null,
    kind:'pallet-charge',startedAt:0,now:i/60,windingUp:!s.noTell&&i>=0&&i<57,
    stillHeld:active,autoFollow:rig.autoFollow,thirdPersonMelee:true,
    sprint,manualLookSinceStart:manual,cleared:!!s.clear&&i>=18,
  },normal) : normal;
  rig.update(dt,g.player.pos.clone().add(new THREE.Vector3(0,1,0)),{
   lookX,lookY:0,zoom:0,moveHeading:heading,speed:sp,...feed,latch:active,
   fovExtra:sprint?5:0,distMul:1
  });
  if(i<0)continue;
  cam.updateMatrixWorld();
  const point=target.pos.clone().add(new THREE.Vector3(0,1.25,0));
  const depth=point.clone().applyMatrix4(cam.matrixWorldInverse).z;
  const {x:nx,y:ny}=point.project(cam);
  trace.push({ms:Math.round((i+1)*1000/60),yaw:rounded(rig.yaw),heading:heading===null?null:rounded(Math.atan2(Math.sin(heading),Math.cos(heading))),
  cue:[rounded(nx),rounded(ny)], visible:depth<0&&Math.abs(nx)<=1&&Math.abs(ny)<=1, safe:depth<0&&Math.abs(nx)<=.8&&Math.abs(ny)<=.82,
  framed:!!feed.aimTarget,selected:g.combat.target===target,flee:rounded(feed.flee),lookX,hold:feed!==normal,
  camera:cam.position.toArray().map(rounded), rotation:cam.quaternion.toArray().map(rounded), fov:rounded(cam.fov),
  hero:g.player.pos.toArray().map(rounded)});
 }
 return trace;
}
const results=cases.map(s=>({case:s.id,baseline:run(s,false),candidate:run(s,true)}));
const summary=results.map(({case:id,...r})=>({id,...Object.fromEntries(Object.entries(r).map(([k,a])=>[k,{
  safe:a.slice(0,57).filter(f=>f.safe).length,visible:a.slice(0,57).filter(f=>f.visible).length,
  maxYaw:Math.round(Math.max(...a.slice(0,57).map(f=>Math.abs(f.yaw)))*180/Math.PI),
  off:a.find(f=>!f.visible)?.ms??null,flee:a.find(f=>f.flee>0)?.ms??null,
  drop:a.find(f=>!f.selected)?.ms??null,
  dragYaw:Math.round((a[47].yaw-a[29].yaw)*180/Math.PI)
 }]))}));
const pick=id=>results.find(r=>r.case===id);
const stat=id=>summary.find(r=>r.id===id);
for (const id of ['backstep','side-backstep']) {
  assert.ok(stat(id).baseline.visible<45);
  assert.equal(stat(id).candidate.safe,57);
}
assert.equal(stat('escape').baseline.drop,stat('escape').candidate.drop);
assert.equal(stat('escape').candidate.flee,967);
assert.equal(stat('drag').baseline.dragYaw,stat('drag').candidate.dragYaw);
assert.equal(pick('drag').candidate[30].hold,false);
assert.equal(pick('drag').candidate.slice(30).some(f=>f.hold),false);
for (const id of ['sprint','no-tell','third-person-follow-off'])
  assert.deepEqual(pick(id).baseline,pick(id).candidate,id);
const samples=Object.fromEntries(['backstep','side-backstep','drag','escape'].map(id=>[
  id,Object.fromEntries(['baseline','candidate'].map(k=>[k,[0,23,35,44,56,57,60].map(i=>pick(id)[k][i])]))
]));
const result = {referenceRevision,sourceGitBlobs:pinned,threeRevision:THREE.REVISION,
  viewport:[402,874],hz:60,windupMs:950,
  scope:'Reference CameraRig and Engagement, open-space scripted input and static tell anchor; no mobs, movement physics, HUD, or device.',
  summary,samples};
process.stdout.write(JSON.stringify(process.argv.includes('--full')?{...result,results}:result,null,2)+'\n');
