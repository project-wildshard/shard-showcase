// Three original shared foundry modules. Local primitives use meters.
export const FOUNDRY_MODULE_EXTENTS=[
 {id:'pressure-manifold',x:-6.65,z:-11.34,zMax:-10.67},
 {id:'counterweight-shutter',x:-1.40,z:-11.17,zMax:-10.55},
 {id:'quench-manifold',x:4.32,z:-11.34,zMax:-10.66}
];
export function addFoundryWallKit({B,C,X,Z,Tori}){
 const [pressure,shutter,quench]=FOUNDRY_MODULE_EXTENTS;
 // Raised-pressure instrument: two copper routes converge on the gauge cage.
 {
  const {x,z}=pressure;
  const at=(a,b,c=0)=>[x+a,b,z+c];
  B('void',[2.05,1.92,.20],at(0,1.82,.12));
  for(const s of [-1,1]){
   B('steel',[.125,1.98,.29],at(s*1.02,1.82,.14));
   C('copper',.12,1.48,at(s*.64,1.76,.33));
   X('edge',.14,.36,at(s*.47,2.50,.34));
   for(const y of [1.14,2.28])C('steel',.166,.085,at(s*.64,y,.33));
   X('copper',.10,.24,at(s*.69,1.04,.34));
  }
  Z('steel',.43,.23,at(0,2.36,.34));Z('edge',.373,.092,at(0,2.36,.48));
  Z('void',.317,.038,at(0,2.36,.537));
  Tori('copper',.323,at(0,2.36,.577));
  for(let i=0;i<7;i++){
   const a=(i-3)*Math.PI/6;
   B(i>=5?'heat':'edge',[.034,.077,.023],at(.249*Math.sin(a),2.36+.249*Math.cos(a),.568),[0,0,-a]);
  }
  B('heat',[.041,.239,.024],at(.066,2.425,.577),[0,0,-.73]);
  Z('edge',.042,.038,at(0,2.36,.607));
  B('copper',[.52,.24,.23],at(0,1.4,.27));B('heat',[.286,.065,.020],at(0,1.4,.400));
 }
 // Wide fire shutter: overlapping lamellae, tapered sides and two counterweights.
 {
  const {x,z}=shutter;
  const at=(a,b,c=0)=>[x+a,b,z+c];
  B('void',[4.23,4.80,.30],at(0,2.5,.09));
  for(let i=0;i<12;i++){
   const y=.91+i*.282;
   B(i===0?'copper':i%3===0?'steel':'tealDark',[3.38,.245,.16],at(0,y,.28));
   B('edge',[3.38,.028,.028],at(0,y-.095,.373));
  }
  for(const s of [-1,1]){
   B('copper',[.31,4.41,.24],at(s*1.88,2.57,.25));
   B('steel',[.11,3.93,.097],at(s*1.75,2.5,.427));
   C('steel',.158,1.99,at(s*2.08,2.06,.30));
   for(const y of [1.11,2.97])C('edge',.194,.142,at(s*2.08,y,.30));
   B('void',[.15,.53,.067],at(s*1.86,3.24,.446));B('heat',[.069,.33,.027],at(s*1.86,3.24,.496));
  }
  B('steel',[4.31,.30,.29],at(0,4.43,.28));B('copper',[3.81,.13,.072],at(0,4.26,.47));
  // Large silhouette motif: a central vent mask and rising airflow seams.
  B('void',[.79,.53,.065],at(0,2.94,.438));
  for(const s of [-1,1])for(let j=0;j<3;j++)
   B(j===2?'edge':'copper',[.056,.36,.033],at(s*(.11+.10*j),2.94,.493),[0,0,s*.55]);
  B('heat',[.144,.064,.025],at(0,2.73,.494));
 }
 // Quench assembly: slanted heat fins above a low return vault.
 {
  const {x,z}=quench,at=(a,b,c=0)=>[x+a,b,z+c];
  B('void',[1.98,1.66,.24],at(0,1.67,.17));
  B('teal',[1.83,.95,.30],at(0,1.72,.29));
  B('steel',[2.02,.10,.42],at(0,2.23,.26));B('copper',[1.89,.13,.33],at(0,1.21,.27));
  for(let j=0;j<9;j++)B('edge',[.079,.69,.084],at((j-4)*.177,1.70,.475),[0,0,.24]);
  for(const s of [-1,1]){
   C('tealDark',.119,1.21,at(s*.77,2.69,.34));
   C('copper',.152,.090,at(s*.77,3.22,.34));
   Z('steel',.13,.355,at(s*.77,3.31,.21));
  }
  B('void',[1.28,.15,.074],at(0,1.065,.47));
  for(let j=0;j<5;j++)B(j===4?'heat':'cyan',[.137,.047,.036],at((j-2)*.22,1.065,.526));
 }
 return FOUNDRY_MODULE_EXTENTS.length;
}
