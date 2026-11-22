// Own just one look pointer. Movement and combat controls remain independent.
export function createTouchLook(){
 let owner,x,y
 return {
  begin(e){
   if(e.pointerType!=='touch'||owner!==undefined)return false
   owner=e.pointerId;x=e.clientX;y=e.clientY
   return true
  },
  move(e){
   if(e.pointerId!==owner||owner===undefined)return
   const delta=[e.clientX-x,e.clientY-y]
   x=e.clientX;y=e.clientY
   return delta
  },
  end(e){if(e.pointerId===owner)owner=undefined},
  clear(){owner=undefined},
 }
}
