# Foundry Executioner · silhouette checkpoint

One humanoid enemy, not a new roster. Design target: adult proportions and textile drape; curved, asymmetric forged plates; dark cloth and oxblood leather; a narrow refractory mask beneath the hood. The concept is a generated design reference, not a screenshot or 3D model. Compare the actual gray mesh against it from front, three-quarter, and profile before trying to sell detail with lighting. Prior robot yard designs are not the visual target.

`executioner-study.blend` is the live, editable Blender source for this checkpoint. `build.py` reconstructs the study from quad ring profiles, shell surfaces, cloth folds, and material node graphs. Body proportions, lead foot placement, drape anchor and helmet shaping are editable independently. There are no external textures or copied game assets. Filenames with “clay” and “steel” are actual Blender renders of the same study, not generated concept art.

```sh
blender -b -t 8 --python-exit-code 1 --python art/actors/foundry-executioner/build.py -- /tmp/executioner
```

**Not yet a game asset.** This checkpoint has no runtime export, rig, weighted joints or gameplay. Current gaps before a candidate review: face opening and mask shape, more asymmetric pauldron silhouette, garment continuity at elbows and knees, hands, fewer exposed mannequin-like transitions and readable material contrast at desktop camera distance. Material graph detail must survive baking and a real Three.js view; studio highlights are not the target. Validate motion with the gameplay camera, not just the studio orbit. No private reference screenshots included.

Second pass: the sleeves and trousers now use single connected mesh loops across each elbow and knee, the helmet has two fitted ceramic panels with a real slit, and the forged shoulder has three shaped plates instead of one bulb. Review the front three-quarter, a gray profile, and the smaller desktop-distance studio render. The latter is not Three.js or gameplay. Run `blender -b art/actors/foundry-executioner/executioner-study.blend --python-exit-code 1 --python art/actors/foundry-executioner/verify.py` to check the saved source. The raw procedural study still falls short of the target's textile/armor interaction, pose and material specificity.
