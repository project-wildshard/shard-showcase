# Forge Yard · original Wildshard combat demo

A standalone local browser prototype. Walker can equip the twelve tracked Wildshard weapon GLBs and face eight differently rigged opponents. The original four use a sweep, pounce, beam and charge. Hook Crane pulls the player, Kiln Warden blocks frontal hits and shoves, Breakwater Snare emerges at a marked point, and Spark Buoy bursts in a radius. The browser uses their exported state clips and the original weapon attack clips. This is not a Wildshard production build and it uses no Fable content or code.

From a checkout of the art branch:

```sh
cd demos/forge-yard
npm ci
npm run build
npm test
cd ../..
python -m http.server 5187
```

Open `http://127.0.0.1:5187/demos/forge-yard/`. Drag the left stick or press WASD to move. Use the two lower-right buttons (or Space and Shift) to attack and dodge. Change weapons with the selector and use Next rival to load another opponent.

For reproducibility the three dependencies are pinned; the generated viewer bundle and dependency tree are not checked into Git. Optional browser smoke: `npx playwright install chromium` then `npm run test:browser -- http://127.0.0.1:5187/demos/forge-yard/ /tmp/forge-yard-proof` from this directory with the server running. The condition-driven touch runner fights each rival, checks the Defeat pose and loads all twelve distinct weapon GLBs. Browser QA is not a physical phone acceptance test.

Scope: first-pass yard layout and Walker placeholder body, no progression, multiplayer, campaign or variants. The standard enemy Move/Windup/Attack/Recover/Hit/Defeat clips are wired; exported Special and Turn clips are not automatically selected in this prototype.
