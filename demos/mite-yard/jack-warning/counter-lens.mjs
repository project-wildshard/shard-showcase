// Presentation-only prototype for the pinned reference probe. The solver is
// given posed anchors in camera-local space and never writes game state.
export function counterLens() {
  const D = Math.PI / 180;
  let turn = 0, widen = 0, quiet = 0;
  const approach = (a, b, step) => a + Math.max(-step, Math.min(step, b - a));
  return function step({anchors, fov, aspect, dt, engaged, override}) {
    if (override) {
      // Deliberate handoff: never hold the camera against intentional movement.
      quiet = 0.18;
      turn = widen = 0;
      return {turn, widen};
    }
    quiet = Math.max(0, quiet - dt);
    let wishTurn = 0, wishWiden = 0;
    if (!quiet && engaged && anchors.length && anchors.every(([,,z]) => z < -.32)) {
      let loss = Infinity;
      for (const yaw of [0, 2, -2, 4, -4, 6, -6, 8, -8, 10, -10, 12, -12]) {
        const c = Math.cos(yaw * D), s = Math.sin(yaw * D);
        for (const w of [0, 4, 8]) {
          const tv = Math.tan((fov + w) * D / 2), th = tv * aspect;
          let bad = 0;
          for (const [x, y, z, hero] of anchors) {
            const depth = -s * x - c * z;
            if (depth < .32) { bad += 100; continue; }
            const X = (c * x - s * z) / (th * depth);
            const Y = y / (tv * depth);
            // Screen-space targets, not collision constraints. Reserve the right
            // near the lower controls, while permitting shoulders in open space.
            const right = Y < -.34 && hero ? .71 : .9;
            bad += Math.max(0, X - right, -.88 - X) ** 2;
            bad += .5 * Math.max(0, -.72 - Y, Y - .80) ** 2;
          }
          const next = 90 * bad + .019 * Math.abs(yaw) + .025 * w + .006 * Math.abs(yaw - turn);
          if (next < loss) { loss = next; wishTurn = yaw; wishWiden = w; }
        }
      }
    }
    turn = approach(turn, wishTurn, 105 * dt);
    widen = approach(widen, wishWiden, 80 * dt);
    return {turn, widen};
  };
}
