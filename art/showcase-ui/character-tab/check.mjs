import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {choose,openBag,player,stats,tabs,subTabs,derived} from './model.mjs';
assert.deepEqual(tabs,['Map','Character','Finds','Pack','Feats']);
assert.deepEqual(subTabs,['Character','Gear']);
const initial=openBag(), gear=choose(initial,'Gear');
assert.deepEqual(initial,{tab:'Character',subTab:'Character'});
assert.deepEqual(gear,{tab:'Character',subTab:'Gear'});
assert.deepEqual(choose(gear,'Map'),gear);
assert.deepEqual(openBag(),initial);
assert.deepEqual(stats.map(x=>x[0]),['VIT','STR','DEX','AGI','DEF','MDEF','LUK']);
assert.deepEqual(stats.map(x=>x[3]).sort(),[.8,.8,1,1,1,1.2,1.2]);
assert.equal(player.level,7);
assert.deepEqual(derived.map(x=>x[1]),['184','29.1%','27.4%','50.6%','12.9% / 5.6%','1.62×','9.1%','2.4%']);
const c=readFileSync(join(process.argv[2],'ui10-character.svg'),'utf8');
const g=readFileSync(join(process.argv[2],'ui10-gear.svg'),'utf8');
for(const s of [c,g]){
 assert.ok(s.includes('viewBox="0 0 402 874"')&&s.includes('not live game'));
 assert.ok(!/<script|onclick|https?:\/(?!\/www\.w3\.org)/.test(s));
 for(const label of tabs)assert.ok(s.includes('>'+label.toUpperCase()+'</text>'));
 assert.equal((s.match(/>CHARACTER<\/text>/g)||[]).length,2);
}
assert.ok(c.includes('data-subtab="Character"')&&c.includes('NO POINTS TO SPEND'));
assert.ok(g.includes('data-subtab="Gear"')&&g.includes('NO EQUIP ACTION'));
for(const label of derived.map(x=>x[0]))assert.ok(c.includes('>'+label+'</text>'));
const light=hex=>{
 const comps=hex.match(/.{2}/g).map(c=>parseInt(c,16)/255);
 return [.2126,.7152,.0722].reduce((n,m,i)=>n+m*(comps[i]<=.04045?comps[i]/12.92:((comps[i]+.055)/1.055)**2.4),0);
};
for(const [fg,bg] of [['aac0c8','142632'],['a8e3ee','1e3d49'],['78dbb6','142632'],['f2c688','11232c'],['8eafb7','121d25']])
 assert.ok((light(fg)+.05)/(light(bg)+.05)>4.5,[fg,bg]);
console.log('Verified approved tab hierarchy, default state, sample stat maths, static SVGs and five text contrast pairs.');
