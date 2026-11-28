// Each modifier has an actual gameplay transition and a readable geometry kit.
// Base enemies are not counted as variants.
export const VARIANTS=[
 {id:'rusher',name:'Rusher',rule:'A burst of speed starts each chase',hp:.83,pace:1.18,windup:.90,recover:1},
 {id:'bulwark',name:'Bulwark',rule:'Front plating resists hits except during wind-up or recovery',hp:1.17,pace:.76,windup:1.07,recover:1.22},
 {id:'feinter',name:'Feinter',rule:'Cancels its first tell into a sidestep before the real attack',hp:.92,pace:1.07,windup:1,recover:1.01},
 {id:'echo',name:'Echo',rule:'Retargets once during recovery for an immediate follow-up',hp:.90,pace:.93,windup:1.13,recover:1.14},
 {id:'overload',name:'Overload',rule:'Starts a delayed radial discharge if you get close',hp:1.01,pace:.9,windup:1.07,recover:1.14},
];
export function configuration(base,id){
 const v=VARIANTS.find(a=>a.id===id);
 if(!v)return {...base,variant:null,baseId:base.id};
 return {...base,baseId:base.id,id:base.id+'-'+v.id,variant:v.id,name:base.name+' · '+v.name,
   hp:Math.round(base.hp*v.hp),pace:base.pace*v.pace,windup:base.windup*v.windup,recover:base.recover*v.recover,
   rule:v.rule};
}
export function roster(enemyTypes){return enemyTypes.flatMap(s=>VARIANTS.map(v=>configuration(s,v.id)));}
