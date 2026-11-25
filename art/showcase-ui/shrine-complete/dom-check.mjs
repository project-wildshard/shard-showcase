import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const {Window}=await import(pathToFileURL(req.resolve('happy-dom')).href)
const window=new Window({url:'https://catalog.example/shrine-complete/',settings:{disableJavaScriptEvaluation:true}})
globalThis.document=window.document
document.write(readFileSync(new URL('./index.html',import.meta.url),'utf8'))
await import('./review.mjs')
const el=id=>document.getElementById(id)
const key=k=>document.dispatchEvent(new window.KeyboardEvent('keydown',{key:k,bubbles:true,cancelable:true}))
assert(!el('continue').hidden&&el('walk').hidden)
assert.equal(el('stage').querySelector('image').getAttribute('href'),'../media/nov24-vault-r4-idle.jpg')
assert.equal([...document.querySelectorAll('button')].filter(b=>!b.hidden&&!b.closest('[hidden]')).length,1)
key('ArrowUp')
assert(!el('continue').hidden)
el('continue').click()
assert(el('continue').hidden&&!el('walk').hidden)
assert.equal(document.activeElement,el('forward'))
assert.match(el('status').textContent,/still inside/)
el('forward').click()
for(let i=0;i<3;i++)key('ArrowUp')
assert.match(el('status').textContent,/still inside/)
key('ArrowUp')
assert.match(el('status').textContent,/Outside/)
el('back').click()
assert.match(el('status').textContent,/new example run/)
assert(el('walk').hidden)
assert.equal(document.activeElement,el('status'))
await window.close()
console.log('DOM: one initial button, dismiss focus, click + arrow input, threshold and return.')
