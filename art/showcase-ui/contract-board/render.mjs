import {createHash} from 'node:crypto';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {join} from 'node:path';
import {demoRows, previews, describe} from './states.mjs';

const [backgroundFile,out] = process.argv.slice(2);
assert(backgroundFile&&out,'Usage: node render.mjs <pinned plaza JPEG> <output dir>');
const bg=await readFile(backgroundFile);
assert.equal(createHash('sha256').update(bg).digest('hex'),'6d54139196c50a2ec14dd9aa94bfecd28bdfee0112fc8a601edd6c8b9d4b9802');
await mkdir(out,{recursive:true});
const w=402,h=874;
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const label=(x,y,size,v,fill='#31251b',family='sans',extra='')=>`<text x="${x}" y="${y}" font-size="${size}" class="${family}" fill="${fill}" ${extra}>${esc(v)}</text>`;
const mono=(x,y,size,v,fill,extra)=>label(x,y,size,v,fill,'mono',extra);
const line=(a,b,c,d,stroke,opts='')=>`<path d="M${a} ${b}L${c} ${d}" stroke="${stroke}" ${opts}/>`;
const pin=(x,y)=>`<ellipse cx="${x+1}" cy="${y+3}" rx="5.4" ry="5.3" fill="#452c19" opacity=".34"/><circle cx="${x}" cy="${y}" r="4.8" fill="url(#pin)" stroke="#4f5146" stroke-width=".6"/>`;
const corners=(x,y,x2,y2)=>[[x,y],[x2,y],[x,y2],[x2,y2]].map(([a,b])=>`<circle cx="${a}" cy="${b}" r="2.6" fill="url(#pin)" stroke="#33251b"/>`).join('');
const woodGrain = Array.from({length:113},(_,i)=>{
  const x=10+i*3.375, a=(i*137%79)-39;
  return `<path d="M${x} 110q${a*.20} 58 ${a*.14} 138t${a*.14} 160t${-a*.08} 162t${-a*.13} 230" stroke="${i%3===0?'#ffc185':'#100d0a'}" stroke-width="${.35+(i*91%11)/10}" opacity="${.035+(i*213%8)/100}" fill="none"/>`;
}).join('');
const footerLine='Only enemies that award XP count.';
const defs=`<defs>
<style>.sans{font-family:DejaVu Sans,sans-serif}.serif{font-family:Bitstream Charter,serif;font-style:italic}.mono{font-family:DejaVu Sans Mono,monospace;letter-spacing:1.1px}</style>
<linearGradient id="back" x2=".0" y2="1"><stop stop-color="#0c181d" stop-opacity=".41"/><stop offset="1" stop-color="#081218" stop-opacity=".74"/></linearGradient>
<linearGradient id="wood" x2=".92" y2="1"><stop stop-color="#754e36"/><stop offset=".44" stop-color="#513925"/><stop offset="1" stop-color="#382b21"/></linearGradient>
<linearGradient id="paper" x2="1" y2="1"><stop stop-color="#fff2d2"/><stop offset="1" stop-color="#e7d4ac"/></linearGradient>
<linearGradient id="locked" x2="1" y2="1"><stop stop-color="#a9a8a0"/><stop offset="1" stop-color="#93948f"/></linearGradient>
<linearGradient id="pin" x2="0" y2="1"><stop stop-color="#d4d9cd"/><stop offset="1" stop-color="#666d68"/></linearGradient>
<clipPath id="board"><rect x="13" y="128" width="376" height="677" rx="12"/></clipPath>
</defs>`;
function lock(row,yy) {
 const p=describe(row,{level:1});
 return `<g aria-label="${esc(row.name)}: ${p.text}">
 <rect x="31" y="${yy+3}" width="340" height="100" rx="5" fill="#17100c" opacity=".44"/>
 <rect x="31" y="${yy}" width="340" height="100" rx="5" fill="url(#locked)" stroke="#bebbab" stroke-width=".8"/>
 <path d="M32 ${yy+6}h338" stroke="#ddd7c7" opacity=".28"/>
 ${pin(201,yy+1)}${mono(47,yy+25,10,row.band,'#242922')}${label(46,yy+53,25,row.name,'#222b28','serif')}
 ${label(48,yy+77,12,p.text,'#222b28')}
 <path d="M327 ${yy+60}v-3a5.4 5.4 0 0110.8 0v3m-13 0h15v12h-15z" fill="none" stroke="#343b35" stroke-width="1.3" stroke-linejoin="round"/>
 </g>`;
}
function active(s){
 const p=describe(demoRows[0],s), done=p.count===20;
 const prog=100*p.count/20, statusFill=done?'#304937':'#313631';
 return `<g>
 <rect x="31" y="265" width="340" height="224" rx="6" fill="#0e0906" opacity=".51"/>
 <rect x="30" y="262" width="341" height="224" rx="6" fill="url(#paper)" stroke="#d0bc91"/>
 <path d="M37 266h327m-329 211h331" stroke="#fff5dc" opacity=".54"/>
 ${pin(200,264)}
 ${mono(48,291,10,'COUNT  /  BAND 01','#713b2c')}
 ${label(47,323,33,'Scrap Patrol','#30251d','serif')}
 ${label(48,349,15,p.text,'#392a1d')}
 <rect x="48" y="369" width="185" height="6" rx="3" fill="#b6a17d"/>
 <rect x="48" y="369" width="${1.85*prog}" height="6" rx="3" fill="#416453"/>
 ${mono(351,375,13,`${p.count} / 20`,'#30251e','text-anchor="end"')}
 ${line(48,389,354,389,'#a6926f','stroke-dasharray="3 4"')}
 ${mono(48,405,9,p.firstClaimed?'REPEAT REWARD':'FIRST REWARD','#663526')}
 ${label(48,425,13,p.firstClaimed?'20 Scrip':'20 Scrip  ·  Wall trophy  ·  Pest Control','#3b3025','serif')}
 <rect x="48" y="443" width="${p.status.length*6.3+25}" height="26" rx="3" fill="${statusFill}"/>
 ${mono(58,459,9,p.status,'#fff3d8')}
 </g>`;
}
function make(key,s){
 return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="title desc">
<title id="title">Wildshard gate plaza: ${esc(s.label)}</title><desc id="desc">${esc(s.caption)} Big Pallet and the Vault Warden remain locked.</desc>
${defs}
<image width="402" height="874" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/jpeg;base64,${bg.toString('base64')}"/>
<rect width="402" height="874" fill="url(#back)"/>
${mono(24,34,10,'WILDSHARD  /  THE SHOWCASE','#d1cdc1')}${mono(24,52,8,'E1f   •   UI-16 PORTRAIT STUDY','#e1b481')}
<g opacity=".42"><rect x="25" y="73" width="94" height="26" rx="6" fill="#162128" stroke="#738989"/>${mono(38,90,9,'JOURNAL','#ebeee0')}</g>
<rect x="296" y="70" width="91" height="36" rx="18" fill="#17242a" stroke="#a0a59a" stroke-width="1"/>
${mono(341.5,92.5,10,'CLOSE','#f3e9d4','text-anchor="middle"')}
<rect x="10" y="134" width="382" height="679" rx="15" fill="#100b09" opacity=".77"/>
<g clip-path="url(#board)">
<rect x="13" y="128" width="376" height="677" fill="url(#wood)"/>
${woodGrain}
${[210,254,494,615,739].map(y=>line(13,y,389,y,'#251d17','stroke-width="2.2" opacity=".50"')+line(13,y+2,389,y+2,'#a67755','opacity=".5"')).join('')}
<path d="M22 140h358v652H22z" fill="none" stroke="#cf9462" opacity=".33"/>
</g>
<rect x="13" y="128" width="376" height="677" rx="12" fill="none" stroke="#b48865" stroke-width="1.2"/>
${corners(25,142,377,791)}
${mono(34,161,11,'THE GATE PLAZA','#f2c98d')}
${label(32,196,38,'Kill contracts','#fff1ce','serif')}
${mono(34,238,10,`DONE ${s.completed} / ${demoRows.length}`,'#f6d8a0')}${mono(165,238,10,`TITLES ${s.titles}`,'#f6d8a0')}${mono(366,238,10,`LV ${s.level}`,'#f6d8a0','text-anchor="end"')}
${active(s)}
${lock(demoRows[1],503)}${lock(demoRows[2],621)}
${label(201,770,13,footerLine,'#f6dab1','serif','text-anchor="middle"')}
${mono(201,840,8,`FIXED LIST  /  ${key.toUpperCase()}  /  VISUAL FIXTURE`,'#ebe2c7','text-anchor="middle"')}
</svg>\n`;
}
for(const [key,s] of Object.entries(previews)) await writeFile(join(out,`e1f-contract-${key}.svg`),make(key,s));
