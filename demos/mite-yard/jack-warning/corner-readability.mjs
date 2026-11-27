// Read-only rig probes and reversible presentation experiments, pinned to the
// stock corner replay. The screen marker is the engine's FX origin, not armor.
export function installReadability(g,p,mob,f,h,draw,began){
 const fx=g.fx, pool=fx.add, recipe=fx.play.bind(fx), emit=fx.emit.bind(fx);
 const tag=new Uint8Array(pool.life.length);
 pool.all.push(tag); // follow particles if the engine compacts its pool
 let sequence=0;
 f.blade=[];
 const project=v=>{
  const q=v.clone().project(g.camera);
  return [(q.x+1)*201,(1-q.y)*437,q.z];
 };
 fx.play=(name,...args)=>{
  if(name!=='hit.blade')return recipe(name,...args);
  const prior=sequence;sequence=1;
  f.impact={world:[args[0].x,args[0].y,args[0].z],power:args[3]};
  try{return recipe(name,...args);}finally{sequence=prior;}
 };
 fx.emit=(...args)=>{
  const before=pool.n;
  const res=emit(...args);
  tag.fill(0,before,pool.n);
  // In the pinned hit.blade recipe, the second emission is the crescent.
  if(sequence){
   if(sequence===1||sequence===2){
    if(pool.n-before!==1)throw Error('Expected one flash / cut particle');
    tag[before]=sequence;
   }
   sequence++;
  }
  return res;
 };
 const v=p.pos.clone();
 const loc=node=>node.getWorldPosition(v.clone());
 const blade=()=>{
  const base=loc(p.weaponModel.base),tip=loc(p.weaponModel.tip);
  const core=loc(mob.rig.sockets.core),weak=loc(mob.rig.sockets.weak);
  const result={base:base.toArray(),tip:tip.toArray(),basePx:project(base),tipPx:project(tip),
   corePx:project(core),eyePx:project(weak),tipDelta:null,fxOriginDistance:null};
  if(f.blade.length){
   result.tipDelta=tip.distanceTo(v.clone().fromArray(f.blade.at(-1).tip));
  }
  if(f.impact){
   const o=v.clone().fromArray(f.impact.world),d=tip.clone().sub(base);
   const t=Math.max(0,Math.min(1,o.clone().sub(base).dot(d)/Math.max(1e-9,d.lengthSq())));
   result.fxOriginDistance=o.distanceTo(base.clone().addScaledVector(d,t));
   result.impactPx=project(o);
  }
  return result;
 };
 f.renderEvidence=(mode)=>{
  if(!['stock','armor','tight','stroke','stock-repeat'].includes(mode))throw Error('Invalid effect mode');
  const originals=mob.rig.materials.map(m=>m.flash.value.w);
  const ids=Array.from({length:pool.n},(_,i)=>i);
  const live=purpose=>ids.filter(i=>tag[i]===purpose&&pool.aCol[i*4+3]>0);
  const cuts=live(2),flashes=live(1);
  if(cuts.length!==1||flashes.length!==1||!originals.some(x=>x>.8))throw Error('Expected stock body flash and one live cut crescent');
  const i=cuts[0]*4+3,size=pool.aPos[i],alpha=pool.aCol[i];
  const j=flashes[0]*4+3,flashSize=pool.aPos[j],flashAlpha=pool.aCol[j];
  const rb=fx.ribbons, trail=[];
  for(let q=0;q<rb.w*2;q++)if(rb.S[q*4]===g.combat.trail?.look.row&&rb.C[q*4+3]>0)trail.push([q*4+3,rb.C[q*4+3]]);
  if(!trail.length)throw Error('No live sword ribbon detected');
  const ribbonDirty=()=>{rb.mesh.geometry.getAttribute('aCol').needsUpdate=true;};
  const update=()=>{for(const k of ['iPos','iCol'])pool.mesh.geometry.getAttribute(k).needsUpdate=true;};
  let result;
  try{
   if(mode==='armor'||mode==='tight'||mode==='stroke')mob.rig.materials.forEach(m=>{m.flash.value.w=Math.min(m.flash.value.w,.22);});
   if(mode==='tight'||mode==='stroke'){pool.aPos[i]=.62*size;pool.aCol[i]=.68*alpha;update();}
   if(mode==='stroke'){
    pool.aPos[j]=.60*flashSize;pool.aCol[j]=.65*flashAlpha;update();
    for(const [k,v] of trail)rb.C[k]=.50*v;
    ribbonDirty();
   }
   draw(g.scene,g.camera,0);
   result={mode,frame:h.frame-began,pose:p.action,actionTime:p.actionT,sim:g.simTime,hp:[g.state.d.hp,mob.hp],
    camera:g.camera.position.toArray(),rotation:g.camera.quaternion.toArray(),lens:g.camera.fov,
    sampled:blade(),bodyFlash:mob.rig.materials.map(m=>m.flash.value.w),crescent:[pool.aPos[i],pool.aCol[i]],
    centralFlash:[pool.aPos[j],pool.aCol[j]],trailVertices:trail.length,trailPeak:Math.max(...trail.map(([k])=>rb.C[k]))};
  }finally{
   mob.rig.materials.forEach((m,j)=>{m.flash.value.w=originals[j];});
   if(mode==='tight'||mode==='stroke'){pool.aPos[i]=size;pool.aCol[i]=alpha;update();}
   if(mode==='stroke'){
    pool.aPos[j]=flashSize;pool.aCol[j]=flashAlpha;update();
    for(const [k,v] of trail)rb.C[k]=v;
    ribbonDirty();
   }
  }
  return result;
 };
 return {sample:r=>f.blade.push({frame:r.frame,action:r.action,...blade()})};
}

export async function captureReadability(page,out){
 for(const mode of ['stock','armor','tight','stroke','stock-repeat']){
  const row=await page.evaluate(mode=>coverFixture.renderEvidence(mode),mode);
  await page.screenshot({path:out+'/light-'+mode+'.png'});
  await page.evaluate(row=>{(coverFixture.visuals??=[]).push(row);},row);
 }
 const rows=await page.evaluate(()=>coverFixture.visuals);
 for(const row of rows.slice(1))for(const k of ['frame','pose','actionTime','sim','hp','camera','rotation','lens'])
  if(JSON.stringify(row[k])!==JSON.stringify(rows[0][k]))throw Error('Unmatched rendering: '+k);
}
