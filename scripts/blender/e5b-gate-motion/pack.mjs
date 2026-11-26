import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';

export const sha = b => createHash('sha256').update(b).digest('hex');
export const door = 'e5b-alarm-gate-pair-motion.glb';
export const durations = {Close: 2.4, Open: 2.8};
export const endpoints = {closed: 3.99, open: 12.11};
export const localTranslation = (side, x) => [side*x, .015, 0];
export const center = (state, t) => {
  const u = Math.min(1,Math.max(0,t/durations[state]));
  const eased = u*u*(3-2*u);
  const {closed,open} = endpoints;
  return state==='Close' ? open+(closed-open)*eased : closed+(open-closed)*eased;
};
export const asset = name => fileURLToPath(new URL('../../../public/assets/wildshard-art/'+name,import.meta.url));
export const receipt = JSON.parse(readFileSync(new URL('../../../project/layouts/e5b-alarm-gate-fit.json',import.meta.url)));
export function splitGlb(b) {
  assert.equal(b.toString('ascii',0,4),'glTF');
  assert.equal(b.readUInt32LE(4),2);
  assert.equal(b.readUInt32LE(8),b.length);
  const n=b.readUInt32LE(12);
  assert.equal(b.toString('ascii',16,20),'JSON');
  assert.equal(b.toString('ascii',24+n,28+n),'BIN\0');
  return [JSON.parse(b.toString('utf8',20,20+n)),b.subarray(28+n)];
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const out=process.argv[2];
  assert(out,'Pass an output directory.');
  const original=readFileSync(asset('e5b-alarm-gate-leaf.glb'));
  assert.equal(sha(original),receipt.assets['e5b-alarm-gate-leaf'].sha256);
  const [j,bin]=splitGlb(original);
  assert(!j.animations && !j.images && !j.skins && j.scenes.length===1);
  const [l]=j.scenes[0].nodes;
  const r=j.nodes.length;
  const {children}=j.nodes[l];
  assert.equal(children.length,20);
  j.nodes[l]={name:'AlarmLeafLeft',children,translation:localTranslation(-1,endpoints.open)};
  j.nodes.push({name:'AlarmLeafRight',children:children.map((_,i)=>r+1+i),
    translation:localTranslation(1,endpoints.open),rotation:[0,1,0,0]});
  j.nodes.push(...children.map(i=>({...j.nodes[i]})));
  j.scenes[0].nodes.push(r);

  const chunks=[bin];
  let offset=bin.length;
  const acc=(rows,type)=>{
    const values=rows.flat();
    const bytes=Buffer.alloc(values.length*4);
    values.forEach((v,i)=>bytes.writeFloatLE(v,i*4));
    const view=j.bufferViews.push({buffer:0,byteOffset:offset,byteLength:bytes.length})-1;
    offset+=bytes.length;
    chunks.push(bytes);
    const axes=Array.isArray(rows[0]) ? rows[0].length : 1;
    const axis=k=>axes===1?values:rows.map(row=>row[k]);
    return j.accessors.push({bufferView:view,componentType:5126,count:rows.length,type,
      min:Array.from({length:axes},(_,k)=>Math.min(...axis(k))),
      max:Array.from({length:axes},(_,k)=>Math.max(...axis(k)))})-1;
  };
  j.animations=Object.entries(durations).map(([state,seconds])=>{
    const times=Array.from({length:Math.round(seconds*30)+1},(_,i)=>i/30);
    const input=acc(times,'SCALAR');
    return {name:'Alarm_gate_'+state.toLowerCase(),
      samplers:[-1,1].map(side=>({input,output:acc(times.map(t=>localTranslation(side,center(state,t))),'VEC3'),interpolation:'LINEAR'})),
      channels:[l,r].map((node,sampler)=>({sampler,target:{node,path:'translation'}}))};
  });
  j.buffers[0].byteLength=offset;

  const json=Buffer.from(JSON.stringify(j));
  const pad=Buffer.alloc((4-json.length%4)%4,0x20);
  const b=Buffer.concat([Buffer.alloc(20),json,pad,Buffer.alloc(8),...chunks]);
  const jsonLength=json.length+pad.length;
  b.write('glTF');
  b.writeUInt32LE(2,4);
  b.writeUInt32LE(b.length,8);
  b.writeUInt32LE(jsonLength,12);
  b.write('JSON',16);
  b.writeUInt32LE(offset,20+jsonLength);
  b.write('BIN\0',24+jsonLength);
  assert(b.length<65536,b.length);
  mkdirSync(out,{recursive:true});
  writeFileSync(join(out,door),b);
  console.log(door,b.length,sha(b));
}
