# Fable prompt: build the Kitchen Sink, clean room

Ask A16. Start a fresh Fable session in an empty directory, copy
[ZONE-DESCRIPTION.md](ZONE-DESCRIPTION.md) into it, and paste
everything below the line. The builder never sees a Wildshard repo,
sharddev, the shard format or the engine.

---

Build a complete, playable, single-player game in one go: the zone
described in `ZONE-DESCRIPTION.md` in this directory. Read all of it
first. It should feel like playing an MMO zone alone.

## Ground rules

- A new git repo in this directory. TypeScript (strict) + three.js +
  Vite, pnpm. Commit as you go with clear messages.
- Clean room: no game engine, no server, no multiplayer, no accounts.
  Everything runs in the browser; save to localStorage.
- No downloaded art or audio. Build models from three.js geometry in
  code, sounds and music from WebAudio.
- **Mobile first.** It must run smoothly on an iPhone in **portrait**,
  with touch controls and the portrait HUD the description lays out.
  Desktop (WASD, mouse, click) works too. Cap the pixel ratio, use
  instancing, and give full AI to at most 16 enemies within 60 m;
  enemies further away idle cheaply.
- Unit-test the combat and level maths (Vitest). `pnpm build` and
  `pnpm test` must pass.
- A dev menu (behind a small gear icon): set your level, XP ×10,
  teleport to any zone, set the time of day, start a storm.

## Done when

On a phone in portrait you can start at level 1 in town, take a quest,
try the west toys, cross the east gate, level through the bands, clear
the Training Vault and the gauntlet, and beat the Crate Titan (the dev
menu may be used to skip the grind). Write a README with how to run it
and what is in and out.
