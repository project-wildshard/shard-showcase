export const example=Object.freeze({
  time:'11:42', best:'11:42 · NEW', deaths:2, rooms:'4 / 4',
  scrip:'150 SCRIP', core:'PLATE CORE', trophy:"WARDEN’S PLATE",
})

// Waypoints show crossing a doorway volume from opposite directions. They
// illustrate the interaction; they are not authored world coordinates.
export const route=Object.freeze([
  [119,602], [126,554], [139,506], [170,458], [201,420], [201,383], [201,346],
].map(Object.freeze))
export const threshold=5
export const start=()=>({card:true,position:0,place:'vault',runs:1,puzzlesSolved:true,chestOpen:true})
export function update(state,event){
  if(event==='continue')return state.card?{...state,card:false}:state
  if(state.card||state.place==='newRun'||!['forward','back'].includes(event))return state
  const position=Math.max(0,Math.min(route.length-1,state.position+(event==='forward'?1:-1)))
  if(position===state.position)return state
  if(state.position<threshold && position>=threshold)
    return {...state,position,place:'outside'}
  if(state.place==='outside' && position<threshold)
    return {...state,position,place:'newRun',runs:state.runs+1,puzzlesSolved:null,chestOpen:null}
  return {...state,position}
}
