import * as T from 'three';

// Outdoor arena built from editable, batched scene geometry. Combat owns all collisions.
export function createBreakwaterDressing(scene,cover){
 const root=new T.Group();root.name='Signal Breakwater at blue hour';scene.add(root);
 let seed=0x9fd0c551;
 const rnd=()=>((seed=Math.imul(seed,1664525)+1013904223|0)>>>0)/4294967296;
 const mat=(color,roughness=.72,metalness=.15,extra={})=>new T.MeshStandardMaterial({color,roughness,metalness,...extra});
 const glow=color=>new T.MeshBasicMaterial({color});
 const mats={
  stone:mat(0x59666a), slate:mat(0x424f55), salt:mat(0x859395), moss:mat(0x526255,.93), deck:mat(0x334b54,.56,.32),
  ochre:mat(0x9b7442,.81), tide:mat(0x48595b,.49,.33),
  iron:mat(0x30434d,.48,.65), bronze:mat(0x966953,.54,.63), brass:mat(0xc5a46f,.46,.57),
  wine:mat(0x743b42,.53,.45), cream:mat(0xd0c2a0,.54,.27), lens:glow(0xffc380), cool:glow(0x82d7da),
  foam:glow(0x7a9ea2), ripple:mat(0x426f79,.49,.41)
 };
 const geom={
  box:new T.BoxGeometry(), oct:new T.CylinderGeometry(1,1,1,8),
  cone:new T.CylinderGeometry(.68,1,1,8), rock:new T.IcosahedronGeometry(1,0),
  ring:new T.TorusGeometry(1,.085,7,20)
 };
 const buckets=new Map(),scratch=new T.Object3D();
 function mark(shape,skin,scale,at,angles=[0,0,0]){
  const key=shape+'-'+skin;
  if(!buckets.has(key))buckets.set(key,{geo:geom[shape],mat:mats[skin],poses:[]});
  scratch.position.set(...at);scratch.scale.set(...scale);scratch.rotation.set(...angles);scratch.updateMatrix();
  buckets.get(key).poses.push(scratch.matrix.clone());
 }
 const box=(m,s,p,a)=>mark('box',m,s,p,a);
 const post=(m,r,h,p,a)=>mark('oct',m,[r,h,r],p,a);
 const boulder=(m,s,p,a)=>mark('rock',m,s,p,a);
 const torus=(m,r,p,a)=>mark('ring',m,[r,r,r],p,a);
 const cc=document.createElement('canvas');cc.width=cc.height=256;
 const ctx=cc.getContext('2d'),pixels=ctx.createImageData(256,256);
 for(let y=0;y<256;y++)for(let x=0;x<256;x++){
  const n=(rnd()-.5)*16+Math.sin(x*.095+y*.031)*3+Math.sin(y*.12+x*.017)*4;
  const i=(y*256+x)*4;
  pixels.data[i]=104+n;pixels.data[i+1]=114+n;pixels.data[i+2]=121+n;pixels.data[i+3]=255;
 }
 ctx.putImageData(pixels,0,0);
 for(let i=0;i<100;i++){
  const x=rnd()*256,y=rnd()*256;
  ctx.strokeStyle=i%3?'rgba(35,47,50,.22)':'rgba(196,207,196,.26)';
  ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+1+rnd()*5,y+rnd()*3);ctx.stroke();
 }
 const texture=new T.CanvasTexture(cc);texture.colorSpace=T.SRGBColorSpace;
 texture.wrapS=texture.wrapT=T.RepeatWrapping;texture.repeat.set(4,4);texture.anisotropy=4;
 const floor=new T.Mesh(new T.PlaneGeometry(22,22),mat(0xb7c2bf,.67,.26,{map:texture}));
 floor.rotation.x=-Math.PI/2;floor.position.y=-.008;root.add(floor);
 const water=new T.Mesh(new T.PlaneGeometry(122,122),mat(0x2b6476,.49,.36));
 water.rotation.x=-Math.PI/2;water.position.y=-1.05;root.add(water);
 box('slate',[22.1,1.02,22.1],[0,-.56,0]);
 for(const side of [-1,1]){
  for(let i=0;i<13;i++){
   const k=-9.9+i*1.65;
   box(i%3===0?'stone':'slate',[1.55,.25,.53],[k,.09,side*10.70]);
   box(i%4===0?'salt':'stone',[.55,.26,1.55],[side*10.70,.09,k]);
   boulder('slate',[1.05,.64,.78],[k,-.53,side*(11.5+rnd()*1.1)],[rnd(),rnd()*6,rnd()]);
   boulder('stone',[.75,.58,1.10],[side*(11.45+rnd()),-.65,k],[rnd(),rnd()*6,rnd()]);
   box('foam',[.65+rnd()*1.6,.012,.026],[k,-1.032,side*(13.2+rnd()*1.9)],[0,(rnd()-.5)*.4,0]);
  }
 }
 for(let i=0;i<96;i++){
  const x=(rnd()-.5)*65,z=(rnd()-.5)*70;
  if(Math.max(Math.abs(x),Math.abs(z))>12.6)
   box('ripple',[.4+rnd()*2.6,.008,.022+rnd()*.032],[x,-1.043,z],[0,(rnd()-.5)*.32,0]);
 }
 // Weathered tar renewals and painted turning guides; no raised collision.
 for(const [x,z,w,d] of [[-6.4,-7.65,5.6,3.4],[5.55,4.85,3.24,4.1],[-.50,7.85,4.38,2.09],[2.8,-5.4,3.32,2.1]]){
  box('tide',[w,.006,d],[x,-.003,z],[0,.032,0]);
  for(let i=0;i<14;i++){
   const rx=x+(rnd()-.5)*w*.92,rz=z+(rnd()-.5)*d;
   box(i%4?'deck':'stone',[rnd()*.20+.035,.003,rnd()*.24+.04],[rx,.001,rz],[0,rnd()*2,0]);
  }
 }
 for(const [x,z,sign] of [[-5.6,-1.8,1],[4.6,3.5,-1],[-4.2,6.8,1],[5.0,-5.26,-1]]){
  for(let i=0;i<5;i++)for(const v of [-1,1]){
   box(i%3?'ochre':'brass',[.065,.004,.55],[x+v*.185,.004,z+sign*i*.50],[0,v*sign*.58,0]);
  }
 }
 // A ruptured paving apron, not a repeated tile grid or a collision lip.
 for(const [x,z,l,a] of [[0,2.85,19.6,-.15],[-.6,-4.1,19.4,.11],[-5.15,.4,16.3,1.60],[4.68,-.18,16.8,1.57],[3.3,-7.7,8.0,-.29],[-3.2,7.4,7.3,.26]])
  box('slate',[l,.008,.027],[x,-.002,z],[0,a,0]);
 for(let i=0;i<68;i++){
  const sx=(i%2?1:-1)*(7.8+rnd()*2.6),z=(rnd()-.5)*20;
  box(i%3?'moss':'salt',[.07+rnd()*.54,.004,.03+rnd()*.18],[sx,.001,z],[0,rnd()*6.28,0]);
 }
 // Four original cover silhouettes; every rigid piece stays in its existing column.
 for(const [i,[x,z,r]] of cover.entries()){
  const at=(dx,y,dz)=>[x+dx,y,z+dz];
  post('slate',r,.14,at(0,.073,0));
  post('salt',r*.89,.09,at(0,.18,0));
  if(i===0){
   post('iron',r*.61,.81,at(0,.62,0));post('bronze',r*.76,.16,at(0,1.03,0));
   torus('brass',.23,at(0,1.31,0),[0,.48,0]);
   post('wine',r*.65,.10,at(0,.38,0));
  }else if(i===1){
   mark('cone','stone',[r*.81,.77,r*.81],at(0,.53,0));
   post('wine',r*.70,.20,at(0,.98,0));
   post('cream',r*.53,.14,at(0,1.13,0));
   post('lens',.095,.068,at(0,1.24,0));
  }else if(i===2){
   post('iron',r*.58,.69,at(0,.55,0));
   for(let k=0;k<3;k++)post(k%2?'brass':'bronze',r*(.77-k*.07),.092,at(0,.83+k*.114,0));
   box('cool',[.52,.05,.057],at(0,1.19,0));
  }else {
   mark('cone','wine',[r*.80,.83,r*.80],at(0,.59,0));
   box('cream',[r*.91,.25,r*.73],at(0,1.03,0),[0,.38,0]);
   box('cool',[r*.74,.079,.065],at(.08,1.08,r*.36),[0,.38,0]);
  }
 }
 // Salt-stained sea wall and signal tower, beyond the playable deck.
 for(let k=0;k<11;k++){
  const x=-8.6+k*1.61,z=-10.98+.20*Math.sin(k*.55);
  const high=k<3||k>7;
  box(k%3?'stone':'slate',[1.51,high?.86:.50,.79],[x,high?.39:.22,z],[0,0,(rnd()-.5)*.045]);
  box('salt',[1.54,.13,.87],[x,high?.865:.51,z]);
  if(k%3===0){post('iron',.17,.52,[x,1.15,z]);post('lens',.12,.085,[x,1.44,z]);}
 }
 const bx=-5.95,bz=-11.80;
 const shorten=([x,y,z])=>[x,y<.4?y:.4+(y-.4)*.41,z];
 const band=(name,r,h,p)=>post(name,r,h*(p[1]>.4?.41:1),shorten(p));
 const panel=(name,[w,h,d],p,a)=>box(name,[w,h*.41,d],shorten(p),a);
 const cast=(name,[w,h,d],p)=>mark('cone',name,[w,h*.41,d],shorten(p));
 band('slate',1.72,1.4,[bx,-.37,bz]);band('stone',1.33,.43,[bx,.52,bz]);
 cast('wine',[1.13,4.55,1.13],[bx,2.83,bz]);
 for(const y of [.95,3.2,4.88])band('bronze',y<2?1.07:.86,.14,[bx,y,bz]);
 panel('iron',[.53,1.18,.14],[bx,.99,bz+1.06]);
 panel('cool',[.125,.61,.09],[bx,2.62,bz+.97]);
 band('iron',1.14,.33,[bx,5.15,bz]);band('brass',1.07,.12,[bx,5.36,bz]);
 band('lens',.63,.86,[bx,5.84,bz]);
 for(let i=0;i<8;i++){
  const a=i*Math.PI/4;panel('iron',[.086,1.14,.10],[bx+.72*Math.cos(a),5.87,bz+.72*Math.sin(a)],[0,-a,0]);
 }
 cast('iron',[1.17,.63,1.17],[bx,6.55,bz]);band('bronze',.15,.68,[bx,7.08,bz]);
 // Far rocks and lantern poles give the pier a readable edge without adding hazards.
 for(let i=0;i<15;i++){
  const x=-19+i*2.75,z=-20+Math.sin(i*.49)*3;
  boulder(i%4?'slate':'moss',[1.2+rnd()*1.1,.75+rnd()*2.45,1.25+rnd()*1.8],[x,-.77,z],[.07,rnd()*6,.12]);
 }
 for(const [x,z] of [[-10.83,-7.1],[10.89,-8.9],[10.89,2.6],[-10.83,7.9]]){
  post('iron',.13,2.28,[x,1.15,z]);box('bronze',[.67,.11,.15],[x+.23,2.27,z]);
  box('lens',[.23,.10,.16],[x+.51,2.15,z]);box('iron',[.28,.068,.20],[x+.51,2.27,z]);
 }
 let instances=0;
 for(const {geo,mat,poses} of buckets.values()){
  const batch=new T.InstancedMesh(geo,mat,poses.length);
  poses.forEach((p,i)=>batch.setMatrixAt(i,p));batch.instanceMatrix.needsUpdate=true;batch.computeBoundingSphere();root.add(batch);
  instances+=poses.length;
 }
 // Local warmth without washing out the threat colors in the combat center.
 const lamp=new T.PointLight(0xffb56a,37,10,2);
 lamp.position.set(bx,2.95,bz+.66);root.add(lamp);
 return {batches:buckets.size,instances,coverCount:cover.length,lightPools:0,practicalLights:1};
}
