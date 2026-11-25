# W3a Six Targets: native walk-and-strike rehearsal

The pinned Engine 0.1.44 capsule travels through the actual Range Gate
scenery and six reimported fixture meshes. It walks 64.79 m without an
airborne tick. The chosen route skirts ornamental vegetation at the outer
stands and uses the west aisle between the two rows. Inputs are simulated
stick/yaw and ordinary swing commands; no teleport, height plane, flag
injection or direct contact callback.

The sword row follows Round 5 X −30/−24/−18 at Z 86. The spear row uses the
same X values at Z 104. Only the angled **approach points** are inferred.
The reimported stands face the approach; each fixture foot seats on its
existing ground. The two bracketed rehearsal item rows are separate from
production inventory. Proven on the installed native loadout, timed melee,
and `world/targets` dispatcher, with one flag per correctly reached
fixture. The intended six swings landed in a repeatable order by 22.1 s
including recovery; this is a scripted test, not a target PB. An independent
run rejects four controls: an aimed miss, wrong weapon, duplicate hit,
and a spear line outside the clear bore. Sight rays through the exported
ring centers were also checked independently in Blender, not inferred from
the engine flags. These contact rows do not add an occlusion law.

```sh
T=/tmp/six-targets
D=demos/native-six-targets
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-range-scenery/build.py -- --output "$T/donor"
B="$T/donor/range-landscape-editable.blend"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- "$T/geometry.json"
node --experimental-transform-types "$D/sample.mjs" "$T/geometry.json" "$T/run.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- "$T/geometry.json" "$T/run.json"
```

Use a Node project containing pinned Engine 0.1.44, Format 0.43.0 and the
engine's Rapier dependencies; set `WSC_NODE_PROJECT` if it is outside
the repo. The last command checks line of sight and renders the trace.
Trail lines and checks are annotations, not game UI. Large rebuilds stay
in scratch. No game-world host/install, equipment loan, player animation,
scoring board, persistence, native client, phone review or public game
deployment is part of this rehearsal.
