// This file is loaded with shoulder-envelope.mjs in the disposable replay.
// Camera presentation is applied only for draw, then restored before input.
export function installLiveShoulder(g,p,mob,f,h,draw,began){
 const cam=g.camera, rig=g.cameraRig, v=p.pos.clone();
 const ease=makeShoulderEnvelope();
 f.liveShoulder=[];
 let last=null;
 const basis=()=>rig.forward(v.clone()).toArray();
 const loc=node=>node.getWorldPosition(v.clone());
 const screen=point=>{
  const q=point.clone().project(cam);
  return [(q.x+1)*201,(1-q.y)*437];
 };
 const safe=(a,b)=>{
  const d=b.clone().sub(a),len=d.length();
  if(len<.0001)return true;
  d.multiplyScalar(1/len);
  return g.physics.spherecast(a,d,len,.24,0xffff0001)===null&&rig.occ.sweep(a,d,len,.24)===null;
 };
 const drawWith=(args,state,option)=>{
  const eye=cam.position.clone(),q=cam.quaternion.clone(),before=basis();
  try{
   if(option){
    cam.position.copy(state.adjusted);
    cam.quaternion.copy(state.adjustedRotation);
    cam.updateMatrixWorld(true);
   }
   draw(...args);
   const base=screen(loc(p.weaponModel.base)),tip=screen(loc(p.weaponModel.tip)),core=screen(loc(mob.rig.sockets.core));
   return {base,tip,core,camera:cam.position.toArray(),rotation:cam.quaternion.toArray()};
  }finally{
   cam.position.copy(eye); cam.quaternion.copy(q); cam.updateMatrixWorld(true);
   if(JSON.stringify(basis())!==JSON.stringify(before))throw Error('Touch basis moved');
  }
 };
 f.nativeDraw=(...args)=>{
  const frame=h.frame-began,tap=f.attack?.frame;
  if(!tap)return;
  const eye=cam.position.clone(),rot=cam.quaternion.clone();
  const time=(frame-tap)/60, look=!!g.input.lookIds?.size||
   Object.values(g.hud.acts).some(a=>a.ptr!==-1&&a.root.classList.contains('steer'));
  // Contact feedback can keep easing while the hero recovers. Never begin a
  // new shot without the existing native target and sword action.
  const engaged=g.combat.target===mob&&mob.alive&&(p.action==='sword1'||!!f.contact);
  const {weight,yielded}=ease({age:time,engaged,look,third:rig.view==='third'});
  const right=v.clone().set(1,0,0).applyQuaternion(rot);right.y=0;right.normalize();
  const adjusted=eye.clone().addScaledVector(right,.35*weight);adjusted.y+=.45*weight;
  let allowed=safe(eye,adjusted);
  if(weight&&last?.applied&&allowed)allowed=safe(last.adjusted,adjusted);
  if(!allowed)adjusted.copy(eye);
  const aim=loc(mob.rig.sockets.core), dir=q=>aim.clone().sub(q).normalize();
  const adjustedRotation=rot.clone().premultiply(rot.clone().setFromUnitVectors(dir(eye),dir(adjusted)));
  const applied=allowed&&weight>1e-6;
  last={frame,args,adjusted,adjustedRotation,applied};
  const shown=drawWith(args,last,true);
  f.liveShoulder.push({frame,time,look,yielded,applied,blocked:!allowed,engaged,weight,
   native:eye.toArray(),position:shown.camera,core:shown.core,span:Math.hypot(shown.tip[0]-shown.base[0],shown.tip[1]-shown.base[1]),
   basis:basis(),hp:[g.state.d.hp,mob.hp],action:p.action});
 };
 f.captureLive=option=>{
  if(last?.frame!==h.frame-began)throw Error('No matching native draw');
  const result=drawWith([g.scene,cam,0],last,option);
  return {frame:last.frame,option,...result,hp:[g.state.d.hp,mob.hp],basis:basis(),pose:p.action,sim:g.simTime};
 };
}

export async function captureLive(page,out){
 const rows=[];
 for(const option of [false,true]){
  const r=await page.evaluate(option=>coverFixture.captureLive(option),option);
  await page.screenshot({path:out+'/live-'+r.frame+'-'+(option?'composed':'stock')+'.png'});
  rows.push(r);
 }
 for(const k of ['frame','hp','basis','pose','sim'])
  if(JSON.stringify(rows[0][k])!==JSON.stringify(rows[1][k]))throw Error('Unmatched native lens: '+k);
 await page.evaluate(rows=>{(coverFixture.liveImages??=[]).push(rows);},rows);
}
