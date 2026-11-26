import assert from 'node:assert/strict';
import {tabs} from '../character-tab/model.mjs';

export {tabs};
export const categories=Object.freeze([
  {key:'vistas',label:'Vistas',limit:8,unit:'viewpoints',color:'#9fdeec',icon:'M-8 6 -2 -4 3 2 6 -2 11 6Z M5 -7h4 M7 -9v4'},
  {key:'caches',label:'Cosmetic caches',limit:6,unit:'cosmetic rewards',color:'#7ee1bd',icon:'M-9 -3h18v11H-9Z M-9 -3 -5 -7h10l4 4 M-2 1h4v4h-4Z'},
  {key:'gold',label:'Gold 1×1s',limit:20,unit:'Calibration Chip progress',color:'#f5cb85',icon:'M0 -9 8 -5v10l-8 4-8-4V-5Z M-8 -5l8 5 8-5 M0 0v9'},
]);
const records=Object.freeze([
  {key:'movers',label:'Movers',format:'time',hint:'Fastest time'},
  {key:'skittles',label:'Skittles',format:'pins',hint:'Most pins down'},
  {key:'riding',label:'Riding lap',format:'time',hint:'Fastest lap'},
]);

function readCount(raw, max){
  const n=raw??0;
  assert(Number.isInteger(n)&&n>=0&&n<=max);
  return n;
}
function formatPB(val,format){
  assert(Number.isInteger(val)&&val>=0);
  if(format==='pins'){
    assert(val<=10);
    return val+' / 10';
  }
  assert(val>0);
  const min=Math.floor(val/60000), sec=Math.floor(val/1000)%60, centi=Math.floor(val/10)%100;
  return min+':'+String(sec).padStart(2,'0')+'.'+String(centi).padStart(2,'0');
}
export function read(sample={}){
  const collection=categories.map(row=>({...row,count:readCount(sample[row.key],row.limit)}));
  const n=collection.find(x=>x.key==='gold').count;
  const earned=Math.floor(n/5);
  const next=earned===4?null:(earned+1)*5;
  return {
    collection, earned, next, remaining:next===null?0:next-n,
    records:records.map(r=>({...r,value:sample.pb?.[r.key]==null?null:formatPB(sample.pb[r.key],r.format)})),
  };
}
export const examples=Object.freeze({
  new:read(),
  trail:read({vistas:3,caches:2,gold:9,pb:{movers:64320,skittles:8}}),
});
