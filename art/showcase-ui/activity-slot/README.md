# The shared activity chip

WSC-SCENE-010 art review only. Replicates the UI-PICKS decisions for UI-20 (course clock), UI-29 A (Vault), and UI-31 (park trick score). One slot directly below the illustrative minimap; it replaces the tracked quest during an activity and restores it at the end. No native HUD or UI rule was changed. All text and scores are fixture values, backgrounds are authored art stills and don't necessarily depict that exact gameplay state. The on-screen Move, Jump and Look marks are inert.

Copy index.html, style.css and app.js into the catalogue output activity-slot directory. The four JPEG stills are existing catalogue assets and link from sibling media, with no added source duplication. Run node test.mjs for state contract tests. Narrow phone screenshots should be taken from the preview, not from the game.

Sources: docs/plans/kitchen-sink-v2/UI-PICKS.md and hud-character-mini-plan.md, original approved UI-20 / UI-29-A / UI-31 review frames.
