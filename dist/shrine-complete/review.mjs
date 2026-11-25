import {start,update} from './model.mjs'
import {board} from './board.mjs'

const stage=document.querySelector('#stage')
const status=document.querySelector('#status')
const walk=document.querySelector('#walk')
const continueButton=document.querySelector('#continue')
const forward=document.querySelector('#forward')
const back=document.querySelector('#back')
let state=start()
function paint(focus=false){
  stage.innerHTML=board(state,'../media/nov24-vault-r4-idle.jpg')
  continueButton.hidden=!state.card
  walk.hidden=state.card||state.place==='newRun'
  status.textContent=state.card?'Review the completion card, then choose Continue.':
    state.place==='vault'?'Card closed. You are still inside. Walk Forward or press ↑.':
    state.place==='outside'?'Outside the Vault. Walk Back or press ↓ to go back through.':
    'Back through the threshold. A new example run has started.'
  if(focus)(state.place==='newRun'?status:forward).focus()
}
function step(action){
 const next=update(state,action)
 if(next===state)return
 const focus=action==='continue'||next.place==='newRun'
 state=next
 paint(focus)
}
continueButton.addEventListener('click',()=>step('continue'))
forward.addEventListener('click',()=>step('forward'))
back.addEventListener('click',()=>step('back'))
document.addEventListener('keydown',e=>{
 if(state.card||!['ArrowUp','ArrowDown'].includes(e.key))return
 e.preventDefault()
 step(e.key==='ArrowUp'?'forward':'back')
})
paint()
