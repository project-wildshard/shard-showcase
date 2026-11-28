import * as T from 'three';
// Original Forge Yard visual kit. Only ARENA and COVER from arena.mjs own collision.
export function createFoundryDressing(scene,cover){
 const root=new T.Group();root.name='Foundry evening shift';scene.add(root);
 const standard=(color,metalness=.36,roughness=.53,options={})=>new T.MeshStandardMaterial({color,metalness,roughness,...options});
 let seed=0xafed58c3;
 const random=()=>{seed=Math.imul(seed,1664525)+1013904223|0;return(seed>>>0)/4294967296;};
 function canvasTexture(w,h,paint){
  const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
  const g=canvas.getContext('2d');paint(g,w,h);
  const t=new T.CanvasTexture(canvas);t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;return t;
 }
 const slagTex=canvasTexture(512,512,(g,w,h)=>{
  const img=g.createImageData(w,h),data=img.data;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const raw=5*Math.sin(x*.048+Math.sin(y*.026)*1.8)*Math.sin(y*.053)
    +4*Math.sin((y+x*.15)*.032)*Math.cos(x*.055)+11*(random()-.5);
   const i=(y*w+x)*4;data[i]=82+raw;data[i+1]=88+raw;data[i+2]=91+raw;data[i+3]=255;
  }
  g.putImageData(img,0,0);
  for(let i=0;i<310;i++){
   const x=random()*w,y=random()*h;
   g.strokeStyle=i%3?'rgba(19,21,22,.12)':'rgba(177,167,148,.10)';
   g.lineWidth=.4+random()*1.5;
   g.beginPath();g.moveTo(x,y);g.lineTo(x+3+random()*19,y+random()*2-1);g.stroke();
  }
  for(let i=0;i<16;i++){
   const x=random()*w,y=random()*h,r=17+random()*34;
   const s=g.createRadialGradient(x,y,2,x,y,r);s.addColorStop(0,'rgba(15,19,14,.16)');s.addColorStop(1,'rgba(24,19,14,0)');
   g.fillStyle=s;g.fillRect(x-r,y-r,r*2,r*2);
  }
  for(let i=0;i<33;i++){
   const x=random()*w,y=random()*h,rx=5+random()*30,ry=4+random()*15;
   g.fillStyle=i%3?'rgba(140,96,69,.085)':'rgba(45,59,58,.10)';
   g.beginPath();g.ellipse(x,y,rx,ry,random()*Math.PI,0,Math.PI*2);g.fill();
  }
 });
 slagTex.wrapS=slagTex.wrapT=T.RepeatWrapping;slagTex.repeat.set(4.05,4.05);
 const floor=new T.Mesh(new T.PlaneGeometry(26,26),standard(0xc9c3b8,.23,.81,{map:slagTex}));
 floor.rotation.x=-Math.PI/2;floor.position.y=-.006;root.add(floor);
 const dampTex=canvasTexture(96,96,(g,w,h)=>{
  const radial=g.createRadialGradient(w/2,h/2,2,w/2,h/2,w/2);
  radial.addColorStop(0,'rgba(27,22,18,.29)');radial.addColorStop(.5,'rgba(32,25,23,.17)');
  radial.addColorStop(1,'rgba(32,25,23,0)');g.fillStyle=radial;g.fillRect(0,0,w,h);
 });
 const damp=new T.MeshBasicMaterial({map:dampTex,transparent:true,depthWrite:false});
 const spill=new T.Mesh(new T.PlaneGeometry(90,90),standard(0x283438,.08,.93));
 spill.rotation.x=-Math.PI/2;spill.position.y=-.032;root.add(spill);
 const mats={
  steel:standard(0x303f42,.62,.48),edge:standard(0x798489,.72,.43),
  void:standard(0x172428,.21,.77),basalt:standard(0x424543,.21,.83),
  teal:standard(0x255359,.53,.50),tealDark:standard(0x1e3f46,.54,.56),
  copper:standard(0x855237,.59,.46),oxide:standard(0x734231,.44,.59),
  ochre:standard(0x936535,.42,.67),paint:standard(0xb98347,.17,.77),
  heat:standard(0x8e5030,.18,.44,{emissive:0xd67834,emissiveIntensity:.48}),
  cyan:standard(0x376e68,.22,.42,{emissive:0x4da39a,emissiveIntensity:.68}),
  wet:standard(0x596268,.58,.44)
 };
 const box=new T.BoxGeometry(1,1,1),round=new T.CylinderGeometry(1,1,1,12),bevel=new T.CylinderGeometry(.84,1,1,12);
 const ring=new T.TorusGeometry(1,.10,7,20),sphere=new T.SphereGeometry(1,10,7);
 const entries=new Map(),o=new T.Object3D();
 function add(geo,mat,sz,pos,rot=[0,0,0]){
  if(![...sz,...pos,...rot].every(Number.isFinite))throw Error('Non-finite foundry fixture');
  const key=geo.uuid+mat;
  if(!entries.has(key))entries.set(key,{geo,mat,matrices:[]});
  o.position.set(...pos);o.scale.set(...sz);o.rotation.set(...rot);o.updateMatrix();
  entries.get(key).matrices.push(o.matrix.clone());
 }
 const B=(m,a,p,r)=>add(box,m,a,p,r);
 const C=(m,r,h,p)=>add(round,m,[r,h,r],p);
 const A=(m,r,h,p)=>add(bevel,m,[r,h,r],p);
 const Tori=(m,r,p,rx=0)=>add(ring,m,[r,r,r],p,[rx,0,0]);
 const X=(m,r,h,p)=>add(round,m,[r,h,r],p,[0,0,Math.PI/2]);
 const Z=(m,r,h,p)=>add(round,m,[r,h,r],p,[Math.PI/2,0,0]);
 // Recessed, graphic rail lane, not a combat obstacle.
 for(const x of [-.44,.44]){
  B('void',[.20,.015,19.5],[x,.003,-.06]);
  B('wet',[.039,.010,19.5],[x,.012,-.06]);
 }
 for(let z=-9.1;z<9.1;z+=1.25)B('steel',[.97,.011,.072],[0,.006,z]);
 for(const x of [-5.65,5.65]){
  for(let z=-9.2;z<9.2;z+=1.16)B('ochre',[.100,.01,.56],[x,.002,z],[0,x>0?.27:-.27,0]);
  B('void',[.17,.008,19.3],[x+Math.sign(x)*.29,.002,0]);
  for(let z=-8.85;z<9.4;z+=.18)B('edge',[.115,.008,.018],[x+Math.sign(x)*.29,.007,z]);
 }
 // Saw-cut sections and a small number of broad plates, not a uniform checkerboard.
 for(const [x,z,w,d] of [[-6.6,-4.95,5.8,.024],[6.1,-3.4,5.9,.026],[-6.6,3.1,5.8,.022],[4.75,4.8,5.6,.028],
  [-6.28,-1.0,.024,8.0],[6.75,1.3,.024,7.75],[-2.05,5.4,.021,6.80],[3.35,-6.7,.023,4.22]]){
  B('void',[w,.009,d],[x,.001,z]);
 }
 for(const [x,z,w,d] of [[-7.65,7.6,2.12,2.66],[8.0,-6.9,2.0,1.92],[-7.75,-8.4,2.3,1.52]]){
  B('wet',[w,.012,d],[x,.002,z]);
  for(const dx of [-w*.4,w*.4])for(const dz of [-d*.38,d*.38])C('void',.033,.012,[x+dx,.014,z+dz]);
 }
 // All collision-bearing silhouettes remain inside the existing four circular footprints.
 const covers=['Charge crucible','Strip spool','Control island','Quench cap'];
 for(const [i,[x,z,r]] of cover.entries()){
  const at=(dx,y,dz)=>[x+dx,y,z+dz];
  const shadow=new T.Mesh(new T.PlaneGeometry(r*3.65,r*3.25),damp);
  shadow.rotation.x=-Math.PI/2;shadow.position.set(x+.16,.001,z+.04);root.add(shadow);
  C('void',r,.011,at(0,.005,0));C('steel',r*.98,.17,at(0,.095,0));
  C('copper',r*.92,.058,at(0,.17,0));
  if(i===0){
   C('oxide',r*.78,.77,at(0,.53,0));A('steel',r*.88,.23,at(0,1.00,0));
   C('void',r*.66,.036,at(0,1.13,0));
   for(const [cx,cz] of [[.14,.17],[-.18,-.12],[.0,-.25],[.14,-.21],[-.20,.19],[-.04,.03]]){
    A('oxide',r*.12,.085,at(r*cx,1.169,r*cz));C('heat',r*.041,.018,at(r*(cx+.02),1.220,r*cz));
   }
   Tori('copper',r*.74,at(0,1.11,0),Math.PI/2);
   for(let j=0;j<10;j++){const a=j*Math.PI/5;B('edge',[.097,.49,.084],at(r*.77*Math.sin(a),.55,r*.77*Math.cos(a)),[0,a,0]);}
  }else if(i===1){
   A('tealDark',r*.78,.19,at(0,.285,0));C('copper',r*.53,.74,at(0,.69,0));
   for(let y=.40;y<1.04;y+=.109)Tori('edge',r*.58,at(0,y,0),Math.PI/2);
   C('teal',r*.86,.13,at(0,1.10,0));C('void',r*.61,.044,at(0,1.18,0));
  }else if(i===2){
   A('teal',r*.82,.92,at(0,.62,0));C('steel',r*.76,.092,at(0,1.12,0));
   for(const s of [-1,1]){
    B('steel',[r*.62,.38,.046],at(0,.65,s*r*.69));
    for(let j=-2;j<=2;j++)B('edge',[.046,.24,.044],at(j*.081,.655,s*r*.717));
   }
   B('void',[r*.61,.033,r*.31],at(-.035,1.176,0));
   for(let j=-2;j<=2;j++)B(j<1?'cyan':'heat',[.044,.032,.088],at(j*.075,1.201,0));
  }else{
   C('tealDark',r*.74,.49,at(0,.41,0));A('oxide',r*.92,.33,at(0,.83,0));
   C('steel',r*.67,.063,at(0,1.03,0));C('copper',r*.19,.087,at(0,1.09,0));
   for(let a=0;a<6;a++)C('edge',.038,.035,at(Math.sin(a*Math.PI/3)*r*.55,1.08,Math.cos(a*Math.PI/3)*r*.55));
  }
 }
 // Far maintenance wall and side return. Keep player-side edges low for the portrait chase camera.
 for(let i=0;i<7;i++){
  const x=-9+i*3;
  B('basalt',[2.88,1.0,.67],[x,.48,-10.95]);
  B('steel',[2.81,.14,.75],[x,.97,-10.93]);
  B('tealDark',[2.80,3.7,.42],[x,2.73,-11.36]);
  for(let k=-2;k<=2;k++)B('teal',[.27,3.25,.06],[x+k*.50,2.65,-11.11]);
  for(let y=1.44;y<4.6;y+=1.06)B('steel',[2.83,.098,.083],[x,y,-11.03]);
  B('steel',[2.72,.62,.38],[x,.31,10.74]);
  B('ochre',[2.55,.074,.46],[x,.62,10.74]);
 }
 for(let z=-8;z<=8;z+=4){
  B('basalt',[.57,1.0,3.77],[-10.92,.48,z]);
  B('steel',[.66,.14,3.68],[-10.91,.97,z]);
  B('tealDark',[.42,2.85,3.63],[-11.22,2.33,z]);
  for(let j=-3;j<=3;j++)B('teal',[.06,2.56,.23],[-10.98,2.30,z+j*.47]);
  B('steel',[.43,.72,3.65],[10.78,.35,z]);
  B('ochre',[.49,.07,3.45],[10.78,.73,z]);
 }
 for(const x of [-9.9,-5.7,2.9,9.9]){
  B('steel',[.43,5.99,.51],[x,2.99,-10.67]);
  B('oxide',[.69,.24,.86],[x,.16,-10.61]);
  B('teal',[.66,.31,.64],[x,5.89,-10.65]);
  B('void',[.69,.21,.29],[x,3.85,-10.27]);
  B('heat',[.41,.055,.034],[x,3.86,-10.09]);
  B('void',[.37,.24,.21],[x,1.89,-10.39]);B('copper',[.41,.064,.224],[x,2.009,-10.39]);
  B('heat',[.229,.127,.033],[x,1.901,-10.255]);
  for(const s of [-1,1])B('steel',[.04,.158,.026],[x+s*.082,1.895,-10.22]);
 }
 // Narrow gate frame, rolled shutters and service gantries behind the low combat fence.
 B('void',[4.20,4.9,.70],[-1.40,2.59,-10.96]);
 for(let i=0;i<13;i++)B(i%3===0?'steel':'tealDark',[3.67,.276,.11],[-1.40,1.07+i*.28,-10.55]);
 for(const v of [-3.44,.62]){
  B('oxide',[.30,4.50,.25],[v,2.50,-10.39]);B('edge',[.077,4.25,.12],[v+.14,2.54,-10.23]);
  B('heat',[.08,.24,.034],[v,3.85,-10.23]);
 }
 B('copper',[4.23,.42,.45],[-1.4,4.76,-10.42]);
 B('steel',[22.9,.55,.82],[0,6.18,-11.32]);
 B('oxide',[22.8,.12,.92],[0,5.94,-11.32]);
 for(let x=-10;x<=10;x+=1.1)B('edge',[.09,.63,.07],[x,6.35,-10.86],[0,0,.45]);
 for(const [x,z] of [[-9,-13],[6.9,-14.4],[-6,-18],[8,-20],[1.5,-21]]){
  C('tealDark',1.1,6.8,[x,3.2,z]);A('steel',1.15,.4,[x,6.75,z]);
  for(const y of [1.0,3.15,5.55])C('copper',1.17,.10,[x,y,z]);
  C('void',.47,4.6,[x,8.8,z]);C('oxide',.57,.21,[x,11.08,z]);
  B('steel',[.13,6.0,.22],[x-.63,3.12,z+1.05]);
  B('steel',[.13,6.0,.22],[x+.63,3.12,z+1.05]);
  for(let y=.5;y<6.2;y+=.52)X('edge',.026,1.19,[x,y,z+1.16]);
 }
 for(const y of [1.6,4.97,5.29]){
  X(y<2?'teal':'copper',.11,20.6,[0,y,-10.29]);
  for(let x=-9.7;x<=10;x+=2.82)X('edge',.151,.094,[x,y,-10.29]);
 }
 // Outside the arena: coiled hose, furnace hoods and long rear pipes.
 for(const x of [-7.8,5.8]){
  A('oxide',.75,1.16,[x,.62,-12.35]);C('void',.56,.58,[x,1.2,-12.33]);
  B('heat',[.62,.065,.24],[x,1.55,-12.34]);
  Z('copper',.19,3.68,[x,4.8,-13.82]);
  add(sphere,'oxide',[.35,.34,.35],[x,4.8,-11.95]);
 }
 const stats={instances:0,batches:0,coverCount:covers.length,collision:'visual only',floorTexture:[512,512]};
 for(const {geo,mat,matrices} of entries.values()){
  const mesh=new T.InstancedMesh(geo,mats[mat],matrices.length);
  matrices.forEach((m,i)=>mesh.setMatrixAt(i,m));
  mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();root.add(mesh);
  stats.instances+=matrices.length;stats.batches++;
 }
 function light(color,intensity,distance,x,y,z){
  const l=new T.PointLight(color,intensity,distance,2);l.position.set(x,y,z);root.add(l);
 }
 light(0xff8a4d,39,9,-3.35,3.35,-3.85);
 light(0x7ee0ef,17,8,6.4,4.7,2.66);
 return stats;
}
