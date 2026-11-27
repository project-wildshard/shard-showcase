// E10d visual timing contract only. No player, damage, collider or quest state.
export const hz = 30;
export const pitch = 3.155;
export const warningFrames = 30;
export const activeFrames = 19;
export const stepFrames = 11;
export const rowOrder = [3, 2, 1, 0, -1, -2, -3];

export const slots = rowOrder.flatMap(row =>
    Array.from({length: 9}, (_, i) => i - 4)
        .filter(col => Math.hypot((Math.abs(col) + .5) * pitch, (Math.abs(row) + .5) * pitch) <= 12)
        .map(col => ({col, row, xyz: [col * pitch, .006, -row * pitch]})));
export const endFrame = (rowOrder.length - 1) * stepFrames + warningFrames + activeFrames;

export function phaseAt(frame, row) {
    const rowId = rowOrder.indexOf(row);
    if (!Number.isInteger(frame) || rowId < 0) throw new RangeError('integer frame and known row required');
    const elapsed = frame - rowId * stepFrames;
    return elapsed < 0 || elapsed >= warningFrames + activeFrames ? 'idle'
        : elapsed < warningFrames ? 'warning' : 'active';
}

export function frameAt(frame) {
    return slots.map(s => ({...s, state: phaseAt(frame, s.row)}));
}
