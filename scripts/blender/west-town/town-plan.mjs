import {BLOCKS,HUB} from './layout.mjs';
let tSeed = 31; const trnd = () => (tSeed = (tSeed * 16807) % 2147483647) / 2147483647;
function townPlan() {
  tSeed = 31;
  const out = [], R = (x0, x1, z0, z1, h, kind, label = '', sub = '') => out.push({ x0, x1, z0, z1, h, kind, label, sub });
  for (const s of HUB.services.filter(q => q.shop)) R(...s.box, 9, 'shop', s.name, s.sub);
  for (const t of HUB.toLet) R(...t, 7, 'tolet', 'TO LET', 'room for a future shop');
  const zh = HUB.zipHouse; R(zh.x0, zh.x1, zh.z0, zh.z1, zh.h, 'zip', 'ZIP HOUSE', 'grapple finish on the roof');
  R(...HUB.stable, 7, 'stable', 'STABLE', 'stalls · loaner horses');
  R(-16, -9, -18, -7, 11, 'gatehouse'); R(-16, -9, 7, 18, 11, 'gatehouse');
  const reserved = out.slice(), hit = (a, b, m = 1) => a.x0 < b.x1 + m && a.x1 > b.x0 - m && a.z0 < b.z1 + m && a.z1 > b.z0 - m;
  for (const [x0, x1, z0, z1] of BLOCKS) {
    const wide = x1 - x0 >= z1 - z0, depth = wide ? z1 - z0 : x1 - x0, len = wide ? x1 - x0 : z1 - z0;
    const rows = depth >= 22 ? [[0, depth / 2], [depth / 2, depth]] : [[0, depth]];
    for (const [r0, r1] of rows) {
      let u = 0;
      while (u < len - 6) {
        const w = Math.min(len - u, 9 + Math.floor(trnd() * 7)), d = (r1 - r0) - (trnd() < .4 ? Math.floor(trnd() * 3) : 0);
        const front = r0 === 0 ? r0 : r1 - d;
        const b = wide ? { x0: x0 + u, x1: x0 + u + w, z0: z0 + front, z1: z0 + front + d } : { x0: x0 + front, x1: x0 + front + d, z0: z0 + u, z1: z0 + u + w };
        u += w + (trnd() < .16 ? 4 : 0);
        if (len - u < 7 && len - u > 0) { if (wide) b.x1 = x1; else b.z1 = z1; u = len; }
        if (reserved.some(q => hit(b, q))) continue;
        const h = [6, 7.5, 9, 9, 10.5, 12][Math.floor(trnd() * 6)];
        out.push({ ...b, h, kind: 'house', roof: trnd() < .6 });
      }
    }
  }
  return out;
}
const TOWN_B = townPlan();
console.log(JSON.stringify(TOWN_B,null,2));
