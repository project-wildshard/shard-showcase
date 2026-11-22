import test from 'node:test'
import assert from 'node:assert/strict'
import {createGame,step} from './combat.mjs'
const advance=(g,secs,i)=>{for(let n=0;n<secs*60;n++)step(g,i,1/60)}
test('walking enters wake radius, turns and pursues',()=>{
 const g=createGame()
 advance(g,.25);assert.equal(g.mite.phase,'sleep')
 advance(g,.95,{forward:1});assert.notEqual(g.mite.phase,'sleep')
 g.player.x=-3.5;g.player.z=2.0;const initial=g.mite.yaw
 advance(g,.94)
 assert.notEqual(g.mite.yaw,initial)
})
test('windup timing, impact and defeat; third attack is special',()=>{
 const g=createGame();Object.assign(g.mite,{phase:'chase',x:0,z:0,yaw:0,strikes:2})
 Object.assign(g.player,{x:0,z:1.8,hp:35})
 step(g);assert(g.mite.special);assert.equal(g.mite.phase,'windup')
 advance(g,.68);assert.equal(g.player.hp,35)
 advance(g,.55);assert.equal(g.player.hp,0);assert(g.over)
})
test('three correctly aimed sword hits kill a Mite',()=>{
 const g=createGame();Object.assign(g.mite,{x:0,z:0,phase:'wake'})
 Object.assign(g.player,{x:0,z:1.35,yaw:0})
 advance(g,1.75,{attack:true});assert.equal(g.kills,1)
 assert.equal(g.mite.phase,'die')
 assert.equal(g.mite.hp,0)
})
test('crates block movement and a direct sword hit',()=>{
 const g=createGame();Object.assign(g.player,{x:6,z:-3.5,yaw:0})
 advance(g,2,{forward:1});assert(g.player.z>-4.1)
 Object.assign(g.mite,{x:6,z:-5.4,phase:'sleep'})
 advance(g,.21,{attack:true});assert.equal(g.mite.hp,70)
})
