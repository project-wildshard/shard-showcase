# Forge Yard · original Wildshard combat demo
Current checkpoint is an engine-independent combat simulation, not a playable page yet. It consumes the four dock enemy definitions and gives the twelve weapons distinct reach, damage, and timing. The four enemy attack families are short sweep, pounce, beam, and charge. Dodge, cover and defeat are tested. Next bind the renderer, models, pose clips and portrait controls, then run an end-to-end browser fight.

```sh
node --test demos/forge-yard/arena.test.mjs
```

No Fable assets or runtime.
