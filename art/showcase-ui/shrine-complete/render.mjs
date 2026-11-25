import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs'
import {join} from 'node:path'
import {board} from './board.mjs'
import {start,update} from './model.mjs'

const [source,out]=process.argv.slice(2), art=readFileSync(source)
assert.equal(createHash('sha256').update(art).digest('hex'),'dbb4e04a38df97a6c02c806ff897ac2b6a17ef02cc81eb232727df79db45e520')
mkdirSync(out,{recursive:true})
const url='data:image/jpeg;base64,'+art.toString('base64')
let state=start()
writeFileSync(join(out,'nov25-ui30-shrine-complete.svg'),board(state,url))
state=update(update(update(state,'continue'),'forward'),'forward')
writeFileSync(join(out,'nov25-ui30-portal-route.svg'),board(state,url))
