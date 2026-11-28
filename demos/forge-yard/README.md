# Forge Yard · original Wildshard combat demo

A standalone local browser prototype. Walker can equip the twelve tracked Wildshard weapon GLBs and face sixteen differently rigged opponents. The original four use a sweep, pounce, beam and charge. Hook Crane pulls the player, Kiln Warden blocks frontal hits and shoves, Breakwater Snare emerges at a marked point, and Spark Buoy bursts in a radius. The ordnance group adds a locked three-pulse salvo, a committed blade lunge, a visible lob into a marked impact zone, and a transverse sweep. The foundry line adds a cone pull and release, alternating cut marks, two flank pylons with a safe seam, and a jet with reverse recoil. The fitted three-quarter camera keeps world-relative stick directions. The browser uses their exported state clips and the original weapon attack clips. This is not a Wildshard production build and it uses no Fable content or code.

From a checkout of the art branch:

```sh
cd demos/forge-yard
npm ci
npm run build
npm test
cd ../..
python -m http.server 5187
```

Open `http://127.0.0.1:5187/demos/forge-yard/`. Drag the left stick or press WASD to move. Use the two lower-right buttons (or Space and Shift) to attack and dodge. Change weapons with the selector and use Next rival to load another opponent. Select Base type or one of five variant kits: Rusher (short sprint), Bulwark (frontal armor), Feinter (false tell and sidestep), Echo (retargeted follow-up), and Overload (timed radial discharge). Each alters the same base type’s fight and adds visible equipment, not simply dye.

For reproducibility the three dependencies are pinned; the generated viewer bundle and dependency tree are not checked into Git. Optional browser smoke: `npx playwright install chromium` then `npm run test:browser -- http://127.0.0.1:5187/demos/forge-yard/ /tmp/forge-yard-proof` from this directory with the server running. The condition-driven touch runner fights each rival, checks the Defeat pose and strikes with all twelve distinct weapon GLBs, and checks that each of the 80 variant selections mounts geometry in the browser. The simulation suite checks all 80 behavior combinations. Full-win browser evidence covers base types with Rivet Maul, not a full fight against every variant; see browser-proof.json for the recorded run. Browser QA is not a physical phone acceptance test.

Startup fetches the first rival and equipped weapon together. Other rival GLBs are fetched when selected and cached for later rematches; a failed next-rival load leaves the current fight in place and can be retried. For a cache-disabled synthetic portrait startup check, run `node demos/forge-yard/startup-smoke.mjs http://127.0.0.1:5187/demos/forge-yard/ lazy` from the repository root. The sample uses 450,000 B/s download and 80 ms latency. See `startup-proof.json` for the matched eager and on-demand receipts.

Scope: first-pass yard layout and Walker placeholder body, no progression, multiplayer or campaign. Eighty variants reuse sixteen base rigs, not eighty separate models. The standard enemy Move/Windup/Attack/Recover/Hit/Defeat clips are wired; Salt Mortar uses Special at launch and Lantern Relay during its pylon attack. The other exported Special clips and all Turn clips are not automatically selected in this prototype.
