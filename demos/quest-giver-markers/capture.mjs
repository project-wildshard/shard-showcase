import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';
const here = fileURLToPath(new URL('.', import.meta.url));
const dir = resolve(process.argv[2]);
const playwright = await import(pathToFileURL(join(resolve(process.argv[3]), 'playwright/index.mjs')));
const [anchors, plate, css, source] = await Promise.all([
  readFile(join(dir,'anchors.json'),'utf8').then(JSON.parse),readFile(join(dir,'marker-plate.png'),'base64'),
  readFile(join(here,'markers.css'),'utf8'),readFile(join(here,'markers.mjs'),'utf8')
]);
const browser = await playwright.chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',args:['--no-sandbox']});
try {
  const page = await browser.newPage({viewport:{width:402,height:874},deviceScaleFactor:2});
  const states = [['offer','available','!', 'rgb(255, 213, 74)'],['turn-in','turnIn','?', 'rgb(255, 213, 74)'],['cleared','done',null,null]];
  const rows=[];
  for (const [shot,state,glyph,yardColor] of states) {
    await page.setContent(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
      <style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#111} main{position:relative;width:100%;height:100%;isolation:isolate}img{width:100%;height:100%;display:block}</style>
      <style>${css}</style><main aria-label="Showcase plaza visual preview"><img alt="" src="data:image/png;base64,${plate}"></main>
      <script type="module">${source}
      const anchors=${JSON.stringify(anchors)}, stage=document.querySelector('main');
      for (const [role,label,phase] of [['surveyor','Surveyor','locked'],['yard-boss','Yard Boss',${JSON.stringify(state)}]]) {
        const marker=createMarker(document,label,phase,anchors[role]);
        if(marker){marker.dataset.role=role;stage.append(marker);}
      }
      window.markerReady=true;</script>`);
    await page.waitForFunction(() => window.markerReady && document.querySelector('img').complete && document.querySelector('img').naturalWidth===804);
    const found = await page.locator('.quest-giver-marker').evaluateAll(markers=>markers.map(root=>{
      const rect=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height};};
      const glyph=root.querySelector('.symbol');
      return {role:root.dataset.role,state:root.dataset.state,glyph:glyph.textContent,color:getComputedStyle(glyph).color,
              stroke:getComputedStyle(glyph).webkitTextStrokeWidth,name:rect(root.querySelector('.name')),glyphBox:rect(glyph),box:rect(root)};
    }));
    assert.equal(found.length,glyph?2:1);
    assert.deepEqual(found.map(row=>[row.role,row.glyph,row.color]),[
      ['surveyor','!','rgb(167, 174, 178)'],...(glyph?[['yard-boss',glyph,yardColor]]:[])
    ]);
    for (const row of found) {
      const anchor = anchors[row.role], b=row.box;
      assert(Math.abs(b.x + b.w/2 - anchor.headX)<.1 && Math.abs(anchor.headY - (b.y + b.h) - 4)<.1);
      assert(row.name.y + row.name.h <= row.glyphBox.y && row.glyphBox.h===40 && row.stroke==='1.5px');
      assert(b.x>=0 && b.x+b.w<=402 && b.y>=0 && b.y+b.h<=874);
    }
    if(found.length===2) assert(found[0].box.x+found[0].box.w+30<found[1].box.x);
    await page.screenshot({path:join(dir,`quest-${shot}.png`)});
    rows.push({shot,found});
  }
  await writeFile(join(dir,'w1b-quest-marker-browser-proof.json'),JSON.stringify({
    scope:'UI-12 four world-marker visual states on pinned actors; no game, minimap or quest bindings',
    viewportCSS:[402,874], outputPixels:[804,1748], deviceScaleFactor:2, eyeHeightM:1.7,
    aboveHeadCSSPixels:4, archiveStyleBlob:'297dff6669b7ac8c15239b30833338144cbee418',
    anchors, rows
  },null,2)+'\n');
} finally { await browser.close(); }
